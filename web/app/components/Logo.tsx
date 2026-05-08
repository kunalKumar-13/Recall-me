type LogoProps = {
  className?: string;
};

/** Same R-on-purple identity as the desktop tray icon. */
export function Logo({ className }: LogoProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      role="img"
      aria-label="Recall"
    >
      <rect x="2" y="2" width="28" height="28" rx="8" fill="#7c8cff" />
      <text
        x="16"
        y="22"
        textAnchor="middle"
        fontSize="16"
        fontWeight="700"
        fill="#fff"
        style={{ fontFamily: "ui-sans-serif, system-ui, sans-serif" }}
      >
        R
      </text>
    </svg>
  );
}
