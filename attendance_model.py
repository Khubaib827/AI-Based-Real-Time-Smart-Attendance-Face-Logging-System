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