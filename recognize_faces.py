"""
recognition/recognize_faces.py - Face Recognition Module (FIXED)
"""

import cv2
import face_recognition
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from utils.logger import get_logger
from config.constants import FACE_RECOGNITION_THRESHOLD, ENCODINGS_DIR

logger = get_logger(__name__)


class FaceRecognizer:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.threshold = FACE_RECOGNITION_THRESHOLD
        self.load_encodings()
    
    def load_encodings(self):
        """Load face encodings from disk"""
        encodings_file = ENCODINGS_DIR / "face_encodings.pkl"
        names_file = ENCODINGS_DIR / "known_names.pkl"
        
        if encodings_file.exists() and names_file.exists():
            import pickle
            try:
                with open(encodings_file, 'rb') as f:
                    self.known_encodings = pickle.load(f)
                with open(names_file, 'rb') as f:
                    self.known_names = pickle.load(f)
                logger.info(f"Loaded {len(self.known_encodings)} face encodings")
            except Exception as e:
                logger.error(f"Error loading encodings: {e}")
                self.known_encodings = []
                self.known_names = []
    
    def add_face(self, name, image_path):
        """Add a face encoding manually"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return False
            
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            
            if not face_locations:
                return False
            
            encodings = face_recognition.face_encodings(rgb, face_locations)
            if encodings:
                self.known_encodings.append(encodings[0])
                self.known_names.append(name)
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding face {name}: {e}")
            return False
    
    def process_frame(self, frame):
        """Process a single frame"""
        results = {"faces": [], "count": 0}
        
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            
            if not face_locations or not self.known_encodings:
                return results
            
            face_encodings = face_recognition.face_encodings(rgb, face_locations)
            
            for encoding, location in zip(face_encodings, face_locations):
                name = "Unknown"
                confidence = 0
                
                distances = face_recognition.face_distance(self.known_encodings, encoding)
                if len(distances) > 0:
                    min_distance = np.min(distances)
                    if min_distance <= self.threshold:
                        best_idx = np.argmin(distances)
                        name = self.known_names[best_idx]
                        confidence = 1 - min_distance
                
                results["faces"].append({
                    "name": name,
                    "confidence": confidence,
                    "location": location
                })
                results["count"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return results
    
    def draw_results(self, frame, results):
        """Draw results on frame"""
        for face in results["faces"]:
            top, right, bottom, left = face["location"]
            name = face["name"]
            confidence = face["confidence"]
            
            if name == "Unknown":
                color = (0, 0, 255)
                label = "Unknown"
            else:
                color = (0, 255, 0)
                label = f"{name} ({confidence:.2f})"
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame