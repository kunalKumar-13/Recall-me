import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Mirrored from the desktop app's palette so the website and
        // launcher feel like the same product.
        bg: "#0a0b0f",
        surface: "rgba(15, 17, 21, 0.92)",
        accent: "#8b9bff",
        accentSoft: "#3b4566",
        highlight: "#cdd2e0",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        tightest: "-0.04em",
      },
      boxShadow: {
        cinematic: "0 40px 120px -30px rgba(0, 0, 0, 0.8)",
        glow: "0 0 80px -10px rgba(139, 155, 255, 0.4)",
      },
      animation: {
        float: "float 8s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
