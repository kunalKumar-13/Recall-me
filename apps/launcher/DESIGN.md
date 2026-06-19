# Recall Launcher — Design Language

This is the design language for the new launcher. Follow it exactly.

## Soul

Recall restores continuity. The panel should feel like a calm, instant,
native surface that hands you back your own momentum — not a search bar,
not a command palette. Raycast-level polish, its own identity.

## Signature — the thread

A hairline vertical spine runs down the left of the results; each row
sits on it as a node. Moments (●), sessions (◇), micro-contexts (✦) are
strung on one thread — continuity drawn, not decorated with a generic
accent bar. This must be unmistakably Recall.

## Palette

Warm dark graphite (not pure black) under native macOS vibrancy. One
accent — **amber `#E8B45A`**, the color of a recalled, lamp-lit thing —
spent only on the selected row and its node. Restrained per-layer node
hues:

- moment — amber
- session — slate-blue `#8FB0D6`
- context — soft violet `#B79CE0`

No second bright accent.

## Type

Native system face (SF) for every title/label — correct and instant.
Monospace (SF Mono) for all provenance — timestamps, domains, file
paths, "why matched", key hints — because Recall's memory lives in plain
auditable files on disk, so the data *about* a memory is set in the
typeface of data.

## Material & shape

Borderless transparent window, native vibrancy (`HudWindow`), 13px
radius, hairline border, content-fit height that grows/shrinks like
Raycast (never a tall empty blurred panel), centered in the upper third.

## Motion

Minimal and fast. Selection moves instantly; the only transition is a
~90ms background fade on the selected row. No bounce, no slide, no
spinners.

## Quality bar

- Summon-to-visible under 100ms, no flicker on show.
- Keyboard-first: arrows move, Enter opens/restores, Esc closes,
  Cmd+C copies path; mouse is for the tray only.
- Hides on blur.
- It must feel native, not web.

## States, continuity-first

1. **Recovery** — the resting state shown before any typing: "Continue
   where you left off," real recovery candidates with their continuation
   plans. The hero.
2. **Search** — opt-in once you type: episodic + session + micro-context
   on the thread.
3. **Resume** — Enter runs the choreographed restore: files, then chats,
   then tabs by domain, then searches.
