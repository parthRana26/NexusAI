from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_chats: int
    files_uploaded: int
    content_generated: int
    last_login: Optional[datetime] = None
    total_messages: int
    memory_count: int = 0
    storage_used_bytes: int = 0
