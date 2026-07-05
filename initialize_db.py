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