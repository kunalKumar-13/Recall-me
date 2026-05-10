type LogoProps = {
  className?: string;
};

/**
 * Recall.me identity mark — a brain glyph rendered as connected
 * concentric arcs and a central pivot. Reads as both a brain (folds,
 * hemispheres) and a memory ripple (concentric resonance), which is
 * the product idea in two strokes.
 *
 * Uses the lavender gradient. Mono-safe: a single solid stroke color
 * also works at small sizes if currentColor is forced upstream.
 */
export function Logo({ className }: LogoProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      role="img"
      aria-label="Recall.me"
      fill="none"
    >
      <defs>
        <linearGradient
          id="recall-mark-light"
          x1="3"
          y1="3"
          x2="29"
          y2="29"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#A99CF7" />
          <stop offset="1" stopColor="#8B7FE3" />
        </linearGradient>
      </defs>

      {/* Outer ring — soft lavender wash container */}
      <circle
        cx="16"
        cy="16"
        r="13.5"
        fill="rgba(169, 156, 247, 0.10)"
        stroke="url(#recall-mark-light)"
        strokeOpacity="0.55"
        strokeWidth="1.1"
      />

      {/* Brain hemisphere — left curl */}
      <path
        d="M11.5 9.5
           C 8.5 11, 8.5 14, 10 16
           C 8.5 18, 9 21, 11.5 22.5"
        stroke="url(#recall-mark-light)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Brain hemisphere — right curl (mirror) */}
      <path
        d="M20.5 9.5
           C 23.5 11, 23.5 14, 22 16
           C 23.5 18, 23 21, 20.5 22.5"
        stroke="url(#recall-mark-light)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Central seam — the connecting fold */}
      <path
        d="M16 9 L16 23"
        stroke="url(#recall-mark-light)"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeOpacity="0.7"
      />

      {/* Pivot — the moment of remembering */}
      <circle cx="16" cy="16" r="1.7" fill="url(#recall-mark-light)" />
    </svg>
  );
}
