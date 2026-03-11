from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.backend.models.application import Application
from app.backend.schemas.application import ApplicationCreate, ApplicationUpdate
from typing import List
import uuid
from datetime import datetime, timedelta


async def get_applications(db: AsyncSession, user_id: uuid.UUID) -> List[Application]:
    result = await db.execute(select(Application).where(Application.user_id == user_id))
    return result.scalars().all()


async def get_application(
    db: AsyncSession, application_id: uuid.UUID, user_id: uuid.UUID
) -> Application:
    result = await db.execute(
        select(Application).where(
            Application.id == application_id, Application.user_id == user_id
        )
    )
    return result.scalars().first()


async def create_application(
    db: AsyncSession, application: ApplicationCreate, user_id: uuid.UUID
) -> Application:
    db_application = Application(**application.dict(), user_id=user_id)
    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)
    return db_application


async def update_application(
    db: AsyncSession,
    application_id: uuid.UUID,
    application_update: ApplicationUpdate,
    user_id: uuid.UUID,
) -> Application:
    db_application = await get_application(db, application_id, user_id)
    if not db_application:
        return None

    update_data = application_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)

    await db.commit()
    await db.refresh(db_application)
    return db_application


async def get_stats(db: AsyncSession, user_id: uuid.UUID) -> dict:
    # Total apps
    result = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total = result.scalar() or 0

    # Apps this week
    one_week_ago = datetime.now() - timedelta(days=7)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id, Application.applied_date >= one_week_ago
        )
    )
    this_week = result.scalar() or 0

    # Success rate (Placeholder: percentage of applications that reached 'Interview' stage)
    result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id, Application.status == "Interview"
        )
    )
    interviews = result.scalar() or 0
    success_rate = (interviews / total * 100) if total > 0 else 0.0

    return {
        "total_applications": total,
        "success_rate": success_rate,
        "applications_this_week": this_week,
        "average_response_time": None,
    }
