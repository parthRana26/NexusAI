from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.models.file import File
from app.models.content import Content
from app.schemas.dashboard import DashboardStats
from app.core.security import get_current_user

from app.models.memory import UserMemory

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get aggregated statistics for the user dashboard.
    """
    # Total chats (sessions)
    total_chats = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    
    # Total messages across all sessions
    total_messages = db.query(ChatMessage).join(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    
    # Files uploaded
    files_uploaded = db.query(File).filter(File.user_id == current_user.id).count()
    
    # Memory count (User facts)
    memory_count = db.query(UserMemory).filter(UserMemory.user_id == current_user.id).count()
    
    # Content generated
    content_generated = db.query(Content).filter(Content.user_id == current_user.id).count()
    
    # Storage used (sum of file sizes)
    storage_used = db.query(func.sum(File.file_size)).filter(File.user_id == current_user.id).scalar() or 0
    
    return {
        "total_chats": total_chats,
        "files_uploaded": files_uploaded,
        "content_generated": content_generated,
        "last_login": current_user.last_login,
        "total_messages": total_messages,
        "memory_count": memory_count,
        "storage_used_bytes": storage_used
    }
