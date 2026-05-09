"use client";

import { motion } from "framer-motion";

const groups = [
  "Developers",
  "Researchers",
  "Founders",
  "Students",
  "Writers",
  "Designers",
  "Anyone with too many thoughts",
];

export function BuiltForThinkers() {
  return (
    <section className="relative py-20 md:py-24 px-6">
      <div className="max-w-4xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="text-3xl md:text-5xl font-semibold tracking-tight text-ink-bright"
        >
          Built for thinkers.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{
            duration: 0.5,
            ease: [0.32, 0.72, 0, 1],
            delay: 0.05,
          }}
          className="mt-5 text-ink max-w-lg mx-auto leading-relaxed"
        >
          Recall is for people who keep notes everywhere, write code at 2am,
          read papers, draft pitch decks — and forget half of it by Friday.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mt-8 flex items-center justify-center gap-2 flex-wrap"
        >
          {groups.map((g, i) => (
            <motion.span
              key={g}
              initial={{ opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{
                duration: 0.4,
                ease: [0.32, 0.72, 0, 1],
                delay: 0.12 + i * 0.025,
              }}
              className="px-3.5 py-1.5 text-sm text-ink rounded-full border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm"
            >
              {g}
            </motion.span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
