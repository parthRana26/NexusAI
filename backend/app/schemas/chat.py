from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[int] = None
    skip_routing: Optional[bool] = False
    system_prompt: Optional[str] = None

class ChatMessageRequest(BaseModel):
    session_id: Optional[int] = None
    message: str

class ChatMessageResponse(BaseModel):
    session_id: int
    reply: str
    category_detected: str
    confidence: float
    mode_used: str
    tools_used: List[str]
    citations: List[str]
    suggestions: List[str]

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatMessageDetail(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True