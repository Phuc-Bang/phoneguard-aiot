# PhoneGuard Phone Web

`phone-web` là trang HTML chạy trên điện thoại Android để gửi telemetry về FastAPI backend qua `POST /telemetry` mỗi 3 giây.

## Chạy bằng Live Server

1. Mở project `phoneguard-aiot` trong VS Code.
2. Cài extension **Live Server** nếu chưa có.
3. Mở file `phone-web/index.html`.
4. Chọn **Open with Live Server**.
5. Trên máy tính, Live Server thường mở dạng:

```text
http://127.0.0.1:5500/phone-web/index.html
```

## Truy cập từ Redmi cùng Wi-Fi

1. Đảm bảo máy tính và Redmi dùng cùng mạng Wi-Fi.
2. Lấy IP LAN của máy tính, ví dụ:

```text
192.168.1.5
```

3. Trên Redmi, mở Chrome và truy cập Live Server bằng IP máy tính:

```text
http://192.168.1.5:5500/phone-web/index.html
```

4. Chạy backend FastAPI:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. Trong ô **Backend URL** trên điện thoại, nhập:

```text
http://192.168.1.5:8000
```

6. Bấm **Start Sending**. Trang sẽ gửi telemetry mỗi 3 giây.

## Payload gửi lên backend

```json
{
  "device_id": "redmi-phone-001",
  "timestamp": "2026-06-09T09:00:00.000Z",
  "battery_level": 72.5,
  "charging": false,
  "acc_x": 0.1,
  "acc_y": 0.2,
  "acc_z": 9.8,
  "light_lux": null,
  "network_type": "online"
}
```

## Fallback cảm biến

- Nếu trình duyệt không hỗ trợ Battery API, trang dùng:
  - `battery_level = 50`
  - `charging = false`
- Nếu trình duyệt không hỗ trợ DeviceMotion hoặc chưa cấp quyền, trang dùng:
  - `acc_x = null`
  - `acc_y = null`
  - `acc_z = null`
- `network_type` lấy từ `navigator.onLine`:
  - `online`
  - `offline`

Các cảnh báo fallback sẽ hiển thị trực tiếp trên giao diện.

## Lưu ý

- Một số trình duyệt yêu cầu HTTPS mới cấp quyền cảm biến. Chrome trên Android thường cho phép `devicemotion` khi chạy từ địa chỉ local/LAN, nhưng tùy phiên bản trình duyệt.
- Nếu gửi thất bại, kiểm tra backend có chạy bằng `--host 0.0.0.0` không và Windows Firewall có chặn port `8000` không.
