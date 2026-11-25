from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.ai.detector import detector
from backend.services.compliance_service import compliance_service


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "PPE Detection API is running"
    }


@router.post("/detect")
async def detect_ppe(file: UploadFile = File(...)):

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed"
        )

    file_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        detection_result = detector.detect(str(file_path))

        report = compliance_service.analyze(detection_result)

        return {
            "success": True,
            "message": "PPE detection completed",
            "data": report
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PPE detection failed: {str(exc)}"
        )

    finally:
        await file.close()
