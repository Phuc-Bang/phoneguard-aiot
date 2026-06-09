from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas
from datetime import datetime

# Device Operations
def get_device_by_id(db: Session, device_id: str):
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()

def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(
        device_id=device.device_id,
        name=device.name,
        model=device.model,
        battery_capacity=device.battery_capacity
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

# Telemetry Operations
def get_telemetry_logs(db: Session, device_id: str, limit: int = 100):
    return db.query(models.TelemetryLog)\
        .filter(models.TelemetryLog.device_id == device_id)\
        .order_by(desc(models.TelemetryLog.timestamp))\
        .limit(limit)\
        .all()

def create_telemetry_log(db: Session, telemetry: schemas.TelemetryCreate):
    db_log = models.TelemetryLog(
        device_id=telemetry.device_id,
        timestamp=telemetry.timestamp,
        battery_level=telemetry.battery_level,
        battery_temperature=telemetry.battery_temperature,
        battery_status=telemetry.battery_status,
        battery_voltage=telemetry.battery_voltage,
        network_type=telemetry.network_type,
        network_strength=telemetry.network_strength,
        accel_x=telemetry.accel_x,
        accel_y=telemetry.accel_y,
        accel_z=telemetry.accel_z
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Anomaly Alert Operations
def get_anomaly_alerts(db: Session, device_id: str, limit: int = 10):
    return db.query(models.AnomalyAlert)\
        .filter(models.AnomalyAlert.device_id == device_id)\
        .order_by(desc(models.AnomalyAlert.timestamp))\
        .limit(limit)\
        .all()

def create_anomaly_alert(db: Session, alert: schemas.AnomalyAlertCreate):
    # Check if duplicate alert of same type exists in the last 1 minute to avoid flooding
    from datetime import datetime, timedelta
    one_min_ago = datetime.utcnow() - timedelta(minutes=1)
    # Convert alert timestamp if present
    ts = alert.timestamp if alert.timestamp else datetime.utcnow()
    
    duplicate = db.query(models.AnomalyAlert)\
        .filter(
            models.AnomalyAlert.device_id == alert.device_id,
            models.AnomalyAlert.anomaly_type == alert.anomaly_type,
            models.AnomalyAlert.timestamp >= one_min_ago
        ).first()
        
    if duplicate:
        return duplicate

    db_alert = models.AnomalyAlert(
        device_id=alert.device_id,
        timestamp=ts,
        anomaly_type=alert.anomaly_type,
        severity=alert.severity,
        description=alert.description,
        resolved=False
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def resolve_alerts_by_type(db: Session, device_id: str, anomaly_type: str):
    db.query(models.AnomalyAlert)\
        .filter(models.AnomalyAlert.device_id == device_id, models.AnomalyAlert.anomaly_type == anomaly_type, models.AnomalyAlert.resolved == False)\
        .update({models.AnomalyAlert.resolved: True})
    db.commit()

# Recommendation Operations
def get_recommendations(db: Session, device_id: str, limit: int = 5):
    return db.query(models.Recommendation)\
        .filter(models.Recommendation.device_id == device_id)\
        .order_by(desc(models.Recommendation.timestamp))\
        .limit(limit)\
        .all()

def create_recommendation(db: Session, rec: schemas.RecommendationBase):
    # Avoid duplicate active recommendation of same category in last 5 minutes
    from datetime import datetime, timedelta
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    
    duplicate = db.query(models.Recommendation)\
        .filter(
            models.Recommendation.device_id == rec.device_id,
            models.Recommendation.category == rec.category,
            models.Recommendation.title == rec.title,
            models.Recommendation.timestamp >= five_min_ago
        ).first()

    if duplicate:
        return duplicate

    db_rec = models.Recommendation(
        device_id=rec.device_id,
        title=rec.title,
        content=rec.content,
        category=rec.category
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

def clear_old_recommendations(db: Session, device_id: str, keep_limit: int = 5):
    # Keeps only the top N latest recommendations
    subq = db.query(models.Recommendation.id)\
        .filter(models.Recommendation.device_id == device_id)\
        .order_by(desc(models.Recommendation.timestamp))\
        .limit(keep_limit)\
        .all()
    keep_ids = [r[0] for r in subq]
    
    if keep_ids:
        db.query(models.Recommendation)\
            .filter(models.Recommendation.device_id == device_id, ~models.Recommendation.id.in_(keep_ids))\
            .delete(synchronize_session=False)
        db.commit()
