import shutil
from pathlib import Path
from config.constants import DATASET_DIR, ENCODINGS_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

class FaceEncoder:
    def __init__(self):
        self.encodings_dir = ENCODINGS_DIR
        self.encodings_dir.mkdir(parents=True, exist_ok=True)
    
    def encode_student(self, student_id):
        student_folder = DATASET_DIR / student_id
        if not student_folder.exists():
            return False, "Folder not found"
        images = list(student_folder.glob("*.jpg")) + list(student_folder.glob("*.jpeg")) + list(student_folder.glob("*.png"))
        if not images:
            return False, "No images found"
        dest_path = self.encodings_dir / f"{student_id}.jpg"
        shutil.copy2(str(images[0]), str(dest_path))
        return True, None