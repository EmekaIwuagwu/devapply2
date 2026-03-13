#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# DevApply startup script
#
# Architecture on Render (single web service):
#   • FastAPI   → internal :8000  (background, auto-restarts on crash)
#   • Streamlit → $PORT           (foreground — this is what Render monitors)
# ─────────────────────────────────────────────────────────────────────────────

echo "=== DevApply starting ==="

# Ensure all `from app.*` imports resolve regardless of how Python was invoked
export PYTHONPATH=/app

echo "DATABASE_URL driver : $(echo "${DATABASE_URL:-NOT SET — using SQLite default}" | cut -d: -f1)"
echo "JWT_SECRET_KEY set  : $([ -n "${JWT_SECRET_KEY}" ] && echo yes || echo no)"

# ── Database initialisation (non-fatal) ───────────────────────────────────────
echo "Initialising database tables..."
python - <<'PYEOF' || echo "DB init skipped (will retry on first request)"
import asyncio, sys
try:
    from app.backend.database.connection import engine, Base
    # Import all models so Base.metadata is fully populated
    import app.backend.models.user        # noqa: F401
    import app.backend.models.strategy    # noqa: F401
    import app.backend.models.application # noqa: F401
    import app.backend.models.resume      # noqa: F401
    import app.backend.models.agent_execution  # noqa: F401
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init_db())
    print("Database tables ready.")
except Exception as e:
    print(f"DB init warning: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

# ── FastAPI backend — background with auto-restart ────────────────────────────
# Runs on internal port 8000. Restarts automatically if it crashes.
# Render does NOT monitor this port — Streamlit ($PORT) is the health target.
(
  while true; do
    echo "[FastAPI] starting on :8000 ..."
    uvicorn app.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      --workers 1 \
      --log-level info
    echo "[FastAPI] exited (code $?), restarting in 5 s ..."
    sleep 5
  done
) &

# Give FastAPI a moment to bind before Streamlit starts calling it
sleep 3

# ── Streamlit frontend — foreground (Render monitors $PORT) ───────────────────
STREAMLIT_PORT="${PORT:-8501}"
echo "Starting Streamlit on :${STREAMLIT_PORT} ..."
exec streamlit run app/frontend/main.py \
  --server.port "${STREAMLIT_PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false \
  --server.enableCORS false
