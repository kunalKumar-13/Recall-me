"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useMemo } from "react";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * ContinuityCore — the hero centerpiece.
 *
 * One composition, three depth layers, no canvas:
 *
 *   1. **Memory particles** drift faintly at the outer ring. Fixed
 *      positions (seeded deterministically so SSR + hydration agree).
 *      A single, very subtle one-shot fade-in on enter; no continuous
 *      particle motion.
 *   2. **Convergence lines** stroke inward from a subset of particles
 *      toward the core. Drawn once via Framer's `pathLength` — the
 *      moment of "fragments resolving into structure".
 *   3. **Thread strands** — three near-horizontal lines pass through
 *      the core area, suggesting the persistent threads that emerge
 *      from the converged fragments. Drawn once on view; then static.
 *
 * The core itself is a small lavender orb with an inner specular
 * highlight and a 1px edge ring. Sits in the canvas centre so the
 * surrounding ring composition reads as orbital, not parallax.
 *
 * **Motion budget.** A single optional drift on the *whole* SVG —
 * 4 px vertical sway over 14 seconds, alternating, very low alpha
 * threshold so the eye reads it as ambient depth rather than motion.
 * Gated on `prefers-reduced-motion`; off when the user has asked
 * for less motion.
 *
 * **Performance.** Pure inline SVG. Zero canvas, zero R3F, zero
 * shaders. Twenty-four circles + eight lines + three strokes = ~36
 * primitives, all GPU-rastered.
 */

const PARTICLE_COUNT = 24;
const CONVERGENCE_COUNT = 8;
const CANVAS = 540;             // viewBox is symmetric around 0
const CENTRE = 0;
const RING_OUTER = 220;
const RING_INNER = 175;
const CORE_R = 12;

function seededRandom(seed: number) {
  // Mulberry32 — small, fast, deterministic. Used so the particle
  // positions are identical between SSR and client hydration.
  let t = seed >>> 0;
  return () => {
    t = (t + 0x6D2B79F5) >>> 0;
    let x = t;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

type Particle = { x: number; y: number; r: number; opacity: number };

function generateParticles(): Particle[] {
  const rand = seededRandom(0x52ec / 13); // arbitrary but constant
  const out: Particle[] = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const angle = (i / PARTICLE_COUNT) * Math.PI * 2 + rand() * 0.12;
    const radius = RING_INNER + rand() * (RING_OUTER - RING_INNER);
    out.push({
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      r: 1.4 + rand() * 1.6,
      opacity: 0.30 + rand() * 0.55,
    });
  }
  return out;
}

export function ContinuityCore() {
  const reduce = useReducedMotion();
  const particles = useMemo(generateParticles, []);

  // Pick which particles get a convergence line. Evenly spaced
  // around the ring for visual balance.
  const convergers = useMemo(
    () =>
      Array.from({ length: CONVERGENCE_COUNT }, (_, i) =>
        particles[Math.round((i * PARTICLE_COUNT) / CONVERGENCE_COUNT) % PARTICLE_COUNT]
      ),
    [particles]
  );

  // Three thread strands passing through the core area. Slight
  // vertical offset to imply parallel persistence over time.
  const strands = [
    { y: -34, opacity: 0.18 },
    { y: 0,   opacity: 0.30 },
    { y: 34,  opacity: 0.18 },
  ];

  return (
    <div
      aria-hidden
      className="relative w-full mx-auto"
      style={{ maxWidth: CANVAS, aspectRatio: "1 / 1" }}
    >
      {/* Atmospheric backdrop — three concentric radial layers, paint-
          once. Soft warmth at the centre, graphite vignette at the
          edges. No bloom; the colour does the work. */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(232, 226, 251, 0.55) 0%, rgba(232, 226, 251, 0.0) 55%)",
        }}
      />
      <div
        className="absolute inset-[8%] rounded-full"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(169, 156, 247, 0.16) 0%, transparent 65%)",
        }}
      />
      <div
        className="absolute inset-[20%] rounded-full"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(169, 156, 247, 0.22) 0%, transparent 70%)",
        }}
      />

      {/* The actual SVG composition. */}
      <motion.svg
        viewBox={`${-CANVAS / 2} ${-CANVAS / 2} ${CANVAS} ${CANVAS}`}
        className="absolute inset-0 w-full h-full"
        // Ambient drift — 4 px vertical sway, alternating, 14 s.
        // Disabled under prefers-reduced-motion.
        animate={
          reduce
            ? undefined
            : { y: [0, -4, 0, 4, 0] }
        }
        transition={
          reduce
            ? undefined
            : {
                duration: 14,
                repeat: Infinity,
                ease: "easeInOut",
              }
        }
      >
        {/* Thread strands — persistent topic continuity. Drawn first
            so the core overlays them. */}
        {strands.map((s, i) => (
          <motion.line
            key={`strand-${i}`}
            x1={-RING_OUTER}
            y1={s.y}
            x2={RING_OUTER}
            y2={s.y}
            stroke="rgba(125, 95, 200, 0.85)"
            strokeWidth={0.6}
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            whileInView={{ pathLength: 1, opacity: s.opacity }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{
              duration: 1.6,
              ease,
              delay: 0.45 + i * 0.12,
            }}
          />
        ))}

        {/* Convergence lines — fragments resolving into structure.
            Each strokes inward toward the centre from its anchor
            particle. */}
        {convergers.map((p, i) => (
          <motion.line
            key={`conv-${i}`}
            x1={p.x}
            y1={p.y}
            x2={CENTRE}
            y2={CENTRE}
            stroke="rgba(169, 156, 247, 0.45)"
            strokeWidth={0.45}
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            whileInView={{ pathLength: 1, opacity: 1 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{
              duration: 1.2,
              ease,
              delay: 0.2 + i * 0.06,
            }}
          />
        ))}

        {/* Outer ring particles — memory fragments. One-shot fade-in
            on enter; static after. */}
        {particles.map((p, i) => (
          <motion.circle
            key={`p-${i}`}
            cx={p.x}
            cy={p.y}
            r={p.r}
            fill="rgba(125, 95, 200, 1)"
            initial={{ opacity: 0, scale: 0.5 }}
            whileInView={{ opacity: p.opacity, scale: 1 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{
              duration: 0.6,
              ease,
              delay: 0.05 + (i / PARTICLE_COUNT) * 0.4,
            }}
          />
        ))}

        {/* The core. Two static layers: a soft halo, then the orb
            with a specular highlight. The core is drawn last so it
            sits on top of every other element in the composition. */}
        <motion.circle
          cx={CENTRE}
          cy={CENTRE}
          r={CORE_R * 2.4}
          fill="rgba(169, 156, 247, 0.18)"
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.9, ease, delay: 0.6 }}
        />
        <motion.circle
          cx={CENTRE}
          cy={CENTRE}
          r={CORE_R}
          fill="#A99CF7"
          stroke="rgba(255, 255, 255, 0.55)"
          strokeWidth={0.5}
          initial={{ opacity: 0, scale: 0.6 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.9, ease, delay: 0.7 }}
        />
        {/* Specular pip — the lighting cue that gives the orb
            implied dimensionality without a shader. */}
        <motion.circle
          cx={CENTRE - 4}
          cy={CENTRE - 5}
          r={2.6}
          fill="rgba(255, 255, 255, 0.85)"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.6, ease, delay: 0.9 }}
        />
      </motion.svg>

      {/* Footer caption — tiny mono label. Sits under the
          composition, anchored to the core's vertical axis. */}
      <div
        className="absolute inset-x-0 bottom-[-8px] text-center pointer-events-none"
      >
        <span className="font-mono text-[10px] tracking-[0.18em] text-ink-dim uppercase">
          continuity-core
        </span>
      </div>
    </div>
  );
}
