import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATASET_DIR = ASSETS_DIR / "dataset"
ENCODINGS_DIR = ASSETS_DIR / "encodings"
EXPORTS_DIR = ASSETS_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "attendance.db"

for directory in [ASSETS_DIR, DATASET_DIR, ENCODINGS_DIR, EXPORTS_DIR, LOGS_DIR, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

FACE_RECOGNITION_THRESHOLD = 0.6
NUMBER_OF_FACE_IMAGES_TO_CAPTURE = 30
DEFAULT_CAMERA_INDEX = 0
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"