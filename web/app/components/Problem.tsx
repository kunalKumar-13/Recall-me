"use client";

import { motion } from "framer-motion";

export function Problem() {
  return (
    <section className="relative py-32 md:py-48 px-6">
      <div className="max-w-3xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease: [0.32, 0.72, 0, 1] }}
          className="text-[11px] font-semibold tracking-[0.18em] text-accent-light/80 uppercase mb-8"
        >
          Why this matters
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: [0.32, 0.72, 0, 1], delay: 0.1 }}
          className="text-4xl md:text-5xl lg:text-6xl font-medium tracking-tight leading-[1.15]"
        >
          <p className="text-ink-dim">Your computer stores information structurally.</p>
          <p className="mt-3 text-ink-bright">Humans remember contextually.</p>
          <p className="mt-8 text-2xl md:text-3xl text-gradient-accent">
            You remember the idea. Not the filename.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
