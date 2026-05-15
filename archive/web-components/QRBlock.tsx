"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Static QR-shaped silhouette. Hand-tuned 17×17 binary grid that
 * reads as a QR code without resolving to actual data — a real QR
 * would need a runtime library, and the silhouette is the point.
 */
function QRCode({ className }: { className?: string }) {
  const size = 17;
  const cells: number[] = [
    0b11111110001111111,
    0b10000010101000001,
    0b10111010111010111,
    0b10111011001010111,
    0b10111010111010111,
    0b10000010100000001,
    0b11111111111111111,
    0b00100110010110100,
    0b11011010101100111,
    0b00110011010101001,
    0b11010100101011110,
    0b00100011001110100,
    0b11111110101011111,
    0b10000010110100100,
    0b10111011011011110,
    0b10111010100110001,
    0b10111011110101011,
  ];

  const rects: React.ReactNode[] = [];
  for (let r = 0; r < size; r++) {
    const row = cells[r] || 0;
    for (let c = 0; c < size; c++) {
      if ((row >> (size - 1 - c)) & 1) {
        rects.push(
          <rect
            key={`${r}-${c}`}
            x={c}
            y={r}
            width={1}
            height={1}
            fill="#16112B"
            rx={0.15}
          />
        );
      }
    }
  }

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      className={className}
      role="img"
      aria-label="Scan to try the launcher"
      shapeRendering="crispEdges"
    >
      {rects}
    </svg>
  );
}

/**
 * Floating QR card — sits at the bottom-right edge of the dashboard
 * mockup. Quiet, single-purpose: a static silhouette + "SCAN TO TRY"
 * caption. No script annotation, no arrow — those would crowd the
 * hero composition the reference is intentionally airy.
 */
export function QRBlock() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease, delay: 0.5 }}
      className="
        rounded-2xl
        bg-bg-base border border-hairline shadow-card
        p-3 flex flex-col items-center gap-1.5
      "
    >
      <QRCode className="w-20 h-20" />
      <div className="text-[9px] font-semibold tracking-[0.18em] text-ink-dim uppercase">
        Scan to try
      </div>
    </motion.div>
  );
}
