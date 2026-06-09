"""Phát hiện anomaly rule-based cho PhoneGuard AIoT."""

import math
from dataclasses import dataclass

from .schemas import AnomalyResult, TelemetryIn, parse_iso_datetime
from .storage import append_anomaly_event, read_telemetry


MODEL_VERSION = "rule_iforest_v1"
SAFETY_NOTE = "AI chỉ cảnh báo, không tự động điều khiển thiết bị."
SEVERITY_WEIGHT = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


@dataclass
class CandidateEvent:
    """Ứng viên anomaly nội bộ để so sánh mức độ nghiêm trọng."""

    event_type: str
    severity: str
    score: float
    explanation: str
    recommendation: str


def acc_magnitude(acc_x: float | None, acc_y: float | None, acc_z: float | None) -> float | None:
    """Tính độ lớn vector gia tốc, trả None nếu thiếu một trục cảm biến."""
    if acc_x is None or acc_y is None or acc_z is None:
        return None
    return math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)


def build_event(event_type: str, severity: str, decision: str, explanation: str, recommendation: str) -> dict:
    """Tạo event output chuẩn để trả API và ghi anomaly_event_log.csv."""
    return {
        "event_type": event_type,
        "severity": severity,
        "decision": decision,
        "explanation": explanation,
        "recommendation": recommendation,
        "safety_note": SAFETY_NOTE,
    }


def detect_anomaly(telemetry: TelemetryIn, persist_event: bool = True) -> AnomalyResult:
    """Chạy toàn bộ rule anomaly và ghi event khi phát hiện bất thường."""
    candidates = [
        _check_low_battery(telemetry),
        _check_battery_drain_fast(telemetry),
        _check_possible_drop(telemetry),
        _check_sensor_stuck(telemetry),
        _check_network_lost(telemetry),
    ]
    active_candidates = [candidate for candidate in candidates if candidate is not None]

    if active_candidates:
        selected = max(active_candidates, key=lambda item: SEVERITY_WEIGHT[item.severity])
        anomaly_score = round(min(sum(item.score for item in active_candidates), 1.0), 3)
        result = {
            "model_output": {
                "is_anomaly": True,
                "anomaly_score": anomaly_score,
                "model_version": MODEL_VERSION,
            },
            "event": build_event(
                event_type=selected.event_type,
                severity=selected.severity,
                decision="ALERT",
                explanation=selected.explanation,
                recommendation=selected.recommendation,
            ),
        }
        if persist_event:
            append_anomaly_event(telemetry.device_id, telemetry.timestamp, result)
    else:
        result = {
            "model_output": {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "model_version": MODEL_VERSION,
            },
            "event": build_event(
                event_type="NORMAL",
                severity="NORMAL",
                decision="PASS",
                explanation="Không phát hiện anomaly trong telemetry hiện tại.",
                recommendation="Tiếp tục giám sát thiết bị theo chu kỳ.",
            ),
        }

    print(
        "[DEBUG] Anomaly "
        f"device={telemetry.device_id} "
        f"type={result['event']['event_type']} "
        f"score={result['model_output']['anomaly_score']}"
    )
    return AnomalyResult(**result)


def _check_low_battery(telemetry: TelemetryIn) -> CandidateEvent | None:
    """LOW_BATTERY: pin dưới 15% và không sạc."""
    if telemetry.battery_level < 15 and not telemetry.charging:
        return CandidateEvent(
            event_type="LOW_BATTERY",
            severity="HIGH",
            score=0.75,
            explanation=f"battery_level={telemetry.battery_level}% thấp hơn 15% và thiết bị không sạc.",
            recommendation="Cắm sạc hoặc giảm tần suất gửi telemetry để tránh thiết bị tắt nguồn.",
        )
    return None


def _check_battery_drain_fast(telemetry: TelemetryIn) -> CandidateEvent | None:
    """BATTERY_DRAIN_FAST: pin giảm từ 5% trở lên trong vòng 10 phút."""
    previous = _find_previous_telemetry(telemetry)
    if previous is None:
        return None

    current_time = parse_iso_datetime(telemetry.timestamp)
    previous_time = parse_iso_datetime(previous["timestamp"])
    elapsed_minutes = (current_time - previous_time).total_seconds() / 60
    drop_percent = previous["battery_level"] - telemetry.battery_level

    if 0 <= elapsed_minutes <= 10 and drop_percent >= 5:
        severity = "HIGH" if drop_percent >= 10 else "MEDIUM"
        return CandidateEvent(
            event_type="BATTERY_DRAIN_FAST",
            severity=severity,
            score=0.85 if severity == "HIGH" else 0.55,
            explanation=(
                f"Pin giảm {drop_percent:.1f}% trong {elapsed_minutes:.1f} phút "
                f"(từ {previous['battery_level']}% xuống {telemetry.battery_level}%)."
            ),
            recommendation="Kiểm tra ứng dụng nền, nhiệt độ máy và chất lượng kết nối mạng.",
        )
    return None


def _check_possible_drop(telemetry: TelemetryIn) -> CandidateEvent | None:
    """POSSIBLE_DROP: độ lớn gia tốc vượt ngưỡng va đập/rơi."""
    magnitude = acc_magnitude(telemetry.acc_x, telemetry.acc_y, telemetry.acc_z)
    if magnitude is not None and magnitude > 18:
        return CandidateEvent(
            event_type="POSSIBLE_DROP",
            severity="CRITICAL",
            score=1.0,
            explanation=f"acc_magnitude={magnitude:.2f} vượt ngưỡng 18, có thể có va đập hoặc rơi.",
            recommendation="Kiểm tra tình trạng vật lý của điện thoại và xác nhận thiết bị vẫn hoạt động bình thường.",
        )
    return None


def _check_sensor_stuck(telemetry: TelemetryIn) -> CandidateEvent | None:
    """SENSOR_STUCK: gia tốc gần như không đổi trong nhiều bản tin gần nhất."""
    if telemetry.acc_x is None or telemetry.acc_y is None or telemetry.acc_z is None:
        return None

    rows = read_telemetry(limit=6, device_id=telemetry.device_id)
    recent = [
        row
        for row in rows
        if row["acc_x"] is not None and row["acc_y"] is not None and row["acc_z"] is not None
    ]
    recent.append(
        {
            "acc_x": telemetry.acc_x,
            "acc_y": telemetry.acc_y,
            "acc_z": telemetry.acc_z,
        }
    )

    if len(recent) < 5:
        return None

    x_values = [row["acc_x"] for row in recent[-5:]]
    y_values = [row["acc_y"] for row in recent[-5:]]
    z_values = [row["acc_z"] for row in recent[-5:]]
    max_delta = max(
        max(x_values) - min(x_values),
        max(y_values) - min(y_values),
        max(z_values) - min(z_values),
    )

    if max_delta <= 0.03:
        return CandidateEvent(
            event_type="SENSOR_STUCK",
            severity="MEDIUM",
            score=0.5,
            explanation=f"acc_x, acc_y, acc_z gần như không đổi trong 5 bản tin gần nhất (max_delta={max_delta:.3f}).",
            recommendation="Kiểm tra quyền cảm biến, trình duyệt và thử xoay/di chuyển điện thoại để xác nhận cảm biến còn phản hồi.",
        )
    return None


def _check_network_lost(telemetry: TelemetryIn) -> CandidateEvent | None:
    """NETWORK_LOST: phone-web báo trạng thái offline."""
    network_type = (telemetry.network_type or "").lower()
    if network_type == "offline":
        severity = "MEDIUM" if not telemetry.charging and telemetry.battery_level < 30 else "LOW"
        return CandidateEvent(
            event_type="NETWORK_LOST",
            severity=severity,
            score=0.4 if severity == "MEDIUM" else 0.25,
            explanation="network_type=offline, điện thoại có thể mất kết nối với backend hoặc mạng Wi-Fi.",
            recommendation="Kiểm tra Wi-Fi/mobile data và đảm bảo backend URL cùng mạng với điện thoại.",
        )
    return None


def _find_previous_telemetry(telemetry: TelemetryIn) -> dict | None:
    """Tìm bản tin trước telemetry hiện tại để so sánh tốc độ tụt pin."""
    rows = read_telemetry(device_id=telemetry.device_id)
    current_time = parse_iso_datetime(telemetry.timestamp)
    previous_rows = [row for row in rows if parse_iso_datetime(row["timestamp"]) < current_time]
    if not previous_rows:
        return None
    return previous_rows[-1]
