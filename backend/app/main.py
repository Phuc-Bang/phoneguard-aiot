import os
import json
from datetime import datetime, timezone
from typing import List, Dict
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models, schemas, crud
from .ai.anomaly_detector import detector
from .ai.battery_predictor import BatteryPredictor
from .ai.recommender import Recommender

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PhoneGuard AIoT API",
    description="Backend API for smartphone monitoring, anomaly detection, and predictive analytics",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be closed already, manager will handle cleanup on disconnect
                pass

manager = ConnectionManager()

# Helper: Get standard dashboard stats for a device
def get_device_dashboard_stats(db: Session, device_id: str) -> dict:
    device = crud.get_device_by_id(db, device_id)
    if not device:
        return {}
    
    logs = crud.get_telemetry_logs(db, device_id, limit=1)
    latest_telemetry = logs[0] if logs else None
    
    recent_alerts = crud.get_anomaly_alerts(db, device_id, limit=10)
    recent_recs = crud.get_recommendations(db, device_id, limit=5)
    
    # AI Predictions
    time_prediction = "N/A"
    health_status = "Good"
    anomaly_score = 0.0
    
    if latest_telemetry:
        time_prediction = BatteryPredictor.predict_remaining_time(
            db, device_id, latest_telemetry.battery_level, latest_telemetry.battery_status
        )
        
        # Calculate simple anomaly score (percentage of unresolved alerts)
        unresolved_alerts = [a for a in recent_alerts if not a.resolved]
        if unresolved_alerts:
            critical_count = sum(1 for a in unresolved_alerts if a.severity == "CRITICAL")
            warning_count = sum(1 for a in unresolved_alerts if a.severity == "WARNING")
            
            if critical_count > 0:
                health_status = "Critical"
                anomaly_score = min(0.9 + 0.1 * critical_count, 1.0)
            elif warning_count > 0:
                health_status = "Warning"
                anomaly_score = min(0.4 + 0.1 * warning_count, 0.8)
        else:
            health_status = "Good"
            anomaly_score = 0.0

    return {
        "device_id": device_id,
        "device_info": schemas.DeviceResponse.model_validate(device) if device else None,
        "latest_telemetry": schemas.TelemetryResponse.model_validate(latest_telemetry) if latest_telemetry else None,
        "time_to_empty_or_full": time_prediction,
        "anomaly_score": anomaly_score,
        "health_status": health_status,
        "recent_alerts": [schemas.AnomalyAlertResponse.model_validate(a) for a in recent_alerts],
        "recent_recommendations": [schemas.RecommendationResponse.model_validate(r) for r in recent_recs]
    }

# API Endpoints
@app.post("/api/v1/devices", response_model=schemas.DeviceResponse)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = crud.get_device_by_id(db, device.device_id)
    if db_device:
        # Update device if already exists
        db_device.name = device.name
        db_device.model = device.model
        db_device.battery_capacity = device.battery_capacity
        db.commit()
        db.refresh(db_device)
        return db_device
    return crud.create_device(db, device)

@app.get("/api/v1/devices", response_model=List[schemas.DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    return db.query(models.Device).all()

@app.post("/api/v1/telemetry", response_model=schemas.TelemetryResponse)
async def log_telemetry(telemetry: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    # Verify device exists, auto-create if not
    db_device = crud.get_device_by_id(db, telemetry.device_id)
    if not db_device:
        crud.create_device(db, schemas.DeviceCreate(device_id=telemetry.device_id, name="Auto Registered Phone"))
    
    # Save log
    db_log = crud.create_telemetry_log(db, telemetry)
    
    # Run AI Anomaly Detection
    detector.process_telemetry(db, telemetry)
    
    # Run Operational Recommendations
    Recommender.generate_recommendations(db, telemetry)
    
    # Broadcast updated stats to WebSockets
    stats = get_device_dashboard_stats(db, telemetry.device_id)
    await manager.broadcast(stats)
    
    return db_log

# Endpoint dedicated to the "Sensor Logger" Android App format
@app.post("/api/v1/telemetry/sensor-logger")
async def log_telemetry_sensor_logger(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    device_id = data.get("deviceId", "sensor_logger_device")
    payload_list = data.get("payload", [])
    
    # Check/register device
    db_device = crud.get_device_by_id(db, device_id)
    if not db_device:
        crud.create_device(
            db, 
            schemas.DeviceCreate(
                device_id=device_id, 
                name="Redmi Note 12 Turbo", 
                model="Redmi Note 12 Turbo"
            )
        )
        
    # Map Sensor Logger arrays into variables
    # We will look for accelerometer, battery and network state
    battery_level = 50.0
    battery_temp = 30.0
    battery_status = "discharging"
    battery_voltage = 3.8
    
    accel_x, accel_y, accel_z = 0.0, 0.0, 9.81
    network_type = "Unknown"
    network_strength = -50.0
    
    timestamp = datetime.now(timezone.utc)
    
    has_battery = False
    has_accel = False
    
    for item in payload_list:
        name = item.get("name")
        time_ns = item.get("time", 0)
        # Convert nanoseconds to float timestamp and datetime
        if time_ns > 0:
            timestamp = datetime.fromtimestamp(time_ns / 1e9, tz=timezone.utc)
            
        values = item.get("values", {})
        
        if name == "battery":
            has_battery = True
            # Sensor Logger fields under values: level (%), temp (C), status, voltage (V)
            battery_level = float(values.get("level", battery_level))
            battery_temp = float(values.get("temperature", values.get("temp", battery_temp)))
            battery_status = str(values.get("status", battery_status)).lower()
            battery_voltage = float(values.get("voltage", battery_voltage))
            
        elif name == "accelerometer":
            has_accel = True
            accel_x = float(values.get("x", accel_x))
            accel_y = float(values.get("y", accel_y))
            accel_z = float(values.get("z", accel_z))
            
        elif name == "network":
            # If network stats are present
            network_type = str(values.get("type", network_type))
            network_strength = float(values.get("strength", network_strength))

    # Standardize Sensor Logger status names to: charging, discharging, full, not_charging
    if "charging" in battery_status:
        battery_status = "charging"
    elif "discharging" in battery_status:
        battery_status = "discharging"
    elif "full" in battery_status:
        battery_status = "full"
    else:
        battery_status = "not_charging"

    # Only save if we got battery or acceleration data
    if has_battery or has_accel:
        telemetry_in = schemas.TelemetryCreate(
            device_id=device_id,
            timestamp=timestamp,
            battery_level=battery_level,
            battery_temperature=battery_temp,
            battery_status=battery_status,
            battery_voltage=battery_voltage,
            network_type=network_type,
            network_strength=network_strength,
            accel_x=accel_x,
            accel_y=accel_y,
            accel_z=accel_z
        )
        
        db_log = crud.create_telemetry_log(db, telemetry_in)
        
        # Run AI Anomaly Detection
        detector.process_telemetry(db, telemetry_in)
        
        # Run Operational Recommendations
        Recommender.generate_recommendations(db, telemetry_in)
        
        # Broadcast updated stats
        stats = get_device_dashboard_stats(db, device_id)
        await manager.broadcast(stats)
        
        return {"status": "success", "id": db_log.id}
        
    return {"status": "skipped", "reason": "No accelerometer or battery data in payload"}

@app.get("/api/v1/dashboard/{device_id}", response_model=schemas.DashboardStats)
def get_dashboard(device_id: str, db: Session = Depends(get_db)):
    stats = get_device_dashboard_stats(db, device_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Device not found or no telemetry data yet")
    return stats

# WebSocket endpoint for real-time dashboard connection
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        # Immediately send latest state of all devices to new connection
        devices = db.query(models.Device).all()
        for dev in devices:
            stats = get_device_dashboard_stats(db, dev.device_id)
            if stats:
                await websocket.send_json(stats)
                
        # Loop to keep connection open and listen for client requests
        while True:
            data = await websocket.receive_text()
            # If client requests updates for specific device
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif msg.get("action") == "get_device" and "device_id" in msg:
                    stats = get_device_dashboard_stats(db, msg["device_id"])
                    await websocket.send_json(stats)
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Serve Frontend static files
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory '{FRONTEND_DIR}' not found. Cannot serve frontend files.")
