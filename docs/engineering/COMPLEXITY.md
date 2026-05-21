# COMPLEXITY.md — where the size lives

A real LOC scan of the Python tree (Phase 5D, 20,152 lines across
`app/` + `api/`), with the long files named and a split path
recommended — but **not executed this cycle**. The directive's no-
behaviour-change rule means a 2,500-line file split is its own PR,
not a hygiene-pass casualty.

Pairs with [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md) (what is
gone) and [`REPO_HEALTH.md`](REPO_HEALTH.md) (the metrics over
time).

---

## Top files (LOC)

| File | LOC | Imports | Role |
|---|---|---|---|
| `app/ui/launcher.py` | 2,536 | 27 | the PyQt6 launcher window + every digest population path |
| `app/ui/widgets.py` | 2,487 | 16 | every result / row / preview / card widget the launcher composes |
| `api/main.py` | 1,070 | 21 | the FastAPI app — every `/v1/*` route |
| `app/core/recovery.py` | 1,026 | 11 | Phase 3B recovery engine + restoration plan |
| `app/core/evolution.py` |   912 |  — | Phase 3A evolution phases |
| `app/core/threads.py` |   892 | 15 | Phase 2C threads + Phase 4H session-anchored bucketing |
| `app/ui/settings.py` |   821 |  — | settings dialog |
| `app/core/resurfacing.py` |   807 |  — | Phase 2B resurfacing |
| `app/core/episodic.py` |   697 |  — | Phase 1A episodic retriever |
| `app/core/events.py` |   639 |  — | event log + Phase 4F parse cache |
| `app/ui/cards.py` |   534 |  — | Phase 4K launcher cards |

Two files are clear outliers: **`launcher.py`** and **`widgets.py`**
together carry **~25 %** of the entire Python tree.

## The three split candidates

The directive lists `launcher.py`, `recovery.py`, `threads.py`.
Here is the recommended carve for each — to be done in **dedicated
PRs**, each with a green 35-section smoke before and after.

### `app/ui/launcher.py` (2,536 LOC)

The launcher window is genuinely doing several jobs in one class:

```
launcher.py
├── window + chrome (build, layout, QSS)
├── digest population              ── _fill_recovery_list etc.
├── results pipeline               ── search worker, render
├── restoration                    ── _on_recovery_restore + plan walk
├── settings + hotkey wiring       ── small
└── tray + lifecycle               ── small
```

**Carve:**

| New file | Pulls in | Approx LOC |
|---|---|---|
| `app/ui/launcher_window.py` | the `LauncherWindow` class skeleton + `_build` | ~900 |
| `app/ui/launcher_digest.py` | every `_fill_*` method (recovery, threads, resurface, queries, activity, resurfaced) | ~700 |
| `app/ui/launcher_search.py` | the search worker plumbing + result rendering | ~500 |
| `app/ui/launcher_restore.py` | `_on_recovery_restore` + the plan-walk handler | ~250 |
| `app/ui/launcher.py` | thin re-export so existing imports keep working | ~50 |

**Risk:** moderate-to-high. The launcher is a single Qt window with
many cross-method references (`self.recovery_list` is touched from
five places). The carve is mechanical but every move needs the
smoke (and ideally a real launcher run) to verify nothing detaches.

### `app/core/recovery.py` (1,026 LOC)

Already has a clean shape — engine + helpers. A modest carve
clarifies it without changing behaviour:

| New file | Content |
|---|---|
| `app/core/recovery/engine.py` | `RecoveryEngine` class, `_score_thread`, the component scores |
| `app/core/recovery/captions.py` | `_preview_caption`, `_behavior_clause` (Phase 4G) |
| `app/core/recovery/plan.py` | `RestorationPlan`, `RestorationStep`, `RestorationResult`, `_classify_targets` |
| `app/core/recovery/__init__.py` | re-exports the public API so existing `from app.core.recovery import ...` keeps working |

**Risk:** low. Pure-Python module split, no UI coupling, and the
recovery smoke sections (§ 25–29, 33, 34) catch any regression
immediately.

### `app/core/threads.py` (892 LOC)

Smaller than the other two; the carve is optional:

| New file | Content |
|---|---|
| `app/core/threads/bucketing.py` | `_bucket_events` (Phase 4H) + the anchor logic |
| `app/core/threads/scoring.py` | the per-thread score components + weights |
| `app/core/threads/store.py` | `ThreadStore` + `_ThreadMeta` |
| `app/core/threads/__init__.py` | re-exports `Thread`, `ThreadBuilder`, `ThreadStore` |

**Risk:** low — pure-Python, smoke sections § 16–20 cover it.

## What this file is *not*

Not a verdict that the long files are bad. `launcher.py` is long
because the launcher *is* a launcher — many small concerns living
near each other. The split above is a navigability win for a new
engineer, not a behaviour win. It belongs after the public-alpha
gate, not before.

## Coupling notes

- **`launcher.py` imports 27 modules** — by far the broadest
  surface area. Most are necessary (Qt, every core layer, every
  widget kind). The carve above reduces *intra-launcher* coupling,
  not the import fan-out.
- **`api/main.py` imports 21 modules** — second-highest, but
  appropriate: it wires every service into FastAPI routes. Splitting
  would create routers, which is a real refactor (not hygiene).
- **`recovery.py` imports 11 modules** — clean.

## How to read the file lengths

A long file is a signal, not a verdict. The two real outliers
(`launcher.py`, `widgets.py`) together describe the entire desktop
UI; everything else is one layer of the engine, one file. That
ratio is honest for a single-process product.
