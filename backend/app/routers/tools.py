from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.file import ToolSearchRequest, ToolNewsRequest, ToolFinanceRequest, ToolWikiRequest
from app.services.web_search_service import web_search_service
from app.services.news_service import news_service
from app.services.finance_service import finance_service
from app.services.wiki_service import wiki_service
from app.services.analytics_service import save_analytics
from app.db.session import get_db
from sqlalchemy.orm import Session
import time

router = APIRouter(prefix="/tools", tags=["Intelligence Tools"])

@router.post("/search")
def tool_search(data: ToolSearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Web search tool."""
    start_time = time.time()
    results = web_search_service.search(data.query)
    save_analytics(db, current_user.id, "/tools/search", data.query, str(results), start_time)
    return {"results": results}

@router.post("/news")
def tool_news(data: ToolNewsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Latest news tool."""
    start_time = time.time()
    results = news_service.get_news(data.query, data.limit)
    save_analytics(db, current_user.id, "/tools/news", data.query, str(results), start_time)
    return {"results": results}

@router.post("/finance")
def tool_finance(data: ToolFinanceRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Stock/Finance tool."""
    start_time = time.time()
    results = finance_service.get_stock_quote(data.symbol)
    save_analytics(db, current_user.id, "/tools/finance", data.symbol, str(results), start_time)
    return {"results": results}

@router.post("/wiki")
def tool_wiki(data: ToolWikiRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Wikipedia information tool."""
    start_time = time.time()
    results = wiki_service.search(data.query)
    save_analytics(db, current_user.id, "/tools/wiki", data.query, str(results), start_time)
    return {"results": results}
