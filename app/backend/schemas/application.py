from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime


class ApplicationBase(BaseModel):
    job_title: str
    company_name: str
    platform: str
    job_url: str
    job_description: Optional[str] = None
    status: Optional[str] = "Pending"
    match_score: Optional[int] = None
    ai_recommendation: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    strategy_id: uuid.UUID
    customized_resume_id: Optional[uuid.UUID] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    user_outcome: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    applied_date: datetime
    customized_resume_id: Optional[uuid.UUID] = None
    submission_success: Optional[bool] = None
    error_message: Optional[str] = None
    response_received: bool
    response_date: Optional[datetime]

    class Config:
        from_attributes = True


class ApplicationStats(BaseModel):
    total_applications: int
    success_rate: float
    applications_this_week: int
    average_response_time: Optional[float] = None
