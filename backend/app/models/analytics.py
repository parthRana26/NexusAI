from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.db.session import Base


class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String, nullable=False)
    prompt_length = Column(Integer, default=0)
    response_length = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    status = Column(String, default="success")
    created_at = Column(DateTime, default=datetime.utcnow)