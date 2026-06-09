"""Schema Pydantic cho backend PhoneGuard AIoT."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TelemetryIn(BaseModel):
    """Telemetry do điện thoại Android gửi lên API."""

    device_id: str = Field(..., min_length=1)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    battery_level: float = Field(..., ge=0, le=100)
    charging: bool
    acc_x: float | None = None
    acc_y: float | None = None
    acc_z: float | None = None
    light_lux: float | None = None
    network_type: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value: str | None) -> str:
        """Chuẩn hóa timestamp về ISO string để lưu CSV nhất quán."""
        if not value:
            return datetime.now(timezone.utc).isoformat()
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @field_validator("network_type")
    @classmethod
    def normalize_network_type(cls, value: str | None) -> str | None:
        """Cắt khoảng trắng network_type nếu client gửi chuỗi."""
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class TelemetryOut(TelemetryIn):
    """Telemetry sau khi backend đã ghi nhận."""

    received_at: str


class AnomalyModelOutput(BaseModel):
    """Phần output mô hình của anomaly detector."""

    is_anomaly: bool
    anomaly_score: float
    model_version: str = "rule_iforest_v1"


class AnomalyEvent(BaseModel):
    """Phần event giải thích quyết định anomaly."""

    event_type: str
    severity: str
    decision: str
    explanation: str
    recommendation: str
    safety_note: str = "AI chỉ cảnh báo, không tự động điều khiển thiết bị."


class AnomalyResult(BaseModel):
    """Kết quả phát hiện dị thường theo contract Lab."""

    model_output: AnomalyModelOutput
    event: AnomalyEvent


class ForecastRequest(BaseModel):
    """Payload tùy chọn cho endpoint forecast."""

    device_id: str | None = None


class ForecastResult(BaseModel):
    """Kết quả dự báo pin từ lịch sử telemetry."""

    device_id: str
    current_battery_level: float | None
    estimated_minutes_remaining: float | None
    trend_percent_per_hour: float | None
    message: str


class RiskResult(BaseModel):
    """Kết quả dự đoán rủi ro và khuyến nghị vận hành."""

    device_id: str
    risk_level: str
    risk_score: float
    recommendations: list[str]


class ModelInfo(BaseModel):
    """Thông tin mô hình inference rule-based hiện tại."""

    name: str
    version: str
    type: str
    storage: str
    telemetry_file: str
    anomaly_file: str
    forecast_file: str
    telemetry_fields: list[str]


def parse_iso_datetime(value: str) -> datetime:
    """Chuyển ISO string sang datetime, dùng chung cho storage và forecast."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def none_to_empty(value: Any) -> Any:
    """Chuyển None sang chuỗi rỗng khi ghi CSV để tránh chữ 'None' trong log."""
    return "" if value is None else value
