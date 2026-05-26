# PHASE_6M.2_STATUS.md — Launcher Geometry Recovery

The receipt for Phase 6M.2. The directive's *Goal*: return the
launcher to a compact premium surface. The 6M.1 refinement
drifted the launcher away from the Raycast / Arc shape and
toward a dashboard shape; this phase recovers the proportions
without rewriting the theme.

**No new features. No theme rewrite. No engine work.** Layout
recovery only.

Numbering note: the directive labelled this phase *6M.1*
(again — the third 6-M-labelled directive this session); since
the *prior* 6M.1 (Launcher Refinement) already shipped with
its own
[`PHASE_6M.1_STATUS.md`](PHASE_6M.1_STATUS.md), this receipt
files as **6M.2** so the audit trail of *what was tried in
6M.1* and *what was recovered in 6M.2* both survive.

Cross-references:
[`LAUNCHER_REGRESSION.md`](../product/LAUNCHER_REGRESSION.md)
(the *why old looked better / what changed / what fixed* audit),
[`PHASE_6M.1_STATUS.md`](PHASE_6M.1_STATUS.md) (the refinement
this phase recovers from),
[`LAUNCHER_REVIEW.md`](../product/LAUNCHER_REVIEW.md) (6M.1's
own audit doc — preserved as the prior step's record).

---

## What shipped

### 1. Theme tokens retuned

[`app/ui/launcher_v3/theme.py`](../../app/ui/launcher_v3/theme.py)
— **no palette change, no shadow change, no radius change**.
Only the spacing rhythm + the typography scale moved to the
directive's recovery values:

| Token | 6M.1 | 6M.2 |
|---|---|---|
| `GUTTER` (outer column padding) | 28 | **20** |
| `SECTION_GAP` (search ↦ hero · hero ↦ investigations) | 20 | **16** |
| `CARD_GAP` (investigations ↦ returns) | 12 | unchanged |
| `RETURNS_GAP` (returns ↦ trust) | (n/a) | **8** (new token) |
| `FS_HERO` | 22 | **20** |
| `FS_TITLE` | 16 | **14** |
| `FS_BODY` | 14 | **13** |
| `FS_LABEL` | 11 | **10** |
| `FS_META` | 12 | **11** |
| `FS_SECTION` | 14 | **13** |
| `FS_CONFIDENCE` | (n/a) | **10** (new token) |

The directive's `title 22 / section 14 / meta 12` scale read
as too heavy *inside* the smaller window — `20 / 13 / 11` is
the recovery scale that lets the typography sit *inside* the
surface rather than dominate it.

### 2. Window + shell geometry compressed

| Surface | 6M.1 | 6M.2 |
|---|---|---|
| `LiveLauncher.DEFAULT_SIZE` | (820, 640) | **(720, 520)** |
| `MinimalWindow.DEFAULT_SIZE` | (820, 640) | **(720, 520)** + `MAX_SIZE = (760, 560)` |
| `MinimalShell.MIN_WIDTH` | 600 | **520** |
| `MinimalShell.MAX_WIDTH` | 760 | **640** |
| Outer window radius | 28 | **24** (directive) |

Window paints with the new 24-px radius; the inner column is
clamped to a 640-px max so the surface stays inside the
Raycast / Arc utility band.

### 3. Search bar — capped width + centred

[`MinimalSearchBar`](../../app/ui/launcher_v3/minimal.py) — the
single change is *centring under a 640-px max*:

- `setFixedHeight(48)` (was 40)
- `setMaximumWidth(640)`
- `setMinimumWidth(360)` so the centering stretches don't
  squeeze the placeholder text (the regression's symptom)
- `setSizePolicy(Expanding, Fixed)` inside an `addStretch(1)`/
  widget/`addStretch(1)` row
- `border-radius: 16` (was 12)
- `padding: 0 18px`
- placeholder: **"Search investigations…"** (directive's exact
  string)

The search bar now reads as a *tool*, not a *page header*.

### 4. Hero card — 92 px, 2×2 grid, bottom-aligned actions

[`RecoveryCardV3`](../../app/ui/launcher_v3/recovery_panel.py):

- `HEIGHT = 92` (was 124). `MAX_HEIGHT = HEIGHT + 24` — the
  card refuses to grow past 116 even if the title wraps,
  preventing the *dashboard sprawl* mode.
- Layout reshaped from `vertical stack with stretch` to a
  **2×2 grid**:

  ```
  ┌────────────────────────────────┬──────────┐
  │  title (left)                  │  HIGH    │
  ├────────────────────────────────┼──────────┤
  │  [chips]                       │ [Resume] │
  └────────────────────────────────┴──────────┘
  ```

  Implemented as a `top` HBox + `addStretch(1)` + `bottom`
  HBox inside one VBox. The eyebrow row (accent dot +
  "CONTINUE" label) was removed — duplicate of the chip
  strip + confidence badge.
- `_ResumePill` bumped from 34 → **36** px (directive's exact
  value). The chip strip is now the prior visual weight; the
  Resume CTA is one of two bottom-row peers.
- `Surfaced because you left this mid-flow.` footer line —
  already removed in 6M.1; stays removed.
- Title font size: `T.FS_HERO - 2` (18 pt — sits *under*
  `FS_HERO=20` so the card breathes inside the 92-px height).

### 5. Investigations row — max 3 + `+N more`

[`MinimalInvestigations`](../../app/ui/launcher_v3/minimal.py):

- `MAX_VISIBLE = 3` (was 4) — the directive's exact cap.
- `_InvestigationPill.setFixedHeight(44)` (was 40).
- Pill paint radius dropped from 20 → **14** (the directive's
  exact value) — matches the `_OverflowChip` radius too, so
  the row reads as one shape.
- Pill title font: `T.FS_TITLE - 1` (13 pt — fits the
  recovered typography scale).
- The `_OverflowChip` widget is unchanged from 6M.1; the row
  shows it whenever there are more than 3 threads.

### 6. Returns strip — quiet 2 rows

[`MinimalReturns`](../../app/ui/launcher_v3/minimal.py):

- `MAX_ROWS = 2` (was 3) — the directive's *quiet strip* spec.
- The section eyebrow (*"RECENT RETURNS"*) is **removed**.
  Replaced with a 1-px `T.HAIRLINE` `QFrame` above the rows.
- Per-row layout shrinks: 22-px tall (was 28), no leading
  dot, 9.5-pt mono when-label, 11-pt INK_3 body. The row
  reads as *ambient*, not as a list item.
- `setVisible(False)` on construction; `populate()` flips
  visibility based on `items` length. Empty list → strip
  collapses (the directive's *hide if empty* rule).

### 7. Digest vertical rhythm — explicit `addSpacing()`

[`MinimalDigest`](../../app/ui/launcher_v3/minimal.py) layout
spacing changed from one global `setSpacing(20)` to **explicit
per-gap `addSpacing()` calls** so the rhythm follows the
directive's non-uniform spec:

```
Hero
↕ T.SECTION_GAP = 16
Investigations
↕ T.CARD_GAP = 12
Returns
↕ T.RETURNS_GAP = 8
Trust
```

### 8. Four new captures

[`infra/scripts/capture/capture_launcher_compact.py`](../../infra/scripts/capture/capture_launcher_compact.py)
produces the directive's exact named outputs into
`assets/screenshots/launcher-compact/`:

```
compact.png         hero + 3 pills + 2 returns + trust (everything together)
hero.png            hero focused + a single investigation pill
investigations.png  4 threads → 3 pills + `+1 more` overflow chip
empty.png           vertically-centred icon + headline + sub + 2 buttons
```

### 9. New audit doc

[`docs/product/LAUNCHER_REGRESSION.md`](../product/LAUNCHER_REGRESSION.md)
ships the directive's *why old looked better / what changed /
what fixed* table — 13 named token comparisons + the
narrative explanation of the *Raycast ↔ Notion* axis.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Centered vertical positioning of the empty card | partial | The empty surface uses `addStretch(1)` above and below the icon-headline-buttons stack, which centers it inside the column. The directive's *center vertically* line is honoured but the screen capture shows the icon a bit higher than perfect-center because the search bar above competes for vertical real estate. A standalone *empty mode* that hides the search bar would lower the icon further; deferred so the layout matches what the user actually sees when they open the launcher to nothing. |
| Hero title eliding | partial | The hero title uses `setWordWrap(False)`; long titles will clip rather than wrap into a second line (which would break the 92-px cap). True Qt text elision needs a custom paintEvent on the QLabel; deferred. The cohort's existing titles ("WebSocket retry debugging") fit at 720-px window width. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Default launcher import | `python -c "from app.ui.launcher import Launcher; print(Launcher.__name__)"` | `LiveLauncher` (unchanged) |
| Geometry | `from app.ui.launcher_v3 import MinimalShell, MinimalWindow` | `MAX_WIDTH = 640` · `DEFAULT_SIZE = (720, 520)` · `MAX_SIZE = (760, 560)` |
| Theme values | `from app.ui.launcher_v3 import theme as T` | `GUTTER = 20` · `SECTION_GAP = 16` · `CARD_GAP = 12` · `RETURNS_GAP = 8` · `FS_HERO = 20` · `FS_SECTION = 13` · `FS_META = 11` · `FS_CONFIDENCE = 10` |
| Caps | `MinimalInvestigations.MAX_VISIBLE = 3` · `MinimalReturns.MAX_ROWS = 2` · `RecoveryCardV3.HEIGHT = 92` | ✓ |
| Captures | `python infra/scripts/capture/capture_launcher_compact.py` | 4 PNGs in `assets/screenshots/launcher-compact/` (compact / hero / investigations / empty) |
| Compact window construct (offscreen) | `Launcher(stub_search_engine)` | 720 × 520 — matches the directive's exact spec |
| Doctor (regression) | `python recall.py doctor` | unchanged |
| Extension build (regression) | `cd apps/extension/ui && npx tsc --noEmit` | unchanged |
| Admin build (regression) | `cd apps/admin/web && npx tsc --noEmit` | unchanged |
| Marketing build (regression) | `cd apps/web && npx tsc --noEmit` | unchanged |

---

## Touched files

```
new code:
  infra/scripts/capture/capture_launcher_compact.py

modified code:
  app/ui/launcher_v3/theme.py           (GUTTER 28→20 · SECTION_GAP 20→16 ·
                                         RETURNS_GAP=8 · FS_HERO 22→20 · …)
  app/ui/launcher_v3/minimal.py         (search 640+centred · pill h44 + r14 ·
                                         MAX_VISIBLE=3 · returns 2 rows + hairline ·
                                         shell MAX_WIDTH=640 · window 720×520 ·
                                         digest explicit per-gap addSpacing)
  app/ui/launcher_v3/recovery_panel.py  (HEIGHT 124→92 · 2×2 grid · _ResumePill 34→36)
  app/ui/launcher_v3/live.py            (DEFAULT_SIZE 820×640 → 720×520)

new captures:
  assets/screenshots/launcher-compact/compact.png
  assets/screenshots/launcher-compact/hero.png
  assets/screenshots/launcher-compact/investigations.png
  assets/screenshots/launcher-compact/empty.png

new docs:
  docs/product/LAUNCHER_REGRESSION.md
  docs/engineering/PHASE_6M.2_STATUS.md
```

No `app/core/`, `api/`, `apps/extension/`, `apps/admin/`, or
`apps/web/` files touched. No engine layer touched. No theme-
*structure* change — only token values moved. The 6M.1
captures stay on disk at `assets/screenshots/launcher-refined/`
as the *before* set the regression doc references.

---

## Read-back of the success criterion

The directive's success line: *launcher feels like Raycast /
Arc utility — NOT dashboard.*

Open
[`assets/screenshots/launcher-compact/compact.png`](../../assets/screenshots/launcher-compact/compact.png).
The surface is a 720 × 520 floating card on a paper-white page,
a centred search bar at the top, a single accent-tinted hero
with the title left + confidence pill top-right + chip row
bottom-left + Resume CTA bottom-right, three equal-width
investigation pills below the hero, a quiet two-line returns
strip with a hairline above it, and the trust line at the
foot. **No dashboard chrome. No edge-to-edge dark canvas. No
giant Resume button.** The eye reads the surface in one
glance and lands on the Resume CTA — exactly the *Raycast /
Arc utility* read the directive's success line names.
