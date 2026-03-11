from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.backend.database.connection import Base


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_job_titles = Column(JSON)  # e.g., ["Python developer", "AI developer"]
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    job_types = Column(JSON)  # ["Full-time", "Contract"]
    location_preference = Column(JSON)  # ["Remote", "Hybrid"]
    company_sizes = Column(JSON)  # ["Startup", "Enterprise"]
    target_industries = Column(JSON)
    required_skills = Column(JSON)
    years_experience_required = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="strategies")
