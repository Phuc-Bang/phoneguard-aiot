// Trang Anomalies hiển thị anomaly event feed.
import type { AnomalyEvent } from "../api/client";
import AnomalyFeed from "../components/AnomalyFeed";

type Props = {
  events: AnomalyEvent[];
};

export default function Anomalies({ events }: Props) {
  return (
    <section className="hud-panel p-4">
      <div className="mb-4">
        <h2 className="text-xl font-black text-white">Anomaly Feed</h2>
        <p className="text-sm text-slate-500">Đọc từ /events và tự động refresh mỗi 3 giây.</p>
      </div>
      <AnomalyFeed events={events} />
    </section>
  );
}
