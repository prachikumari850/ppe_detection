
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "storage" / "processed"

app = FastAPI(
    title="PPE Violation Detection API",
    description="AI-powered Personal Protective Equipment detection system",
    version="1.0.0"
)

app.mount(
    "/processed",
    StaticFiles(directory=PROCESSED_DIR),
    name="processed"
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "PPE Violation Detection API",
        "status": "running"
    }
