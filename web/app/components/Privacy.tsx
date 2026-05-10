"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Pledge = {
  title: string;
  body: string;
  glyph: React.ReactNode;
};

const PLEDGES: Pledge[] = [
  {
    title: "100% Local",
    body: "All data and AI processing happens on your device.",
    glyph: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3l8 3v6c0 4.5-3.4 8.4-8 9-4.6-.6-8-4.5-8-9V6l8-3z" />
        <path d="M9.5 12l1.7 1.7L15 10.5" />
      </svg>
    ),
  },
  {
    title: "No Cloud",
    body: "We don't store, sync, or backup your data.",
    glyph: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4l16 16" />
        <path d="M17.5 17.5h-12a4 4 0 0 1-.5-7.96A6 6 0 0 1 16 8" />
      </svg>
    ),
  },
  {
    title: "No Telemetry",
    body: "No tracking. No analytics. No usage data.",
    glyph: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 3l18 18" />
        <path d="M10.6 5.2A11 11 0 0 1 12 5c5 0 9 4 10 7-.5 1.4-1.6 3-3.2 4.3" />
        <path d="M6.2 6.2C4 7.6 2.6 9.6 2 12c1 3 5 7 10 7 1.5 0 2.9-.4 4.2-1" />
      </svg>
    ),
  },
  {
    title: "Open & Transparent",
    body: "Open source and community audited.",
    glyph: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 7l-5 5 5 5M15 7l5 5-5 5" />
      </svg>
    ),
  },
];

function ShieldArt() {
  return (
    <div
      aria-hidden
      className="
        relative w-full max-w-[300px] aspect-square mx-auto
        rounded-[28px]
        bg-bg-base border border-hairline shadow-card
        flex items-center justify-center
        overflow-hidden
      "
    >
      {/* Soft top wash inside the card */}
      <div
        className="absolute -inset-x-10 -top-10 h-40 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(169, 156, 247, 0.18) 0%, transparent 70%)",
        }}
      />
      {/* Shield glyph — gradient-filled with soft shadow */}
      <svg
        viewBox="0 0 96 96"
        className="relative w-32 h-32"
        aria-hidden
      >
        <defs>
          <linearGradient id="shield-fill" x1="0" y1="0" x2="0" y2="96" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#C5B4FA" />
            <stop offset="1" stopColor="#8B7FE3" />
          </linearGradient>
          <linearGradient id="shield-shine" x1="0" y1="0" x2="0" y2="96" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="white" stopOpacity="0.55" />
            <stop offset="1" stopColor="white" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d="M48 8 L82 22 V46
             C82 65, 67 80, 48 86
             C29 80, 14 65, 14 46 V22 Z"
          fill="url(#shield-fill)"
        />
        <path
          d="M48 8 L82 22 V46
             C82 56, 75 64, 48 64
             C21 64, 14 56, 14 46 V22 Z"
          fill="url(#shield-shine)"
          opacity="0.4"
        />
        {/* Lock body */}
        <rect x="36" y="42" width="24" height="20" rx="3" fill="white" opacity="0.95" />
        {/* Lock shackle */}
        <path
          d="M40 42 V36 a8 8 0 0 1 16 0 V42"
          fill="none"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
        />
        {/* Keyhole */}
        <circle cx="48" cy="50" r="2.4" fill="#8B7FE3" />
        <rect x="46.6" y="50" width="2.8" height="6" rx="1" fill="#8B7FE3" />
      </svg>
    </div>
  );
}

export function Privacy() {
  return (
    <section id="privacy" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* ── Left: copy + pledges ──────────────────────────── */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease }}
              className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
            >
              Privacy
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease, delay: 0.06 }}
              className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]"
            >
              Your data <span className="italic">never</span>
              <br />
              leaves your device.
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease, delay: 0.12 }}
              className="mt-5 text-ink leading-relaxed text-[15px] max-w-lg"
            >
              Recall is built on a simple promise: your data is yours, always.
            </motion.p>

            <ul className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
              {PLEDGES.map((p, i) => (
                <motion.li
                  key={p.title}
                  initial={{ opacity: 0, y: 6 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.45, ease, delay: 0.15 + i * 0.04 }}
                  className="flex items-start gap-3"
                >
                  <div
                    className="
                      shrink-0 w-8 h-8 rounded-lg
                      flex items-center justify-center
                      text-lavender-deep
                      border border-lavender/25 bg-lavender/[0.06]
                    "
                  >
                    <div className="w-4 h-4">{p.glyph}</div>
                  </div>
                  <div className="min-w-0">
                    <div className="text-[14px] font-semibold text-ink-bright tracking-tight">
                      {p.title}
                    </div>
                    <div className="text-[12.5px] text-ink leading-relaxed mt-0.5">
                      {p.body}
                    </div>
                  </div>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* ── Right: shield card with private-by-design caption ─ */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.65, ease, delay: 0.1 }}
              className="flex flex-col items-center"
            >
              <ShieldArt />
              <p className="font-editorial mt-7 text-center text-[20px] md:text-[24px] font-medium tracking-editorial text-ink-bright leading-snug">
                Private by default.
                <br />
                Private by <span className="italic">design.</span>
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
