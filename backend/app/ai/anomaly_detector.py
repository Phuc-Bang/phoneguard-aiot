import os
import math
import numpy as np
import joblib
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .. import crud, schemas, models

# Path to the pre-trained Isolation Forest model
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../../models")
ISOLATION_FOREST_PATH = os.path.join(MODEL_DIR, "isolation_forest_model.pkl")

# Load model helper
def load_anomaly_model():
    if os.path.exists(ISOLATION_FOREST_PATH):
        try:
            return joblib.load(ISOLATION_FOREST_PATH)
        except Exception as e:
            print(f"Error loading Isolation Forest model: {e}")
    return None

class AnomalyDetector:
    def __init__(self):
        self.model = load_anomaly_model()
        
    def reload_model(self):
        self.model = load_anomaly_model()

    def process_telemetry(self, db: Session, telemetry: schemas.TelemetryCreate) -> list:
        """
        Process incoming telemetry log. Detects anomalies and creates alerts in the database.
        Returns a list of detected alerts.
        """
        alerts = []
        
        # 1. Acceleration-based Anomaly (Free Fall or Severe Shock)
        accel_mag = math.sqrt(telemetry.accel_x**2 + telemetry.accel_y**2 + telemetry.accel_z**2)
        
        # Free Fall: magnitude close to 0 m/s^2
        if accel_mag < 2.0:
            alert_create = schemas.AnomalyAlertCreate(
                device_id=telemetry.device_id,
                anomaly_type="FREE_FALL",
                severity="CRITICAL",
                description=f"Điện thoại đang bị rơi tự do! Gia tốc magnitude chỉ {accel_mag:.2f} m/s²."
            )
            alerts.append(crud.create_anomaly_alert(db, alert_create))
            
        # Severe Shock/Impact: magnitude > 25 m/s^2 (excluding earth gravity of 9.8)
        elif accel_mag > 25.0:
            alert_create = schemas.AnomalyAlertCreate(
                device_id=telemetry.device_id,
                anomaly_type="SEVERE_SHOCK",
                severity="CRITICAL",
                description=f"Phát hiện chấn động mạnh (va chạm/rơi)! Lực tác động đạt {accel_mag:.2f} m/s²."
            )
            alerts.append(crud.create_anomaly_alert(db, alert_create))
        else:
            # Resolve shocks/free-fall alerts if everything is back to normal
            crud.resolve_alerts_by_type(db, telemetry.device_id, "FREE_FALL")
            crud.resolve_alerts_by_type(db, telemetry.device_id, "SEVERE_SHOCK")

        # 2. Temperature-based Anomaly (Overheating)
        if telemetry.battery_temperature >= 45.0:
            alert_create = schemas.AnomalyAlertCreate(
                device_id=telemetry.device_id,
                anomaly_type="OVERHEATING",
                severity="CRITICAL",
                description=f"Nhiệt độ pin quá cao ({telemetry.battery_temperature}°C)! Nguy cơ cháy nổ, hãy rút sạc và ngừng các tác vụ nặng ngay lập tức."
            )
            alerts.append(crud.create_anomaly_alert(db, alert_create))
        elif telemetry.battery_temperature >= 40.0:
            alert_create = schemas.AnomalyAlertCreate(
                device_id=telemetry.device_id,
                anomaly_type="HIGH_TEMPERATURE",
                severity="WARNING",
                description=f"Pin đang nóng ({telemetry.battery_temperature}°C). Hãy chú ý nhiệt độ môi trường và sạc pin."
            )
            alerts.append(crud.create_anomaly_alert(db, alert_create))
        else:
            crud.resolve_alerts_by_type(db, telemetry.device_id, "OVERHEATING")
            crud.resolve_alerts_by_type(db, telemetry.device_id, "HIGH_TEMPERATURE")

        # 3. Battery Drain Rate Anomaly (Isolation Forest or Rule-based)
        # Fetch previous logs from the last 15 minutes to calculate drain rate
        logs = db.query(models.TelemetryLog)\
            .filter(
                models.TelemetryLog.device_id == telemetry.device_id,
                models.TelemetryLog.timestamp >= telemetry.timestamp - timedelta(minutes=15)
            ).order_by(models.TelemetryLog.timestamp.desc()).all()
            
        if len(logs) >= 2:
            # Calculate battery change and time delta
            latest = logs[0]
            oldest = logs[-1]
            time_diff_min = (latest.timestamp - oldest.timestamp).total_seconds() / 60.0
            
            if time_diff_min > 2.0:  # Must span at least 2 minutes
                level_diff = oldest.battery_level - latest.battery_level
                
                # If battery is discharging
                if latest.battery_status.lower() in ["discharging", "not_charging"] and level_diff > 0:
                    drain_rate = level_diff / time_diff_min  # % per minute
                    
                    # Rule-based threshold: draining more than 1.5% per minute
                    if drain_rate > 1.5:
                        alert_create = schemas.AnomalyAlertCreate(
                            device_id=telemetry.device_id,
                            anomaly_type="BATTERY_DRAIN_ANOMALY",
                            severity="WARNING",
                            description=f"Tốc độ tụt pin bất thường ({drain_rate:.2f}% mỗi phút). Phát hiện các ứng dụng chạy ngầm ngốn pin."
                        )
                        alerts.append(crud.create_anomaly_alert(db, alert_create))
                    else:
                        # If we have an Isolation Forest model, evaluate it
                        if self.model:
                            try:
                                # Feature shape for Isolation Forest: [battery_level, battery_temperature, battery_voltage, accel_mag, drain_rate]
                                features = np.array([[
                                    telemetry.battery_level,
                                    telemetry.battery_temperature,
                                    telemetry.battery_voltage if telemetry.battery_voltage else 4.0,
                                    accel_mag,
                                    drain_rate
                                ]])
                                prediction = self.model.predict(features)
                                if prediction[0] == -1:  # -1 represents an anomaly in Isolation Forest
                                    alert_create = schemas.AnomalyAlertCreate(
                                        device_id=telemetry.device_id,
                                        anomaly_type="BATTERY_DRAIN_ANOMALY",
                                        severity="WARNING",
                                        description=f"Phát hiện bất thường trong hành vi sử dụng năng lượng bằng AI (Tốc độ xả pin: {drain_rate:.2f}%/m)."
                                    )
                                    alerts.append(crud.create_anomaly_alert(db, alert_create))
                                else:
                                    crud.resolve_alerts_by_type(db, telemetry.device_id, "BATTERY_DRAIN_ANOMALY")
                            except Exception as e:
                                print(f"Error predicting with Isolation Forest: {e}")
                        else:
                            crud.resolve_alerts_by_type(db, telemetry.device_id, "BATTERY_DRAIN_ANOMALY")
                else:
                    # Charging or not draining
                    crud.resolve_alerts_by_type(db, telemetry.device_id, "BATTERY_DRAIN_ANOMALY")
                    
        return [a for a in alerts if a is not None]

# Global instance
detector = AnomalyDetector()
