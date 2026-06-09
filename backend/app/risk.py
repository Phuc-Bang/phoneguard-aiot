"""Dự đoán rủi ro và khuyến nghị vận hành từ telemetry."""

from .anomaly import detect_anomaly
from .schemas import RiskResult, TelemetryIn


def predict_risk(telemetry: TelemetryIn) -> RiskResult:
    """Kết hợp anomaly score và trạng thái pin/mạng để tạo risk recommendation."""
    anomaly = detect_anomaly(telemetry, persist_event=False)
    score = anomaly.model_output.anomaly_score
    recommendations: list[str] = []

    if telemetry.battery_level <= 20 and not telemetry.charging:
        score += 0.2
        recommendations.append("Cắm sạc hoặc giảm tần suất gửi telemetry để tránh tắt nguồn.")

    network_type = (telemetry.network_type or "unknown").lower()
    if network_type in {"cellular", "4g", "5g"}:
        recommendations.append("Ưu tiên Wi-Fi khi làm lab để giảm tiêu thụ pin và ổn định kết nối.")
    elif network_type in {"none", "offline", "unknown"}:
        recommendations.append("Kiểm tra kết nối mạng trước khi chạy thu thập telemetry dài hạn.")

    if anomaly.model_output.is_anomaly:
        recommendations.append(anomaly.event.explanation)
        recommendations.append(anomaly.event.recommendation)

    if not recommendations:
        recommendations.append("Thiết bị ổn định, tiếp tục gửi telemetry theo chu kỳ.")

    score = min(score, 1.0)
    if score >= 0.7:
        risk_level = "high"
    elif score >= 0.35:
        risk_level = "medium"
    else:
        risk_level = "low"

    print(f"[DEBUG] Risk device={telemetry.device_id} score={score:.2f} level={risk_level}")
    return RiskResult(
        device_id=telemetry.device_id,
        risk_level=risk_level,
        risk_score=round(score, 3),
        recommendations=recommendations,
    )
