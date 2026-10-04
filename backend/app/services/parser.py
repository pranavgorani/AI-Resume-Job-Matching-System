import os
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: Path) -> Tuple[str, str]:
    """
    Extracts text from PDF, DOCX, or TXT.
    Returns (raw_text, detected_type).
    """
    ext = file_path.suffix.lower()
    
    if ext == ".pdf":
        return _extract_from_pdf(file_path), "pdf"
    elif ext in [".docx", ".doc"]:
        return _extract_from_docx(file_path), "docx"
    elif ext in [".txt", ".md", ".json"]:
        return _extract_from_txt(file_path), "txt"
    else:
        # Fallback treat as text
        try:
            return _extract_from_txt(file_path), "txt"
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}")

def _extract_from_pdf(file_path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        extracted = "\n".join(text_parts).strip()
        if not extracted:
            raise ValueError("PDF appears empty or scanned without extractable text layer.")
        return extracted
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

def _extract_from_docx(file_path: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(file_path))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        full_text.append(cell.text)
        extracted = "\n".join(full_text).strip()
        if not extracted:
            raise ValueError("DOCX document appears empty.")
        return extracted
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        raise ValueError(f"Failed to parse DOCX document: {str(e)}")

def _extract_from_txt(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {e}")
        raise ValueError(f"Failed to read text file: {str(e)}")
