import os
from sqlalchemy.orm import Session
from fastapi import UploadFile
from datetime import datetime
from app.models.file import File
from app.services.rag_service import rag_service
from app.core.config import settings
from app.core.constants import NEXUS_AI_IDENTITY
from app.core.logging import logger

class FileService:
    @staticmethod
    async def upload_file(db: Session, user_id: int, file: UploadFile, category: str):
        # Ensure uploads directory exists
        upload_dir = "app/uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save file to local storage
        file_path = os.path.join(upload_dir, f"{user_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            file_size = len(content)

        # Create database record
        db_file = File(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.content_type,
            category=category
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # Index in RAG
        try:
            rag_service.index_document(user_id, db_file.id, file_path)
        except Exception as e:
            logger.error(f"RAG Indexing Error: {e}")
            # We don't fail the whole upload if indexing fails, 
            # but in production you might want to retry or mark as "not indexed"

        return db_file

    @staticmethod
    def get_user_files(db: Session, user_id: int):
        return db.query(File).filter(File.user_id == user_id).all()

    @staticmethod
    def delete_file(db: Session, user_id: int, file_id: int):
        db_file = db.query(File).filter(File.id == file_id, File.user_id == user_id).first()
        if not db_file:
            return False

        # Delete from RAG
        try:
            rag_service.delete_file_vectors(user_id, file_id)
        except Exception as e:
            logger.error(f"RAG Deletion Error: {e}")

        # Delete from local storage
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)

        # Delete from DB
        db.delete(db_file)
        db.commit()
        return True

    @staticmethod
    def get_file_by_id(db: Session, user_id: int, file_id: int):
        return db.query(File).filter(File.id == file_id, File.user_id == user_id).first()

    @staticmethod
    def ask_question(user_id: int, question: str, file_id: int = None, db: Session = None, api_key: str = None):
        """
        Powerful intelligent query engine with intent detection and CRAG.
        """
        from app.services.ai_service import ask_ai
        from app.services.web_search_service import web_search_service
        
        # 1. Intent Detection
        q_lower = question.lower()
        is_summary = any(word in q_lower for word in ["summarize", "summary", "overview", "tl;dr", "key points"])
        is_analysis = any(word in q_lower for word in ["analyze", "analysis", "deep dive", "insights", "limitations"])
        is_extraction = any(word in q_lower for word in ["extract", "find", "identify", "total", "date", "amount"])

        # 2. Context Building
        doc_context = ""
        sources = []
        max_score = 0.0
        source_mode = "docs"
        tools_used = []
        web_context = ""

        # Global intent optimization: if specific file is provided and user wants summary/analysis
        if file_id and (is_summary or is_analysis):
            file = db.query(File).filter(File.id == file_id, File.user_id == user_id).first()
            if file:
                # Pull large text block for global context (up to 15k chars)
                doc_context = rag_service.extract_text(file.file_path)[:15000]
                sources = [os.path.basename(file.file_path)]
                max_score = 1.0 # Forced high relevance for direct file context
                source_mode = "docs (global)"
        else:
            # Standard RAG Retrieval
            search_result = rag_service.query(user_id, question, file_id=file_id)
            context_chunks = search_result["chunks"]
            max_score = search_result["max_score"]
            doc_context = "\n\n".join([c['content'] for c in context_chunks])
            sources = list(set([c['file_path'] for c in context_chunks]))

        # 3. CRAG Decision Engine (only if not in global mode)
        if source_mode != "docs (global)":
            if max_score < 0.35:
                source_mode = "web"
                web_results = web_search_service.search(question)
                web_context = "\n\n".join([f"Title: {r['title']}\nContent: {r['content']}" for r in web_results])
                tools_used.append("tavily_search")
            elif max_score < 0.65:
                source_mode = "docs+web"
                web_results = web_search_service.search(question)
                web_context = "\n\n".join([f"Title: {r['title']}\nContent: {r['content']}" for r in web_results])
                tools_used.append("tavily_search")

        # 4. Prompt Engineering
        system_prompt = f"{NEXUS_AI_IDENTITY}\nYou are NexusAI, a premium production-ready knowledge engine. "
        if is_summary:
            system_prompt += "Focus on creating a high-level summary with key takeaways and structured sections."
        elif is_analysis:
            system_prompt += "Focus on deep analysis, identifying trends, anomalies, and critical insights."
        elif is_extraction:
            system_prompt += "Focus on precision. Extract exactly what is asked in a structured format."
        else:
            system_prompt += "Provide accurate, cited answers based on available context."

        if source_mode == "docs (global)":
            prompt = f"Using the following COMPLETE document content, {question}.\n\nContext:\n{doc_context}"
        elif source_mode == "docs":
            prompt = f"Using ONLY the relevant document snippets provided, answer: {question}.\n\nContext:\n{doc_context}"
        elif source_mode == "docs+web":
            prompt = f"Combine information from internal documents and web search to answer: {question}.\n\nDoc Context:\n{doc_context}\n\nWeb Context:\n{web_context}"
        else:
            prompt = f"The documents provided little relevance. Using web knowledge, answer: {question}.\n\nWeb Context:\n{web_context}"

        # 5. Execute LLM Call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        answer = ask_ai(messages, api_key=api_key)

        return {
            "answer": answer,
            "source_mode": source_mode,
            "relevance_score": float(max_score),
            "citations": sources,
            "suggestions": ["Can you explain more?", "Summarize the key findings", "What are the limitations?"],
            "tools_used": tools_used,
            "intent": "summary" if is_summary else "analysis" if is_analysis else "query"
        }
