from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FileBase(BaseModel):
    filename: str
    category: str
    file_size: int
    file_type: str

class FileCreate(FileBase):
    user_id: int
    file_path: str

class FileResponse(FileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FileAskRequest(BaseModel):
    question: str
    file_id: Optional[int] = None
    category: Optional[str] = None

class FileAskResponse(BaseModel):
    answer: str
    source_mode: str
    relevance_score: float
    citations: List[str]
    suggestions: List[str]
    tools_used: List[str]

class ToolSearchRequest(BaseModel):
    query: str

class ToolNewsRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class ToolFinanceRequest(BaseModel):
    symbol: str

class ToolWikiRequest(BaseModel):
    query: str
