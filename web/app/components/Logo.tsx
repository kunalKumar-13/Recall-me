type LogoProps = {
  className?: string;
};

/**
 * Recall identity mark — three concentric arcs converging on a solid
 * pivot. Reads as resonance / ripples of memory: a thought you cast,
 * the rings that come back. Geometric, mono-safe, distinctive at any
 * size. Pairs with the "Recall" wordmark in the nav.
 */
export function Logo({ className }: LogoProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      role="img"
      aria-label="Recall"
      fill="none"
    >
      <defs>
        <linearGradient
          id="recall-mark"
          x1="4"
          y1="4"
          x2="28"
          y2="28"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#7C9BFF" />
          <stop offset="1" stopColor="#AFC2FF" />
        </linearGradient>
      </defs>

      {/* Subtle frame — the container of memory */}
      <rect
        x="2.25"
        y="2.25"
        width="27.5"
        height="27.5"
        rx="8"
        fill="rgba(124, 155, 255, 0.08)"
        stroke="url(#recall-mark)"
        strokeOpacity="0.45"
        strokeWidth="1"
      />

      {/* Outer arc — the call going out */}
      <path
        d="M22.5 8.5 A 10 10 0 1 1 8.5 22.5"
        stroke="url(#recall-mark)"
        strokeWidth="1.7"
        strokeLinecap="round"
      />

      {/* Inner arc — the recall coming back */}
      <path
        d="M19.5 12 A 5 5 0 1 1 12 19.5"
        stroke="url(#recall-mark)"
        strokeWidth="1.7"
        strokeLinecap="round"
      />

      {/* Pivot — the moment of remembering */}
      <circle cx="16" cy="16" r="1.9" fill="url(#recall-mark)" />
    </svg>
  );
}
