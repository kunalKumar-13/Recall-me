"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Step = {
  index: string;
  title: string;
  body: string;
};

const STEPS: Step[] = [
  {
    index: "1",
    title: "It watches locally",
    body:
      "Recall runs in the background and understands your notes, docs, code, and conversations — all on your device.",
  },
  {
    index: "2",
    title: "It understands context",
    body:
      "Our local AI models turn your content into meaning, not just keywords.",
  },
  {
    index: "3",
    title: "You ask naturally",
    body:
      "Ask anything in plain English. Recall finds what you mean.",
  },
  {
    index: "4",
    title: "It brings things back",
    body:
      "Get instant results, previews, and related memories to keep your flow going.",
  },
];

// File-type cards arranged around the central brain. Positions are
// in the diagram's local coordinate space (centered on 0,0).
type Slot = "top" | "right" | "bottom-right" | "bottom-left" | "left";
type TypeCard = {
  label: string;
  slot: Slot;
  glyph: React.ReactNode;
};

const TYPE_GLYPHS = {
  Notes: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 4h11l3 3v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" />
      <path d="M16 4v3h3" />
      <path d="M8 12h8M8 16h6" />
    </svg>
  ),
  Docs: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <path d="M8 8h8M8 12h8M8 16h5" />
    </svg>
  ),
  Code: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 7l-5 5 5 5M15 7l5 5-5 5" />
    </svg>
  ),
  PDFs: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 3h11l3 3v15a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" />
      <path d="M9 12h2.5a1.5 1.5 0 0 1 0 3H9v-3zM14 12h2.5M14 12v3M14 13.5h2.2M16 18h-2v-3" />
    </svg>
  ),
  Chats: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 5h16v11H8l-4 4V5z" />
    </svg>
  ),
};

const TYPE_CARDS: TypeCard[] = [
  { label: "Notes", slot: "top", glyph: TYPE_GLYPHS.Notes },
  { label: "Docs", slot: "right", glyph: TYPE_GLYPHS.Docs },
  { label: "Code", slot: "bottom-right", glyph: TYPE_GLYPHS.Code },
  { label: "PDFs", slot: "bottom-left", glyph: TYPE_GLYPHS.PDFs },
  { label: "Chats", slot: "left", glyph: TYPE_GLYPHS.Chats },
];

// Logical x/y in the diagram coordinate system. Diagram is 380×380.
const SLOT_POS: Record<Slot, { x: number; y: number }> = {
  top: { x: 0, y: -150 },
  right: { x: 145, y: -10 },
  "bottom-right": { x: 105, y: 130 },
  "bottom-left": { x: -105, y: 130 },
  left: { x: -145, y: -10 },
};

function MemoryCoreSmall() {
  return (
    <div
      aria-hidden
      className="relative gpu"
      style={{ width: 96, height: 96 }}
    >
      {/* Outer halo */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(181, 168, 255, 0.45) 0%, transparent 70%)",
        }}
      />
      {/* Core */}
      <div
        className="absolute inset-4 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 35% 30%, rgba(232, 226, 251, 0.95) 0%, rgba(169, 156, 247, 0.95) 40%, rgba(125, 95, 200, 1) 80%)",
          boxShadow:
            "0 0 28px 4px rgba(169, 156, 247, 0.55), inset 0 -6px 12px rgba(80, 60, 150, 0.45)",
        }}
      />
      {/* Highlight pip */}
      <div
        className="absolute"
        style={{
          top: 26,
          left: 26,
          width: 10,
          height: 10,
          borderRadius: 999,
          background:
            "radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0) 70%)",
        }}
      />
    </div>
  );
}

function TypeCardChip({ card, index }: { card: TypeCard; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.5, ease, delay: 0.35 + index * 0.06 }}
      className="
        flex items-center gap-2
        px-3 py-2 rounded-lg
        bg-bg-base border border-hairline shadow-card
        text-ink-bright
      "
      style={{ minWidth: 88 }}
    >
      <div className="w-4 h-4 text-lavender-deep">{card.glyph}</div>
      <div className="text-[12px] font-medium tracking-tight">{card.label}</div>
    </motion.div>
  );
}

/**
 * HowItWorks — left column carries the four numbered steps; right
 * column carries a small memory diagram with the lavender core in
 * the centre and the five content types orbiting around it. The
 * diagram echoes the dark MemoryVisualization further down the page,
 * but here it sits on the cream surface so it reads as a quieter,
 * blueprint-style version of the same idea.
 */
export function HowItWorks() {
  return (
    <section
      id="how"
      className="relative pt-24 md:pt-32 pb-24 md:pb-28 px-5 md:px-8"
    >
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* ── Left: numbered steps ─────────────────────────── */}
          <div className="lg:col-span-6">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease }}
              className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
            >
              How it works
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease, delay: 0.06 }}
              className="font-editorial mt-3 text-[30px] md:text-[40px] font-medium tracking-editorial text-ink-bright leading-[1.05]"
            >
              Your memory layer in{" "}
              <span className="italic">4 steps.</span>
            </motion.h2>

            <ol className="mt-10 space-y-7">
              {STEPS.map((s, i) => (
                <motion.li
                  key={s.index}
                  initial={{ opacity: 0, y: 8 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.5, ease, delay: 0.1 + i * 0.05 }}
                  className="flex items-start gap-4"
                >
                  <div
                    className="
                      shrink-0 w-7 h-7 rounded-full
                      flex items-center justify-center
                      bg-lavender-soft text-lavender-deep
                      text-[12px] font-semibold
                    "
                  >
                    {s.index}
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-[15.5px] font-semibold text-ink-bright tracking-tight">
                      {s.title}
                    </h3>
                    <p className="mt-1 text-[13.5px] text-ink leading-relaxed max-w-md">
                      {s.body}
                    </p>
                  </div>
                </motion.li>
              ))}
            </ol>
          </div>

          {/* ── Right: memory diagram with type chips ────────── */}
          <div className="lg:col-span-6">
            <div
              className="relative mx-auto"
              style={{ maxWidth: 420, height: 400 }}
            >
              {/* Soft blueprint-style outer ring + spokes */}
              <svg
                className="absolute inset-0 w-full h-full pointer-events-none"
                viewBox="-200 -200 400 400"
                preserveAspectRatio="xMidYMid meet"
                aria-hidden
              >
                {/* outer ring */}
                <motion.circle
                  cx={0}
                  cy={0}
                  r={170}
                  fill="none"
                  stroke="rgba(169, 156, 247, 0.20)"
                  strokeWidth={0.8}
                  strokeDasharray="2 4"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.6, ease, delay: 0.2 }}
                />
                {/* connection threads to each type card */}
                {TYPE_CARDS.map((c, i) => {
                  const p = SLOT_POS[c.slot];
                  return (
                    <motion.line
                      key={c.label}
                      x1={0}
                      y1={0}
                      x2={p.x}
                      y2={p.y}
                      stroke="rgba(169, 156, 247, 0.30)"
                      strokeWidth={0.7}
                      strokeLinecap="round"
                      initial={{ pathLength: 0, opacity: 0 }}
                      whileInView={{ pathLength: 1, opacity: 0.7 }}
                      viewport={{ once: true, margin: "-80px" }}
                      transition={{
                        duration: 0.7,
                        ease,
                        delay: 0.3 + i * 0.05,
                      }}
                    />
                  );
                })}
              </svg>

              {/* Centred core */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                <motion.div
                  initial={{ opacity: 0, scale: 0.85 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.7, ease }}
                >
                  <MemoryCoreSmall />
                </motion.div>
              </div>

              {/* Type chips */}
              {TYPE_CARDS.map((c, i) => {
                const p = SLOT_POS[c.slot];
                // Offsets to centre the chip on the line endpoint.
                // Chip is roughly 100×34, so subtract half each.
                const dx = p.x - 50;
                const dy = p.y - 17;
                return (
                  <div
                    key={c.label}
                    className="absolute"
                    style={{
                      top: "50%",
                      left: "50%",
                      transform: `translate(${dx}px, ${dy}px)`,
                    }}
                  >
                    <TypeCardChip card={c} index={i} />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
