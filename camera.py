import cv2
import time
from utils.logger import get_logger

logger = get_logger(__name__)

class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
    
    def open(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Camera error: {e}")
            return False
    
    def get_frame(self):
        if not self.cap or not self.cap.isOpened():
            if not self.open():
                return False, None
        ret, frame = self.cap.read()
        return ret, frame
    
    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None