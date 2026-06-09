"""Dự báo battery_level bằng baseline linear trend từ telemetry CSV."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .schemas import ForecastResult, TelemetryIn, parse_iso_datetime
from .storage import append_forecast, get_latest, read_telemetry


MODEL_VERSION = "battery_linear_trend_v1"
SAFETY_NOTE = "Forecast chỉ là tín hiệu khuyến nghị, không phải lệnh điều khiển."


@dataclass
class ForecastPoint:
    """Điểm dữ liệu sạch dùng để fit linear trend."""

    timestamp: datetime
    battery_level: float


def forecast_battery(telemetry: TelemetryIn | None = None, device_id: str | None = None) -> ForecastResult:
    """Dự báo battery_level sau 15 và 30 phút từ telemetry hiện tại và lịch sử CSV."""
    current = _resolve_current_telemetry(telemetry=telemetry, device_id=device_id)
    output_device_id = current["device_id"] if current else (device_id or "unknown")

    if current is None:
        result = _fallback_result(
            predicted_battery=None,
            reason="Chưa có telemetry hiện tại và CSV chưa có dữ liệu hợp lệ.",
        )
        append_forecast(output_device_id, result)
        return result

    history = _load_clean_history(current["device_id"])
    points = _merge_current_point(history, current)

    if len(points) < 2:
        result = _fallback_result(
            predicted_battery=current["battery_level"],
            reason="Cần ít nhất 2 mẫu có timestamp và battery_level để tính linear trend.",
        )
        append_forecast(output_device_id, result)
        return result

    trend_percent_per_min = _linear_trend_percent_per_min(points)
    predicted_15 = clamp_battery(current["battery_level"] + trend_percent_per_min * 15)
    predicted_30 = clamp_battery(current["battery_level"] + trend_percent_per_min * 30)
    confidence = _estimate_confidence(points)
    decision = _build_decision(predicted_30, reason=f"Linear trend={trend_percent_per_min:.4f}%/phút từ {len(points)} mẫu gần nhất.")

    result = ForecastResult(
        model_output={
            "target": "battery_level",
            "predicted_battery_15min": round(predicted_15, 2),
            "predicted_battery_30min": round(predicted_30, 2),
            "model_version": MODEL_VERSION,
            "confidence": confidence,
        },
        decision=decision,
    )
    append_forecast(output_device_id, result)
    print(
        "[DEBUG] Forecast "
        f"device={output_device_id} "
        f"p15={predicted_15:.2f} p30={predicted_30:.2f} confidence={confidence:.2f}"
    )
    return result


def clamp_battery(value: float) -> float:
    """Giới hạn battery prediction trong khoảng 0 đến 100."""
    return max(0.0, min(100.0, value))


def _resolve_current_telemetry(telemetry: TelemetryIn | None, device_id: str | None) -> dict[str, Any] | None:
    """Lấy telemetry hiện tại từ request hoặc fallback sang bản mới nhất trong CSV."""
    if telemetry is not None:
        return {
            "device_id": telemetry.device_id,
            "timestamp": telemetry.timestamp,
            "battery_level": telemetry.battery_level,
        }

    latest = get_latest(device_id=device_id)
    if latest is None:
        return None
    if latest.get("timestamp") in (None, "") or latest.get("battery_level") is None:
        return None
    return {
        "device_id": latest["device_id"],
        "timestamp": latest["timestamp"],
        "battery_level": latest["battery_level"],
    }


def _load_clean_history(device_id: str) -> list[ForecastPoint]:
    """Đọc lịch sử CSV và bỏ qua dòng thiếu timestamp hoặc battery_level."""
    points: list[ForecastPoint] = []
    for row in read_telemetry(limit=40, device_id=device_id):
        try:
            if row.get("timestamp") in (None, "") or row.get("battery_level") is None:
                continue
            points.append(
                ForecastPoint(
                    timestamp=parse_iso_datetime(row["timestamp"]),
                    battery_level=float(row["battery_level"]),
                )
            )
        except (TypeError, ValueError):
            print(f"[DEBUG] Bo qua dong forecast khong hop le: {row}")
    return points


def _merge_current_point(history: list[ForecastPoint], current: dict[str, Any]) -> list[ForecastPoint]:
    """Thêm telemetry hiện tại vào history nếu timestamp chưa trùng dòng cuối."""
    points = list(history)
    try:
        current_point = ForecastPoint(
            timestamp=parse_iso_datetime(current["timestamp"]),
            battery_level=float(current["battery_level"]),
        )
    except (TypeError, ValueError):
        return points

    if not points or points[-1].timestamp != current_point.timestamp:
        points.append(current_point)
    return points[-40:]


def _linear_trend_percent_per_min(points: list[ForecastPoint]) -> float:
    """Tính slope tuyến tính battery_level theo phút bằng công thức bình phương tối thiểu."""
    base_time = points[0].timestamp
    x_values = [(point.timestamp - base_time).total_seconds() / 60 for point in points]
    y_values = [point.battery_level for point in points]
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _estimate_confidence(points: list[ForecastPoint]) -> float:
    """Ước lượng confidence đơn giản theo số mẫu và độ dài cửa sổ thời gian."""
    elapsed_minutes = max((points[-1].timestamp - points[0].timestamp).total_seconds() / 60, 0)
    sample_score = min(len(points) / 8, 1.0)
    time_score = min(elapsed_minutes / 10, 1.0)
    return round(max(0.2, min((sample_score + time_score) / 2, 0.95)), 2)


def _fallback_result(predicted_battery: float | None, reason: str) -> ForecastResult:
    """Tạo response fallback rõ ràng khi dữ liệu chưa đủ hoặc thiếu field."""
    predicted = 100.0 if predicted_battery is None else clamp_battery(predicted_battery)
    risk_level = "NORMAL" if predicted_battery is None else _risk_level(predicted)
    return ForecastResult(
        model_output={
            "target": "battery_level",
            "predicted_battery_15min": round(predicted, 2),
            "predicted_battery_30min": round(predicted, 2),
            "model_version": MODEL_VERSION,
            "confidence": 0.2,
        },
        decision={
            "risk_level": risk_level,
            "recommendation": "Thu thập thêm telemetry trước khi dùng forecast để ra quyết định.",
            "reason": reason,
            "safety_note": SAFETY_NOTE,
        },
    )


def _build_decision(predicted_battery_30min: float, reason: str) -> dict[str, str]:
    """Tạo quyết định rủi ro từ predicted_battery_30min."""
    risk_level = _risk_level(predicted_battery_30min)
    if risk_level == "CRITICAL":
        recommendation = "Pin có nguy cơ cạn rất sớm, hãy cắm sạc ngay nếu cần tiếp tục giám sát."
    elif risk_level == "HIGH":
        recommendation = "Chuẩn bị sạc hoặc giảm tần suất gửi telemetry."
    elif risk_level == "WARNING":
        recommendation = "Theo dõi pin sát hơn trong 30 phút tới."
    else:
        recommendation = "Pin dự kiến vẫn đủ cho chu kỳ giám sát ngắn hạn."

    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "reason": reason,
        "safety_note": SAFETY_NOTE,
    }


def _risk_level(predicted_battery_30min: float) -> str:
    """Áp dụng risk rule theo predicted_battery_30min."""
    if predicted_battery_30min < 5:
        return "CRITICAL"
    if predicted_battery_30min < 10:
        return "HIGH"
    if predicted_battery_30min < 20:
        return "WARNING"
    return "NORMAL"
