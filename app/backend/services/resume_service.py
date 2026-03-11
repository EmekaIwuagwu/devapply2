from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.backend.models.resume import Resume
from app.backend.schemas.resume import ResumeCreate, ResumeUpdate
import uuid
from typing import List
import os
from app.config import settings


async def get_resumes(db: AsyncSession, user_id: uuid.UUID) -> List[Resume]:
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    return result.scalars().all()


async def get_resume(
    db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
) -> Resume:
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalars().first()


async def create_resume(
    db: AsyncSession, resume: ResumeCreate, user_id: uuid.UUID
) -> Resume:
    # If this is set as primary, unset other primaries
    if resume.is_primary:
        result = await db.execute(
            select(Resume).where(Resume.user_id == user_id, Resume.is_primary == True)
        )
        existing_primaries = result.scalars().all()
        for rp in existing_primaries:
            rp.is_primary = False

    db_resume = Resume(**resume.dict())
    db.add(db_resume)
    await db.commit()
    await db.refresh(db_resume)
    return db_resume


async def delete_resume(
    db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    db_resume = await get_resume(db, resume_id, user_id)
    if not db_resume:
        return False

    # Optional: Delete file from disk
    if os.path.exists(db_resume.file_path):
        os.remove(db_resume.file_path)

    await db.delete(db_resume)
    await db.commit()
    return True
