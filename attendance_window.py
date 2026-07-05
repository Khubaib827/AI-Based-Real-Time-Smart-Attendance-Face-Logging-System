"""
gui/attendance_window.py - Attendance Window (FIXED)
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
import threading
import time
from PIL import Image, ImageTk
import os

from recognition.recognize_faces import FaceRecognizer
from attendance.attendance_manager import AttendanceManager
from utils.logger import get_logger
from config.constants import ENCODINGS_DIR

logger = get_logger(__name__)


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
        self.camera_ready = False
        
        ctk.set_appearance_mode("dark")
        self.create_widgets()
        
        # Load known faces
        self.load_known_faces()
        
        # Start attendance session
        self.manager.start_session()
        
        # Start camera after UI loads
        self.after(500, self.start_camera)
    
    def load_known_faces(self):
        """Load all encoded faces"""
        if ENCODINGS_DIR.exists():
            for img_path in ENCODINGS_DIR.glob("*.jpg"):
                student_id = img_path.stem
                self.recognizer.add_face(student_id, str(img_path))
                logger.info(f"Loaded face: {student_id}")
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Video frame
        self.video_frame = ctk.CTkFrame(main_frame, width=640, height=480)
        self.video_frame.pack(pady=10)
        
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text="📷 Camera starting...\n\nPlease wait...",
            font=("Arial", 20)
        )
        self.video_label.pack(fill="both", expand=True)
        
        # Controls
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=10)
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="⏹ Stop Attendance",
            command=self.stop_attendance,
            width=150,
            height=40
        )
        self.stop_btn.pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="📊 Summary",
            command=self.show_summary,
            width=150,
            height=40
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="❌ Close",
            command=self.close_window,
            width=150,
            height=40
        ).pack(side="left", padx=10)
        
        # Status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="🔄 Initializing camera...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        self.recognized_label = ctk.CTkLabel(
            main_frame,
            text="Recognized: None",
            font=("Arial", 12)
        )
        self.recognized_label.pack(pady=5)
    
    def start_camera(self):
        """Start the camera with multiple attempts"""
        self.is_running = True
        
        # Try different camera indices
        camera_indices = [0, 1, 2]
        camera_found = False
        
        for idx in camera_indices:
            try:
                self.status_label.configure(text=f"🔄 Trying camera {idx}...")
                self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # DirectShow for Windows
                
                if self.cap.isOpened():
                    camera_found = True
                    self.status_label.configure(text=f"✅ Camera {idx} opened!")
                    logger.info(f"Camera {idx} opened successfully")
                    break
                else:
                    self.cap.release()
                    self.cap = None
            except Exception as e:
                logger.error(f"Camera {idx} error: {e}")
                self.cap = None
        
        if not camera_found:
            self.video_label.configure(text="❌ No Camera Found!\n\nPlease:\n1. Connect webcam\n2. Check permissions\n3. Restart app")
            self.status_label.configure(text="❌ Camera not found!")
            messagebox.showerror(
                "Camera Error",
                "No camera detected!\n\n"
                "Please check:\n"
                "1. Camera is connected\n"
                "2. Camera drivers are installed\n"
                "3. Camera permissions are enabled\n"
                "4. Close other apps using camera"
            )
            self.is_running = False
            return
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Test if camera can read
        ret, test_frame = self.cap.read()
        if not ret:
            self.video_label.configure(text="❌ Camera Error!\n\nCannot read from camera.")
            self.status_label.configure(text="❌ Camera read error!")
            self.is_running = False
            return
        
        self.camera_ready = True
        self.video_label.configure(text="📷 Camera ready!\nWaiting for faces...")
        self.status_label.configure(text="📷 Attendance session active...")
        
        # Start video processing thread
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def process_video(self):
        """Process video frames for face recognition"""
        frame_count = 0
        
        while self.is_running and self.cap is not None:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.status_label.configure(text="⚠️ Camera disconnected!")
                    time.sleep(0.5)
                    continue
                
                frame_count += 1
                
                # Process every 2nd frame for better performance
                if frame_count % 2 != 0:
                    # Still display frame even if not processing
                    self.display_frame(frame)
                    continue
                
                # Process frame for face recognition
                results = self.recognizer.process_frame(frame)
                
                # Draw results on frame
                annotated_frame = self.recognizer.draw_results(frame.copy(), results)
                
                # Mark attendance for recognized faces
                if results and results.get('faces'):
                    marked = self.manager.process_recognition_result(results)
                    if marked:
                        self.recognized_label.configure(text=f"✅ Recognized: {', '.join(marked)}")
                        # Reset after 3 seconds
                        self.after(3000, lambda: self.recognized_label.configure(text="Recognized: None"))
                
                # Display frame
                self.display_frame(annotated_frame)
                
            except Exception as e:
                logger.exception(f"Error in video processing: {e}")
                time.sleep(0.1)
        
        logger.info("Video processing stopped")
    
    def display_frame(self, frame):
        """Display frame in the GUI"""
        try:
            # Resize frame
            height, width = frame.shape[:2]
            display_width = 640
            display_height = int(display_width * height / width)
            frame_resized = cv2.resize(frame, (display_width, display_height))
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.video_label.configure(image=imgtk, text="")
            self.video_label.image = imgtk
            
        except Exception as e:
            logger.exception(f"Error displaying frame: {e}")
    
    def stop_attendance(self):
        """Stop attendance session"""
        self.is_running = False
        self.manager.end_session()
        self.stop_btn.configure(text="✅ Stopped", state="disabled")
        self.status_label.configure(text="Attendance session ended")
        self.video_label.configure(text="📷 Session ended")
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Attendance stopped")
    
    def show_summary(self):
        """Show attendance summary"""
        summary = self.manager.get_attendance_summary()
        if summary:
            msg = f"""
            📊 Attendance Summary
            =====================
            Date: {summary.get('date', 'N/A')}
            Total Students: {summary.get('total_students', 0)}
            Present Today: {summary.get('present_today', 0)}
            Absent Today: {summary.get('absent_today', 0)}
            Attendance Percentage: {summary.get('attendance_percentage', 0)}%
            """
            messagebox.showinfo("Attendance Summary", msg)
    
    def close_window(self):
        """Close the window"""
        self.stop_attendance()
        self.destroy()
        if self.parent:
            self.parent.update_stats()