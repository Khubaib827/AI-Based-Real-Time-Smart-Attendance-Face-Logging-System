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