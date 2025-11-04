# src/config.py
import os
import json
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ==== API Configuration ====
    API_TITLE: str = "AI Resume Parser"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ==== CORS ====
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    # ==== Database ====
    DATABASE_URL: str = "postgresql://resume_user:password123@localhost:5432/resume_parser"
    SECRET_KEY: str = "your-secret-key"

    # ==== OpenAI ====
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TIMEOUT: int = 30

    # ==== File Upload Settings ====
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "doc", "txt", "jpg", "png", "jpeg"]
    UPLOAD_DIR: str = "./uploads"

    # ==== Processing Options ====
    ENABLE_OCR: bool = True
    ENABLE_AI_ENHANCEMENT: bool = True
    DEFAULT_LANGUAGE: str = "en"

    # ==== Security ====
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ==== Rate Limiting ====
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_BURST: int = 50

    # ==== Logging ====
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ==== Cache ====
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600

    # ==== Tesseract ====
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # ==== Matching ====
    MATCHING_THRESHOLD: float = 0.6
    MIN_MATCH_SCORE: int = 50
    MAX_MATCH_SCORE: int = 100

    # ==== Validators ====
    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    def parse_allowed_extensions(cls, v):
        """
        ✅ Parse ALLOWED_EXTENSIONS from .env file
        Supports:
          - Comma-separated strings → "pdf,docx,txt"
          - JSON-style lists → ["pdf","docx","txt"]
        """
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [ext.strip().lower() for ext in parsed]
            except json.JSONDecodeError:
                return [ext.strip().lower() for ext in v.split(",") if ext.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# ✅ Instantiate Settings
settings = Settings()

# ✅ Optional Debug Print
if settings.DEBUG:
    print("Loaded Allowed Extensions:", settings.ALLOWED_EXTENSIONS)
