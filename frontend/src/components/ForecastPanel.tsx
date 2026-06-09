// Panel hiển thị forecast pin 15/30 phút và khuyến nghị.
import { BatteryCharging } from "lucide-react";
import type { ForecastResult } from "../api/client";

type Props = {
  forecast: ForecastResult | null;
};

export default function ForecastPanel({ forecast }: Props) {
  if (!forecast) {
    return (
      <section className="hud-panel p-5">
        <p className="text-sm font-bold text-slate-300">Forecast chưa sẵn sàng</p>
        <p className="mt-2 text-sm text-slate-500">Cần telemetry hiện tại từ /latest trước khi gọi /forecast.</p>
      </section>
    );
  }

  return (
    <section className="hud-panel p-5">
      <div className="mb-5 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-md border border-pg-green/40 bg-pg-green/10 text-pg-green">
          <BatteryCharging className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-black text-white">Battery Forecast</h2>
          <p className="text-sm text-slate-500">{forecast.model_output.model_version} · confidence {forecast.model_output.confidence}</p>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="hud-panel-muted p-4">
          <p className="text-sm text-slate-500">Predicted 15min</p>
          <strong className="mt-2 block text-3xl font-black text-pg-green">{forecast.model_output.predicted_battery_15min}%</strong>
        </div>
        <div className="hud-panel-muted p-4">
          <p className="text-sm text-slate-500">Predicted 30min</p>
          <strong className="mt-2 block text-3xl font-black text-pg-cyan">{forecast.model_output.predicted_battery_30min}%</strong>
        </div>
      </div>
      <div className="hud-panel-muted mt-4 p-4">
        <p className="text-xs font-bold text-slate-500">Recommendation</p>
        <p className="mt-2 text-slate-200">{forecast.decision.recommendation}</p>
        <p className="mt-2 text-sm text-slate-500">{forecast.decision.reason}</p>
      </div>
    </section>
  );
}
