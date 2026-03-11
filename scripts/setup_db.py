import asyncio
from app.backend.database.connection import engine, Base
from app.backend.models import User, Strategy, Resume, Application, AgentExecution


async def init_db():
    print("Initializing database...")
    async with engine.begin() as conn:
        # For development, we can drop and recreate or just create
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
