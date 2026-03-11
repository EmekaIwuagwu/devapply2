from celery import Celery
import asyncio
import os

# Use SQLite as broker if Redis is not configured
BROKER_URL = os.getenv("CELERY_BROKER_URL", "sqla+sqlite:///./celery_broker.db")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "db+sqlite:///./celery_results.db")

celery_app = Celery(
    "devapply_tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

# Important: Ensure tasks are always discovered
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)


@celery_app.task(name="tasks.run_agent", bind=True)
def run_agent_task(self, user_strategy: dict, user_profile: dict):
    """Celery task to run the agent workflow in the background."""
    task_id = self.request.id or "manual"
    try:
        self.update_state(state="STARTED", meta={"status": "Agent workflow starting..."})
        from app.agents.executor import run_agent_workflow
        # Create a new event loop for the async workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                run_agent_workflow(user_strategy, user_profile, task_id=task_id)
            )
        finally:
            loop.close()
        return {"status": "completed", "result": str(result)}
    except Exception as e:
        from app.backend.services.agent_log_store import add_log, set_idle
        add_log("ERROR", f"❌ Celery task failed: {str(e)[:200]}", task_id)
        set_idle(f"error: {str(e)[:60]}")
        self.update_state(state="FAILURE", meta={"status": f"Error: {str(e)}"})
        raise
