"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Problem — three lines, increasing emotional resolution.
 *
 *   Line 1 (dim ink)         : the technical truth
 *   Line 2 (mid ink)          : the human truth
 *   Line 3 (serif, lavender)  : the punchline
 *
 * Light-mode pass: ink colors cool to deep purple-black; the
 * lavender accent on the punchline carries the emotional weight.
 */
export function Problem() {
  return (
    <section className="relative py-28 md:py-36 px-5 md:px-8">
      <div className="max-w-3xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5, ease }}
          className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase mb-9"
        >
          Why this matters
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease, delay: 0.05 }}
          className="space-y-3"
        >
          <p className="text-[26px] md:text-[34px] font-light text-ink-dim leading-snug tracking-tight">
            Your computer stores information structurally.
          </p>
          <p className="text-[26px] md:text-[34px] font-light text-ink leading-snug tracking-tight">
            Humans remember contextually.
          </p>

          <div className="pt-7">
            <p className="font-editorial text-[32px] md:text-[48px] font-medium leading-[1.05] tracking-editorial text-ink-bright">
              You remember the idea.
            </p>
            <p className="font-editorial text-[32px] md:text-[48px] font-medium italic leading-[1.05] tracking-editorial mt-1">
              <span className="lavender-underline text-lavender-deep">
                Not the filename.
              </span>
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
