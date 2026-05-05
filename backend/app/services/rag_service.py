import os
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document
from app.core.config import settings
from app.core.logging import logger

class RAGService:
    def __init__(self):
        try:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
        except Exception as e:
            logger.error(f"CRITICAL: Failed to initialize Qdrant client: {e}")
            self.client = None

        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._model = None
        
        # Initial attempt to load model
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"RAG model failed to load during startup: {e}")
        
        if self.client:
            self._ensure_collection()

    def _load_model(self):
        """Loads the SentenceTransformer model."""
        logger.info(f"Loading RAG model: all-MiniLM-L6-v2...")
        self._model = SentenceTransformer('all-MiniLM-L6-v2', token=settings.HF_TOKEN)
        logger.info("RAG model loaded successfully.")

    @property
    def model(self):
        """Lazy property to get or load the model."""
        if self._model is None:
            try:
                self._load_model()
            except Exception as e:
                logger.error(f"Failed to lazy-load RAG model: {e}")
        return self._model

    def _ensure_collection(self):
        if not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=models.Distance.COSINE
                    ),
                )
                # Create payload indexes for faster filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="user_id",
                    field_schema=models.PayloadSchemaType.INTEGER,
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="file_id",
                    field_schema=models.PayloadSchemaType.INTEGER,
                )
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        from app.services.ocr_service import ocr_service
        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
                
                # If very little text extracted, might be a scanned PDF
                if len(text.strip()) < 100:
                    logger.info(f"Low text detected in {file_path}, falling back to OCR...")
                    text = ocr_service.extract_text_from_image(file_path)
            elif ext == ".docx":
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
                text = ocr_service.extract_text_from_image(file_path)
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext in [".csv", ".xlsx"]:
                import pandas as pd
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                text = df.to_string()
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
        return text

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        chunks = []
        if not text:
            return chunks
        
        # Clean text: remove multiple newlines and extra spaces
        text = " ".join(text.split())
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
        return chunks

    def index_document(self, user_id: int, file_id: int, file_path: str):
        if not self.model:
            logger.error("Cannot index document, model not available.")
            return

        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        if not chunks:
            return
            
        points = []
        for i, chunk in enumerate(chunks):
            # Convert chunk to vector
            vector = self.model.encode(chunk).tolist()
            
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user_id": user_id,
                    "file_id": file_id,
                    "content": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "file_path": os.path.basename(file_path)
                    }
                }
            ))
        
        # Batch upsert
        if self.client:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def query(self, user_id: int, question: str, limit: int = 10, file_id: int = None) -> Dict[str, Any]:
        if not self.model:
            logger.error("Cannot query, model not available.")
            return {"chunks": [], "max_score": 0}

        query_vector = self.model.encode(question).tolist()
        
        must_filter = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id)
            )
        ]
        
        if file_id:
            must_filter.append(
                models.FieldCondition(
                    key="file_id",
                    match=models.MatchValue(value=file_id)
                )
            )

        if not self.client:
            return {"chunks": [], "max_score": 0}

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=models.Filter(must=must_filter),
            limit=limit,
            with_payload=True
        )
        
        relevant_chunks = []
        max_score = 0
        for res in results.points:
            if res.score > max_score:
                max_score = res.score
            relevant_chunks.append({
                "content": res.payload["content"],
                "score": res.score,
                "file_path": res.payload["metadata"]["file_path"]
            })

        return {
            "chunks": relevant_chunks,
            "max_score": max_score
        }

    def delete_file_vectors(self, user_id: int, file_id: int):
        if not self.client:
            return
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        ),
                        models.FieldCondition(
                            key="file_id",
                            match=models.MatchValue(value=file_id)
                        )
                    ]
                )
            )
        )

rag_service = RAGService()
