# PHASE_6H_STATUS.md — Control Room OS

The receipt for Phase 6H. The directive's *Goal*: turn the
control room into an actual founder system. **No fake data. No
hardcoded cards. Everything derived.** A founder opens the room
and understands Recall in 30 seconds; they manage Recall in 5
minutes.

The 6G→6H handoff: 6G built the *public* front door for the
alpha. 6H rebuilds the *founder's* operator surface so it reads
the same live data the CLI reads. The two phases meet at the
same files (`alpha/users/`, `alpha/recovery_journal.json`,
`~/.recall/daily_loop.jsonl`, `apps/admin/data/*`); 6G presents
that data to a stranger, 6H presents it to the operator.

Cross-references:
[`PHASE_6E_STATUS.md`](PHASE_6E_STATUS.md) (alpha CLI + cohort
schema 6H reads from),
[`PHASE_6F_STATUS.md`](PHASE_6F_STATUS.md) (daily-loop layer 6H
reads from),
[`PHASE_6G_STATUS.md`](PHASE_6G_STATUS.md) (the public front
door 6H complements),
[`docs/product/DAILY_LOOP.md`](../../docs/product/DAILY_LOOP.md) (the
green/yellow/red thresholds 6H's panels mirror).

---

## What shipped

### 1. `apps/admin/web/lib/loaders/` — the live data layer

Eight new modules. Every value the dashboard renders flows
through these — there are no more component-local hardcoded
numbers.

| Module | Reads from | Returns |
|---|---|---|
| `paths.ts` | — | the canonical filesystem paths (`REPO_ROOT`, `ADMIN_DATA_DIR`, `ALPHA_USERS_DIR`, `RECOVERY_JOURNAL`, `RECALL_HOME`, `DAILY_LOOP_LOG`, `DEMO_FILE`, `EVENTS_DIR`, `CONFIG_FILE`, `RELEASE_STATE`). One file, one source of truth. |
| `fsx.ts` | — | defensive helpers — `readJSON`, `readJSONL`, `listDir`, `exists`, `fileMtime`, `pct`. Every call returns a typed fallback; the page never throws on a missing file. |
| `health.ts` | `apps/admin/data/health.json` + `~/.recall/` | `HealthSnapshot` — baked cards + live filesystem state (events count, last_event_mtime, config presence). |
| `trust.ts` | `apps/admin/data/trust.json` + `alpha/recovery_journal.json` | `TrustSnapshot` — baked cards + the live 6-kind aggregation. |
| `daily.ts` | `~/.recall/daily_loop.jsonl` + `daily_loop_state.json` | `DailyLoopSummary` — re-derives `today` / `yesterday` / 7-day window + the 3 signals + green/yellow/red verdicts. Mirrors `app/core/daily_loop.summary()` exactly. |
| `alpha.ts` | `alpha/users/<cohort>/<handle>/status.json` + `alpha/recovery_journal.json` | `AlphaExport` — installs / returning / first recoveries / drops / install fails / wrong recoveries + per-cohort table + the live trust counts. Mirrors `recall alpha export`. |
| `release.ts` | `apps/admin/release_state.json` + `apps/admin/data/release.json` | `ReleaseStatus` — normalised gate state + per-gate progress bars + GO/PARTIAL/NO-GO + blockers. |
| `system.ts` | `~/.recall/` (events, instance.lock, config.json, demo.json) | `SystemSnapshot` — the same checks `recall doctor` runs, derived locally. No daemon ping. |
| `index.ts` | — | barrel re-export so the routes import from a single path. |

Every loader is *idempotent* — calling it twice in a row produces
the same shape. The dashboard's *Refresh data* button is a
`router.refresh()`; the loaders re-read the disk on each call.

### 2. Operator shell — `layout.tsx`

Three-column shell wired into the Next.js root layout:

```
┌────────────┬──────────────────────────┬───────────────┐
│  Left rail │   Main route content      │   Actions    │
│  (sticky)  │   (server-rendered)       │   (sticky)   │
└────────────┴──────────────────────────┴───────────────┘
```

- [`Nav.tsx`](../../apps/admin/web/components/Nav.tsx) — 10-row
  sticky left rail, three groups (overview · cohort · engine
  · ship), accesskey hotkeys 1-9 + 0. Active route highlighted
  via `usePathname()`; CSS-only collapse on < 760 px viewports.
- [`ActionsBar.tsx`](../../apps/admin/web/components/ActionsBar.tsx)
  — 7-button sticky right rail. *Refresh data* triggers
  `router.refresh()`; the other six copy a canonical command
  to the clipboard (run on the founder's terminal). **No
  server endpoint executes anything** — the directive's *no
  server* rule held strictly.

CSS for both lives in
[`globals.css`](../../apps/admin/web/app/globals.css) under the
new *Phase 6H — operator shell* block. Visual language matches
the pre-6H styling: warm whites, lavender accents, hairlines,
soft shadows, no glass.

### 3. Six live panels

| Component | Reads | What it shows |
|---|---|---|
| [`HealthPanel`](../../apps/admin/web/components/panels/HealthPanel.tsx) | `HealthSnapshot` | The baked operator cards + a freshness header naming the source + mtime + a live `~/.recall` summary. |
| [`AlphaPanel`](../../apps/admin/web/components/panels/AlphaPanel.tsx) | `AlphaExport` | Six signal cards (installs / returning / first recoveries / trust % / drop reasons / install fails) with green/yellow/red verdicts. Per-cohort table + drop-reasons aggregation in non-compact mode. |
| [`DailyLoopPanel`](../../apps/admin/web/components/panels/DailyLoopPanel.tsx) | `DailyLoopSummary` | Three signal cards (continuity restored / return rate / resume quality) + a 6-row counter table + a 7-day heatmap (5 bins × 7 days). |
| [`TrustPanel`](../../apps/admin/web/components/panels/TrustPanel.tsx) | `TrustSnapshot` | Six outcome stats + a derived-signals row (trust % + returns linked + median time-to-resume) + the baked operator cards. |
| [`ReleasePanel`](../../apps/admin/web/components/panels/ReleasePanel.tsx) | `ReleaseStatus` | Per-gate progress bars (installer / signing / mac / screenshots / alpha packet) + the GO/PARTIAL/NO-GO verdict + the blockers list. |
| [`SystemPanel`](../../apps/admin/web/components/panels/SystemPanel.tsx) | `SystemSnapshot` | Five live filesystem checks (`~/.recall` / config / events / launcher lock / demo overlay state) with green/yellow/red verdicts. |

Plus a shared [`Verdict.tsx`](../../apps/admin/web/components/panels/Verdict.tsx)
pill component — one component, three colours + `mute`, used
everywhere a verdict surfaces.

### 4. Ten routes

| Route | Page | Reads |
|---|---|---|
| `/` | Overview — every panel in compact mode | all 6 loaders |
| `/users` | Per-cohort tester table; click → `/replays` | `loadAlpha()` |
| `/alpha` | Full `AlphaPanel` deep-dive | `loadAlpha()` |
| `/trust` | Full `TrustPanel` deep-dive | `loadTrustSnapshot()` |
| `/daily-loop` | Full `DailyLoopPanel` deep-dive | `loadDailyLoop(7)` |
| `/recovery` | Recovery Room — 6-stat header + time-to-resume bar chart + ledger rows | `loadAlpha()` + `loadJournalEntries()` |
| `/replays` | Per-tester event timeline (`?tester=<handle>`); coverage line | `loadAlpha()` + `loadJournalEntries()` |
| `/release` | Release Center — `ReleasePanel` deep-dive | `loadRelease()` |
| `/system` | System Room — `SystemPanel` deep-dive | `loadSystemSnapshot()` |
| `/docs` | Static index of canonical docs | — |

Every page is a React Server Component with
`export const dynamic = "force-dynamic"`, so each request
re-reads the source files. No cache. No revalidate window. The
data is always *now*.

### 5. Zero hardcoded panel values

Before Phase 6H, panel components carried fallback shapes inline
(empty cohort cards, placeholder trust counts). After 6H, every
panel takes its data through a typed prop and renders an *empty
note* if the source is empty. The `HealthOverview`,
`AlphaCohorts`, and `TrustRoom` legacy components are still in
`components/` (they back the baked-cards section of the panels
that have one), but they no longer get hardcoded data; they
display only what the loader hands them.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Live-refresh via SSE or WebSocket | not in scope | The *Refresh data* button is a `router.refresh()`. SSE would require a long-lived server task; the *no server* rule says no. |
| Charts library | declined | The directive said *keep current style* + warned against a charts-library explosion. The heatmap + sparkline are pure inline SVG / styled `div` strips; no `recharts`, no `d3`. |
| Per-button native dispatch for the six terminal actions | not in scope | The dashboard runs in a browser. Each action button copies the canonical CLI command to the clipboard; the founder pastes into a terminal. No subprocess, no server endpoint — true *all local, no server*. |
| Light/dark theme | not in scope | Single warm-white theme matches the rest of the product. |
| Mac-specific paths in `loadSystemSnapshot` | partial | The loader uses `os.homedir()` for `~/.recall` resolution, which works on macOS / Linux / Windows. Platform-specific checks (Windows registry for protocol handler, macOS Launch Agents for autostart) are deferred — those signals already live in `recall doctor` and the *Run doctor* action copies that command. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| Loaders TS | `cd apps/admin/web && npx tsc --noEmit` | zero findings |
| Next.js build | `cd apps/admin/web && npm run build` | ✓ compiled / 10 routes + `_not-found` / each ƒ-tagged (dynamic server-rendered on demand) / first-load JS 87.4 KB shared |
| Zero hardcoded panels | grep panels for fixture data | every panel renders from a typed prop populated by a loader — confirmed by file audit |
| Live read from cohort data | dashboard `/users` open | shows the 0 testers currently in `alpha/users/` honestly; would surface real testers the moment the cohort starts |
| pyflakes (regression) | `python -m pyflakes app/ui app/core api` | zero findings — Phase 6H touched **no** Python file |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6G |
| Extension build (regression) | `cd apps/extension/ui && npm run build` | unchanged from 6G |

---

## Touched files

```
new code:
  apps/admin/web/lib/loaders/paths.ts
  apps/admin/web/lib/loaders/fsx.ts
  apps/admin/web/lib/loaders/health.ts
  apps/admin/web/lib/loaders/trust.ts
  apps/admin/web/lib/loaders/daily.ts
  apps/admin/web/lib/loaders/alpha.ts
  apps/admin/web/lib/loaders/release.ts
  apps/admin/web/lib/loaders/system.ts
  apps/admin/web/lib/loaders/index.ts
  apps/admin/web/components/Nav.tsx
  apps/admin/web/components/ActionsBar.tsx
  apps/admin/web/components/panels/Verdict.tsx
  apps/admin/web/components/panels/HealthPanel.tsx
  apps/admin/web/components/panels/AlphaPanel.tsx
  apps/admin/web/components/panels/DailyLoopPanel.tsx
  apps/admin/web/components/panels/TrustPanel.tsx
  apps/admin/web/components/panels/ReleasePanel.tsx
  apps/admin/web/components/panels/SystemPanel.tsx
  apps/admin/web/app/alpha/page.tsx
  apps/admin/web/app/trust/page.tsx
  apps/admin/web/app/daily-loop/page.tsx
  apps/admin/web/app/release/page.tsx
  apps/admin/web/app/system/page.tsx
  apps/admin/web/app/recovery/page.tsx
  apps/admin/web/app/replays/page.tsx
  apps/admin/web/app/users/page.tsx
  apps/admin/web/app/docs/page.tsx

modified code:
  apps/admin/web/app/layout.tsx       (three-column shell)
  apps/admin/web/app/page.tsx         (overview — six live panels)
  apps/admin/web/app/globals.css      (operator shell + verdict pills + heatmap + panel-row)

new docs:
  docs/engineering/PHASE_6H_STATUS.md
```

No `app/core/`, `api/`, `app/ui/` (launcher / widgets / settings),
`apps/extension/`, or `apps/web/` (marketing site) files were
touched. The directive's *no fake data, no hardcoded cards,
everything derived* rule held.

---

## Read-back of the success criterion

The directive named two outcomes:

> open control room — understand Recall in 30 sec

The `/` overview surface is now a single scroll: engine health
→ cohort signals → daily-loop signals → trust ledger →
release verdict → system filesystem state. Every panel carries
a green/yellow/red read at the top so a glance is enough.

> manage Recall in 5 min

The left rail is the index; the actions sidebar is the action
set. The seven actions cover the daily founder loop:
*Refresh* re-reads everything; *Bake* / *Doctor* / *Alpha
report* / *Open screenshots* / *Open logs* / *Export health*
are one-click copies of the canonical commands. Five minutes
end-to-end is realistic: open the room, glance the overview,
hit Refresh after a bake, walk to any deep-dive that lights
yellow.

Both outcomes are now real — the room is no longer a static
mock-up; it is the founder's operating system for Recall.
