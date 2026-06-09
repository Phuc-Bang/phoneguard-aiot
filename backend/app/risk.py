"""Tổng hợp risk recommendation từ telemetry, anomaly và forecast."""

from .schemas import AnomalyResult, ForecastResult, RiskResult, TelemetryIn


MODEL_VERSION = "risk_recommendation_v1"
SAFETY_NOTE = "PhoneGuard AIoT chỉ khuyến nghị, không tự điều khiển thiết bị."
RISK_WEIGHT = {"NORMAL": 0, "WARNING": 1, "HIGH": 2, "CRITICAL": 3}


def predict_risk(telemetry: TelemetryIn, anomaly: AnomalyResult, forecast: ForecastResult) -> RiskResult:
    """Kết hợp telemetry hiện tại, anomaly result và forecast result để tạo khuyến nghị."""
    recommendations: list[str] = []
    reasons: list[str] = []

    anomaly_severity = anomaly.event.severity.upper()
    forecast_risk = forecast.decision.risk_level.upper()
    overall_risk = "NORMAL"

    if anomaly_severity == "CRITICAL":
        overall_risk = "CRITICAL"
        reasons.append(f"Anomaly severity CRITICAL: {anomaly.event.event_type}.")
    else:
        overall_risk = _max_risk(overall_risk, _map_anomaly_severity_to_risk(anomaly_severity))
        if anomaly.model_output.is_anomaly:
            reasons.append(f"Anomaly {anomaly.event.event_type} severity={anomaly_severity}.")

    if forecast_risk == "CRITICAL":
        overall_risk = _max_risk(overall_risk, "CRITICAL")
        reasons.append("Forecast dự báo pin 30 phút ở mức CRITICAL.")
    elif forecast_risk == "HIGH":
        overall_risk = _max_risk(overall_risk, "HIGH")
        reasons.append("Forecast risk HIGH nên overall_risk ít nhất HIGH.")
    else:
        overall_risk = _max_risk(overall_risk, forecast_risk)
        if forecast_risk != "NORMAL":
            reasons.append(f"Forecast risk={forecast_risk}.")

    if telemetry.battery_level < 20 and not telemetry.charging:
        overall_risk = _max_risk(overall_risk, "WARNING")
        recommendations.append("Cắm sạc hoặc giảm tần suất gửi telemetry vì pin đang thấp và thiết bị không sạc.")
        reasons.append(f"battery_level={telemetry.battery_level}% và charging=false.")

    if anomaly.event.event_type == "POSSIBLE_DROP":
        recommendations.append("Kiểm tra tình trạng vật lý của điện thoại sau va đập/rơi.")

    if anomaly.event.event_type == "NETWORK_LOST" or (telemetry.network_type or "").lower() == "offline":
        recommendations.append("Kiểm tra kết nối Wi-Fi/mobile data và xác nhận Backend URL còn truy cập được.")

    if forecast.decision.risk_level.upper() in {"WARNING", "HIGH", "CRITICAL"}:
        recommendations.append(forecast.decision.recommendation)

    if anomaly.model_output.is_anomaly and anomaly.event.recommendation not in recommendations:
        recommendations.append(anomaly.event.recommendation)

    if not recommendations:
        recommendations.append("Thiết bị ổn định, tiếp tục giám sát và gửi telemetry theo chu kỳ.")

    main_reason = " ".join(reasons) if reasons else "Telemetry, anomaly và forecast chưa cho thấy rủi ro đáng kể."
    risk_score = _risk_score(overall_risk, anomaly.model_output.anomaly_score, forecast.model_output.confidence)

    print(
        "[DEBUG] Risk "
        f"device={telemetry.device_id} overall={overall_risk} "
        f"score={risk_score:.2f} anomaly={anomaly.event.event_type} forecast={forecast_risk}"
    )
    return RiskResult(
        device_id=telemetry.device_id,
        overall_risk=overall_risk,
        risk_score=risk_score,
        main_reason=main_reason,
        recommendations=_dedupe(recommendations),
        control_allowed=False,
        safety_note=SAFETY_NOTE,
        model_version=MODEL_VERSION,
    )


def _map_anomaly_severity_to_risk(severity: str) -> str:
    """Ánh xạ severity anomaly sang thang risk tổng hợp."""
    if severity in {"CRITICAL", "HIGH"}:
        return severity
    if severity == "MEDIUM":
        return "WARNING"
    return "NORMAL"


def _max_risk(left: str, right: str) -> str:
    """Trả về risk cao hơn theo thứ tự NORMAL < WARNING < HIGH < CRITICAL."""
    return left if RISK_WEIGHT[left] >= RISK_WEIGHT[right] else right


def _risk_score(overall_risk: str, anomaly_score: float, forecast_confidence: float) -> float:
    """Tính điểm risk đơn giản, dễ giải thích và mở rộng."""
    base = {
        "NORMAL": 0.1,
        "WARNING": 0.4,
        "HIGH": 0.7,
        "CRITICAL": 0.95,
    }[overall_risk]
    adjusted = base + min(anomaly_score, 1.0) * 0.04 + min(forecast_confidence, 1.0) * 0.01
    return round(min(adjusted, 1.0), 3)


def _dedupe(items: list[str]) -> list[str]:
    """Loại khuyến nghị trùng lặp nhưng giữ nguyên thứ tự."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
