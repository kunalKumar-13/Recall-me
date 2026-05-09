"use client";

import { motion } from "framer-motion";

export function FinalCTA() {
  return (
    <section
      id="download"
      className="relative pt-32 md:pt-44 pb-28 md:pb-36 px-6 overflow-hidden"
    >
      {/* Soft accent halo behind the headline */}
      <div
        aria-hidden
        className="absolute left-1/2 -translate-x-1/2 -top-20 w-[720px] h-[720px] opacity-90"
        style={{
          background:
            "radial-gradient(circle, rgba(124,155,255,0.22) 0%, transparent 60%)",
        }}
      />

      <div className="relative max-w-3xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
          className="text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tightest leading-[1.05] text-gradient"
        >
          Your digital life already contains your best ideas.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1], delay: 0.06 }}
          className="mt-6 md:mt-8 text-ink text-lg md:text-xl max-w-xl mx-auto leading-relaxed"
        >
          Recall helps you find them again.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1], delay: 0.12 }}
          className="mt-10 flex items-center justify-center gap-4 flex-wrap"
        >
          <a
            href="#download"
            className="px-6 py-3.5 rounded-lg bg-ink-bright text-bg-deepest text-[15px] font-medium hover:bg-white transition-colors shadow-cta"
          >
            Download for Windows
          </a>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3.5 rounded-lg border border-white/[0.10] text-ink-bright/95 text-[15px] hover:bg-white/[0.04] hover:border-white/20 transition-colors"
          >
            GitHub
          </a>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, delay: 0.24 }}
          className="mt-6 text-xs text-ink-dim"
        >
          Free · macOS &amp; Linux coming soon · No account required
        </motion.p>
      </div>
    </section>
  );
}
