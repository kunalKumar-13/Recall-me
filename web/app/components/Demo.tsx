"use client";

import { motion } from "framer-motion";

function PlayGlyph() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="w-6 h-6 ml-1"
      fill="currentColor"
    >
      <path d="M8 5v14l11-7z" />
    </svg>
  );
}

/**
 * Demo section — a premium video placeholder, framed like a paused
 * cinematic player. The container is real (16:9 glass card with a
 * play button); the video file is wired via the `src` below when the
 * actual demo asset is ready. Until then, the card itself is the
 * artifact — the design hints at what's coming.
 */
export function Demo() {
  return (
    <section id="demo" className="relative pt-32 md:pt-40 pb-24 md:pb-28 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="text-center max-w-xl mx-auto mb-10 md:mb-12"
        >
          <div className="text-[11px] font-semibold tracking-[0.18em] text-accent-light uppercase">
            Demo
          </div>
          <h2 className="mt-3 text-3xl md:text-5xl font-semibold tracking-tight text-ink-bright">
            See it remember.
          </h2>
          <p className="mt-5 text-ink leading-relaxed">
            Thirty seconds. One vague query. One recovered idea.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.98 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: [0.32, 0.72, 0, 1] }}
          className="relative rounded-2xl border border-white/[0.08] surface-glass shadow-cinematic overflow-hidden gpu"
        >
          {/* Outer accent halo behind the card — same depth language as the
              hero mockup so the page reads as one design system */}
          <div
            aria-hidden
            className="absolute -inset-x-12 -inset-y-8 -z-10 rounded-[3rem] pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(124, 155, 255, 0.10) 0%, transparent 60%)" }}
          />
          {/* 16:9 frame */}
          <div className="relative aspect-video w-full">
            {/* Backdrop — soft accent gradient hinting at content */}
            <div
              aria-hidden
              className="absolute inset-0"
              style={{
                background:
                  "radial-gradient(ellipse at 50% 60%, rgba(124,155,255,0.15), transparent 60%), linear-gradient(180deg, rgba(11,16,32,0.6), rgba(8,17,31,0.9))",
              }}
            />

            {/* Subtle horizon line for cinematic feel */}
            <div
              aria-hidden
              className="absolute left-0 right-0 top-1/2 h-px hairline opacity-30"
            />

            {/* Centered play button */}
            <button
              type="button"
              aria-label="Play demo"
              className="
                absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2
                w-20 h-20 md:w-24 md:h-24 rounded-full
                bg-ink-bright/95 text-bg-deepest
                flex items-center justify-center
                hover:bg-white transition-all duration-300
                shadow-glow
                group
              "
            >
              {/* Concentric ripple, gentle and constant */}
              <span
                aria-hidden
                className="absolute inset-0 rounded-full border border-white/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-ping"
                style={{ animationDuration: "2.5s" }}
              />
              <PlayGlyph />
            </button>

            {/* Caption strip — like a real video player chrome */}
            <div className="absolute bottom-0 inset-x-0 px-6 py-4 flex items-center justify-between text-[11px] text-ink-dim">
              <span className="tracking-[0.2em] uppercase">
                Recall · 0:32
              </span>
              <span className="hidden md:inline tracking-wide">
                A vague memory, recovered in a single keystroke.
              </span>
              <span className="tracking-wide">↗ Fullscreen</span>
            </div>

            {/* Top accent hairline */}
            <div
              aria-hidden
              className="absolute inset-x-0 top-0 h-px hairline"
            />
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1, delay: 0.2 }}
          className="mt-6 text-center text-xs text-ink-dim"
        >
          Demo recorded on Windows · 1080p · No edits, one take.
        </motion.p>
      </div>
    </section>
  );
}
