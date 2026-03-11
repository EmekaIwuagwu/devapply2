import asyncio
import os
import shutil
from sqlalchemy import text
from app.backend.database.connection import AsyncSessionLocal
from app.backend.services import agent_log_store

async def clear_database():
    print("🧹 Cleaning database...")
    async with AsyncSessionLocal() as db:
        # Clear Applications
        await db.execute(text("DELETE FROM applications;"))
        
        # Clear Resumes
        await db.execute(text("DELETE FROM resumes;"))
        
        await db.commit()
    print("✅ Database cleared.")

    # Clear Agent Logs
    agent_log_store.clear_logs()
    agent_log_store.set_idle("cleared")
    print("✅ Agent activity logs cleared.")

    # Clear uploaded resumes directory
    uploads_dir = "uploads/resumes"
    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir, exist_ok=True)
    print("✅ Uploaded resume files cleared.")

if __name__ == "__main__":
    asyncio.run(clear_database())
