#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# DevApply startup script
# Launches FastAPI (port 8000) and Streamlit ($PORT) in the same container.
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "=== DevApply starting ==="

# ── Database initialisation ────────────────────────────────────────────────
# Create all tables if they don't exist yet (idempotent).
echo "Initialising database..."
python - <<'PYEOF'
import asyncio, sys
try:
    from app.backend.database.connection import engine, Base
    # Import all models so Base.metadata knows about them
    from app.backend.models import (  # noqa: F401
        user, strategy, application, resume, agent_execution
    )
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init_db())
    print("Database ready.")
except Exception as e:
    print(f"DB init warning (may already exist): {e}", file=sys.stderr)
PYEOF

# ── FastAPI backend ────────────────────────────────────────────────────────
echo "Starting FastAPI on :8000..."
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info &
BACKEND_PID=$!

# Give FastAPI a moment to bind before Streamlit starts hitting it
sleep 2

# ── Streamlit frontend ─────────────────────────────────────────────────────
# Render sets $PORT; fall back to 8501 for local runs.
STREAMLIT_PORT=${PORT:-8501}
echo "Starting Streamlit on :${STREAMLIT_PORT}..."
streamlit run app/frontend/main.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false &
FRONTEND_PID=$!

echo "=== DevApply running ==="
echo "  Backend  → http://localhost:8000"
echo "  Frontend → http://localhost:${STREAMLIT_PORT}"

# Exit if either process dies
wait -n
EXIT_CODE=$?
echo "A service exited (code ${EXIT_CODE}) — shutting down."
kill "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
exit "${EXIT_CODE}"
