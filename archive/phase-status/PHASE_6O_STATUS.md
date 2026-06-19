# PHASE_6O_STATUS.md — Launcher Reset

The receipt for Phase 6O. The directive's three repeated lines:

> We overbuilt.
> Stop adding.
> Delete complexity.

The launcher returns to a single floating surface — search ·
CONTINUE · OTHER WORK · empty. Nothing else. Six files moved
to `archive/launcher-overbuild/` with a per-file README; three
files in the v3 package were rewritten from scratch around the
reset spec.

Pairs with
[`LAUNCHER_RESET.md`](../../docs/product/LAUNCHER_RESET.md) (the
directive's *what removed / why launcher failed / new
philosophy* audit) and
[`archive/launcher-overbuild/README.md`](../launcher-overbuild/README.md)
(per-archived-file rationale).

---

## What shipped

### 1. New `RecoveryCardV3` — fixed 100 px, no variants

[`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
rewritten from scratch.

```python
RecoveryCardV3(
    candidate_id,
    title,
    meta,                 # ambient meta sentence — never chips
    *,
    n_targets=0,
)
```

The directive's contract:

- `setFixedHeight(100)` — *no dynamic growth*.
- One CTA shape only — `_ResumeButton` (accent-filled, `1`
  shortcut chip). The previous 3-kind `_ResumePill` is gone.
- Title left + ambient meta line under it + Resume right.
  Two-line text column on the left; vertically-centred.
- No `signal` parameter. No `confidence` parameter. No
  `sentence` parameter. The widget knows one shape.
- New `_EliderLabel` helper paints `…` when the title can't
  fit the constrained-width column (long titles like
  *"WebSocket retry debugging"* now elide gracefully inside
  the 680 px window).

The card paint is accent-soft tint + accent-line border;
focus glow doubles the border width. That's the entire
visual vocabulary.

### 2. New `InvestigationCardV3` + `InvestigationRow`

[`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
rewritten from scratch.

- `InvestigationCardV3` is now a **bare `QLabel`**. No border,
  no background, no status dot, no surface chip, no shadow.
  Click / Enter / Space emits `open_thread`.
- `InvestigationRow` lays out **up to 3 titles** equal-width.
  Anything past the third is dropped — no overflow chip, no
  scroll, no animation. The directive's *max 3 · single row ·
  equal width · no overflow animations* lands here.
- `sort_for_digest` is gone. The row shows the first three
  threads the engine returned, in the engine's order.

### 3. New `minimal.py` — search + CONTINUE + OTHER WORK / empty

[`minimal.py`](../../app/ui/launcher_v3/minimal.py) rewritten
from scratch. Five public classes:

| Class | Purpose |
|---|---|
| `MinimalSearchBar` | Single rounded input, centred, capped 620 px wide, 44-tall, radius 14, placeholder *"Search investigations…"*. |
| `MinimalDigest` | Search → CONTINUE section (hero only when present) → OTHER WORK section (3-title row). Hero section label appears only when there is a hero. |
| `MinimalEmpty` | Centred *Recall notices unfinished work* + *Work normally. / Return later.* + *Show example* + *Start normally*. No icon. No preview. No trust line. No card wrapper. |
| `MinimalShell` | 24-px outer padding, 16-px gap between search and body, single-column min 480 / max 620. |
| `MinimalWindow` | Top-level QWidget, default **680 × 460**, paper-white background, outer radius 24, soft drop shadow. |

What's gone from the previous `minimal.py`: `MinimalReturns`,
`MinimalTrust`, `_OverflowChip`, `_build_preview_card`,
`_ReturnRow`, the dashed-border preview caption wiring.

### 4. `LiveLauncher` — HIGH-only hero gate

[`live.py`](../../app/ui/launcher_v3/live.py) `_populate_digest`
rewritten:

- Reads `recovery_recent(n=1)` + `threads_recent(n=3)`.
- The hero is constructed **only** when the recovery has
  `len(suggested_targets) >= 4` (the HIGH bar). Below the
  bar → no hero.
- If there is no hero AND no investigations → `_show_empty()`.
- Otherwise → `_digest.populate(hero=…, investigations=…)`.

`_recovery_to_v3` simplified to four lines. `_thread_to_v3`
returns a bare `InvestigationCardV3(id, topic, title)`.
`_build_returns`, `_refresh_context`, the sort import, the
sentence override hook — all gone.

`DEFAULT_SIZE = (680, 460)` — was 720 × 520 in 6M.2.

`_activate_card(idx)` updated to target the hero on `1` and
the n-th title on `2-4` (the row caps at 3).

### 5. `archive/launcher-overbuild/` + README

Six files moved out of the live code paths:

```
archive/launcher-overbuild/
├── README.md                              ← per-file rationale
├── minimal.py                             ← prior MinimalReturns/Trust/etc.
├── recovery_panel.py                      ← signal variants + sentence + chips
├── investigation_panel.py                 ← status dots + pills + sort
├── digest.py                              ← legacy 6I DigestColumn/EmptyDigest
├── capture_launcher_compact.py            ← 6M.2 capture script
└── capture_launcher_recovery.py           ← 6N capture script
```

The directive: *Archive removed UI*. Each file's README entry
names what surface it carried and why the reset removed it.

### 6. `capture_launcher_reset.py`

[`infra/scripts/capture/capture_launcher_reset.py`](../../infra/scripts/capture/capture_launcher_reset.py)
produces the directive-named outputs into
`assets/screenshots/launcher-reset/`:

```
populated.png    HIGH-recovery path · search + hero + 3 titles
empty.png        no recovery · search + headline + body + buttons
```

Both render at 680 × 460 against the same widgets `LiveLauncher`
composes at runtime.

### 7. Two new docs

- [`docs/product/LAUNCHER_RESET.md`](../../docs/product/LAUNCHER_RESET.md)
  — the directive's *what we removed · why the launcher failed
  · the new philosophy* audit. Three failure modes, three
  design rules.
- This `PHASE_6O_STATUS.md` — engineering receipt.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Investigation row truly equal-width on long titles | partial | The row pads with `Expanding` spacers when fewer than 3 titles land, but each title's natural width is bounded by its text, not the slot. Two titles + a third can read as uneven when one title is significantly longer than the others. A `setMinimumWidth(slot_width)` per title would fix; deferred until cohort feedback says it actually reads as a problem. |
| Tab / focus navigation across hero + row | partial | `1-4` hotkeys target the four focusable widgets; arrow-key tab order is Qt's default (left-to-right reading order). A first-class focus ring on the titles is not yet wired (the title-as-QLabel widget paints on focus via stylesheet alone). |
| Drop the legacy `app/ui/cards.py` evidence parser | declined | The Phase 6K legacy launcher (`RECALL_LAUNCHER=legacy`) still imports it. Removing it breaks the escape hatch. The reset surface doesn't use it; the legacy path does. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Default import | `python -c "from app.ui.launcher import Launcher; print(Launcher.__name__)"` | `LiveLauncher` |
| Window default | `MinimalWindow.DEFAULT_SIZE` | `(680, 460)` |
| Shell | `MinimalShell.MIN_WIDTH, MAX_WIDTH` | `480 / 620` |
| Hero height | `RecoveryCardV3.HEIGHT` | `100` (fixed via `setFixedHeight`) |
| Row cap | `InvestigationRow.MAX_VISIBLE` | `3` |
| Live launcher construct | offscreen Qt + stub `search_engine` | `680 × 460` |
| Captures | `python infra/scripts/capture/capture_launcher_reset.py` | 2 PNGs · `populated.png` (hero + 3 titles) + `empty.png` (centered headline + buttons) |
| Doctor (regression) | `python recall.py doctor` | unchanged |

---

## Touched files

```
new code:
  infra/scripts/capture/capture_launcher_reset.py

rewritten code:
  app/ui/launcher_v3/recovery_panel.py    (one fixed-100px hero, no variants)
  app/ui/launcher_v3/investigation_panel.py (bare title + max-3 equal-width row)
  app/ui/launcher_v3/minimal.py           (search + CONTINUE + OTHER WORK / empty)
  app/ui/launcher_v3/__init__.py          (drop archived exports)
  app/ui/launcher_v3/live.py              (HIGH-only hero gate; simplified mappers)

moved (out of app/ui/launcher_v3/):
  minimal.py             → archive/launcher-overbuild/minimal.py
  recovery_panel.py      → archive/launcher-overbuild/recovery_panel.py
  investigation_panel.py → archive/launcher-overbuild/investigation_panel.py
  digest.py              → archive/launcher-overbuild/digest.py

moved (out of infra/scripts/capture/):
  capture_launcher_compact.py   → archive/launcher-overbuild/
  capture_launcher_recovery.py  → archive/launcher-overbuild/

new captures:
  assets/screenshots/launcher-reset/populated.png
  assets/screenshots/launcher-reset/empty.png

new docs:
  archive/launcher-overbuild/README.md
  docs/product/LAUNCHER_RESET.md
  docs/engineering/PHASE_6O_STATUS.md
```

No `app/core/`, `api/`, `apps/extension/`, `apps/admin/`, or
`apps/web/` files touched. No engine layer touched. The
`launcher_legacy.py` escape hatch (`RECALL_LAUNCHER=legacy`)
is preserved.

---

## Read-back of the success criterion

The directive's success line: *Open Recall. Understand in
3 seconds.*

Open
[`assets/screenshots/launcher-reset/populated.png`](../../assets/screenshots/launcher-reset/populated.png).
The eye reads, in order: *Search investigations…* (top, ambient)
→ *CONTINUE · WebSocket retry debugging · Resume* (centre,
focal) → *OTHER WORK · WebSocket · Healthcare proposal · RLHF*
(below, ambient). Three seconds. One decision: click Resume or
type to search. The directive's bar is cleared.
