// Trang Settings cho phép đổi API base URL runtime.
import { useState } from "react";

type Props = {
  apiBaseUrl: string;
  onSave: (value: string) => void;
};

export default function Settings({ apiBaseUrl, onSave }: Props) {
  const [value, setValue] = useState(apiBaseUrl);

  return (
    <section className="hud-panel p-5">
      <h2 className="text-xl font-black text-white">Settings</h2>
      <p className="mt-2 text-sm text-slate-500">API base URL mặc định lấy từ VITE_API_BASE_URL, fallback http://localhost:8000.</p>
      <label className="mt-5 grid gap-2 text-sm font-bold text-slate-300">
        API Base URL
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          className="focus-ring h-11 rounded-md border border-pg-line bg-black/30 px-3 text-slate-100 outline-none focus:border-pg-cyan"
          placeholder="http://localhost:8000"
        />
      </label>
      <button
        onClick={() => onSave(value)}
        className="focus-ring mt-4 h-11 rounded-md border border-pg-green/40 bg-pg-green/15 px-4 text-sm font-black text-pg-green transition hover:-translate-y-px hover:bg-pg-green/20 active:translate-y-0 active:scale-[0.99]"
      >
        Save API URL
      </button>
    </section>
  );
}
