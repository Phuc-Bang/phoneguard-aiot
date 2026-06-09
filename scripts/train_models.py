import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Set directories
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(ROOT_DIR, "backend", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "isolation_forest_model.pkl")

def train_and_save_model():
    print("--- 🧠 ĐANG HUẤN LUYỆN MÔ HÌNH AI PHÁT HIỆN DỊ THƯỜNG ---")
    
    # Generate synthetic training data (Normal operations)
    # Features: [battery_level, battery_temperature, battery_voltage, accel_mag, drain_rate]
    np.random.seed(42)
    num_samples = 1000
    
    # Normal patterns
    battery_level = np.random.uniform(20, 100, num_samples)
    battery_temp = np.random.normal(32, 2.5, num_samples)  # centered around 32C
    battery_voltage = np.random.uniform(3.7, 4.2, num_samples)
    accel_mag = np.random.normal(9.81, 0.2, num_samples)  # Earth gravity + slight noise
    drain_rate = np.random.normal(0.08, 0.03, num_samples)  # ~0.08% per min (normal)
    
    X_train = np.column_stack([battery_level, battery_temp, battery_voltage, accel_mag, drain_rate])
    
    # Fit Isolation Forest
    # contamination=0.02 means we assume 2% of training data could be noisy/anomalous
    model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
    model.fit(X_train)
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Đã huấn luyện thành công Isolation Forest!")
    print(f"💾 Mô hình được lưu tại: {MODEL_PATH}")
    
    # Initialize the database with default device
    try:
        from backend.app.database import engine, Base, SessionLocal
        from backend.app import models, schemas, crud
        
        print("\n--- 🛠️ KHỞI TẠO CƠ SỞ DỮ LIỆU ---")
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        
        # Check if default device already exists
        default_dev_id = "redmi_note_12_turbo"
        db_device = crud.get_device_by_id(db, default_dev_id)
        if not db_device:
            crud.create_device(
                db, 
                schemas.DeviceCreate(
                    device_id=default_dev_id, 
                    name="Redmi Note 12 Turbo (Bang)", 
                    model="Redmi Note 12 Turbo",
                    battery_capacity=5000
                )
            )
            print(f"✅ Đã đăng ký thiết bị mặc định: {default_dev_id}")
        else:
            print(f"ℹ️ Thiết bị {default_dev_id} đã tồn tại trong DB.")
        db.close()
    except Exception as e:
        print(f"❌ Không thể tự động khởi tạo DB: {e}")
        print("Mẹo: Hãy chạy uvicorn trước để khởi tạo DB.")

if __name__ == "__main__":
    train_and_save_model()
