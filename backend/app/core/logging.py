import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    """
    Configure structured logging for the application.
    Uses standard library logging but formatted for production visibility.
    """
    log_level = logging.INFO
    if settings.DEBUG:
        log_level = logging.DEBUG

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # File Handler (Production Audit Trail)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "nexusai.log"),
        maxBytes=10*1024*1024, # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)

    # Suppress some noisy logs from dependencies
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.ERROR)

logger = logging.getLogger("nexusai")
