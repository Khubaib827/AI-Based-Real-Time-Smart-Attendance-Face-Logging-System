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