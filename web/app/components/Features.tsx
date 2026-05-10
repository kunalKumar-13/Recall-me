"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Feature = {
  title: string;
  body: string;
  glyph: React.ReactNode;
};

const Glyph = {
  Search: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="M20 20l-4.5-4.5" />
    </svg>
  ),
  Lock: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  ),
  Eye: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
  Layers: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l9 5-9 5-9-5 9-5z" />
      <path d="M3 13l9 5 9-5" />
      <path d="M3 17l9 5 9-5" />
    </svg>
  ),
  Network: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6" cy="7" r="2.2" />
      <circle cx="18" cy="6" r="2.2" />
      <circle cx="12" cy="17" r="2.2" />
      <path d="M7.7 8.5l3.2 6.7M16.5 7.6l-3.4 7.5" />
    </svg>
  ),
  Globe: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a13 13 0 0 1 0 18M12 3a13 13 0 0 0 0 18" />
    </svg>
  ),
};

const FEATURES: Feature[] = [
  {
    title: "AI Memory Search",
    body:
      "Search your notes, docs, code, and conversations using natural language. Recall understands meaning, not just keywords.",
    glyph: Glyph.Search,
  },
  {
    title: "Local & Private",
    body:
      "Everything stays on your device. No cloud. No telemetry. No data leaves your machine. Ever.",
    glyph: Glyph.Lock,
  },
  {
    title: "Smart Previews",
    body:
      "Get instant previews and excerpts so you can find the right memory without opening every file.",
    glyph: Glyph.Eye,
  },
  {
    title: "Auto Memory Layer",
    body:
      "Recall continuously indexes your content in the background so your memories are always just a search away.",
    glyph: Glyph.Layers,
  },
  {
    title: "Related Memories",
    body:
      "Recall surfaces connected ideas and related context to help you think deeper and faster.",
    glyph: Glyph.Network,
  },
  {
    title: "Works Everywhere",
    body:
      "Supports notes, docs, code, PDFs, spreadsheets, chats, and more — all in one place.",
    glyph: Glyph.Globe,
  },
];

/**
 * Features — 2 × 3 grid of self-contained white cards. Each card has
 * a lavender-tinted icon chip, a tight heading, and a short body.
 * The grid is hairline-separated rather than card-bordered so the
 * surface reads as one unified panel even at large widths.
 */
export function Features() {
  return (
    <section id="features" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase">
            Features
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Built for deep thinkers
            <br />
            who hate <span className="italic">forgetting.</span>
          </h2>
          <p className="mt-5 text-ink leading-relaxed text-[15px] max-w-md">
            Recall runs locally and privately on your device, giving you
            superpowers for your digital memory.
          </p>
        </motion.div>

        <div
          className="
            mt-12 md:mt-14
            grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
            gap-px rounded-2xl overflow-hidden
            border border-hairline
            bg-hairline shadow-card
          "
        >
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, ease, delay: i * 0.04 }}
              className="
                group relative p-7 md:p-8
                bg-bg-base
                hover:bg-bg-raised
                transition-colors duration-500
              "
            >
              <div
                className="
                  w-10 h-10 rounded-xl flex items-center justify-center
                  text-lavender-deep
                  border border-lavender/25 bg-lavender/[0.06]
                  group-hover:border-lavender/40 group-hover:bg-lavender/[0.10]
                  transition-colors duration-500
                "
              >
                <div className="w-[18px] h-[18px]">{f.glyph}</div>
              </div>

              <h3 className="mt-5 text-ink-bright font-semibold tracking-tight text-[16px]">
                {f.title}
              </h3>
              <p className="mt-2 text-[13.5px] text-ink leading-relaxed">
                {f.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
