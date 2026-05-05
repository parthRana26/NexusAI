import time
import logging
from app.models.analytics import AnalyticsLog
from app.core.logging import logger

def save_analytics(
    db,
    user_id: int,
    endpoint: str,
    prompt: str,
    response: str,
    start_time: float,
    status: str = "success"
):
    """
    Saves an analytics log to the database and logs the request to stdout.
    """
    end_time = time.time()
    duration_ms = int((end_time - start_time) * 1000)

    try:
        log = AnalyticsLog(
            user_id=user_id,
            endpoint=endpoint,
            prompt_length=len(str(prompt)),
            response_length=len(str(response)),
            response_time_ms=duration_ms,
            status=status
        )

        db.add(log)
        db.commit()
        
        # Structured log for monitoring
        logger.info(f"API Call | User: {user_id} | Path: {endpoint} | Status: {status} | Duration: {duration_ms}ms")
        
    except Exception as e:
        logger.error(f"Failed to save analytics: {str(e)}")
        db.rollback()