# AI Document Verification System

A runnable FastAPI + OCR prototype for AI-assisted document verification.

## Features

- PDF/image upload
- Native PDF text extraction
- OCR for scanned/image documents
- Basic document classification
- Extraction of email, phone, date and ID-like values
- Heuristic risk indicators
- Verification dashboard
- JSON report storage

## 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install Python dependencies

```powershell
pip install -r backend\requirements.txt
```

## 3. Install Tesseract OCR

This project uses Tesseract for image OCR. On Windows, install Tesseract OCR separately and make sure `tesseract.exe` is in PATH.

If it is not in PATH, edit `backend/document_engine.py` and add before OCR:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 4. Start the app

From the project root:

```powershell
uvicorn backend.main:app --reload
```

Open:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs

## Important

This is an educational prototype. Its risk score and confidence are heuristic indicators and must not be treated as proof of legal/official authenticity. A production verification system should validate against trusted issuer records, cryptographic signatures, or authorized databases.

## Suggested next upgrades

1. Add MySQL/PostgreSQL
2. Add user authentication
3. Add issuer database verification
4. Add document-specific field schemas
5. Add computer-vision tamper detection
6. Add ML anomaly classifier
7. Add admin dashboard
8. Add audit logs
9. Add signed verification reports
10. Deploy frontend/backend securely


## Mobile App Installation (PWA)

This project is now a Progressive Web App.

### Android / Chrome
1. Run/deploy the backend on a server accessible from your phone.
2. Open the site in Chrome.
3. Use **Install App** or Chrome menu → **Add to Home screen**.
4. The app opens in a standalone mobile window.

### Important
`127.0.0.1`/`localhost` only works on the computer running the server. For phone access, deploy the backend or run it on a computer and expose it safely over the same network/tunnel.

For a real Play Store APK/AAB later, the PWA can be wrapped with a tool such as Trusted Web Activity/Capacitor after deployment.

## Deploy on Render

1. Push this folder to a GitHub repository.
2. In Render, create a **New Web Service** and select the repository.
3. Render can use the included `render.yaml`, or enter:
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Deploy.
5. Open the generated HTTPS URL on your phone.

### Tesseract note

The current OCR implementation uses the Windows Tesseract executable and therefore needs a Linux-compatible Tesseract installation on the hosting server. The Render deployment should be updated to install the `tesseract-ocr` system package before relying on OCR for scanned images.

For a production deployment, use a Docker image that installs Tesseract and the Python dependencies, and use persistent/object storage rather than local `uploads/` and `reports/`.
