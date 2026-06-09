from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Device Schemas
class DeviceBase(BaseModel):
    device_id: str
    name: Optional[str] = "Smartphone"
    model: Optional[str] = "Unknown"
    battery_capacity: Optional[int] = 5000

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Telemetry Schemas
class TelemetryCreate(BaseModel):
    device_id: str
    timestamp: datetime
    battery_level: float = Field(..., ge=0, le=100)
    battery_temperature: float = Field(..., description="In Celsius")
    battery_status: str = Field(..., description="charging, discharging, full, etc.")
    battery_voltage: Optional[float] = None  # in Volts
    network_type: Optional[str] = "Unknown"
    network_strength: Optional[float] = None
    accel_x: Optional[float] = 0.0
    accel_y: Optional[float] = 0.0
    accel_z: Optional[float] = 9.81

class TelemetryResponse(TelemetryCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Anomaly Alert Schemas
class AnomalyAlertBase(BaseModel):
    device_id: str
    anomaly_type: str
    severity: str
    description: str

class AnomalyAlertCreate(AnomalyAlertBase):
    timestamp: Optional[datetime] = None

class AnomalyAlertResponse(AnomalyAlertBase):
    id: int
    timestamp: datetime
    resolved: bool

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationBase(BaseModel):
    device_id: str
    title: str
    content: str
    category: str

class RecommendationResponse(RecommendationBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Dashboard Stats Response Schema
class DashboardStats(BaseModel):
    device_id: str
    device_info: Optional[DeviceResponse] = None
    latest_telemetry: Optional[TelemetryResponse] = None
    time_to_empty_or_full: Optional[str] = "N/A"
    anomaly_score: float = 0.0
    health_status: str = "Good"  # Good, Warning, Critical
    recent_alerts: List[AnomalyAlertResponse] = []
    recent_recommendations: List[RecommendationResponse] = []
