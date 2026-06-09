"""Dự báo pin đơn giản từ lịch sử telemetry CSV."""

from .schemas import ForecastResult, parse_iso_datetime
from .storage import append_forecast, read_telemetry


def forecast_battery(device_id: str | None = None) -> ForecastResult:
    """Ước lượng thời gian hết pin dựa trên độ dốc pin trong lịch sử gần nhất."""
    rows = read_telemetry(limit=40, device_id=device_id)
    if not rows:
        result = ForecastResult(
            device_id=device_id or "unknown",
            current_battery_level=None,
            estimated_minutes_remaining=None,
            trend_percent_per_hour=None,
            message="Chưa có dữ liệu telemetry để dự báo",
        )
        append_forecast(result)
        return result

    latest = rows[-1]
    if len(rows) < 2:
        result = ForecastResult(
            device_id=latest["device_id"],
            current_battery_level=latest["battery_level"],
            estimated_minutes_remaining=None,
            trend_percent_per_hour=None,
            message="Cần ít nhất 2 mẫu telemetry để tính xu hướng",
        )
        append_forecast(result)
        return result

    first = rows[0]
    elapsed_hours = max((parse_iso_datetime(latest["timestamp"]) - parse_iso_datetime(first["timestamp"])).total_seconds() / 3600, 1 / 3600)
    trend = (latest["battery_level"] - first["battery_level"]) / elapsed_hours

    if latest["charging"]:
        minutes = None
        message = "Thiết bị đang sạc, không tính thời gian hết pin"
    elif trend >= 0:
        minutes = None
        message = "Pin chưa giảm trong cửa sổ dữ liệu gần nhất"
    else:
        minutes = round((latest["battery_level"] / abs(trend)) * 60, 1)
        message = f"Ước lượng còn khoảng {minutes} phút trước khi hết pin"

    print(f"[DEBUG] Forecast device={latest['device_id']} trend={trend:.3f}%/h")
    result = ForecastResult(
        device_id=latest["device_id"],
        current_battery_level=latest["battery_level"],
        estimated_minutes_remaining=minutes,
        trend_percent_per_hour=round(trend, 3),
        message=message,
    )
    append_forecast(result)
    return result
