"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Memory visualization — the page's single dark moment.
 *
 * A small lavender memory-core glows at the centre; four file-typed
 * cards orbit at the corners; thin SVG threads tie the cards back to
 * the core. The composition is deliberately compact — the previous
 * version's giant brain read as "AI startup", and the brief asked
 * for an intimate "ideas becoming connected" feel instead.
 *
 * Performance contract:
 *   • Core uses layered radial-gradients only — no `filter: blur`,
 *     no shaders, no canvas. Glow is paint-once.
 *   • Orbit motion is pure transform + opacity, GPU-accelerated.
 *   • Connection lines use SVG `pathLength` so the draw-on stays on
 *     the compositor.
 *   • Each card carries a single one-shot enter animation; nothing
 *     loops aggressively.
 */

type CardSlot = "tl" | "tr" | "bl" | "br";

type MemoryCard = {
  title: string;
  date: string;
  slot: CardSlot;
};

const CARDS: MemoryCard[] = [
  { title: "User Interview", date: "Apr 28, 2024", slot: "tl" },
  { title: "Competitor Analysis", date: "May 03, 2024", slot: "tr" },
  { title: "API Integration", date: "Feb 19, 2024", slot: "bl" },
  { title: "Design System", date: "Apr 02, 2024", slot: "br" },
];

// Card positions are expressed in the SVG's coordinate system so the
// lines + cards share a single source of truth. The container is
// 720×480 logical units; cards are placed near the corners.
const SLOT_POS: Record<CardSlot, { x: number; y: number }> = {
  tl: { x: -260, y: -120 },
  tr: { x: 260, y: -120 },
  bl: { x: -240, y: 130 },
  br: { x: 240, y: 130 },
};

function MemoryCore() {
  // Static composition. Two radial gradients (halo + orb) plus a
  // small specular pip. The previous version stacked three gradients
  // and rotated a conic glint; both read as "something is loading"
  // rather than "something is alive". Restraint reads as trust.
  return (
    <div
      aria-hidden
      className="relative gpu"
      style={{ width: 188, height: 188 }}
    >
      {/* Halo */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(181, 168, 255, 0.42) 0%, transparent 68%)",
        }}
      />
      {/* Orb */}
      <div
        className="absolute inset-12 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 35% 30%, rgba(232, 226, 251, 0.95) 0%, rgba(169, 156, 247, 0.95) 38%, rgba(125, 95, 200, 1) 78%)",
          boxShadow:
            "0 0 32px 2px rgba(169, 156, 247, 0.45), inset 0 -8px 14px rgba(80, 60, 150, 0.5)",
        }}
      />
      {/* Specular highlight */}
      <div
        className="absolute"
        style={{
          top: 60,
          left: 60,
          width: 14,
          height: 14,
          borderRadius: 999,
          background:
            "radial-gradient(circle, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0) 70%)",
        }}
      />
    </div>
  );
}

function FloatingCard({ card, index }: { card: MemoryCard; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, ease, delay: 0.3 + index * 0.08 }}
      className="
        rounded-xl px-3 py-2.5 flex items-start gap-2.5
        border
      "
      style={{
        width: 184,
        background: "rgba(28, 30, 44, 0.85)",
        borderColor: "rgba(181, 168, 255, 0.20)",
        boxShadow: "0 8px 32px -12px rgba(0, 0, 0, 0.55)",
      }}
    >
      <div
        className="shrink-0 w-7 h-7 rounded-md flex items-center justify-center"
        style={{
          background: "rgba(181, 168, 255, 0.15)",
          border: "1px solid rgba(181, 168, 255, 0.25)",
        }}
      >
        <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="#D4CCFF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 4h11l3 3v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" />
          <path d="M16 4v3h3" />
        </svg>
      </div>
      <div className="min-w-0">
        <div className="text-[12.5px] font-medium text-white truncate tracking-tight">
          {card.title}
        </div>
        <div className="text-[10px] text-white/45 truncate mt-0.5">
          {card.date}
        </div>
      </div>
    </motion.div>
  );
}

export function MemoryVisualization() {
  return (
    <section
      id="memory-visualization"
      className="
        relative overflow-hidden
        py-24 md:py-32 px-5 md:px-8
        bg-[#0A0B12]
      "
    >
      {/* Soft cinematic top glow — calmed (alpha 0.16 → 0.10) so the
          memory core itself carries the warmth instead of the
          surrounding wash. The cyan side-light is removed entirely —
          two competing washes were too much for one section. */}
      <div
        aria-hidden
        className="absolute inset-x-0 top-0 h-[55%] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 75% at 50% 0%, rgba(181, 168, 255, 0.10), transparent 70%)",
        }}
      />

      <div className="relative max-w-5xl mx-auto">
        {/* Heading */}
        <div className="text-center mb-14 md:mb-16">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, ease }}
            className="text-[10.5px] font-semibold tracking-[0.20em] uppercase"
            style={{ color: "#B5A8FF" }}
          >
            One graph, on your machine
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease, delay: 0.06 }}
            className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial leading-[1.06] text-white"
          >
            Your ideas. Connected.
            <br />
            <span className="italic">Always within reach.</span>
          </motion.h2>
        </div>

        {/* Stage — fixed-aspect canvas with the core + cards + lines */}
        <div className="relative mx-auto" style={{ maxWidth: 720, height: 420 }}>
          {/* Connection lines, drawn first so cards layer on top */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox="-360 -210 720 420"
            preserveAspectRatio="xMidYMid meet"
            aria-hidden
          >
            {CARDS.map((c, i) => {
              const p = SLOT_POS[c.slot];
              return (
                <motion.line
                  key={c.title}
                  x1={0}
                  y1={0}
                  x2={p.x}
                  y2={p.y}
                  stroke="rgba(181, 168, 255, 0.30)"
                  strokeWidth={0.8}
                  strokeLinecap="round"
                  initial={{ pathLength: 0, opacity: 0 }}
                  whileInView={{ pathLength: 1, opacity: 0.6 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{
                    duration: 0.85,
                    ease,
                    delay: 0.3 + i * 0.08,
                  }}
                />
              );
            })}
          </svg>

          {/* Memory core — dead centre */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <motion.div
              initial={{ opacity: 0, scale: 0.85 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.8, ease, delay: 0.1 }}
            >
              <MemoryCore />
            </motion.div>
          </div>

          {/* Cards — positioned from slot mapping. Translated so the
              card's top-left lands at the SVG line endpoint. */}
          {CARDS.map((c, i) => {
            const p = SLOT_POS[c.slot];
            // Approximate offset that centers each 184×~50 card at p
            const dx = p.x - 92;
            const dy = p.y - 22;
            return (
              <div
                key={c.title}
                className="absolute"
                style={{
                  top: "50%",
                  left: "50%",
                  transform: `translate(${dx}px, ${dy}px)`,
                }}
              >
                <FloatingCard card={c} index={i} />
              </div>
            );
          })}
        </div>

        {/* Caption */}
        <motion.p
          initial={{ opacity: 0, y: 6 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.55, ease, delay: 0.6 }}
          className="
            mt-14 md:mt-16 text-center
            text-[14px] md:text-[15px] text-white/65 leading-relaxed
            max-w-xl mx-auto
          "
        >
          Recall connects the dots across your digital world —
          <br className="hidden md:inline" />
          so you can think bigger and create faster.
        </motion.p>
      </div>
    </section>
  );
}
