from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid, json, re, shutil, os

from document_engine import analyze_document

BASE = Path(__file__).resolve().parent.parent
UPLOADS = BASE / "uploads"
REPORTS = BASE / "reports"
FRONTEND = BASE / "frontend"

app = FastAPI(title="AI Document Verification System", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")

@app.get("/")
def home():
    return FileResponse(str(FRONTEND / "index.html"))

@app.get("/health")
def health():
    return {"status": "healthy", "service": "AI Document Verification System"}

@app.post("/api/verify")
async def verify_document(file: UploadFile = File(...)):
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, "Supported files: PDF, PNG, JPG, JPEG, WEBP")

    doc_id = uuid.uuid4().hex
    saved = UPLOADS / f"{doc_id}{ext}"

    with saved.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        result = analyze_document(saved)
        result["document_id"] = doc_id
        result["filename"] = file.filename
        report_path = REPORTS / f"{doc_id}.json"
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result
    except Exception as e:
        if saved.exists():
            saved.unlink()
        raise HTTPException(500, f"Document analysis failed: {e}")

@app.get("/api/report/{document_id}")
def get_report(document_id: str):
    path = REPORTS / f"{document_id}.json"
    if not path.exists():
        raise HTTPException(404, "Report not found")
    return json.loads(path.read_text(encoding="utf-8"))
