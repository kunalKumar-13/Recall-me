# PHASE_6L_STATUS.md — Launcher Simplification

The receipt for Phase 6L. The directive's *Goal*: remove the
dashboard feeling. The launcher becomes a **single floating
surface**, not an admin panel / control room / analytics view.
Delete complexity.

The 6K→6L handoff: 6K promoted the v3 widget tree to be the
default launcher; 6L strips that tree to one calm vertical
column. The three-column shell (sidebar + centre + context
column) the launcher inherited from Phase 6I moves to
`archive/launcher-v2/` — kept on disk for reference, **not** on
the default import path, not a fallback.

Cross-references:
[`PHASE_6I_STATUS.md`](PHASE_6I_STATUS.md) (the v3 surface
primitives the new layout still uses),
[`PHASE_6K_STATUS.md`](PHASE_6K_STATUS.md) (the promotion this
phase further simplifies),
[`archive/launcher-v2/README.md`](../launcher-v2/README.md)
(the *why removed* doc the directive asked for).

---

## What shipped

### 1. The new minimal composition — `app/ui/launcher_v3/minimal.py`

A single file replaces the three-column shell with a calm
vertical stack:

```
┌────────────────────────────────────────────────┐
│  Search input                                   │  MinimalSearchBar
├────────────────────────────────────────────────┤
│  CONTINUE                                       │
│  WebSocket retry debugging          [HIGH]      │  Continue hero
│  [2 tabs] [3 files] [2d gap]      [Resume 1]    │
├────────────────────────────────────────────────┤
│  ACTIVE INVESTIGATIONS                          │  Horizontal pill strip
│  ● WS retry · ● Proposal · ● RLHF · ● Healthcare│  (max 4 visible)
├────────────────────────────────────────────────┤
│  RECENT RETURNS                                 │  Optional small list
│  ● yesterday — picked up WS retry               │  (hidden if empty)
├────────────────────────────────────────────────┤
│  ● local only · 127.0.0.1:4545 · no cloud       │  MinimalTrust footer
└────────────────────────────────────────────────┘
```

Eight new classes:

| Class | Purpose |
|---|---|
| `MinimalSearchBar` | One rounded `QLineEdit`. No labels, no kbd hint, no nav rows. Emits `query_changed`. |
| `_InvestigationPill` | A 36-px horizontal pill — accent dot + title + optional count chip. Focus-aware, Enter activates. |
| `MinimalInvestigations` | Horizontal flow of up to 4 pills. The directive's *max 4 visible* + *compact* rules are the binding constraint. Never grows a scrollbar. |
| `_ReturnRow` | Thin row: mute dot + mono-font when + body. 28 px tall. |
| `MinimalReturns` | Up to 3 `_ReturnRow`s. Hides itself when the list is empty (the directive's *delete density* rule). |
| `MinimalTrust` | One quiet line — *local only · 127.0.0.1:4545 · no cloud*. No surface, no shadow, just text. |
| `MinimalEmpty` | Single floating `GlassCard`: headline + body + Show example / Start normally + trust line. The Phase 6D contract preserved. |
| `MinimalDigest` | Composes hero + investigations + returns + trust. `populate(hero, investigations, returns)` is the only data path. |
| `MinimalShell` | Single-column floating shell. Outer gutter 32; centre column clamped **760-860 px** (directive); section gap 24. |
| `MinimalWindow` | Top-level `QWidget`. Default 920 × 720 — narrower than the 1180 × 760 the three-column shell needed. |

### 2. Removed: the right context column + the rich sidebar

The directive's "REMOVE" list:

```
right context column · doctor panel · stats panel · health blocks ·
daily loop cards · alpha info
```

…all lived inside `ContextColumn` and the rich `Sidebar` from
Phase 6I's three-column composition. Both classes moved to
[`archive/launcher-v2/`](../launcher-v2) (see §6
below) alongside the `Shell` + `LauncherWindow` that hosted them.

System info now lives **only** in the founder control room
(`apps/admin/web/`) — exactly where the directive said it should.

### 3. LiveLauncher rewired to the minimal composition

[`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
now imports from `.minimal` instead of `.shell` / `.sidebar`. The
constructor composes `MinimalShell` with a `QStackedLayout` that
swaps between `MinimalDigest` and `MinimalEmpty`. The default
window size dropped from `1180 × 760` to **`920 × 720`** to
match the narrower single-column shape.

Data path changes:

- `_populate_digest()` now reads **one** recovery
  (`api_client.recovery_recent(n=1)`) — the *only ONE primary
  card* rule. Threads are still fetched in groups of 4 because
  the strip needs more than one pill to feel ambient.
- `_recovery_to_v3()` keeps the confidence derivation
  (`n_targets ≥ 4 → high · 2-3 → medium · 0-1 → low`) — matches
  the v2 launcher + extension popup.
- Demo overlay path (`_populate_demo()`) shrinks too:
  one hero + three investigations (the canonical
  *WebSocket / Healthcare pitch / RLHF*).
- **New** `_build_returns()` reads `daily_loop.summary(days=3)`
  best-effort and surfaces the *today* / *yesterday* return
  rows. Counts only — per the Phase 6F trust contract; if the
  cohort hasn't produced returns the strip silently collapses.
- `_refresh_context()` was deleted — there is no context column
  to refresh.

`_activate_card(idx)` now targets the hero card on `1` and the
n-th investigation pill on `2-N`. The directive's *5-second
understanding* rule: the eye lands on the hero first; the
hotkey vocabulary follows.

### 4. Dynamic sizing — preserved + tightened

| Rule | How it's enforced |
|---|---|
| Outer gutter **32** | `MinimalShell` sets `setContentsMargins(32, 32, 32, 32)`. |
| Section gap **24** | Each `MinimalDigest`-internal layout uses `setSpacing(24)`; the directive's between-section rhythm. |
| Inner card **14** | `RecoveryCardV3` already uses 14-px inner spacing; unchanged. |
| Card radius **24** | `RADIUS_PANEL = 24` in `theme.py`; `GlassCard(radius=T.RADIUS_HERO)` (=28) for the Empty card so it reads as the strongest *floating* surface. |
| Soft shadow | `surfaces.GlassCard` paints one drop only; no heavy borders. |
| Width clamp **760-860** | `MinimalShell.MIN_WIDTH = 760, MAX_WIDTH = 860`. The centre column is a single fixed band; the parent window centres it. |
| Single column | `MinimalShell` is `QHBoxLayout(stretch + column + stretch)`. No left rail, no right rail. |
| No fixed heights | No `setFixedHeight` in `minimal.py`. The hero card is **content-driven**; the pill strip wraps cleanly; the returns row hides on empty. |

### 5. Motion — fade · lift · expand only

The directive's allowed list. No new animations land in this
phase; the v3 `motion.py` already carries `fade()` / `slide_y()`
/ `expand()` factories with **`OutCubic`** easing and the
**120 / 180 / 260** timings. The minimal layout inherits the
same vocabulary. Bounce / spring / overshoot remain banned.

### 6. Archive — `archive/launcher-v2/`

Three files moved out of `app/ui/launcher_v3/`:

```
archive/launcher-v2/
├── README.md       — the *why removed* doc the directive asked for
├── shell.py        — Shell + ContextColumn (3-column composition)
├── sidebar.py      — the rich left rail (nav + search + accent-dot active markers)
└── window.py       — the LauncherWindow that hosted the Shell
```

The README documents:
- which class lived in each file,
- why each was archived (single-paragraph rationale per widget),
- what stays in `app/ui/launcher_v3/` after Phase 6L,
- the rule that **nothing** in `app/`, `infra/`, or `apps/`
  imports from the archive — it is reference, not a code path,
  not a feature-flag fallback.

The Phase 6I/6K captures (`assets/screenshots/launcher-v3/`,
`launcher-live/`) still exist on disk; their generator scripts
(`capture_launcher_v3.py`, `capture_launcher_live.py`) reference
the archived widgets and will fail if re-run. That's the
expected outcome — those scripts are *legacy capture* tools and
their outputs are preserved on disk; the new
`capture_launcher_minimal.py` is the canonical pipeline from
Phase 6L forward.

### 7. Captures — `assets/screenshots/launcher-minimal/`

[`infra/scripts/capture/capture_launcher_minimal.py`](../../infra/scripts/capture/capture_launcher_minimal.py)
produces the four directive-named shots:

```
launcher-minimal/
├── hero.png            single column · Continue hero + 4 investigation pills + 3 returns
├── empty.png           first-run empty (Show example / Start normally + trust line)
├── investigations.png  populated with a lower-confidence hero so the strip carries the read
└── resume.png          hero in `_focused = True` state + one pill (the *resume* moment)
```

Each capture renders against the **same `MinimalDigest` /
`MinimalEmpty` widget tree** that the LiveLauncher composes at
runtime. Deterministic offscreen Qt; no engine call.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| First-recovery banner on the empty state | not in scope | The empty surface ships the directive's exact copy + Show example / Start normally + trust line. The *first-recovery* celebratory banner is the follow-up for the moment a cohort tester records their first recovery (Phase 6E's MOMENTS.md row #4). Slot exists in `MinimalEmpty`; widget lands when the cohort has its first row. |
| Live search-results column on `/` typing | partial | `MinimalSearchBar` emits `query_changed` on every keystroke; the LiveLauncher relays it via `_request_search`. Rendering the results inline (a third `QStackedLayout` index between `MinimalDigest` and `MinimalEmpty`) is a focused 30-line follow-up. |
| Delete the archived widgets entirely | declined | The directive said *archive*, not *delete*. The README documents why each was archived; future maintainers can audit the *previous-shape* without git-spelunking. |
| Delete the v3 `Shell` / `Sidebar` / `LauncherWindow` re-exports from the package barrel | done | `__init__.py` drops them from `__all__`; consumers of those names will see an `ImportError`, which is the right outcome — they shouldn't be imported any more. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| Default import path | `python -c "from app.ui.launcher import Launcher; print(Launcher.__name__)"` | `LiveLauncher` |
| LiveLauncher construct (offscreen) | stub `search_engine.store.count() → 0` | `920 × 720`; `MinimalEmpty` shown; show_example / start_normally signals connected |
| Minimal package exports | `from app.ui.launcher_v3 import MinimalShell, MinimalDigest, MinimalEmpty, MinimalSearchBar, MinimalInvestigations, MinimalReturns, MinimalTrust, MinimalWindow` | all 8 import |
| Captures | `python infra/scripts/capture/capture_launcher_minimal.py` | 4 PNGs into `assets/screenshots/launcher-minimal/` |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6K |
| Marketing site (regression) | `cd apps/web && npx tsc --noEmit` | unchanged |
| Extension (regression) | `cd apps/extension/ui && npx tsc --noEmit` | unchanged |

---

## Touched files

```
new code:
  app/ui/launcher_v3/minimal.py
  infra/scripts/capture/capture_launcher_minimal.py

modified code:
  app/ui/launcher_v3/__init__.py        (drop Shell / Sidebar / ContextColumn / LauncherWindow exports; add minimal classes)
  app/ui/launcher_v3/live.py            (compose MinimalShell instead of Shell + Sidebar + ContextColumn)

moved (out of app/ui/launcher_v3/):
  shell.py    → archive/launcher-v2/shell.py
  sidebar.py  → archive/launcher-v2/sidebar.py
  window.py   → archive/launcher-v2/window.py

new captures:
  assets/screenshots/launcher-minimal/hero.png
  assets/screenshots/launcher-minimal/empty.png
  assets/screenshots/launcher-minimal/investigations.png
  assets/screenshots/launcher-minimal/resume.png

new docs:
  archive/launcher-v2/README.md
  docs/engineering/PHASE_6L_STATUS.md
```

No `app/core/`, `api/`, `apps/extension/`, `apps/admin/`, or
`apps/web/` files were touched. No engine layer touched. No
recovery-logic change. The directive's *UI only* spirit held.

---

## Read-back of the success criterion

The directive's success line:

> open launcher — understand in 5 seconds

Open
[`assets/screenshots/launcher-minimal/hero.png`](../../assets/screenshots/launcher-minimal/hero.png):
the surface reads as **one thing to do** — a calm Continue hero
with a Resume button. Below, four ambient investigation pills
name the topics still in flight. Below those, a 3-row recent-
returns strip carries the *what you came back to* signal. The
trust line restates the boundary at the very bottom.

No daemon block, no doctor verdict, no version drift chip, no
events-today counter, no extension health row, no readiness
pill. Those signals all still exist — they live in the founder
control room (`apps/admin/web/`), exactly where the directive
sent them.

A user opening the launcher for the first time finds **one big
card to press Resume on**, **four titles to glance at**, and
**three quiet rows that say "you came back yesterday"**. Five
seconds is enough.
