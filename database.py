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