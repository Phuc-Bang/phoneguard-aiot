from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, default="Smartphone")
    model = Column(String, default="Unknown Model")
    battery_capacity = Column(Integer, default=5000)  # mAh
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    battery_level = Column(Float, nullable=False)  # 0 to 100
    battery_temperature = Column(Float, nullable=False)  # Celsius
    battery_status = Column(String, nullable=False)  # charging, discharging, full, etc.
    battery_voltage = Column(Float, nullable=True)  # Volts
    network_type = Column(String, default="Unknown")
    network_strength = Column(Float, nullable=True)
    accel_x = Column(Float, default=0.0)
    accel_y = Column(Float, default=0.0)
    accel_z = Column(Float, default=9.81)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    anomaly_type = Column(String, nullable=False)  # FREE_FALL, OVERHEATING, DRAIN_ANOMALY
    severity = Column(String, nullable=False)  # INFO, WARNING, CRITICAL
    description = Column(String, nullable=False)
    resolved = Column(Boolean, default=False)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(String, nullable=False)  # BATTERY, TEMPERATURE, USAGE
