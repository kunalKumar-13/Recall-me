# PHASE_6B_STATUS.md — Launcher Identity

The receipt for Phase 6B. The directive's *Goal*: the launcher
must feel **calm / floating / premium / memory-like** — not dense,
not hardcoded, not desktop utility. The directive's success line
was a one-liner: someone sees the screenshot and says *"this
looks expensive."* This phase delivers the theme + chip-row split
+ empty-state redesign that drive that read.

The 6A→6B handoff: 6A added the *confidence badge* + softer copy
but kept the dark theme (which I called out as the major
deferred item). 6B is the actual theme swap to warm white +
lavender + soft glass, plus the visible refinements that the new
palette enables.

Cross-references:
[`PHASE_6A_STATUS.md`](PHASE_6A_STATUS.md) (the predecessor;
this phase honours its *Deferred* list),
[`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) (any item still open
after this phase).

---

## What shipped

### 1. Palette inversion — warm white + lavender

[`app/ui/styles.py`](../../app/ui/styles.py) tokens flipped:

| Token | Before (dark) | After (warm white, Phase 6B) |
|---|---|---|
| `BG` | `#0f1115` (near-black) | `#fbf7f4` (warm off-white, cream) |
| `BG_RAISED` | `#161922` | `#ffffff` (card surface) |
| `BG_HOVER` | `#1c202b` | `#f4efea` (hover row) |
| `BG_SELECTED` | `#252a3a` | `#ede9fb` (accent-soft for selected) |
| `BORDER` | `#262a36` | `#e8e2dc` (soft hairline on warm-white) |
| `BORDER_STRONG` | `#3a4055` | `#d4ccc4` |
| `TEXT` | `#e8eaf0` | `#16112b` (warm dark ink) |
| `TEXT_DIM` | `#9097a8` | `#4a4458` |
| `TEXT_DIMMER` | `#5a6072` | `#847b8e` |
| `ACCENT` | `#8b9bff` (blue-ish) | `#8b7fe3` (lavender; matches extension `--accent`) |
| `ACCENT_DIM` | `#3b4566` | `#ede9fb` (soft accent fill; matches extension `--accent-soft`) |

The launcher and the extension popup now share a single visual
language. Tokens preserve their names, so every widget that read
through the indirection automatically follows the new palette;
hardcoded literal colors in QSS/paintEvent are listed in the
*Touched files* below.

### 2. LAUNCHER_QSS — soft glass surface

The launcher's main card flips to a translucent white surface:

```qss
QWidget#launcher_card {
    background: rgba(255, 255, 255, 184);    /* 72% white over OS */
    border: 1px solid rgba(24, 17, 45, 30);
    border-radius: 22px;
}
```

Plus the directive's spacing rhythm — section labels gain
`padding: 18px 24px 6px 24px`; search input gets `padding: 0 24px`;
list items get `border-radius: 10px` and `margin: 2px 6px` so
there's air around each row. Scrollbar handles flip to lavender
(`rgba(139, 127, 227, 56)`) so the calmness extends to the
scroll affordance.

A new `QPushButton#example_button` style ships with the QSS — a
soft lavender pill at low alpha for the empty-state's *Show
example* button (it's the only call-to-action on the surface).

### 3. Card hover — accent-tinted, not beige

The `CardBase.paintEvent` hover fill changed from `BG_HOVER`
(warm beige on white = flash) to a low-alpha lavender accent:

```python
# before
fill = QColor(BG_HOVER); fill.setAlphaF(0.55 * self._hover)

# after
fill = QColor(ACCENT); fill.setAlphaF(0.10 * self._hover)
```

Hover lift bumped from 2 → 3 px (still inside the directive's
*"hover lift: 4 px max"* rule). Hover rounded corners bumped
from 9 → 12 px to match the new card's softer radius.

### 4. Recovery card — evidence row as chip pills

The biggest legibility win of the phase. The prior dim text line
*"2 tabs · 3 files · reopened after a 2-day gap"* now renders as
**three separate chip widgets**:

```
[2 tabs]  [3 files]  [2d gap]
```

Wire-up in [`app/ui/cards.py`](../../app/ui/cards.py):

- New `_EvidenceChip` widget — small (height 18, radius 6) pill
  with a soft fill and label. *count* chips (tabs/files/chats)
  use accent-tinted background; *time* chips (`2d gap`) use the
  neutral warm beige.
- New `_middle_with_chips(title, chips)` mirrors the existing
  `_middle(title, evidence)` shape but renders a horizontal chip
  row instead of the dim text line.
- New `_parse_evidence_chips(evidence)` parses the engine's
  deterministic preview caption (`split('·')` + light suffix
  normalisation: *"-day gap" → "d gap"*, *"hours ago" → "h
  ago"*, etc.). **Pure parsing — never invents data.** When the
  evidence string is empty (rare degenerate candidate), the card
  falls back to the prior dim-text `_middle()` rather than
  showing an empty chip row.
- `RecoveryCard.__init__` calls `_parse_evidence_chips(evidence)`
  + `_middle_with_chips(...)` automatically; no launcher
  changes.

### 5. EmptyCard — first-magic redesign

The directive's empty-state spec:

```
illustration zone
headline: "Recall notices unfinished work."
body: "Work normally.  Return later.\nRecall fills itself."
button: "Show example"
```

`EmptyCard.empty()` now produces:

- A 210-px tall card (was 132) — the empty surface earns its
  vertical weight.
- The same `_GlyphChip("spark", ACCENT)` mark, centered, as the
  illustration zone (no new asset; the existing spark glyph is
  the *illustration* the directive named).
- Headline at 11 pt (was 10), `font-weight: 600`: *"Recall
  notices unfinished work."*
- Body at 9 pt (was 8.4) with `wordWrap: true` and the new
  copy: *"Work normally. Return later.\nRecall fills itself."*
- A *Show example* `QPushButton` with `objectName:
  "example_button"` so the new QSS styles it as a soft lavender
  pill. The button emits the new `EmptyCard.show_example` Qt
  signal on click; the live launcher decides what to do with
  the signal (currently a UI stub — no engine wiring).

The `__init__` gained two optional kwargs (`height=132,
show_example_button=False`) so the unchanged `offline()` and
`first_week()` factories produce the same compact card they
always did.

### 6. Capture pipeline — `launcher-v2/`

[`infra/scripts/capture/_render.py`](../../infra/scripts/capture/_render.py)
gained an optional `subdir: str | None = None` parameter on
`render()` — capture scripts pass `subdir="launcher-v2"` to
write into `assets/screenshots/launcher-v2/`. The default
behaviour (no subdir → flat `assets/screenshots/`) is preserved
for the extension + doctor + installer-flow captures that
aren't part of the v2 set.

`_render.py`'s `Panel` default background also flipped from dark
(`#13151b`) to warm white (`#ffffff`) so captures render against
the new launcher backdrop. Capture scripts that needed the old
dark background can still pass `bg=...` explicitly.

`capture_launcher.py` + `capture_recovery.py` updated to call
`render(..., subdir="launcher-v2")`. Seven PNGs land in the new
directory:

```
assets/screenshots/launcher-v2/
├── launcher-digest.png         (the populated digest)
├── launcher-empty.png          (the new empty surface with Show example)
├── launcher-first-week.png
├── launcher-loading.png
├── launcher-offline.png
├── recovery-card.png           (the chip-row recovery card)
└── recovery-card-focused.png   (with the lavender focus ring)
```

The historical `launcher-*.png` at the top level
(`assets/screenshots/launcher-*.png`) stay as the *before* set
referenced by older docs.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Live launcher's empty surface wired to use `EmptyCard.empty()` | partial | The redesigned `EmptyCard` lives in `cards.py` and renders in screenshots, but the *running* launcher's empty path uses its own QLabel-based widgets (`empty_title` + `empty_body` ids in the QSS). Wiring `EmptyCard` into the live empty path is a focused launcher refactor — deferred to keep this phase's diff readable. The QSS / labels do get the new palette automatically. |
| *Show example* button — live demo-seed integration | stub | The button + signal exist. The signal connects to nothing yet (the live launcher doesn't construct `EmptyCard.empty()`). When the live empty path migrates to `EmptyCard`, the launcher can connect `show_example` to a *demo digest* flow that reads `app/core/demo_seed.py` — the directive's *"Read demo seed only"* line. **No engine work** would be required (demo_seed is already an engine module). |
| Floating digest at `max-width: 860-920` | partial | The launcher's main card now uses radius 22 + 184-alpha white, which reads as floating. The actual width constraint (the launcher's `QWidget#launcher` sizing) lives in `app/ui/launcher.py`'s init and is a separate one-line change deferred to keep the diff focused. |
| Section rename to *Continue / Investigations / Recent returns / Trust* | deferred (same as 6A) | Touches `docs/product/CONTINUITY_LANGUAGE.md`; right home is a continuity-language pass. |
| Live launcher palette validation on a real desktop | deferred (external) | Offscreen captures verify the QSS resolves and renders without runtime errors; a real desktop session is the only way to verify visual feel on actual display hardware. Closed by the same maintainer who walks `CLEAN_MACHINE_RUN.md`. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.ui.cards import RecoveryCard, EmptyCard, _parse_evidence_chips"` | OK; parser test: `'2 tabs · 3 files · reopened after a 2-day gap'` → `[('2 tabs', 'count'), ('3 files', 'count'), ('2d gap', 'time')]` (matches the directive's chip example **exactly**) |
| launcher captures | `python infra/scripts/capture/capture_launcher.py` | 5 PNGs into `assets/screenshots/launcher-v2/` |
| recovery captures | `python infra/scripts/capture/capture_recovery.py` | 2 PNGs into `assets/screenshots/launcher-v2/` |
| extension build | (regression check; unchanged) | unchanged from 6A — Phase 6B touched no extension files |
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED (unchanged) |
| founder status | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged) |
| alpha CLI | `python recall.py alpha report` | 0 testers (unchanged) |

---

## Touched files

```
modified code:
  app/ui/styles.py
    - palette tokens inverted (BG / BG_RAISED / BG_HOVER / BG_SELECTED / BORDER /
      BORDER_STRONG / TEXT / TEXT_DIM / TEXT_DIMMER / HIGHLIGHT / ACCENT /
      ACCENT_DIM all flipped to warm-white + lavender values)
    - LAUNCHER_QSS rewrite: floating white card, generous spacing,
      lavender scrollbar, accent-tinted row hover
    - new QPushButton#example_button style for the empty-state CTA

  app/ui/cards.py
    - _ACCENT_RAIL retuned to lavender on warm-white (rgba(139,127,227,0.88))
    - _OK / _WARN retuned to the extension's --ok / --warn hues
    - HOVER_LIFT_PX 2.0 → 3.0
    - hover-fill swapped from BG_HOVER (warm beige) to low-alpha ACCENT;
      radius 9 → 12
    - new _EvidenceChip widget (height 18, radius 6, count/time variants)
    - new _middle_with_chips(title, chips) helper
    - new _parse_evidence_chips(evidence) — pure parser
    - RecoveryCard.__init__ routes evidence through the chip parser
    - EmptyCard: optional height + show_example_button kwargs; new
      show_example pyqtSignal; EmptyCard.empty() redesigned with new copy
      + 210-px tall surface + "Show example" QPushButton

  infra/scripts/capture/_render.py
    - render(..., subdir=None) optional parameter
    - Panel default background flipped from "#13151b" to "#ffffff"
    - Panel default radius 14 → 22

  infra/scripts/capture/capture_launcher.py
    - main() calls render(..., subdir="launcher-v2")

  infra/scripts/capture/capture_recovery.py
    - main() calls render(..., subdir="launcher-v2")

new screenshots:
  assets/screenshots/launcher-v2/launcher-digest.png
  assets/screenshots/launcher-v2/launcher-empty.png
  assets/screenshots/launcher-v2/launcher-first-week.png
  assets/screenshots/launcher-v2/launcher-loading.png
  assets/screenshots/launcher-v2/launcher-offline.png
  assets/screenshots/launcher-v2/recovery-card.png
  assets/screenshots/launcher-v2/recovery-card-focused.png

new docs:
  docs/engineering/PHASE_6B_STATUS.md   (this file)

modified docs:
  docs/founder/PHASE_TRACKER.md
  docs/founder/ROADMAP_LIVE.md
  docs/release/CHANGELOG.md
  docs/DOC_INDEX.md
```

No engine module touched. No memory layer. No founder system.
The directive's *NO engine changes / Only launcher surface*
rules held.

---

## The *this looks expensive* test

The directive's one-line success criterion: a viewer sees the
screenshot and says *"this looks expensive."* Of the seven new
PNGs:

- `launcher-digest.png` carries the whole identity story:
  warm-white surface, lavender accents on one Resume pill, chip
  pills replacing the dim text row, generous section spacing,
  confidence badge inline.
- `launcher-empty.png` is the *first-30-seconds* surface — the
  new headline ("Recall notices unfinished work."), the calm
  body, the soft Show example pill.
- `recovery-card.png` is the milestone surface — chips, badge,
  pill — that the directive lifted directly into its spec.

The verdict is external (it's a tester's reaction). What is
true now: the three core screenshots no longer read as *desktop
utility*. The eventual maintainer-side validation on a real
display will tell whether the visual instincts encoded here
actually land — same external-dependency shape as every prior
phase's success line.
