from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

app = FastAPI()

# Mount static files for uploaded file previews
UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)  # Create directory using pathlib
app.mount("/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting backend...")
    yield
    print("Shutting down backend...")

app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    return {
        "message": "Document Summary Assistant - AI Backend",
        "endpoints": ["/upload (POST)", "/files/{filename} (GET)"],
        "success": True
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), length: str = Form("medium")):
    """
    Upload document and generate AI-powered summary.
    """
    upload_path = None
    try:
        # Validate file
        if not file or file.size == 0:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        if file.size > 15 * 1024 * 1024:  # 15MB limit
            raise HTTPException(status_code=413, detail="File too large (max 15MB)")
        
        allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(status_code=400, detail="Only PDF and image files allowed")
        
        # Create unique filename and save using pathlib for cross-platform safety
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        saved_filename = f"{timestamp}_{file.filename}"
        upload_path = UPLOAD_DIR / saved_filename  # Use pathlib for path joining
        
        # Ensure the path is absolute
        upload_path = upload_path.resolve()
        
        # Write file content
        content = await file.read()
        with open(upload_path, "wb") as buffer:
            buffer.write(content)
        
        print(f"File saved: {upload_path}")
        print(f"File exists: {upload_path.exists()}")
        
        # Extract text from uploaded file
        text = ""
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(upload_path)
        else:
            text = extract_text_from_image(upload_path)
        
        if not text or not text.strip():
            # Generate a fallback summary if no text extracted
            summary = "No readable text found. Please ensure your PDF contains selectable text or upload a text-rich document."
            improvements = "Consider using searchable PDFs or documents with clear text content."
        else:
            # Generate summary using your updated summarize.py (fast!)
            from utils.summarize import generate_summary, generate_improvements
            summary = generate_summary(text, length)
            improvements = generate_improvements(text)
        
        return {
            "success": True,
            "filename": file.filename,
            "saved_filename": saved_filename,
            "file_url": f"/files/{saved_filename}",
            "summary": summary,
            "improvements": improvements,
            "text_extracted": len(text),
            "processing_status": "complete"
        }
    
    except Exception as e:
        print(f"Error processing file: {e}")
        print(f"Upload path was: {upload_path}")
        return {
            "success": False,
            "detail": f"File processing failed: {str(e)}"
        }

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    # Convert Path object to string if needed
    pdf_path = str(pdf_path) if isinstance(pdf_path, Path) else pdf_path
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using Tesseract OCR."""
    # Convert Path object to string if needed
    image_path = str(image_path) if isinstance(image_path, Path) else image_path
    
    try:
        import pytesseract
        from PIL import Image
        # Try to find tesseract in common locations
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'/usr/bin/tesseract',  # Linux
            r'/opt/homebrew/bin/tesseract',  # macOS with homebrew
            'tesseract'  # In PATH
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        
        image = Image.open(image_path)
        if image.mode != 'L':
            image = image.convert('L')
        text = pytesseract.image_to_string(image, lang='eng')
        return text.strip()
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return ""

@app.get("/files/{filename:path}")
async def get_uploaded_file(filename: str):
    """Serve uploaded file for preview."""
    file_path = UPLOAD_DIR / filename
    file_path = file_path.resolve()
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        media_type='application/pdf' if filename.endswith('.pdf') else 'image/png',
        filename=filename  
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_model": "ready", "file_serving": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)