// Feed hiển thị anomaly events từ /events.
import { AlertTriangle } from "lucide-react";
import type { AnomalyEvent } from "../api/client";

type Props = {
  events: AnomalyEvent[];
};

const severityClass: Record<string, string> = {
  CRITICAL: "text-pg-red border-pg-red/40 bg-pg-red/10",
  HIGH: "text-pg-red border-pg-red/40 bg-pg-red/10",
  MEDIUM: "text-pg-amber border-pg-amber/40 bg-pg-amber/10",
  LOW: "text-pg-cyan border-pg-cyan/40 bg-pg-cyan/10",
};

export default function AnomalyFeed({ events }: Props) {
  if (!events.length) {
    return (
      <div className="hud-panel-muted p-5 text-sm text-slate-400">
        Chưa có anomaly event. Khi backend phát hiện LOW_BATTERY, POSSIBLE_DROP hoặc NETWORK_LOST, event sẽ xuất hiện tại đây.
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {events.slice().reverse().map((event) => {
        const tone = severityClass[String(event.severity).toUpperCase()] || "text-slate-300 border-pg-line bg-white/5";
        return (
          <article key={event.event_id} className={`rounded-lg border p-4 shadow-bezel ${tone}`}>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex gap-3">
                <AlertTriangle className="mt-1 h-5 w-5 shrink-0" />
                <div>
                  <h3 className="font-black text-white">{event.event_type || "ANOMALY"}</h3>
                  <p className="mt-1 text-sm text-slate-300">{event.explanation || event.recommendation || "Không có mô tả."}</p>
                </div>
              </div>
              <span className="rounded-md border border-current px-2 py-1 text-xs font-black">{event.severity}</span>
            </div>
            {event.recommendation && <p className="mt-3 text-sm text-slate-300">{event.recommendation}</p>}
            <p className="mt-3 text-xs text-slate-500">{event.device_id} · {new Date(event.timestamp).toLocaleString()}</p>
          </article>
        );
      })}
    </div>
  );
}
