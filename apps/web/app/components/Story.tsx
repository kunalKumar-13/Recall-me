"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Phase 6G — the *Demo Story* section.
 *
 * Three named threads from the canonical demo overlay
 * (`app/core/demo_mode.demo_payload()`):
 *
 *   1. WebSocket retry debugging — the hero recovery candidate
 *   2. Healthcare pitch — proposal draft
 *   3. RLHF reward shaping — research investigation
 *
 * Each story is a card with: title · what it would look like in your
 * day · a thumbnail from the deterministic demo screenshots. Real
 * data only — every thumbnail is the actual offscreen capture, not
 * a mock-up.
 *
 * Copy-rule restated: no AI generation, no synthesised content. The
 * stories below describe the *shape* of work the user does, not
 * content the daemon invents.
 */

type Story = {
  eyebrow: string;
  title: string;
  arc: string;
  whatRecallDoes: string;
  thumbnail: { src: string; alt: string };
};

const STORIES: Story[] = [
  {
    eyebrow: "Developer",
    title: "WebSocket retry debugging",
    arc:
      "Stack Overflow, MDN, two implementation files, a Claude chat about backoff. Two days, a meeting, gone.",
    whatRecallDoes:
      "Recall surfaces the *whole* thread back — tabs, files, and the chat — in one Resume click.",
    thumbnail: {
      src: "/screens/extension/extension-recovery.png",
      alt: "Extension popup showing the WebSocket retry debugging recovery card",
    },
  },
  {
    eyebrow: "Founder",
    title: "Proposal draft",
    arc:
      "A notes file, a market-sizing spreadsheet, a model-assumptions chat, an investor tab. You step away to ship something else.",
    whatRecallDoes:
      "Five days later, Recall notices the gap and offers the resume — every artifact, in order, ready to reopen.",
    thumbnail: {
      src: "/screens/demo/demo-launcher.png",
      alt: "Launcher demo digest showing a Healthcare pitch proposal draft investigation",
    },
  },
  {
    eyebrow: "Researcher",
    title: "Research investigation",
    arc:
      "A search across three engines, four arXiv abstracts, two long-form blog posts. The thread lives across a week and your attention keeps splitting.",
    whatRecallDoes:
      "Recall keeps the investigation coherent without your filing it — and resurfaces it the next morning when you sit back down.",
    thumbnail: {
      src: "/screens/extension/extension-home.png",
      alt: "Extension popup with the Today rail and an active research investigation",
    },
  },
];

export function Story() {
  return (
    <section id="story" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
            How it shows up
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Three threads,
            <br />
            <span className="italic">one calm return.</span>
          </h2>
          <p className="mt-5 text-[15px] text-ink leading-[1.7] max-w-[560px]">
            The shapes of work Recall is built for — the same three the
            demo overlay shows on a fresh install. Real data only;
            nothing here is generated.
          </p>
        </motion.div>

        <div className="mt-12 md:mt-14 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {STORIES.map((s, i) => (
            <motion.article
              key={s.title}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.55, ease, delay: i * 0.07 }}
              className="
                rounded-3xl border border-hairline bg-bg-base
                overflow-hidden shadow-card flex flex-col
              "
            >
              <div className="px-6 pt-6 pb-4">
                <div className="text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase">
                  {s.eyebrow}
                </div>
                <h3 className="font-editorial mt-2 text-[22px] font-medium text-ink-bright leading-[1.15]">
                  {s.title}
                </h3>
                <p className="mt-3 text-[13.5px] text-ink leading-[1.6]">
                  {s.arc}
                </p>
                <p className="mt-3 text-[13.5px] text-ink-bright leading-[1.6]">
                  {s.whatRecallDoes}
                </p>
              </div>
              <div className="px-4 pb-4 mt-auto">
                <div className="
                  rounded-xl overflow-hidden
                  border border-hairline bg-bg-base
                ">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={s.thumbnail.src}
                    alt={s.thumbnail.alt}
                    loading="lazy"
                    className="w-full h-auto block"
                  />
                </div>
              </div>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
