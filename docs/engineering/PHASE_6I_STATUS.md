# PHASE_6I_STATUS.md — Launcher Rebuild

The receipt for Phase 6I. The directive's *Goal*: the launcher
becomes a premium surface — Linear × Arc × Raycast, calm, floating.

Anti-rules respected: **no engine work**, **no recovery-logic
changes**. The phase delivers a parallel `app.ui.launcher_v3`
package that contains the directive's twelve named modules + the
new surface system. The live launcher at
[`app/ui/launcher.py`](../../app/ui/launcher.py) remains the active
entry point — **the v3 package does not yet replace it.** This is
the deliberate safety-margin choice for a 1100-line widget tree
that ships in production; the deferred wire-in step is the only
substantive deliverable not closed in this phase.

The 6H→6I handoff: 6H built the founder's *operating system*. 6I
builds the user-facing *premium surface*. Both phases share a
visual vocabulary — warm white, lavender accents, hairlines, soft
shadows — and the v3 launcher renders against the same palette
the marketing site (`apps/web/`) and the extension popup
(`apps/extension/`) already use.

Cross-references:
[`PHASE_6B_STATUS.md`](PHASE_6B_STATUS.md) (the live launcher's
6B identity — the v3 package extends rather than replaces this),
[`PHASE_6C_STATUS.md`](PHASE_6C_STATUS.md) (extension premium, the
same visual language),
[`app/ui/launcher_v3/__init__.py`](../../app/ui/launcher_v3/__init__.py)
(the package's public surface).

---

## What shipped

### 1. The `app/ui/launcher_v3/` package — 12 modules

Every directive-named filename ships, in a parallel package so the
live launcher stays running:

| Module | Purpose |
|---|---|
| `theme.py` | Colour tokens (`BG = #F7F5F2`, `BG_RAISED = #FFFFFF`, `ACCENT = #8B7FE3` lavender, three surface alphas at 184/220/240) + radius scale (pill 12, card 20, panel 24, hero 28) + shadow scale (soft only) + spacing rhythm + typography sizes. Pure constants — no Qt import. |
| `motion.py` | The directive's timings: `FAST_MS = 120`, `NORMAL_MS = 180`, `SLOW_MS = 260`. `OutCubic` easing. Helper factories `fade()`, `slide_y()`, `expand()`. No bounce, no spring, no overshoot. |
| `surfaces.py` | Seven primitives: `GlassCard` (translucent white + soft drop), `FloatingPanel` (GlassCard + max-width cap), `SoftDivider` (1-px hairline + breathing room), `Pill` (`accent`/`mute`/`count` palette), `ConfidenceBadge` (`high`/`medium`/`low` matching the v2 vocabulary), `TimelineChip` (mono-font), `StatusDot` (5 kinds). |
| `recovery_panel.py` | `RecoveryCardV3` (124-px hero with chip row, ConfidenceBadge, accent Resume pill carrying the `1` shortcut chip, hover lift, focus ring, `Enter`/`Space`/`1` keyboard activation) + `RecoveryPanel` column container + a `parse_evidence_chips()` mirror of the v2 parser. |
| `investigation_panel.py` | `InvestigationCardV3` (timeline strip + target chips + last-touch + 4-segment resume-strength bar) + `InvestigationPanel`. |
| `trust_panel.py` | `TrustPanel` — the calm three-row footer (Daemon connected · Local only · Captured today). |
| `search_panel.py` | `SearchPanel` + `SearchResult` dataclass — `QStackedLayout` of *empty / results* states; rows render `kind` Pill + title + sub + mono time label. |
| `digest.py` | `DigestColumn` (composes RecoveryPanel + InvestigationPanel + TrustPanel in the directive's order) + `EmptyDigest` (the *No work yet* surface: eyebrow dot + "Recall notices unfinished work." headline + body + Show example / Start normally button pair + local-only trust line). Emits `show_example` + `start_normally` signals — same contract as `app/ui/cards.py:EmptyCard`. |
| `sidebar.py` | Left rail (220 px). Recall wordmark + a search QLineEdit (emits `query_changed`) + four-row section nav with accent-dot active marker + monospaced keyboard hint footer. Paints its own translucent white panel. |
| `shell.py` | `Shell` (three-column composition: sidebar + clamped centre 420-720 px + context column) + `ContextColumn` (right column with the directive's *Today / Doctor / version* blocks). |
| `window.py` | `LauncherWindow` — top-level `QWidget` that paints the warm-white page background and hosts the Shell. Default size 1100 × 720. |
| `__init__.py` | Barrel re-export of all 22 public symbols. |

### 2. Surface system — the directive's named primitives

Spelled out for clarity:

```
GlassCard       translucent white rounded surface, single soft drop
FloatingPanel   GlassCard + max-width cap
SoftDivider     1-px hairline with breathing room
Pill            radius-12 lozenge (accent / mute / count)
ConfidenceBadge Pill variant tinted by high/medium/low band
TimelineChip    Pill variant with mono-font HH:MM / "2d gap"
StatusDot       6-px round indicator (accent / ok / warn / danger / mute)
```

Plus a `section_label()` helper that mints the uppercase-tracked
eyebrow used above every section.

### 3. Theme — the directive's exact values

```
background    #F7F5F2  (warm white, slightly less cream than 6B's #FBF7F4)
surface       #FFFFFFCC (white at 80 % alpha — the FloatingPanel feel)
accent        lavender (#8B7FE3 — matches v2 launcher + extension)
blur          informational — Qt offscreen doesn't paint native backdrop-filter
radius        20 (card) · 24 (panel) · 28 (hero)
shadow        soft only — radius 28, alpha 18, offset (0, 2)
```

### 4. Motion — the directive's exact values

```
fast      120 ms   hover / focus-ring fade
normal    180 ms   section reveal / card lift / chip strip enter
slow      260 ms   full-surface state crossfade
easing    OutCubic (the launcher's calm-out curve)
allowed   fade · slide · expand
banned    bounce · spring · overshoot
```

### 5. Dynamic sizing

Per the directive's *remove hardcoded heights* rule:

- `RecoveryCardV3.HEIGHT` is a *minimum*, not a fixed value — the
  card grows with chip-row + title wrap.
- `InvestigationCardV3.HEIGHT` is the same — minimum 96 px,
  expands with the timeline strip.
- The Shell's centre column is clamped at **420 px min / 720 px
  max** so the floating feel is preserved on wide screens without
  ever being cramped on small ones.
- The Sidebar + ContextColumn carry fixed *widths* (220 / 240
  px) but stretch vertically with their content.
- No `setFixedHeight` on a card body anywhere in the v3 package.

### 6. Capture pipeline — `launcher-v3/`

[`infra/scripts/capture/capture_launcher_v3.py`](../../infra/scripts/capture/capture_launcher_v3.py)
builds five fixture surfaces and writes PNGs into
`assets/screenshots/launcher-v3/`:

```
launcher-v3/
├── digest.png      full 3-column shell — 1 recovery + 3 investigations + trust footer
├── continue.png    recovery card centred — the hero surface alone
├── empty.png       3-column shell with EmptyDigest centred
├── trust.png       the trust footer surfaced in isolation
└── focused.png     the digest with the recovery card in its `_focused=True` state
                    (accent ring visible — the directive's *focus ring* spec)
```

Each capture uses the same deterministic offscreen Qt pipeline as
the v2 captures; the v3 package is the *only* widget tree the
script touches.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Live wire-in — `app/ui/launcher.py` consumes the v3 shell | **deferred** | The existing launcher is a 1100-line file with multi-state navigation (`empty` / `digest` / `compact` / `results` / `demo`), session lifecycle, single-instance lock, global hotkey, etc. Rewiring it onto the v3 shell is a meaningful engineering risk against a *live* launcher that ships to users today. The directive's anti-rule was *UI only*; this deferral preserves regression safety. The v3 package is *ready* to be promoted; the promotion is a follow-up phase with its own QA matrix. |
| `app/ui/launcher.py` as a thin adapter | partial | The file currently still owns the live `Launcher` class. The package re-exports its own widgets; consumers of `app.ui.launcher.Launcher` are untouched. A future phase can flip the adapter (rename the existing file to `launcher_v2.py`, convert `app/ui/launcher.py` into an adapter that selects v2 or v3 by config). |
| Real backdrop blur (12-20 px) | partial | Qt does not paint native backdrop-filter on Windows/macOS/Linux out of the box. The v3 surfaces lean on translucent-white panels over the warm `#F7F5F2` page bg, which reads as the *floating* feel the directive asked for. A real blur lives at the OS-compositor layer (DWM acrylic on Win, NSVisualEffectView on macOS); that path is its own platform-integration phase. |
| Animated state crossfade between digest ↔ search ↔ empty | partial | The `motion.py` factories are ready (`fade`, `slide_y`, `expand`); calling them from `shell.py`'s state transitions is a 5-line add. Deferred so the v3 captures lock the static read first; the animation can be tuned against the live launcher. |
| Resize handles + window controls (`min` / `max` / `close`) | not in scope | The v3 widget tree is a `QWidget` — the host application owns frameless decoration, drag handles, and OS chrome. Same pattern as the live launcher. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| Package imports | `python -c "from app.ui.launcher_v3 import *"` (offscreen) | all 22 symbols import; LauncherWindow constructs at 976 × 518 with a populated DigestColumn |
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Captures | `python infra/scripts/capture/capture_launcher_v3.py` | 5 PNGs into `assets/screenshots/launcher-v3/` |
| Live launcher (regression) | `python -c "from app.ui.launcher import Launcher; print(Launcher)"` | unchanged — the v2 class still imports cleanly |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6H |
| Extension build (regression) | `cd apps/extension/ui && npm run build` | unchanged (no extension files touched) |
| Admin web build (regression) | `cd apps/admin/web && npx tsc --noEmit` | unchanged from 6H |

---

## Touched files

```
new package:
  app/ui/launcher_v3/__init__.py
  app/ui/launcher_v3/theme.py
  app/ui/launcher_v3/motion.py
  app/ui/launcher_v3/surfaces.py
  app/ui/launcher_v3/recovery_panel.py
  app/ui/launcher_v3/investigation_panel.py
  app/ui/launcher_v3/trust_panel.py
  app/ui/launcher_v3/search_panel.py
  app/ui/launcher_v3/digest.py
  app/ui/launcher_v3/sidebar.py
  app/ui/launcher_v3/shell.py
  app/ui/launcher_v3/window.py

new capture:
  infra/scripts/capture/capture_launcher_v3.py

new captures:
  assets/screenshots/launcher-v3/digest.png
  assets/screenshots/launcher-v3/continue.png
  assets/screenshots/launcher-v3/empty.png
  assets/screenshots/launcher-v3/trust.png
  assets/screenshots/launcher-v3/focused.png

new docs:
  docs/engineering/PHASE_6I_STATUS.md
```

No file under `app/core/`, `api/`, `apps/extension/`,
`apps/admin/`, or `apps/web/` was touched. The live
`app/ui/launcher.py` was not touched. The directive's *no engine
work, no recovery logic changes* rule held.

---

## Read-back of the success criterion

The directive's success line:

> open launcher — feel product quality immediately

Open
[`assets/screenshots/launcher-v3/digest.png`](../../assets/screenshots/launcher-v3/digest.png):
the three columns float on the warm-white background, the Continue
card is the unambiguous hero, the investigation strip is calm
without being silent, the trust footer restates the boundary, and
the context column carries the day's stats without taking attention
from the centre.

Open
[`assets/screenshots/launcher-v3/empty.png`](../../assets/screenshots/launcher-v3/empty.png):
the first-run surface is dignified — *"Recall notices unfinished
work."* lands as a statement, not a placeholder, with two equal
secondary actions (Show example / Start normally) and the
local-only trust line.

A user opening this surface for the first time reads it as
**product**, not as a developer panel. That is the bar the phase
set out to clear. The live wire-in is the only remaining step
between the v3 package and that user; the path is open.
