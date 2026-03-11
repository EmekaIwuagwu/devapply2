import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.backend.api import auth, users, strategies, applications, resumes, agents

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(
    applications.router, prefix="/api/applications", tags=["Applications"]
)
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to DevApply API",
        "version": settings.APP_VERSION,
        "status": "online",
    }
