// Tailwind config cho dark cyber AIoT monitoring dashboard.
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pg: {
          bg: "#061014",
          panel: "#0b171d",
          line: "#1f3c46",
          cyan: "#00e5ff",
          green: "#39ff14",
          amber: "#ffcc4d",
          red: "#ff4d6d",
        },
      },
      boxShadow: {
        bezel: "inset 0 0 0 1px #10262d, 0 20px 60px rgb(0 0 0 / 0.35)",
      },
    },
  },
  plugins: [],
} satisfies Config;
