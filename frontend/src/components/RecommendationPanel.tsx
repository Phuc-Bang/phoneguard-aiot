// Panel khuyến nghị tổng hợp từ /predict-risk.
import { ShieldCheck } from "lucide-react";
import type { RiskResult } from "../api/client";

type Props = {
  risk: RiskResult | null;
};

const riskTone: Record<string, string> = {
  NORMAL: "text-pg-green",
  WARNING: "text-pg-amber",
  HIGH: "text-pg-red",
  CRITICAL: "text-pg-red",
};

export default function RecommendationPanel({ risk }: Props) {
  if (!risk) {
    return (
      <section className="hud-panel p-5">
        <p className="text-sm font-bold text-slate-300">Risk recommendation chưa sẵn sàng</p>
        <p className="mt-2 text-sm text-slate-500">Dashboard sẽ tự cập nhật khi backend có latest telemetry.</p>
      </section>
    );
  }

  return (
    <section className="hud-panel p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-md border border-pg-cyan/40 bg-pg-cyan/10 text-pg-cyan">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-black text-white">Risk Recommendation</h2>
          <p className="text-sm text-slate-500">{risk.model_version}</p>
        </div>
      </div>
      <p className={`text-3xl font-black ${riskTone[risk.overall_risk] || "text-slate-100"}`}>{risk.overall_risk}</p>
      <p className="mt-2 text-sm text-slate-400">{risk.main_reason} · score {risk.risk_score}</p>
      <ul className="mt-4 grid gap-2">
        {risk.recommendations.map((item) => (
          <li key={item} className="hud-panel-muted p-3 text-sm text-slate-200">
            {item}
          </li>
        ))}
      </ul>
      <p className="mt-4 text-xs text-slate-500">{risk.safety_note}</p>
    </section>
  );
}
