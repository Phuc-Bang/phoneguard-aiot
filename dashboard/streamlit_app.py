"""Dashboard Streamlit đọc phone_telemetry.csv và anomaly_event_log.csv."""

import os
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("PHONEGUARD_OUTPUT_DIR", ROOT_DIR / "outputs"))
TELEMETRY_FILE = DATA_DIR / "phone_telemetry.csv"
EVENT_FILE = DATA_DIR / "anomaly_event_log.csv"

st.set_page_config(page_title="PhoneGuard AIoT Dashboard", layout="wide")
st.title("PhoneGuard AIoT Dashboard")
st.caption("Dashboard đọc trực tiếp dữ liệu CSV từ FastAPI backend.")


def read_csv(path: Path) -> pd.DataFrame:
    """Đọc CSV an toàn để dashboard không crash khi chưa có dữ liệu."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


telemetry = read_csv(TELEMETRY_FILE)
events = read_csv(EVENT_FILE)

if telemetry.empty:
    st.warning("Chưa có telemetry. Hãy chạy phone-web hoặc gọi POST /telemetry.")
    st.stop()

telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"], errors="coerce")
telemetry = telemetry.dropna(subset=["timestamp"]).sort_values("timestamp")
telemetry["charging"] = telemetry["charging"].astype(str).str.lower().eq("true")

devices = sorted(telemetry["device_id"].dropna().unique())
selected_device = st.sidebar.selectbox("Device", devices)
filtered = telemetry[telemetry["device_id"] == selected_device].tail(300)
latest = filtered.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pin", f"{latest['battery_level']:.0f}%")
col2.metric("Sạc", "Có" if bool(latest["charging"]) else "Không")
col3.metric("Ánh sáng", f"{latest['light_lux']:.0f} lux")
col4.metric("Mạng", str(latest["network_type"]))

st.subheader("Pin theo thời gian")
st.line_chart(filtered.set_index("timestamp")[["battery_level"]])

st.subheader("Gia tốc")
st.line_chart(filtered.set_index("timestamp")[["acc_x", "acc_y", "acc_z"]])

st.subheader("Ánh sáng")
st.line_chart(filtered.set_index("timestamp")[["light_lux"]])

st.subheader("Anomaly events")
if events.empty:
    st.info("Chưa có anomaly event.")
else:
    st.dataframe(events.tail(100), use_container_width=True)
