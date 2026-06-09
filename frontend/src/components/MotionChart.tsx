// Biểu đồ độ lớn gia tốc từ acc_x, acc_y, acc_z.
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import type { Telemetry } from "../api/client";

type Props = {
  history: Telemetry[];
};

function magnitude(row: Telemetry): number | null {
  if (row.acc_x === null || row.acc_y === null || row.acc_z === null) return null;
  return Math.sqrt(row.acc_x ** 2 + row.acc_y ** 2 + row.acc_z ** 2);
}

export default function MotionChart({ history }: Props) {
  const data = history.map((row) => ({
    time: new Date(row.timestamp).toLocaleTimeString(),
    magnitude: magnitude(row),
  }));
  const validSamples = data.filter((row) => row.magnitude !== null).length;

  return (
    <section className="hud-panel p-4">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
        <h2 className="text-lg font-black text-white">Acceleration Magnitude</h2>
        <p className="text-sm text-slate-500">sqrt(acc_x² + acc_y² + acc_z²)</p>
        </div>
        <span className="text-xs font-bold text-pg-cyan">{validSamples ? `${validSamples} motion samples` : "sensor fallback"}</span>
      </div>
      <div className="h-72">
        {!validSamples ? (
          <div className="grid h-full place-items-center rounded-md border border-dashed border-pg-line bg-black/20 text-sm text-slate-500">
            Chưa có dữ liệu accelerometer hợp lệ.
          </div>
        ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#1f3c46" strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fill: "#94a3b8", fontSize: 11 }} minTickGap={24} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#071014", border: "1px solid #1f3c46", color: "#ecfeff" }} />
            <Line type="monotone" dataKey="magnitude" stroke="#00e5ff" strokeWidth={2} dot={false} connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}
