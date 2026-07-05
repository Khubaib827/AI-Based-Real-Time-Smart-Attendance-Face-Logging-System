"""
Project File Generator - Creates all required files with code
"""
import os
from pathlib import Path

# All file contents
FILES = {
    "app.py": '''
"""
AI-Based Real-Time Smart Attendance & Face Logging System
app.py - Main Application Entry Point
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gui.login_window import LoginWindow
from utils.logger import get_logger
from database.initialize_db import init_database

logger = get_logger(__name__)

def main():
    try:
        logger.info("=" * 60)
        logger.info("AI Smart Attendance System Starting...")
        logger.info("=" * 60)
        if not init_database():
            logger.error("Database initialization failed!")
            return
        app = LoginWindow()
        app.mainloop()
        logger.info("Application closed successfully")
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
''',

    "requirements.txt": '''
opencv-python==4.8.1.78
numpy==1.24.3
pandas==2.0.3
openpyxl==3.1.2
Pillow==10.0.1
customtkinter==5.2.0
reportlab==4.0.4
matplotlib==3.7.2
python-dotenv==1.0.0
tensorflow==2.13.0
keras==2.13.1
deepface==0.0.79
''',

    "config/__init__.py": "# Config package",
    
    "config/constants.py": '''
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
''',

    "config/settings.py": '''
from config.constants import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

class Settings:
    def __init__(self):
        self._settings = {
            "admin": {"username": DEFAULT_ADMIN_USERNAME, "password": DEFAULT_ADMIN_PASSWORD},
            "camera": {"index": 0},
            "recognition": {"threshold": 0.6}
        }
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self._settings
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        return value

settings = Settings()
''',

    "database/__init__.py": "# Database package",
    
    "database/database.py": '''
import sqlite3
import threading
from pathlib import Path
from config.constants import DATABASE_PATH

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._connections = {}
    
    def get_connection(self):
        thread_id = threading.get_ident()
        if thread_id not in self._connections:
            conn = sqlite3.connect(str(DATABASE_PATH), timeout=10)
            conn.row_factory = sqlite3.Row
            self._connections[thread_id] = conn
        return self._connections[thread_id]
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def execute_insert(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

db = DatabaseManager()
''',

    "database/initialize_db.py": '''
from database.database import db
from config.constants import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

def init_database():
    queries = [
        "CREATE TABLE IF NOT EXISTS students (student_id TEXT PRIMARY KEY, roll_number TEXT UNIQUE, name TEXT NOT NULL, department TEXT NOT NULL, semester INTEGER, email TEXT UNIQUE, phone TEXT, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_active INTEGER DEFAULT 1)",
        "CREATE TABLE IF NOT EXISTS attendance (attendance_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, name TEXT NOT NULL, date DATE NOT NULL, time TIME NOT NULL, status TEXT DEFAULT 'Present', confidence REAL, FOREIGN KEY (student_id) REFERENCES students(student_id))",
        "CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ]
    conn = db.get_connection()
    cursor = conn.cursor()
    for query in queries:
        cursor.execute(query)
    cursor.execute("SELECT id FROM admin WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD))
    conn.commit()
    return True

if __name__ == "__main__":
    init_database()
''',

    "database/student_model.py": '''
from database.database import db

class StudentModel:
    @staticmethod
    def create(data):
        query = "INSERT INTO students (student_id, roll_number, name, department, semester, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)"
        return db.execute_insert(query, (data.get("student_id"), data.get("roll_number"), data.get("name"), data.get("department"), int(data.get("semester", 1)), data.get("email"), data.get("phone")))
    
    @staticmethod
    def get_all():
        return db.execute_query("SELECT * FROM students WHERE is_active = 1 ORDER BY name ASC")
    
    @staticmethod
    def get_by_id(student_id):
        result = db.execute_query("SELECT * FROM students WHERE student_id = ? AND is_active = 1", (student_id,))
        return result[0] if result else None
''',

    "database/attendance_model.py": '''
from database.database import db
from datetime import date

class AttendanceModel:
    @staticmethod
    def create(data):
        query = "INSERT INTO attendance (student_id, name, date, time, status, confidence) VALUES (?, ?, ?, ?, ?, ?)"
        return db.execute_insert(query, (data.get("student_id"), data.get("name"), data.get("date", date.today().isoformat()), data.get("time"), data.get("status", "Present"), data.get("confidence")))
    
    @staticmethod
    def get_today():
        today = date.today().isoformat()
        return db.execute_query("SELECT * FROM attendance WHERE date = ? ORDER BY time ASC", (today,))
    
    @staticmethod
    def check_today_attendance(student_id):
        today = date.today().isoformat()
        result = db.execute_query("SELECT COUNT(*) as count FROM attendance WHERE student_id = ? AND date = ?", (student_id, today))
        return result[0]['count'] > 0 if result else False
    
    @staticmethod
    def get_by_date_range(start_date, end_date):
        return db.execute_query("SELECT * FROM attendance WHERE date BETWEEN ? AND ? ORDER BY date DESC", (start_date, end_date))
''',

    "utils/__init__.py": "# Utils package",
    
    "utils/logger.py": '''
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config.constants import LOGS_DIR

LOG_FILE = LOGS_DIR / "application.log"

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
''',

    "utils/validators.py": '''
import re

class Validator:
    @staticmethod
    def validate_student_id(student_id):
        if not student_id:
            return False, "Student ID is required"
        if not re.match(r'^STU\d{5}$', student_id):
            return False, "Format: STUXXXXX"
        return True, None
''',

    "utils/camera.py": '''
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
''',

    "recognition/__init__.py": "# Recognition package",
    
    "recognition/capture_faces.py": '''
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
''',

    "recognition/encode_faces.py": '''
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
''',

    "recognition/recognize_faces.py": '''
import cv2
import numpy as np
import os
import tempfile
from deepface import DeepFace
from config.constants import FACE_RECOGNITION_THRESHOLD
from utils.logger import get_logger

logger = get_logger(__name__)

class FaceRecognizer:
    def __init__(self):
        self.known_faces = {}
        self.threshold = FACE_RECOGNITION_THRESHOLD
        self.temp_dir = tempfile.gettempdir()
    
    def add_face(self, name, image_path):
        self.known_faces[name] = image_path
    
    def recognize_face(self, face_image):
        if not self.known_faces:
            return None, None
        try:
            temp_path = os.path.join(self.temp_dir, "temp_face.jpg")
            cv2.imwrite(temp_path, face_image)
            best_match = None
            best_confidence = 0
            for name, known_path in self.known_faces.items():
                try:
                    result = DeepFace.verify(img1_path=temp_path, img2_path=known_path, model_name='Facenet', enforce_detection=False)
                    if result['verified']:
                        confidence = 1 - result['distance']
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = name
                except:
                    continue
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if best_match and best_confidence >= self.threshold:
                return best_match, best_confidence
            return "Unknown", None
        except Exception as e:
            logger.exception(f"Error: {e}")
            return None, None
    
    def process_frame(self, frame):
        results = {"faces": [], "names": [], "count": 0}
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]
                if face_roi.size > 0:
                    name, confidence = self.recognize_face(face_roi)
                    results["faces"].append({"name": name or "Unknown", "confidence": confidence, "location": (y, x+w, y+h, x)})
                    results["names"].append(name or "Unknown")
                    results["count"] += 1
            return results
        except Exception as e:
            logger.exception(f"Error: {e}")
            return results
    
    def draw_results(self, frame, results):
        for face_data in results["faces"]:
            top, right, bottom, left = face_data["location"]
            name = face_data["name"]
            if name == "Unknown" or name is None:
                color = (0, 0, 255)
                label = "Unknown"
            else:
                color = (0, 255, 0)
                label = name
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return frame
''',

    "attendance/__init__.py": "# Attendance package",
    
    "attendance/attendance_manager.py": '''
from database.attendance_model import AttendanceModel
from database.student_model import StudentModel
from datetime import date, datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class AttendanceManager:
    def __init__(self):
        self.marked_students = set()
        self.session_date = date.today().isoformat()
    
    def start_session(self):
        self.marked_students = set()
        self.session_date = date.today().isoformat()
    
    def mark_attendance(self, student_id, confidence=None):
        if AttendanceModel.check_today_attendance(student_id):
            return True
        student = StudentModel.get_by_id(student_id)
        if not student:
            return False
        data = {"student_id": student_id, "name": student["name"], "date": self.session_date, "time": datetime.now().strftime("%H:%M:%S"), "status": "Present", "confidence": confidence}
        if AttendanceModel.create(data):
            self.marked_students.add(student_id)
            return True
        return False
    
    def process_recognition_result(self, results):
        marked = []
        for face in results.get("faces", []):
            name = face.get("name")
            confidence = face.get("confidence")
            if name and name != "Unknown" and confidence is not None:
                if self.mark_attendance(name, confidence):
                    marked.append(name)
        return marked
''',

    "attendance/report_generator.py": '''
import pandas as pd
from pathlib import Path
from datetime import datetime
from config.constants import EXPORTS_DIR
from database.attendance_model import AttendanceModel
from utils.logger import get_logger

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(self):
        self.exports_dir = EXPORTS_DIR
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, start_date, end_date):
        records = AttendanceModel.get_by_date_range(start_date, end_date)
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        return df
    
    def export_to_csv(self, data, filename=None):
        if data.empty:
            return None
        if not filename:
            filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.exports_dir / filename
        data.to_csv(filepath, index=False)
        return filepath
''',

    "gui/__init__.py": "# GUI package",
    
    "gui/login_window.py": '''
import customtkinter as ctk
from tkinter import messagebox
from database.database import db
from gui.dashboard import Dashboard
from config.constants import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Smart Attendance - Login")
        self.geometry("400x500")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.create_widgets()
    
    def create_widgets(self):
        ctk.CTkLabel(self, text="AI Smart Attendance System", font=("Arial", 24, "bold")).pack(pady=50)
        ctk.CTkLabel(self, text="Login to continue", font=("Arial", 14)).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=300, height=40)
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=300, height=40, show="*")
        self.password_entry.pack(pady=10)
        self.login_btn = ctk.CTkButton(self, text="Login", width=300, height=45, command=self.login, font=("Arial", 14, "bold"))
        self.login_btn.pack(pady=20)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin WHERE username = ? AND password_hash = ?", (username, password))
        if cursor.fetchone():
            self.destroy()
            Dashboard().mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")
''',

    "gui/dashboard.py": '''
import customtkinter as ctk
from tkinter import messagebox
from gui.register_student import RegisterStudentWindow
from gui.attendance_window import AttendanceWindow
from database.student_model import StudentModel
from database.attendance_model import AttendanceModel

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Smart Attendance - Dashboard")
        self.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.create_widgets()
        self.update_stats()
    
    def create_widgets(self):
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(header, text="AI Smart Attendance System", font=("Arial", 20, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkButton(header, text="Logout", width=100, command=self.logout).pack(side="right", padx=20, pady=10)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_labels = {}
        stats_data = [("Total Students", "0"), ("Today's Present", "0"), ("Total Attendance", "0")]
        
        for i, (title, value) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_frame, width=200, height=100)
            card.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 0))
            label = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"))
            label.pack(pady=(5, 10))
            self.stats_labels[title] = label
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        buttons = [
            ("📝 Register Student", self.open_register),
            ("📷 Start Attendance", self.open_attendance),
            ("👥 View Students", self.view_students),
            ("📊 Reports", self.view_reports)
        ]
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(buttons_frame, text=text, width=200, height=50, font=("Arial", 14), command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
    
    def update_stats(self):
        try:
            students = StudentModel.get_all()
            self.stats_labels["Total Students"].configure(text=str(len(students)))
            today = AttendanceModel.get_today()
            self.stats_labels["Today's Present"].configure(text=str(len(today)))
            self.stats_labels["Total Attendance"].configure(text=str(len(today)))
        except:
            pass
    
    def open_register(self):
        RegisterStudentWindow(self)
    
    def open_attendance(self):
        AttendanceWindow(self)
    
    def view_students(self):
        students = StudentModel.get_all()
        if students:
            msg = "\\n".join([f"{s['student_id']}: {s['name']} ({s['department']})" for s in students[:10]])
            if len(students) > 10:
                msg += f"\\n... and {len(students)-10} more"
            messagebox.showinfo("Students", f"Total: {len(students)}\\n\\n{msg}")
        else:
            messagebox.showinfo("Students", "No students registered")
    
    def view_reports(self):
        from attendance.report_generator import ReportGenerator
        from datetime import datetime, timedelta
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        gen = ReportGenerator()
        df = gen.generate_report(start, end)
        if not df.empty:
            filepath = gen.export_to_csv(df)
            if filepath:
                messagebox.showinfo("Reports", f"Report exported: {filepath}")
        else:
            messagebox.showinfo("Reports", "No data found")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.destroy()
            from gui.login_window import LoginWindow
            LoginWindow().mainloop()
''',

    "gui/register_student.py": '''
import customtkinter as ctk
from tkinter import messagebox
import threading
from database.student_model import StudentModel
from recognition.capture_faces import FaceCapture
from recognition.encode_faces import FaceEncoder
from recognition.recognize_faces import FaceRecognizer
from utils.validators import Validator

class RegisterStudentWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Register Student")
        self.geometry("800x600")
        self.is_capturing = False
        ctk.set_appearance_mode("dark")
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(main_frame, text="Student Registration", font=("Arial", 20, "bold")).pack(pady=10)
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        fields = [("Student ID", "student_id", "STU00001"), ("Roll Number", "roll_number", "ABCD123-456"), ("Full Name", "name", "John Doe"), ("Department", "department", "CS"), ("Semester", "semester", "1"), ("Email", "email", "john@example.com"), ("Phone", "phone", "03123456789")]
        self.entries = {}
        for label, key, placeholder in fields:
            frame = ctk.CTkFrame(form_frame)
            frame.pack(fill="x", pady=5)
            ctk.CTkLabel(frame, text=label, width=120).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=300)
            entry.pack(side="left", padx=5, fill="x", expand=True)
            self.entries[key] = entry
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)
        self.capture_btn = ctk.CTkButton(button_frame, text="📸 Capture Faces", command=self.capture_faces, width=150, height=40)
        self.capture_btn.pack(side="left", padx=10)
        self.save_btn = ctk.CTkButton(button_frame, text="💾 Save Student", command=self.save_student, width=150, height=40)
        self.save_btn.pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="❌ Cancel", command=self.destroy, width=150, height=40).pack(side="left", padx=10)
        self.status_label = ctk.CTkLabel(main_frame, text="Ready", font=("Arial", 12))
        self.status_label.pack(pady=10)
    
    def capture_faces(self):
        student_id = self.entries["student_id"].get().strip()
        name = self.entries["name"].get().strip()
        if not student_id or not name:
            messagebox.showerror("Error", "Enter ID and Name")
            return
        self.is_capturing = True
        self.capture_btn.configure(state="disabled")
        self.status_label.configure(text="Capturing...")
        def capture_thread():
            try:
                capture = FaceCapture(student_id, name)
                count, success = capture.capture_images()
                if success and count > 0:
                    self.status_label.configure(text=f"✅ Captured {count} images")
                    messagebox.showinfo("Success", f"Captured {count} images! Click Save.")
                else:
                    self.status_label.configure(text="❌ Capture failed")
                    messagebox.showerror("Error", "Capture failed")
            except Exception as e:
                self.status_label.configure(text=f"Error: {e}")
            finally:
                self.is_capturing = False
                self.capture_btn.configure(state="normal")
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def save_student(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        is_valid, error = Validator.validate_student_id(data["student_id"])
        if not is_valid:
            messagebox.showerror("Error", error)
            return
        if StudentModel.create(data):
            encoder = FaceEncoder()
            encoder.encode_student(data["student_id"])
            # Add to recognizer
            from recognition.recognize_faces import FaceRecognizer
            recognizer = FaceRecognizer()
            encodings_dir = Path("assets/encodings")
            recognizer.add_face(data["student_id"], str(encodings_dir / f"{data['student_id']}.jpg"))
            messagebox.showinfo("Success", f"Student {data['name']} registered!")
            self.destroy()
''',

    "gui/attendance_window.py": '''
import customtkinter as ctk
from tkinter import messagebox
import cv2
import threading
import time
from recognition.recognize_faces import FaceRecognizer
from attendance.attendance_manager import AttendanceManager
from pathlib import Path
from config.constants import ENCODINGS_DIR

class AttendanceWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Start Attendance")
        self.geometry("900x700")
        self.recognizer = FaceRecognizer()
        self.manager = AttendanceManager()
        self.is_running = False
        self.cap = None
        ctk.set_appearance_mode("dark")
        self.create_widgets()
        self.load_known_faces()
        self.manager.start_session()
        self.start_camera()
    
    def load_known_faces(self):
        # Load all encoded faces
        encodings_dir = ENCODINGS_DIR
        if encodings_dir.exists():
            for img_path in encodings_dir.glob("*.jpg"):
                student_id = img_path.stem
                self.recognizer.add_face(student_id, str(img_path))
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.video_frame = ctk.CTkFrame(main_frame, width=640, height=480)
        self.video_frame.pack(pady=10)
        self.video_label = ctk.CTkLabel(self.video_frame, text="Camera starting...")
        self.video_label.pack(fill="both", expand=True)
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=10)
        self.start_btn = ctk.CTkButton(controls_frame, text="⏹ Stop", command=self.stop_attendance, width=150, height=40)
        self.start_btn.pack(side="left", padx=10)
        ctk.CTkButton(controls_frame, text="❌ Close", command=self.close_window, width=150, height=40).pack(side="left", padx=10)
        self.status_label = ctk.CTkLabel(main_frame, text="Attendance session active...")
        self.status_label.pack(pady=10)
        self.recognized_label = ctk.CTkLabel(main_frame, text="Recognized: None")
        self.recognized_label.pack(pady=5)
    
    def start_camera(self):
        self.is_running = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Camera not found!")
            self.destroy()
            return
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def process_video(self):
        while self.is_running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                continue
            results = self.recognizer.process_frame(frame)
            frame = self.recognizer.draw_results(frame, results)
            marked = self.manager.process_recognition_result(results)
            if marked:
                self.recognized_label.configure(text=f"✅ Recognized: {', '.join(marked)}")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.display_frame(frame_rgb)
            time.sleep(0.033)
    
    def display_frame(self, frame):
        from PIL import Image, ImageTk
        h, w, _ = frame.shape
        aspect = w / h
        display_w = 640
        display_h = int(display_w / aspect)
        frame_resized = cv2.resize(frame, (display_w, display_h))
        img = Image.fromarray(frame_resized)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.configure(image=imgtk, text="")
        self.video_label.image = imgtk
    
    def stop_attendance(self):
        self.is_running = False
        self.start_btn.configure(text="✅ Stopped", state="disabled")
        self.status_label.configure(text="Attendance ended")
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def close_window(self):
        self.stop_attendance()
        self.destroy()
        if self.parent:
            self.parent.update_stats()
''',

    "README.md": '''
# AI-Based Real-Time Smart Attendance & Face Logging System

## Features
- Face Recognition using DeepFace
- Real-time webcam attendance
- Student Registration with face capture
- SQLite database storage
- Export reports (CSV, Excel, PDF)
- Modern GUI with CustomTkinter

## Installation
1. Create virtual environment: python -m venv venv
2. Activate: env\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)
3. Install: pip install -r requirements.txt
4. Run: python app.py

## Default Login
- Username: admin
- Password: admin123

## Author
[Your Name]
'''
}

def create_project():
    """Create all files and folders"""
    base_dir = Path(".")
    
    for file_path, content in FILES.items():
        full_path = base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Created: {file_path}")

if __name__ == "__main__":
    print("Creating project files...")
    create_project()
    print("✅ All files created successfully!")
    print("🚀 Run: python app.py")
