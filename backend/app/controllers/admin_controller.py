from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
import csv
import io

from app.models.user import User
from app.models.file import File
from app.models.chat import ChatSession
from app.models.analytics import AnalyticsLog
from app.schemas.user import UserAdminUpdate

import json
from app.core.logging import logger

class AdminController:
    @staticmethod
    def _format_user(u: User):
        """Helper to convert User ORM to JSON-safe dict with parsed preferences."""
        prefs = u.preferences
        if isinstance(prefs, str):
            try:
                prefs = json.loads(prefs)
            except:
                prefs = {}
        
        return {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "avatar_url": u.avatar_url,
            "preferences": prefs,
            "last_login": u.last_login,
            "created_at": u.created_at,
            "updated_at": u.updated_at
        }
    @staticmethod
    def get_dashboard_stats(db: Session):
        total_users = db.query(User).count()
        total_files = db.query(File).count()
        total_chats = db.query(ChatSession).count()
        total_generations = db.query(AnalyticsLog).filter(
            AnalyticsLog.endpoint.contains("generator")
        ).count()
        active_today = db.query(User).filter(
            User.last_login >= datetime.utcnow() - timedelta(days=1)
        ).count()
        new_users_7d = db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()

        return {
            "total_users": total_users,
            "total_files": total_files,
            "total_chats": total_chats,
            "total_generations": total_generations,
            "active_today": active_today,
            "new_users_7d": new_users_7d
        }

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100):
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            return [AdminController._format_user(u) for u in users]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserAdminUpdate):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(404, "User not found")
        
        if user_update.is_active is not None:
            db_user.is_active = user_update.is_active
        if user_update.role is not None:
            db_user.role = user_update.role
        
        db.commit()
        db.refresh(db_user)
        return AdminController._format_user(db_user)

    @staticmethod
    def get_usage_stats(db: Session):
        usage_data = db.query(
            AnalyticsLog.endpoint,
            func.count(AnalyticsLog.id).label("count")
        ).group_by(AnalyticsLog.endpoint).all()

        modules = {"chat": 0, "generator": 0, "files": 0, "tools": 0, "others": 0}
        for endpoint, count in usage_data:
            if "chat" in endpoint: modules["chat"] += count
            elif "generator" in endpoint: modules["generator"] += count
            elif "files" in endpoint or "upload" in endpoint: modules["files"] += count
            elif "tools" in endpoint: modules["tools"] += count
            else: modules["others"] += count

        return {
            "breakdown": modules,
            "raw_endpoints": {e: c for e, c in usage_data}
        }
