
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

    def __init__(self, confidence: float = 0.40):
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
            conf=0.15,
            iou=0.45,
            max_det=100,
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
                label = CLASS_MAPPING[original_class]

                if label == "vest":
                    if confidence < 0.15:
                        continue
                elif confidence < self.confidence:
                    continue

                x1, y1, x2, y2 = (
                    float(value) for value in box.xyxy[0].tolist()
                )

                detections.append({
                    "class_id": class_id,
                    "class_name": original_class,
                    "label": label,
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


        annotated_image = cv2.imread(str(image_path))

        class_colors = {
            "person": (255, 0, 255),       # Purple
            "helmet": (255, 140, 0),       # Blue
            "no-helmet": (0, 0, 255),      # Red
            "vest": (0, 200, 0),           # Green
            "no-vest": (0, 0, 255),        # Red
        }

        display_labels = {
            "person": "PERSON",
            "helmet": "HELMET",
            "no-helmet": "NO HELMET",
            "vest": "VEST",
            "no-vest": "NO VEST",
        }

        for detection in detections:
            bbox = detection["bbox"]
            label = detection["label"]
            confidence = detection["confidence"]

            x1 = int(bbox["x1"])
            y1 = int(bbox["y1"])
            x2 = int(bbox["x2"])
            y2 = int(bbox["y2"])

            color = class_colors[label]

            cv2.rectangle(
                annotated_image,
                (x1, y1),
                (x2, y2),
                color,
                2,
            )

            text = (
                f"{display_labels[label]} "
                f"{confidence:.2f}"
            )

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            thickness = 1

            (text_width, text_height), baseline = cv2.getTextSize(
                text,
                font,
                font_scale,
                thickness,
            )

            label_y = max(y1, text_height + 10)

            cv2.rectangle(
                annotated_image,
                (x1, label_y - text_height - 8),
                (x1 + text_width + 8, label_y + baseline - 4),
                color,
                -1,
            )

            cv2.putText(
                annotated_image,
                text,
                (x1 + 4, label_y - 4),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA,
            )

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
