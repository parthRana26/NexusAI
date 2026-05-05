from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.analytics import AnalyticsLog
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/me")
def my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(AnalyticsLog).filter(
        AnalyticsLog.user_id == current_user.id
    ).count()

    return {
        "user_id": current_user.id,
        "total_requests": total
    }

@router.get("/admin")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total_requests = db.query(AnalyticsLog).count()

    active_users = db.query(
        func.count(func.distinct(AnalyticsLog.user_id))
    ).scalar()

    if active_users is None:
        active_users = 0

    return {
        "total_requests": total_requests,
        "active_users": active_users
    }