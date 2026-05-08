"use client";

import { motion } from "framer-motion";

type Feature = {
  title: string;
  body: string;
  glyph: React.ReactNode;
};

const Glyph = {
  Memory: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2" />
    </svg>
  ),
  Resurface: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M3 12a9 9 0 1 0 3-6.7" />
      <path d="M3 4v5h5" />
    </svg>
  ),
  Lock: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  ),
  Cross: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <path d="M10 6.5h4M10 17.5h4M6.5 10v4M17.5 10v4" />
    </svg>
  ),
  Bolt: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z" strokeLinejoin="round" />
    </svg>
  ),
  Calendar: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M8 3v4M16 3v4M3 10h18" />
    </svg>
  ),
};

const features: Feature[] = [
  {
    title: "Semantic memory retrieval",
    body: "Type what you vaguely remember. Recall finds the meaning, not the filename.",
    glyph: Glyph.Memory,
  },
  {
    title: "Resurfaced ideas",
    body: "Old thoughts return when they're relevant — abandoned concepts come back at the right moment.",
    glyph: Glyph.Resurface,
  },
  {
    title: "Local-first, always",
    body: "Files never leave your device. No cloud, no accounts, no telemetry.",
    glyph: Glyph.Lock,
  },
  {
    title: "Cross-format understanding",
    body: "The same idea lives across notes, code, and PDFs. Recall sees the connection.",
    glyph: Glyph.Cross,
  },
  {
    title: "Instant launcher",
    body: "Press Ctrl + Space anywhere. Type. Open. Like Spotlight, but for ideas.",
    glyph: Glyph.Bolt,
  },
  {
    title: "Weekly memory review",
    body: "A calm digest of what you've been working on — and what older threads might want a second look.",
    glyph: Glyph.Calendar,
  },
];

export function Features() {
  return (
    <section id="features" className="relative py-24 md:py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-2xl mx-auto"
        >
          <div className="text-[11px] font-semibold tracking-[0.18em] text-accent/80 uppercase">
            How Recall thinks
          </div>
          <h2 className="mt-3 text-3xl md:text-5xl font-semibold tracking-tight text-white">
            Memory, not search.
          </h2>
          <p className="mt-5 text-white/55 leading-relaxed">
            Recall doesn't index file names. It indexes meaning, continuity, and
            the ideas that quietly connect your work over time.
          </p>
        </motion.div>

        <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-px rounded-2xl overflow-hidden border border-white/5 bg-white/5">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                duration: 0.7,
                ease: [0.16, 1, 0.3, 1],
                delay: i * 0.04,
              }}
              className="bg-bg p-7 md:p-8"
            >
              <div className="w-9 h-9 rounded-lg flex items-center justify-center text-accent border border-accent/20 bg-accent/5">
                <div className="w-[18px] h-[18px]">{f.glyph}</div>
              </div>
              <h3 className="mt-5 text-white font-semibold tracking-tight">
                {f.title}
              </h3>
              <p className="mt-2 text-sm text-white/55 leading-relaxed">
                {f.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
