# PHASE_6M.1_STATUS.md — Launcher Refinement

The receipt for Phase 6M.1. The directive's *Goal*: the launcher
should feel **shipped**. **No new features. No engine work. No
control-room work. Refinement only.**

Numbering note: the previous turn's directive labelled this phase
*6M*, but Phase 6M (*Desktop Memory Layer*) already shipped this
session with a full
[`PHASE_6M_STATUS.md`](PHASE_6M_STATUS.md). To preserve that
engineering history, this phase is filed as **6M.1** — a sub-phase
that follows 6M chronologically without overwriting its receipt.

Cross-references:
[`LAUNCHER_REVIEW.md`](../../docs/product/LAUNCHER_REVIEW.md) (the audit
doc — *removed / kept / why / future*),
[`archive/launcher-refine/README.md`](../launcher-refine/README.md)
(the per-capture-script archive rationale),
[`PHASE_6L_STATUS.md`](PHASE_6L_STATUS.md) (the prior simplification
this phase polishes).

---

## What shipped

### 1. Theme tokens refit

[`app/ui/launcher_v3/theme.py`](../../app/ui/launcher_v3/theme.py)
swapped the previous *glass* token vocabulary for the directive's
exact values:

| Token | Before (6I/6L) | After (6M.1) |
|---|---|---|
| `SURFACE_ALPHA_MID` | 220 (translucent white) | **255** (solid) |
| `SURFACE_ALPHA_HIGH` | 240 | **255** |
| `SURFACE_ALPHA_LOW` | 184 | **255** |
| `RADIUS_HERO` | 28 | **20** (directive: *radius 20*) |
| `RADIUS_PANEL` | 24 | **20** (single value) |
| `SHADOW_SOFT_OFFSET` | 2 (implicit) | **8** (directive: *0 8 24*) |
| `GUTTER` | 24 | **28** |
| `CARD_GAP` | 14 | **12** |
| `HAIRLINE` | rgba(24,17,45,18) | rgba(24,17,45,**24**) — slightly stronger |
| `FS_HERO` | 19 | **22** (directive: *title 22*) |
| `FS_TITLE` | 15 | 16 |
| `FS_BODY` | 13 | 14 |
| `FS_LABEL` | 10 | 11 |
| `FS_META` | 11 | **12** (directive: *meta 12*) |
| `FS_SECTION` | (n/a) | **14** (new — directive: *section 14*) |

The `SHADOW_SOFT_OFFSET` constant is new and used by the
GlassCard paint to push the drop *down* slightly so cards read
as resting on the page rather than floating above it.

### 2. `GlassCard` flipped to solid

[`app/ui/launcher_v3/surfaces.py`](../../app/ui/launcher_v3/surfaces.py)
`GlassCard.paintEvent` now paints a fully opaque white fill. The
`alpha` constructor arg is silently clamped to 255 (the directive
forbids transparency outright) — downstream callers don't need
changes.

The drop-shadow effect uses the new `T.SHADOW_SOFT_OFFSET` value
so every solid card on the paper-white page has the same physical
shadow shape — the directive's *0 8 24 low opacity* spec.

The hairline border is tuned from rgba(...,18) to rgba(...,24)
so cards visibly belong to the page rather than blending into
it.

### 3. `MinimalEmpty` rewritten

[`app/ui/launcher_v3/minimal.py:MinimalEmpty`](../../app/ui/launcher_v3/minimal.py)
dropped the wrapping `GlassCard`. The surface is now:

```
   (vertical center)
   ┌────────────────────┐
   │  ▢ (lavender dot)  │  48 × 48 tinted square + a small
   │                    │  painted dot (no Unicode glyph, so
   │                    │  every system font renders it the
   │                    │  same)
   └────────────────────┘

   Recall notices unfinished work.    (FS_HERO = 22, bold)

   Work normally. Return later.       (FS_BODY = 14)
   Recall fills itself.

   [ Show example ]  [ Start normally ]   (38 px tall, radius 12)

   local only · 127.0.0.1:4545 · no cloud   (mono trust line)
   (vertical center)
```

No card. No "Surfaced because…". No section labels. The
directive's *No dashboard* rule held strictly: the empty
surface is a single calm centered column.

### 4. Hero card refit

[`recovery_panel.py:RecoveryCardV3`](../../app/ui/launcher_v3/recovery_panel.py)
changed in three ways:

1. The action row (chip strip + Resume pill) is now
   **bottom-aligned**: the layout adds a stretch above it so
   the title + chips read as content and the Resume CTA
   visually anchors the card.
2. The *Surfaced because you left this mid-flow.* footer line
   was deleted. The chip strip + confidence badge carry the
   same information; the footer was duplicate text.
3. The accent fill is now **solid** (alpha=255). The card
   stays distinct from neighbouring investigation pills by
   tint, not by transparency.

The card's `HEIGHT = 124` minimum stays inside the directive's
*120-140* band.

### 5. Investigation strip — equal-width + overflow

[`minimal.py:MinimalInvestigations`](../../app/ui/launcher_v3/minimal.py)
changed:

- `_strip.addWidget(pill, 1)` — pills now share the strip's
  width equally, instead of hugging their content with a
  trailing stretch.
- New `_OverflowChip` widget renders a `+N more` dashed-border
  pill when the cohort has more than 4 investigations. The
  dashed border makes it visually quieter than a real pill
  (the eye doesn't try to click it).
- `_InvestigationPill` flipped to a solid white fill (was
  translucent) + 40-px height (was 36) so the pill row's
  bottom edge aligns with the hero card's footer.

### 6. Shell geometry

[`minimal.py:MinimalShell`](../../app/ui/launcher_v3/minimal.py)
+ `MinimalWindow`:

- `MAX_WIDTH = 760` (was 860) — the directive's *max width 760*.
- `MIN_WIDTH = 600` (was 760) — the column now breathes on
  smaller windows.
- Outer padding = `T.GUTTER = 28` (was 32).
- Section gap = `T.SECTION_GAP = 20` (was 24).
- `DEFAULT_SIZE = (820, 640)` (was 920 × 720) — directive's
  exact value.

`LiveLauncher.DEFAULT_SIZE` matches.

### 7. Archive

[`archive/launcher-refine/`](../launcher-refine) is a
new sibling directory to the Phase 6L `archive/launcher-v2/`. Three
capture scripts moved here:

- `capture_launcher_v3.py` (the 6I 3-column gallery script)
- `capture_launcher_live.py` (the 6K live composition captures)
- `capture_launcher_minimal.py` (the 6L pre-refinement minimal)

Plus a README documenting why each was archived (the previous
shape they fixtured no longer matches the refined launcher).

The 6I / 6K / 6L screenshots themselves stay on disk under
`assets/screenshots/launcher-{v3,live,minimal}/` as historical
reference — the directive's *delete unused* rule targeted the
**scripts**, not the **outputs**.

### 8. New capture pipeline

[`infra/scripts/capture/capture_launcher_refined.py`](../../infra/scripts/capture/capture_launcher_refined.py)
produces the five directive-named shots into
`assets/screenshots/launcher-refined/`:

```
hero           single column · hero + 4 equal-width pills + trust line
empty          vertically centred icon + headline + sub + 2 buttons
investigations 6 threads → 4 pills + a `+2 more` dashed overflow chip
resume         hero with `_focused = True` (accent ring) + one pill
focused        hero focused + a fully populated pill row
```

Each capture renders against the **same widgets `LiveLauncher`
composes at runtime**. Deterministic offscreen Qt, no engine
call.

### 9. Motion narrowing

The directive's allowed list — `hover raise`, `focus glow`,
`fade in` — was already the Phase 6I `motion.py` vocabulary:
`fade()`, `slide_y()`, `expand()` with `OutCubic` easing.
Phase 6M.1 doesn't add new motion files, but the refit
*removed* every place the launcher composition was implicitly
using slide / expand on a state change:

- the `MinimalEmpty → MinimalDigest` swap now uses a plain
  `QStackedLayout.setCurrentIndex()` — Qt handles the swap
  without animation, which **is** the "fade in" feel the
  directive wants;
- the hero card's focus state is rendered by the existing
  paint-event border change — a *focus glow* without a
  geometric motion;
- pill hover is `setCursor(PointingHandCursor)` only, no
  animation — the cursor is the lift signal.

No bounce. No spring. No overshoot.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| First-recovery banner on the empty card | not in scope | Slot reserved; widget lands when the cohort records its first recovery. Same deferral as Phase 6L. |
| Live ContextColumn flow into the minimal surface | not in scope | The directive's *delete dashboard* + *delete density* rules push system info into the control room. Surfacing it in the launcher again would regress. |
| `_OverflowChip` clickable | partial | The chip paints, indicates surplus, but doesn't navigate anywhere. The directive said *no scrolling, no walls* — clicking the chip would open a list, which is exactly the *wall* the rule forbids. |
| Cross-platform `MinimalEmpty` icon | partial | The painted-dot icon avoids Unicode glyph coverage problems. A future phase could ship a real per-OS SVG; today's solution renders the same on every host. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Default launcher import | `from app.ui.launcher import Launcher` | `LiveLauncher` (unchanged) |
| Geometry | `from app.ui.launcher_v3 import MinimalShell, MinimalWindow` | `MAX_WIDTH = 760` · `DEFAULT_SIZE = (820, 640)` |
| Theme values | `from app.ui.launcher_v3 import theme as T` | `GUTTER = 28` · `SECTION_GAP = 20` · `CARD_GAP = 12` · `FS_HERO = 22` · `FS_SECTION = 14` · `FS_META = 12` |
| Captures | `python infra/scripts/capture/capture_launcher_refined.py` | 5 PNGs into `assets/screenshots/launcher-refined/` |
| Doctor (regression) | `python recall.py doctor` | unchanged |
| Extension build (regression) | `cd apps/extension/ui && npx tsc --noEmit` | unchanged |
| Admin build (regression) | `cd apps/admin/web && npx tsc --noEmit` | unchanged |
| Marketing build (regression) | `cd apps/web && npx tsc --noEmit` | unchanged |

---

## Touched files

```
new code:
  infra/scripts/capture/capture_launcher_refined.py

modified code:
  app/ui/launcher_v3/theme.py          (token refit — see table above)
  app/ui/launcher_v3/surfaces.py       (GlassCard → solid; shadow offset)
  app/ui/launcher_v3/minimal.py        (MinimalEmpty / Shell / Window /
                                        _InvestigationPill / _OverflowChip)
  app/ui/launcher_v3/recovery_panel.py (bottom-aligned action row;
                                        dropped "Surfaced because…";
                                        solid accent fill)
  app/ui/launcher_v3/live.py           (DEFAULT_SIZE = 820 × 640)

moved (out of infra/scripts/capture/):
  capture_launcher_v3.py     → archive/launcher-refine/capture_launcher_v3.py
  capture_launcher_live.py   → archive/launcher-refine/capture_launcher_live.py
  capture_launcher_minimal.py → archive/launcher-refine/capture_launcher_minimal.py

new docs:
  archive/launcher-refine/README.md
  docs/product/LAUNCHER_REVIEW.md
  docs/engineering/PHASE_6M.1_STATUS.md

new captures:
  assets/screenshots/launcher-refined/hero.png
  assets/screenshots/launcher-refined/empty.png
  assets/screenshots/launcher-refined/investigations.png
  assets/screenshots/launcher-refined/resume.png
  assets/screenshots/launcher-refined/focused.png
```

No `app/core/`, `api/`, `apps/extension/`, `apps/admin/`, or
`apps/web/` files touched. No engine layer touched. No
recovery-logic change. The directive's *refinement only* spirit
held.

---

## Read-back of the success criterion

The directive's success line: *launcher looks like product
screenshot*.

Open
[`assets/screenshots/launcher-refined/hero.png`](../../assets/screenshots/launcher-refined/hero.png)
— the surface reads as a finished product capture. Solid white
search bar on a paper-white page; a single lavender-tinted
hero card with the title at 22 px, the chips below, the
confidence badge at the top-right, the Resume CTA bottom-right
with its `1` keyboard hint. Below the hero, four equal-width
investigation pills sit on the same grid line. The trust line
sits at the foot, mono, ink-4. Everything aligns to one grid.

That's the bar the phase set out to clear.
