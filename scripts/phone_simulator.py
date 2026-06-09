"""CLI giả lập điện thoại Android gửi telemetry đúng schema PhoneGuard AIoT."""

import os
import random
import sys
import threading
import time
from datetime import datetime, timezone

import requests


# Cấu hình endpoint có thể đổi bằng biến môi trường PHONEGUARD_API_URL.
API_URL = os.getenv("PHONEGUARD_API_URL", "http://localhost:8000/telemetry")
DEVICE_ID = os.getenv("PHONEGUARD_DEVICE_ID", "redmi_note_12_turbo")
SEND_INTERVAL_SECONDS = 3.0

# Trạng thái mô phỏng được bảo vệ bằng lock vì luồng gửi telemetry chạy nền.
state_lock = threading.Lock()
current_mode = "normal"
stop_simulator = False

battery_level = 80.0
charging = False
acc_x = 0.0
acc_y = 0.0
acc_z = 9.81
light_lux = 120.0
network_type = "wifi"


def print_menu() -> None:
    """In menu điều khiển trạng thái mô phỏng cho người demo."""
    print("\n" + "=" * 58)
    print("GIẢ LẬP ĐIỆN THOẠI REDMI NOTE 12 TURBO (PHONEGUARD AIoT)")
    print("=" * 58)
    print(f"Backend endpoint: {API_URL}")
    print(f"Chế độ hiện tại: {current_mode.upper()}")
    print(f"Chỉ số: Pin {battery_level:.1f}% | Sạc {charging} | Mạng {network_type}")
    print("-" * 58)
    print("Nhập lệnh để thay đổi trạng thái:")
    print("  [n] - Bình thường")
    print("  [c] - Cắm sạc")
    print("  [d] - Hao pin nhanh")
    print("  [f] - Va chạm/rơi thiết bị")
    print("  [x] - Mất mạng/offline")
    print("  [q] - Thoát giả lập")
    print("=" * 58)
    print("Nhập lựa chọn của bạn: ", end="", flush=True)


def simulator_loop() -> None:
    """Luồng nền cập nhật trạng thái và gửi telemetry mỗi 3 giây."""
    global battery_level, charging, acc_x, acc_y, acc_z, light_lux, network_type, current_mode

    while not stop_simulator:
        time.sleep(SEND_INTERVAL_SECONDS)

        with state_lock:
            if current_mode == "normal":
                charging = False
                battery_level = max(1.0, battery_level - random.uniform(0.02, 0.08))
                acc_x = random.uniform(-0.1, 0.1)
                acc_y = random.uniform(-0.1, 0.1)
                acc_z = 9.81 + random.uniform(-0.12, 0.12)
                light_lux = random.uniform(80, 220)
                network_type = "wifi"

            elif current_mode == "charging":
                charging = True
                battery_level = min(100.0, battery_level + random.uniform(0.12, 0.28))
                acc_x = random.uniform(-0.03, 0.03)
                acc_y = random.uniform(-0.03, 0.03)
                acc_z = 9.81 + random.uniform(-0.04, 0.04)
                light_lux = random.uniform(60, 180)
                network_type = "wifi"

            elif current_mode == "drain":
                charging = False
                battery_level = max(1.0, battery_level - random.uniform(5.0, 7.5))
                acc_x = random.uniform(-0.2, 0.2)
                acc_y = random.uniform(-0.2, 0.2)
                acc_z = 9.81 + random.uniform(-0.2, 0.2)
                light_lux = random.uniform(100, 260)
                network_type = "wifi"

            elif current_mode == "offline":
                charging = False
                battery_level = max(1.0, battery_level - random.uniform(0.05, 0.12))
                acc_x = random.uniform(-0.1, 0.1)
                acc_y = random.uniform(-0.1, 0.1)
                acc_z = 9.81 + random.uniform(-0.1, 0.1)
                light_lux = random.uniform(40, 140)
                network_type = "offline"

            elif current_mode == "drop":
                charging = False
                acc_x = random.uniform(10.0, 18.0)
                acc_y = random.uniform(-18.0, -10.0)
                acc_z = random.uniform(20.0, 32.0)
                light_lux = random.uniform(20, 120)
                network_type = "wifi"
                print("\n[DEBUG] Simulator đang gửi sample POSSIBLE_DROP")
                current_mode = "normal"

            payload = build_payload()

        send_post(payload)


def build_payload() -> dict[str, object]:
    """Tạo payload đúng schema TelemetryIn của backend FastAPI."""
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_level": round(battery_level, 2),
        "charging": charging,
        "acc_x": round(acc_x, 4),
        "acc_y": round(acc_y, 4),
        "acc_z": round(acc_z, 4),
        "light_lux": round(light_lux, 2),
        "network_type": network_type,
    }


def send_post(payload: dict[str, object]) -> None:
    """Gửi telemetry tới backend và in trạng thái ngắn gọn cho terminal demo."""
    try:
        response = requests.post(API_URL, json=payload, timeout=3)
        if response.status_code < 400:
            print(".", end="", flush=True)
            print(f"\n[DEBUG] Gửi telemetry thành công: pin={payload['battery_level']} mode={current_mode}")
        else:
            print("x", end="", flush=True)
            print(f"\n[DEBUG] Backend trả lỗi {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as exc:
        print("?", end="", flush=True)
        print(f"\n[DEBUG] Không gửi được telemetry: {exc}")


def main() -> None:
    """Chạy CLI điều khiển simulator và luồng gửi telemetry nền."""
    global current_mode, stop_simulator

    sender_thread = threading.Thread(target=simulator_loop, daemon=True)
    sender_thread.start()

    try:
        while True:
            print_menu()
            command = sys.stdin.readline().strip().lower()

            with state_lock:
                if command == "q":
                    stop_simulator = True
                    print("Đang dừng simulator...")
                    break
                if command == "n":
                    current_mode = "normal"
                elif command == "c":
                    current_mode = "charging"
                elif command == "d":
                    current_mode = "drain"
                elif command == "f":
                    current_mode = "drop"
                elif command == "x":
                    current_mode = "offline"
                else:
                    print("Lệnh không hợp lệ.")

            time.sleep(0.3)
    except KeyboardInterrupt:
        stop_simulator = True
        print("\nĐang dừng simulator...")

    sender_thread.join(timeout=2)
    print("Đã dừng.")


if __name__ == "__main__":
    main()
