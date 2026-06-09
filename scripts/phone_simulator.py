import time
import requests
import random
import sys
import threading
from datetime import datetime, timezone

# Configuration
API_URL = "http://localhost:8005/api/v1/telemetry"
DEVICE_ID = "redmi_note_12_turbo"

# State variables (thread-safe using lock)
state_lock = threading.Lock()
current_mode = "normal"  # normal, charging, overheat, drain, freefall_triggered
battery_level = 80.0
battery_temp = 32.0
battery_status = "discharging"
battery_voltage = 3.9

# Accelerometer defaults (G-force static)
accel_x = 0.0
accel_y = 0.0
accel_z = 9.81

# Network defaults
network_type = "Wi-Fi"
network_strength = -55.0

stop_simulator = False

def print_menu():
    print("\n" + "="*50)
    print("📱 GIẢ LẬP ĐIỆN THOẠI REDMI NOTE 12 TURBO (AIoT)")
    print("="*50)
    print("Chế độ hiện tại: " + current_mode.upper())
    print("Chỉ số: Pin: {:.1f}% | Nhiệt độ: {:.1f}°C | Sạc: {}".format(battery_level, battery_temp, battery_status))
    print("-"*50)
    print("Nhập lệnh để thay đổi trạng thái:")
    print("  [n] - Chế độ Bình thường (Xả pin chậm, mát mẻ)")
    print("  [c] - Chế độ Cắm sạc (Pin tăng, nhiệt độ hơi ấm)")
    print("  [o] - Chế độ Quá nhiệt (Pin nóng lên tới >45°C)")
    print("  [d] - Chế độ Hao pin bất thường (Xả nhanh, ứng dụng ngầm)")
    print("  [f] - Giả lập Rơi tự do (Free Fall & Shock)")
    print("  [q] - Thoát giả lập")
    print("="*50)
    print("Nhập lựa chọn của bạn: ", end="", flush=True)

def simulator_loop():
    global battery_level, battery_temp, battery_status, battery_voltage
    global accel_x, accel_y, accel_z, current_mode
    global network_type, network_strength
    
    last_send_time = time.time()
    
    while not stop_simulator:
        time.sleep(0.5)  # Internal tick frequency
        
        # Only send telemetry every 2 seconds
        if time.time() - last_send_time >= 2.0:
            last_send_time = time.time()
            
            with state_lock:
                # Update metrics based on current mode
                if current_mode == "normal":
                    battery_status = "discharging"
                    # Normal discharging rate (~0.05% per 2 seconds)
                    battery_level = max(1.0, battery_level - random.uniform(0.02, 0.05))
                    # Normal temperature fluctuation
                    battery_temp = max(28.0, min(36.0, battery_temp + random.uniform(-0.2, 0.2)))
                    battery_voltage = max(3.6, min(4.2, 3.6 + (battery_level / 100.0) * 0.6))
                    # Accelerometer static with micro-vibrations
                    accel_x = random.uniform(-0.1, 0.1)
                    accel_y = random.uniform(-0.1, 0.1)
                    accel_z = 9.81 + random.uniform(-0.1, 0.1)
                    network_type = "Wi-Fi"
                    network_strength = -55.0 + random.uniform(-2, 2)
                    
                elif current_mode == "charging":
                    battery_status = "charging"
                    # Fast charging rate (~0.2% per 2 seconds)
                    battery_level = min(100.0, battery_level + random.uniform(0.15, 0.3))
                    # Normal charging warm up
                    battery_temp = min(38.5, battery_temp + random.uniform(0.1, 0.3))
                    battery_voltage = min(4.35, 3.8 + (battery_level / 100.0) * 0.5)
                    # Static phone on table
                    accel_x, accel_y, accel_z = 0.0, 0.0, 9.81
                    network_type = "Wi-Fi"
                    network_strength = -50.0
                    
                elif current_mode == "overheat":
                    # Simulating heavy gaming while charging
                    battery_status = "charging"
                    battery_level = min(100.0, battery_level + random.uniform(0.05, 0.1))
                    # Temperature rises quickly
                    battery_temp = min(50.0, battery_temp + random.uniform(0.4, 0.8))
                    battery_voltage = 4.2 + random.uniform(-0.05, 0.05)
                    accel_x = random.uniform(-0.5, 0.5)
                    accel_y = random.uniform(-0.5, 0.5)
                    accel_z = 9.81 + random.uniform(-0.5, 0.5)
                    network_type = "Cellular"
                    network_strength = -95.0 + random.uniform(-5, 5)  # Weak cellular signal makes it hotter
                    
                elif current_mode == "drain":
                    battery_status = "discharging"
                    # Rapid drain (1.5% per 2 seconds)
                    battery_level = max(1.0, battery_level - random.uniform(1.2, 1.8))
                    # Temperature stays relatively high due to heavy load
                    battery_temp = max(35.0, min(41.0, battery_temp + random.uniform(0.1, 0.4)))
                    battery_voltage = max(3.4, battery_voltage - random.uniform(0.01, 0.03))
                    accel_x, accel_y, accel_z = random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 9.81
                    network_type = "Wi-Fi"
                    network_strength = -65.0
                    
                elif current_mode == "freefall_triggered":
                    # Free Fall sequence: 
                    # 1. We send 0 G-force (Free Fall)
                    print("\n💥 [SIMULATOR] ĐANG RƠI TỰ DO...")
                    accel_x, accel_y, accel_z = 0.1, 0.1, 0.2
                    # Create payload for free fall
                    payload = {
                        "device_id": DEVICE_ID,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "battery_level": round(battery_level, 2),
                        "battery_temperature": round(battery_temp, 2),
                        "battery_status": battery_status,
                        "battery_voltage": round(battery_voltage, 2),
                        "network_type": network_type,
                        "network_strength": network_strength,
                        "accel_x": accel_x,
                        "accel_y": accel_y,
                        "accel_z": accel_z
                    }
                    send_post(payload)
                    
                    time.sleep(1.0) # falls for 1 second
                    
                    # 2. Impact: High G-force spike
                    print("💥 [SIMULATOR] VA CHẠM MẠNH (SHOCK)!")
                    accel_x, accel_y, accel_z = 12.5, -15.2, 32.4
                    payload["accel_x"] = accel_x
                    payload["accel_y"] = accel_y
                    payload["accel_z"] = accel_z
                    send_post(payload)
                    
                    time.sleep(1.0)
                    
                    # 3. Stabilization back to normal
                    print("📱 [SIMULATOR] Điện thoại nằm im sau va chạm.")
                    accel_x, accel_y, accel_z = 0.0, 0.0, 9.81
                    current_mode = "normal"
                    # Don't send yet, standard loop will pick it up on next cycle
                    continue

                # Prepare standard payload
                payload = {
                    "device_id": DEVICE_ID,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "battery_level": round(battery_level, 2),
                    "battery_temperature": round(battery_temp, 2),
                    "battery_status": battery_status,
                    "battery_voltage": round(battery_voltage, 2),
                    "network_type": network_type,
                    "network_strength": network_strength,
                    "accel_x": round(accel_x, 4),
                    "accel_y": round(accel_y, 4),
                    "accel_z": round(accel_z, 4)
                }
                
                send_post(payload)

def send_post(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=2)
        if response.status_code == 200:
            print(".", end="", flush=True)
        else:
            print("x", end="", flush=True)
    except requests.exceptions.RequestException:
        print("?", end="", flush=True)  # Server down

def main():
    global current_mode, stop_simulator
    
    # Run the background sender thread
    t = threading.Thread(target=simulator_loop)
    t.daemon = True
    t.start()
    
    # Simple CLI control loop
    try:
        while True:
            print_menu()
            cmd = sys.stdin.readline().strip().lower()
            
            if cmd == 'q':
                stop_simulator = True
                print("👋 Đang dừng simulator...")
                break
            elif cmd == 'n':
                with state_lock:
                    current_mode = "normal"
            elif cmd == 'c':
                with state_lock:
                    current_mode = "charging"
            elif cmd == 'o':
                with state_lock:
                    current_mode = "overheat"
            elif cmd == 'd':
                with state_lock:
                    current_mode = "drain"
            elif cmd == 'f':
                with state_lock:
                    current_mode = "freefall_triggered"
            else:
                print("Lệnh không hợp lệ!")
                
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_simulator = True
        print("\n👋 Đang dừng simulator...")
    
    t.join(timeout=2)
    print("Đã dừng.")

if __name__ == "__main__":
    main()
