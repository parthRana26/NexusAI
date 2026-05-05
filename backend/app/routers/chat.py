from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatSessionResponse, ChatMessageDetail
from app.core.security import get_current_user
from app.controllers.chat_controller import ChatController

router = APIRouter(prefix="/chat", tags=["AI Chat"])

@router.post("/")
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ChatController.process_chat(db, current_user, data)

@router.post("/message")
def chat_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Support both / and /message for frontend compatibility
    return ChatController.process_chat(db, current_user, data)

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ChatController.get_sessions(db, current_user)

@router.get("/{session_id}/messages", response_model=List[ChatMessageDetail])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ChatController.get_messages(db, current_user, session_id)