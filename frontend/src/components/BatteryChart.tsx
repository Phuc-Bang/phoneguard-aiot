// Biểu đồ battery_level theo thời gian bằng Recharts.
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import type { Telemetry } from "../api/client";

type Props = {
  history: Telemetry[];
};

export default function BatteryChart({ history }: Props) {
  const data = history.map((row) => ({
    time: new Date(row.timestamp).toLocaleTimeString(),
    battery: row.battery_level,
  }));
  const hasData = data.length > 0;

  return (
    <section className="hud-panel p-4">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
        <h2 className="text-lg font-black text-white">Battery Line Chart</h2>
        <p className="text-sm text-slate-500">battery_level từ /history</p>
        </div>
        <span className="text-xs font-bold text-pg-green">{hasData ? `${data.length} samples` : "waiting for telemetry"}</span>
      </div>
      <div className="h-72">
        {!hasData ? (
          <div className="grid h-full place-items-center rounded-md border border-dashed border-pg-line bg-black/20 text-sm text-slate-500">
            Chưa có dữ liệu battery.
          </div>
        ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#1f3c46" strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} minTickGap={24} />
            <YAxis domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#071014", border: "1px solid #1f3c46", color: "#ecfeff" }} />
            <Line type="monotone" dataKey="battery" stroke="#39ff14" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
