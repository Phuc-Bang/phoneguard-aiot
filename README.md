# PhoneGuard AIoT: Hệ thống Giám sát Sức khỏe & Trạng thái Hoạt động Điện thoại thông minh

Dự án giám sát trạng thái hoạt động (Pin, Nhiệt độ, Gia tốc, Mạng) của điện thoại Android Redmi Note 12 Turbo đóng vai trò thiết bị IoT thực tế, kết hợp với các thuật toán Trí tuệ nhân tạo (AI/ML) để phát hiện dị thường, dự báo nguy cơ hao pin và đề xuất khuyến nghị vận hành thời gian thực.

## 🌟 Tính Năng Chính
1. **Thu thập Telemetry thời gian thực**: Nhận dữ liệu mức pin, nhiệt độ pin, điện áp, trạng thái sạc, tín hiệu Wi-Fi, và gia tốc 3 trục từ điện thoại thông minh.
2. **AI Anomaly Detection**: Phát hiện các trạng thái dị thường như:
   - Rơi tự do (Free Fall) hoặc va đập mạnh dựa trên đột biến cảm biến gia tốc.
   - Quá nhiệt pin (>45°C) gây nguy cơ cháy nổ.
   - Hao hụt pin bất thường (Anomaly Drain Rate) sử dụng mô hình Isolation Forest.
3. **AI Battery Forecasting**: Dự báo thời gian ước tính pin sẽ cạn (Time-to-Empty) hoặc sạc đầy (Time-to-Full) dựa trên phân tích hồi quy chuỗi thời gian ngắn hạn.
4. **Hệ thống Khuyến nghị thông minh (Smart Recommendations)**: Đưa ra cảnh báo vận hành để kéo dài tuổi thọ pin và bảo vệ thiết bị.
5. **Dashboard Glassmorphism cao cấp**: Giao diện tối (Dark mode) sang trọng, hiển thị biểu đồ pin, chuyển động gia tốc thời gian thực thông qua kết nối **WebSocket**.
6. **Đóng gói Docker Compose**: Khởi chạy dễ dàng toàn bộ hệ thống với một câu lệnh duy nhất.

---

## 📁 Cấu Trúc Dự Án
```text
phoneguard-aiot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI App, WebSockets, Routers
│   │   ├── database.py         # Cấu hình SQLite & SQLAlchemy Engine
│   │   ├── models.py           # Định nghĩa các bảng Database
│   │   ├── schemas.py          # Pydantic Schemas để validate dữ liệu
│   │   ├── crud.py             # Thao tác đọc/ghi Cơ sở dữ liệu
│   │   └── ai/                 # Các Module xử lý AI/ML
│   │       ├── __init__.py
│   │       ├── anomaly_detector.py # Phát hiện dị thường (Rules + Isolation Forest)
│   │       ├── battery_predictor.py # Hồi quy dự đoán thời lượng pin
│   │       └── recommender.py       # Hệ thống sinh khuyến nghị tối ưu
│   ├── requirements.txt        # Các thư viện Python cần thiết
│   └── Dockerfile              # Dockerfile build backend
├── frontend/
│   ├── index.html              # Trang giao diện chính
│   ├── css/
│   │   └── style.css           # CSS Glassmorphism cao cấp, responsive
│   └── js/
│       └── app.js              # Xử lý Websocket & Chart.js vẽ biểu đồ động
├── scripts/
│   ├── phone_simulator.py      # Script giả lập dữ liệu điện thoại gửi về backend
│   └── train_models.py         # Script huấn luyện / khởi tạo trọng số model ML ban đầu
├── docker-compose.yml          # Docker Compose kết nối dịch vụ
└── README.md                   # Tài liệu hướng dẫn sử dụng (File này)
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử Nghiệm

### Cách 1: Chạy bằng Docker Compose (Khuyên dùng)
Yêu cầu máy tính đã cài đặt **Docker** và **Docker Desktop** (trên Windows).
1. Di chuyển vào thư mục dự án:
   ```bash
   cd e:/AIoT/Home-Work/phoneguard-aiot
   ```
2. Khởi chạy toàn bộ hệ thống:
   ```bash
   docker compose up --build -d
   ```
3. Truy cập Dashboard giám sát tại địa chỉ: `http://localhost:8000`

---

### Cách 2: Chạy trực tiếp trên máy local (Python)
1. **Thiết lập Backend**:
   ```bash
   cd backend
   python -m venv .venv
   # Kích hoạt venv (Windows):
   .venv\Scripts\activate
   # Cài đặt thư viện:
   pip install -r requirements.txt
   ```
2. **Khởi tạo và huấn luyện model ban đầu**:
   ```bash
   # Chạy từ thư mục gốc phoneguard-aiot
   python -m scripts.train_models
   ```
3. **Chạy server FastAPI**:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *Truy cập Swagger API docs: `http://localhost:8000/docs`*

---

## 📱 Hướng Dẫn Kết Nối Điện Thoại Redmi Note 12 Turbo (Thực tế)
1. Cài đặt ứng dụng **Sensor Logger** (hoặc bất kỳ ứng dụng Logger HTTP POST nào) từ Google Play Store.
2. Mở ứng dụng, vào phần **Settings** -> **HTTP Settings** hoặc **Push Link**:
   - **URL/Endpoint**: Nhập địa chỉ IP của máy tính chạy server backend, dạng: `http://<IP_MÁY_TÍNH>:8000/api/v1/telemetry/sensor-logger` (Nếu dùng Sensor Logger) hoặc `http://<IP_MÁY_TÍNH>:8000/api/v1/telemetry`.
   - **Update Interval / Frequency**: Đặt tần suất gửi dữ liệu (khuyên dùng: 1Hz - 1 giây một lần hoặc 0.2Hz - 5 giây một lần để tiết kiệm pin và băng thông).
3. Chọn các cảm biến cần gửi: **Battery**, **Accelerometer**, **Network State**.
4. Nhấn **Start** / **Stream** để bắt đầu đẩy dữ liệu cảm biến thực tế về hệ thống và xem Dashboard nhảy số trực quan!
