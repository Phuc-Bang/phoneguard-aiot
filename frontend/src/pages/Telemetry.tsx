// Trang Telemetry hiển thị chart pin và gia tốc.
import type { Telemetry as TelemetryRow } from "../api/client";
import BatteryChart from "../components/BatteryChart";
import MotionChart from "../components/MotionChart";

type Props = {
  history: TelemetryRow[];
};

export default function Telemetry({ history }: Props) {
  return (
    <div className="grid gap-4">
      <BatteryChart history={history} />
      <MotionChart history={history} />
    </div>
  );
}
