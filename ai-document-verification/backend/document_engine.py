from pathlib import Path
import re
import cv2
import numpy as np

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def _ocr_image(img):
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(thresh)


def extract_text(path: Path):
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        if fitz is None:
            raise RuntimeError("PyMuPDF is not installed")
        doc = fitz.open(path)
        chunks = []
        for page in doc:
            native = page.get_text("text").strip()
            if native:
                chunks.append(native)
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:
                    arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
                else:
                    arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                chunks.append(_ocr_image(arr))
        return "\n".join(chunks)

    img = cv2.imread(str(path))
    if img is None:
        raise RuntimeError("Could not read image")
    return _ocr_image(img)


def classify_document(text):
    t = text.lower()
    scores = {
        "certificate": sum(x in t for x in ["certificate", "certified", "award"]),
        "marksheet": sum(x in t for x in ["mark", "marksheet", "semester", "grade", "subject"]),
        "invoice": sum(x in t for x in ["invoice", "subtotal", "tax", "total amount", "gst"]),
        "identity document": sum(x in t for x in ["date of birth", "dob", "identity", "address", "gender"]),
    }
    label, score = max(scores.items(), key=lambda x: x[1])
    if score == 0:
        return "unknown"
    return label


def extract_fields(text):
    compact = re.sub(r"\s+", " ", text).strip()
    patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "phone": r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b",
        "date": r"\b(?:0?[1-9]|[12]\d|3[01])[-/](?:0?[1-9]|1[0-2])[-/](?:19|20)\d{2}\b",
        "id_like": r"\b[A-Z]{2,8}[-/]?\d{3,12}\b",
    }
    out = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, compact, flags=re.I)
        out[key] = list(dict.fromkeys(matches))[:10]
    return out


def risk_analysis(text, fields, doc_type):
    checks = []
    low = text.lower()

    if len(text.strip()) < 40:
        checks.append({"severity": "high", "message": "Very little readable text was extracted."})
    else:
        checks.append({"severity": "info", "message": "Readable text was extracted successfully."})

    if doc_type == "unknown":
        checks.append({"severity": "medium", "message": "Document type could not be confidently classified."})

    suspicious_terms = ["edited", "sample", "draft", "copy", "specimen"]
    found = [x for x in suspicious_terms if x in low]
    if found:
        checks.append({"severity": "medium", "message": f"Review these text indicators: {', '.join(found)}."})
    else:
        checks.append({"severity": "info", "message": "No common review-indicator words were found."})

    risk = "low"
    if any(c["severity"] == "high" for c in checks):
        risk = "high"
    elif any(c["severity"] == "medium" for c in checks):
        risk = "medium"

    # This is a heuristic risk indicator, not proof of authenticity.
    confidence = 95 if risk == "low" else 78 if risk == "medium" else 55
    return risk, confidence, checks


def analyze_document(path: Path):
    text = extract_text(path)
    doc_type = classify_document(text)
    fields = extract_fields(text)
    risk, confidence, checks = risk_analysis(text, fields, doc_type)

    return {
        "status": "analysis_complete",
        "document_type": doc_type,
        "risk_level": risk,
        "confidence": confidence,
        "checks": checks,
        "extracted_fields": fields,
        "text_preview": text[:4000],
        "note": "This prototype provides automated document risk indicators. It does not establish legal or official authenticity."
    }
