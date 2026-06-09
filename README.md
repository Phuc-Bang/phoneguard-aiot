# PhoneGuard AIoT

PhoneGuard AIoT dùng điện thoại Android như một IoT device. Điện thoại gửi telemetry về FastAPI backend, backend lưu CSV, phát hiện dị thường rule-based, dự báo pin cơ bản và hiển thị dữ liệu bằng Streamlit.

## Cấu trúc thư mục

```text
phoneguard-aiot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── storage.py
│   │   ├── anomaly.py
│   │   ├── forecasting.py
│   │   └── risk.py
│   ├── data/
│   ├── Dockerfile
│   └── requirements.txt
├── phone-web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── dashboard/
│   └── streamlit_app.py
├── docs/
│   └── lab_mapping.md
└── docker-compose.yml
```

## Chạy backend local

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Kiểm tra:

```bash
curl http://localhost:8000/health
```

## Test API

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"android-phone-001\",\"timestamp\":\"2026-06-09T09:00:00Z\",\"battery_level\":72,\"charging\":false,\"acc_x\":0.1,\"acc_y\":0.2,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"wifi\"}"
```

Các endpoint chính:

- `GET /health`
- `POST /telemetry`
- `GET /latest`
- `POST /detect-anomaly`
- `POST /forecast`
- `POST /predict-risk`
- `GET /events`
- `GET /model-info`

## Chạy phone-web trên điện thoại

1. Chạy backend trên máy tính trong cùng mạng Wi-Fi.
2. Lấy IP máy tính, ví dụ `192.168.1.10`.
3. Mở `phone-web/index.html` bằng trình duyệt Android.
4. Đặt Backend URL là `http://192.168.1.10:8000`.
5. Bấm `Start`. Telemetry sẽ gửi mỗi 3 giây.

Lưu ý: một số trình duyệt Android giới hạn Battery API, DeviceLight hoặc DeviceMotion. Khi API không có, phone-web dùng giá trị fallback để demo vẫn chạy.

## Chạy dashboard Streamlit

```bash
cd phoneguard-aiot
python -m pip install -r backend/requirements.txt
streamlit run dashboard/streamlit_app.py
```

Mở:

```text
http://localhost:8501
```

## Chạy Docker

```bash
docker compose up --build
```

Backend:

```text
http://localhost:8000
```

Dashboard:

```text
http://localhost:8501
```

## File dữ liệu

- Telemetry: `backend/data/telemetry.csv`
- Anomaly event: `backend/data/anomaly_event_log.csv`

## Mapping Lab

Xem chi tiết tại `docs/lab_mapping.md`.
