// Trang Forecast hiển thị predicted battery 15/30 phút và recommendation.
import type { ForecastResult, Telemetry } from "../api/client";
import ForecastPanel from "../components/ForecastPanel";

type Props = {
  forecast: ForecastResult | null;
  latest: Telemetry | null;
};

export default function Forecast({ forecast, latest }: Props) {
  return (
    <div className="grid gap-4">
      <ForecastPanel forecast={forecast} />
      <section className="hud-panel p-5">
        <h2 className="text-lg font-black text-white">Forecast Input</h2>
        <pre className="hud-panel-muted mt-3 max-h-80 overflow-auto p-4 text-sm text-slate-300">
          {latest ? JSON.stringify(latest, null, 2) : "No latest telemetry"}
        </pre>
      </section>
    </div>
  );
}
