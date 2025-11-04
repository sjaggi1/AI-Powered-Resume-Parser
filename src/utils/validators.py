# src/utils/validators.py

from pydantic import BaseModel
from typing import List, Optional
import os
import re
from src.config import settings

# ---------- RESUME SCHEMA ----------

class ContactInfo(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]
    location: Optional[str]
    portfolio: Optional[str]


class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: List[str] = []


class Education(BaseModel):
    institution: str
    degree: str
    start_date: Optional[str]
    end_date: Optional[str]


class Project(BaseModel):
    title: str
    description: Optional[str]
    link: Optional[str]


class Resume(BaseModel):
    name: str
    contact_info: ContactInfo
    summary: Optional[str]
    work_experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    skills: List[str] = []
    tools: List[str] = []

# ---------- VALIDATION HELPERS ----------

def validate_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(email_regex, email))


def validate_phone(phone: str) -> bool:
    phone_regex = r"^\+?[0-9]{7,15}$"
    return bool(re.match(phone_regex, phone))


def validate_file_size(file_size: int, max_size: int) -> bool:
    """Check file size (bytes) against MAX_FILE_SIZE"""
    return file_size <= max_size


def validate_file_extension(filename: str, allowed_extensions) -> bool:
    """Validate that the file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower().replace('.', '')
    return ext in [e.lower() for e in allowed_extensions]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent unsafe paths"""
    sanitized = re.sub(r'[^A-Za-z0-9_.-]', '_', filename)
    return sanitized
