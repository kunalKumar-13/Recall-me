/**
 * The Recall mark: one thread finding its node. Drawn, not iconed —
 * the same gesture the product makes when it hands your work back.
 */
export function Mark({ size = 22 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 28"
      fill="none"
      aria-hidden
      className="mark"
    >
      <path
        d="M3 20.5 C 9 4.5, 13.5 25, 19.5 12.5 S 24.5 8.5, 24.6 8.4"
        stroke="var(--red)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="24.4" cy="8.2" r="3" fill="var(--red)" />
    </svg>
  );
}
