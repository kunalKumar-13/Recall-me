# PHASE_6N_STATUS.md — Recovery Precision

The receipt for Phase 6N. The directive's *Goal*: the launcher
*feels intelligent*. **No redesign. No geometry changes. No
control-room work.** Recovery experience only — differentiated
signal states, real-evidence chips, a quiet confidence
sentence, a preview card on the empty surface, an investigation
sort order.

Cross-references:
[`RECOVERY_VISUAL_AUDIT.md`](../../docs/product/RECOVERY_VISUAL_AUDIT.md)
(the directive's *high / medium / low / silence / bad recovery*
audit doc),
[`PHASE_6M.2_STATUS.md`](PHASE_6M.2_STATUS.md) (the prior compact
geometry this phase builds on).

---

## What shipped

### 1. RecoveryCardV3 — three signal states

[`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
gained a `signal` parameter and three default sentences. The
constructor signature now:

```python
RecoveryCardV3(
    candidate_id, title, evidence, time_label,
    *,
    confidence="high",      # right-pill colour (kept for back-compat)
    signal=None,            # Phase 6N — drives CTA verb + fill strength
    sentence=None,          # Phase 6N — optional engine-provided sentence
    n_targets=0,
)
```

`signal` derives the CTA verb via `_CTA_FOR_SIGNAL`:

| Signal | Verb | Pill paint |
|---|---|---|
| `high` | **Resume** | accent-filled, white text |
| `medium` | **Continue** | accent-soft fill + 1-px accent border, accent text |
| `low` | **Review** | ghost — no fill, hairline border, ink-2 text |

The card's outer paint also varies by signal:

| Signal | Fill | Border |
|---|---|---|
| `high` | `T.ACCENT_SOFT` | accent line α=80 |
| `medium` | `QColor(245, 242, 252)` — halfway tint | accent line α=48 |
| `low` | `T.BG_RAISED` (plain white) | hairline α=24 |

A `DEFAULT_SENTENCES` map gives every signal a default
confidence line; the constructor's `sentence` arg overrides
when the engine provides a more specific one
(`getattr(c, "why_summary", None)` in LiveLauncher).

### 2. Resume confidence sentence row

A small `QLabel` at the foot of the card carries one
sentence — the directive's exact strings:

- HIGH → *"Recall thinks this was interrupted work"*
- MED → *"Seen again after return"*
- LOW → *"Weak signal — review first"*

Rendered at `T.FS_META` (11 px), `T.INK_3`, no background. Adds
~28 px to the card height, well inside the existing
`HEIGHT + 32 = 124` cap from Phase 6M.2.

### 3. Real-evidence chips capped at 3

`RecoveryCardV3.__init__` now truncates
`parse_evidence_chips(evidence)[:3]`. The chip parser is
unchanged and continues to refuse to fabricate — an empty
caption yields zero chips, no inference of "0 tabs" or
"unknown gap".

### 4. `_ResumePill` — three kinds

The previous one-shape accent pill became a three-variant
widget:

```python
_ResumePill(kind="resume" | "continue" | "review")
```

`KIND_VERBS` carries the directive's exact verbs. Paint
varies per kind (filled / accent-soft / ghost). The `1`
keyboard-shortcut chip stays on every variant because the
Enter / `1` activation contract is the same.

### 5. LiveLauncher wiring

[`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
`_recovery_to_v3` now passes:

- `signal=confidence` (mirrors the existing confidence
  derivation; future engine work can split signal from
  confidence cleanly);
- `sentence=getattr(c, "why_summary", None)` — hook for the
  engine to ship a per-row sentence in a future phase. Until
  then, `DEFAULT_SENTENCES` provides the directive's exact
  strings per signal band.

The demo overlay's hero is explicitly constructed with
`signal="high"` (the demo is the canonical strongest possible
recovery).

### 6. Investigation sort — `sort_for_digest()`

[`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
ships a new pure helper:

```python
def sort_for_digest(cards: List[InvestigationCardV3]) -> List[InvestigationCardV3]
```

…with the directive's exact rank order:

| Rank | Heuristic |
|---|---|
| 0 unfinished | `strength >= 3` AND `last_touch` doesn't start with `resolved` / `done` |
| 1 returned | `last_touch` contains `return`, `revisit`, or `back` |
| 2 recent | `last_touch in ("today", "now", "active")` OR ends in `h` OR ends in `d` with N ≤ 3 |
| 3 passive | everything else |

Within a rank, **high-strength threads win**. The function is
pure (no I/O, no Qt) — unit-testable.

LiveLauncher's `_populate_digest` now calls
`sort_for_digest(...)` before handing the list to
`MinimalInvestigations.populate` (which still caps at the
6M.2 `MAX_VISIBLE = 3` + drops surplus into the `+N more`
chip).

### 7. MinimalEmpty preview card

[`minimal.py:MinimalEmpty._build_preview_card`](../../app/ui/launcher_v3/minimal.py)
adds a LOW-state `RecoveryCardV3` between the sub-headline
and the buttons. The fixture is the canonical demo:

- title: *WebSocket retry debugging*
- evidence: *2 tabs · 2 files · reopened after a 2-day gap*
- sentence: *A real recovery will replace this*
- caption above the card: `PREVIEW` (mono, ink-4, letter-
  spacing 1.4)

The card is rendered through the same `RecoveryCardV3` widget
the live launcher uses — so the empty surface's preview is a
*literal* preview, not an illustration. It's stripped of
interactivity (`setEnabled(False)`, `Qt.FocusPolicy.NoFocus`,
`Qt.CursorShape.ArrowCursor`, `restore` signal **not**
connected). The card is clamped 360–440 px wide so it doesn't
compete with the buttons.

Auto-dismiss is handled by the launcher's state machine:
`MinimalEmpty` is only rendered when the engine has zero
recoveries; the first real ingest flips the state to
`MinimalDigest` and the preview is gone before the next
paint frame. The directive's *"dismiss immediately when real
events arrive"* contract is enforced upstream of the widget.

### 8. Five captures

[`infra/scripts/capture/capture_launcher_recovery.py`](../../infra/scripts/capture/capture_launcher_recovery.py)
produces the directive's exact 5 outputs into
`assets/screenshots/launcher-recovery/`:

```
high.png      HIGH-signal hero (Resume + accent fill + sentence)
medium.png    MED-signal hero (Continue + lighter fill + sentence)
low.png       LOW-signal hero (Review ghost + plain fill + sentence)
empty.png     empty surface with the preview card landed
resume.png    HIGH hero focused — the `1` keypress moment
```

All five render against the same widgets `LiveLauncher`
composes at runtime.

### 9. Audit doc

[`docs/product/RECOVERY_VISUAL_AUDIT.md`](../../docs/product/RECOVERY_VISUAL_AUDIT.md)
carries the directive's *high / medium / low / silence / bad
recovery* sections with the visual contract per state, plus a
cross-cutting rules table.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Engine-side signal vocabulary distinct from confidence | partial | LiveLauncher's `_recovery_to_v3` derives `signal=confidence` for now. Splitting the two cleanly (so a HIGH-confidence card can still be MED-signal when the cohort hasn't acted on it yet) is a focused recovery-engine change; the widget surface is already wired to accept it. |
| Per-row engine sentence | partial | The constructor accepts a `sentence` arg; LiveLauncher passes `getattr(c, "why_summary", None)`. The recovery engine doesn't currently emit `why_summary`; when it does, the launcher picks it up without further changes. |
| Cleanup / archive of duplicate evidence renderers | done in spirit | The two parsers (`app/ui/cards.py:_parse_evidence_chips` and `app/ui/launcher_v3/recovery_panel.py:parse_evidence_chips`) are kept as separate mirrors because `app/ui/cards.py` belongs to the legacy `launcher_legacy.py` (still reachable via `RECALL_LAUNCHER=legacy`). Archiving the legacy mirror would break the escape hatch; we leave both in place. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Default launcher import | `from app.ui.launcher import Launcher` | `LiveLauncher` (unchanged) |
| Sort helper unit | constructed 4 fixtures (passive / unfinished / returned / recent) | order: unfinished · returned · recent · passive ✓ |
| 5 captures | `python infra/scripts/capture/capture_launcher_recovery.py` | all 5 PNGs land · `EXIT=0` |
| Geometry (regression) | `MinimalShell.MAX_WIDTH = 640` · `MinimalWindow.DEFAULT_SIZE = (720, 520)` | unchanged from 6M.2 |
| Theme (regression) | `T.GUTTER = 20` · `T.SECTION_GAP = 16` · `T.FS_HERO = 20` | unchanged from 6M.2 |
| Doctor (regression) | `python recall.py doctor` | unchanged |

---

## Touched files

```
new code:
  infra/scripts/capture/capture_launcher_recovery.py

modified code:
  app/ui/launcher_v3/recovery_panel.py    (_ResumePill kind variants;
                                           RecoveryCardV3 signal+sentence;
                                           paint varies by signal)
  app/ui/launcher_v3/minimal.py           (_build_preview_card on MinimalEmpty)
  app/ui/launcher_v3/investigation_panel.py (sort_for_digest + _digest_rank)
  app/ui/launcher_v3/__init__.py          (export sort_for_digest)
  app/ui/launcher_v3/live.py              (pass signal/sentence; sort_for_digest)

new captures:
  assets/screenshots/launcher-recovery/high.png
  assets/screenshots/launcher-recovery/medium.png
  assets/screenshots/launcher-recovery/low.png
  assets/screenshots/launcher-recovery/empty.png
  assets/screenshots/launcher-recovery/resume.png

new docs:
  docs/product/RECOVERY_VISUAL_AUDIT.md
  docs/engineering/PHASE_6N_STATUS.md
```

No `app/core/`, `api/`, `apps/extension/`, `apps/admin/`, or
`apps/web/` files touched. No engine layer touched. No
geometry / theme / control-room work — every change lives
inside the launcher's recovery surface.

---

## Read-back of the success criterion

The directive's success line:

> open launcher — immediately know: resume now · continue
> later · ignore safely

Open the three signal captures side-by-side:

- **[`launcher-recovery/high.png`](../../assets/screenshots/launcher-recovery/high.png)** —
  the accent-filled card with *Resume* + *Recall thinks this
  was interrupted work* reads as **act now**.
- **[`launcher-recovery/medium.png`](../../assets/screenshots/launcher-recovery/medium.png)** —
  the lighter card with *Continue* + *Seen again after return*
  reads as **come back to this**.
- **[`launcher-recovery/low.png`](../../assets/screenshots/launcher-recovery/low.png)** —
  the plain card with the ghost *Review* + *Weak signal —
  review first* reads as **look before you act**.

A user opening the launcher in any of these three states
forms the right read in the first second — exactly the
*intelligent feel* the directive named.
