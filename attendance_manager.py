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