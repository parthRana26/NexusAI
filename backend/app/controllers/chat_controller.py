from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest
from app.services.chat_router_service import ChatRouterService
from app.services.analytics_service import save_analytics
import time
import json

class ChatController:
    @staticmethod
    def process_chat(db: Session, current_user: User, data: ChatRequest):
        start_time = time.time()
        
        # 1. Get or Create Session
        if not data.session_id or data.session_id == 0:
            session = ChatSession(
                user_id=current_user.id,
                title=data.message[:40] if hasattr(data, 'message') else data.prompt[:40]
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        else:
            session = db.query(ChatSession).filter(
                ChatSession.id == data.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")

        # 2. Save User Message
        prompt = data.message if hasattr(data, 'message') else data.prompt
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=prompt
        )
        db.add(user_msg)
        db.commit()

        # 3. Get User API Key if exists
        user_preferences = {}
        if current_user.preferences:
            try:
                user_preferences = json.loads(current_user.preferences) if isinstance(current_user.preferences, str) else current_user.preferences
            except:
                user_preferences = {}
        
        # Ensure user_preferences is always a dict before calling .get()
        if not isinstance(user_preferences, dict):
            user_preferences = {}
            
        user_api_key = user_preferences.get("groq_api_key")

        # 4. Route and Execute via AI Router
        if data.skip_routing:
            from app.services.ai_service import ask_ai
            messages = []
            if data.system_prompt:
                messages.append({"role": "system", "content": data.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            ai_reply = ask_ai(messages, api_key=user_api_key)
            result = {
                "reply": ai_reply,
                "category_detected": "direct",
                "tools_used": [],
                "citations": []
            }
        else:
            result = ChatRouterService.route_and_execute(db, current_user, prompt, session.id, api_key=user_api_key)
            ai_reply = result["reply"]

        # 5. Save AI Response
        bot_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_reply
        )
        db.add(bot_msg)
        db.commit()

        # 6. Update Summary Memory (Background fact extraction)
        try:
            from app.services.memory_service import memory_service
            memory_service.update_user_memory(db, current_user.id, session.id, api_key=user_api_key)
        except Exception as e:
            from app.core.logging import logger
            logger.error(f"Background memory update failed: {e}")

        # 5. Save Analytics
        save_analytics(
            db=db,
            user_id=current_user.id,
            endpoint="/chat",
            prompt=prompt,
            response=ai_reply,
            start_time=start_time
        )

        return {
            "session_id": session.id,
            "title": session.title,
            "reply": ai_reply,
            "response": ai_reply,
            "meta": {
                "category": result["category_detected"],
                "tools": result["tools_used"],
                "citations": result["citations"]
            }
        }

    @staticmethod
    def get_sessions(db: Session, current_user: User):
        return db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(ChatSession.created_at.desc()).all()

    @staticmethod
    def get_messages(db: Session, current_user: User, session_id: int):
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.asc()).all()
