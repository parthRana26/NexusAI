from sqlalchemy.orm import Session
from app.models.memory import UserMemory
from app.models.chat import ChatMessage
from app.services.ai_service import ask_ai
from app.core.logging import logger
import json

class MemoryService:
    @staticmethod
    def update_user_memory(db: Session, user_id: int, session_id: int, api_key: str = None):
        """
        Extracts key facts and a summary from the latest interaction and updates UserMemory.
        """
        try:
            # 1. Fetch the last few messages to analyze
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(2).all()
            
            if len(messages) < 2:
                return

            context = "\n".join([f"{m.role}: {m.content}" for m in reversed(messages)])
            
            # 2. Ask AI to extract a single concise fact or update existing ones
            extraction_prompt = (
                "You are a memory extraction tool. Analyze the following conversation snippet and extract ONE "
                "essential fact about the user (e.g., their name, a project they are working on, their skills, or a current goal). "
                "If no new fact is present, output 'NONE'. "
                "Keep the fact extremely concise (under 20 words).\n\n"
                f"Conversation:\n{context}\n\n"
                "Fact (JSON format: {\"fact\": \"...\", \"category\": \"...\"} or NONE):"
            )
            
            response = ask_ai([{"role": "user", "content": extraction_prompt}], api_key=api_key)
            
            if "NONE" in response.upper():
                return
            
            try:
                # Basic parsing in case AI doesn't return pure JSON
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end != -1:
                    data = json.loads(response[start:end])
                    fact_content = data.get("fact")
                    category = data.get("category", "other")
                    
                    if fact_content:
                        # 3. Save to UserMemory
                        new_memory = UserMemory(
                            user_id=user_id,
                            content=fact_content,
                            category=category
                        )
                        db.add(new_memory)
                        db.commit()
                        logger.info(f"Memory updated for user {user_id}: {fact_content}")
            except Exception as e:
                logger.error(f"Failed to parse memory extraction response: {e}")

        except Exception as e:
            logger.error(f"Error in update_user_memory: {e}")

memory_service = MemoryService()
