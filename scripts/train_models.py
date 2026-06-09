"""Script thử nghiệm huấn luyện Isolation Forest cho dữ liệu giả lập PhoneGuard."""

import os

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


# Tạo thư mục model nội bộ để lưu file thử nghiệm.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(ROOT_DIR, "backend", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "isolation_forest_model.pkl")

def train_and_save_model() -> None:
    """Sinh dữ liệu giả lập, huấn luyện Isolation Forest và lưu file model."""
    print("--- 🧠 ĐANG HUẤN LUYỆN MÔ HÌNH AI PHÁT HIỆN DỊ THƯỜNG ---")

    # Sinh dữ liệu huấn luyện giả lập cho trạng thái vận hành bình thường.
    # Feature thử nghiệm: [battery_level, battery_temperature, battery_voltage, accel_mag, drain_rate].
    np.random.seed(42)
    num_samples = 1000

    # Các phân phối này chỉ dùng cho demo Lab, chưa đại diện cho dữ liệu thực tế.
    battery_level = np.random.uniform(20, 100, num_samples)
    battery_temp = np.random.normal(32, 2.5, num_samples)
    battery_voltage = np.random.uniform(3.7, 4.2, num_samples)
    accel_mag = np.random.normal(9.81, 0.2, num_samples)
    drain_rate = np.random.normal(0.08, 0.03, num_samples)

    X_train = np.column_stack([battery_level, battery_temp, battery_voltage, accel_mag, drain_rate])

    # Huấn luyện Isolation Forest với giả định 2% mẫu có thể là nhiễu/anomaly.
    model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
    model.fit(X_train)

    # Lưu model để sinh artifact tham khảo, backend hiện chưa load model này.
    joblib.dump(model, MODEL_PATH)
    print("✅ Đã huấn luyện thành công Isolation Forest!")
    print(f"💾 Mô hình được lưu tại: {MODEL_PATH}")

    print("\n✅ Hoàn tất huấn luyện. Model có thể được load bằng joblib để inference.")
    print("Lưu ý: Model Isolation Forest này chưa được tích hợp vào backend hiện tại.")
    print("Backend đang dùng rule-based detection. Cần cập nhật anomaly.py để dùng model này.")


if __name__ == "__main__":
    train_and_save_model()
