"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Demo — editorial pull-quotes of the kinds of half-thoughts Recall
 * is built to recover. Sets up MemoryReconstruction by *naming* the
 * shape of the queries before showing one resolve.
 */

const examples = [
  "that healthcare startup idea from last winter",
  "the websocket retry logic I wrote",
  "what I read about reward shaping",
  "the email I half-replied to about pricing",
  "the screenshot I took on Tuesday",
];

export function Demo() {
  return (
    <section
      id="demo"
      className="relative pt-24 md:pt-28 pb-16 md:pb-20 px-5 md:px-8"
    >
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5, ease }}
          className="text-center max-w-xl mx-auto mb-12"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase">
            What it answers
          </div>
          <h2 className="font-editorial mt-3 text-[28px] md:text-[40px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            The vague half-thoughts
            <br />
            <span className="italic">your computer keeps for you.</span>
          </h2>
        </motion.div>

        <ul className="space-y-4 md:space-y-5">
          {examples.map((line, i) => (
            <motion.li
              key={line}
              initial={{ opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.45, ease, delay: i * 0.04 }}
              className="
                relative pl-6 md:pl-7
                text-ink-bright
                font-editorial italic
                text-[18px] md:text-[22px]
                leading-snug tracking-editorial
              "
            >
              <span
                aria-hidden
                className="
                  absolute left-0 top-1.5 bottom-1.5 w-[2px]
                  bg-gradient-to-b
                    from-transparent via-lavender to-transparent
                  rounded-full
                "
              />
              <span className="text-ink-dim/60 not-italic font-sans">
                &ldquo;
              </span>
              {line}
              <span className="text-ink-dim/60 not-italic font-sans">
                &rdquo;
              </span>
            </motion.li>
          ))}
        </ul>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease, delay: 0.25 }}
          className="mt-12 text-center text-[13px] text-ink-dim"
        >
          Watch one of these recover itself, below.
        </motion.p>
      </div>
    </section>
  );
}
