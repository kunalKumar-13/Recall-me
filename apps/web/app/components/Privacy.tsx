"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Point = { title: string; body: string; glyph: React.ReactNode };

const pg = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

// Phase 6G — the directive's five-point trust statement. Mirrors
// `docs/engineering/TRUST_LEDGER.md`: local only · no cloud · no
// telemetry · counts only · export only. Order is from broadest
// (the boundary itself) to most specific (what the user can take
// with them when they leave).
const POINTS: Point[] = [
  {
    title: "Local only",
    body: "Capture, processing, and recovery all happen on this device. There is no remote engine.",
    glyph: (
      <svg viewBox="0 0 24 24" {...pg}>
        <rect x="3" y="4" width="18" height="13" rx="2" />
        <path d="M8 21h8M12 17v4" />
      </svg>
    ),
  },
  {
    title: "No cloud",
    body: "Recall never stores, syncs, or backs up your data to a remote service.",
    glyph: (
      <svg viewBox="0 0 24 24" {...pg}>
        <path d="M6.5 18A4 4 0 0 1 6 10.1 6 6 0 0 1 16.4 7.6" />
        <path d="M19 14.5A3.5 3.5 0 0 0 17.5 18H9" />
        <path d="M3 3l18 18" />
      </svg>
    ),
  },
  {
    title: "No telemetry",
    body: "Zero tracking, zero analytics, zero usage pings — even \"anonymous\" ones.",
    glyph: (
      <svg viewBox="0 0 24 24" {...pg}>
        <path d="M12 3l7.5 3v5.5c0 5-3.4 8.3-7.5 9.5-4.1-1.2-7.5-4.5-7.5-9.5V6z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    ),
  },
  {
    title: "Counts only",
    body: "If you ever share stats with us, they're counts (recoveries shown / accepted). Never the work itself.",
    glyph: (
      <svg viewBox="0 0 24 24" {...pg}>
        <path d="M4 19V5M9 19V9M14 19v-7M19 19v-4" />
      </svg>
    ),
  },
  {
    title: "Export only",
    body: "Every artifact on disk is plain JSON. `recall stats --export` puts your own data in your hands; deleting `~/.recall/` is a full reset.",
    glyph: (
      <svg viewBox="0 0 24 24" {...pg}>
        <path d="M12 3v12M7 8l5-5 5 5" />
        <path d="M5 21h14" />
      </svg>
    ),
  },
];

export function Privacy() {
  return (
    <section id="privacy" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          {/* ── Left: copy + points ─────────────────────────────── */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.55, ease }}
            >
              <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
                Trust
              </div>
              <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
                Your memory <span className="italic">never</span>
                <br />
                leaves your device.
              </h2>
              <p className="mt-5 text-ink leading-relaxed text-[15px] max-w-md">
                Recall is built on a simple promise: your memory is yours,
                always. The loopback bind is the boundary — there is no
                account to create and no server to trust. The five rules
                below are not aspiration; they are the on-disk contract.
              </p>
            </motion.div>

            <div className="mt-9 grid grid-cols-1 sm:grid-cols-2 gap-6">
              {POINTS.map((p, i) => (
                <motion.div
                  key={p.title}
                  initial={{ opacity: 0, y: 8 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.5, ease, delay: i * 0.06 }}
                  className="flex gap-3.5"
                >
                  <span className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-lavender-deep border border-lavender/25 bg-lavender/[0.06]">
                    <span className="w-[17px] h-[17px]">{p.glyph}</span>
                  </span>
                  <span>
                    <span className="block text-[14px] font-semibold text-ink-bright">
                      {p.title}
                    </span>
                    <span className="block mt-0.5 text-[12.5px] text-ink leading-relaxed">
                      {p.body}
                    </span>
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* ── Right: shield card ──────────────────────────────── */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.65, ease, delay: 0.1 }}
              className="
                relative rounded-3xl overflow-hidden
                bg-bg-base border border-hairline shadow-card
                px-8 py-12 text-center
              "
            >
              <div
                aria-hidden
                className="absolute left-1/2 -translate-x-1/2 top-6 w-[280px] h-[280px] pointer-events-none"
                style={{
                  background:
                    "radial-gradient(circle, rgba(169,156,247,0.16) 0%, transparent 65%)",
                }}
              />
              <div className="relative inline-flex items-center justify-center w-28 h-28 rounded-3xl bg-lavender-gradient shadow-lift">
                <svg viewBox="0 0 24 24" className="w-12 h-12" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3l7.5 3v5.5c0 5-3.4 8.3-7.5 9.5-4.1-1.2-7.5-4.5-7.5-9.5V6z" />
                  <rect x="9" y="11" width="6" height="5" rx="1" />
                  <path d="M10.3 11V9.7a1.7 1.7 0 0 1 3.4 0V11" />
                </svg>
              </div>
              <h3 className="relative mt-7 font-editorial text-[24px] md:text-[26px] font-medium tracking-editorial text-ink-bright leading-tight">
                Private by default.
                <br />
                <span className="italic">Private by design.</span>
              </h3>
              <p className="relative mt-3 text-[12.5px] font-mono text-ink-dim">
                127.0.0.1:4545 · ~/.recall · MIT
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
