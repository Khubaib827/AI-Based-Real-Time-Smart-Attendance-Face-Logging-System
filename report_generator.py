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