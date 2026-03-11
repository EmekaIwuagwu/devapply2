from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime


class ResumeBase(BaseModel):
    file_name: str
    file_type: str
    detected_skills: Optional[List[str]] = None
    is_primary: bool = False


class ResumeCreate(ResumeBase):
    user_id: uuid.UUID
    file_path: str


class ResumeUpdate(BaseModel):
    is_primary: Optional[bool] = None
    detected_skills: Optional[List[str]] = None


class ResumeResponse(ResumeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    file_path: str
    upload_date: datetime
    version_of: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
