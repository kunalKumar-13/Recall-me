"use client";

import { motion } from "framer-motion";
import { LINKS } from "../lib/links";
import { LauncherMockup } from "./LauncherMockup";
import { QRBlock } from "./QRBlock";
import { TrustBadges } from "./TrustBadges";
import { WindowsGlyph } from "./WindowsGlyph";

const ease = [0.32, 0.72, 0, 1] as const;

// ----------------------------------------------------------- glyphs

function Sparkle({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden>
      <path d="M12 1.5l1.7 6.3a4 4 0 0 0 2.5 2.5l6.3 1.7-6.3 1.7a4 4 0 0 0-2.5 2.5l-1.7 6.3-1.7-6.3a4 4 0 0 0-2.5-2.5L1.5 12l6.3-1.7a4 4 0 0 0 2.5-2.5L12 1.5z" />
    </svg>
  );
}

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

// ----------------------------------------------------------- hero

export function Hero() {
  return (
    <section
      id="top"
      className="relative pt-24 md:pt-28 pb-16 md:pb-20 px-5 md:px-8"
    >
      {/* Stage light — single soft lavender ellipse cast from above
          the dashboard. Static; reads as ambient lighting, not as a
          beam, and costs zero paint time. */}
      <div
        aria-hidden
        className="
          absolute left-1/2 top-[6%] -translate-x-1/2
          w-[1100px] h-[640px] pointer-events-none
        "
        style={{
          background:
            "radial-gradient(ellipse 50% 55% at 50% 0%, rgba(181, 168, 255, 0.16), transparent 65%)",
        }}
      />

      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-start">
          {/* ── Left: copy + CTAs + trust badges ────────────────── */}
          <div className="lg:col-span-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease }}
              className="inline-flex items-center gap-2 text-[10.5px] font-semibold tracking-[0.16em] text-lavender-deep uppercase"
            >
              <Sparkle className="w-3 h-3 text-lavender" />
              AI memory layer for your laptop
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease, delay: 0.06 }}
              className="
                font-editorial mt-6
                text-[40px] sm:text-[52px] md:text-[64px] lg:text-[72px]
                font-medium tracking-editorial leading-[1.02]
                text-ink-bright
              "
            >
              Ask your computer
              <br />
              <span className="italic font-normal">
                <span className="lavender-underline">what you</span>{" "}
                <span className="lavender-underline">forgot</span>.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease, delay: 0.14 }}
              className="
                mt-7 text-[15px] md:text-[16px]
                text-ink leading-[1.6] max-w-[480px]
              "
            >
              Recall is a private AI memory layer that helps you track,
              find, and reconnect with ideas across your notes, docs,
              code, and more —{" "}
              <span className="lavender-underline text-ink-bright font-medium">
                all locally.
              </span>
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease, delay: 0.22 }}
              className="mt-9 flex items-center gap-4 flex-wrap"
            >
              <a
                href={LINKS.release}
                target="_blank"
                rel="noopener noreferrer"
                className="
                  inline-flex items-center gap-2
                  h-11 px-5 rounded-lg
                  bg-ink-bright text-white text-[14px] font-medium
                  hover:bg-black transition-[background,transform] duration-300
                  hover:-translate-y-px
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
                  hover:opacity-80
                "
              >
                <PlayCircle className="w-9 h-9 transition-transform duration-300 group-hover:scale-105" />
                Watch 90s demo
              </a>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, ease, delay: 0.32 }}
              className="mt-10"
            >
              <TrustBadges />
            </motion.div>
          </div>

          {/* ── Right: dashboard mockup + floating QR ──────────────
              The dashboard sits inside a relative container so the QR
              card can float at the bottom-right edge without breaking
              flow on small screens. */}
          <div className="lg:col-span-6 relative">
            {/* Decorative ✦ near the dashboard's upper-right area —
                tiny lavender note that the device is alive. */}
            <motion.div
              aria-hidden
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7, ease, delay: 0.5 }}
              className="hidden md:block absolute -top-1 right-12 z-10 text-lavender-deep/70"
            >
              <Sparkle className="w-4 h-4" />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease, delay: 0.3 }}
              className="relative"
            >
              <LauncherMockup />

              {/* QR card floats at the bottom-right edge of the device */}
              <div className="hidden md:block absolute -right-3 -bottom-10 z-10">
                <QRBlock />
              </div>
            </motion.div>

            {/* On mobile the QR sits below the device, centered */}
            <div className="md:hidden mt-10 flex justify-center">
              <QRBlock />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
