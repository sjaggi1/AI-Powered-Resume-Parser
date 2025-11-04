"""
Health check endpoint
"""

from fastapi import APIRouter
from datetime import datetime
import time
from loguru import logger

from src.config import settings


router = APIRouter()

# Track startup time
startup_time = time.time()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns service health status and basic information
    """
    try:
        uptime = int(time.time() - startup_time)
        
        # Check database connection (if configured)
        database_status = "not_configured"
        try:
            from src.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            database_status = "connected"
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            database_status = "error"
        
        # Check AI service
        ai_status = "operational" if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-key-here" else "not_configured"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.API_VERSION,
            "uptime": uptime,
            "services": {
                "database": database_status,
                "ai_service": ai_status,
                "storage": "available"
            },
            "environment": settings.ENVIRONMENT
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }