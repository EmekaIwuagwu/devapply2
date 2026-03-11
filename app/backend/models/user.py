from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.backend.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    profile_bio = Column(Text)
    linkedin_url = Column(String(255))
    github_url = Column(String(255))
    portfolio_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # LinkedIn Easy Apply credentials (password is Fernet-encrypted at rest)
    linkedin_email = Column(String(255), nullable=True)
    linkedin_password_encrypted = Column(Text, nullable=True)
