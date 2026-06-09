# 03. Telemetry Schema

## Payload telemetry

Telemetry là dữ liệu trạng thái điện thoại gửi từ `phone-web` về backend qua `POST /telemetry`.

| Trường | Kiểu dữ liệu | Bắt buộc | Mô tả | Ví dụ |
|---|---|---:|---|---|
| `device_id` | `string` | Có | Định danh thiết bị gửi dữ liệu | `redmi-note-12-turbo` |
| `timestamp` | `string` | Có | Thời điểm đo, ISO 8601 | `2026-06-09T09:00:00Z` |
| `battery_level` | `float` | Có | Mức pin phần trăm, từ 0 đến 100 | `72.0` |
| `charging` | `boolean` | Có | Thiết bị có đang sạc hay không | `false` |
| `acc_x` | `float \| null` | Không | Gia tốc trục X | `0.1` |
| `acc_y` | `float \| null` | Không | Gia tốc trục Y | `0.2` |
| `acc_z` | `float \| null` | Không | Gia tốc trục Z | `9.8` |
| `light_lux` | `float \| null` | Không | Cường độ ánh sáng môi trường | `120.0` |
| `network_type` | `string \| null` | Không | Trạng thái mạng từ `navigator.onLine` | `online` |

## JSON mẫu normal

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

## JSON mẫu anomaly

Ví dụ điện thoại có thể vừa pin thấp vừa có gia tốc lớn:

```json
{
  "device_id": "redmi-note-12-turbo",
  "timestamp": "2026-06-09T09:03:00Z",
  "battery_level": 8.0,
  "charging": false,
  "acc_x": 22.0,
  "acc_y": 1.0,
  "acc_z": 3.0,
  "light_lux": 85.0,
  "network_type": "online"
}
```

## Lưu trữ CSV

Telemetry được lưu tại:

```text
outputs/phone_telemetry.csv
```

Các anomaly event được lưu tại:

```text
outputs/anomaly_event_log.csv
```

Các forecast result được lưu tại:

```text
outputs/forecast_log.csv
```
