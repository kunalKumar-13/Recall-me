"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Architecture — the six-layer stack, presented as an infrastructure
 * diagram. Each layer reads from the one below; layers compose
 * upward without collapsing. The visual is deliberately quiet: a
 * vertical rail, six labelled rows, two columns of prose. No glow,
 * no chart axes, no animated lines. Reads like a Stripe / Tailscale
 * architecture page.
 *
 * The "sacred hierarchy" — same wording as the CLAUDE.md charter —
 * is the strongest piece of trust we can communicate to a developer
 * audience on the landing page. The point is: this is a system, not
 * a wrapper.
 */

type Layer = {
  name: string;
  oneLine: string;
  detail: string;
};

const LAYERS: Layer[] = [
  {
    name: "events",
    oneLine: "raw capture",
    detail:
      "Per-day JSONL log under ~/.recall/events. Append-only, hand-editable.",
  },
  {
    name: "sessions",
    oneLine: "30-min temporal groupings",
    detail:
      "Activity gaps bound a session. Pure-temporal; no clustering.",
  },
  {
    name: "contexts",
    oneLine: "topic-coherent sub-blocks",
    detail:
      "Domain affinity + token overlap split sessions into micro-contexts.",
  },
  {
    name: "resurfacing",
    oneLine: "idle-launcher continuity",
    detail:
      "Surfaces unfinished work across days, sessions, and revisits.",
  },
  {
    name: "threads",
    oneLine: "persistent topic identity",
    detail:
      "Long-lived continuity. Confidence strengthens; decay is natural.",
  },
  {
    name: "evolution",
    oneLine: "chronological phases of a thread",
    detail:
      "Research → implementation → revisit. Deterministic segmentation.",
  },
];

export function Architecture() {
  return (
    <section
      id="architecture"
      className="relative py-24 md:py-28 px-5 md:px-8"
    >
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
          {/* ── Left: heading + prose ────────────────────────── */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, ease }}
              className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
            >
              Architecture
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.55, ease, delay: 0.05 }}
              className="
                font-editorial mt-3
                text-[32px] md:text-[44px]
                font-medium tracking-editorial leading-[1.05]
                text-ink-bright
              "
            >
              Six layers,
              <br />
              <span className="italic">composed upward.</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, ease, delay: 0.1 }}
              className="mt-5 text-ink leading-relaxed text-[15px] max-w-md"
            >
              Recall is a small Python process. Each layer is a few
              hundred lines, reads only from the layer below, and has
              its own performance budget and disable flag. Delete the
              top layer and the rest keeps working — the hierarchy is
              additive by construction.
            </motion.p>

            <motion.p
              initial={{ opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, ease, delay: 0.14 }}
              className="mt-4 text-ink leading-relaxed text-[15px] max-w-md"
            >
              No embeddings above the file layer. No LLMs. No remote
              inference. Same events in, same outputs out — every
              time.
            </motion.p>

            <motion.a
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, ease, delay: 0.2 }}
              href="https://docs.recall.computer"
              className="
                mt-8 inline-flex items-center gap-2
                text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase
                hover:opacity-80 transition-opacity duration-300
              "
            >
              Read the architecture docs
              <svg
                viewBox="0 0 24 24"
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14M13 5l7 7-7 7" />
              </svg>
            </motion.a>
          </div>

          {/* ── Right: the stack diagram ─────────────────────── */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.55, ease, delay: 0.08 }}
              className="
                relative rounded-2xl
                border border-hairline bg-white
                shadow-card
                p-5 md:p-7
              "
            >
              <div className="relative">
                {/* Vertical rail behind the layer rows */}
                <div
                  aria-hidden
                  className="absolute left-[14px] top-3 bottom-3 w-px bg-hairline"
                />

                {LAYERS.map((layer, i) => {
                  // Stabilize upward — the lowest layer (events) settles
                  // first, then sessions, contexts, … until evolution
                  // lands on top. The vertical translate is small (8px)
                  // so the eye reads it as the layer *finding its
                  // place*, not as a flourish.
                  const reverseIndex = LAYERS.length - 1 - i;
                  return (
                  <motion.div
                    key={layer.name}
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-40px" }}
                    transition={{
                      duration: 0.55,
                      ease,
                      delay: 0.08 + reverseIndex * 0.07,
                    }}
                    className="relative pl-10 py-3.5 first:pt-1 last:pb-1"
                  >
                    {/* Layer marker — small lavender square anchored
                        on the rail. Filled for the top of the stack
                        (current frontier), outlined below. */}
                    <span
                      aria-hidden
                      className={`
                        absolute left-[7px] top-[18px] w-[15px] h-[15px]
                        rounded-[4px] border
                        ${i === LAYERS.length - 1
                          ? "bg-lavender-deep border-lavender-deep"
                          : "bg-white border-lavender/55"}
                      `}
                    />

                    <div className="flex items-baseline gap-3 flex-wrap">
                      <code
                        className="
                          font-mono text-[13.5px] text-ink-bright
                          font-semibold tracking-tight
                        "
                      >
                        {layer.name}
                      </code>
                      <span className="text-[12px] text-ink-dim">
                        →&nbsp;&nbsp;{layer.oneLine}
                      </span>
                    </div>
                    <p className="mt-1 text-[12.5px] text-ink leading-snug">
                      {layer.detail}
                    </p>
                  </motion.div>
                  );
                })}
              </div>
            </motion.div>

            {/* Footnote — explicit budgets table teaser. */}
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, ease, delay: 0.5 }}
              className="
                mt-4 text-center text-[11px] text-ink-dim
                tracking-tight
              "
            >
              Every layer carries a perf budget &mdash;{" "}
              <code className="font-mono">/v1/threads/recent</code>{" "}
              lands in 30 ms on a 10K-event log.
            </motion.p>
          </div>
        </div>
      </div>
    </section>
  );
}
