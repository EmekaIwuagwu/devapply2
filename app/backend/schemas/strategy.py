from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_job_titles: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    job_types: Optional[List[str]] = None
    location_preference: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    years_experience_required: Optional[int] = None


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(StrategyBase):
    pass


class StrategyResponse(StrategyBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
