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