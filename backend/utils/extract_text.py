# backend/utils/extract_text.py
from pathlib import Path
import logging

logger = logging.getLogger("extract_text")

def extract_pdf_text(path: str) -> str:
    """
    Extract text from PDF using PyPDF2 (recommended).
    If PyPDF2 not available, raises ImportError with instructions.
    """
    try:
        import PyPDF2
    except ImportError as e:
        raise ImportError("PyPDF2 is required for PDF extraction. Install: pip install PyPDF2") from e

    text_parts = []
    with open(path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_ocr_text(path: str) -> str:
    """
    Extract text from image using pytesseract + Pillow.
    Must have tesseract installed on system and pytesseract & PIL on python.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise ImportError("Pillow is required for image OCR. Install: pip install pillow") from e

    try:
        import pytesseract
    except ImportError as e:
        raise ImportError("pytesseract is required for OCR. Install: pip install pytesseract") from e

    # If pytesseract can't find tesseract binary, it will raise; that's OK.
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return text.strip()
