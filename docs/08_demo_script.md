# 08. Kịch Bản Demo Trước Giảng Viên

## Chuẩn bị

Thiết bị:

- Laptop chạy Docker Desktop.
- Redmi Note 12 Turbo.
- Cả hai cùng mạng Wi-Fi.

Phần mềm:

- Docker Desktop.
- VS Code Live Server hoặc static server cho `phone-web`.
- Browser trên laptop và Redmi.

## Bước 1: Giới thiệu bài toán

Nói ngắn gọn:

> PhoneGuard AIoT dùng điện thoại Android như một thiết bị IoT. Điện thoại gửi telemetry về FastAPI backend, backend lưu CSV, chạy anomaly detection, forecast pin và risk recommendation. Dashboard React hiển thị dữ liệu theo thời gian gần thực.

## Bước 2: Chạy hệ thống Docker

Tại thư mục `phoneguard-aiot`:

```bash
docker compose up --build
```

Mở kiểm tra:

```text
http://localhost:8000/health
http://localhost:8000/docs
http://localhost:3000
```

Kỳ vọng:

- Health trả `status: ok`.
- Swagger docs mở được.
- Dashboard mở được.

## Bước 3: Mở phone-web trên Redmi

Lấy IP LAN của laptop, ví dụ:

```text
192.168.1.5
```

Mở phone-web bằng Live Server:

```text
http://192.168.1.5:5500/phone-web/index.html
```

Trong ô Backend URL nhập:

```text
http://192.168.1.5:8000
```

Bấm:

```text
Start Sending
```

Giải thích:

- Phone-web gửi `POST /telemetry` mỗi 3 giây.
- Nếu Battery API hoặc DeviceMotion không hỗ trợ, client dùng fallback và hiển thị cảnh báo.

## Bước 4: Xem telemetry trên dashboard

Trên laptop mở:

```text
http://localhost:3000
```

Đi qua các trang:

1. Overview: xem Battery, Charging, Network, Device status, Last update, Overall risk.
2. Telemetry: xem Battery line chart và Acceleration magnitude chart.
3. Anomalies: xem anomaly event feed.
4. Forecast: xem predicted battery 15 phút và 30 phút.
5. Settings: cho thấy có thể đổi API base URL.

## Bước 5: Tạo anomaly demo

Cách demo an toàn:

- Giảm mô phỏng bằng curl thay vì làm rơi điện thoại thật.
- Gửi telemetry có `acc_x` lớn để kích hoạt `POSSIBLE_DROP`.

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"redmi-note-12-turbo\",\"timestamp\":\"2026-06-09T09:10:00Z\",\"battery_level\":70,\"charging\":false,\"acc_x\":22,\"acc_y\":1,\"acc_z\":3,\"light_lux\":120,\"network_type\":\"online\"}"
```

Kỳ vọng:

- Backend ghi anomaly event.
- Dashboard Anomalies hiển thị `POSSIBLE_DROP`.
- Risk recommendation khuyến nghị kiểm tra thiết bị.

## Bước 6: Demo forecast

Gửi một vài mẫu pin giảm dần:

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"redmi-note-12-turbo\",\"timestamp\":\"2026-06-09T09:00:00Z\",\"battery_level\":80,\"charging\":false,\"acc_x\":0,\"acc_y\":0,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"online\"}"
```

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"redmi-note-12-turbo\",\"timestamp\":\"2026-06-09T09:05:00Z\",\"battery_level\":76,\"charging\":false,\"acc_x\":0,\"acc_y\":0,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"online\"}"
```

Sau đó gọi:

```bash
curl -X POST http://localhost:8000/forecast ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"redmi-note-12-turbo\"}"
```

Kỳ vọng:

- Response có `predicted_battery_15min`.
- Response có `predicted_battery_30min`.
- `outputs/forecast_log.csv` được cập nhật.

## Bước 7: Chỉ ra file log

Mở thư mục:

```text
outputs/
```

Giải thích 3 file:

- `phone_telemetry.csv`: log dữ liệu cảm biến.
- `anomaly_event_log.csv`: log cảnh báo bất thường.
- `forecast_log.csv`: log kết quả dự báo.

## Bước 8: Kết luận

Nói ngắn gọn:

> Dự án thể hiện một pipeline AIoT hoàn chỉnh: Android phone làm IoT device, FastAPI làm backend inference, CSV làm storage đơn giản, React dashboard hiển thị monitoring, Docker Compose đóng gói multi-service. AI chỉ khuyến nghị và cảnh báo, không tự điều khiển thiết bị.
