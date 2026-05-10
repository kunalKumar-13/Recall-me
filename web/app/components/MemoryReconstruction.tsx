"use client";

import { motion, useInView } from "framer-motion";
import { useCallback, useEffect, useRef, useState } from "react";

const QUERY = "that healthcare startup idea from last winter";
const TYPE_INTERVAL_MS = 30;
const SCATTER_AFTER_MS = 180;
const ALIGN_AFTER_MS = 1000;
const FOCUS_AFTER_MS = 1900;

const ease = [0.32, 0.72, 0, 1] as const;

type Fragment = {
  id: string;
  ext: { label: string; tint: string; bg: string; fg: string };
  title: string;
  meta: string;
  excerpt?: string;
  primary?: boolean;
  scatter: { x: number; y: number; rotate: number };
  aligned: { x: number; y: number };
};

const FRAGMENTS: Fragment[] = [
  {
    id: "primary",
    ext: { label: "PDF", tint: "rose", bg: "rgba(244, 168, 201, 0.18)", fg: "#D67896" },
    title: "Healthcare startup pitch deck",
    meta: "pitch_deck.pdf  ·  January 14, 2024",
    excerpt:
      "Pediatric triage routing via natural-language intake — agent classifies urgency, matches to specialists.",
    primary: true,
    scatter: { x: -40, y: 60, rotate: -3 },
    aligned: { x: 0, y: 0 },
  },
  {
    id: "md",
    ext: { label: "MD", bg: "rgba(169, 156, 247, 0.16)", fg: "#8B7FE3", tint: "lavender" },
    title: "Onboarding flow notes",
    meta: "founders.md  ·  Jan 17",
    scatter: { x: -330, y: -180, rotate: -10 },
    aligned: { x: -270, y: -130 },
  },
  {
    id: "py",
    ext: { label: "PY", bg: "rgba(125, 216, 232, 0.20)", fg: "#3FB1C9", tint: "cyan" },
    title: "class TriageAgent",
    meta: "agent.py  ·  Jan 22",
    scatter: { x: 320, y: -190, rotate: 8 },
    aligned: { x: 270, y: -130 },
  },
  {
    id: "log",
    ext: { label: "LOG", bg: "rgba(184, 178, 192, 0.22)", fg: "#75716A", tint: "neutral" },
    title: "Notes from Aditi call",
    meta: "log_2024_01_09.txt",
    scatter: { x: -340, y: 50, rotate: -6 },
    aligned: { x: -300, y: 28 },
  },
  {
    id: "json",
    ext: { label: "JSON", bg: "rgba(135, 222, 183, 0.18)", fg: "#42B384", tint: "mint" },
    title: "FDA endpoint mapping",
    meta: "fda_data.json  ·  Jan 19",
    scatter: { x: 340, y: 60, rotate: 5 },
    aligned: { x: 300, y: 28 },
  },
  {
    id: "doc",
    ext: { label: "DOC", bg: "rgba(125, 216, 232, 0.18)", fg: "#3FB1C9", tint: "cyan" },
    title: "Investor memo v2",
    meta: "memo.docx  ·  Jan 21",
    scatter: { x: -240, y: 220, rotate: -4 },
    aligned: { x: -200, y: 175 },
  },
  {
    id: "img",
    ext: { label: "IMG", bg: "rgba(135, 222, 183, 0.18)", fg: "#42B384", tint: "mint" },
    title: "Whiteboard sketch",
    meta: "IMG_2741.jpg  ·  Jan 11",
    scatter: { x: 240, y: 230, rotate: 3 },
    aligned: { x: 200, y: 175 },
  },
];

type Phase = "idle" | "typing" | "scattered" | "aligning" | "focused";

function FragmentCard({
  fragment: f,
  phase,
  index,
}: {
  fragment: Fragment;
  phase: Phase;
  index: number;
}) {
  const visible = phase !== "idle" && phase !== "typing";
  const aligned = phase === "aligning" || phase === "focused";
  const focused = phase === "focused";
  const isPrimary = !!f.primary;

  const targetX = aligned ? f.aligned.x : f.scatter.x;
  const targetY = aligned ? f.aligned.y : f.scatter.y;
  const targetRotate = aligned ? 0 : f.scatter.rotate;
  const targetOpacity = !visible ? 0 : focused ? (isPrimary ? 1 : 0.42) : 1;
  const targetScale = !visible
    ? 0.94
    : focused
    ? isPrimary
      ? 1.04
      : 0.95
    : 1;

  const cardW = isPrimary ? 280 : 178;
  const cardH = isPrimary ? 124 : 66;

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
        scale: 0.94,
      }}
      animate={{
        x: targetX,
        y: targetY,
        rotate: targetRotate,
        opacity: targetOpacity,
        scale: targetScale,
      }}
      transition={{
        duration: aligned ? 0.6 : 0.5,
        ease,
        delay:
          phase === "scattered"
            ? index * 0.035
            : phase === "aligning"
            ? index * 0.03
            : 0,
      }}
    >
      <div
        className={`
          relative h-full w-full rounded-xl px-3 py-2.5 flex items-start gap-2.5
          bg-bg-base
          ${
            isPrimary
              ? "border border-lavender/45 shadow-cardHover"
              : "border border-hairline shadow-card"
          }
        `}
      >
        <div
          className="shrink-0 w-7 h-7 rounded-md flex items-center justify-center text-[9px] font-semibold tracking-widest"
          style={{ background: f.ext.bg, color: f.ext.fg }}
        >
          {f.ext.label}
        </div>

        <div className="flex-1 min-w-0">
          <div
            className={`${
              isPrimary ? "text-[12.5px]" : "text-[11.5px]"
            } font-semibold text-ink-bright truncate tracking-tight`}
          >
            {f.title}
          </div>
          <div className="text-[10px] text-ink-dim truncate mt-0.5">
            {f.meta}
          </div>
          {isPrimary && f.excerpt && (
            <div className="font-editorial text-[11px] italic text-ink mt-2 leading-snug line-clamp-2">
              {f.excerpt}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

/**
 * Memory reconstruction — the page's emotional centerpiece.
 *
 * Watch a half-thought become a recovered memory. Light-mode pass:
 * cards are white with hairline borders, the primary catches a soft
 * lavender border + chromier shadow; satellites stay white but fade
 * to ~42% in the focused state. The connecting lines and halo are
 * lavender at low alpha.
 */
export function MemoryReconstruction() {
  const sectionRef = useRef<HTMLElement>(null);
  const inView = useInView(sectionRef, { once: true, margin: "-15%" });
  const [phase, setPhase] = useState<Phase>("idle");
  const [typed, setTyped] = useState("");

  const cleanupRef = useRef<(() => void) | null>(null);

  const runSequence = useCallback(() => {
    cleanupRef.current?.();
    setPhase("typing");
    setTyped("");

    let i = 0;
    const typingInterval = window.setInterval(() => {
      i++;
      setTyped(QUERY.slice(0, i));
      if (i >= QUERY.length) window.clearInterval(typingInterval);
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
    return runSequence();
  }, [inView, runSequence]);

  const replay = useCallback(() => runSequence(), [runSequence]);

  const lines = FRAGMENTS.filter((f) => !f.primary);
  const linesActive = phase === "aligning" || phase === "focused";
  const cursorVisible = phase === "idle" || phase === "typing";

  return (
    <section
      ref={sectionRef}
      id="reconstruction"
      className="relative pt-28 md:pt-36 pb-24 md:pb-28 px-5 md:px-8 overflow-hidden"
    >
      <div className="max-w-2xl mx-auto text-center mb-12 md:mb-14">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5, ease }}
          className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
        >
          Memory reconstruction
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease, delay: 0.05 }}
          className="font-editorial mt-4 text-[32px] md:text-[48px] font-medium tracking-editorial text-ink-bright leading-[1.05]"
        >
          From half-thought
          <br />
          <span className="italic">to recovered idea.</span>
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5, ease, delay: 0.1 }}
          className="mt-6 text-ink leading-relaxed max-w-md mx-auto text-[15px]"
        >
          Watch a vague memory rebuild itself — the file you forgot, the
          notes you wrote alongside it, the connections you didn&apos;t.
        </motion.p>
      </div>

      {/* Search bar */}
      <div className="max-w-[600px] mx-auto relative">
        <div
          className="
            relative flex items-center gap-3 px-4 py-3
            rounded-xl border border-hairline
            bg-bg-base shadow-card
          "
        >
          <kbd className="text-[10px] text-ink-dim px-1.5 py-0.5 rounded border border-hairline bg-bg-page font-sans tracking-wider shrink-0">
            Ctrl + Space
          </kbd>
          <div className="flex-1 text-[14px] text-ink-bright leading-none tracking-[-0.005em]">
            <span>{typed}</span>
            <span
              aria-hidden
              className={`
                inline-block w-[1.5px] h-[15px] bg-lavender-deep ml-0.5 align-text-bottom
                ${cursorVisible ? "animate-pulse" : "opacity-0"}
              `}
            />
            {!typed && cursorVisible && (
              <span className="text-ink-dim/55">Type a half-memory…</span>
            )}
          </div>
        </div>

        <div
          aria-hidden
          className="absolute left-1/2 -translate-x-1/2 -bottom-12 w-[360px] h-32 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse at top, rgba(169, 156, 247, 0.28) 0%, transparent 70%)",
          }}
        />
      </div>

      {/* Stage */}
      <div className="relative mt-10 md:mt-12 mx-auto max-w-[820px]">
        <div
          className="
            relative w-full rounded-2xl overflow-hidden
            border border-hairline
            bg-bg-base shadow-card
          "
          style={{ height: 520 }}
        >
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            viewBox="-410 -260 820 520"
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
                stroke="rgba(169, 156, 247, 0.5)"
                strokeWidth={0.7}
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
                  duration: 0.6,
                  ease,
                  delay: phase === "aligning" ? i * 0.04 : 0,
                }}
              />
            ))}
          </svg>

          <motion.div
            aria-hidden
            className="
              absolute top-1/2 left-1/2
              -translate-x-1/2 -translate-y-1/2
              rounded-full pointer-events-none
            "
            style={{
              width: 460,
              height: 200,
              background:
                "radial-gradient(ellipse at center, rgba(169, 156, 247, 0.20) 0%, transparent 70%)",
              willChange: "opacity",
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: phase === "focused" ? 1 : 0 }}
            transition={{ duration: 0.7, ease }}
          />

          {FRAGMENTS.map((f, i) => (
            <FragmentCard key={f.id} fragment={f} phase={phase} index={i} />
          ))}
        </div>
      </div>

      <div className="mt-10 text-center">
        <p
          className={`
            min-h-[24px] text-[14px]
            ${
              phase === "focused"
                ? "font-editorial italic text-lavender-deep"
                : "text-ink-dim"
            }
          `}
        >
          {phase === "focused"
            ? "One half-memory · seven fragments · one recovered thought."
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
            mt-4 text-[12px] text-ink-dim hover:text-ink-bright
            transition-colors duration-300
            disabled:opacity-30 disabled:cursor-not-allowed
            underline decoration-hairline-strong underline-offset-4
            hover:decoration-lavender
          "
        >
          Watch again
        </button>
      </div>
    </section>
  );
}
