"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Audience = { label: string; glyph: React.ReactNode };

const g = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const AUDIENCES: Audience[] = [
  {
    label: "Researchers",
    glyph: (
      <svg viewBox="0 0 24 24" {...g}>
        <circle cx="10.5" cy="10.5" r="6.5" />
        <path d="M20 20l-4.5-4.5" />
      </svg>
    ),
  },
  {
    label: "Developers",
    glyph: (
      <svg viewBox="0 0 24 24" {...g}>
        <path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13 5l-2 14" />
      </svg>
    ),
  },
  {
    label: "Founders",
    glyph: (
      <svg viewBox="0 0 24 24" {...g}>
        <path d="M13 3L4 14h6l-1 7 9-11h-6z" />
      </svg>
    ),
  },
  {
    label: "Students",
    glyph: (
      <svg viewBox="0 0 24 24" {...g}>
        <path d="M3 8.5L12 4l9 4.5L12 13z" />
        <path d="M7 10.5V16c0 1.5 2.5 3 5 3s5-1.5 5-3v-5.5" />
      </svg>
    ),
  },
  {
    label: "Writers",
    glyph: (
      <svg viewBox="0 0 24 24" {...g}>
        <path d="M4 20l4-1L19 8a2.5 2.5 0 0 0-3.5-3.5L4.5 15.5z" />
        <path d="M14 6l4 4" />
      </svg>
    ),
  },
];

/**
 * TrustedBy — a quiet strip of audience pills between the hero and
 * the "how it works" section. No logos (the project has none and the
 * charter forbids fake social proof) — just the kinds of thinkers the
 * continuity layer is built for.
 */
export function TrustedBy() {
  return (
    <section className="relative px-5 md:px-8 py-10 md:py-12 border-y border-hairline">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, ease }}
          className="flex flex-col md:flex-row md:items-center gap-5 md:gap-8"
        >
          <div className="text-[10px] font-semibold tracking-[0.2em] text-ink-dim uppercase shrink-0">
            Built for thinkers &amp; builders
          </div>
          <div className="flex flex-wrap items-center gap-2.5">
            {AUDIENCES.map((a, i) => (
              <motion.span
                key={a.label}
                initial={{ opacity: 0, y: 6 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.45, ease, delay: i * 0.05 }}
                className="
                  inline-flex items-center gap-2
                  h-9 px-3.5 rounded-full
                  border border-hairline bg-bg-base
                  text-[12.5px] text-ink
                "
              >
                <span className="w-[15px] h-[15px] text-lavender-deep">
                  {a.glyph}
                </span>
                {a.label}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
