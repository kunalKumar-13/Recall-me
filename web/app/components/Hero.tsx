"use client";

import { motion } from "framer-motion";
import { LauncherMockup } from "./LauncherMockup";

const ease = [0.16, 1, 0.3, 1] as const;

export function Hero() {
  return (
    <section
      id="top"
      className="relative pt-32 md:pt-40 pb-24 px-6 overflow-hidden"
    >
      <div className="max-w-6xl mx-auto text-center">
        {/* Eyebrow chip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/[0.02] text-xs text-white/65"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_8px_rgba(139,155,255,0.6)]" />
          An AI memory layer for your laptop
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease, delay: 0.08 }}
          className="mt-7 text-[44px] md:text-7xl font-semibold tracking-tightest leading-[1.05] text-gradient"
        >
          Ask your computer
          <br />
          what you forgot.
        </motion.h1>

        {/* Subhead */}
        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease, delay: 0.16 }}
          className="mt-6 md:mt-7 text-base md:text-xl text-white/55 max-w-2xl mx-auto leading-relaxed"
        >
          Recall instantly resurfaces forgotten ideas, notes, PDFs, code, and
          context from across your laptop — privately and offline.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease, delay: 0.24 }}
          className="mt-10 flex items-center justify-center gap-3 flex-wrap"
        >
          <a
            href="#download"
            className="px-5 py-3 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-colors shadow-[0_8px_30px_-8px_rgba(255,255,255,0.18)]"
          >
            Download for Windows
          </a>
          <a
            href="#demo"
            className="px-5 py-3 rounded-lg border border-white/15 text-white/85 text-sm hover:bg-white/[0.04] hover:border-white/25 transition-colors"
          >
            Watch demo
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, ease, delay: 0.32 }}
          className="mt-5 text-xs text-white/35"
        >
          Free · Local-first · No account required
        </motion.div>
      </div>

      {/* Cinematic launcher mockup — gently floats. The outer wrapper
          handles the entrance; the inner motion handles the slow ambient
          float so the entrance and the loop don't fight each other. */}
      <motion.div
        initial={{ opacity: 0, y: 60, scale: 0.965 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 1.2, ease, delay: 0.4 }}
        className="mt-20 md:mt-24 max-w-5xl mx-auto px-2"
      >
        <motion.div
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        >
          <LauncherMockup />
        </motion.div>
      </motion.div>
    </section>
  );
}
