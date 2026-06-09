// Trang Overview hiển thị trạng thái tổng quan thiết bị.
import { Battery, Clock, PlugZap, Router, ShieldAlert, Smartphone } from "lucide-react";
import type { DashboardData } from "../api/client";
import MetricCard from "../components/MetricCard";
import RecommendationPanel from "../components/RecommendationPanel";

type Props = {
  data: DashboardData;
  lastRefresh: string;
};

export default function Overview({ data, lastRefresh }: Props) {
  const latest = data.latest;
  const risk = data.risk?.overall_risk || "UNKNOWN";

  return (
    <div className="grid gap-4">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <MetricCard className="xl:col-span-1" icon={<Battery className="h-5 w-5" />} label="Battery" value={latest ? `${latest.battery_level}%` : "--"} tone="green" />
        <MetricCard className="xl:col-span-1" icon={<PlugZap className="h-5 w-5" />} label="Charging" value={latest?.charging ? "YES" : latest ? "NO" : "--"} tone={latest?.charging ? "green" : "amber"} />
        <MetricCard className="xl:col-span-1" icon={<Router className="h-5 w-5" />} label="Network" value={latest?.network_type || "--"} tone={latest?.network_type === "offline" ? "red" : "cyan"} />
        <MetricCard className="xl:col-span-1" icon={<Smartphone className="h-5 w-5" />} label="Device status" value={data.health ? "ONLINE" : "OFFLINE"} detail={latest?.device_id || "No device"} tone={data.health ? "green" : "red"} />
        <MetricCard className="xl:col-span-2" icon={<Clock className="h-5 w-5" />} label="Last update" value={latest ? new Date(latest.timestamp).toLocaleTimeString() : "--"} detail={`Refresh ${lastRefresh}`} tone="slate" />
        <MetricCard className="md:col-span-2 xl:col-span-6" icon={<ShieldAlert className="h-5 w-5" />} label="Overall risk" value={risk} detail={data.risk?.main_reason || "No risk data"} tone={risk === "NORMAL" ? "green" : risk === "WARNING" ? "amber" : "red"} />
      </section>
      <RecommendationPanel risk={data.risk} />
    </div>
  );
}
