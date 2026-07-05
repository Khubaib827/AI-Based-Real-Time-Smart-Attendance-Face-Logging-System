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