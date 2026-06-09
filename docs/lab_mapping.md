# Mapping PhoneGuard AIoT Với Lab 1 Đến Lab 5

## Lab 1: IoT Device & Telemetry

- Android phone đóng vai trò IoT device.
- `phone-web/index.html` và `phone-web/app.js` đọc Battery API, DeviceMotion, DeviceLight và Network Information API.
- Client gửi telemetry mỗi 3 giây tới `POST /telemetry`.

## Lab 2: Backend API & Data Ingestion

- FastAPI backend nằm trong `backend/app/main.py`.
- Schema telemetry nằm trong `backend/app/schemas.py`.
- Endpoint chính: `GET /health`, `POST /telemetry`, `GET /latest`.

## Lab 3: Storage & Event Logging

- Lưu telemetry bằng CSV tại `backend/data/telemetry.csv`.
- Lưu anomaly event tại `backend/data/anomaly_event_log.csv`.
- Logic đọc/ghi tập trung trong `backend/app/storage.py`.

## Lab 4: AI Rule-Based Baseline

- Phát hiện dị thường: `backend/app/anomaly.py` và endpoint `POST /detect-anomaly`.
- Dự báo pin: `backend/app/forecasting.py` và endpoint `POST /forecast`.
- Dự đoán rủi ro/khuyến nghị: `backend/app/risk.py` và endpoint `POST /predict-risk`.
- Thông tin mô hình: `GET /model-info`.

## Lab 5: Dashboard & Deployment

- Dashboard Streamlit: `dashboard/streamlit_app.py`.
- Docker backend: `backend/Dockerfile`.
- Docker Compose chạy backend và dashboard: `docker-compose.yml`.
