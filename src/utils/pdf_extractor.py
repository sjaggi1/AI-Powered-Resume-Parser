"""
PDF text extraction utilities
Supports both text-based PDFs and scanned PDFs with OCR
"""

import io
from typing import Union
import PyPDF2
import pdfplumber
from PIL import Image
from loguru import logger

try:
    import pytesseract
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not available. Install pytesseract and pdf2image for OCR support.")


def extract_text_from_pdf(pdf_content: bytes, use_ocr: bool = True) -> str:
    """
    Extract text from PDF using multiple methods
    
    Args:
        pdf_content: PDF file content as bytes
        use_ocr: Whether to use OCR for scanned PDFs
    
    Returns:
        Extracted text
    """
    text = ""
    
    try:
        # Method 1: Try pdfplumber first (best for structured PDFs)
        logger.info("Attempting text extraction with pdfplumber...")
        text = _extract_with_pdfplumber(pdf_content)
        
        if text and len(text.strip()) > 100:
            logger.info(f"Successfully extracted {len(text)} characters with pdfplumber")
            return text
        
        # Method 2: Try PyPDF2 as fallback
        logger.info("Attempting text extraction with PyPDF2...")
        text = _extract_with_pypdf2(pdf_content)
        
        if text and len(text.strip()) > 100:
            logger.info(f"Successfully extracted {len(text)} characters with PyPDF2")
            return text
        
        # Method 3: Use OCR if enabled and text extraction failed
        if use_ocr and OCR_AVAILABLE:
            logger.info("Text extraction failed, attempting OCR...")
            text = _extract_with_ocr(pdf_content)
            
            if text and len(text.strip()) > 100:
                logger.info(f"Successfully extracted {len(text)} characters with OCR")
                return text
        
        # If still no text, raise error
        if not text or len(text.strip()) < 50:
            raise ValueError("Could not extract sufficient text from PDF")
        
        return text
        
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise


def _extract_with_pdfplumber(pdf_content: bytes) -> str:
    """Extract text using pdfplumber"""
    try:
        pdf_file = io.BytesIO(pdf_content)
        text_parts = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
        
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
        return ""


def _extract_with_pypdf2(pdf_content: bytes) -> str:
    """Extract text using PyPDF2"""
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_parts = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
        
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed: {e}")
        return ""


def _extract_with_ocr(pdf_content: bytes) -> str:
    """Extract text using OCR (for scanned PDFs)"""
    if not OCR_AVAILABLE:
        logger.error("OCR libraries not available")
        return ""
    
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_content)
        text_parts = []
        
        # Perform OCR on each page
        for i, image in enumerate(images):
            logger.info(f"Performing OCR on page {i+1}/{len(images)}...")
            page_text = pytesseract.image_to_string(image, lang='eng')
            
            if page_text:
                text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return ""


def extract_text_from_image(image_content: bytes) -> str:
    """
    Extract text from image using OCR
    
    Args:
        image_content: Image file content as bytes
    
    Returns:
        Extracted text
    """
    if not OCR_AVAILABLE:
        raise ValueError("OCR libraries not available. Install pytesseract and pdf2image.")
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_content))
        
        # Perform OCR
        logger.info("Performing OCR on image...")
        text = pytesseract.image_to_string(image, lang='eng')
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Could not extract sufficient text from image")
        
        logger.info(f"Successfully extracted {len(text)} characters from image")
        return text
        
    except Exception as e:
        logger.error(f"Image text extraction failed: {e}")
        raise