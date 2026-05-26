# Phase 6R — Launcher Finalization

**Status:** complete · **launcher is now a frozen product surface**
**Directive:** stop feature work · only launcher · make it feel
like shipped software
**Scope:** launcher only. No docs (except this + the audit). No
trust system. No recovery ranking. No control room. No
extension.

> No more launcher phases after this. Launcher becomes frozen
> product surface.

---

## What shipped

### Window

- **680 × 440**, hard clamp (`setFixedSize`). Resize disabled.
  `WA_TranslucentBackground = False` — no glass, no blur, no
  floating opacity tricks.

### Paint

- Page warmed to **`#F4F1EC`** (was `#F3F1ED`).
- New `BORDER_RAISED_STRONG = #E7DED3` (2-px search-bar border).
- New `SHADOW_SEARCH_* = 0 8 24 rgba(0,0,0,.06)` for the search
  bar; existing `SHADOW_CARD_* = 0 12 32 rgba(0,0,0,.08)`
  preserved for the hero + OTHER WORK card.

### Search bar

- 52 px tall, radius 14, 2-px warm border, lavender focus ring.
- Hand-drawn magnifying-glass icon (no Unicode dependency).
- Placeholder **`Search work…`**.

### Hero card

- Fixed 88-px height, single dense row.
- **6-px lavender left accent strip** clipped to the rounded
  border.
- Title (one line, elided with `...`) + tiny **HIGH** confidence
  pill.
- Chips row beneath the title — max 3, derived from
  `suggested_targets` via `_chips_from_targets`.
- **Resume button fixed 112-px wide** with the `1` shortcut chip.
- **Removed:** subtitle, meta caption, prose, *Why this?* link,
  `signals` parameter, `request_why` signal.

### OTHER WORK list

- Vertical list (was horizontal in 6O). Each row 44 px tall.
- Dot (lavender 6-px) + title (elided) + quiet right arrow.
- Max 3 rows. White card wrapper with 1-px inter-row dividers.

### Empty surface

- Centred stack: lavender square · headline · *Show example*
  (primary) · *Start working* (secondary).
- Both buttons 200-px fixed width, **inside the stack** — no
  longer floating page furniture.
- *Start normally* → *Start working* per the directive's text.

### Footer

- Single line `local only  ·  no cloud`, 10-px ink-3, centred.
- Present on populated **and** empty surfaces.

### Visibility audit

[`docs/product/LAUNCHER_FINAL_AUDIT.md`](../product/LAUNCHER_FINAL_AUDIT.md)
documents the frozen contract:

- Geometry table (window, gaps, padding)
- Paint table (fill / border / shadow per surface)
- Hero / OTHER WORK / empty / footer contracts
- 7-check visibility audit (arm-length, dark-room, 50 % / 125 %
  scaling, title overflow, empty state, demo state, resume state)
- The freeze rule + per-archive pointer

### Captures

Four PNGs in [`assets/screenshots/launcher-final/`](../../assets/screenshots/launcher-final/):

- `hero.png` — populated digest
- `empty.png` — stacked onboarding
- `focus.png` — lavender focus ring on the search bar
- `overflow.png` — both elider paths (hero + OTHER WORK)

### Archived

[`archive/launcher-debt/`](../../archive/launcher-debt/) carries
the four files 6R froze out + a per-file README:

- `minimal_6p1.py` — the 6P.1 visibility recovery surface
- `recovery_panel_6q.py` — the 6Q hero with the *Why this?* link
- `investigation_panel_6o.py` — the 6O horizontal row
- `why_sheet_6q.py` — the 6Q signal overlay

---

## Files touched

**New:**

- [`infra/scripts/capture/capture_launcher_final.py`](../../infra/scripts/capture/capture_launcher_final.py)
- [`docs/product/LAUNCHER_FINAL_AUDIT.md`](../product/LAUNCHER_FINAL_AUDIT.md)
- [`docs/engineering/PHASE_6R_STATUS.md`](PHASE_6R_STATUS.md) (this file)
- [`archive/launcher-debt/README.md`](../../archive/launcher-debt/README.md)
- 4 captures under
  [`assets/screenshots/launcher-final/`](../../assets/screenshots/launcher-final/)

**Rewritten:**

- [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
- [`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
- [`app/ui/launcher_v3/investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)

**Edited:**

- [`app/ui/launcher_v3/theme.py`](../../app/ui/launcher_v3/theme.py) —
  `BG`, `BORDER_RAISED_STRONG`, `SHADOW_SEARCH_*`
- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py) —
  `setFixedSize(680, 440)`, opaque background, dropped Why-sheet
  wiring + escape cascade entry
- [`app/ui/launcher_v3/__init__.py`](../../app/ui/launcher_v3/__init__.py) —
  exports

**Deleted (archived):**

- `app/ui/launcher_v3/why_sheet.py` (snapshot in
  [`archive/launcher-debt/why_sheet_6q.py`](../../archive/launcher-debt/why_sheet_6q.py))

---

## Verification matrix

| Check                                                              | Result        |
|--------------------------------------------------------------------|---------------|
| `python -m pyflakes app/ui app/core api`                           | clean         |
| `import app.ui.launcher_v3 as v3`                                  | 23 exports    |
| `v3.MinimalWindow.DEFAULT_SIZE`                                    | `(680, 440)`  |
| `v3.RecoveryCardV3.HEIGHT`                                         | `88`          |
| `v3.MinimalSearchBar.HEIGHT`                                       | `52`          |
| `v3.InvestigationCardV3.HEIGHT`                                    | `44`          |
| `v3.InvestigationList.MAX_VISIBLE`                                 | `3`           |
| Hero capture has accent strip + 3 chips + HIGH + fixed Resume      | yes           |
| OTHER WORK capture is vertical list with dividers                  | yes           |
| Empty capture has stacked logo/headline/2 buttons                  | yes           |
| Overflow capture elides both hero + OTHER WORK titles              | yes           |
| Focus capture shows lavender ring on the search bar                | yes           |
| Footer reads *local only · no cloud* on every capture              | yes           |

---

## Success criterion

> open Recall · understand instantly · click Resume · done.

The four-step user journey lands inside the frozen surface:

1. **Open** — `680 × 440` warm-paper window, no resize.
2. **Understand instantly** — search bar at top, single CONTINUE
   hero with the accent strip directing attention, three OTHER
   WORK rows below, trust footer at the bottom. Nothing else
   competes for the eye.
3. **Click Resume** — fixed-width 112-px button on the
   right of the hero with the `1` shortcut chip.
4. **Done** — the 6P resume pipeline (preview → toast → hide)
   carries the user the rest of the way.

The launcher is closed for feature work.
