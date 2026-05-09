import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Layered backgrounds — the page is a vertical descent through
        // these three deeps so motion has somewhere to go.
        bg: {
          deepest: "#08111F",
          base: "#0B1020",
          raised: "#111827",
        },
        // Accent blues — luminous, never neon. Used sparingly, on the
        // beats that should actually be remembered.
        accent: {
          base: "#7C9BFF",
          DEFAULT: "#8BA5FF",
          light: "#AFC2FF",
        },
        // Text — cool, slightly blue-tinted, three weights of presence.
        ink: {
          bright: "#F5F7FB",
          DEFAULT: "#B6C2D9",
          dim: "#7C8799",
        },
        // Glass surfaces — the launcher card and inner panels.
        glass: {
          base: "rgba(18, 24, 38, 0.72)",
          soft: "rgba(24, 30, 48, 0.55)",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        display: [
          "var(--font-inter)",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      letterSpacing: {
        tightest: "-0.04em",
        tighter: "-0.02em",
      },
      boxShadow: {
        // Used on the floating launcher mockup
        cinematic: "0 40px 120px -30px rgba(0, 0, 0, 0.8)",
        // Used on primary CTA buttons
        cta: "0 10px 40px -10px rgba(124, 155, 255, 0.35)",
        // Used on the play button in the demo card
        glow: "0 0 80px -10px rgba(124, 155, 255, 0.55)",
      },
      backgroundImage: {
        "page-gradient":
          "linear-gradient(180deg, #08111F 0%, #0B1020 55%, #111827 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
