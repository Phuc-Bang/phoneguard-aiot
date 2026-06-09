// App shell: quản lý navigation, API URL và auto refresh 3 giây.
import { useEffect, useMemo, useState } from "react";
import Sidebar, { type PageKey } from "./components/Sidebar";
import { getDefaultApiBaseUrl, loadDashboardData, saveApiBaseUrl, type DashboardData } from "./api/client";
import Overview from "./pages/Overview";
import Telemetry from "./pages/Telemetry";
import Anomalies from "./pages/Anomalies";
import Forecast from "./pages/Forecast";
import Settings from "./pages/Settings";

const emptyData: DashboardData = {
  health: null,
  latest: null,
  history: [],
  events: [],
  forecast: null,
  risk: null,
};

export default function App() {
  const [activePage, setActivePage] = useState<PageKey>("overview");
  const [apiBaseUrl, setApiBaseUrl] = useState(getDefaultApiBaseUrl());
  const [data, setData] = useState<DashboardData>(emptyData);
  const [lastRefresh, setLastRefresh] = useState<string>("--");
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      const nextData = await loadDashboardData(apiBaseUrl);
      setData(nextData);
      setLastRefresh(new Date().toLocaleTimeString());
      setError(null);
      console.log("[DEBUG] Dashboard refresh", nextData);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown API error";
      setError(message);
      console.log("[DEBUG] Dashboard refresh failed", err);
    }
  }

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 3000);
    return () => window.clearInterval(timer);
  }, [apiBaseUrl]);

  const page = useMemo(() => {
    if (activePage === "telemetry") return <Telemetry history={data.history} />;
    if (activePage === "anomalies") return <Anomalies events={data.events} />;
    if (activePage === "forecast") return <Forecast forecast={data.forecast} latest={data.latest} />;
    if (activePage === "settings") {
      return (
        <Settings
          apiBaseUrl={apiBaseUrl}
          onSave={(value) => {
            const cleaned = value.replace(/\/$/, "");
            saveApiBaseUrl(cleaned);
            setApiBaseUrl(cleaned);
          }}
        />
      );
    }
    return <Overview data={data} lastRefresh={lastRefresh} />;
  }, [activePage, apiBaseUrl, data, lastRefresh]);

  return (
    <div className="min-h-[100dvh] text-slate-100">
      <div className="mx-auto flex w-full max-w-[1440px] gap-4 p-3 sm:p-4">
        <Sidebar activePage={activePage} onNavigate={setActivePage} />
        <main className="min-w-0 flex-1">
          <header className="hud-panel mb-4 overflow-hidden p-4 sm:p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-xs font-semibold text-pg-cyan">PhoneGuard AIoT</p>
                <h1 className="mt-2 text-balance text-3xl font-black leading-tight text-white sm:text-4xl">
                  Cyber monitoring dashboard
                </h1>
                <p className="mt-2 max-w-[64ch] text-sm leading-6 text-slate-400">
                  Giám sát Android telemetry, anomaly, forecast và khuyến nghị rủi ro trong một cockpit Docker Lab 5.
                </p>
              </div>
              <div className="grid gap-2 text-sm text-slate-300 sm:min-w-80">
                <div className="hud-panel-muted flex items-center justify-between px-3 py-2">
                  <span>Backend</span>
                  <span className={data.health ? "font-black text-pg-green" : "font-black text-pg-red"}>{data.health?.status || "offline"}</span>
                </div>
                <div className="hud-panel-muted truncate px-3 py-2 text-xs text-slate-500">{apiBaseUrl}</div>
              </div>
            </div>
            {error && <p className="mt-3 rounded-md border border-pg-red/40 bg-pg-red/10 p-3 text-sm text-pg-red">{error}</p>}
          </header>
          {page}
        </main>
      </div>
    </div>
  );
}
