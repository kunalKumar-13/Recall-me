# LAUNCHER_REGRESSION.md — the 6M.1 launcher regression

The directive-required audit doc explaining the Phase 6M.1 →
6M.2 recovery. Three sections: **why the old looked better**,
**what changed in 6M.1 that broke it**, **what 6M.2 fixed**.

Pairs with
[`PHASE_6M.2_STATUS.md`](../../archive/phase-status/PHASE_6M.2_STATUS.md)
(the engineering receipt) and the prior
[`LAUNCHER_REVIEW.md`](LAUNCHER_REVIEW.md) (6M.1's own
audit doc, which described the problems 6M.1 was *trying*
to fix).

---

## What "the old" was

Two iterations had the launcher feeling right:

- **6I** (the parallel v3 package), captured at
  `assets/screenshots/launcher-v3/`. A premium 3-column shell —
  sidebar nav + centre column + context column — at
  1180 × 760. Felt like an *editor*, not a dashboard. The
  weight of the surface came from the visual rhythm of the
  three columns, not from the size of the cards.
- **6L** (the simplified single-floating-surface), captured at
  `assets/screenshots/launcher-minimal/`. A single 920 × 720
  column, 760-860 width range, a hero card, four horizontal
  investigation pills. *Calmer* than 6I; still recognisably
  *Raycast / Arc utility* shaped because each element was
  small relative to the page.

Both reads were the same thing: **the launcher carried itself
on the visual proportions of the cards inside it, not on the
size of the window**.

## Why the old looked better

| Read | 6I + 6L did | The user's eye does |
|---|---|---|
| **Window is a tool** | 920 × 720 (6L) is just barely too big to be a *toolbar* and exactly right to be a *page-on-top-of-pages*. | Stops looking for chrome; reads the surface as content. |
| **Card is the focal point** | Hero at 124 px, chip strip + Resume in one row. | Eye lands on the title, then chips, then Resume CTA — the read takes < 1 second. |
| **Cards sit on a page** | Soft drop shadow, 1-px hairline, accent-tinted hero. | Cards read as *physical objects on paper*; the eye distinguishes them from the page without effort. |
| **Pills look like ambient surfaces** | 4 pills at 36-40 px tall, soft shadow, equal spacing. | The pills read as a *strip*, not as four buttons-with-state. |

## What 6M.1 changed that broke it

Phase 6M.1 was directed as a *refinement* — solid cards, paper-
white page, tightened shadow, tighter typography. The
refinement landed three changes that *looked correct in
isolation* but accumulated into a regression:

1. **Window size grew slightly** from 920 × 720 → 820 × 640.
   The intent was *more compact*; the effect was *the cards
   look bigger inside a smaller window*. The hero card's
   124-px height occupied a larger share of the visible
   surface — the surface read as *card-with-page-around-it*
   instead of *page-with-card*.
2. **Search bar stretched edge-to-edge** inside the inner
   column. The 6L search bar had the same shape but the
   column was wider, so the bar's max-width felt right; in
   the 6M.1 narrower window, the same full-width search bar
   read as *the search bar is the page*.
3. **Investigation pills bumped to 40 px and gained equal-
   width stretch**. With the previous flush-left layout, the
   pills hugged their content and the row read as "four
   things floating left." With equal-width stretch in a
   narrower window, the same four pills filled the row edge-
   to-edge and read as "four buttons that take up half the
   surface."

Net effect: the surface read as a **dashboard** — busy, full,
asking for attention — rather than the *Raycast utility* it
had been at 6L.

## What 6M.2 fixed

The directive's recovery values, translated into the in-source
constants:

| Surface | 6M.1 (regressed) | 6M.2 (recovery) |
|---|---|---|
| `LiveLauncher.DEFAULT_SIZE` | `(820, 640)` | **`(720, 520)`** |
| `MinimalWindow.DEFAULT_SIZE` | `(820, 640)` | **`(720, 520)`** + `MAX_SIZE = (760, 560)` |
| `MinimalShell.MAX_WIDTH` | `760` | **`640`** |
| `MinimalShell.MIN_WIDTH` | `600` | **`520`** |
| `T.GUTTER` (outer padding) | `28` | **`20`** |
| `T.SECTION_GAP` (between sections) | `20` | **`16`** |
| `T.CARD_GAP` (cards/strip↦returns) | `12` | unchanged |
| `T.RETURNS_GAP` (returns↦trust) | (n/a) | **`8`** |
| `MinimalSearchBar` width | full-width | **max 640 px, centred** |
| `MinimalSearchBar` height | `40` | **`48`** (taller — the *tool* shape) |
| `MinimalSearchBar` placeholder | *Search the work you remember…* | ***Search investigations…*** |
| `RecoveryCardV3.HEIGHT` | `124` | **`92`** + `MAX = 116` cap |
| Hero layout | header (eyebrow+confidence) → title → action row | **2×2 grid** — title TL · confidence TR · chips BL · Resume BR |
| `_ResumePill` height | `34` | **`36`** (directive's exact value) |
| `MinimalInvestigations.MAX_VISIBLE` | `4` | **`3`** + `+N more` overflow |
| `_InvestigationPill` height | `40` | **`44`** |
| `_InvestigationPill` radius | `20` | **`14`** |
| `MinimalReturns.MAX_ROWS` | `3` | **`2`** |
| Returns row eyebrow | section_label("Recent returns") | **removed** — replaced with a 1-px hairline above the rows |
| Returns when-label | `FS_BODY=14, INK_2, dot indicator` | **`9.5 pt, INK_3, no dot`** |
| Typography | `FS_HERO=22 / FS_SECTION=14 / FS_META=12` | **`FS_HERO=20 / FS_SECTION=13 / FS_META=11 / FS_CONFIDENCE=10`** |
| Outer window radius | `28` | **`24`** |

Most important: the *hero card layout*. The 6M.1 hero stacked
*eyebrow + title + action row* vertically inside a 124-px
card with a stretch in the middle pushing the action row to
the bottom. The 6M.2 hero is a 2×2 grid inside a 92-px card —
title and confidence on top, chips and Resume on the bottom,
no stretch needed. The eye reads the four cells as one
*scene*, not as three stacked rows.

## What 6M.2 deliberately kept

| Surface | Why kept |
|---|---|
| Paper-white `#F7F5F2` page | Right colour; the regression wasn't in the palette. |
| Solid white card paint (alpha = 255) | Right call from 6M.1 — translucent cards were the *previous* regression. |
| Soft drop shadow `0 8 24` | Right shape; the cards still look physical. |
| Lavender accent + accent-tinted hero | Right hue and right *amount* of accent. |
| `MinimalEmpty`'s no-card-wrapper composition | Right structural choice from 6M.1. The icon shrank from 48 → 44 in spirit, but Phase 6M.2 made no structural change here. |
| `_OverflowChip` (`+N more`) | Same widget as 6M.1; only the cap dropped from 4 → 3, so the chip now appears at smaller cohort sizes. |
| `RECALL_LAUNCHER=legacy` escape hatch | Untouched; the 6K promotion's safety margin stays. |

## Why this matters

The user reported the regression with one phrase: *"current
version regressed."* The diagnostic was: the launcher had
drifted toward *dashboard* on the *utility ↔ dashboard*
axis — even though every individual 6M.1 change had a
reasonable rationale, the **accumulated effect** moved the
surface away from the Raycast / Arc shape it should have.

Refinement that does *not* hold the *whole-surface* read in
mind is the most common path to a regression like this. The
6M.2 recovery's contract is to keep that axis explicit:
**every change must answer whether it makes the launcher
read more like Raycast or more like Notion**. The directive's
recovery values answered "Raycast" on every dimension.

## Related

- [`PHASE_6M.2_STATUS.md`](../../archive/phase-status/PHASE_6M.2_STATUS.md) —
  the engineering receipt + verification matrix.
- [`PHASE_6M.1_STATUS.md`](../../archive/phase-status/PHASE_6M.1_STATUS.md) —
  the prior refinement's receipt (preserved; the 6M.1 work
  itself is *not* reverted, it's *re-tuned* per token).
- [`LAUNCHER_REVIEW.md`](LAUNCHER_REVIEW.md) — 6M.1's own
  audit doc (preserved as the *what was tried in 6M.1* record).
- [`assets/screenshots/launcher-compact/`](../../assets/screenshots/launcher-compact)
  — the 4 new compact captures.
- [`assets/screenshots/launcher-refined/`](../../assets/screenshots/launcher-refined)
  — the 5 6M.1 captures, kept on disk as the *before* set the
  regression doc references.
