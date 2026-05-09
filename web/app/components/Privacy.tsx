"use client";

import { motion } from "framer-motion";

function PrivacyPill({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs text-ink border border-white/[0.08] bg-white/[0.02]">
      {label}
    </span>
  );
}

function LockGlyph() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="w-3.5 h-3.5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
    >
      <rect x="5" y="11" width="14" height="9" rx="2" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </svg>
  );
}

export function Privacy() {
  return (
    <section id="privacy" className="relative py-24 md:py-28 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease: [0.32, 0.72, 0, 1] }}
          className="
            relative rounded-3xl border border-white/[0.08]
            surface-glass-soft
            p-10 md:p-14 text-center overflow-hidden
          "
        >
          {/* Top hairline */}
          <div aria-hidden className="absolute inset-x-0 top-0 h-px hairline" />
          {/* Inner accent halo */}
          <div
            aria-hidden
            className="absolute -inset-x-20 -top-20 h-72 opacity-60"
            style={{
              background:
                "radial-gradient(ellipse at center, rgba(124,155,255,0.15) 0%, transparent 70%)",
            }}
          />

          <div className="relative">
            <div className="inline-flex items-center gap-2 text-[11px] font-semibold tracking-[0.18em] text-accent-light uppercase">
              <LockGlyph />
              Private by design
            </div>
            <h2 className="mt-4 text-3xl md:text-5xl font-semibold tracking-tight text-ink-bright leading-tight">
              Your memory is yours alone.
            </h2>
            <p className="mt-6 text-ink max-w-xl mx-auto leading-relaxed">
              Recall runs entirely on your laptop. The only network call is
              the one-time download of the embedding model — after that,
              every search, every memory, every passage stays local.
            </p>
            <div className="mt-9 flex items-center justify-center gap-2 flex-wrap">
              <PrivacyPill label="Offline-first" />
              <PrivacyPill label="No cloud" />
              <PrivacyPill label="No accounts" />
              <PrivacyPill label="No telemetry" />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
