/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        void: "#05070d",
        surface: "#0b0f19",
        panel: "#0f1523",
        line: "#1c2436",
        signal: {
          DEFAULT: "#39ffb0",
          dim: "#1f8f68",
        },
        alert: {
          low: "#39ffb0",
          medium: "#ffd23f",
          high: "#ff8f3f",
          critical: "#ff4d6a",
        },
        ink: {
          DEFAULT: "#e6ecf5",
          dim: "#8a95ab",
          faint: "#4d5871",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
        body: ["'Inter'", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(57,255,176,0.35)",
        panel: "0 1px 0 0 rgba(255,255,255,0.04) inset",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "28px 28px",
      },
    },
  },
  plugins: [],
};
