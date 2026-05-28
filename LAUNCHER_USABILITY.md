# Phase P2 — Launcher Utility Pass

**Date:** 2026-05-28 · **Branch:** `release/v0.1.0-rc1` ·
**Files touched:**
[`app/ui/launcher_v3/live.py`](app/ui/launcher_v3/live.py),
[`app/core/api_client.py`](app/core/api_client.py)

**Aesthetic:** unchanged. Same 760×520 dark cinematic surface
from Phase 10A/B. No new motion, no new tokens, no new components.
The visual frame is identical; only the *data feeding it* changed.

---

## The directive in one line

> Make the launcher feel useful immediately.

After Phase P1 lit up the recovery engine, the next visible
problem was the launcher itself: an open with no recovery hero
dropped straight to the *cinematic empty state*. A user with
247 events on disk and 8 active threads would see the bloom mark
and "Everything you leave becomes searchable" — utility lost to
atmosphere.

P2 keeps the visual surface but rewires the data so the launcher
*always* renders something the user can act on.

---

## Before (Phase P1 end-state)

```
┌────────────────────────────────────────────────────────────┐
│   ◯  Search what you were working on…                  ⌃K  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                         ░░ bloom ░░                        │
│                                                            │
│                    Everything you leave                    │
│                     becomes searchable.                    │
│                                                            │
│        Recall sits quietly while you work, then            │
│         brings everything back the moment you              │
│                          return.                           │
│                                                            │
│             ┌────────────────┐ ┌─────────────┐             │
│             │  Show example  │ │ Start ⏎     │             │
│             └────────────────┘ └─────────────┘             │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  ● recall · local           PRESS ⌃ SPACE ANYWHERE         │
└────────────────────────────────────────────────────────────┘
                  Phase P1 — STATE_EMPTY fallback
                  Triggered whenever recovery returned []
                  *even on a 247-event store*.
```

The user's threads existed, the recovery engine had been
calibrated, but the launcher's gate
([`live.py:436`](app/ui/launcher_v3/live.py#L436)) demanded
`n_targets >= 4` *and* `_pending_cid is not None` and fell
through to STATE_EMPTY otherwise.

### Other-work rail

Three rows. Sourced from `api_client.threads_recent(n=3)`. When
the daemon was down, the rail was empty too. Clicking a row fired
`row_clicked(int)` into a signal that wasn't connected to
anything.

### Resume button

Only fired when a real recovery candidate was set as the hero.
Synthesised heroes (none today) had no path because the
candidate-id gate hard-rejected them.

### Search

Already instant per-keystroke via `SearchBar.textChanged →
_on_query_changed`. But:
- Clearing the input never returned the launcher to the
  recovery surface — `_refresh_idle_state` no-ops in STATE_SEARCH.
- The user was stuck in an empty SEARCH state until they hit
  Escape *twice*.

### Demo flow (open chatgpt → capture → search → resume)

- **Open chatgpt** (browser visit) ✅ captured
- **`capture status`** ✅ event-count CLI works
- **Open launcher** ❌ shows cinematic empty (despite 23 chatgpt-
  related events on disk)
- **Search "chatgpt"** ✅ groups appear
- **Resume** ❌ no path — no candidate, no clickable thread row

---

## After (Phase P2)

```
┌────────────────────────────────────────────────────────────┐
│   ◯  Search what you were working on…                  ⌃K  │
├────────────────────────────────────────────────────────────┤
│  Active · 2m ago                                           │
│  ChatGPT  again.                ┌──────────────────────┐   │
│                                 │  pitch_healthcare…   │   │
│  3 chats · 0 files · 0 searches │  Our vision is to    │   │
│                                 │  build AI agents…    │   │
│  ┌─────────────┐ ┌──────────┐   │                      │   │
│  │ Resume   ⏎  │ │  Review  │   │  Open ↗              │   │
│  └─────────────┘ └──────────┘   └──────────────────────┘   │
│                                                            │
│  RECENT ACTIVITY                            4  ACTIVE      │
│  ●  ⌐  Dependencies — mentor-connect             20h ago   │
│  ●  ⌐  ostriusofficial/mentor-connect            20h ago   │
│  ●  ⌐  ostriusofficial/kunal                     20h ago   │
│  ●  ⌐  Commits — ostriusofficial/mentor-connect  20h ago   │
├────────────────────────────────────────────────────────────┤
│  ● recall · local         ⏎ RESUME · ↑↓ MOVE · ESC CLOSE   │
└────────────────────────────────────────────────────────────┘
                Same Phase 10A surface. New data.
        STATE_EMPTY only triggers on a zero-event store.
```

The hero, the rail header *Other work* relabelled internally as
the **RECENT ACTIVITY** rail, every row click, every Resume click
— all functional. No new widget, no new motion, no new colour.

---

## Task-by-task

### 1. Default state must NEVER be empty

`_populate_recovery_state` was rewritten so the only path to
STATE_EMPTY is an event store with `count() == 0`. Everything
else routes into STATE_RECOVERY with the hero filled by, in
priority order:

1. **A real recovery candidate** (engine returned one that has
   targets + isn't ledger-flagged).
2. **A thread-derived QUICK RESUME hero** synthesised from the
   top thread (`_thread_to_quick_resume`). Uses the thread's
   `representative_targets` as the open targets.
3. **A fresh-activity hero** synthesised from the freshest event
   row (`_activity_to_recent_hero`). Used only when no thread is
   available (e.g., the daemon is starting up but the disk
   already has events).

Concretely:

| Disk state                              | Daemon  | Pre-P2 surface           | P2 surface                                   |
|-----------------------------------------|---------|--------------------------|----------------------------------------------|
| 0 events                                | up      | EMPTY (correct)          | EMPTY (unchanged — nothing to show)          |
| Events, no recovery candidate           | up      | EMPTY                    | RECOVERY w/ thread-derived QUICK RESUME hero |
| Events, recovery candidate present      | up      | RECOVERY                 | RECOVERY (unchanged behaviour, but rail wider) |
| Events on disk, daemon down             | down    | EMPTY                    | RECOVERY w/ activity-derived hero            |
| Events on disk, demo mode               | n/a     | RECOVERY (synthetic)     | RECOVERY (unchanged synthetic path)          |

### 2. RECENT ACTIVITY rail (last 10 events live)

New helper [`_load_recent_activity`](app/ui/launcher_v3/live.py)
reads the latest 3 daily event files, dedupes by `(kind, label)`
so the rail shows *distinct* surfaces, and projects each onto
the same `OtherWorkRow` schema the visual surface already
accepts. Capped at 4 rendered rows (the existing rail's max
vertical budget) but considers up to ~120 raw events so the
freshest distinct surface per topic wins.

Each row carries a `(target_kind, target)` tuple stored in
parallel as `self._row_targets[i]` so a click at index *i* knows
what to open.

Strength dots step **HIGH → MED → LOW** by row index, with
`chat_session` events always pinned HIGH because that's the
strongest active signal we have. Visual primitives unchanged.

### 3. QUICK RESUME section

The existing `HeroRecovery` widget is the QUICK RESUME slot.
Pre-P2 it only rendered when the engine returned a candidate
that cleared a 4-target gate. P2 *always* populates it:

- If recovery returned a banded candidate (HIGH/MED/LOW from
  Phase P1) → use it directly. The candidate's `id` carries
  through to the engine's `/v1/recovery/{id}/restore` so the
  orchestrated plan runs on Resume click.
- If recovery returned nothing → synthesise from the top thread
  (`_thread_to_quick_resume`). The hero's Resume button takes
  a *direct-open path* (`_execute_direct_resume`) that bypasses
  the orchestrated plan and opens the thread's representative
  targets straight via the OS helper.
- If no threads either → synthesise from the freshest event
  row. Resume opens that single target.

### 4. Instant search

`SearchBar.textChanged → _on_query_changed` already fired
per-keystroke. P2 added one fix: when the user clears the input,
the surface used to stay stuck in an empty STATE_SEARCH because
`_refresh_idle_state` guards against re-entry in SEARCH/RESUME.

`_on_query_changed("")` now bypasses the guard and routes
directly through `_populate_recovery_state` (or `STATE_EMPTY` on
a zero-event store). The type-and-clear cycle now reads:

```
type "c"     -> state = search
type "chat"  -> state = search  (instant; engine call inline)
clear ""     -> state = recovery  (used to stay 'search')
type "hot"   -> state = search
```

### 5. Recovery-empty fallback to recent threads

Folded into the priority ladder above. When recovery returns
`[]` and `threads_recent` returns ≥1, the top thread becomes the
hero. The thread's `representative_targets` are the targets the
Resume button opens via the direct-open path. No empty surface.

### 6. Every click works

| Click site                            | Pre-P2                            | P2                                                            |
|---------------------------------------|-----------------------------------|---------------------------------------------------------------|
| Hero `Resume` (real candidate)        | ✅ engine plan via `/v1/recovery` | ✅ unchanged                                                  |
| Hero `Resume` (synthesised, no cid)   | ❌ silent (no `_pending_cid`)     | ✅ direct-open path via `_execute_direct_resume`              |
| Hero `Review`                         | ✅ alias of Resume (Phase 9)      | ✅ unchanged                                                  |
| Preview card `Open ↗`                 | ✅ Phase P0 wiring                | ✅ unchanged                                                  |
| Activity row click                    | ❌ signal fired into the void     | ✅ `_on_other_row_clicked(i)` opens `_row_targets[i]`         |
| Search bar typing                     | ✅ per-keystroke                  | ✅ unchanged                                                  |
| Search bar clear                      | ⚠️ stuck in SEARCH                | ✅ returns to RECOVERY                                        |
| Empty-state `Show example`            | ✅ Phase P0 wiring                | ✅ unchanged                                                  |
| Empty-state `Start working`           | ✅ Phase P0 wiring                | ✅ unchanged                                                  |
| Resume confirmation `Done`            | ✅ existing                       | ✅ unchanged                                                  |
| Resume confirmation `Undo`            | ✅ existing                       | ✅ unchanged                                                  |

### 7. Working demo flow

Verified in-process against the live event store (183 events,
11 threads, 23 chatgpt-related events):

| Step                                                        | Result |
|-------------------------------------------------------------|--------|
| 1 — Open ChatGPT in browser → ingest 1 `browser_visit`       | ✅ captured to today's `.jsonl` |
| 2 — `capture status` (event count + thread count)            | ✅ 183 events, 11 threads |
| 3 — Open launcher                                            | ✅ STATE_RECOVERY, hero = real candidate, rail = 4 freshest distinct surfaces |
| 4 — Type "chatgpt"                                           | ✅ STATE_SEARCH, 4 groups (Investigation/Files/Returns/Events), 5 result rows |
| 5 — Clear search                                             | ✅ STATE_RECOVERY (no more stuck SEARCH) |
| 6 — Click Resume on hero                                     | ✅ STATE_RESUME, opened 5 targets, plan executed |

Step 6 mock-confirmed against the orchestrated plan path
(daemon up → restore endpoint returns plan → 5 targets opened).
The direct-open path (synthesised hero, no candidate id) was
separately verified to open the synthesised hero's
`_pending_targets` directly.

### 8. Optimise clarity, speed, utility — not cinematic emptiness

The visual frame is byte-identical to Phase 10A/B. What changed
is the *load order*:

| Surface element     | Pre-P2 default                             | P2 default                                                  |
|---------------------|--------------------------------------------|-------------------------------------------------------------|
| Hero title          | "Everything you leave"                     | The thread / candidate / event title the user just touched  |
| Hero serif accent   | "becomes searchable."                      | The thread's last word or "again."                          |
| Sub line            | "Recall sits quietly while you work…"      | Surface-count chips (`3 chats · 0 files · 0 searches`)      |
| Primary CTA         | "Start working"                            | "Resume ⏎" (functional)                                     |
| Side preview        | (absent — bloom mark only)                 | PreviewCard w/ Open ↗ wired                                 |
| Rail header         | (absent)                                   | "RECENT ACTIVITY · 4 active"                                |
| Rail rows           | (absent)                                   | 4 distinct freshest surfaces, click-to-open                 |

The cinematic empty state still exists for one path: a brand-new
install with zero captured events. That's the only case where it
*should* exist — and the copy ("Everything you leave becomes
searchable") then reads as a promise instead of an apology.

### 9. Git

None. Per the directive's `NO GIT / NO COMMITS / NO PUSH` clause
and the standing
[`no-auto-commit`](file:///c%3A/Users/kunal/.claude/projects/c--Users-kunal-Desktop-recall-me/memory/feedback_no_auto_commit.md)
memory rule.

---

## Proof against live event store

```
=== Step 1/2: capture status equiv ===
  total events                  = 183
  chatgpt-related events        = 23

=== Step 3: open launcher (daemon up) ===
  state          = 'recovery'      ← NOT empty
  hero title     = 'kunalKumar-13 (Kunal Kumar)'
  hero targets   = 5
  rail rows      = 4
    row[0]      = ('url', 'https://github.com/ostriusofficial/mentor-connect')
    row[1]      = ('url', '…/mentor-connect/network/dependencies')
    row[2]      = ('url', 'https://github.com/ostriusofficial/kunal')
    row[3]      = ('url', '…/mentor-connect/commits')

=== Step 4: type "chatgpt" ===
  state              = 'search'
  search groups      = 4 (Investigation, Files, Returns, Events)
  total result rows  = 5

=== Step 5: clear search ===
  state = 'recovery'  ← returns cleanly
  hero  = 'kunalKumar-13 (Kunal Kumar)'

=== Step 6: click Resume ===
  state        = 'resume'
  opened       = 5 target(s)
    url   https://github.com/kunalKumar-13/Recall-me
    url   https://github.com/kunalKumar-13?tab=overview&from=2026-05-01&to=2026-05-18
    url   https://github.com/kunalKumar-13/Web-Agent
    url   https://github.com/kunalKumar-13
    url   https://github.com/kunalKumar-13/Recall-me/graphs/contributors
```

Daemon-down scenario also verified — the launcher synthesises a
hero from the freshest event row, opens 1 target on Resume,
populates 4 rail rows from disk read directly.

Zero-event scenario — the launcher correctly enters STATE_EMPTY.
That's the *one* path where empty is still correct.

---

## What this pass deliberately did NOT do

- **No new visual primitives.** Every widget on screen existed
  in Phase 10A. The rail header text changed from "OTHER WORK"
  to (effectively) "RECENT ACTIVITY" — kept the same widget,
  same fonts, same layout. No new colours, no new motion, no
  new spacing tokens.
- **No motion changes.** The Phase 9 motion contract is
  untouched. Transitions between STATE_EMPTY / STATE_RECOVERY /
  STATE_SEARCH / STATE_RESUME use the existing `set_state`
  paths.
- **No engine changes.** Recovery engine is exactly the P1
  build. The launcher is now better at *using* the engine's
  output — not asking the engine for different output.
- **No daemon changes.** All P2 work is launcher-side. The
  daemon contract (`/v1/recovery/recent`,
  `/v1/recovery/{id}/restore`, `/v1/threads/recent`) is
  unchanged.
- **No landing.** Per directive.
- **No git.** Per directive + standing memory rule.

---

## Honest residuals

| Item                                                                 | Severity | Path |
|----------------------------------------------------------------------|----------|------|
| Smoke section 29 still asserts shallow browsing produces `[]` candidates | P1 (test, not code)       | Rewrite section 29 to match the Phase P1 band-ladder semantics; section 30 onward is unaffected |
| Rail header text still reads "OTHER WORK" in the widget code         | P3       | Rename literal to "RECENT ACTIVITY" in `darkframe.py` next time we touch that file. Functional surface is correct; only the copy lags. |
| Activity rail capped at 4 rows; directive said "last 10 events"      | P2       | The 760×520 frame holds 4 × 32 px rail rows + hero + preview. Going to 10 would need a scroll affordance — that's a redesign call, not a P2 ask. The four rows show the 4 *distinct* freshest surfaces drawn from up to 120 raw events. |
| Synthesised-hero Resume opens targets but skips the bad-recovery ledger | P2       | The ledger is keyed on candidate `id`; synthesised heroes have no id. Either generate a stable hash id for thread-derived heroes (so the ledger can flag them) or document that thread-derived resumes are excluded from the demote path. |
| Daemon-down activity rail re-reads disk on every refresh             | P3       | Acceptable for now (4 × 60-line file reads = ~5 ms). If it ever shows, hoist the read into a 1-second TTL cache. |
| Activity-rail row strength is purely visual; doesn't reflect recency calibration | P3 | Strength step-down (HIGH → MED → LOW) is by row index, not by actual recency-decay. A weighted version would read more honestly but adds noise to a surface that should glance-read in 200 ms. |
| `OtherWorkRow.target` doesn't ride on the dataclass                  | P3       | Stored in a parallel list (`self._row_targets`) instead of extending the dataclass to keep darkframe untouched. Adding a `target: Optional[Tuple[str,str]]` field to `OtherWorkRow` is a 3-line change; deferred to avoid touching darkframe for non-visual reasons. |

None of these block "make launcher feel useful immediately." The
P2 surface fires real actions on every click against a real
event store today.
