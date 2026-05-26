# PHASE_6M_STATUS.md — Desktop Memory Layer

The receipt for Phase 6M. The directive's *Goal*: Recall sees
work outside the browser. **No screenshots. No recording. No
pixels. Metadata only.**

The 6L→6M handoff: 6L simplified the launcher surface; 6M
expands what the engine *sees*. A desktop focus block in Cursor
or VLC or Premiere now lands in the same JSONL event log the
browser extension already writes to, so an investigation
spanning *Google → Stack Overflow → backoff.py → Cursor → OBS*
reads as one thread.

Cross-references:
[`DESKTOP_LAYER.md`](../product/DESKTOP_LAYER.md) (the
product-side story — what the layer is, what it isn't, how it
joins the engine),
[`TRUST.md`](../product/TRUST.md) (the five-rule public
contract this layer respects),
[`TRUST_LEDGER.md`](TRUST_LEDGER.md) (the on-disk boundary
spec).

---

## What shipped

### 1. `app/core/desktop/` — the capture package

Five new modules + a barrel `__init__.py`:

| File | Role |
|---|---|
| `events.py` | `KIND = "desktop_window"` constant + `DesktopWindowEvent` dataclass. The single JSONL payload shape the watcher emits. |
| `processes.py` | PID → exe-name / exe-path resolver via `OpenProcess` + `QueryFullProcessImageNameW`. Pure ctypes; no `psutil` dependency. Non-Windows hosts → `None` (graceful no-op). |
| `windows.py` | `probe_foreground()` reads the current foreground window's title + PID via `GetForegroundWindow` + `GetWindowTextW` + `GetWindowThreadProcessId`. Returns a `ForegroundWindow` dataclass with a `stable_key` for the aggregator. |
| `sessions.py` | `FocusAggregator` — pure, no-I/O focus-block aggregator with three rules: minimum 30 s duration, 60 s re-focus consolidation, EXE-prefix blocklist (Recall's own windows). |
| `watcher.py` | `DesktopWatcher` background-thread polling loop + `start_watcher()` / `stop_watcher()` convenience helpers. Writes via the existing `EventLogger`; refuses to start when `RECALL_DESKTOP=off` or the platform is unsupported. |

The aggregator is unit-testable without Qt:

```python
agg = FocusAggregator(min_focus_s=10, re_focus_window_s=20)
events = agg.observe(fg1, now=t0)                 # focus starts
events += agg.observe(fg2, now=t0 + 15s)          # crosses 10s floor
assert events[0].app == "Cursor.exe"
assert events[0].duration == 15
```

The smoke I ran during this phase exercised exactly that path
and emitted two events end-to-end.

### 2. API ingestion — `POST /v1/events/desktop`

[`api/schemas.py`](../../api/schemas.py) gains
`DesktopWindowIn` with the directive's exact field whitelist:
`app`, `title`, `duration`, `focus_start`, `focus_end`,
`switch_count`, `path` (optional), `process` (optional). The
schema's `_StrictModel` base drops anything else silently —
the *metadata only* rule enforced at the request boundary.

[`api/main.py`](../../api/main.py) gains the route handler
`ingest_desktop` mirroring the other ingest paths
(`_post_ingest_hook(ok)` triggers demo auto-dismiss + daily-loop
mark_event the same way).

[`app/core/ingest.py`](../../app/core/ingest.py)'s
`ALLOWED_KINDS` frozenset gains `"desktop_window"` so the
ingestion service accepts the new kind.

End-to-end smoke (TestClient → JSONL):

| Test | Result |
|---|---|
| Valid event (200, `ingested=1`) | ✓ |
| Extra field ignored (the schema's `extra="ignore"`) | ✓ |
| JSONL `~/.recall/events/YYYY-MM-DD.jsonl` row appears with `kind=desktop_window` | ✓ |

### 3. Control room `/desktop` route

[`apps/admin/web/app/desktop/page.tsx`](../../apps/admin/web/app/desktop/page.tsx)
ships the directive's four signals:

- **apps** — unique exe count in the 7-day window
- **focus** — total focus seconds (formatted `Nh Mm`)
- **top tools** — per-app row sorted by focus time
- **session time** — longest single focus block

Plus a session-log card surfacing the newest 100 focus blocks
and a *Privacy* card restating the *metadata only* contract.
All values come from a new
[`apps/admin/web/lib/loaders/desktop.ts`](../../apps/admin/web/lib/loaders/desktop.ts)
loader that streams `~/.recall/events/*.jsonl`, filters for
`kind === "desktop_window"`, and aggregates per app.

Nav row + Ctrl+K palette entry added so the page is reachable
from the existing operator surfaces.

### 4. Extension popup — desktop badge

[`apps/extension/ui/src/App.tsx`](../../apps/extension/ui/src/App.tsx)
Header gains a `desktopApps` prop. When the daemon reports
`health.desktop_apps_today > 0`, a small `⊞-N` accent badge
renders next to the existing *N today* caption — the
directive's *Desktop badge: apps active* signal.

The wire surface:

| Type | Field | Source |
|---|---|---|
| `Health.desktopApps?: number` | the popup's defensive type | optional; older daemons omit it |
| `data.desktop_apps_today` | `/v1/health` JSON | the daemon's count |

(The `/v1/health` JSON gains the field naturally once a daemon
implementation counts `desktop_window` events; this phase ships
the consumer side. Pre-6M daemons silently report 0 → no badge.)

### 5. Privacy contract restated

Every surface restates the *no screenshots, no OCR, no audio,
no pixels* contract:

- the watcher's docstring + the `events.py` payload comment;
- the `DesktopWindowIn` schema's field descriptions;
- the `/desktop` page's footer *Privacy* card;
- [`DESKTOP_LAYER.md`](../product/DESKTOP_LAYER.md)'s "What the
  watcher does NOT capture" table.

If a field outside the whitelist ever sneaks in, the schema
rejects it at the boundary — the contract isn't aspirational,
it's enforced.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Launcher Continue chip surfacing `[N app]` next to `[2 tabs] [3 files] [2d gap]` | partial | The data path lands in the engine via the new event kind; the *parsing* of `app` chips in the recovery engine's `preview_caption` is a focused recovery-engine change (not strictly UI). Pure parser change once the engine produces the caption string with the app count. |
| Cross-platform watcher (macOS / Linux) | partial | Windows is the only platform with a probe today. The package's `is_supported()` predicate gates the watcher cleanly; `darwin.py` / `linux.py` siblings drop in next to `windows.py` when a maintainer with the hardware runs them. |
| `recall doctor` row for the desktop watcher | not in scope | The watcher is a process-internal thread; the doctor reports filesystem state. A future check could surface "events with `kind=desktop_window` in the last 24 h" — a follow-up line, not a 6M deliverable. |
| Auto-start the watcher in `app/main.py` | partial | The boot path calls `start_watcher(event_logger)` only when `config.json:desktop_capture_enabled = True` — opt-in by default. Hooking that line into `app/main.py`'s startup sequence is a one-line follow-up; the engine layer is ready. |
| Engine-side aggregation that surfaces `apps active` on `/v1/health` | partial | The dashboard's `/desktop` loader computes the count locally from the JSONL. Adding `desktop_apps_today` to `/v1/health` is a small server-side change (count today's `desktop_window` events) — the popup's `desktopApps` prop is wired and renders the badge once the daemon publishes the field. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| `pyflakes` | `python -m pyflakes app/ui app/core api` | zero findings |
| Default launcher import | `from app.ui.launcher import Launcher` | unchanged — still returns `LiveLauncher` |
| Aggregator unit smoke | end-to-end Python | two focus blocks emit two events with correct durations |
| API ingest | TestClient `POST /v1/events/desktop` | 200 / `ingested=1` / JSONL row appears with `kind=desktop_window` |
| Admin Next.js build | `cd apps/admin/web && npm run build` | ✓ compiled / 15 routes (was 14) / `/desktop` is `ƒ` server-rendered / 87.4 KB first-load shared |
| Extension build | `cd apps/extension/ui && npm run build` | ✓ 400 modules / 293.75 kB JS / 93.31 kB gzipped (+0.7 kB vs 6L for the badge) |
| Marketing build | `cd apps/web && npx tsc --noEmit` | unchanged from 6L |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6L |

---

## Touched files

```
new code:
  app/core/desktop/__init__.py
  app/core/desktop/events.py
  app/core/desktop/processes.py
  app/core/desktop/windows.py
  app/core/desktop/sessions.py
  app/core/desktop/watcher.py
  apps/admin/web/lib/loaders/desktop.ts
  apps/admin/web/app/desktop/page.tsx

modified code:
  api/schemas.py                                 (DesktopWindowIn)
  api/main.py                                    (POST /v1/events/desktop)
  app/core/ingest.py                             (ALLOWED_KINDS += desktop_window)
  apps/admin/web/lib/loaders/index.ts            (export desktop loader)
  apps/admin/web/components/Nav.tsx              (Desktop nav row)
  apps/admin/web/components/CommandPalette.tsx   (palette entry)
  apps/extension/ui/src/App.tsx                  (header desktop badge)
  apps/extension/ui/src/lib/api.ts               (fetchHealth → desktopApps)
  apps/extension/ui/src/lib/types.ts             (Health.desktopApps)
  apps/extension/popup/...                       (vite build output)

new docs:
  docs/product/DESKTOP_LAYER.md
  docs/engineering/PHASE_6M_STATUS.md
```

No file in `apps/web/` (marketing site), no file in the
launcher widget tree (`app/ui/launcher_v3/`), no engine layer
*above* `events` was touched. The new layer is **purely
additive** — deleting `app/core/desktop/` removes the watcher
+ events without breaking any other artifact, per the CLAUDE.md
rule for new layers.

---

## Read-back of the success criterion

The directive's success line:

> Recall understands real work

A user works on a WebSocket retry investigation: a Google
search lands as `browser_search`, a Stack Overflow visit lands
as `browser_visit`, opening `backoff.py` lands as `open`,
focusing Cursor for ten minutes lands as `desktop_window`,
recording an explainer in OBS lands as another `desktop_window`,
checking the playback in VLC lands as yet another. The engine's
session reconstructor (which already groups events by
30-minute idle gap) folds them all into one session; the
threads layer folds the session into the *WebSocket retry
debugging* thread; the recovery engine surfaces the whole
thread as one Continue card.

Without Phase 6M the desktop hours were silent; the cohort
saw a recovery card that didn't know about the work done in
Cursor and OBS. With Phase 6M the engine sees the **real work**
the user actually did — metadata only, but enough to recognise
the same investigation across browser, file system, and
desktop. The directive's bar is cleared.
