from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import uuid
import asyncio
from datetime import datetime
from app.backend.schemas.agent_execution import (
    AgentStatusResponse, AgentConfig, AgentExecutionResponse, AgentLogEntry
)
from app.backend.services.auth_service import get_current_user
from app.backend.database.connection import get_db
from app.backend.models.user import User
from app.backend.models.strategy import Strategy
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.services import agent_log_store

router = APIRouter()


def _run_agent_background(user_strategy: dict, user_profile: dict, task_id: str):
    """Run the agent workflow as a FastAPI background task."""
    import sys
    import asyncio
    
    # Ensure background thread can use subprocesses on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    try:
        from app.agents.executor import run_agent_workflow
        asyncio.run(run_agent_workflow(user_strategy, user_profile, task_id=task_id))
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        # Log to file for UI
        agent_log_store.add_log("ERROR", f"❌ Workflow error: {str(e) or type(e).__name__}", task_id)
        agent_log_store.set_idle(f"error: {(str(e) or type(e).__name__)[:60]}")
        # Print to console for dev
        print(f"\n--- WORKFLOW ERROR TRACEBACK ---\n{err_msg}\n---------------------------------\n")


@router.post("/start")
async def start_automation_agent(
    strategy_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start the agent workflow as a background task."""
    strategy = await db.get(Strategy, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if not strategy.target_job_titles:
        raise HTTPException(
            status_code=400,
            detail="Strategy has no target job titles. Please edit your strategy first."
        )

    user_strategy = {
        "id": str(strategy.id),
        "name": strategy.name,
        "target_job_titles": strategy.target_job_titles or [],
        "location_preference": strategy.location_preference,
        "job_types": strategy.job_types,
    }

    user_profile = {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "first_name": getattr(current_user, "first_name", ""),
        "skills": getattr(current_user, "skills", ""),
    }

    # Clear old logs and update state
    task_id = str(uuid.uuid4())
    agent_log_store.clear_logs()
    agent_log_store.set_running(task_id, "starting")
    agent_log_store.add_log("INFO", f"🔔 New run triggered by {current_user.email}", task_id)

    # Schedule the agent workflow to run in the background (non-blocking)
    background_tasks.add_task(_run_agent_background, user_strategy, user_profile, task_id)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Agent workflow is now running in the background."
    }


@router.post("/stop")
async def stop_automation_agent(current_user: User = Depends(get_current_user)):
    agent_log_store.set_idle("stopped_by_user")
    agent_log_store.add_log("WARN", f"⛔ Agent stopped by {current_user.email}")
    return {"status": "stopped"}


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(current_user: User = Depends(get_current_user)):
    """Returns real agent status from file-backed state."""
    status = agent_log_store.get_status()
    return AgentStatusResponse(
        is_running=status.get("is_running", False),
        last_run_time=datetime.now() if status.get("is_running") else None,
        last_run_status=status.get("last_run_status", "idle"),
    )


@router.get("/logs", response_model=List[AgentLogEntry])
async def fetch_agent_logs(last_n: int = 100):
    """Returns real agent logs from the file-backed store."""
    raw_logs = agent_log_store.get_logs(last_n=last_n)
    entries = []
    for entry in raw_logs:
        try:
            ts = entry.get("timestamp", datetime.now().isoformat())
            entries.append(AgentLogEntry(
                timestamp=ts,
                level=entry.get("level", "INFO"),
                message=entry.get("message", ""),
                execution_id=None,
            ))
        except Exception:
            continue
    return entries


@router.delete("/logs")
async def clear_logs(current_user: User = Depends(get_current_user)):
    agent_log_store.clear_logs()
    return {"status": "cleared"}


@router.post("/run-once", response_model=AgentExecutionResponse)
async def execute_single_agent_run(
    strategy_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    strategy = await db.get(Strategy, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    task_id = str(uuid.uuid4())
    user_strategy = {"id": str(strategy.id), "name": strategy.name, "target_job_titles": strategy.target_job_titles or []}
    user_profile = {"email": current_user.email}

    agent_log_store.clear_logs()
    agent_log_store.set_running(task_id, "starting")
    background_tasks.add_task(_run_agent_background, user_strategy, user_profile, task_id)

    return AgentExecutionResponse(
        execution_id=uuid.UUID(task_id),
        status="started",
        start_time=datetime.now(),
    )


@router.post("/config", response_model=AgentConfig)
async def configure_agent_parameters(config: AgentConfig):
    return config
