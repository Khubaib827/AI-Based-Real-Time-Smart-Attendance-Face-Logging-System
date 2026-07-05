import cv2
import time
from pathlib import Path
from config.constants import DATASET_DIR, NUMBER_OF_FACE_IMAGES_TO_CAPTURE
from utils.camera import CameraManager
from utils.logger import get_logger

logger = get_logger(__name__)

class FaceCapture:
    def __init__(self, student_id, student_name):
        self.student_id = student_id
        self.student_name = student_name
        self.student_folder = DATASET_DIR / student_id
        self.camera = CameraManager()
        self.captured_count = 0
        self.total_needed = NUMBER_OF_FACE_IMAGES_TO_CAPTURE
    
    def capture_images(self):
        self.student_folder.mkdir(parents=True, exist_ok=True)
        if not self.camera.open():
            return 0, False
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            while self.captured_count < self.total_needed:
                success, frame = self.camera.get_frame()
                if not success:
                    continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = frame[y:y+h, x:x+w]
                    if face_roi.size > 0:
                        face_resized = cv2.resize(face_roi, (320, 320))
                        img_name = f"{self.student_id}_{self.captured_count+1:03d}.jpg"
                        cv2.imwrite(str(self.student_folder / img_name), face_resized)
                        self.captured_count += 1
                        logger.info(f"Captured {self.captured_count}/{self.total_needed}")
                cv2.imshow("Face Capture - Press 'q' to quit", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.05)
            cv2.destroyAllWindows()
            self.camera.close()
            return self.captured_count, self.captured_count >= self.total_needed * 0.5
        except Exception as e:
            logger.exception(f"Error: {e}")
            cv2.destroyAllWindows()
            self.camera.close()
            return self.captured_count, False