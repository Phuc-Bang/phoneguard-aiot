"""FastAPI backend cho PhoneGuard AIoT."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .anomaly import detect_anomaly
from .forecasting import forecast_battery
from .risk import predict_risk
from .schemas import AnomalyResult, ForecastRequest, ForecastResult, ModelInfo, RiskResult, TelemetryIn, TelemetryOut
from .storage import (
    ANOMALY_FILE,
    FORECAST_FILE,
    TELEMETRY_FILE,
    append_telemetry,
    get_latest,
    read_events,
    read_telemetry,
)


app = FastAPI(
    title="PhoneGuard AIoT Backend",
    description="FastAPI backend nhận telemetry Android, lưu CSV và chạy inference baseline.",
    version="1.0.0",
)

# Cho phép phone-web và React/Vite dashboard gọi API trong môi trường local/Docker.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Healthcheck đơn giản cho local run và Docker healthcheck."""
    print("[DEBUG] Health check")
    return {"status": "ok", "service": "phoneguard-aiot-backend"}


@app.get("/model-info", response_model=ModelInfo)
def model_info() -> ModelInfo:
    """Trả thông tin baseline model và đường dẫn file log."""
    return ModelInfo(
        name="PhoneGuard rule-based inference baseline",
        version="1.0.0",
        type="rule-based",
        storage="csv",
        telemetry_file=str(TELEMETRY_FILE),
        anomaly_file=str(ANOMALY_FILE),
        forecast_file=str(FORECAST_FILE),
        telemetry_fields=[
            "device_id",
            "timestamp",
            "battery_level",
            "charging",
            "acc_x",
            "acc_y",
            "acc_z",
            "light_lux",
            "network_type",
        ],
    )


@app.post("/telemetry", response_model=TelemetryOut)
def telemetry(payload: TelemetryIn) -> TelemetryOut:
    """Nhận telemetry, lưu CSV và tự động ghi anomaly event nếu phát hiện bất thường."""
    try:
        print(f"[DEBUG] Nhan telemetry device={payload.device_id} pin={payload.battery_level}%")
        saved = append_telemetry(payload)
        detect_anomaly(payload)
        return TelemetryOut(**saved)
    except Exception as exc:
        print(f"[DEBUG] Loi xu ly telemetry: {exc}")
        raise HTTPException(status_code=500, detail="Không thể lưu telemetry") from exc


@app.get("/latest")
def latest(device_id: str | None = Query(default=None)) -> dict:
    """Lấy telemetry mới nhất, có thể lọc theo device_id."""
    row = get_latest(device_id=device_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Chưa có telemetry")
    return row


@app.get("/history")
def history(limit: int = Query(default=100, ge=1, le=5000), device_id: str | None = Query(default=None)) -> list[dict]:
    """Lấy lịch sử telemetry từ outputs/phone_telemetry.csv."""
    return read_telemetry(limit=limit, device_id=device_id)


@app.post("/detect-anomaly", response_model=AnomalyResult)
def detect_anomaly_endpoint(payload: TelemetryIn) -> AnomalyResult:
    """Chạy anomaly detection cho một telemetry sample."""
    return detect_anomaly(payload)


@app.post("/forecast", response_model=ForecastResult)
def forecast(payload: ForecastRequest | None = None, device_id: str | None = Query(default=None)) -> ForecastResult:
    """Dự báo pin từ lịch sử CSV và ghi forecast_log.csv."""
    selected_device = device_id or (payload.device_id if payload else None)
    current_telemetry = payload.telemetry if payload else None
    return forecast_battery(telemetry=current_telemetry, device_id=selected_device)


@app.post("/predict-risk", response_model=RiskResult)
def predict_risk_endpoint(payload: TelemetryIn) -> RiskResult:
    """Sinh mức rủi ro và khuyến nghị từ telemetry."""
    anomaly = detect_anomaly(payload, persist_event=False)
    forecast_result = forecast_battery(telemetry=payload, device_id=payload.device_id)
    return predict_risk(payload, anomaly=anomaly, forecast=forecast_result)


@app.get("/events")
def events(limit: int = Query(default=100, ge=1, le=1000), device_id: str | None = Query(default=None)) -> list[dict]:
    """Đọc anomaly events từ outputs/anomaly_event_log.csv."""
    return read_events(limit=limit, device_id=device_id)
