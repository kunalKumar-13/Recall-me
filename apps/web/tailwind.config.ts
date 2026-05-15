import type { Config } from "tailwindcss";

/**
 * Light-mode design tokens — the canonical palette per the v3
 * screenshot reference (calm editorial futurism, Apple × Arc × Linear).
 *
 * The page is a warm off-white with a faint lavender wash; cards are
 * pure white sitting on it. Lavender carries every accent moment;
 * cyan and mint are reserved for at most two intentional spots each.
 *
 * Glass + heavy blur are out. Surfaces are solid white over the warm
 * page wash, separated by hairline borders and subtle shadows. That's
 * the entire system.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Page surfaces — warm off-whites. Cream not gray.
        bg: {
          page: "#FBF7F4",
          base: "#FFFFFF",
          raised: "#F8F4F0",
          sidebar: "#F4EFEA",
        },
        // Lavender — every accent moment.
        lavender: {
          DEFAULT: "#A99CF7",
          deep: "#8B7FE3",
          soft: "#E8E2FB",
          wash: "#F4EFFF",
        },
        // Reserved secondary accents.
        cyan: {
          DEFAULT: "#7DD8E8",
          soft: "#D7F1F6",
        },
        mint: {
          DEFAULT: "#87DEB7",
          soft: "#DBF4E7",
        },
        // Highlight tint used on excerpts (the yellow marker effect).
        highlight: {
          DEFAULT: "#FEF2A6",
          soft: "#FFF8D6",
        },
        // Ink — three weights of presence, slight purple warmth.
        ink: {
          bright: "#16112B",
          DEFAULT: "#4A4458",
          dim: "#847B8E",
          dimmer: "#B8B2C0",
        },
        // Hairline tint — lavender-tinged so dividers belong to the
        // accent palette rather than fighting it.
        hairline: {
          DEFAULT: "rgba(24, 17, 45, 0.07)",
          strong: "rgba(24, 17, 45, 0.12)",
          lavender: "rgba(169, 156, 247, 0.18)",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        display: [
          "var(--font-fraunces)",
          "ui-serif",
          "Georgia",
          "serif",
        ],
        // Caveat — handwritten script. Used only on the
        // peripheral annotations ("Not filenames. Thoughts." etc.).
        script: [
          "var(--font-caveat)",
          "Bradley Hand",
          "cursive",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      letterSpacing: {
        tightest: "-0.04em",
        tighter: "-0.025em",
        editorial: "-0.015em",
      },
      lineHeight: {
        editorial: "1.05",
      },
      boxShadow: {
        // Card shadows tuned for cream backgrounds. Smaller radius +
        // lower opacity than dark-mode equivalents — light surfaces
        // need subtle shadows to read as raised.
        card: "0 1px 2px rgba(20, 20, 40, 0.04), 0 4px 16px -8px rgba(20, 20, 40, 0.06)",
        cardHover: "0 1px 2px rgba(20, 20, 40, 0.05), 0 8px 28px -10px rgba(20, 20, 40, 0.10)",
        // Dashboard mockup gets a deeper, warmer halo.
        dashboard: "0 30px 80px -30px rgba(80, 60, 140, 0.18), 0 4px 12px -4px rgba(20, 20, 40, 0.05)",
        // Lavender-tinted lift for the primary CTA.
        lift: "0 12px 32px -10px rgba(139, 127, 227, 0.45)",
        // Tiny chip shadow for the floating annotations + trust badges.
        chip: "0 2px 12px -4px rgba(20, 20, 40, 0.10)",
      },
      backgroundImage: {
        // Primary CTA gradient — lavender that catches a touch more
        // saturation in the lower-right corner.
        "lavender-gradient":
          "linear-gradient(135deg, #B5A8FF 0%, #8B7FE3 100%)",
        "lavender-gradient-hover":
          "linear-gradient(135deg, #A99CF7 0%, #7A6FD0 100%)",
        // Page wash — a faint lavender from the top, fading into the
        // warm cream.
        "page-wash":
          "linear-gradient(180deg, rgba(232, 226, 251, 0.35) 0%, rgba(251, 247, 244, 0) 30%), linear-gradient(180deg, #FBF7F4 0%, #F8F4F0 100%)",
      },
      transitionTimingFunction: {
        soft: "cubic-bezier(0.32, 0.72, 0, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
