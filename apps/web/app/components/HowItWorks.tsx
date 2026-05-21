"use client";

import { motion } from "framer-motion";
import { Logo } from "./Logo";

const ease = [0.32, 0.72, 0, 1] as const;

type Step = { title: string; body: string };

const STEPS: Step[] = [
  {
    title: "It captures while you work",
    body:
      "Recall quietly notes the files, tabs, and chats you touch as you go. No buttons, nothing to remember to save — and nothing leaves your machine.",
  },
  {
    title: "It rebuilds the context",
    body:
      "Those moments fold into sessions and investigations — the unit you actually remember. “The websocket bug,” not forty separate tab opens.",
  },
  {
    title: "You ask in a half-thought",
    body:
      "Press Ctrl + Space and describe what you were doing — no keywords, no query syntax. Recall finds the investigation you mean.",
  },
  {
    title: "You re-enter the work",
    body:
      "One click reopens the files, tabs, and chats from that investigation in order. You step back into flow instead of reconstructing it.",
  },
];

type Orbiter = { label: string; glyph: React.ReactNode };

const og = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const ORBITERS: Orbiter[] = [
  {
    label: "Notes",
    glyph: (
      <svg viewBox="0 0 24 24" {...og}>
        <path d="M6 3h9l5 5v13H6z" />
        <path d="M14 3v6h6M9 13h7M9 17h7" />
      </svg>
    ),
  },
  {
    label: "Chats",
    glyph: (
      <svg viewBox="0 0 24 24" {...og}>
        <path d="M4 5h16v11H9l-5 4z" />
        <path d="M8 9h8M8 12h5" />
      </svg>
    ),
  },
  {
    label: "Docs",
    glyph: (
      <svg viewBox="0 0 24 24" {...og}>
        <path d="M7 3h7l4 4v14H7z" />
        <path d="M13 3v5h5" />
      </svg>
    ),
  },
  {
    label: "Code",
    glyph: (
      <svg viewBox="0 0 24 24" {...og}>
        <path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13 5l-2 14" />
      </svg>
    ),
  },
  {
    label: "PDFs",
    glyph: (
      <svg viewBox="0 0 24 24" {...og}>
        <path d="M7 3h8l4 4v14H7z" />
        <path d="M9 14h2M9 17h6M9 11h2" />
      </svg>
    ),
  },
];

/** Five orbiters evenly spaced on a circle, first one at the top. */
function orbitPosition(i: number, total: number): { x: string; y: string } {
  const angle = (-90 + (360 / total) * i) * (Math.PI / 180);
  const r = 41;
  return {
    x: `${50 + r * Math.cos(angle)}%`,
    y: `${50 + r * Math.sin(angle)}%`,
  };
}

export function HowItWorks() {
  return (
    <section id="how" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
            How it works
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Your continuity layer
            <br />
            <span className="italic">in four steps.</span>
          </h2>
        </motion.div>

        <div className="mt-12 md:mt-14 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* ── Steps ────────────────────────────────────────────── */}
          <ol className="lg:col-span-6 space-y-6">
            {STEPS.map((s, i) => (
              <motion.li
                key={s.title}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, ease, delay: i * 0.06 }}
                className="flex gap-4"
              >
                <span
                  className="
                    shrink-0 w-8 h-8 rounded-full
                    flex items-center justify-center
                    bg-lavender-soft text-lavender-deep
                    text-[13px] font-semibold
                  "
                >
                  {i + 1}
                </span>
                <span>
                  <span className="block text-[15.5px] font-semibold text-ink-bright">
                    {s.title}
                  </span>
                  <span className="block mt-1 text-[13.5px] text-ink leading-relaxed max-w-md">
                    {s.body}
                  </span>
                </span>
              </motion.li>
            ))}
          </ol>

          {/* ── Orbit diagram ───────────────────────────────────── */}
          <div className="lg:col-span-6 flex justify-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, ease }}
              className="relative w-[300px] h-[300px] sm:w-[360px] sm:h-[360px]"
            >
              {/* Orbit rings */}
              <div className="absolute inset-0 rounded-full border border-hairline" />
              <div className="absolute inset-[16%] rounded-full border border-dashed border-hairline" />

              {/* Connector lines */}
              <svg
                viewBox="0 0 100 100"
                className="absolute inset-0 w-full h-full"
                aria-hidden
              >
                {ORBITERS.map((_, i) => {
                  const angle = (-90 + (360 / ORBITERS.length) * i) * (Math.PI / 180);
                  return (
                    <line
                      key={i}
                      x1="50"
                      y1="50"
                      x2={50 + 41 * Math.cos(angle)}
                      y2={50 + 41 * Math.sin(angle)}
                      stroke="rgba(169,156,247,0.3)"
                      strokeWidth="0.5"
                    />
                  );
                })}
              </svg>

              {/* Center node */}
              <div
                className="
                  absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2
                  w-[88px] h-[88px] rounded-2xl
                  flex items-center justify-center
                  bg-bg-base border border-hairline shadow-card
                "
              >
                <Logo className="w-9 h-9" />
              </div>

              {/* Orbiters */}
              {ORBITERS.map((o, i) => {
                const pos = orbitPosition(i, ORBITERS.length);
                return (
                  <div
                    key={o.label}
                    className="absolute -translate-x-1/2 -translate-y-1/2"
                    style={{ left: pos.x, top: pos.y }}
                  >
                    <div
                      className="
                        flex flex-col items-center gap-1
                        w-[72px]
                      "
                    >
                      <span
                        className="
                          w-11 h-11 rounded-xl
                          flex items-center justify-center
                          bg-bg-base border border-hairline shadow-chip
                          text-lavender-deep
                        "
                      >
                        <span className="w-[18px] h-[18px]">{o.glyph}</span>
                      </span>
                      <span className="text-[10.5px] font-medium text-ink-dim">
                        {o.label}
                      </span>
                    </div>
                  </div>
                );
              })}
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
