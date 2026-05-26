# Repo State — Phase 8A

The state-of-the-repo summary after the full audit. Read
this *first*; the other AUDIT/ docs are the evidence.

> Success: understand the entire repo. No more accidental
> building. No more launcher rewrites. No more code slop.

---

## What Recall is

Recall is a **local-first continuity operating system**.
The user's machine captures what they were *mentally
working on* across browser, files, chat tools, and time
— and resurfaces it later as recoverable threads of work.

Concrete shipping shape today:

| Layer            | Implementation                                                          |
|------------------|-------------------------------------------------------------------------|
| Capture          | Browser extension (Chromium MV3) → loopback HTTP → daemon → JSONL       |
| Engine           | 7 sacred layers: events → sessions → contexts → resurfacing → threads → evolution → recovery |
| Surface          | PyQt6 desktop launcher (frozen 700×500) + browser-popup (frozen 440×640) |
| Trust            | All state on `~/.recall/`; no cloud; no telemetry                       |
| Ops              | 8 CLIs: `doctor`, `capture {status,tail}`, `inspect`, `trust review`, `stats`, `founder`, `alpha`, `repair`/`reset`/`reinstall-check` |

The whole product fits inside one local install + one
browser extension. No accounts, no servers, no
subscription.

---

## What ships

The user-facing surfaces, ranked by importance:

1. **Desktop launcher** (`python recall.py` → frozen
   700×500). Hero card + Recent Memory + OTHER WORK +
   trust row. [Phase 7E, contract frozen 7E.1.]
2. **Browser extension** (Chromium MV3, frozen 440×640).
   Continue document + Activity status + Trust strip.
   [Phase 7A, frozen.]
3. **Resume pipeline** — preview overlay + restore toast
   inside the launcher. [Phase 6P.]
4. **Capture pipeline** — extension → daemon → JSONL →
   threads → recovery. [Verified Phase 7D.]
5. **Diagnostic CLIs** (`doctor`, `capture`, `inspect`,
   `trust`). Each diagnoses a specific hop.
6. **Operator surfaces** — `founder` CLI + admin control
   room (`apps/admin/web/`). Local-only.
7. **Windows installer** (`Recall-Setup-lite.exe`,
   216 MB; `-full.exe`, 261 MB).

Marketing site (`apps/web/`) + docs site (`apps/docs/`)
also ship but aren't part of the runtime product.

---

## What is dead

Today's dead-or-near-dead surfaces:

| Item                                              | Status         | Evidence                                  |
|---------------------------------------------------|----------------|-------------------------------------------|
| 8 pre-7A extension components                     | **DEAD**       | Not imported by current `App.tsx`. See [`DEAD_CODE.md`](DEAD_CODE.md) §9. |
| 7 root-level launcher PNGs                        | **ORPHAN**     | No consumer found. See [`ASSETS.md`](ASSETS.md). |
| 5 API routes                                      | **ORPHAN**     | `thread_forget`, `contexts/recent`, `sessions/recent`, `replay_day`, `threads_clear_evolution_cache`. See [`DEAD_CODE.md`](DEAD_CODE.md) §6. |
| 3 marketing-web npm dependencies                  | **UNUSED**     | `clsx`, `lucide-react`, `tailwind-merge`. See [`DEPENDENCIES.md`](DEPENDENCIES.md). |
| 1 extension dep in wrong section                  | **MISPLACED**  | `playwright` in `dependencies` instead of `devDependencies`. |
| v3 search results panel                           | **TODO**       | `_request_search` signal fires into the void; no consumer renders the results. |

---

## What survives

The healthy spine of the product:

| Layer / surface                                                              | Note                                  |
|------------------------------------------------------------------------------|---------------------------------------|
| The 7 sacred engine layers (events → sessions → … → recovery)                | Stable, well-documented, tested        |
| `app/ui/launcher_v3/` (the v3 launcher tree)                                 | Frozen contract (7E.1)                 |
| `apps/extension/ui/src/components/v2/`                                       | Frozen surface (7A)                    |
| `apps/admin/web/` (control room) + 12 routes                                 | Loaders read straight from disk        |
| `apps/web/` (marketing site)                                                 | Phase 6G; minimal                      |
| `app/core/{recovery,bad_recoveries,daily_loop,desktop,demo_mode}.py`         | All wired + tested                     |
| `api/main.py` + `api/services/*`                                             | Loopback-only; pydantic-strict         |
| Diagnostic CLIs (`capture`, `inspect`, `trust review`, `doctor`, `stats`)    | Each diagnoses a real pipeline hop     |
| Installer (`recall.spec` → Inno Setup)                                       | Windows-only today                     |
| Resume pipeline (Phase 6P — preview + toast + per-step `os.startfile`)        | All hops alive                         |

---

## What gets deleted next (if anything)

Phase 8A is *audit*, not *deletion*. The catalogue below
is what an 8B might safely remove **after re-verifying
each row's grep evidence**:

### Tier 1 — safe-to-delete after re-grep (high confidence)

```
assets/screenshots/control-room.png
assets/screenshots/doctor-output.png
assets/screenshots/installer-flow.png
assets/screenshots/settings-dialog.png
assets/screenshots/launcher-first-week.png
assets/screenshots/launcher-loading.png
assets/screenshots/launcher-offline.png
```

7 root-level PNGs. Stale timestamps, no `grep` consumers.

### Tier 2 — requires `npm uninstall` + build verify

```
apps/web/package.json — remove `clsx`
apps/web/package.json — remove `lucide-react`
apps/web/package.json — remove `tailwind-merge`
apps/extension/ui/package.json — move `playwright` to devDependencies
```

### Tier 3 — requires verifying the legacy escape hatch isn't needed

```
app/ui/launcher_legacy.py
app/ui/launcher_anims.py
app/ui/launcher_digest.py
app/ui/cards.py
app/ui/widgets.py
app/ui/styles.py
app/core/demo_data.py
app/core/ceremonies.py
```

Only after running `_smoke_api.py` + a real user-walk
without the legacy launcher.

### Tier 4 — requires removing handlers + updating extension

```
api/main.py — remove `thread_forget`, `contexts/recent`,
              `sessions/recent`, `replay_day` routes
```

### Tier 5 — finish the v3 search loop, then no deletion needed

The v3 search results panel was scaffolded by 6I + 6J but
never wired to live data. Either wire it (so `_request_search`
has a consumer) or delete the panel.

---

## Verify (Phase 8A live readings, this machine, this run)

```
$ python recall.py doctor
  GREEN   config       2 folder(s) indexed
  GREEN   events       5 day-file(s) on disk
  GREEN   event flow   events in the last 24h
  GREEN   daemon       127.0.0.1:4545 ok (8 ingested total)
  GREEN   extension    browser events in the last 7d
  YELLOW  launcher     stale instance lock (PID 28176 not alive)
  GREEN   installer    Recall-Setup-lite.exe (216.2 MB) / Recall-Setup-full.exe (260.8 MB)
  YELLOW  autostart    autostart off (no Run key, no Startup shortcut)
  YELLOW  protocol     recall:// not registered (extension Open won't deep-link)
  YELLOW  versions     engine 0.1.0 vs extension 2.0.0 (drift; manual check)

$ python recall.py capture status
  events today        8
    tabs                  8  (browser_visit)
  returns (>= 30 min gap)   0
  investigations            11
  last event                11:52:32 UTC  (38m ago)
                            kind = browser_visit

$ python recall.py founder status
  Health (top of dashboard):
    [YELLOW] Active installs        12
    [YELLOW] Returning installs     5
    [GREEN ] Continuity restored    78%
    [GREEN ] Resume sessions        41
    [GREEN ] Investigations         134
    [GREEN ] Extension connected    75%

$ npx tsc --noEmit  (extension UI / admin web / marketing web)
  All clean.

$ Offscreen LiveLauncher boot
  Launcher boots: (700, 500)
```

**Zero red flags.** Five YELLOWs across the audit
surface — all of them are either *the user hasn't done
this yet* (autostart, recall:// registration) or *drift
the user can fix manually* (stale lock, version drift,
active-install count).

---

## The freeze rules

Phase 7E.1 froze the launcher contract
([`docs/product/LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md)).
Phase 8A documents the surface inventory + the wiring
maps. The combined rule:

> Future phases may **add** to the surface. They may
> **not remove or rename** anything in the contracts
> below. Removal requires (a) updating the host first,
> (b) waiting one release, (c) then removing from the
> widget, (d) then updating the contract doc.

The contracts:

- `MinimalSearchBar` 5 signals + 3 methods
- `LiveLauncher` 2 signals + 4 methods + 4 hotkeys
- `RecoveryCardV3` 1 signal + constructor signature + 3 attrs
- `InvestigationCardV3` + `InvestigationList` — `open_thread`
  + `activated` signals + `_titles` property
- `MinimalWindow.DEFAULT_SIZE` = `(700, 500)` (hard
  clamp, frozen 7E)

---

## What this audit prevents

- **Accidental rebuilds.** Every surface has a status +
  an owner. A future contributor opens [`SURFACES.md`](SURFACES.md)
  and knows whether what they're about to "improve" is
  already LIVE, LEGACY, or ARCHIVE.
- **Silent regressions.** The contracts ([`LAUNCHER_MAP.md`](LAUNCHER_MAP.md)
  + [`LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md))
  list every symbol the host depends on. A rewrite that
  drops one is a real bug; the contract catches it.
- **Bit rot.** Every dead-code claim in [`DEAD_CODE.md`](DEAD_CODE.md)
  is *evidence-based* — file path + line number + grep
  result. The next audit can re-verify in minutes.
- **Surface sprawl.** [`SURFACES.md`](SURFACES.md) caps
  the total at ~36 LIVE surfaces. Adding a 37th now
  comes with an explicit cost (one more row in the
  inventory, one more thing to test, one more thing to
  diagnose).

---

## What this audit does NOT do

- **No deletions.** Every "delete next" in the tier
  list above is a recommendation, not an action.
- **No refactors.** The duplicate confidence logic
  catalogued in [`DEAD_CODE.md`](DEAD_CODE.md) §3 still
  ships as two implementations.
- **No new tests.** The audit ran the existing CLIs +
  build checks; it did not author new test files.
- **No new features.** This is the audit phase, not a
  feature phase. The directive's first line: *STOP
  BUILDING FEATURES.*

---

## Success criterion

> Understand the entire repo. No more accidental
> building. No more launcher rewrites. No more code
> slop.

Met by:

1. The 6 AUDIT/ docs (this one + SURFACES + DEAD_CODE +
   LAUNCHER_MAP + CAPTURE_MAP + ASSETS + DEPENDENCIES)
   plus the DOC_INDEX cross-link. Every line of evidence
   in the audit cites a file path or a CLI output.
2. The launcher's frozen contract (Phase 7E.1) is now
   the documented spine — no future rewrite can drop a
   signal silently.
3. Phase 8A's recommendation list is *tier-graded* —
   easy deletes first, contract-impact deletes last.
   Future contributors don't need to guess what's safe
   to remove.

The next phase, if there is one, should be **8B —
Execute Tier 1** (delete the 7 orphan PNGs after fresh
re-grep), or *no new phase* — the repo is healthy.
