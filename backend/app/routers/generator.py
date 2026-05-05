from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.generator import (
    EmailGenerateRequest, EmailGenerateResponse,
    InstagramGenerateRequest, InstagramGenerateResponse,
    FacebookGenerateRequest, FacebookGenerateResponse,
    TwitterGenerateRequest, TwitterGenerateResponse,
    PromptGenerateRequest, PromptGenerateResponse,
    BlogGenerateRequest, BlogGenerateResponse,
    ProductGenerateRequest, ProductGenerateResponse,
    LinkedInGenerateRequest, LinkedInGenerateResponse,
    TemplateListResponse
)
from app.services.generator_service import GeneratorService
from app.services.analytics_service import save_analytics
from app.db.session import get_db
from sqlalchemy.orm import Session
import time

router = APIRouter(prefix="/generate", tags=["AI Generator Suite"])

@router.post("/email", response_model=EmailGenerateResponse)
def generate_email(data: EmailGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate professional emails."""
    start_time = time.time()
    try:
        result = GeneratorService.generate_email(data.type, data.topic, data.recipient, data.tone)
        save_analytics(db, current_user.id, "/generate/email", data.topic, str(result), start_time)
        return result
    except Exception as e:
        save_analytics(db, current_user.id, "/generate/email", data.topic, str(e), start_time, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram", response_model=InstagramGenerateResponse)
def generate_instagram(data: InstagramGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate Instagram captions."""
    start_time = time.time()
    try:
        result = GeneratorService.generate_instagram(data.topic, data.tone)
        save_analytics(db, current_user.id, "/generate/instagram", data.topic, str(result), start_time)
        return result
    except Exception as e:
        save_analytics(db, current_user.id, "/generate/instagram", data.topic, str(e), start_time, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/facebook", response_model=FacebookGenerateResponse)
def generate_facebook(data: FacebookGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate Facebook posts."""
    try:
        return GeneratorService.generate_facebook(data.topic, data.tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twitter", response_model=TwitterGenerateResponse)
def generate_twitter(data: TwitterGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate Twitter/X threads."""
    try:
        return GeneratorService.generate_twitter(data.topic, data.tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prompt", response_model=PromptGenerateResponse)
def generate_prompt(data: PromptGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate optimized AI prompts."""
    try:
        return GeneratorService.generate_prompt(data.goal, data.tool)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blog", response_model=BlogGenerateResponse)
def generate_blog(data: BlogGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate blog articles."""
    try:
        return GeneratorService.generate_blog(data.topic, data.words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/product", response_model=ProductGenerateResponse)
def generate_product(data: ProductGenerateRequest, current_user: User = Depends(get_current_user)):
    """Generate product descriptions."""
    try:
        return GeneratorService.generate_product(data.product_name, data.target_audience)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/linkedin", response_model=LinkedInGenerateResponse)
def generate_linkedin(data: LinkedInGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate LinkedIn posts."""
    start_time = time.time()
    try:
        result = GeneratorService.generate_linkedin(data.topic)
        save_analytics(db, current_user.id, "/generate/linkedin", data.topic, str(result), start_time)
        return result
    except Exception as e:
        save_analytics(db, current_user.id, "/generate/linkedin", data.topic, str(e), start_time, status="error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=TemplateListResponse)
def get_templates(current_user: User = Depends(get_current_user)):
    """List all available generator templates."""
    return {"templates": GeneratorService.get_templates()}
