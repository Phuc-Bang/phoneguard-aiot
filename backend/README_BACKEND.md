# PhoneGuard AIoT Backend

Backend FastAPI nhận telemetry từ điện thoại Android, lưu log CSV trong `outputs/`, chạy anomaly detection, forecasting và risk recommendation baseline.

## Cấu trúc

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ schemas.py
│  ├─ storage.py
│  ├─ anomaly.py
│  ├─ forecasting.py
│  └─ risk.py
├─ requirements.txt
└─ README_BACKEND.md
```

## Cài đặt

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Chạy Uvicorn

Chạy từ thư mục `backend/`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Mở API docs:

```text
http://localhost:8000/docs
```

Healthcheck:

```text
http://localhost:8000/health
```

## Endpoint

- `GET /health`
- `GET /model-info`
- `POST /telemetry`
- `GET /latest`
- `GET /history`
- `POST /detect-anomaly`
- `POST /forecast`
- `POST /predict-risk`
- `GET /events`

## Telemetry payload

```json
{
  "device_id": "android-phone-001",
  "timestamp": "2026-06-09T09:00:00Z",
  "battery_level": 72.0,
  "charging": false,
  "acc_x": 0.1,
  "acc_y": 0.2,
  "acc_z": 9.8,
  "light_lux": 120.0,
  "network_type": "wifi"
}
```

Các trường `acc_x`, `acc_y`, `acc_z`, `light_lux`, `network_type` có thể là `null`.

## File log

Backend tự tạo thư mục `outputs/` ở root project:

- `outputs/phone_telemetry.csv`
- `outputs/anomaly_event_log.csv`
- `outputs/forecast_log.csv`

Có thể đổi thư mục output bằng biến môi trường:

```bash
set PHONEGUARD_OUTPUT_DIR=E:\AIoT\Home-Work\phoneguard-aiot\outputs
```

## Test nhanh

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"android-phone-001\",\"timestamp\":\"2026-06-09T09:00:00Z\",\"battery_level\":72,\"charging\":false,\"acc_x\":0.1,\"acc_y\":0.2,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"wifi\"}"
```
