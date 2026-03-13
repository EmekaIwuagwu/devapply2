from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.backend.database.connection import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10))  # PDF, DOCX
    detected_skills = Column(JSON)
    is_primary = Column(Boolean, default=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    version_of = Column(String(36), ForeignKey("resumes.id"), nullable=True)

    user = relationship("User", backref="resumes")
    # version relationship would be many-to-one to self
    parent_version = relationship("Resume", remote_side=[id], backref="versions")
