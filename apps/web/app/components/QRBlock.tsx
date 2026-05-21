/**
 * QRBlock — the small "scan to try" card that overlaps the launcher
 * mockup's lower-right corner in the hero.
 *
 * The QR is decorative: a deterministic module pattern with three
 * real finder squares. It is not a scannable code (there is no live
 * mobile build to point at yet), so it is aria-hidden. When a real
 * install URL exists, swap in an encoded SVG.
 */

const GRID = 21;

/** Deterministic on/off for a module — no randomness, paint-stable. */
function isFinder(x: number, y: number): boolean {
  const inBox = (bx: number, by: number) =>
    x >= bx && x < bx + 7 && y >= by && y < by + 7;
  return inBox(0, 0) || inBox(GRID - 7, 0) || inBox(0, GRID - 7);
}

function finderModule(x: number, y: number): boolean {
  const local = (bx: number, by: number) => {
    const lx = x - bx;
    const ly = y - by;
    const ring = lx === 0 || lx === 6 || ly === 0 || ly === 6;
    const core = lx >= 2 && lx <= 4 && ly >= 2 && ly <= 4;
    return ring || core;
  };
  if (x < 7 && y < 7) return local(0, 0);
  if (x >= GRID - 7 && y < 7) return local(GRID - 7, 0);
  if (x < 7 && y >= GRID - 7) return local(0, GRID - 7);
  return false;
}

function dataModule(x: number, y: number): boolean {
  return ((x * 7 + y * 13 + x * y * 3) & 5) === 0;
}

export function QRBlock() {
  const modules: { x: number; y: number }[] = [];
  for (let y = 0; y < GRID; y++) {
    for (let x = 0; x < GRID; x++) {
      const on = isFinder(x, y) ? finderModule(x, y) : dataModule(x, y);
      if (on) modules.push({ x, y });
    }
  }

  return (
    <div
      className="
        flex flex-col items-center gap-2
        rounded-2xl bg-bg-base border border-hairline shadow-chip
        p-3.5 w-[124px]
      "
    >
      <svg
        viewBox={`0 0 ${GRID} ${GRID}`}
        className="w-[86px] h-[86px]"
        aria-hidden
        shapeRendering="crispEdges"
      >
        <rect width={GRID} height={GRID} fill="#FFFFFF" />
        {modules.map((m) => (
          <rect
            key={`${m.x}-${m.y}`}
            x={m.x}
            y={m.y}
            width={1}
            height={1}
            fill="#16112B"
          />
        ))}
      </svg>
      <span className="text-[8.5px] font-semibold tracking-[0.2em] text-ink-dim uppercase">
        Scan to try
      </span>
    </div>
  );
}
