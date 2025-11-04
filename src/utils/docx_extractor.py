# src/utils/docx_extractor.py

import io
from docx import Document

def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extracts text content from a DOCX file given its bytes.
    """
    try:
        # Use BytesIO to handle in-memory file uploads
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Error extracting text from DOCX: {e}")
