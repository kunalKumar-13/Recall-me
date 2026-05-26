# Launcher Visibility — Phase 6P.1

> **Success criterion:** the launcher is readable from two meters
> away. Every surface registers as a stacked object on a warm
> page, not as a sheet of mixed-temperature whites.

---

## Problem

Phase 6O reset the launcher to one surface, but the reset went too
far on the *paint* side: every interactive element was painted the
same near-white (`#F7F5F2` page, `#FFFFFF` cards) with only
rgba hairlines for separation. On a normal monitor at normal
viewing distance the surfaces *blended into each other*:

- The page (`#F7F5F2`) and the white hero card differed by ~10%
  luminance — below the threshold where most viewers see two
  distinct surfaces.
- The search input had no card wrapper, so it sat flush with the
  page — a floating bar that didn't read as a control.
- The investigation row was bare text on the page — three titles
  adrift, with no shared container.
- The empty-state buttons floated below the headline with no
  fixed widths, so the surface read as "loose strings of text" not
  "an interface".
- The launcher window itself painted flush to its window edge —
  no visible frame, no sense of the launcher as a discrete object.

Net effect: the launcher looked like a CSS reset that had
forgotten to set borders.

---

## Fix

The 6P.1 directive: keep the 6O reset's structure, restore its
*visibility*. Eight concrete changes:

### 1. Warmer page

`theme.BG` drops from `#F7F5F2` → **`#F3F1ED`**. The warm-grey
page is now ~6% darker than the white cards — enough contrast
for layering to read at arm's length.

### 2. Layered cards everywhere

New `_LayeredCard` base class. White fill (`#FFFFFF`) + 1-px
warm-grey border (**`#E4DED6`**) + soft drop shadow
(**`0 12 32 rgba(0,0,0,.08)`** — `T.SHADOW_CARD_*`). Every
interactive surface inherits it:

| Surface          | Card?                  |
|------------------|------------------------|
| Search bar       | yes (radius 14)        |
| Recovery hero    | yes (radius 22)        |
| Investigations   | yes (radius 18, wraps the row) |

### 3. Search bar

Now a layered card with three elements:

- A **hand-drawn magnifying-glass icon** (`_SearchIcon` — circle
  + handle painted in `QPainter`, no Unicode glyph dependency).
- A bare `QLineEdit` with no chrome of its own (the card carries
  the chrome).
- A **lavender focus ring** — the card's paint flips from a
  warm-grey 1-px border to a 2-px `T.ACCENT` border when the
  input has focus.

Inactive cards are painted at ~0.96 alpha so the focused card
always reads as the foreground element.

### 4. Hero card

- White fill (was accent-tinted in 6O).
- **Soft 4-px lavender left accent strip** painted inside the
  rounded border so it tucks behind the card edge.
- **Resume button is fixed-width 110-px** (was content-sized) so
  the right edge is stable across recoveries with different
  title lengths.
- Padding tightened to 20-px outer / 24-px left (the extra 4 px
  on the left clears the accent strip).
- Border radius dropped to **22-px** (was `T.RADIUS_HERO=20`) per
  directive.

### 5. Empty state

Stacked: **logo dot · headline · sub · buttons row**, 16-px
gap between everything. The two buttons are fixed-width 140-px,
center-aligned. The primary (*Show example*) is accent-filled;
the secondary (*Start normally*) is a layered white card with the
same border colour.

### 6. Window frame

`MinimalWindow` now reserves a **12-px outer margin**. The page
paints inside that margin with a 1-px warm-grey border at radius
**24**. The launcher reads as a *discrete object*, not as a
patch of paint covering the desktop.

### 7. Removed

- Transparent areas (every painted surface is opaque).
- Floating sections (every interactive element sits inside a
  card).
- White-on-white blending (the page is now `#F3F1ED`).
- Unbounded spacing (`MinimalEmpty` stacks at a fixed 16-px gap).

### 8. Captures

Four PNGs in [`assets/screenshots/launcher-visible/`](../../assets/screenshots/launcher-visible/):

- `hero.png` — populated digest (search + CONTINUE + OTHER WORK)
- `empty.png` — stacked empty surface
- `focus.png` — search bar with the lavender focus ring on
- `investigations.png` — the OTHER WORK card alone

---

## Before / After

| Surface     | 6O (before)                                      | 6P.1 (after)                                           |
|-------------|--------------------------------------------------|--------------------------------------------------------|
| Page        | `#F7F5F2`                                        | **`#F3F1ED`** (6% darker; layering reads)              |
| Search      | bare `QLineEdit`, full-width                     | layered card, hand-drawn icon, **lavender focus ring** |
| Hero        | accent-tinted fill, no left mark                 | white fill, **4-px lavender accent strip**             |
| Resume      | content-sized                                    | **fixed-width 110-px**                                 |
| OTHER WORK  | bare titles on the page                          | wrapped in **white card, radius 18, padding 12**       |
| Empty state | headline + sub + buttons (no logo, no fixed width)| **logo → headline → sub → buttons**, 16-px gap, 140-px buttons |
| Window      | flush to edge                                    | **12-px outer margin, inner radius 24, 1-px border**   |
| Borders     | rgba hairlines (visually muddy)                  | solid `#E4DED6` warm-grey (visually crisp)             |
| Shadow      | `0 8 24 rgba(0,0,0,.07)`                         | **`0 12 32 rgba(0,0,0,.08)`** (stronger layering)      |

The structural geometry (680×460, column 480-620, hero 100-px
fixed, OTHER WORK max 3, HIGH-only gate) is unchanged from 6O.
This phase only touched paint.

---

## Files touched

- [app/ui/launcher_v3/theme.py](../../app/ui/launcher_v3/theme.py)
  — `BG`, `BORDER_RAISED`, `SHADOW_CARD_*` tokens.
- [app/ui/launcher_v3/minimal.py](../../app/ui/launcher_v3/minimal.py)
  — `_LayeredCard`, `_SearchIcon`, layered search bar,
  `_InvestigationsCard` wrapper, stacked empty, window frame.
- [app/ui/launcher_v3/recovery_panel.py](../../app/ui/launcher_v3/recovery_panel.py)
  — white fill + accent strip + fixed-width Resume.
- [infra/scripts/capture/capture_launcher_visible.py](../../infra/scripts/capture/capture_launcher_visible.py)
  — 4 captures.
- [assets/screenshots/launcher-visible/](../../assets/screenshots/launcher-visible/)
  — `hero.png`, `empty.png`, `focus.png`, `investigations.png`.

---

## What this proves

Open the launcher on a 2K display, stand back two meters, and the
four shapes register: a search bar, a CONTINUE card with an
accent left edge, an OTHER WORK card with three titles, and an
outer frame around all of it. None of those layers blends into
its neighbour.

That's the bar. Anywhere the launcher fails it is a regression.
