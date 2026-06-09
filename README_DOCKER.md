# PhoneGuard AIoT - Lab 5 Docker Guide

PhoneGuard AIoT chạy theo mô hình **Dockerized Multi-Service AIoT Inference System**:

- `backend`: FastAPI nhận telemetry, chạy anomaly/forecast/risk và ghi log CSV.
- `frontend`: React/Vite dashboard build static và phục vụ bằng Nginx.

## Chạy Docker Compose

Từ thư mục gốc `phoneguard-aiot`:

```bash
docker compose up --build
```

Sau khi chạy xong, mở:

- Backend docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000
- Health: http://localhost:8000/health

Nếu `localhost:8000` đang bị service khác chiếm, hãy dừng service đó rồi chạy lại `docker compose up --build`.

## Kiểm tra service

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

Dừng hệ thống:

```bash
docker compose down
```

## Docker image là gì?

Docker image là gói đóng băng môi trường chạy ứng dụng. Image backend chứa Python, FastAPI, Uvicorn và mã nguồn `backend/app`. Image frontend dùng Node để build React/Vite, sau đó copy `dist/` sang Nginx.

Image là bản mẫu chỉ đọc. Khi chạy image, Docker tạo container.

## Container là gì?

Container là tiến trình đang chạy từ image, có filesystem và môi trường riêng.

Trong dự án này:

- `phoneguard-backend` chạy FastAPI ở port container `8000`.
- `phoneguard-frontend` chạy Nginx ở port container `80`.

## Port mapping là gì?

Port mapping nối port trong container ra máy host.

Backend:

```yaml
ports:
  - "8000:8000"
```

Nghĩa là người dùng mở `http://localhost:8000`, request được chuyển vào port `8000` trong container backend.

Frontend:

```yaml
ports:
  - "3000:80"
```

Nghĩa là người dùng mở `http://localhost:3000`, request được chuyển vào Nginx port `80` trong container frontend.

## Volume giữ telemetry/event/forecast logs

Backend mount:

```yaml
volumes:
  - ./outputs:/app/outputs
environment:
  - OUTPUT_DIR=/app/outputs
```

Backend ghi log trong container tại `/app/outputs`, nhưng dữ liệu thật nằm ở thư mục `./outputs` trên máy host. Khi `docker compose down`, container bị xóa nhưng các CSV vẫn còn.

Các file log:

- `outputs/phone_telemetry.csv`
- `outputs/anomaly_event_log.csv`
- `outputs/forecast_log.csv`

## Vì sao phải chạy local trước Docker?

Nên chạy local trước để tách lỗi ứng dụng khỏi lỗi đóng gói:

1. Chạy backend local và kiểm tra `http://localhost:8000/health`.
2. Gửi thử `POST /telemetry` và chắc chắn CSV ghi đúng.
3. Chạy frontend local bằng `npm run dev` và kiểm tra dashboard gọi được backend.
4. Khi app local ổn, mới build Docker.

Cách này giúp biết lỗi nằm ở code FastAPI/React hay ở Dockerfile, port mapping, volume, network hoặc biến môi trường.

## Demo bằng Redmi Note 12 Turbo cùng Wi-Fi

1. Cho laptop và Redmi Note 12 Turbo vào cùng mạng Wi-Fi.
2. Chạy Docker:

```bash
docker compose up --build
```

3. Lấy IP LAN của laptop, ví dụ:

```text
192.168.1.5
```

4. Mở phone-web trên Redmi bằng Live Server hoặc một static server cùng mạng. Ví dụ nếu Live Server chạy port `5500`:

```text
http://192.168.1.5:5500/phone-web/index.html
```

5. Trong ô Backend URL trên phone-web, nhập:

```text
http://192.168.1.5:8000
```

6. Bấm **Start Sending**. Điện thoại sẽ gửi telemetry mỗi 3 giây vào backend Docker.

7. Trên laptop, mở dashboard:

```text
http://localhost:3000
```

8. Theo dõi log backend:

```bash
docker compose logs -f backend
```

## Test nhanh API

```bash
curl -X POST http://localhost:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"redmi-note-12-turbo\",\"timestamp\":\"2026-06-09T09:00:00Z\",\"battery_level\":72,\"charging\":false,\"acc_x\":0.1,\"acc_y\":0.2,\"acc_z\":9.8,\"light_lux\":120,\"network_type\":\"online\"}"
```
