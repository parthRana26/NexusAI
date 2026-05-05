from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from qdrant_client import QdrantClient
import httpx
import time
import logging

from app.db.session import get_db
from app.core.config import settings

router = APIRouter(tags=["System Monitoring"])
logger = logging.getLogger("nexusai.health")

@router.get("/health")
def health_check():
    """
    Liveness check for the API.
    Used by orchestration tools (Kubernetes, Render) to verify the process is alive.
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check verifying all external dependencies are operational.
    """
    checks = {}
    
    # 1. Database Check (Using text() to fix SQLAlchemy warning)
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        logger.error(f"Health Check - DB Error: {str(e)}")
        checks["database"] = "disconnected"

    # 2. Qdrant Check
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=5
        )
        client.get_collections()
        checks["qdrant"] = "connected"
    except Exception as e:
        logger.error(f"Health Check - Qdrant Error: {str(e)}")
        checks["qdrant"] = "disconnected"

    # 3. AI Provider Connectivity
    try:
        async with httpx.AsyncClient() as client:
            if settings.AI_PROVIDER == "groq":
                url = "https://api.groq.com/openai/v1/models"
                headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
            else:
                url = "https://api.openai.com/v1/models"
                headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
            
            resp = await client.get(url, headers=headers, timeout=5)
            checks["ai_provider"] = "reachable" if resp.status_code == 200 else f"degraded:{resp.status_code}"
    except Exception as e:
        logger.warning(f"Health Check - AI Provider Timeout/Error: {str(e)}")
        checks["ai_provider"] = "timeout"

    is_ready = all(v == "connected" or v == "reachable" for k, v in checks.items() if k != "ai_provider")
    
    return {
        "ready": is_ready,
        "status": "ready" if is_ready else "not_ready",
        "dependencies": checks
    }