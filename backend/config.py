import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in (UPLOADS_DIR, RESULTS_DIR, REPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Configuration values
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'visionguard.db'}")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

FACT_CHECK_API_KEY = os.getenv("FACT_CHECK_API_KEY", "")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "visionguard-forensic-baseline-v1")
