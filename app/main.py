import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.backend.api import auth, users, strategies, applications, resumes, agents


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Ensure all DB tables exist before the first request is served."""
    try:
        from app.backend.database.connection import engine, Base
        import app.backend.models.user            # noqa: F401
        import app.backend.models.strategy        # noqa: F401
        import app.backend.models.application     # noqa: F401
        import app.backend.models.resume          # noqa: F401
        import app.backend.models.agent_execution # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables verified/created on startup.")
    except Exception as exc:
        print(f"⚠️  DB startup init failed (continuing): {exc}", file=sys.stderr)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api/auth",         tags=["Authentication"])
app.include_router(users.router,        prefix="/api/users",        tags=["Users"])
app.include_router(strategies.router,   prefix="/api/strategies",   tags=["Strategies"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(resumes.router,      prefix="/api/resumes",      tags=["Resumes"])
app.include_router(agents.router,       prefix="/api/agents",       tags=["Agents"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to DevApply API",
        "version": settings.APP_VERSION,
        "status": "online",
    }
