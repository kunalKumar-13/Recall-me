"use client";

import { motion } from "framer-motion";
import { LINKS } from "../lib/links";
import { ContinuityCore } from "./ContinuityCore";
import { WindowsGlyph } from "./WindowsGlyph";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Hero — the cinematic opening.
 *
 * Composition (left → right):
 *
 *   ┌──────────────────────────┬──────────────────────────┐
 *   │  eyebrow                 │                          │
 *   │  editorial headline      │     ContinuityCore       │
 *   │  one paragraph of body   │     (~520×520 stage)     │
 *   │  CTAs                    │                          │
 *   │  trust line (mono)       │                          │
 *   └──────────────────────────┴──────────────────────────┘
 *
 * The previous build used a dashboard mockup + QR card on the right.
 * Both are dropped — they signalled "product screenshot" where the
 * brief now asks for "operating-layer atmosphere". The continuity-
 * core composition does the same narrative work (this is a system)
 * with one calm visual instead of two competing surfaces.
 *
 * The hero stage uses `.hero-stage` from globals.css: a dark-ivory
 * gradient with a centred warmth and a graphite vignette pulling
 * the eye toward the core. No oversized hero blob, no animated
 * background — depth comes from layered radial gradients, paint-
 * once on mount.
 */

function PlayCircle({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <circle
        cx="16"
        cy="16"
        r="15.4"
        fill="white"
        stroke="rgba(24,17,45,0.12)"
        strokeWidth="1.2"
      />
      <path d="M13 11.5 L 21 16 L 13 20.5 Z" fill="#16112B" />
    </svg>
  );
}

export function Hero() {
  return (
    <section
      id="top"
      className="
        relative pt-24 md:pt-28 pb-20 md:pb-24 px-5 md:px-8
        overflow-hidden
        hero-stage
      "
    >
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* ── Left: copy + CTAs ────────────────────────────────── */}
          <div className="lg:col-span-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, ease }}
              className="
                inline-flex items-center gap-2
                text-[10.5px] font-semibold tracking-[0.22em]
                text-lavender-deep uppercase
              "
            >
              <span
                aria-hidden
                className="w-1.5 h-1.5 rounded-full bg-lavender-deep"
              />
              Local-first cognitive continuity
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease, delay: 0.08 }}
              className="
                font-editorial mt-7
                text-[42px] sm:text-[54px] md:text-[66px] lg:text-[72px]
                font-medium tracking-editorial leading-[1.02]
                text-ink-bright
              "
            >
              The continuity layer
              <br />
              <span className="italic font-normal">beneath your work.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.18 }}
              className="
                mt-7 text-[15px] md:text-[16px]
                text-ink leading-[1.65] max-w-[500px]
              "
            >
              Recall captures what you touched — files, browser, chat —
              and reconstructs it on demand into the moments, sessions,
              and long-lived threads of thought you actually remember.
            </motion.p>

            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.24 }}
              className="
                mt-3 text-[14px] md:text-[15px]
                text-ink-bright font-medium leading-snug
              "
            >
              Everything stays on disk.
              <span className="text-ink-dim font-normal">
                {" "}No cloud. No telemetry.
              </span>
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease, delay: 0.32 }}
              className="mt-10 flex items-center gap-5 flex-wrap"
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
                className="
                  group inline-flex items-center gap-2.5
                  text-ink-bright text-[14px] font-medium
                  transition-opacity duration-300
                  hover:opacity-75
                "
              >
                <PlayCircle className="w-9 h-9 transition-transform duration-300 group-hover:scale-105" />
                Watch 90s demo
              </a>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7, ease, delay: 0.5 }}
              className="
                mt-11 flex items-center gap-5
                text-[10.5px] font-mono text-ink-dim tracking-[0.05em]
              "
            >
              <span className="flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-mint" />
                127.0.0.1:4545
              </span>
              <span className="opacity-50">·</span>
              <span>~/.recall</span>
              <span className="opacity-50">·</span>
              <span>MIT</span>
            </motion.div>
          </div>

          {/* ── Right: the continuity-core composition ──────────────
              The composition is centered in its column and anchored
              by the dark-ivory hero stage behind. Slight Y translate
              on enter so it settles into place rather than appearing
              all at once. */}
          <div className="lg:col-span-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.0, ease, delay: 0.15 }}
              className="relative gpu"
            >
              <ContinuityCore />
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
