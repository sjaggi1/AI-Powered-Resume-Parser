"""
AI-Powered Resume Parser API
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
from loguru import logger

from src.config import settings
from src.database import engine, Base
from src.api.routes import health, resumes, matching, analytics

# Configure logger
logger.add("logs/api_{time}.log", rotation="500 MB", retention="10 days", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting up AI Resume Parser API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Resume Parser API...")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description="""
    ## AI-Powered Resume Parser API
    
    An intelligent resume parsing system that uses advanced AI/ML technologies to extract,
    analyze, and structure information from various resume formats.
    
    ### Key Features
    - 📄 Multi-format support (PDF, DOCX, TXT, Images)
    - 🤖 AI-powered data extraction using GPT-4
    - 🎯 Intelligent job matching with relevancy scoring
    - 📊 Comprehensive analytics and insights
    - ⚡ Real-time processing status tracking
    - 🔒 Secure and scalable architecture
    
    ### Authentication
    Use Bearer token authentication for all endpoints (except /health)
    
    ### Rate Limits
    - 1000 requests per hour per API key
    - Maximum file size: 10MB
    
    ### Support
    For issues or questions, contact: ai-hackathon2025@geminisolutions.com
    """,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "API Support",
        "email": "ai-hackathon2025@geminisolutions.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.3f}s"
    )
    
    return response


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "NOT_FOUND",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
            "path": str(request.url.path)
        }
    )


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["System"])
app.include_router(resumes.router, prefix="/api/v1", tags=["Resume Processing"])
app.include_router(matching.router, prefix="/api/v1", tags=["Resume Processing"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to documentation"""
    return {
        "message": "Welcome to AI-Powered Resume Parser API",
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for API authentication"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )