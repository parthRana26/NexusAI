from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
import json
import os
from pydantic import field_validator

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "NexusAI"
    ENVIRONMENT: str = "development"  # development / production
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./app/nexusai.db"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        if v.startswith("postgresql://") and "+psycopg2" not in v:
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # AI Suite
    GROQ_API_KEY: str = ""
    AI_PROVIDER: str = "groq"
    AI_MODEL: str = "llama-3.3-70b-versatile"

    # Qdrant & RAG Settings
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "nexusai_vectors"
    HF_TOKEN: str = ""

    # OCR Settings
    OCR_API_KEY: str = ""
    OCR_PROVIDER: str = "ocrspace"

    # Tool APIs
    TAVILY_API_KEY: str = ""
    GNEWS_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()