import asyncio
from app.backend.database.connection import AsyncSessionLocal
from app.backend.services.user_service import create_user
from app.backend.schemas.user import UserCreate
from app.backend.database.connection import get_db


async def create_admin():
    async with AsyncSessionLocal() as db:
        admin_data = UserCreate(
            email="admin@example.com",
            password="password",
            first_name="Admin",
            last_name="User",
        )
        try:
            user = await create_user(db, admin_data)
            print(f"Admin user created: {user.email}")
        except Exception as e:
            print(f"Error creating admin: {e}")


if __name__ == "__main__":
    asyncio.run(create_admin())
