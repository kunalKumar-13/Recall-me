"use client";

import { motion } from "framer-motion";

/**
 * Atmospheric background — five static + animated layers, composited
 * to feel cinematic without touching scroll performance.
 *
 * Layer stack (back to front):
 *   1. Page-level gradient (in body via globals.css)
 *   2. Dot-grid texture (static, masked toward edges)
 *   3. Aurora beams (slow diagonal drift, transform-only)
 *   4. Volumetric orbs (long-loop motion, transform + opacity only)
 *   5. Top hairline horizon
 *
 * Performance contract:
 *   - Every animated element uses transform/opacity, never blur or filter
 *     transitions. The blur amounts are static; only translate/scale
 *     animate, so the browser hoists each to its own compositor layer.
 *   - `gpu` class promotes layers explicitly and keeps the main thread
 *     out of paint work.
 */
export function AmbientBackground() {
  return (
    <div
      aria-hidden
      className="fixed inset-0 -z-10 overflow-hidden pointer-events-none"
    >
      {/* Layer 2 — dot-grid texture */}
      <div className="absolute inset-0 grid-texture" />

      {/* Layer 3 — aurora beams (slow diagonal drift) */}
      <motion.div
        className="absolute -inset-[15%] aurora-beam gpu"
        animate={{ x: ["-3%", "3%", "-3%"], y: ["0%", "2%", "0%"] }}
        transition={{ duration: 34, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -inset-[15%] aurora-beam-alt gpu"
        animate={{ x: ["2%", "-2%", "2%"], y: ["1%", "-1%", "1%"] }}
        transition={{
          duration: 42,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 6,
        }}
      />

      {/* Layer 4 — volumetric orbs */}
      {/* Top-left brand orb — slow drift down-right */}
      <motion.div
        animate={{
          x: [0, 60, 0],
          y: [0, 40, 0],
          opacity: [0.55, 0.85, 0.55],
        }}
        transition={{ duration: 32, repeat: Infinity, ease: "easeInOut" }}
        className="absolute -top-[18%] -left-[10%] w-[680px] h-[680px] rounded-full gpu"
        style={{ background: "radial-gradient(circle, rgba(124, 155, 255, 0.16) 0%, transparent 60%)" }}
      />

      {/* Mid-right accent orb — slower, opposite direction */}
      <motion.div
        animate={{
          x: [0, -50, 0],
          y: [0, 30, 0],
          opacity: [0.45, 0.7, 0.45],
        }}
        transition={{
          duration: 38,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 4,
        }}
        className="absolute top-[30%] -right-[12%] w-[580px] h-[580px] rounded-full gpu"
        style={{ background: "radial-gradient(circle, rgba(175, 194, 255, 0.10) 0%, transparent 60%)" }}
      />

      {/* Lower-center deep orb — pulses + slow scale only */}
      <motion.div
        animate={{
          opacity: [0.35, 0.6, 0.35],
          scale: [1, 1.04, 1],
        }}
        transition={{
          duration: 26,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 8,
        }}
        className="absolute bottom-[6%] left-1/2 -translate-x-1/2 w-[540px] h-[540px] rounded-full gpu"
        style={{ background: "radial-gradient(circle, rgba(139, 165, 255, 0.10) 0%, transparent 60%)" }}
      />

      {/* Layer 5 — hairline horizon at the very top of the page */}
      <div className="absolute inset-x-0 top-0 h-px hairline opacity-30" />
    </div>
  );
}
