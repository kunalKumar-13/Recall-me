# MOTION.md — the motion contract

Recall has motion in three places — the launcher, the extension
popup, and the website. They drifted: different durations, different
curves, different intent. This file is the single contract.

**One principle: motion is continuity, not delight.** Every
animation in Recall exists to help the eye follow a change — to
preserve context as something appears, expands, or replaces
something else. Motion that exists to feel nice is not allowed. If
an animation were removed and the user lost nothing, it should not
be there.

---

## Durations

One ladder, three rungs. Pick the rung by *what changed*, never by
taste.

| Rung | Duration | Used for |
|---|---|---|
| **Hover / press** | **100–140 ms** | a row lighting on hover, a button settling under a press |
| **Expand / collapse** | **180–220 ms** | a card opening, an accordion, a panel sliding in |
| **Section reveal** | **250 ms** | a whole section appearing as a surface loads |

Nothing in Recall animates longer than 250 ms. A 400 ms transition
is not "smooth," it is *slow* — the user is waiting for the UI to
finish performing.

## Easing

**One family, every surface:** `cubic-bezier(0.32, 0.72, 0, 1)`.

A calm decelerating curve — fast to start, gentle to settle, **no
overshoot**. The launcher (Qt), the extension (Framer Motion), and
the website (Framer Motion) all use this exact curve. It is the
`EASE` constant in the extension's `lib/motion.ts` and the
`[0.16, 1, 0.3, 1]`-family curve on the website; they are tuned to
read identically.

## The three allowed motions

| Motion | What it is | Where |
|---|---|---|
| **Fade** | opacity 0 → 1 | content arriving / leaving |
| **Expand** | opacity + a few px of travel (≤ 8 px) | a card or section settling into place |
| **Slide** | a view replacing another along one axis | launcher ↔ search, popup ↔ settings |

That is the whole vocabulary. A new kind of motion needs a row in
this table and a reason.

## Forbidden

- **Bounce / spring overshoot.** The easing curve has no overshoot
  for a reason. Nothing in Recall springs.
- **Floating / looping animation.** No idle drift, no breathing
  glow, no ambient particles on a live surface.
- **Staggered choreography for its own sake.** A section's children
  may stagger by ~50 ms so the surface settles top-down; more than
  that is a performance.
- **Motion on data the user is reading.** Numbers do not count up,
  text does not type on.
- **Anything that ignores `prefers-reduced-motion`.** Every surface
  collapses all of the above to near-instant under that media query.

## Per-surface mapping

| | Hover | Expand | Reveal | Curve |
|---|---|---|---|---|
| Launcher (Qt) | row highlight, instant-ish | preview pane | digest on open | matched curve |
| Extension (Framer Motion) | `calmFast` 180 ms | `calm` 260 ms | `staggered()` ~280 ms | `EASE` |
| Website (Framer Motion) | link/opacity | `whileInView` once | section entrance | calm bezier |

The extension's `lib/motion.ts` is the reference implementation —
new surfaces copy its constants rather than inventing their own.

---

*If motion does not preserve continuity, cut it.*
