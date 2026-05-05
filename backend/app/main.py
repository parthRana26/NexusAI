from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import time
import logging
from collections import defaultdict

from app.routers import api_router
from app.db.session import Base, engine
from app.core.config import settings
from app.core.logging import setup_logging, logger

# 1. Initialize Logging
setup_logging()

# 2. Initialize Database (In development, use Alembic migrations)
# Base.metadata.create_all is removed for production-readiness in favor of Alembic.
if settings.ENVIRONMENT == "development":
    logger.info("Initializing database tables for development...")
    Base.metadata.create_all(bind=engine)

# 3. App Initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NexusAI Production Backend - Enterprise AI SaaS Infrastructure.",
    version="1.0.5",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# 4. CORS & Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Store
rate_limit_store = defaultdict(list)
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < RATE_LIMIT_PERIOD]
    
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_CALLS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    rate_limit_store[client_ip].append(now)
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Relax CSP for docs to allow CDN assets (Swagger UI, Redoc)
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com;"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
    return response

# 5. Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Error: {exc.detail} on {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail, "data": None}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()} on {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "Invalid input data", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception: {str(exc)}", exc_info=True)
    message = "Internal Server Error" if settings.ENVIRONMENT == "production" else str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": message, "data": None}
    )

# 6. Base Routes
@app.get("/", tags=["General"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "private"
    }

# 7. Include API Router
app.include_router(api_router, prefix="/api/v1")