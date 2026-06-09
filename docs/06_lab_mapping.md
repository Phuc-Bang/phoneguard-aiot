# 06. Mapping Lab 1 Đến Lab 5

| Lab | Nội dung lab | Mapping trong PhoneGuard AIoT | File/Module |
|---:|---|---|---|
| Lab 1 | IoT device và telemetry | Điện thoại Android đóng vai trò IoT device, gửi dữ liệu cảm biến mỗi 3 giây | `phone-web/index.html`, `phone-web/app.js` |
| Lab 2 | API ingestion | FastAPI nhận `POST /telemetry`, validate schema và trả response | `backend/app/main.py`, `backend/app/schemas.py` |
| Lab 3 | Storage và logging | Lưu telemetry, anomaly event và forecast log vào CSV | `backend/app/storage.py`, `outputs/*.csv` |
| Lab 4 | AI inference baseline | Rule-based anomaly, linear forecast, risk recommendation | `backend/app/anomaly.py`, `forecasting.py`, `risk.py` |
| Lab 5 | Dockerized multi-service system | Docker Compose chạy backend và frontend, mount volume logs | `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml` |

## Lab 1: Phone Sensor Client

Điện thoại Android dùng browser để chạy `phone-web`. Client đọc:

- Battery API nếu trình duyệt hỗ trợ.
- DeviceMotionEvent nếu cảm biến được cấp quyền.
- `navigator.onLine` để biết trạng thái mạng.

## Lab 2: FastAPI Backend

Backend có các endpoint:

- `/health`
- `/telemetry`
- `/latest`
- `/history`
- `/detect-anomaly`
- `/forecast`
- `/predict-risk`
- `/events`
- `/model-info`

## Lab 3: CSV Storage

Không dùng database phức tạp ở phiên bản đầu. Dữ liệu được ghi vào:

- `outputs/phone_telemetry.csv`
- `outputs/anomaly_event_log.csv`
- `outputs/forecast_log.csv`

## Lab 4: AI Modules

Các module AI hiện tại là baseline:

- Anomaly: rule-based.
- Forecast: linear trend.
- Risk: tổng hợp rule từ anomaly và forecast.

## Lab 5: Docker Deployment

Compose chạy 2 service:

- `backend`: FastAPI ở `http://localhost:8000`
- `frontend`: Dashboard ở `http://localhost:3000`

Volume `./outputs:/app/outputs` giúp giữ logs sau khi container bị xóa.
