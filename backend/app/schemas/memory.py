from pydantic import BaseModel
from typing import List, Optional


class MemoryCreate(BaseModel):
    """Payload for creating a memory (manual endpoint)."""
    content: str
    category: Optional[str] = None  # optional; auto‑extracted memories will set it


class MemoryOut(BaseModel):
    id: int
    user_id: int
    content: str
    category: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True


class MemoryStats(BaseModel):
    total_memories: int
    recent_preview: List[MemoryOut] = []
