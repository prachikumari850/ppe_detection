from pathlib import Path
import shutil
import uuid
from sqlalchemy import desc
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.ai.detector import detector
from backend.services.compliance_service import compliance_service
from backend.database.database import get_db
from backend.database.models import DetectionRecord


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
async def detect_ppe(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

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

        summary = report["summary"]

        record = DetectionRecord(
            image_name=report["image_name"],
            annotated_image=report["annotated_image"],
            status=report["status"],
            total_persons_detected=summary["total_persons_detected"],
            helmets_detected=summary["helmets_detected"],
            missing_helmets_detected=summary["missing_helmets_detected"],
            vests_detected=summary["vests_detected"],
            missing_vests_detected=summary["missing_vests_detected"],
            total_violations_detected=summary["total_violations_detected"],
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "success": True,
            "message": "PPE detection completed",
            "record_id": record.id,
            "data": report
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"PPE detection failed: {str(exc)}"
        )

    finally:
        await file.close()


@router.get("/history")
def get_detection_history(
    db: Session = Depends(get_db)
):
    try:
        records = (
            db.query(DetectionRecord)
            .order_by(desc(DetectionRecord.created_at))
            .all()
        )

        history = []

        for record in records:
            history.append({
                "id": record.id,
                "image_name": record.image_name,
                "annotated_image": record.annotated_image.replace("\\", "/"),
                "status": record.status,
                "summary": {
                    "total_persons_detected": record.total_persons_detected,
                    "helmets_detected": record.helmets_detected,
                    "missing_helmets_detected": record.missing_helmets_detected,
                    "vests_detected": record.vests_detected,
                    "missing_vests_detected": record.missing_vests_detected,
                    "total_violations_detected": record.total_violations_detected,
                },
                "created_at": record.created_at.isoformat(),
            })

        return {
            "success": True,
            "total_records": len(history),
            "data": history,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve detection history: {str(exc)}"
        )
