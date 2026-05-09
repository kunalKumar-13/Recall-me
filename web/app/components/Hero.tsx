"use client";

import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
import { useCallback } from "react";
import { LauncherMockup } from "./LauncherMockup";

function FloatingMemory({ title, type, color, delay, className, parallaxX, parallaxY }: any) {
  return (
    <motion.div
      aria-hidden
      style={{ x: parallaxX, y: parallaxY }}
      className={`absolute z-20 pointer-events-none gpu ${className}`}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.7, delay, ease: [0.32, 0.72, 0, 1] }}
      >
        <motion.div
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 6 + delay, repeat: Infinity, ease: "easeInOut", delay: delay * 2 }}
          className="surface-glass-soft border border-white/[0.08] rounded-xl p-2.5 flex items-center gap-3 shadow-cinematic"
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[9px] font-bold tracking-widest"
            style={{ background: `${color}22`, color: color, border: `1px solid ${color}55` }}
          >
            {type}
          </div>
          <div className="text-[12px] font-medium text-ink-bright pr-2 whitespace-nowrap">{title}</div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}

const ease = [0.32, 0.72, 0, 1] as const;

export function Hero() {
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 130, damping: 22, mass: 0.4 });
  const sy = useSpring(my, { stiffness: 130, damping: 22, mass: 0.4 });

  // Three depth layers — each moves a different amount.
  const orbX = useTransform(sx, [-1, 1], [-22, 22]);
  const orbY = useTransform(sy, [-1, 1], [-14, 14]);
  const haloX = useTransform(sx, [-1, 1], [-12, 12]);
  const haloY = useTransform(sy, [-1, 1], [-8, 8]);
  const ghost2X = useTransform(sx, [-1, 1], [-9, 9]);
  const ghost2Y = useTransform(sy, [-1, 1], [-6, 6]);
  const ghost1X = useTransform(sx, [-1, 1], [-7, 7]);
  const ghost1Y = useTransform(sy, [-1, 1], [-5, 5]);
  const mockX = useTransform(sx, [-1, 1], [-6, 6]);
  const mockY = useTransform(sy, [-1, 1], [-4, 4]);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
      mx.set(x);
      my.set(y);
    },
    [mx, my]
  );

  return (
    <section
      id="top"
      onMouseMove={handleMouseMove}
      className="relative pt-32 md:pt-40 pb-12 md:pb-16 px-6 overflow-hidden"
    >
      {/* ───── Aceternity-style atmospheric layers ───── */}

      {/* Vertical light beams descending from the top — very subtle,
          they read as shafts of light behind the device. */}
      <div
        aria-hidden
        className="absolute left-[18%] top-0 w-px h-[58%] pointer-events-none"
        style={{
          background:
            "linear-gradient(180deg, rgba(124, 155, 255, 0.30), transparent 80%)",
        }}
      />
      <div
        aria-hidden
        className="absolute left-[34%] top-0 w-[2px] h-[68%] pointer-events-none"
        style={{
          background:
            "linear-gradient(180deg, rgba(175, 194, 255, 0.18), transparent 75%)",
        }}
      />
      <div
        aria-hidden
        className="absolute right-[22%] top-0 w-px h-[64%] pointer-events-none"
        style={{
          background:
            "linear-gradient(180deg, rgba(124, 155, 255, 0.24), transparent 80%)",
        }}
      />
      <div
        aria-hidden
        className="absolute right-[38%] top-0 w-[2px] h-[54%] pointer-events-none"
        style={{
          background:
            "linear-gradient(180deg, rgba(139, 165, 255, 0.16), transparent 75%)",
        }}
      />

      {/* Spotlight — wide vertical-elliptical radial gradient cast from
          above the mockup. The "stage light." */}
      <div
        aria-hidden
        className="absolute left-1/2 top-[8%] -translate-x-1/2 w-[1100px] h-[820px] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 50% 60% at 50% 0%, rgba(124, 155, 255, 0.20), transparent 65%)",
        }}
      />

      {/* Hero-local cursor-tracking orb (sits below the spotlight) */}
      <motion.div
        aria-hidden
        style={{ x: orbX, y: orbY }}
        className="absolute -top-[14%] left-1/2 -translate-x-1/2 w-[1100px] h-[520px] rounded-full gpu pointer-events-none"
      >
        <div
          className="w-full h-full rounded-full"
          style={{ background: "radial-gradient(ellipse at center, rgba(124, 155, 255, 0.20) 0%, transparent 60%)" }}
        />
      </motion.div>

      {/* ───── Hero content ───── */}

      <div className="relative max-w-6xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/[0.08] bg-white/[0.02] text-[11px] text-ink-dim tracking-wide"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_10px_rgba(124,155,255,0.7)]" />
          An AI memory layer for your laptop
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease, delay: 0.05 }}
          className="mt-6 text-[52px] md:text-[88px] lg:text-[104px] font-semibold tracking-tightest leading-[0.95] text-gradient"
        >
          Ask your computer
          <br />
          what you forgot.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease, delay: 0.1 }}
          className="mt-6 md:mt-7 text-base md:text-xl text-ink max-w-[520px] mx-auto leading-[1.5]"
        >
          A private memory layer for everything on your laptop. Type the
          half-thought you can&apos;t shake — Recall finds the file, the
          passage, the connected ideas.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease, delay: 0.15 }}
          className="mt-8 flex items-center justify-center gap-3 flex-wrap"
        >
          <a
            href="#download"
            className="px-5 py-3 rounded-lg bg-ink-bright text-bg-deepest text-sm font-medium hover:bg-white transition-colors shadow-cta"
          >
            Download for Windows
          </a>
          <a
            href="#demo"
            className="px-5 py-3 rounded-lg border border-white/[0.10] text-ink-bright/95 text-sm hover:bg-white/[0.04] hover:border-white/20 transition-colors"
          >
            Watch the 30-second demo
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.45, ease, delay: 0.2 }}
          className="mt-4 text-[11px] text-ink-dim tracking-wide"
        >
          Free · Local-first · No account required
        </motion.div>
      </div>

      {/* ───── Floating launcher composition ─────
          Six layers, all parallaxed at different depths so the device
          reads as a real object catching ambient light:

            1. ghost panel 2  (furthest back, biggest, most transparent)
            2. ghost panel 1  (middle)
            3. outer halo
            4. glass frame
            5. launcher mockup
            6. reflection plane (below — the surface it sits on)
      */}
      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease, delay: 0.22 }}
        className="relative mt-10 md:mt-14 max-w-6xl mx-auto px-2"
        style={{ perspective: 1400 }}
      >
        <motion.div
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
          className="relative gpu"
          style={{ transformStyle: "preserve-3d", transform: "rotateX(4deg)" }}
        >
          {/* Layer 1 — furthest ghost panel */}
          <motion.div
            aria-hidden
            style={{ x: ghost2X, y: ghost2Y }}
            className="absolute -inset-x-10 -inset-y-6 rounded-[36px] pointer-events-none gpu"
          >
            <div
              className="w-full h-full rounded-[36px] border"
              style={{
                background: "rgba(255, 255, 255, 0.012)",
                borderColor: "rgba(255, 255, 255, 0.04)",
                transform: "translateY(22px) scale(0.99)",
              }}
            />
          </motion.div>

          {/* Layer 2 — middle ghost panel */}
          <motion.div
            aria-hidden
            style={{ x: ghost1X, y: ghost1Y }}
            className="absolute -inset-x-5 -inset-y-3 rounded-[32px] pointer-events-none gpu"
          >
            <div
              className="w-full h-full rounded-[32px] border"
              style={{
                background: "rgba(255, 255, 255, 0.022)",
                borderColor: "rgba(255, 255, 255, 0.06)",
                transform: "translateY(11px) scale(0.995)",
              }}
            />
          </motion.div>

          {/* Layer 3 — outer halo */}
          <motion.div
            aria-hidden
            style={{ x: haloX, y: haloY }}
            className="absolute -inset-x-32 -inset-y-24 pointer-events-none gpu"
          >
            <div
              className="w-full h-full rounded-[3rem]"
              style={{ background: "radial-gradient(circle, rgba(124, 155, 255, 0.20) 0%, transparent 60%)" }}
            />
          </motion.div>

          {/* Layer 4-5 — glass frame + launcher */}
          <motion.div
            style={{ x: mockX, y: mockY }}
            className="
              relative rounded-[28px] p-[6px]
              bg-gradient-to-br from-white/[0.10] via-white/[0.03] to-white/[0.01]
              border border-white/[0.08]
              shadow-cinematic
              gpu
            "
          >
            <div
              aria-hidden
              className="absolute inset-x-12 top-0 h-px hairline opacity-60"
            />
            <div className="rounded-[22px] overflow-hidden">
              <LauncherMockup />
            </div>
          </motion.div>

          {/* Layer 6 — reflection plane (below the device — the surface it
              casts a soft glow onto). Embeds the mockup in space rather
              than presenting it in a box. */}
          <div
            aria-hidden
            className="absolute left-1/2 -translate-x-1/2 -bottom-16 w-[78%] h-32 rounded-[100%] pointer-events-none"
            style={{
              background:
                "radial-gradient(ellipse at top, rgba(124, 155, 255, 0.16) 0%, transparent 70%)",
            }}
          />

          {/* Floating Memory Cards */}
          <FloatingMemory
            title="healthcare pitch deck from last winter"
            type="PDF"
            color="#EF4444"
            delay={0.8}
            parallaxX={ghost2X}
            parallaxY={ghost2Y}
            className="-left-[8%] top-[15%]"
          />
          <FloatingMemory
            title="grading logic for multi-agent evals"
            type="PY"
            color="#7C9BFF"
            delay={1.1}
            parallaxX={ghost1X}
            parallaxY={ghost1Y}
            className="-right-[10%] top-[45%]"
          />
          <FloatingMemory
            title="RL reward discussion"
            type="TXT"
            color="#94A3B8"
            delay={1.4}
            parallaxX={haloX}
            parallaxY={haloY}
            className="-left-[4%] top-[70%]"
          />
        </motion.div>
      </motion.div>
    </section>
  );
}
