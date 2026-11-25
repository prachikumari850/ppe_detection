class PPEComplianceService:

    VIOLATION_CLASSES = {
        "no-helmet": "Missing Helmet",
        "no-vest": "Missing Safety Vest",
    }

    def analyze(self, detection_result: dict) -> dict:
        detections = detection_result.get("detections", [])

        counts = {
            "person": 0,
            "helmet": 0,
            "no-helmet": 0,
            "vest": 0,
            "no-vest": 0,
        }

        violations = []

        for detection in detections:
            label = detection.get("label")

            if label not in counts:
                continue

            counts[label] += 1

            if label in self.VIOLATION_CLASSES:
                violations.append({
                    "type": label,
                    "description": self.VIOLATION_CLASSES[label],
                    "confidence": detection["confidence"],
                    "bbox": detection["bbox"],
                })

        violation_count = len(violations)

        if violation_count > 0:
            status = "VIOLATION DETECTED"
        elif counts["person"] > 0:
            status = "NO VIOLATION DETECTED"
        else:
            status = "NO PERSON DETECTED"

        return {
            "image_name": detection_result.get("image_name"),
            "annotated_image": detection_result.get("annotated_image"),
            "status": status,
            "summary": {
                "total_persons_detected": counts["person"],
                "helmets_detected": counts["helmet"],
                "missing_helmets_detected": counts["no-helmet"],
                "vests_detected": counts["vest"],
                "missing_vests_detected": counts["no-vest"],
                "total_violations_detected": violation_count,
            },
            "violations": violations,
            "detections": detections,
        }

compliance_service = PPEComplianceService()
