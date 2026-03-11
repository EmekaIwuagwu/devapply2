from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.schemas.user import (
    UserUpdate, UserResponse,
    LinkedInCredentialsIn, LinkedInCredentialsStatus,
)
from app.backend.services.auth_service import get_current_user
from app.backend.services import user_service
from app.backend.services.credential_service import encrypt_credential
from app.backend.database.connection import get_db
from app.backend.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Return the current logged-in user's profile."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return a specific user profile (only if it's the current user or admin)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # current_user is already fetched from DB by get_current_user
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: uuid.UUID, 
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile information."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    updated_user = await user_service.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.post("/me/linkedin-credentials", response_model=LinkedInCredentialsStatus)
async def save_linkedin_credentials(
    payload: LinkedInCredentialsIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Encrypt and persist LinkedIn Easy Apply credentials for the current user."""
    current_user.linkedin_email = payload.email
    current_user.linkedin_password_encrypted = encrypt_credential(payload.password)
    await db.commit()
    await db.refresh(current_user)
    return LinkedInCredentialsStatus(linkedin_email=current_user.linkedin_email, has_password=True)


@router.get("/me/linkedin-credentials/status", response_model=LinkedInCredentialsStatus)
async def get_linkedin_credentials_status(
    current_user: User = Depends(get_current_user),
):
    """Return whether LinkedIn credentials are stored (never exposes the raw password)."""
    return LinkedInCredentialsStatus(
        linkedin_email=current_user.linkedin_email,
        has_password=bool(current_user.linkedin_password_encrypted),
    )


@router.delete("/me/linkedin-credentials")
async def delete_linkedin_credentials(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove stored LinkedIn credentials for the current user."""
    current_user.linkedin_email = None
    current_user.linkedin_password_encrypted = None
    await db.commit()
    return {"message": "LinkedIn credentials removed"}


@router.delete("/{user_id}")
async def delete_account(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the user account."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Implement actual deletion in service if needed
    # For now, just return success
    return {"message": "Account deletion requested"}
