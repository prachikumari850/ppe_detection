
from pathlib import Path

import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "ppe_model.pt"
PROCESSED_DIR = PROJECT_ROOT / "storage" / "processed"

RELEVANT_CLASSES = {
    "Hardhat",
    "NO-Hardhat",
    "Safety Vest",
    "NO-Safety Vest",
    "Person",
}

CLASS_MAPPING = {
    "Hardhat": "helmet",
    "NO-Hardhat": "no-helmet",
    "Safety Vest": "vest",
    "NO-Safety Vest": "no-vest",
    "Person": "person",
}


class PPEDetector:

    def __init__(self, confidence: float = 0.25):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"PPE model not found: {MODEL_PATH}"
            )

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        self.model = YOLO(str(MODEL_PATH))
        self.confidence = confidence

        self.relevant_class_ids = [
            class_id
            for class_id, class_name in self.model.names.items()
            if class_name in RELEVANT_CLASSES
        ]

    def detect(self, image_path: str) -> dict:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=self.confidence,
            classes=self.relevant_class_ids,
            device="cpu",
            verbose=False,
        )

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())

                original_class = self.model.names[class_id]

                x1, y1, x2, y2 = (
                    float(value) for value in box.xyxy[0].tolist()
                )

                detections.append({
                    "class_id": class_id,
                    "class_name": original_class,
                    "label": CLASS_MAPPING[original_class],
                    "confidence": round(confidence, 4),
                    "bbox": {
                        "x1": round(x1, 2),
                        "y1": round(y1, 2),
                        "x2": round(x2, 2),
                        "y2": round(y2, 2),
                    },
                })

        annotated_filename = f"{image_path.stem}_annotated.jpg"
        annotated_path = PROCESSED_DIR / annotated_filename

        for result in results:
            annotated_image = result.plot()
            cv2.imwrite(str(annotated_path), annotated_image)

        return {
            "image_name": image_path.name,
            "total_detections": len(detections),
            "annotated_image": str(
                annotated_path.relative_to(PROJECT_ROOT)
            ),
            "detections": detections,
        }


detector = PPEDetector()
