from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.backend.services.auth_service import get_current_user
from app.backend.services import resume_service
from app.backend.database.connection import get_db
from app.backend.models.user import User
from app.config import settings

router = APIRouter()


@router.post("/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ensure storage path exists
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    file_extension = file.filename.split(".")[-1]
    file_id = uuid.uuid4()
    file_path = os.path.join(settings.STORAGE_PATH, f"{file_id}.{file_extension}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    resume_in = ResumeCreate(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file_extension.upper(),
    )
    return await resume_service.create_resume(db, resume_in, current_user.id)


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await resume_service.get_resumes(db, current_user.id)


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = await resume_service.delete_resume(db, resume_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"message": "Resume deleted"}


@router.post("/{resume_id}/customize", response_model=ResumeResponse)
async def generate_customized_resume(
    resume_id: uuid.UUID,
    job_details: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # This will be implemented in Phase 3 with AI Agents
    pass


@router.get("/{resume_id}/versions", response_model=List[ResumeResponse])
async def get_resume_versions(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Future implementation
    pass
