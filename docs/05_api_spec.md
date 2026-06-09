# 05. API Specification

Backend FastAPI chạy mặc định tại:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Bảng endpoint

| Method | Endpoint | Mục đích | Body |
|---|---|---|---|
| `GET` | `/health` | Kiểm tra backend sống | Không |
| `GET` | `/model-info` | Lấy thông tin model và file log | Không |
| `POST` | `/telemetry` | Gửi telemetry từ điện thoại | Telemetry JSON |
| `GET` | `/latest` | Lấy telemetry mới nhất | Không |
| `GET` | `/history` | Lấy lịch sử telemetry | Query `limit`, `device_id` |
| `POST` | `/detect-anomaly` | Chạy anomaly detection | Telemetry JSON |
| `POST` | `/forecast` | Dự báo pin | `device_id` hoặc telemetry hiện tại |
| `POST` | `/predict-risk` | Sinh khuyến nghị rủi ro | Telemetry JSON |
| `GET` | `/events` | Lấy anomaly event feed | Query `limit`, `device_id` |

## POST /telemetry

Request:

```json
{
  "device_id": "redmi-note-12-turbo",
  "timestamp": "2026-06-09T09:00:00Z",
  "battery_level": 72.0,
  "charging": false,
  "acc_x": 0.1,
  "acc_y": 0.2,
  "acc_z": 9.8,
  "light_lux": 120.0,
  "network_type": "online"
}
```

Response:

```json
{
  "device_id": "redmi-note-12-turbo",
  "timestamp": "2026-06-09T09:00:00Z",
  "battery_level": 72.0,
  "charging": false,
  "acc_x": 0.1,
  "acc_y": 0.2,
  "acc_z": 9.8,
  "light_lux": 120.0,
  "network_type": "online",
  "received_at": "2026-06-09T09:00:01Z"
}
```

## POST /forecast

Request:

```json
{
  "device_id": "redmi-note-12-turbo"
}
```

Hoặc:

```json
{
  "device_id": "redmi-note-12-turbo",
  "telemetry": {
    "device_id": "redmi-note-12-turbo",
    "timestamp": "2026-06-09T09:15:00Z",
    "battery_level": 74.0,
    "charging": false,
    "acc_x": 0.1,
    "acc_y": 0.2,
    "acc_z": 9.8,
    "light_lux": 120.0,
    "network_type": "online"
  }
}
```

## GET /history

Ví dụ:

```text
GET /history?limit=100&device_id=redmi-note-12-turbo
```

## GET /events

Ví dụ:

```text
GET /events?limit=50&device_id=redmi-note-12-turbo
```
