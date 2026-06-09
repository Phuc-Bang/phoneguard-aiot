// Sidebar điều hướng các khu vực giám sát chính của dashboard.
import { Activity, AlertTriangle, BarChart3, Gauge, Settings, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type PageKey = "overview" | "telemetry" | "anomalies" | "forecast" | "settings";

type SidebarProps = {
  activePage: PageKey;
  onNavigate: (page: PageKey) => void;
};

const items: Array<{ key: PageKey; label: string; icon: LucideIcon }> = [
  { key: "overview", label: "Overview", icon: Gauge },
  { key: "telemetry", label: "Telemetry", icon: Activity },
  { key: "anomalies", label: "Anomalies", icon: AlertTriangle },
  { key: "forecast", label: "Forecast", icon: BarChart3 },
  { key: "settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <>
      <nav className="fixed inset-x-3 bottom-3 z-20 grid grid-cols-5 gap-1 rounded-lg border border-pg-line bg-pg-panel/95 p-1 shadow-bezel backdrop-blur lg:hidden">
        {items.map((item) => {
          const Icon = item.icon;
          const active = activePage === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onNavigate(item.key)}
              className={`focus-ring grid min-h-12 place-items-center rounded-md text-[10px] font-bold transition active:scale-[0.98] ${
                active ? "bg-pg-cyan/12 text-pg-cyan" : "text-slate-500"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <aside className="sticky top-4 hidden h-[calc(100vh-2rem)] w-64 shrink-0 rounded-lg border border-pg-line bg-pg-panel/90 p-4 shadow-bezel lg:block">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg border border-pg-cyan/40 bg-pg-cyan/10 text-pg-cyan">
            <Zap className="h-5 w-5" strokeWidth={1.8} />
          </div>
          <div>
            <p className="text-sm font-black text-white">PhoneGuard</p>
            <p className="text-xs text-slate-500">AIoT node ops</p>
          </div>
        </div>
        <nav className="grid gap-2">
          {items.map((item) => {
            const Icon = item.icon;
            const active = activePage === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className={`focus-ring flex h-11 items-center gap-3 rounded-md border px-3 text-left text-sm font-bold transition hover:-translate-y-px active:translate-y-0 active:scale-[0.99] ${
                  active
                    ? "border-pg-cyan/60 bg-pg-cyan/10 text-pg-cyan"
                    : "border-transparent text-slate-400 hover:border-pg-line hover:bg-white/5 hover:text-slate-100"
                }`}
              >
                <Icon className="h-4 w-4" strokeWidth={1.8} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
