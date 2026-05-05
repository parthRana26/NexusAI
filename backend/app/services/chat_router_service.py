import json
import re
from typing import Dict, Any, List
from app.services.ai_service import ask_ai
from app.services.web_search_service import web_search_service
from app.services.news_service import news_service
from app.services.finance_service import finance_service
from app.services.wiki_service import wiki_service
from app.services.generator_service import GeneratorService
from app.services.file_service import FileService
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.memory import UserMemory
from app.core.logging import logger
from app.core.constants import NEXUS_AI_IDENTITY

class ChatRouterService:
    @staticmethod
    def classify_intent(message: str, api_key: str = None) -> Dict[str, Any]:
        """
        Uses LLM to classify user intent into one of the categories.
        """
        system_prompt = f"""
        {NEXUS_AI_IDENTITY}
        You are an intelligent intent classifier for NexusAI.
        Classify the user message into exactly one of these categories:
        - normal_chat: General conversation, greetings, philosophical questions.
        - memory: Questions about previous interactions or user facts ("What did I say yesterday?", "What is my job?").
        - files_rag: Questions about uploaded documents ("Summarize my PDF", "What is in my file?").
        - web_search: General knowledge questions that might need up-to-date info ("Who is Elon Musk?", "Current status of X").
        - news: Latest news or current events ("AI news today", "What happened in Gaza?").
        - wikipedia: Encyclopedic information requests.
        - finance: Stock prices, financial trends, or market data.
        - generator: Content creation requests ("Write an email", "Make an IG post", "Create a prompt").
        - hybrid: Complex requests combining multiple tools ("Get AI news and write a tweet about it").

        Return ONLY a JSON object:
        {{"category": "...", "confidence": 0.xx, "reason": "..."}}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = ask_ai(messages, api_key=api_key)
            # Basic JSON extraction
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"category": "normal_chat", "confidence": 0.5, "reason": "Parsing failed"}
        except Exception as e:
            logger.error(f"Classification Error: {e}", exc_info=True)
            return {"category": "normal_chat", "confidence": 0.1, "reason": str(e)}

    @staticmethod
    def route_and_execute(db: Session, user: User, message: str, session_id: int = None, api_key: str = None) -> Dict[str, Any]:
        # 1. Classify
        intent = ChatRouterService.classify_intent(message, api_key=api_key)
        category = intent.get("category", "normal_chat")
        confidence = intent.get("confidence", 0.0)
        
        # 2. Execution Logic
        reply = ""
        mode_used = category
        tools_used = []
        citations = []
        suggestions = ["Tell me more", "How does this work?", "Summarize this"]

        try:
            if category == "files_rag":
                result = FileService.ask_question(user.id, message, db=db, api_key=api_key)
                reply = result["answer"]
                mode_used = result["source_mode"]
                citations = result["citations"]
                tools_used = ["rag_engine"]
            
            elif category == "generator":
                # Use a general generation prompt via AI service
                gen_prompt = f"Act as a professional content generator. {message}. Return only the generated content."
                reply = ask_ai([{"role": "user", "content": gen_prompt}], api_key=api_key)
                tools_used.append("generator_engine")
            
            elif category == "news":
                results = news_service.get_news(message)
                context = "\n\n".join([f"Title: {r['title']}\nSource: {r['source']}\nContent: {r['description']}" for r in results])
                prompt = f"Using the following news results, answer the user's query: {message}\n\nNews Context:\n{context}"
                reply = ask_ai([{"role": "user", "content": prompt}], api_key=api_key)
                tools_used.append("gnews_api")
                citations = [r['url'] for r in results]
            
            elif category == "web_search":
                results = web_search_service.search(message)
                context = "\n\n".join([f"Title: {r['title']}\nContent: {r['content']}" for r in results])
                prompt = f"Using the following web search results, answer: {message}\n\nSearch Context:\n{context}"
                reply = ask_ai([{"role": "user", "content": prompt}], api_key=api_key)
                tools_used.append("tavily_search")
                citations = [r['url'] for r in results]

            elif category == "finance":
                # Try to extract symbol
                symbol_match = re.search(r'\b[A-Z]{1,5}\b', message)
                symbol = symbol_match.group() if symbol_match else "AAPL"
                stock_data = finance_service.get_stock_quote(symbol)
                prompt = f"The user asked about finance/stocks. Here is data for {symbol}: {stock_data}. Answer the user: {message}"
                reply = ask_ai([{"role": "user", "content": prompt}], api_key=api_key)
                tools_used.append("alpha_vantage")

            elif category == "wikipedia":
                results = wiki_service.search(message)
                reply = results[0] if results else "I couldn't find anything on Wikipedia."
                tools_used.append("wikipedia_api")

            elif category == "memory":
                # Fetch long-term facts
                memories = db.query(UserMemory).filter(UserMemory.user_id == user.id).all()
                mem_context = "\n".join([f"- {m.category}: {m.content}" for m in memories])
                
                # Fetch short-term session history
                history_str = ""
                if session_id:
                    from app.models.chat import ChatMessage
                    history = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.desc()).limit(5).all()
                    history_str = "\n".join([f"{m.role}: {m.content}" for m in reversed(history)])

                prompt = f"The user is asking about their past. Facts:\n{mem_context}\n\nRecent History:\n{history_str}\n\nQuestion: {message}"
                reply = ask_ai([{"role": "user", "content": prompt}], api_key=api_key)
                tools_used.append("postgres_memory")

            elif category == "hybrid":
                # Special hybrid logic (simplified for now: search + chat)
                search_results = web_search_service.search(message)
                context = "\n\n".join([f"Content: {r['content']}" for r in search_results])
                prompt = f"This is a hybrid request. Use these search results to fulfill it: {message}\n\nContext:\n{context}"
                reply = ask_ai([{"role": "user", "content": prompt}], api_key=api_key)
                tools_used.extend(["tavily_search", "hybrid_router"])

            else: # normal_chat
                # 1. Fetch Long-term memory (Summary Memory)
                memories = db.query(UserMemory).filter(UserMemory.user_id == user.id).limit(10).all()
                summary_memory = "\n".join([f"- {m.content}" for m in memories]) if memories else "No previous facts known."
                
                # 2. Fetch Recent Messages (Last 5)
                recent_messages_str = "No recent messages."
                if session_id:
                    from app.models.chat import ChatMessage
                    history = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.desc()).limit(6).all()
                    # We take 6 because the current message was already saved, we want the 5 BEFORE it.
                    # Actually, the user asked for "last 5 messages of the conversation (full context)".
                    recent_history = history[1:6] if len(history) > 1 else []
                    recent_messages_str = "\n".join([f"{m.role}: {m.content}" for m in reversed(recent_history)])

                # 3. Construct Conversational Prompt with Strict Identity
                system_prompt = (
                    "You are NexusAI, a professional and helpful conversational AI assistant.\n"
                    "When asked who or what you are, respond as: 'I’m NexusAI, your AI-powered assistant designed to help with tasks like chatting, document analysis, prompt optimization, and more.'\n"
                    "Respond naturally like a human. Keep responses clear, helpful, and concise.\n"
                    "Do not generate titles, summaries, or structured sections.\n"
                    "Use previous conversation context silently to improve responses.\n"
                    "Always represent yourself as NexusAI. Never give generic identity responses."
                )

                user_prompt = (
                    "CONTEXT PROVIDED (USE SILENTLY):\n"
                    f"- Summary Memory: {summary_memory}\n"
                    f"- Recent History: {recent_messages_str}\n\n"
                    f"USER INPUT: {message}"
                )

                prompt_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                    
                reply = ask_ai(prompt_messages, api_key=api_key)
                mode_used = "structured_tool_mode"

        except Exception as e:
            logger.error(f"Routing Execution Error: {e}", exc_info=True)
            reply = "I encountered an error while processing your request. Please try again."

        return {
            "reply": reply,
            "category_detected": category,
            "confidence": confidence,
            "mode_used": mode_used,
            "tools_used": tools_used,
            "citations": citations,
            "suggestions": suggestions
        }
