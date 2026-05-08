/**
 * Atmospheric background — three soft, blurred orbs floating behind the
 * page. Server component (no JS shipped). Pointer events disabled so it
 * never intercepts clicks.
 */
export function AmbientBackground() {
  return (
    <div
      aria-hidden
      className="fixed inset-0 -z-10 overflow-hidden pointer-events-none"
    >
      {/* Top-left accent orb (the brand blue) */}
      <div
        className="absolute -top-[20%] -left-[10%] w-[640px] h-[640px] rounded-full blur-[140px]"
        style={{ background: "rgba(124, 140, 255, 0.10)" }}
      />
      {/* Mid-right violet orb */}
      <div
        className="absolute top-[28%] -right-[12%] w-[520px] h-[520px] rounded-full blur-[140px]"
        style={{ background: "rgba(139, 92, 246, 0.08)" }}
      />
      {/* Lower cyan orb — deepest, faintest */}
      <div
        className="absolute bottom-[8%] left-[18%] w-[420px] h-[420px] rounded-full blur-[120px]"
        style={{ background: "rgba(6, 182, 212, 0.05)" }}
      />
    </div>
  );
}
