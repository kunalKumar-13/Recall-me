"use client";

import { motion } from "framer-motion";

export function Problem() {
  return (
    <section className="relative py-32 md:py-40 px-6">
      <div className="max-w-3xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-120px" }}
          transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-3xl md:text-5xl font-semibold tracking-tight leading-[1.15]"
        >
          <p className="text-white">Your computer stores files.</p>
          <p className="mt-2 text-white/55">
            Your brain stores memories.
          </p>
          <p className="mt-2 text-gradient-accent">
            Recall connects the two.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
