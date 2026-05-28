# Product Recovery — Phase P0

Honest end-to-end pipeline diagnosis + the minimum
set of fixes that make the launcher actually work
on real user data. Files only. No git.

**Date:** 2026-05-27.
**Scope walked:** browser extension → loopback
daemon → event store → thread builder →
investigation cache → recovery engine → launcher
search → launcher resume → preview pane → button
handlers.

---

## Working

What the diagnostic walk found that already works on
the live install:

| Layer                  | Evidence                                                                  |
|------------------------|---------------------------------------------------------------------------|
| Browser extension capture | `~/.recall/events/` has 247 events across 6 day-files. Today: 19 events. Last event 19 min before this walk: `browser_visit hotstar.com`. Extension is firing for hotstar, gmail, bondscanner, etc. |
| Daemon HTTP surface    | `/v1/health` → 200, `ingested_total=19`. `/v1/recovery/recent` 200. `/v1/threads/recent` 200 (returns 6 hot threads with real `event_count`, `surface_types`, `confidence`). `/v1/resurface/idle` returns 4 contexts. `/v1/contexts/recent` returns 5. `/v1/search` returns blended episodic + contexts + sessions for every test query. |
| Event store on disk    | JSONL appends are clean, schema is the expected `{ts, session_id, kind, payload}`. |
| Threads cache          | `threads.json` is an index only (id / topic_key / title / created_at / last_active_at / muted). The full thread shape — `event_count`, `surface_types`, `confidence` — is computed live by the daemon's `/v1/threads/recent` endpoint, *not* persisted. Live response is correct. |
| Recovery hero buttons  | `RecoveryView.resume` + `RecoveryView.review` → `LiveLauncher._on_resume_clicked` → `api_client.recovery_restore` → `_open_target`. The chain compiles and the no-candidate path falls through cleanly. |
| Resume state buttons   | `ResumeView.done_clicked` → `_on_resume_done`, `ResumeView.undo_clicked` → `_on_resume_undo`. Both wired since Phase 10B. |
| Public import contract | `from app.ui.launcher import Launcher` → `LiveLauncher` at 760×520 in the `empty` state. `from app.main import main` imports clean. |

---

## Broken

What was producing the wrong user-visible behaviour:

### 1. Continue card never appeared (engine calibration)

**Recovery engine returned `candidates: []` for every probe**, even though the daemon had 6 hot threads with healthy event counts (19, 28, 37, 13, 8, 6).

Per-thread trace (the inline diagnostic, against live `~/.recall/`):

```
thr_ab0ddc02  topic='chatgpt'      ec=19  surf={chat_session, query}
   continuity = 0.4786   < MIN_CONFIDENCE 0.55   (FAIL trust)
   confidence = 0.0000   < MIN_RESUME_INTENT 0.32 (FAIL intent)
   reason: last_phase.transition='initial' → all confidence signals 0;
           density=0.000 + last_momentum=0.087 → continuity below floor.

thr_08a5564a  topic='inbox'        ec=28  surf={browser_visit}
   REJECT at depth=0 gate (browser_visit not in _DEPTH_KINDS).

thr_7a1dc3f2  topic='jiohotstar'   ec=37  surf={browser_visit}    same.
thr_bc459361  topic='kunalkumar-13' ec=13  surf={browser_visit}   same.
thr_923cba46  topic='invitation'   ec=8   surf={browser_visit}    same.
thr_392d7871  topic='meet'         ec=6   surf={browser_visit}    same.
```

**Diagnosis:** the recovery engine's gates assume threads with at
least one "depth" surface (`open` / `reveal` / `chat_session` /
`browser_search`). Most real-user browsing is single-surface
`browser_visit` only — those threads can't surface even when
they're large. The one thread with depth (chatgpt) is fresh, so
the confidence signals (abandonment / revisit / acceleration /
unresolved) all score 0.

**Fix kind:** engine calibration. Two reasonable knobs:
1. Add `browser_visit` to `_DEPTH_KINDS` (weight it as half-depth
   so a pure-browse thread can surface).
2. Lower `_MIN_RESUME_INTENT` from 0.32 → ~0.10 so a fresh
   high-continuity thread isn't gated out by zero intent.

**Decision deferred.** Calibration affects the false-positive
rate, which erodes trust if loosened too far. Documented here;
not changed in P0. See *next fixes* below.

### 2. Launcher search returned nothing

**The launcher was wired to the wrong engine.** `_on_query_changed`
called `self.search_engine.search(q)` — the ChromaDB **file index**.
The user has zero chatgpt-named files, so every search of
`chatgpt`/`github`/`google`/`stitch` returned an empty list and the
search state showed darkframe's design fixture (mock data).

But `/v1/search` on the daemon already runs the full episodic +
contexts + sessions blend over the event store, and returns real
data for every query:

```
q='chatgpt'  episodic=3 contexts=2 sessions=2 ms=4.6
q='github'   episodic=3 contexts=2 sessions=2 ms=3.4
q='google'   episodic=3 contexts=2 sessions=2 ms=6.2
q='stitch'   episodic=3 contexts=1 sessions=1 ms=3.0
q='mail'     episodic=3 contexts=2 sessions=2 ms=3.9
q='hotstar'  episodic=1 contexts=1 sessions=1 ms=2.7
```

**Fix shipped (P0):** `_search_engine_to_groups` in
`app/ui/launcher_v3/live.py` now routes through
`self.api_client.search(q)`, maps episodic + contexts + sessions
onto the design's four buckets (Investigations / Files / Returns
/ Events), and falls back to the file index only when the daemon
is unreachable. The same module gained `_glyph_for_episodic` to
pick the right row icon per event kind.

Live verification (after fix):

```
chatgpt  → Investigations × 4 · Returns × 3 · Events × 4
github   → Investigations × 2 · Returns × 2 · Events × 4
stitch   → Investigations × 1 · Returns × 1 · Events × 3
```

### 3. Four buttons were decorative

The Phase 10B migration introduced the dark surface but missed
wiring four signals from `darkframe.py` to handlers in `live.py`:

| Button                                | Was                            | Now                                              |
|---------------------------------------|--------------------------------|--------------------------------------------------|
| EmptyView · Show example              | Signal defined, never connected | `_on_show_example` → `demo_mode.activate()` + idle refresh |
| EmptyView · Start working             | Signal defined, never connected | `_on_start_working` → dismisses demo, hides launcher |
| PreviewCard · Open ↗                  | Signal defined; the QLabel never emitted it (no click handler) | Added `_ClickableLabel` subclass; the link now emits `open_clicked` → forwarded through `RecoveryView.preview_open` → `_on_preview_open` → `_open_target(path|url)` |
| SearchView mini-pane · Resume         | Signal defined on `_MiniPreviewPane`, never bubbled by `SearchView` | **Still not wired** — flagged as a P1 because it requires a second signal-forward through `SearchView` and a result-row selection model (no row is "selected" today, so we don't know which investigation to resume). |

---

## Fake surfaces

Visual elements that draw correctly but don't currently reflect
engine state:

| Surface                                                                 | Why fake                                                                                              |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Search state's mini preview pane (`_MiniPreviewPane`)                  | Always shows the "WebSocket retry debugging" investigation block + two faint placeholder lines. Doesn't update from the currently-selected row. |
| Resume state's `last active during implementation` mono footer text    | Hard-coded string in `darkframe.py` — not derived from the candidate or plan.                          |
| Other-work strength dots (high / med / low) in non-demo populated state | Heuristic based on `len(surface_types)` — for browser_visit-only threads (most of the user's data) this always returns `low`, even on threads with 30+ events. |
| Final-CTA "0.4 SECONDS" in Resume state header                          | Hard-coded; not measured.                                                                              |

---

## Real surfaces

Visual elements that are honestly engine-driven:

- The launcher's empty-state copy + bloom mark + serif accent.
- The recovery hero's title / chips / eyebrow text (all derived
  from `RecoveryProps` built by `_engine_to_recovery_props`).
- The recovery state's Other work rail when populated (derived
  from `threads_recent` via `_thread_to_other_row`).
- The search state's 4 result groups **after the P0 rewire**
  (every row is a real daemon hit).
- The Resume state's restored item list (every row is the actual
  outcome of `_open_target` on a plan step).
- The footer's left-aligned `RECALL · LOCAL` daemon indicator —
  static text but accurate (always local).

---

## Missing wiring

Signal endpoints that exist on the dark surface but have no
host-side consumer:

| Endpoint                                       | Status         | Consequence today                                            |
|------------------------------------------------|----------------|---------------------------------------------------------------|
| `SearchView.selection_changed(int)`             | unbound        | Mini preview pane doesn't follow keyboard arrow / mouse hover. |
| `SearchView.open_selected()`                    | unbound        | Pressing Enter on a search result does nothing.                |
| `_MiniPreviewPane.resume_clicked()`            | unbound        | Resume button inside the search-state preview pane is decorative. |
| `RecoveryView.row_clicked(int)`                | unbound        | Clicking an Other-work row doesn't change focus.               |
| `OtherRow.clicked()`                           | bubbled but unconsumed | Same as above.                                       |

None of these were on the directive's "make work" list, but the
audit should record them.

---

## Next fixes (proposed, not executed in P0)

Ordered by user-visible impact ÷ engineering risk.

### P1 — Recovery calibration

The directive's task 3 asked for the Continue card to appear;
the underlying reason it doesn't is calibration, not wiring.
Two-knob proposal:

1. Add `browser_visit` to `_DEPTH_KINDS` but compute depth as
   `0.5 × browser_visit + 1.0 × {open|reveal|chat|search}` so
   passive reading still counts but doesn't drown out active
   work.
2. Lower `_MIN_RESUME_INTENT` from 0.32 → 0.10 so fresh
   high-continuity threads (transition='initial') can surface.

Net effect on the current event store: would surface the
`jiohotstar` + `inbox` threads as Continue candidates with
medium-strength signals. Whether *that's the right product
behaviour* is a calibration call I won't make unilaterally.

### P1 — Search row selection model

Wire `SearchView.selection_changed` + `open_selected` +
`_MiniPreviewPane.resume_clicked`. Currently the search list is
visual only: the "selected" lavender highlight is a static
property on the design's first investigation row. Real
keyboard / mouse selection requires storing a selected-row
index in `SearchView`, emitting changes, and feeding the
chosen investigation into the preview pane.

### P2 — Fake-surface cleanup

Replace the four hard-coded strings (Resume header time,
last-active footer copy, mini-preview placeholder lines,
strength-dot heuristic) with either engine-derived values or
honest absent states.

### P2 — `_LAST_PHASE_RECENCY_DAYS` review

The 7-day last-phase recency gate is strict for a tool whose
job is "remember what I was doing." A 9-day-old investigation
is still recoverable. Consider raising to 14 d (matching
`_RECOVERY_WINDOW_DAYS`).

### P2 — Empty-state honesty on first run

A brand-new install with zero events will show the empty
state and `Show example` triggers demo mode — but the demo
overlay reuses the recovery surface with synthetic data,
which can mislead a fresh user about whether the engine has
real data yet. Add a small "DEMO" pill on the recovery hero
when `demo_mode.is_active()` so the surface stays honest.

---

## Files touched in P0

| Path                                     | Change                                                                                        |
|------------------------------------------|-----------------------------------------------------------------------------------------------|
| `app/ui/launcher_v3/live.py`             | rewired `_search_engine_to_groups` to `api_client.search()`; added `_wire_empty_view` + `_on_show_example` + `_on_start_working` + `_on_preview_open`; extended `_wire_recovery_view` to bind `preview_open`; added two `_wire_empty_view()` calls at the STATE_EMPTY transition sites; added `_glyph_for_episodic` helper. |
| `app/ui/launcher_v3/darkframe.py`        | added additive `RecoveryView.preview_open` signal forwarding from PreviewCard; added `_ClickableLabel` subclass so the Open ↗ link actually fires a click; replaced the plain `QLabel` in `PreviewCard` with the clickable variant. |
| `PRODUCT_RECOVERY.md`                    | this file.                                                                                    |

Lint clean on both modified Python files. Offscreen
construction verified: `Launcher(FakeEngine())` builds, state
transitions work, empty view exposes `show_example` +
`start_working`, recovery view exposes `preview_open`, and the
search rewire returns real grouped results against the live
daemon.

---

## What didn't happen in P0

- **No design changes.** The dark surface is bit-identical to
  what shipped in Phase 10D / 11A.
- **No new components.** Only an `additive` `_ClickableLabel`
  helper inside `darkframe.py` (10 LOC) and additive signal
  wiring on `RecoveryView` (one new `preview_open`).
- **No engine calibration.** Recovery gates unchanged.
  Documented above as a P1 follow-up.
- **No landing changes.** `apps/web/` untouched.
- **No git operations.** Per the standing memory rule.

The launcher now talks to its own daemon for search instead of
guessing through the file index, three previously-decorative
buttons are wired to real handlers, and the diagnosis above
names every remaining gap with its severity and an estimated
fix path.
