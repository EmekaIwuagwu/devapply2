from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.backend.database.connection import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    strategy_id = Column(String(36), ForeignKey("strategies.id"), nullable=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    platform = Column(String(50))  # LinkedIn, Indeed, Google Jobs
    job_url = Column(String(500), nullable=False)
    job_description = Column(Text)
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    customized_resume_id = Column(String(36), ForeignKey("resumes.id"))
    status = Column(String(50), default="Pending")  # Pending, Rejected, Interview, etc.
    match_score = Column(Integer)  # 0-100
    ai_recommendation = Column(Text)
    submission_success = Column(Boolean)
    error_message = Column(Text)
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime(timezone=True))
    user_outcome = Column(String(50))

    user = relationship("User", backref="applications")
    strategy = relationship("Strategy", backref="applications")
    resume = relationship("Resume", backref="applications")
