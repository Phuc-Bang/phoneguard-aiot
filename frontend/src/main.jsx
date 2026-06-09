// Entry React: render dashboard và đọc API base URL từ biến môi trường Vite.
import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, Battery, Bell, Brain, Server, Wifi } from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [health, setHealth] = useState(null);
  const [latest, setLatest] = useState(null);
  const [events, setEvents] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [status, setStatus] = useState("loading");

  const deviceId = latest?.device_id || "android-phone-001";

  async function loadDashboard() {
    try {
      const [healthRes, latestRes, eventsRes, modelRes, forecastRes] = await Promise.all([
        fetch(`${API_BASE_URL}/health`),
        fetch(`${API_BASE_URL}/latest`),
        fetch(`${API_BASE_URL}/events?limit=8`),
        fetch(`${API_BASE_URL}/model-info`),
        fetch(`${API_BASE_URL}/forecast`, { method: "POST" }),
      ]);

      const healthData = await healthRes.json();
      const latestData = await latestRes.json();
      const eventsData = await eventsRes.json();
      const modelData = await modelRes.json();
      const forecastData = await forecastRes.json();

      console.log("[DEBUG] Dashboard data", { healthData, latestData, eventsData, modelData, forecastData });
      setHealth(healthData);
      setLatest(latestData.device_id ? latestData : null);
      setEvents(Array.isArray(eventsData) ? eventsData : []);
      setModelInfo(modelData);
      setForecast(forecastData);
      setStatus("online");
    } catch (error) {
      console.log("[DEBUG] Loi tai dashboard", error);
      setStatus("offline");
    }
  }

  useEffect(() => {
    loadDashboard();
    const timer = window.setInterval(loadDashboard, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const riskText = useMemo(() => {
    if (!latest) return "Chưa có telemetry";
    if (latest.battery_level <= 20 && !latest.charging) return "Cần chú ý pin thấp";
    return "Thiết bị ổn định";
  }, [latest]);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>PhoneGuard AIoT</h1>
          <p>Dockerized Multi-Service AIoT Inference System</p>
        </div>
        <span className={`status ${status}`}>{status}</span>
      </header>

      <section className="grid">
        <Metric icon={<Server />} label="Backend" value={health?.status || "--"} detail={API_BASE_URL} />
        <Metric icon={<Battery />} label="Battery" value={latest ? `${latest.battery_level}%` : "--"} detail={latest?.charging ? "Đang sạc" : "Không sạc"} />
        <Metric icon={<Wifi />} label="Network" value={latest?.network_type || "--"} detail={deviceId} />
        <Metric icon={<Brain />} label="Inference" value={forecast?.estimated_minutes_remaining ? `${forecast.estimated_minutes_remaining} phút` : "N/A"} detail={forecast?.message || "Chưa có forecast"} />
      </section>

      <section className="content">
        <article className="panel">
          <div className="panel-title">
            <Activity />
            <h2>Latest Telemetry</h2>
          </div>
          {latest ? (
            <pre>{JSON.stringify(latest, null, 2)}</pre>
          ) : (
            <p className="empty">Chưa có telemetry. Hãy mở phone-web và gửi dữ liệu tới backend.</p>
          )}
        </article>

        <article className="panel">
          <div className="panel-title">
            <Bell />
            <h2>Anomaly Events</h2>
          </div>
          {events.length > 0 ? (
            <ul className="events">
              {events.map((event) => (
                <li key={event.event_id}>
                  <strong>{event.severity}</strong>
                  <span>{event.device_id}</span>
                  <p>{event.reasons}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty">Chưa có anomaly event.</p>
          )}
        </article>
      </section>

      <section className="footer-grid">
        <div className="panel small">
          <h2>Risk Recommendation</h2>
          <p>{riskText}</p>
        </div>
        <div className="panel small">
          <h2>Model Info</h2>
          <p>{modelInfo?.name || "--"}</p>
          <p className="muted">{modelInfo?.storage || "--"} logs in mounted volume</p>
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value, detail }) {
  return (
    <article className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

createRoot(document.getElementById("root")).render(<App />);
