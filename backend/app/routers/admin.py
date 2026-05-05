from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserAdminUpdate, AdminDashboardStats
from app.core.security import require_admin
from app.controllers.admin_controller import AdminController

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard", response_model=AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return AdminController.get_dashboard_stats(db)

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return AdminController.list_users(db, skip, limit)

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user_status(
    user_id: int,
    user_update: UserAdminUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return AdminController.update_user(db, user_id, user_update)

@router.get("/usage")
def get_usage_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return AdminController.get_usage_stats(db)
