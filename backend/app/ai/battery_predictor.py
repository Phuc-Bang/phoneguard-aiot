import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models

class BatteryPredictor:
    @staticmethod
    def predict_remaining_time(db: Session, device_id: str, current_level: float, current_status: str) -> str:
        """
        Predict remaining time to empty (discharging) or to full (charging) in minutes.
        Returns a human-readable string (e.g. '2h 15m remaining', '35m to full', or 'Calculating...').
        """
        current_status = current_status.lower()
        if current_status in ["full", "not_charging"] and current_level >= 99:
            return "Pin đầy"
        if current_status not in ["charging", "discharging"]:
            return "Không sạc"

        # Fetch logs from the last 30 minutes to compute rate
        thirty_min_ago = datetime.utcnow() - timedelta(minutes=30)
        logs = db.query(models.TelemetryLog)\
            .filter(
                models.TelemetryLog.device_id == device_id,
                models.TelemetryLog.timestamp >= thirty_min_ago
            ).order_by(models.TelemetryLog.timestamp.asc()).all()

        if len(logs) < 5:
            return "Đang tính..."

        # Calculate time and battery change
        first_log = logs[0]
        last_log = logs[-1]
        
        time_diff_min = (last_log.timestamp - first_log.timestamp).total_seconds() / 60.0
        level_diff = last_log.battery_level - first_log.battery_level

        if time_diff_min < 2.0:
            return "Đang tính..."

        # If charging
        if current_status == "charging":
            if level_diff > 0:
                rate_per_min = level_diff / time_diff_min  # % per minute
                remaining_percent = 100.0 - current_level
                if rate_per_min > 0.01:
                    est_minutes = remaining_percent / rate_per_min
                    return BatteryPredictor._format_time(est_minutes, suffix="để sạc đầy")
            # Fallback if logs don't show increase yet, but we are charging
            return "Đang sạc..."

        # If discharging
        elif current_status == "discharging":
            if level_diff < 0:
                rate_per_min = abs(level_diff) / time_diff_min  # % per minute
                if rate_per_min > 0.01:
                    est_minutes = current_level / rate_per_min
                    return BatteryPredictor._format_time(est_minutes, suffix="còn lại")
            # Fallback based on average smartphone battery life if not enough negative diff
            return "Đang tính..."

        return "N/A"

    @staticmethod
    def _format_time(minutes: float, suffix: str) -> str:
        if minutes <= 0:
            return "Xong"
        
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        
        if hours > 0:
            return f"{hours}h {mins}m {suffix}"
        else:
            return f"{mins}m {suffix}"
