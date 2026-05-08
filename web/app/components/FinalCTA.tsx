"use client";

import { motion } from "framer-motion";

export function FinalCTA() {
  return (
    <section
      id="download"
      className="relative py-32 md:py-44 px-6 overflow-hidden"
    >
      {/* A soft accent halo behind the headline */}
      <div
        aria-hidden
        className="absolute left-1/2 -translate-x-1/2 -top-20 w-[640px] h-[640px] blur-[140px]"
        style={{
          background:
            "radial-gradient(circle, rgba(139,155,255,0.16), transparent 60%)",
        }}
      />

      <div className="relative max-w-3xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-4xl md:text-6xl font-semibold tracking-tightest leading-[1.05] text-gradient"
        >
          Your laptop finally
          <br />
          remembers your thoughts.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.08 }}
          className="mt-6 md:mt-7 text-white/55 text-base md:text-lg leading-relaxed"
        >
          Download Recall. Press Ctrl + Space. Ask the question you've been
          carrying around all week.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.16 }}
          className="mt-10 flex items-center justify-center gap-3 flex-wrap"
        >
          <a
            href="#"
            className="px-6 py-3.5 rounded-lg bg-white text-black text-[15px] font-medium hover:bg-white/90 transition-colors shadow-[0_8px_30px_-8px_rgba(255,255,255,0.18)]"
          >
            Download for Windows
          </a>
          <a
            href="#demo"
            className="px-6 py-3.5 rounded-lg border border-white/15 text-white/85 text-[15px] hover:bg-white/[0.04] hover:border-white/25 transition-colors"
          >
            Watch demo
          </a>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, delay: 0.24 }}
          className="mt-6 text-xs text-white/35"
        >
          Free · macOS &amp; Linux coming soon · No account required
        </motion.p>
      </div>
    </section>
  );
}
