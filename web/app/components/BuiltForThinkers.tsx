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
    <section className="relative py-24 md:py-32 px-6">
      <div className="max-w-4xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="text-3xl md:text-5xl font-semibold tracking-tight text-white"
        >
          Built for thinkers.
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{
            duration: 0.9,
            ease: [0.16, 1, 0.3, 1],
            delay: 0.08,
          }}
          className="mt-6 text-white/55 max-w-xl mx-auto leading-relaxed"
        >
          Recall is for people who keep notes everywhere, write code at 2am,
          read papers, draft pitch decks — and forget half of it by Friday.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 1, delay: 0.16 }}
          className="mt-10 flex items-center justify-center gap-2 flex-wrap"
        >
          {groups.map((g, i) => (
            <motion.span
              key={g}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{
                duration: 0.6,
                ease: [0.16, 1, 0.3, 1],
                delay: 0.18 + i * 0.04,
              }}
              className="px-3.5 py-1.5 text-sm text-white/75 rounded-full border border-white/10 bg-white/[0.02] backdrop-blur-sm"
            >
              {g}
            </motion.span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
