// MetricCard hiển thị một chỉ số vận hành chính.
import type { ReactNode } from "react";

type MetricCardProps = {
  label: string;
  value: string;
  detail?: string;
  icon: ReactNode;
  tone?: "cyan" | "green" | "amber" | "red" | "slate";
  className?: string;
};

const toneClass = {
  cyan: "text-pg-cyan bg-pg-cyan/10 border-pg-cyan/30",
  green: "text-pg-green bg-pg-green/10 border-pg-green/30",
  amber: "text-pg-amber bg-pg-amber/10 border-pg-amber/30",
  red: "text-pg-red bg-pg-red/10 border-pg-red/30",
  slate: "text-slate-300 bg-white/5 border-pg-line",
};

export default function MetricCard({ label, value, detail, icon, tone = "cyan", className = "" }: MetricCardProps) {
  return (
    <article className={`hud-panel group relative min-h-36 overflow-hidden p-4 transition duration-200 hover:-translate-y-0.5 hover:border-pg-cyan/40 ${className}`}>
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-pg-cyan/60 to-transparent opacity-0 transition group-hover:opacity-100" />
      <div className={`mb-4 grid h-10 w-10 place-items-center rounded-md border ${toneClass[tone]}`}>{icon}</div>
      <p className="text-xs font-semibold text-slate-500">{label}</p>
      <strong className="mt-2 block break-words text-3xl font-black leading-none text-white">{value}</strong>
      {detail && <p className="mt-3 break-words text-sm leading-5 text-slate-400">{detail}</p>}
    </article>
  );
}
