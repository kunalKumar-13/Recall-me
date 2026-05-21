"use client";

import { motion } from "framer-motion";
import { LINKS } from "../lib/links";
import { LauncherMockup } from "./LauncherMockup";
import { QRBlock } from "./QRBlock";
import { WindowsGlyph } from "./WindowsGlyph";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Hero — two-column opening.
 *
 *   ┌──────────────────────────┬──────────────────────────┐
 *   │  eyebrow badge           │                          │
 *   │  editorial headline      │     LauncherMockup       │
 *   │  one paragraph of body   │     + QRBlock overlap     │
 *   │  two CTAs                │                          │
 *   │  four trust stats        │                          │
 *   └──────────────────────────┴──────────────────────────┘
 *
 * Copy is charter-vocabulary only — "continuity", "memory",
 * "local-first". No "AI memory layer", no chatbot framing.
 */

type Stat = { label: string; sub: string; glyph: React.ReactNode };

const STAT_GLYPH = {
  lock: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  ),
  cloudOff: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6.5 18A4 4 0 0 1 6 10.1 6 6 0 0 1 16.4 7.6" />
      <path d="M19 14.5A3.5 3.5 0 0 0 17.5 18H9" />
      <path d="M3 3l18 18" />
    </svg>
  ),
  shield: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l7.5 3v5.5c0 5-3.4 8.3-7.5 9.5-4.1-1.2-7.5-4.5-7.5-9.5V6z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  ),
  key: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="8" cy="14" r="4.5" />
      <path d="M11.2 10.8L20 2M16.5 5.5l2.5 2.5M14 8l2 2" />
    </svg>
  ),
};

const STATS: Stat[] = [
  { label: "100% Local", sub: "Your data stays on this device", glyph: STAT_GLYPH.lock },
  { label: "No Cloud", sub: "Nothing syncs, ever", glyph: STAT_GLYPH.cloudOff },
  { label: "No Telemetry", sub: "Zero tracking, zero pings", glyph: STAT_GLYPH.shield },
  { label: "Your Data, Yours", sub: "You own every memory", glyph: STAT_GLYPH.key },
];

function PlayCircle({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <circle cx="16" cy="16" r="15.4" fill="white" stroke="rgba(24,17,45,0.12)" strokeWidth="1.2" />
      <path d="M13 11.5 L 21 16 L 13 20.5 Z" fill="#16112B" />
    </svg>
  );
}

export function Hero() {
  return (
    <section
      id="top"
      className="relative pt-28 md:pt-32 pb-20 md:pb-24 px-5 md:px-8 overflow-hidden hero-stage"
    >
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-10 items-center">
          {/* ── Left: copy ─────────────────────────────────────── */}
          <div className="lg:col-span-6">
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, ease }}
              className="
                inline-flex items-center gap-2
                rounded-full border border-lavender/30 bg-lavender-wash
                px-3 py-1
                text-[10px] font-semibold tracking-[0.18em] uppercase
                text-lavender-deep
              "
            >
              <span aria-hidden className="w-1.5 h-1.5 rounded-full bg-lavender-deep" />
              Local-first continuity OS
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease, delay: 0.08 }}
              className="
                font-editorial mt-6
                text-[44px] sm:text-[56px] md:text-[64px] lg:text-[68px]
                font-medium tracking-editorial leading-[1.04]
                text-ink-bright
              "
            >
              Pick up exactly
              <br />
              <span className="italic font-normal lavender-underline">
                where you left off.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.18 }}
              className="mt-6 text-[15px] md:text-[16px] text-ink leading-[1.65] max-w-[480px]"
            >
              Every interruption makes you rebuild context from scratch —
              the open tabs, the right files, the line of thinking you
              were chasing.
              Recall restores that whole working state in one keystroke, so
              you re-enter the work instead of reconstructing it. It all
              stays{" "}
              <span className="text-ink-bright font-medium">on your machine</span>.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.3 }}
              className="mt-8 flex items-center gap-5 flex-wrap"
            >
              <a
                href={LINKS.release}
                target="_blank"
                rel="noopener noreferrer"
                className="
                  inline-flex items-center gap-2
                  h-11 px-5 rounded-lg
                  bg-ink-bright text-white text-[14px] font-medium
                  shadow-lift
                  transition-[transform,background] duration-300
                  hover:-translate-y-px hover:bg-black
                "
              >
                <WindowsGlyph className="w-4 h-4" />
                Download for Windows
              </a>

              <a
                href={LINKS.demoVideo}
                className="group inline-flex items-center gap-2.5 text-ink-bright text-[14px] font-medium transition-opacity duration-300 hover:opacity-75"
              >
                <PlayCircle className="w-9 h-9 transition-transform duration-300 group-hover:scale-105" />
                Watch 90s demo
              </a>
            </motion.div>

            {/* Trust stats */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.42 }}
              className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-5"
            >
              {STATS.map((s) => (
                <div key={s.label}>
                  <span className="w-7 h-7 flex items-center justify-center text-lavender-deep">
                    <span className="w-[18px] h-[18px]">{s.glyph}</span>
                  </span>
                  <div className="mt-1.5 text-[12.5px] font-semibold text-ink-bright">
                    {s.label}
                  </div>
                  <div className="text-[10.5px] text-ink-dim leading-snug">
                    {s.sub}
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* ── Right: launcher mockup + QR ─────────────────────── */}
          <div className="lg:col-span-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.0, ease, delay: 0.15 }}
              className="relative gpu"
            >
              <LauncherMockup />
              <div className="absolute -bottom-6 -right-3 sm:-right-6 hidden sm:block">
                <QRBlock />
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
