# CONTROL_ROOM_V2.md — the founder's operating system

Phase 6J turned the control room at [`apps/admin/web/`](../../apps/admin/web)
from a single-page dashboard into the founder's actual operating
system for Recall. Pairs with
[`CONTROL_ROOM.md`](CONTROL_ROOM.md) (the Phase 5E origin doc) and
[`FOUNDER_OPERATIONS.md`](FOUNDER_OPERATIONS.md) (the daily runbook).

This page is the **user manual** the founder reaches for when they
want to understand a surface they're looking at. The
implementation receipt is
[`PHASE_6J_STATUS.md`](../../archive/phase-status/PHASE_6J_STATUS.md).

---

## The shell

Every route renders inside the same chrome:

```
┌──────────────────────────────────────────────────────────────────┐
│  Top bar       Recall · health · readiness · installs · ⌘K       │
├────────────┬────────────────────────────────┬────────────────────┤
│  Left rail │   Main route content            │   Actions sidebar │
│  (12 rows) │   (server-rendered, no cache)   │   (7 buttons)     │
├────────────┴────────────────────────────────┴────────────────────┤
│  Bottom bar    v0.2.0 · doctor GREEN · phase-6J · local           │
└──────────────────────────────────────────────────────────────────┘
```

- **Top bar** — always visible. Three live pills (daemon · readiness · installs), the wordmark, the `⌘K` command-palette trigger.
- **Left rail** — 12 sections, 4 groups (overview · cohort · engine · ship · lab), accesskey hotkeys 1-9 + 0.
- **Actions sidebar** — 7 buttons. *Refresh* re-runs the loaders; the other six copy canonical CLI commands.
- **Bottom bar** — version + per-machine doctor verdict + build label.
- **Command palette (⌘K / Ctrl-K)** — fuzzy-search any route or action; arrow keys + Enter to select.

The shell consults six live loaders for its global stats:
`loadAlpha()` (installs), `loadRelease()` (readiness), `loadSystemSnapshot()`
(daemon + doctor). No page renders fake values.

---

## The 14 routes

Eight from Phase 6H, plus five new in 6J, plus the experiments page
that fans out feature flags + alpha gates.

### Engine + cohort

| Route | Loader | What it shows |
|---|---|---|
| `/` | health + alpha + daily + trust + release + system | Overview — every panel in compact mode. The 30-second read. |
| `/users` | `loadAlpha()` | Per-cohort tester table; click → `/replays`. |
| `/recovery` | `loadAlpha()` + `loadJournalEntries()` | **Recovery Lab.** 6-outcome stats + kind filter strip + confidence distribution + 7-day return-after-gap heatmap + time-to-resume bar chart + clickable ledger rows. |
| `/replays?tester=<handle>` | `loadAlpha()` + `loadJournalEntries()` | **Replay Studio.** Per-tester event timeline + coverage line (install / activity / recovery / resume / return / wow / failure). |
| `/daily-loop` | `loadDailyLoop(7)` | 6 counters + 3 signals + 5×7 heatmap. |
| `/trust` | `loadTrustSnapshot()` | Recovery ledger + derived signals. |
| `/alpha` | `loadAlpha()` | Cohort five-signal panel (deep-dive). |

### Ship

| Route | Loader | What it shows |
|---|---|---|
| `/release` | `loadRelease()` | Per-gate progress bars + GO/PARTIAL/NO-GO + blockers. |
| `/system` | `loadSystemSnapshot()` | 5 filesystem-derived doctor checks + **Copy diagnostics** (redacted markdown blob to clipboard). |
| `/extension` | manifest + `loadDailyLoop()` + `loadSystemSnapshot()` | Pairing health · ext/engine version drift · capture rate · popup screenshots · repair commands. |
| `/launcher` | `loadScreenshots()` + filesystem | v3 gallery + **v3 ↔ v2 diff strip** (side-by-side captures) + promotion checklist (wire-in deferred items from Phase 6I). |

### Lab

| Route | Loader | What it shows |
|---|---|---|
| `/experiments` | `loadAlpha()` + `loadDailyLoop()` + `~/.recall/config.json` + `~/.recall/demo.json` + env | **Product Lab.** 8 feature flags (`demo overlay`, `episodic capture`, `browser ingest`, `resurfacing`, `threads`, `daily loop`, `evolution`, `recovery`) — each with its live value, the flip command, and the verdict. Plus the 4-row alpha gate table. Plus 3 GREEN-floor threshold cards. |
| `/logs?source=<id>&q=<query>` | `loadLogSources()` | Picker for 5 sources (doctor / recovery / daily / alpha / release) + filtered viewer + download command. |
| `/screenshots` | `loadScreenshots()` | One section per bucket (launcher-v2 / launcher-v3 / extension-v2 / demo / alpha / legacy flat) with per-bucket verdict, thumbnails, **missing markers** for every expected file the bucket doesn't have. |
| `/docs` | static | Map of canonical docs across product / alpha / release / engineering / founder. |

---

## The command palette

`Ctrl+K` (or `⌘K` on macOS) opens a fuzzy search over every route
and every directive-named action:

```
Run doctor             →  python recall.py doctor
Bake data              →  python recall.py founder bake
Generate alpha report  →  python recall.py alpha export
Export trust           →  python recall.py stats --export
Open screenshots folder
Open alpha folder
Open recovery journal
Open daily loop
Open logs
Refresh data           (router.refresh, no command)
```

Selecting an action copies the command to the clipboard; selecting
a route navigates. The palette never executes anything server-side
— same *no server* contract as the Phase 6H actions sidebar.

---

## The trust contract — restated

Every loader respects the same boundary as the rest of the
product:

1. **Counts only.** No URLs, no filenames, no queries, no chat
   content. Per-tester `wow_moment` / `confusion` / `notes`
   strings are the founder's own paraphrases.
2. **Local only.** Every read is filesystem-local — no HTTP, no
   third-party SDK.
3. **No server endpoint executes anything.** Buttons copy
   commands or trigger a `router.refresh()`. The founder runs
   the commands themselves on their terminal.
4. **Honest empty.** Missing files render an empty-note row, never
   a placeholder zero.

---

## How a deep-dive flows

Example: **a tester reports a bad recovery.**

1. Open `/recovery`. Click the `bad_recovery` filter chip → the
   ledger view narrows.
2. Click the row → lands on `/replays?tester=<handle>` showing the
   per-tester timeline.
3. Hit ⌘K → "Open recovery journal" → opens
   `alpha/recovery_journal.json` in Notepad.
4. Edit the row (add `notes`, set `confidence`); save; the
   dashboard's `Refresh data` reflects the change on the next
   render.
5. If the bad recovery is the second of its kind, open
   `docs/alpha/KNOWN_FAILURES.md` and promote the pattern.
6. ⌘K → "Run doctor" → confirm no engine regression.

Every step in that loop lives inside the same room.

---

## Related

- [`PHASE_6J_STATUS.md`](../../archive/phase-status/PHASE_6J_STATUS.md) —
  the implementation receipt.
- [`PHASE_6H_STATUS.md`](../../archive/phase-status/PHASE_6H_STATUS.md) —
  the v1 control-room foundation 6J extends.
- [`FOUNDER_OPERATIONS.md`](FOUNDER_OPERATIONS.md) — the daily
  cadence the dashboard supports.
- [`CONTROL_ROOM.md`](CONTROL_ROOM.md) — the v1 origin doc.
- [`docs/engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)
  — the boundary every loader honours.
