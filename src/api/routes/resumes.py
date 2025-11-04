# src/api/routes/resumes.py
"""
Resume processing API endpoints
Handles resume upload, parsing, retrieval, update, and deletion
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from loguru import logger
import json

from src.services.parser_service import parser_service
from src.utils.validators import (
    validate_file_size,
    validate_file_extension,
    sanitize_filename,
    Resume  # ✅ schema imported
)
from src.config import settings

router = APIRouter()

# Temporary in-memory storage (replace with DB later)
resumes_db: Dict[str, Dict[str, Any]] = {}


# @router.post("/resumes/upload")
# async def upload_resume(
#     file: UploadFile = File(...),
#     options: Optional[str] = Form(None)
# ):
#     """
#     Upload and parse a resume file.
#     Supports multiple formats: PDF, DOCX, DOC, TXT, JPG, PNG.
#     """
#     try:
#         if not file:
#             raise HTTPException(status_code=400, detail="No file provided")

#         # Read file content
#         file_content = await file.read()

#         # ✅ Validate file size
#         if not validate_file_size(len(file_content), settings.MAX_FILE_SIZE):
#             raise HTTPException(
#                 status_code=413,
#                 detail={
#                     "error": "FILE_TOO_LARGE",
#                     "message": f"File exceeds limit ({settings.MAX_FILE_SIZE / 1024 / 1024} MB)"
#                 }
#             )

#         # ✅ Validate file extension
#         if not validate_file_extension(file.filename, settings.ALLOWED_EXTENSIONS):
#             raise HTTPException(
#                 status_code=415,
#                 detail={
#                     "error": "UNSUPPORTED_FORMAT",
#                     "message": "File format not supported",
#                     "details": {
#                         "supportedFormats": settings.ALLOWED_EXTENSIONS,
#                         "receivedFormat": file.filename.split('.')[-1]
#                     }
#                 }
#             )

#         # ✅ Sanitize filename
#         safe_filename = sanitize_filename(file.filename)

#         # ✅ Parse JSON options safely
#         parsing_options = {}
#         if options:
#             try:
#                 parsing_options = json.loads(options)
#             except json.JSONDecodeError:
#                 logger.warning(f"Invalid JSON in options: {options}")

#         # ✅ Generate unique resume ID
#         resume_id = str(uuid.uuid4())
#         logger.info(f"Processing resume upload: {safe_filename} (ID: {resume_id})")

#         # ✅ Parse resume (core logic)
#         parsed_data = await parser_service.parse_resume(file_content, safe_filename, parsing_options)

#         # ✅ Validate parsed data against Resume schema to avoid 422
#         try:
#             resume_valid = Resume(**parsed_data).dict()
#         except Exception as e:
#             logger.error(f"Resume validation failed: {e}")
#             raise HTTPException(status_code=422, detail=str(e))

#         # ✅ Store validated data in memory
#         resumes_db[resume_id] = {
#             "id": resume_id,
#             "status": "completed",
#             "data": resume_valid,
#             "uploadedAt": datetime.now().isoformat()
#         }

#         return JSONResponse(
#             status_code=202,
#             content={
#                 "id": resume_id,
#                 "status": "completed",
#                 "message": "Resume uploaded and parsed successfully",
#                 "estimatedProcessingTime": 30,
#                 "webhookUrl": None
#             }
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    options: Optional[str] = Form(None)
):
    """
    Upload and parse a resume file.
    Supports multiple formats: PDF, DOCX, DOC, TXT, JPG, PNG.
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        file_content = await file.read()

        if not validate_file_size(len(file_content), settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "FILE_TOO_LARGE",
                    "message": f"File exceeds limit ({settings.MAX_FILE_SIZE / 1024 / 1024} MB)"
                }
            )

        if not validate_file_extension(file.filename, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=415,
                detail={
                    "error": "UNSUPPORTED_FORMAT",
                    "message": "File format not supported",
                    "details": {
                        "supportedFormats": settings.ALLOWED_EXTENSIONS,
                        "receivedFormat": file.filename.split('.')[-1]
                    }
                }
            )

        safe_filename = sanitize_filename(file.filename)

        parsing_options = {}
        if options:
            try:
                parsing_options = json.loads(options)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in options: {options}")

        resume_id = str(uuid.uuid4())
        logger.info(f"Processing resume upload: {safe_filename} (ID: {resume_id})")

        # ✅ FIX: Await the async function
        parsed_data = await parser_service.parse_resume(file_content, safe_filename, parsing_options)

        # ✅ Validate the parsed data
        try:
            resume_valid = Resume(**parsed_data).dict()
        except Exception as e:
            logger.error(f"Resume validation failed: {e}")
            raise HTTPException(status_code=422, detail=str(e))

        resumes_db[resume_id] = {
            "id": resume_id,
            "status": "completed",
            "data": resume_valid,
            "uploadedAt": datetime.now().isoformat()
        }

        return JSONResponse(
            status_code=202,
            content={
                "id": resume_id,
                "status": "completed",
                "message": "Resume uploaded and parsed successfully",
                "estimatedProcessingTime": 30,
                "webhookUrl": None
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/resumes/{id}")
async def get_resume(id: str):
    """Retrieve parsed resume data by ID"""
    try:
        if id not in resumes_db:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume = resumes_db[id]
        return {"id": id, **resume["data"]}
    except Exception as e:
        logger.error(f"Error retrieving resume {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/resumes/{id}")
async def update_resume(id: str, update_data: Dict[str, Any]):
    """Update parsed resume data"""
    try:
        if id not in resumes_db:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume = resumes_db[id]
        data = resume["data"]

        # Merge updates safely
        for key, value in update_data.items():
            if key in data:
                if isinstance(data[key], dict) and isinstance(value, dict):
                    data[key].update(value)
                else:
                    data[key] = value

        resumes_db[id]["data"] = data
        return {"id": id, **data}

    except Exception as e:
        logger.error(f"Error updating resume {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/resumes/{id}")
async def delete_resume(id: str):
    """Delete a resume and all associated data"""
    try:
        if id not in resumes_db:
            raise HTTPException(status_code=404, detail="Resume not found")

        del resumes_db[id]
        logger.info(f"Resume {id} deleted successfully")

        return JSONResponse(status_code=204, content=None)

    except Exception as e:
        logger.error(f"Error deleting resume {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumes/{id}/status")
async def get_processing_status(id: str):
    """Get the current processing status of a resume"""
    try:
        if id not in resumes_db:
            raise HTTPException(status_code=404, detail="Resume not found")

        resume = resumes_db[id]
        status = resume["status"]

        if status == "completed":
            return {
                "id": id,
                "status": "completed",
                "progress": 100,
                "currentStep": "completed",
                "completedAt": resume.get("uploadedAt"),
                "processingTime": resume["data"].get("metadata", {}).get("processingTime", 0)
            }

        return {
            "id": id,
            "status": "processing",
            "progress": 50,
            "currentStep": "ai_parsing",
            "estimatedTimeRemaining": 20
        }

    except Exception as e:
        logger.error(f"Error getting status for resume {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
