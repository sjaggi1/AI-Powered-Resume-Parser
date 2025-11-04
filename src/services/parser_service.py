"""
Resume Parser Service
Coordinates document extraction, AI parsing, and data enhancement
"""

import os
import hashlib
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
from loguru import logger

from src.services.ai_service import ai_service
from src.utils.pdf_extractor import extract_text_from_pdf
from src.utils.docx_extractor import extract_text_from_docx
from src.utils.validators import validate_email, validate_phone
from src.config import settings

    
class ParserService:
    """Main resume parsing service"""
    
    def __init__(self):
        """Initialize parser service"""
        self.ai_service = ai_service
        
    async def parse_resume(
        self,
        file_content: bytes,
        filename: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse resume from file content
        
        Args:
            file_content: Binary file content
            filename: Original filename
            options: Parsing options
        
        Returns:
            Complete parsed resume data
        """
        options = options or {}
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting resume parsing: {filename}")
            
            # Step 1: Extract text from document
            logger.info("Step 1: Extracting text from document...")
            raw_text = await self._extract_text(file_content, filename, options)
            
            if not raw_text or len(raw_text.strip()) < 50:
                raise ValueError("Could not extract sufficient text from document")
            
            logger.info(f"Extracted {len(raw_text)} characters of text")
            
            # Step 2: Parse with AI
            logger.info("Step 2: Parsing with AI (GPT-4)...")
            structured_data = self.ai_service.parse_resume(raw_text, options)
            
            # Step 3: Enhance with AI if enabled
            ai_enhancements = {}
            if options.get('enhanceWithAI', True):
                logger.info("Step 3: Enhancing with AI insights...")
                ai_enhancements = self.ai_service.enhance_with_ai(structured_data)
            
            # Step 4: Calculate metadata
            logger.info("Step 4: Calculating metadata...")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            metadata = {
                "fileName": filename,
                "fileSize": len(file_content),
                "fileType": self._get_file_type(filename),
                "fileHash": hashlib.sha256(file_content).hexdigest(),
                "uploadedAt": start_time.isoformat(),
                "processedAt": datetime.now().isoformat(),
                "processingTime": round(processing_time, 2),
                "rawTextLength": len(raw_text),
                "parsingMethod": "AI-GPT4"
            }
            
            # Step 5: Combine all data
            complete_data = {
                "metadata": metadata,
                "rawText": raw_text[:5000],  # Store first 5000 chars for reference
                **structured_data,
                "aiEnhancements": ai_enhancements
            }
            
            # Step 6: Post-process and validate
            complete_data = self._post_process(complete_data)
            
            logger.info(f"Resume parsing completed in {processing_time:.2f}s")
            
            return complete_data
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            raise
    
    async def _extract_text(
        self,
        file_content: bytes,
        filename: str,
        options: Dict[str, Any]
    ) -> str:
        """
        Extract text from various file formats
        
        Args:
            file_content: Binary file content
            filename: Original filename
            options: Extraction options
        
        Returns:
            Extracted text
        """
        file_ext = filename.lower().split('.')[-1]
        
        try:
            if file_ext == 'pdf':
                text = extract_text_from_pdf(file_content, options.get('performOCR', True))
            
            elif file_ext in ['docx', 'doc']:
                text = extract_text_from_docx(file_content)
            
            elif file_ext == 'txt':
                text = file_content.decode('utf-8', errors='ignore')
            
            elif file_ext in ['jpg', 'jpeg', 'png']:
                # For images, always use OCR
                if options.get('performOCR', True):
                    from src.utils.pdf_extractor import extract_text_from_image
                    text = extract_text_from_image(file_content)
                else:
                    raise ValueError("OCR is required for image files but was disabled")
            
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return text
            
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            raise ValueError(f"Failed to extract text from {file_ext.upper()} file: {str(e)}")
    
    def _post_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process and validate parsed data

        Args:
            data: Parsed resume data

        Returns:
            Validated and cleaned data
        """
        # Validate email if present
        if data.get('personalInfo', {}).get('contact', {}).get('email'):
            email = data['personalInfo']['contact']['email']
            if not validate_email(email):
                logger.warning(f"Invalid email detected: {email}")
                data['personalInfo']['contact']['emailValid'] = False
            else:
                data['personalInfo']['contact']['emailValid'] = True

        # Validate phone if present
        if data.get('personalInfo', {}).get('contact', {}).get('phone'):
            phone = data['personalInfo']['contact']['phone']
            if not validate_phone(phone):
                logger.warning(f"Invalid phone detected: {phone}")
                data['personalInfo']['contact']['phoneValid'] = False
            else:
                data['personalInfo']['contact']['phoneValid'] = True

        # Calculate total experience
        total_experience = self._calculate_total_experience(data.get('experience', []))

        # ✅ Ensure summary is a dict before adding structured info
        if isinstance(data.get('summary'), str):
            data['summary'] = {"text": data['summary']}
        elif not isinstance(data.get('summary'), dict):
            data['summary'] = {}

        # Add computed total experience
        data['summary']['totalYearsOfExperience'] = total_experience

        # Add confidence scores
        data['confidenceScores'] = {
            "overall": 0.85,
            "contactInfo": 0.90 if data.get('personalInfo', {}).get('contact') else 0.5,
            "experience": 0.85 if data.get('experience') else 0.3,
            "education": 0.80 if data.get('education') else 0.4,
            "skills": 0.75 if data.get('skills') else 0.2
        }
        
        # After all processing (before return)
        flat_output = {
            "name": data.get("personalInfo", {}).get("name", "Not found"),
            "contact_info": {
                "email": data.get("personalInfo", {}).get("contact", {}).get("email", "Not found"),
                "phone": data.get("personalInfo", {}).get("contact", {}).get("phone", "Not found"),
                "linkedin": data.get("personalInfo", {}).get("contact", {}).get("linkedin", "Not found"),
                "location": data.get("personalInfo", {}).get("contact", {}).get("location", "Not found"),
                "portfolio": data.get("personalInfo", {}).get("contact", {}).get("portfolio", "Not found"),
            },
            "summary": data.get("summary", {}).get("text", "")
                if isinstance(data.get("summary"), dict)
                else data.get("summary", ""),
        }

        data.update(flat_output)
        return data

    
    def _calculate_total_experience(self, experiences: list) -> float:
        """Calculate total years of experience from work history"""
        if not experiences:
            return 0.0
        
        total_months = 0
        
        for exp in experiences:
            start_date = exp.get('startDate')
            end_date = exp.get('endDate') or datetime.now().strftime('%Y-%m')
            
            if start_date:
                try:
                    # Parse dates (assuming YYYY-MM format)
                    start_parts = start_date.split('-')
                    end_parts = end_date.split('-') if isinstance(end_date, str) else [
                        datetime.now().year, datetime.now().month
                    ]
                    
                    start_year = int(start_parts[0])
                    start_month = int(start_parts[1]) if len(start_parts) > 1 else 1
                    
                    end_year = int(end_parts[0])
                    end_month = int(end_parts[1]) if len(end_parts) > 1 else 12
                    
                    # Calculate months
                    months = (end_year - start_year) * 12 + (end_month - start_month)
                    total_months += max(0, months)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse dates: {start_date} to {end_date}")
                    continue
        
        return round(total_months / 12, 1)
    
    def _get_file_type(self, filename: str) -> str:
        """Get file MIME type from filename"""
        ext = filename.lower().split('.')[-1]
        
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        
        return mime_types.get(ext, 'application/octet-stream')
    
    async def get_parsing_status(self, resume_id: str) -> Dict[str, Any]:
        """
        Get parsing status for a resume
        (In production, this would query from database/cache)
        """
        # This is a placeholder - in real implementation, query from database
        return {
            "id": resume_id,
            "status": "completed",
            "progress": 100,
            "currentStep": "completed"
        }


# Global parser service instance
parser_service = ParserService()