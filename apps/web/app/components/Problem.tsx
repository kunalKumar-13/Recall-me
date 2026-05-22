"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Phase 6G — the *Problem* section.
 *
 * Sits between the Hero and HowItWorks: a short, calm paragraph that
 * names the thing every knowledge worker recognises but rarely
 * articulates. The continuity layer's job is to fix this; the page's
 * job here is to make the reader nod.
 *
 * No chart, no statistics, no scare quote. One sentence, then three
 * short observation rows. Same visual rhythm as HowItWorks; copy is
 * deliberately quieter than the Hero.
 */

type Observation = { eyebrow: string; line: string };

const OBSERVATIONS: Observation[] = [
  {
    eyebrow: "What broke",
    line: "Every interruption deletes the context you were building.",
  },
  {
    eyebrow: "What it costs",
    line: "Twenty minutes of tab-hunting before you can think again.",
  },
  {
    eyebrow: "What does not work",
    line: "Note-taking, pinning, second-monitor habits — they fight your attention.",
  },
];

export function Problem() {
  return (
    <section id="problem" className="relative py-20 md:py-24 px-5 md:px-8">
      <div className="max-w-[1100px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
            The problem
          </div>
          <h2 className="font-editorial mt-3 text-[28px] md:text-[40px] font-medium tracking-editorial text-ink-bright leading-[1.1]">
            Context loss is the tax
            <br />
            <span className="italic">on every working day.</span>
          </h2>
          <p className="mt-5 text-[15px] text-ink leading-[1.7] max-w-[560px]">
            The work was alive in twenty open tabs, four files, and a
            half-finished chat. Then a meeting, a notification, a different
            project. When you come back, none of it is still in your head —
            and none of the tools you have can rebuild it for you.
          </p>
        </motion.div>

        <div className="mt-10 md:mt-12 grid grid-cols-1 sm:grid-cols-3 gap-5">
          {OBSERVATIONS.map((o, i) => (
            <motion.div
              key={o.eyebrow}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, ease, delay: i * 0.07 }}
              className="
                rounded-2xl border border-hairline bg-bg-base
                px-5 py-5 shadow-card
              "
            >
              <div className="text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase">
                {o.eyebrow}
              </div>
              <p className="mt-2 text-[14px] leading-[1.55] text-ink-bright">
                {o.line}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
