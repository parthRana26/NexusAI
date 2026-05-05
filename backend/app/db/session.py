from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

# Production-grade engine configuration
# pool_size: The number of connections to keep open
# max_overflow: How many connections to allow beyond pool_size
# pool_timeout: How long to wait for a connection before failing
# pool_recycle: How often to recycle connections (prevents stale DB connections)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """
    Dependency to get a DB session.
    Ensures the session is closed after use and handles rollback on errors.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()