import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user profile.
    """
    # Parse preferences if stored as string
    if isinstance(current_user.preferences, str):
        try:
            current_user.preferences = json.loads(current_user.preferences)
        except:
            current_user.preferences = {}
    return current_user

@router.patch("/profile", response_model=UserResponse)
def update_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user profile.
    """
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.avatar_url is not None:
        current_user.avatar_url = user_in.avatar_url
    if user_in.preferences is not None:
        current_user.preferences = json.dumps(user_in.preferences)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # Parse back for response
    if isinstance(current_user.preferences, str):
        try:
            current_user.preferences = json.loads(current_user.preferences)
        except:
            current_user.preferences = {}
            
    return current_user
