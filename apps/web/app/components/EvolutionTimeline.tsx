"use client";

import { motion, useReducedMotion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Evolution timeline — the iconic moment.
 *
 * One thread, four phases, drawn as a single trace that gains
 * structure as it advances:
 *
 *   • Particles dust the page background at the moment the thread
 *     begins (research is exploratory; events are loose).
 *   • A polyline traces phase-to-phase from left to right, drawn
 *     on view via `pathLength`. Phase boundaries are anchored on
 *     pill nodes whose vertical position encodes momentum.
 *   • Transition dividers between pills are colour-coded
 *     (acceleration / pivot / revisit / resumption / continuation)
 *     — same colours the launcher uses, same colours the docs
 *     describe.
 *
 * The whole sequence is *one* on-enter animation. No continuous
 * motion. No scroll-tied parallax. The composition is the visual;
 * we don't decorate it.
 *
 * The pill data below is the *real* shape `/v1/threads/{id}/evolution`
 * returns. Keeping the marketing surface honest with the product
 * surface is part of the "infrastructure, not assistant" posture.
 */

type Phase = {
  title: string;
  range: string;
  events: number;
  momentum: number; // 0..1 — drives the trace's vertical position
  transition:
    | "initial"
    | "acceleration"
    | "pivot"
    | "revisit"
    | "resumption"
    | "continuation";
  detail: string;
};

const PHASES: Phase[] = [
  {
    title: "Research",
    range: "Apr 28 – Apr 30",
    events: 9,
    momentum: 0.35,
    transition: "initial",
    detail:
      "Eight browser visits and one search. Stack Overflow, MDN, a couple of arXiv papers.",
  },
  {
    title: "Implementation",
    range: "May 01",
    events: 4,
    momentum: 0.95,
    transition: "acceleration",
    detail:
      "Surface shift to file opens. ~/code/websocket-retry/client.py, four edits in an afternoon.",
  },
  {
    title: "Discussion",
    range: "May 03",
    events: 5,
    momentum: 0.55,
    transition: "pivot",
    detail:
      "Claude chat about retry backoff strategy. Surface pivot, same topic.",
  },
  {
    title: "Revisit",
    range: "May 13",
    events: 3,
    momentum: 0.45,
    transition: "revisit",
    detail:
      "Returned to the original Stack Overflow thread after a long gap. 100% target overlap with phase 1.",
  },
];

function transitionColour(transition: Phase["transition"]) {
  switch (transition) {
    case "acceleration":
      return "rgba(135, 222, 183, 0.65)"; // mint
    case "pivot":
      return "rgba(125, 216, 232, 0.65)"; // cyan
    case "revisit":
      return "rgba(214, 120, 150, 0.55)"; // rose
    case "resumption":
      return "rgba(199, 151, 60, 0.55)"; // amber
    default:
      return "rgba(160, 150, 180, 0.40)"; // muted grey
  }
}

/* The trace canvas — drawn behind the pill row. ViewBox is
 * normalized so the polyline maths is independent of the
 * container's pixel width. */
const TRACE_W = 1000;
const TRACE_H = 140;
const TRACE_PAD_X = 100;
const TRACE_PAD_Y = 24;

function tracePoints() {
  // Linearly distribute phase centres across the canvas.
  const usable_w = TRACE_W - TRACE_PAD_X * 2;
  const usable_h = TRACE_H - TRACE_PAD_Y * 2;
  return PHASES.map((p, i) => {
    const x = TRACE_PAD_X + (i / (PHASES.length - 1)) * usable_w;
    // Higher momentum = lower y (visually "rising").
    const y = TRACE_PAD_Y + (1 - p.momentum) * usable_h;
    return { x, y };
  });
}

export function EvolutionTimeline() {
  const reduce = useReducedMotion();
  const points = tracePoints();
  const polyline = points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <section
      id="evolution"
      className="relative py-24 md:py-28 px-5 md:px-8 overflow-hidden"
    >
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase">
            Evolution
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            One thread,
            <br />
            <span className="italic">gaining structure.</span>
          </h2>
          <p className="mt-5 text-ink leading-relaxed text-[15px] max-w-md">
            A thread is the shape of an ongoing concern across files,
            browser, and chat. Evolution breaks it into the phases the
            user actually lived: research, implementation, revisit. No
            charts, no analytics &mdash; just a chronology.
          </p>
        </motion.div>

        {/* ── The thread trace ──────────────────────────────────────
            A single polyline traces left to right, animating once on
            view. Phase pills sit at the vertices. The background
            edge-highlight surface gives the composition a layered,
            "lit-from-above" feel without bloom. */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease, delay: 0.08 }}
          className="
            relative mt-12 md:mt-14
            rounded-2xl bg-white edge-highlight
            p-5 md:p-7 overflow-hidden
          "
        >
          {/* Topic header line */}
          <div className="flex items-center gap-2 mb-5">
            <span
              aria-hidden
              className="w-2 h-2 rounded-full bg-lavender-deep"
            />
            <code className="font-mono text-[12px] text-ink-bright font-medium">
              websocket retry on disconnect
            </code>
            <span className="text-[11px] text-ink-dim ml-1">
              · 21 events · 4 phases
            </span>
          </div>

          {/* Trace canvas + pill overlay. The SVG sits absolute
              behind the pill flexbox; the pills are placed by the
              same x-coordinates the polyline uses, so the line
              passes through their visual centres. */}
          <div className="relative">
            <svg
              className="w-full"
              viewBox={`0 0 ${TRACE_W} ${TRACE_H}`}
              preserveAspectRatio="none"
              style={{ height: TRACE_H }}
              aria-hidden
            >
              {/* Subtle baseline rule so the trace reads as climbing
                  *above* a reference line, not floating in space. */}
              <line
                x1={0}
                y1={TRACE_H - 10}
                x2={TRACE_W}
                y2={TRACE_H - 10}
                stroke="rgba(24, 17, 45, 0.05)"
                strokeWidth={1}
              />

              {/* Drop lines from each phase node down to the
                  baseline — like an x-ray ladder of where the
                  thread was at each moment. */}
              {points.map((p, i) => (
                <motion.line
                  key={`drop-${i}`}
                  x1={p.x}
                  y1={p.y + 4}
                  x2={p.x}
                  y2={TRACE_H - 10}
                  stroke="rgba(169, 156, 247, 0.18)"
                  strokeWidth={1}
                  strokeDasharray="2 3"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{
                    duration: 0.4,
                    ease,
                    delay: 0.4 + i * 0.05,
                  }}
                />
              ))}

              {/* The thread trace itself. Drawn-on once on view. */}
              <motion.polyline
                points={polyline}
                fill="none"
                stroke="#7D5FC8"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0, opacity: 0 }}
                whileInView={{ pathLength: 1, opacity: 1 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{
                  duration: reduce ? 0.001 : 1.6,
                  ease,
                  delay: 0.2,
                }}
              />

              {/* Vertex dots — phase boundaries, drawn last so they
                  sit on top of the trace. */}
              {points.map((p, i) => (
                <motion.circle
                  key={`vx-${i}`}
                  cx={p.x}
                  cy={p.y}
                  r={5}
                  fill="white"
                  stroke="#7D5FC8"
                  strokeWidth={2}
                  initial={{ opacity: 0, scale: 0.6 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{
                    duration: 0.45,
                    ease,
                    delay: 1.1 + i * 0.08,
                  }}
                />
              ))}
            </svg>
          </div>

          {/* Pill row sits *below* the trace canvas, structurally
              separate so layout doesn't depend on the SVG. The
              dividers between pills carry the transition colour
              cue — the only place we use colour to encode state. */}
          <div className="mt-6 overflow-x-auto pb-1">
            <div className="flex items-stretch min-w-fit">
              {PHASES.map((phase, i) => (
                <div
                  key={phase.title}
                  className="flex items-stretch min-w-fit"
                >
                  {i > 0 && (
                    <div
                      aria-hidden
                      className="self-center mx-1 md:mx-2 h-px w-6 md:w-12 shrink-0"
                      style={{ background: transitionColour(phase.transition) }}
                    />
                  )}
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-60px" }}
                    transition={{
                      duration: 0.45,
                      ease,
                      delay: 1.4 + i * 0.08,
                    }}
                    className="
                      min-w-[170px] md:min-w-[210px]
                      px-4 py-3 rounded-lg
                      border border-lavender/22 bg-lavender/[0.06]
                    "
                  >
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="text-[13px] font-semibold text-ink-bright tracking-tight">
                        {phase.title}
                      </span>
                      <span className="text-[10px] text-ink-dim tracking-tight font-mono">
                        {phase.events}&nbsp;ev
                      </span>
                    </div>
                    <div className="mt-1 text-[10.5px] text-ink-dim font-mono">
                      {phase.range}
                    </div>
                  </motion.div>
                </div>
              ))}
            </div>
          </div>

          {/* Per-phase detail rows — sit below the strip for users
              who want the chronology in prose. The grid + monospace
              transition tag give it a log-readout feel. */}
          <div className="mt-7 divide-y divide-hairline">
            {PHASES.map((phase, i) => (
              <motion.div
                key={phase.title + "-row"}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.4, ease, delay: 1.8 + i * 0.04 }}
                className="py-3 grid grid-cols-12 gap-3 items-baseline"
              >
                <div className="col-span-3 md:col-span-2 text-[11px] font-semibold text-ink-bright tracking-tight">
                  {phase.title}
                </div>
                <div className="col-span-9 md:col-span-10 text-[12px] text-ink leading-snug">
                  <span className="text-ink-dim tracking-tight font-mono mr-2">
                    [{phase.transition}]
                  </span>
                  {phase.detail}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, ease, delay: 0.4 }}
          className="mt-6 text-center text-[11px] text-ink-dim tracking-tight"
        >
          Same thread, same events, every time &mdash; the segmentation
          is deterministic. No model, no probabilities.
        </motion.p>
      </div>
    </section>
  );
}
