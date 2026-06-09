"""Lưu trữ CSV cho telemetry, anomaly event và forecast log."""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from .schemas import ForecastResult, TelemetryIn, none_to_empty


PROJECT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(os.getenv("PHONEGUARD_OUTPUT_DIR", PROJECT_DIR / "outputs"))
TELEMETRY_FILE = OUTPUT_DIR / "phone_telemetry.csv"
ANOMALY_FILE = OUTPUT_DIR / "anomaly_event_log.csv"
FORECAST_FILE = OUTPUT_DIR / "forecast_log.csv"

TELEMETRY_FIELDS = [
    "device_id",
    "timestamp",
    "battery_level",
    "charging",
    "acc_x",
    "acc_y",
    "acc_z",
    "light_lux",
    "network_type",
    "received_at",
]

ANOMALY_FIELDS = [
    "event_id",
    "device_id",
    "timestamp",
    "event_type",
    "severity",
    "decision",
    "explanation",
    "recommendation",
    "safety_note",
    "anomaly_score",
    "model_version",
]

FORECAST_FIELDS = [
    "forecast_id",
    "device_id",
    "timestamp",
    "current_battery_level",
    "estimated_minutes_remaining",
    "trend_percent_per_hour",
    "message",
]

_lock = Lock()


def ensure_storage() -> None:
    """Tạo thư mục outputs và các file CSV với header chuẩn."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_csv(TELEMETRY_FILE, TELEMETRY_FIELDS)
    _ensure_csv(ANOMALY_FILE, ANOMALY_FIELDS)
    _ensure_csv(FORECAST_FILE, FORECAST_FIELDS)


def _ensure_csv(path: Path, fields: list[str]) -> None:
    """Tạo file CSV mới khi file chưa tồn tại."""
    if path.exists() and _csv_header_matches(path, fields):
        return
    if path.exists():
        backup_path = path.with_suffix(f".bak-{int(datetime.now(timezone.utc).timestamp())}.csv")
        path.rename(backup_path)
        print(f"[DEBUG] Header CSV cu khong khop, da backup: {backup_path}")
    with path.open("w", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=fields).writeheader()
    print(f"[DEBUG] Tao CSV file: {path}")


def _csv_header_matches(path: Path, fields: list[str]) -> bool:
    """Kiểm tra header CSV để tránh ghi sai cột sau khi schema log thay đổi."""
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader, [])
    return header == fields


def append_telemetry(telemetry: TelemetryIn) -> dict[str, Any]:
    """Ghi telemetry vào outputs/phone_telemetry.csv."""
    ensure_storage()
    row = {
        "device_id": telemetry.device_id,
        "timestamp": telemetry.timestamp,
        "battery_level": telemetry.battery_level,
        "charging": telemetry.charging,
        "acc_x": none_to_empty(telemetry.acc_x),
        "acc_y": none_to_empty(telemetry.acc_y),
        "acc_z": none_to_empty(telemetry.acc_z),
        "light_lux": none_to_empty(telemetry.light_lux),
        "network_type": none_to_empty(telemetry.network_type),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        with TELEMETRY_FILE.open("a", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=TELEMETRY_FIELDS).writerow(row)
    print(f"[DEBUG] Luu telemetry device={telemetry.device_id} pin={telemetry.battery_level}%")
    return coerce_telemetry_row(row)


def read_telemetry(limit: int | None = None, device_id: str | None = None) -> list[dict[str, Any]]:
    """Đọc lịch sử telemetry từ CSV, hỗ trợ lọc thiết bị và giới hạn số dòng."""
    ensure_storage()
    with TELEMETRY_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = [coerce_telemetry_row(row) for row in csv.DictReader(file)]
    if device_id:
        rows = [row for row in rows if row["device_id"] == device_id]
    if limit is not None:
        rows = rows[-limit:]
    return rows


def get_latest(device_id: str | None = None) -> dict[str, Any] | None:
    """Lấy telemetry mới nhất, trả None nếu chưa có dữ liệu."""
    rows = read_telemetry(device_id=device_id)
    if not rows:
        return None
    return rows[-1]


def append_anomaly_event(device_id: str, timestamp: str, result: dict[str, Any]) -> dict[str, Any]:
    """Ghi anomaly event vào outputs/anomaly_event_log.csv."""
    ensure_storage()
    event_id = f"{device_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    model_output = result["model_output"]
    event = result["event"]
    row = {
        "event_id": event_id,
        "device_id": device_id,
        "timestamp": timestamp,
        "event_type": event["event_type"],
        "severity": event["severity"],
        "decision": event["decision"],
        "explanation": event["explanation"],
        "recommendation": event["recommendation"],
        "safety_note": event["safety_note"],
        "anomaly_score": model_output["anomaly_score"],
        "model_version": model_output["model_version"],
    }
    with _lock:
        with ANOMALY_FILE.open("a", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=ANOMALY_FIELDS).writerow(row)
    print(f"[DEBUG] Luu anomaly event device={device_id} severity={event['severity']}")
    return row


def read_events(limit: int = 100, device_id: str | None = None) -> list[dict[str, Any]]:
    """Đọc danh sách anomaly events mới nhất."""
    ensure_storage()
    with ANOMALY_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if device_id:
        rows = [row for row in rows if row["device_id"] == device_id]
    return rows[-limit:]


def append_forecast(result: ForecastResult) -> dict[str, Any]:
    """Ghi kết quả forecast vào outputs/forecast_log.csv."""
    ensure_storage()
    timestamp = datetime.now(timezone.utc).isoformat()
    row = {
        "forecast_id": f"{result.device_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}",
        "device_id": result.device_id,
        "timestamp": timestamp,
        "current_battery_level": none_to_empty(result.current_battery_level),
        "estimated_minutes_remaining": none_to_empty(result.estimated_minutes_remaining),
        "trend_percent_per_hour": none_to_empty(result.trend_percent_per_hour),
        "message": result.message,
    }
    with _lock:
        with FORECAST_FILE.open("a", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=FORECAST_FIELDS).writerow(row)
    print(f"[DEBUG] Luu forecast log device={result.device_id}")
    return row


def coerce_telemetry_row(row: dict[str, Any]) -> dict[str, Any]:
    """Ép kiểu dữ liệu đọc từ CSV về JSON đúng schema."""
    return {
        "device_id": row["device_id"],
        "timestamp": row["timestamp"],
        "battery_level": float(row["battery_level"]),
        "charging": str(row["charging"]).lower() == "true",
        "acc_x": _optional_float(row.get("acc_x")),
        "acc_y": _optional_float(row.get("acc_y")),
        "acc_z": _optional_float(row.get("acc_z")),
        "light_lux": _optional_float(row.get("light_lux")),
        "network_type": row.get("network_type") or None,
        "received_at": row["received_at"],
    }


def _optional_float(value: Any) -> float | None:
    """Chuyển chuỗi rỗng thành None, còn lại thành float."""
    if value in (None, ""):
        return None
    return float(value)
