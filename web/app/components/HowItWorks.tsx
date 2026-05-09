"use client";

import { motion } from "framer-motion";

type Step = {
  index: string;
  title: string;
  body: string;
};

const steps: Step[] = [
  {
    index: "01",
    title: "Point Recall at your folders.",
    body:
      "Documents, Desktop, a code repo — anything Recall should remember. Nothing leaves your laptop. The first scan runs locally and you can keep working while it builds.",
  },
  {
    index: "02",
    title: "It builds a private memory layer.",
    body:
      "Notes, code, PDFs are parsed and embedded on your CPU. The index lives in ~/.recall, never in the cloud. A small file watcher keeps it current as you create and edit.",
  },
  {
    index: "03",
    title: "Ask vaguely. Get exactly.",
    body:
      "Press Ctrl + Space. Type the half-thought you've been carrying. Recall finds the right passage — even when you don't remember the filename, the folder, or the exact words.",
  },
  {
    index: "04",
    title: "Old threads come back.",
    body:
      "Pitches from January. Notes from February. Recall surfaces forgotten work when it relates to what you're thinking about now — quietly, and only when it should.",
  },
];

export function HowItWorks() {
  return (
    <section
      id="how"
      className="relative pt-32 md:pt-40 pb-24 md:pb-28 px-6"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="text-center max-w-xl mx-auto"
        >
          <div className="text-[11px] font-semibold tracking-[0.18em] text-accent-light uppercase">
            How Recall thinks
          </div>
          <h2 className="mt-3 text-3xl md:text-5xl font-semibold tracking-tight text-ink-bright">
            Four quiet steps. Then it just works.
          </h2>
          <p className="mt-5 text-ink leading-relaxed">
            No prompts to write. No agents to configure. Recall does the
            remembering so your computer can hand things back to you when
            you need them.
          </p>
        </motion.div>

        <div className="mt-14 grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5">
          {steps.map((s, i) => (
            <motion.div
              key={s.index}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                duration: 0.5,
                ease: [0.32, 0.72, 0, 1],
                delay: i * 0.03,
              }}
              className="
                group relative rounded-2xl p-7 md:p-8
                surface-glass
                border border-white/[0.06]
                hover:border-accent/30
                hover:-translate-y-0.5
                transition-[transform,border-color,box-shadow] duration-500 ease-out
                hover:shadow-[0_30px_80px_-30px_rgba(124,155,255,0.25)]
              "
            >
              {/* Step index — large, subtle */}
              <div className="text-[11px] font-semibold tracking-[0.18em] text-accent-light/80">
                STEP {s.index}
              </div>
              <h3 className="mt-3 text-[20px] md:text-[22px] font-semibold tracking-tight text-ink-bright leading-snug">
                {s.title}
              </h3>
              <p className="mt-3 text-sm md:text-[15px] text-ink leading-relaxed">
                {s.body}
              </p>

              {/* Inner top hairline that lights on hover */}
              <div
                aria-hidden
                className="absolute inset-x-6 top-0 h-px opacity-40 hairline"
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
