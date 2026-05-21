"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Node = {
  label: string;
  date: string;
  /** Position in the panel, as a percentage. */
  x: number;
  y: number;
};

const NODES: Node[] = [
  { label: "User Research", date: "Apr 28", x: 20, y: 26 },
  { label: "Competitor Analysis", date: "Mar 03", x: 80, y: 22 },
  { label: "API Integration", date: "Feb 18", x: 18, y: 76 },
  { label: "Design System", date: "Apr 02", x: 82, y: 74 },
];

/**
 * ThreadConstellation — the mid-page visualization.
 *
 * Replaces the earlier "memory orb" concept. There is deliberately no
 * brain, no neural imagery, no glow bloom — the charter rules those
 * out. What is shown is what the engine actually produces: discrete
 * memory threads (labeled cards) linked to one continuity hub by
 * plain hairlines. A node graph, not a metaphor.
 *
 * The dark panel reuses the `.topology-card` surface so it reads as
 * the same family as the local-first section.
 */
export function ThreadConstellation() {
  return (
    <section className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="text-center max-w-2xl mx-auto"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
            Investigations
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Your investigations, connected.
            <br />
            <span className="italic">Always within reach.</span>
          </h2>
        </motion.div>

        {/* ── Dark constellation panel ──────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, ease, delay: 0.1 }}
          className="
            relative mt-12 md:mt-14
            rounded-3xl overflow-hidden topology-card
            px-6 md:px-10 pt-10 pb-9
          "
        >
          <div className="relative h-[320px] sm:h-[380px]">
            {/* Connector lines */}
            <svg
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              className="absolute inset-0 w-full h-full"
              aria-hidden
            >
              {NODES.map((n) => (
                <line
                  key={n.label}
                  x1="50"
                  y1="50"
                  x2={n.x}
                  y2={n.y}
                  stroke="rgba(169,156,247,0.35)"
                  strokeWidth="0.4"
                />
              ))}
            </svg>

            {/* Center hub */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
              <div
                className="
                  w-[104px] h-[104px] rounded-full
                  flex items-center justify-center
                  border border-lavender/40
                "
                style={{
                  background:
                    "radial-gradient(circle, rgba(169,156,247,0.22) 0%, rgba(169,156,247,0.04) 70%)",
                }}
              >
                <div className="w-11 h-11 rounded-full bg-lavender-gradient flex items-center justify-center">
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="6" cy="7" r="2.4" />
                    <circle cx="18" cy="17" r="2.4" />
                    <path d="M6 9.4v2.6A4 4 0 0 0 10 16h5.6" />
                  </svg>
                </div>
              </div>
              <div className="mt-2 text-[10px] font-semibold tracking-[0.16em] uppercase text-lavender">
                Continuity
              </div>
            </div>

            {/* Thread cards */}
            {NODES.map((n, i) => (
              <motion.div
                key={n.label}
                initial={{ opacity: 0, scale: 0.92 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, ease, delay: 0.15 + i * 0.08 }}
                className="absolute -translate-x-1/2 -translate-y-1/2"
                style={{ left: `${n.x}%`, top: `${n.y}%` }}
              >
                <div
                  className="
                    flex items-center gap-2.5
                    rounded-xl px-3 py-2.5
                    border border-white/10
                  "
                  style={{ background: "rgba(255,255,255,0.05)" }}
                >
                  <span className="w-7 h-7 shrink-0 rounded-lg bg-white/[0.07] border border-white/10 flex items-center justify-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-lavender" />
                  </span>
                  <span>
                    <span className="block text-[12px] font-medium text-white/90 whitespace-nowrap">
                      {n.label}
                    </span>
                    <span className="block text-[9.5px] font-mono text-white/40">
                      {n.date}
                    </span>
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          <p className="relative mt-2 text-center text-[13px] text-white/55 leading-relaxed max-w-xl mx-auto">
            Recall links the moments behind your work so a half-remembered
            investigation comes back whole — files, tabs, and chats, in
            sequence.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
