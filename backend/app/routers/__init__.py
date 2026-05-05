from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.user import router as user_router
from app.routers.dashboard import router as dashboard_router
from app.routers.analytics import router as analytics_router
from app.routers.memory import router as memory_router
from app.routers.files import router as files_router
from app.routers.generator import router as generator_router
from app.routers.tools import router as tools_router
from app.routers.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(user_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(memory_router)
api_router.include_router(files_router)
api_router.include_router(generator_router)
api_router.include_router(tools_router)
api_router.include_router(admin_router)
