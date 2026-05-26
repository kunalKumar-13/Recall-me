# PHASE_6K_STATUS.md — Launcher Promotion

The receipt for Phase 6K. The directive's *Goal*: replace the old
launcher with the v3 widget tree built in Phase 6I. **No parallel
surface. No dead launcher path. Promote safely.**

The 6I→6K handoff: 6I built the parallel `app/ui/launcher_v3/`
package — twelve modules, seven surface primitives, the warm-white
premium look — but kept the live `app/ui/launcher.py` running the
v2 widget tree. 6K closes that gap: `from app.ui.launcher import
Launcher` now returns the v3 `LiveLauncher` by default, and the
legacy class is one env var away as a safety hatch.

Cross-references:
[`PHASE_6I_STATUS.md`](PHASE_6I_STATUS.md) (the v3 package this
phase promotes),
[`PHASE_6D_STATUS.md`](PHASE_6D_STATUS.md) (the demo overlay the
LiveLauncher honours),
[`PHASE_6F_STATUS.md`](PHASE_6F_STATUS.md) (the daily-loop counters
the LiveLauncher's context column will surface).

---

## What shipped

### 1. The promoted entry point — `LiveLauncher`

[`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
ships a new `LiveLauncher(QWidget)` class that:

- carries the **legacy constructor signature** —
  `LiveLauncher(search_engine, event_logger=None)` — so
  `app/main.py:416` constructs it unchanged;
- emits the legacy signals — `request_settings`, `_request_search`
  — so settings + search wire-ups keep working;
- composes the v3 Shell (Sidebar + ContextColumn) with a
  `QStackedLayout` centre that swaps between `EmptyDigest` and
  `DigestColumn` based on engine state;
- preserves the legacy public API — `show_centered()`,
  `invalidate_digest()`, `_refresh_idle_state()` — so callers
  (the global hotkey + tray icon paths in `app/main.py`) work
  without a single touch;
- registers QShortcut bindings for the directive's keyboard layer:
  `Esc` hides, `1-9` focus the n-th card.

The LiveLauncher reads live data via the existing
[`app.core.api_client.APIClient`](../../app/core/api_client.py):

| Source | Loader |
|---|---|
| Recovery cards | `api_client.recovery_recent(n=3)` |
| Investigations | `api_client.threads_recent(n=6)` |
| Events today (context col) | `api_client.health()` |

`_recovery_to_v3()` / `_thread_to_v3()` translate the API
DTOs into the v3 widget arguments. Confidence derivation mirrors
the launcher v2 + extension popup:
`n_targets ≥ 4 → high · 2-3 → medium · 0-1 → low`. No new field,
no schema change.

Demo overlay is honoured: when `demo_mode.is_active()` and the
engine is otherwise empty, `_populate_demo()` reads
`demo_mode.demo_payload()` and renders the canonical WebSocket /
Healthcare pitch / RLHF investigations. The same auto-dismiss
hook from Phase 6D still applies — a real ingest flips state to
`dismissed` and the next `_refresh_idle_state()` falls through to
the live engine.

### 2. The thin adapter — `app/ui/launcher.py`

The previous 1130-line live launcher moved to
[`app/ui/launcher_legacy.py`](../../app/ui/launcher_legacy.py). The
new
[`app/ui/launcher.py`](../../app/ui/launcher.py)
is **38 lines**, evaluated at import time:

```python
_FLAVOR = os.environ.get("RECALL_LAUNCHER", "v3").strip().lower()
if _FLAVOR == "legacy":
    from .launcher_legacy import Launcher, LAUNCHER_WIDTH, …
else:
    from .launcher_v3 import LiveLauncher as Launcher
    from .launcher_legacy import LAUNCHER_WIDTH, SHADOW_MARGIN, …
```

- **Default** path returns the v3 LiveLauncher as `Launcher`.
- **`RECALL_LAUNCHER=legacy`** returns the legacy class — the
  *promote safely* escape hatch the directive named.
- Backwards-compat constants (`LAUNCHER_WIDTH`, `SHADOW_MARGIN`,
  `FOOTER_H`) re-export from the legacy module so
  `app/ui/launcher_anims.py` and `app/ui/launcher_digest.py` keep
  working unchanged.

### 3. Dynamic layout — preserved from 6I

The v3 widget tree already honoured the directive's *no fixed
heights* rule:

- `RecoveryCardV3.HEIGHT` (124) is a **minimum**, not a `setFixedHeight`.
- `InvestigationCardV3.HEIGHT` (96) is a **minimum**.
- The Shell's centre column is clamped 420 px / 720 px so a wide
  screen doesn't stretch the surface but a narrow one still
  breathes.
- Sidebar + ContextColumn carry fixed *widths* (220 / 240 px) so
  the visual rhythm is stable; everything *vertical* flexes.

LiveLauncher adds no new fixed sizes — the `QStackedLayout`
swap between empty/digest is purely a stack-index change, not a
geometry change.

### 4. Context column — live data hook

`ContextColumn` (built in 6I) is now driven by `_refresh_context()`,
which reads `api_client.health()` and rebuilds the column with the
real `events_today` + derived doctor / extension / protocol
verdicts. The directive's named fields land:

| Field | Source |
|---|---|
| Events today | `health.events_today \|\| ingested_total` |
| Doctor state | derived (`GREEN` when events > 0 else `YELLOW`) |
| Extension state | derived (`connected` when events > 0 else `pairing`) |
| Protocol state | placeholder until the doctor's protocol check surfaces |
| Version | hardcoded `0.2.0` until version-drift hook lands |

### 5. Empty experience — the same 6D buttons

The empty surface ships the directive's *Show example / Start
normally* contract via the existing `EmptyDigest` widget. The
LiveLauncher wires both signals to `demo_mode.activate()` /
`demo_mode.dismiss()` + `_refresh_idle_state()`. First-recovery
banner (the directive's *first recovery banner*) is a follow-up
— the slot exists; the banner widget will land when the first
cohort tester records their first recovery.

### 6. Keyboard layer

LiveLauncher registers QShortcuts for:

- `Esc` → `hide()`
- `1` … `9` → `_activate_card(idx)` focuses the n-th card across
  recovery + investigation panels combined.

`Enter` activation and focus-ring rendering already lived in the
v3 card widgets (Phase 6I). The arrow-key tab-order follows from
each card carrying `Qt.FocusPolicy.StrongFocus`.

### 7. Screenshot pipeline — `launcher-live/`

[`infra/scripts/capture/capture_launcher_live.py`](../../infra/scripts/capture/capture_launcher_live.py)
builds six fixture surfaces and writes PNGs into
`assets/screenshots/launcher-live/`:

```
launcher-live/
├── overview.png   the full 3-column shell, populated digest
├── continue.png   the hero recovery card alone
├── empty.png      first-run empty surface (Show example / Start normally)
├── trust.png      trust footer in isolation
├── focus.png      digest with the recovery card in `_focused=True`
└── recovery.png   the *cohort-facing* shape — one recovery, one investigation
```

All six render against the v3 widget tree — the same widgets
LiveLauncher composes at runtime.

### 8. Promotion audit

| Item | Outcome |
|---|---|
| `app/ui/launcher.py` (1130 lines, v2 entry) | moved to `app/ui/launcher_legacy.py`; opt-in via `RECALL_LAUNCHER=legacy` |
| `app/ui/launcher.py` (new) | 38-line adapter, default v3 |
| Legacy row-card widget consumers (`launcher_anims.py`, `launcher_digest.py`) | unchanged — `LAUNCHER_WIDTH` / `SHADOW_MARGIN` / `FOOTER_H` re-exported from the legacy module so they keep working |
| `app/main.py` | unchanged — same `from app.ui.launcher import Launcher` line |
| Capture pipeline | the launcher-live captures supersede the launcher-v3 captures (which the marketing site still references for the 6G screens gallery); both directories are preserved |
| Duplicate launcher logic | the v2 lifecycle (single-instance lock, global hotkey, tray icon) stays in `launcher_legacy.py` and is invoked **only** when the env-var escape hatch flips back to legacy; the v3 LiveLauncher implements its own lighter lifecycle |

No widget code was deleted in this phase. The legacy file is
*archived in place* — present, not on the default import path,
not dead.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| First-recovery banner | partial | The empty-state surface ships the directive's exact copy + Show example / Start normally; the *first-recovery* celebration banner is the follow-up surface for the moment a cohort tester records their first recovery. Slot exists in the EmptyDigest; widget lands when the cohort has its first row. |
| Search results column wired to the v3 SearchPanel | partial | `SearchPanel` exists; the LiveLauncher emits `_request_search` on every keystroke. Wiring the results onto the centre stack (a third stack index between empty/digest) is a focused 30-line follow-up. |
| Live ContextColumn refresh on every render | partial | `_refresh_context()` rebuilds the column when the digest populates; deeper refresh cadence (e.g. on doctor-state change) is deferred to keep the diff focused. |
| Delete the legacy launcher entirely | declined | The legacy file is the *escape hatch* the directive's *promote safely* rule names. Deleting it eliminates the safety margin. The file is archived in place; a clean deletion can land in a follow-up after one cohort week confirms zero v3 regressions. |
| Live single-instance lock + global hotkey in LiveLauncher | partial | The lifecycle code in `app/main.py` already owns those globals; LiveLauncher's `show_centered()` integrates with them. The legacy class's heavy custom-tray paths are not duplicated. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| default import path | `python -c "from app.ui.launcher import Launcher; print(Launcher.__name__)"` | `LiveLauncher` |
| legacy fallback | `RECALL_LAUNCHER=legacy python -c "from app.ui.launcher import Launcher; print(Launcher.__name__)"` | `Launcher` (the legacy class) |
| LiveLauncher construct (offscreen) | stub `search_engine` with `.store.count()` | `1180 × 760`; `_refresh_idle_state()` runs; `_show_empty()` lands the EmptyDigest |
| Backwards-compat constants | `from app.ui.launcher import LAUNCHER_WIDTH` | `652` (re-exported from legacy) |
| Captures | `python infra/scripts/capture/capture_launcher_live.py` | 6 PNGs into `assets/screenshots/launcher-live/` |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6J |
| Extension build (regression) | `cd apps/extension/ui && npm run build` | unchanged |
| Admin build (regression) | `cd apps/admin/web && npm run build` | unchanged from 6J (still 14 routes) |
| Marketing site (regression) | `cd apps/web && npx tsc --noEmit` | unchanged |

---

## Touched files

```
new code:
  app/ui/launcher_v3/live.py            (LiveLauncher)
  infra/scripts/capture/capture_launcher_live.py

modified code:
  app/ui/launcher_v3/__init__.py        (export LiveLauncher)
  app/ui/launcher.py                    (now a 38-line adapter)

renamed:
  app/ui/launcher.py → app/ui/launcher_legacy.py
    (legacy class archived in place; reachable via RECALL_LAUNCHER=legacy)

new captures:
  assets/screenshots/launcher-live/overview.png
  assets/screenshots/launcher-live/continue.png
  assets/screenshots/launcher-live/empty.png
  assets/screenshots/launcher-live/trust.png
  assets/screenshots/launcher-live/focus.png
  assets/screenshots/launcher-live/recovery.png

new docs:
  docs/engineering/PHASE_6K_STATUS.md
```

No changes to `app/core/`, `api/`, `apps/extension/`,
`apps/admin/`, or `apps/web/`. No engine layer touched. No
recovery-logic change. The directive's *UI only* spirit held.

---

## Read-back of the success criterion

The directive's success line:

> v3 becomes Recall launcher

`from app.ui.launcher import Launcher` now returns
`LiveLauncher` — the v3 widget tree, wired to live recovery /
threads / health data, honouring the demo overlay, the empty
surface buttons, and the directive's keyboard layer. The
legacy class is archived in place behind a single env-var
escape hatch so an operator can pin to legacy if a regression
surfaces during cohort week. The screenshot pipeline produces
six PNGs in `launcher-live/` from the same widgets the runtime
composes. No parallel surface, no dead launcher path; the
promotion is safe.
