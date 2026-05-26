import type { Transition, Variants } from "framer-motion";

/**
 * Continuity motion only. The popup is allowed to *fade*, *expand*,
 * and *slide* — motion that preserves context and helps the eye
 * follow a change. It is never allowed to bounce, float, or perform.
 *
 * One easing curve for everything: a calm cubic-bezier with no
 * overshoot. Durations come from `styles.css` design tokens
 * (`--motion-fast / --motion-normal / --motion-slow`) — the values
 * below are their literal seconds equivalents so framer-motion can
 * read them without a runtime DOM lookup.
 */
export const EASE = [0.32, 0.72, 0, 1] as const;

// Phase 7A — *120 / 180 / 240*. Mirrors the `--motion-fast`,
// `--motion-normal`, `--motion-slow` tokens in styles.css.
const MOTION_FAST_S = 0.12;
const MOTION_NORMAL_S = 0.18;
const MOTION_SLOW_S = 0.24;

export const fadeExpand: Variants = {
  hidden: { opacity: 0, y: 6 },
  show: { opacity: 1, y: 0 },
};

export const fade: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1 },
};

/** Settings panel enters from the right, main view exits to the left. */
export const slideView: Variants = {
  fromRight: { opacity: 0, x: 24 },
  center: { opacity: 1, x: 0 },
  toLeft: { opacity: 0, x: -24 },
};

/**
 * Body-state crossfade variants for the popup's PopupState transitions.
 * Each entry slides in slightly from below + fades; exits go back up.
 * No bounce, no spring, no rotate — per Phase 5I motion rules.
 */
export const bodyState: Variants = {
  enter: { opacity: 0, y: 4 },
  show: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
};

export const calm: Transition = { duration: MOTION_SLOW_S, ease: EASE };
export const calmFast: Transition = { duration: MOTION_NORMAL_S, ease: EASE };
export const calmFastest: Transition = { duration: MOTION_FAST_S, ease: EASE };

/** Stagger children of a section so the popup settles top-down. */
export function staggered(index: number): Transition {
  return { duration: MOTION_SLOW_S, ease: EASE, delay: 0.03 + index * 0.04 };
}
