"use client";

import { motion, useInView } from "framer-motion";
import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Memory reconstruction — the page's emotional centerpiece.
 *
 * A four-phase animation triggered when the section enters view:
 *
 *   idle      → nothing visible
 *   typing    → query types into the search bar character-by-character
 *   scattered → seven memory fragments fade in at random offsets, slightly
 *               rotated, as if pulled in from different parts of the disk
 *   aligning  → fragments slide into a constellation around a primary card
 *               while delicate connection lines draw from the center
 *   focused   → primary becomes vivid + scales up, fragments fade to ~40%,
 *               an accent halo appears behind the primary
 *
 * Performance contract:
 *   - All motion is transform + opacity. No filter/blur transitions.
 *   - SVG lines use `pathLength` (compiled to stroke-dasharray, GPU-OK).
 *   - The whole thing fires once via useInView({ once: true }); no
 *     scroll-tied animation, so it cannot cause scroll jank.
 *   - A "Watch again" button replays the sequence on demand.
 */

// ----------------------------------------------------------- data

const QUERY = "that healthcare startup idea from last winter";
const TYPE_INTERVAL_MS = 28;
const SCATTER_AFTER_MS = 150;
const ALIGN_AFTER_MS = 950;
const FOCUS_AFTER_MS = 1850;

type Fragment = {
  id: string;
  ext: { label: string; color: string };
  title: string;
  meta: string;
  excerpt?: string; // primary only
  primary?: boolean;
  // Coordinates are relative to canvas center (0, 0).
  scatter: { x: number; y: number; rotate: number };
  aligned: { x: number; y: number };
};

const FRAGMENTS: Fragment[] = [
  {
    id: "primary",
    ext: { label: "PDF", color: "#EF4444" },
    title: "Healthcare agents pitch deck",
    meta: "pitch_deck.pdf  ·  Jan 14, 2024",
    excerpt:
      "Pediatric triage routing via natural-language intake — agent classifies urgency, matches to specialists.",
    primary: true,
    scatter: { x: -40, y: 60, rotate: -3 },
    aligned: { x: 0, y: 0 },
  },
  {
    id: "md",
    ext: { label: "MD", color: "#A78BFA" },
    title: "Onboarding flow notes",
    meta: "founders.md  ·  Jan 17",
    scatter: { x: -330, y: -190, rotate: -10 },
    aligned: { x: -270, y: -130 },
  },
  {
    id: "py",
    ext: { label: "PY", color: "#7C9BFF" },
    title: "class TriageAgent",
    meta: "agent.py  ·  Jan 22",
    scatter: { x: 320, y: -200, rotate: 8 },
    aligned: { x: 270, y: -130 },
  },
  {
    id: "log",
    ext: { label: "LOG", color: "#94A3B8" },
    title: "Notes from Aditi call",
    meta: "log_2024_01_09.txt",
    scatter: { x: -340, y: 50, rotate: -6 },
    aligned: { x: -300, y: 28 },
  },
  {
    id: "json",
    ext: { label: "JSON", color: "#10B981" },
    title: "FDA endpoint mapping",
    meta: "fda_data.json  ·  Jan 19",
    scatter: { x: 340, y: 60, rotate: 5 },
    aligned: { x: 300, y: 28 },
  },
  {
    id: "doc",
    ext: { label: "DOC", color: "#3B82F6" },
    title: "Investor memo v2",
    meta: "memo.docx  ·  Jan 21",
    scatter: { x: -240, y: 220, rotate: -4 },
    aligned: { x: -200, y: 175 },
  },
  {
    id: "img",
    ext: { label: "IMG", color: "#10B981" },
    title: "Whiteboard sketch",
    meta: "IMG_2741.jpg  ·  Jan 11",
    scatter: { x: 240, y: 230, rotate: 3 },
    aligned: { x: 200, y: 175 },
  },
];

type Phase = "idle" | "typing" | "scattered" | "aligning" | "focused";

const ease = [0.32, 0.72, 0, 1] as const;

// ----------------------------------------------------------- card

type CardProps = {
  fragment: Fragment;
  phase: Phase;
  index: number;
};

function FragmentCard({ fragment: f, phase, index }: CardProps) {
  const visible = phase !== "idle" && phase !== "typing";
  const aligned = phase === "aligning" || phase === "focused";
  const focused = phase === "focused";
  const isPrimary = !!f.primary;

  const targetX = aligned ? f.aligned.x : f.scatter.x;
  const targetY = aligned ? f.aligned.y : f.scatter.y;
  const targetRotate = aligned ? 0 : f.scatter.rotate;

  const targetOpacity = !visible ? 0 : focused ? (isPrimary ? 1 : 0.42) : 1;

  const targetScale = !visible
    ? 0.92
    : focused
    ? isPrimary
      ? 1.05
      : 0.94
    : 1;

  const cardW = isPrimary ? 280 : 184;
  const cardH = isPrimary ? 124 : 70;

  return (
    <motion.div
      className="absolute top-1/2 left-1/2"
      style={{
        width: cardW,
        height: cardH,
        marginLeft: -cardW / 2,
        marginTop: -cardH / 2,
        zIndex: isPrimary ? 10 : 5,
        willChange: "transform, opacity",
      }}
      initial={{
        x: f.scatter.x,
        y: f.scatter.y,
        rotate: f.scatter.rotate,
        opacity: 0,
        scale: 0.92,
      }}
      animate={{
        x: targetX,
        y: targetY,
        rotate: targetRotate,
        opacity: targetOpacity,
        scale: targetScale,
      }}
      transition={{
        duration: aligned ? 0.55 : 0.45,
        ease,
        delay:
          phase === "scattered"
            ? index * 0.03
            : phase === "aligning"
            ? index * 0.025
            : 0,
      }}
    >
      <div
        className={`
          relative h-full w-full rounded-xl px-3 py-2.5 flex items-start gap-2.5
          ${
            isPrimary
              ? "border border-accent/45 surface-glass shadow-cinematic"
              : "border border-white/[0.08] surface-glass-soft"
          }
        `}
      >
        {/* File-type tag */}
        <div
          className="shrink-0 w-7 h-7 rounded-md flex items-center justify-center text-[9px] font-bold tracking-widest"
          style={{
            background: `${f.ext.color}22`,
            color: f.ext.color,
            border: `1px solid ${f.ext.color}55`,
          }}
        >
          {f.ext.label}
        </div>

        <div className="flex-1 min-w-0">
          <div
            className={`${
              isPrimary ? "text-[13px]" : "text-[12px]"
            } font-semibold text-ink-bright truncate`}
          >
            {f.title}
          </div>
          <div className="text-[10px] text-ink-dim truncate mt-0.5">
            {f.meta}
          </div>
          {isPrimary && f.excerpt && (
            <div className="text-[11px] italic text-ink/80 mt-2 leading-snug line-clamp-2">
              {f.excerpt}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ----------------------------------------------------------- section

export function MemoryReconstruction() {
  const sectionRef = useRef<HTMLElement>(null);
  const inView = useInView(sectionRef, { once: true, margin: "-15%" });
  const [phase, setPhase] = useState<Phase>("idle");
  const [typed, setTyped] = useState("");

  // Cleanup tracker for the running sequence
  const cleanupRef = useRef<(() => void) | null>(null);

  const runSequence = useCallback(() => {
    // Cancel any in-flight sequence so replay always starts clean.
    cleanupRef.current?.();

    setPhase("typing");
    setTyped("");

    let i = 0;
    const typingInterval = window.setInterval(() => {
      i++;
      setTyped(QUERY.slice(0, i));
      if (i >= QUERY.length) {
        window.clearInterval(typingInterval);
      }
    }, TYPE_INTERVAL_MS);

    const totalTypingMs = QUERY.length * TYPE_INTERVAL_MS;
    const t1 = window.setTimeout(
      () => setPhase("scattered"),
      totalTypingMs + SCATTER_AFTER_MS
    );
    const t2 = window.setTimeout(
      () => setPhase("aligning"),
      totalTypingMs + ALIGN_AFTER_MS
    );
    const t3 = window.setTimeout(
      () => setPhase("focused"),
      totalTypingMs + FOCUS_AFTER_MS
    );

    const cleanup = () => {
      window.clearInterval(typingInterval);
      window.clearTimeout(t1);
      window.clearTimeout(t2);
      window.clearTimeout(t3);
    };
    cleanupRef.current = cleanup;
    return cleanup;
  }, []);

  useEffect(() => {
    if (!inView) return;
    const cleanup = runSequence();
    return cleanup;
  }, [inView, runSequence]);

  const replay = useCallback(() => {
    runSequence();
  }, [runSequence]);

  const lines = FRAGMENTS.filter((f) => !f.primary);
  const linesActive = phase === "aligning" || phase === "focused";
  const cursorVisible = phase === "idle" || phase === "typing";

  return (
    <section
      ref={sectionRef}
      id="demo"
      className="relative pt-32 md:pt-40 pb-24 md:pb-28 px-6 overflow-hidden"
    >
      {/* Heading */}
      <div className="max-w-2xl mx-auto text-center mb-12 md:mb-14">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5, ease }}
          className="text-[11px] font-semibold tracking-[0.18em] text-accent-light uppercase"
        >
          Memory reconstruction
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease, delay: 0.04 }}
          className="mt-3 text-3xl md:text-5xl font-semibold tracking-tight text-ink-bright leading-[1.05]"
        >
          From half-thought to
          <br />
          recovered idea.
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease, delay: 0.08 }}
          className="mt-5 text-ink leading-relaxed max-w-md mx-auto"
        >
          Watch Recall rebuild the thought from fragments — the file you
          forgot, the notes you wrote, the connections you didn&apos;t.
        </motion.p>
      </div>

      {/* Search bar — the source of the query */}
      <div className="max-w-[640px] mx-auto relative">
        <div
          className="
            relative flex items-center gap-3 px-5 py-3.5
            rounded-xl border border-white/[0.08]
            surface-glass shadow-cinematic
          "
        >
          <kbd className="text-[10px] text-ink-dim px-1.5 py-0.5 rounded border border-white/[0.08] bg-white/[0.03] font-sans tracking-wider shrink-0">
            Ctrl + Space
          </kbd>
          <div className="flex-1 text-[15px] text-ink-bright tabular-nums leading-none">
            <span>{typed}</span>
            <span
              aria-hidden
              className={`
                inline-block w-[2px] h-[16px] bg-accent ml-0.5 align-text-bottom
                ${cursorVisible ? "animate-pulse" : "opacity-0"}
              `}
            />
            {!typed && cursorVisible && (
              <span className="text-ink-dim/60">
                Type a half-memory…
              </span>
            )}
          </div>
        </div>

        {/* Accent glow under the search bar — connects the query to the
            canvas below by spilling soft light into the stage area */}
        <div
          aria-hidden
          className="absolute left-1/2 -translate-x-1/2 -bottom-16 w-[420px] h-40 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse at top, rgba(124, 155, 255, 0.22) 0%, transparent 70%)",
          }}
        />
      </div>

      {/* Stage — the constellation canvas, framed in a subtle glass
          container so the reconstruction reads as one composed scene */}
      <div className="relative mt-10 md:mt-12 mx-auto max-w-[860px]">
        <div
          className="
            relative w-full rounded-2xl overflow-hidden
            border border-white/[0.05]
            surface-glass-soft
          "
          style={{ height: 540 }}
        >
          {/* Top-edge accent hairline — picks up where the search-bar
              glow leaves off, threading them visually together */}
          <div
            aria-hidden
            className="absolute inset-x-0 top-0 h-px hairline opacity-40"
          />
          {/* SVG connection lines (drawn during alignment phase) */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox="-410 -270 820 540"
            preserveAspectRatio="xMidYMid meet"
            aria-hidden
          >
            {lines.map((f, i) => (
              <motion.line
                key={f.id}
                x1={0}
                y1={0}
                x2={f.aligned.x}
                y2={f.aligned.y}
                stroke="rgba(124, 155, 255, 0.5)"
                strokeWidth={0.8}
                strokeLinecap="round"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{
                  pathLength: linesActive ? 1 : 0,
                  opacity:
                    phase === "focused"
                      ? 0.55
                      : phase === "aligning"
                      ? 0.4
                      : 0,
                }}
                transition={{
                  duration: 0.55,
                  ease,
                  delay: phase === "aligning" ? i * 0.035 : 0,
                }}
              />
            ))}
          </svg>

          {/* Accent halo behind primary in focused state */}
          <motion.div
            aria-hidden
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full pointer-events-none"
            style={{
              width: 480,
              height: 220,
              background: "radial-gradient(ellipse at center, rgba(124, 155, 255, 0.20) 0%, transparent 70%)",
              willChange: "opacity",
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: phase === "focused" ? 1 : 0 }}
            transition={{ duration: 0.6, ease }}
          />

          {/* Cards */}
          {FRAGMENTS.map((f, i) => (
            <FragmentCard key={f.id} fragment={f} phase={phase} index={i} />
          ))}
        </div>
      </div>

      {/* Caption + replay */}
      <div className="mt-8 md:mt-10 text-center">
        <p className="text-sm text-ink-dim min-h-[20px]">
          {phase === "focused"
            ? "One half-memory · seven fragments · one reconstructed thought."
            : phase === "aligning"
            ? "Connecting ideas across files…"
            : phase === "scattered"
            ? "Fragments surfacing…"
            : phase === "typing"
            ? "Listening…"
            : "Scroll to begin."}
        </p>
        <button
          type="button"
          onClick={replay}
          disabled={phase !== "focused"}
          className="
            mt-4 px-4 py-2 text-xs text-ink rounded-md
            border border-white/[0.08] bg-white/[0.02]
            hover:bg-white/[0.05] hover:border-white/20
            transition-colors
            disabled:opacity-40 disabled:cursor-not-allowed
          "
        >
          Watch again
        </button>
      </div>
    </section>
  );
}
