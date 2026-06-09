# 04. AI Modules

PhoneGuard AIoT dùng các module AI baseline đơn giản, dễ giải thích và phù hợp cho Lab.

## 1. Anomaly Detection

File chính:

```text
backend/app/anomaly.py
```

Các rule hiện tại:

| Event type | Điều kiện | Severity |
|---|---|---|
| `LOW_BATTERY` | `battery_level < 15` và `charging = false` | `HIGH` |
| `BATTERY_DRAIN_FAST` | Pin giảm ít nhất 5% trong vòng 10 phút | `MEDIUM` hoặc `HIGH` |
| `POSSIBLE_DROP` | `sqrt(acc_x^2 + acc_y^2 + acc_z^2) > 18` | `CRITICAL` |
| `SENSOR_STUCK` | Gia tốc gần như không đổi trong nhiều bản tin gần nhất | `MEDIUM` |
| `NETWORK_LOST` | `network_type = offline` | `LOW` hoặc `MEDIUM` |

Output anomaly:

```json
{
  "model_output": {
    "is_anomaly": true,
    "anomaly_score": 1.0,
    "model_version": "rule_iforest_v1"
  },
  "event": {
    "event_type": "POSSIBLE_DROP",
    "severity": "CRITICAL",
    "decision": "ALERT",
    "explanation": "acc_magnitude vượt ngưỡng 18, có thể có va đập hoặc rơi.",
    "recommendation": "Kiểm tra tình trạng vật lý của điện thoại và xác nhận thiết bị vẫn hoạt động bình thường.",
    "safety_note": "AI chỉ cảnh báo, không tự động điều khiển thiết bị."
  }
}
```

## 2. Forecasting

File chính:

```text
backend/app/forecasting.py
```

Mục tiêu:

- Dự báo `battery_level` sau 15 phút.
- Dự báo `battery_level` sau 30 phút.
- Dùng baseline linear trend từ lịch sử CSV gần nhất.
- Clamp kết quả trong khoảng 0 đến 100.

JSON mẫu forecast response:

```json
{
  "model_output": {
    "target": "battery_level",
    "predicted_battery_15min": 68.0,
    "predicted_battery_30min": 62.0,
    "model_version": "battery_linear_trend_v1",
    "confidence": 0.75
  },
  "decision": {
    "risk_level": "NORMAL",
    "recommendation": "Pin dự kiến vẫn đủ cho chu kỳ giám sát ngắn hạn.",
    "reason": "Linear trend=-0.4000%/phút từ 4 mẫu gần nhất.",
    "safety_note": "Forecast chỉ là tín hiệu khuyến nghị, không phải lệnh điều khiển."
  }
}
```

Risk rule forecast:

| Điều kiện | Risk |
|---|---|
| `predicted_battery_30min < 5` | `CRITICAL` |
| `predicted_battery_30min < 10` | `HIGH` |
| `predicted_battery_30min < 20` | `WARNING` |
| Còn lại | `NORMAL` |

## 3. Risk Recommendation

File chính:

```text
backend/app/risk.py
```

Module risk kết hợp:

- Telemetry hiện tại.
- Anomaly result.
- Forecast result.

Output:

```json
{
  "device_id": "redmi-note-12-turbo",
  "overall_risk": "HIGH",
  "risk_score": 0.74,
  "main_reason": "Forecast risk HIGH nên overall_risk ít nhất HIGH.",
  "recommendations": [
    "Chuẩn bị sạc hoặc giảm tần suất gửi telemetry.",
    "Theo dõi pin sát hơn trong 30 phút tới."
  ],
  "control_allowed": false,
  "safety_note": "PhoneGuard AIoT chỉ khuyến nghị, không tự điều khiển thiết bị.",
  "model_version": "risk_recommendation_v1"
}
```

## Vì sao dùng baseline trước?

Phiên bản đầu ưu tiên:

- Dễ chạy.
- Dễ debug.
- Dễ giải thích trước giảng viên.
- Không phụ thuộc database hoặc model training phức tạp.
- Phù hợp tinh thần xây dựng pipeline AIoT trước, tối ưu sau.
