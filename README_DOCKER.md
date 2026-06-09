# PhoneGuard AIoT - Lab 5 Docker Guide

Tài liệu này hướng dẫn chạy PhoneGuard AIoT theo mô hình **Dockerized Multi-Service AIoT Inference System** gồm 2 service:

- `backend`: FastAPI inference API, nhận telemetry và ghi log.
- `frontend`: React/Vite dashboard, build thành static site và chạy bằng Nginx.

## 1. Chạy Docker Compose

Từ thư mục gốc dự án:

```bash
docker compose up --build
```

Sau khi build và chạy xong, mở:

- Backend docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000
- Health: http://localhost:8000/health

Nếu `http://localhost:8000/health` trả về nội dung của dự án khác, nghĩa là port `8000` trên máy host đang bị service khác chiếm. Hãy dừng service/container đó rồi chạy lại:

```bash
docker compose up --build
```

## 2. Kiểm tra service

```bash
docker compose ps
```

Xem log backend:

```bash
docker compose logs -f backend
```

Xem log frontend:

```bash
docker compose logs -f frontend
```

Dừng và xóa container:

```bash
docker compose down
```

## 3. Docker image là gì?

Docker image là gói đóng băng môi trường chạy ứng dụng. Image backend chứa Python, thư viện FastAPI và mã nguồn trong `backend/app`. Image frontend chứa Node để build React/Vite, sau đó copy kết quả build sang Nginx để phục vụ dashboard.

Image giống như bản mẫu chỉ đọc. Khi chạy image, Docker tạo ra container.

## 4. Container là gì?

Container là tiến trình đang chạy được tạo từ image. Trong dự án này:

- Container `phoneguard-backend` chạy `uvicorn app.main:app`.
- Container `phoneguard-frontend` chạy Nginx để phục vụ dashboard.

Container có filesystem riêng, network riêng và biến môi trường riêng, nhưng vẫn có thể mount thư mục từ máy host để giữ log.

## 5. Port mapping là gì?

Port mapping nối port trong container ra port trên máy host.

Trong `docker-compose.yml`:

```yaml
ports:
  - "8000:8000"
```

Nghĩa là backend trong container lắng nghe port `8000`, người dùng trên máy host truy cập bằng `http://localhost:8000`.

Frontend dùng:

```yaml
ports:
  - "3000:80"
```

Nghĩa là Nginx trong container lắng nghe port `80`, nhưng người dùng mở dashboard bằng `http://localhost:3000`.

## 6. Volume giữ telemetry/event/forecast logs như thế nào?

Backend mount volume:

```yaml
volumes:
  - ./outputs:/app/outputs
```

Điều này nghĩa là:

- Trong container, backend ghi log vào `/app/outputs`.
- Trên máy host, dữ liệu thật nằm ở `./outputs`.

Các file log:

- `outputs/telemetry.csv`: telemetry từ điện thoại Android.
- `outputs/anomaly_event_log.csv`: anomaly event do backend phát hiện.
- `outputs/forecast_log.csv`: log kết quả dự báo pin/inference.

Khi chạy `docker compose down`, container bị xóa nhưng dữ liệu trong `./outputs` vẫn còn.

## 7. Frontend gọi backend qua biến môi trường

Dashboard React/Vite đọc API base URL từ:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Trong Docker build, biến này được truyền qua `build.args`:

```yaml
args:
  VITE_API_BASE_URL: http://localhost:8000
```

Vì Vite nhúng biến `VITE_*` vào bundle lúc build, cần rebuild frontend nếu đổi URL backend:

```bash
docker compose up --build
```

## 8. Vì sao phải chạy local trước Docker?

Nên chạy local trước Docker để tách lỗi ứng dụng khỏi lỗi đóng gói.

Thứ tự kiểm tra khuyến nghị:

1. Chạy backend local và kiểm tra `http://localhost:8000/health`.
2. Gửi thử `POST /telemetry` và chắc chắn CSV được ghi đúng.
3. Chạy frontend local bằng Vite và kiểm tra dashboard gọi được backend.
4. Sau khi app chạy ổn, mới build Docker.

Cách này giúp biết lỗi nằm ở code FastAPI/React hay ở Dockerfile, port mapping, volume, network hoặc biến môi trường.

## 9. Test nhanh telemetry trong Docker

Sau khi `docker compose up --build`, gửi mẫu telemetry:

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"android-phone-001\",\"timestamp\":\"2026-06-09T09:00:00Z\",\"battery_level\":72,\"charging\":false,\"acc_x\":0.1,\"acc_y\":0.2,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"wifi\"}"
```

Sau đó mở dashboard:

```text
http://localhost:3000
```
