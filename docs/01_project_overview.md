# 01. Tổng Quan Dự Án PhoneGuard AIoT

## PhoneGuard AIoT là gì?

PhoneGuard AIoT là một hệ thống AIoT dùng điện thoại Android như một thiết bị IoT. Điện thoại thu thập telemetry từ các nguồn sẵn có như pin, trạng thái sạc, cảm biến gia tốc và trạng thái mạng, sau đó gửi dữ liệu về backend FastAPI để lưu trữ, phân tích bất thường, dự báo pin và sinh khuyến nghị rủi ro.

Hệ thống gồm các phần chính:

- `phone-web`: trang web chạy trên điện thoại Android để gửi telemetry.
- `backend`: FastAPI backend nhận dữ liệu, lưu CSV và chạy các module AI rule-based.
- `frontend`: dashboard React/Vite hiển thị telemetry, anomaly, forecast và khuyến nghị.
- `outputs`: thư mục lưu log `phone_telemetry.csv`, `anomaly_event_log.csv`, `forecast_log.csv`.
- Docker Compose: chạy backend và frontend như một hệ thống multi-service.

## Bài toán thực tế

Trong các hệ thống IoT, thiết bị biên thường gặp các vấn đề:

- Pin yếu làm gián đoạn quá trình thu thập dữ liệu.
- Thiết bị rơi hoặc va đập gây sai lệch cảm biến.
- Kết nối mạng mất làm telemetry không gửi được về server.
- Dữ liệu cảm biến bị đứng hoặc thiếu làm mô hình AI dự báo sai.
- Người vận hành cần dashboard dễ quan sát và khuyến nghị rõ ràng.

PhoneGuard AIoT mô phỏng bài toán này bằng chính điện thoại Android, giúp sinh viên hiểu luồng AIoT end-to-end từ thiết bị, backend, lưu trữ, inference đến dashboard.

## Mục tiêu phiên bản hiện tại

- Gửi telemetry từ điện thoại mỗi 3 giây.
- Lưu telemetry vào CSV đơn giản, chưa dùng database phức tạp.
- Phát hiện anomaly bằng rule-based baseline.
- Dự báo pin 15 phút và 30 phút bằng linear trend.
- Tổng hợp risk recommendation từ telemetry, anomaly và forecast.
- Docker hóa backend và frontend theo tinh thần Lab 5.

## Giới hạn của phiên bản đầu

- Chưa huấn luyện mô hình machine learning phức tạp.
- Forecast chỉ là baseline tuyến tính từ dữ liệu gần nhất.
- Dashboard đọc API theo chu kỳ 3 giây, chưa dùng streaming real-time.
- AI chỉ đưa ra cảnh báo và khuyến nghị, không tự điều khiển thiết bị.
