from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile_bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class LinkedInCredentialsIn(BaseModel):
    """Payload for saving LinkedIn Easy Apply credentials."""
    email: str
    password: str


class LinkedInCredentialsStatus(BaseModel):
    """What the API returns — never exposes the raw password."""
    linkedin_email: Optional[str] = None
    has_password: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None
