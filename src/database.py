"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from src.config import settings


# Create database engine
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.warning(f"Database engine creation failed: {e}")
    logger.info("Application will run in memory-only mode")
    # Create a fallback engine (SQLite in-memory for demo)
    engine = create_engine("sqlite:///:memory:", echo=settings.DEBUG)


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    """
    Database session dependency for FastAPI
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test database connection
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False