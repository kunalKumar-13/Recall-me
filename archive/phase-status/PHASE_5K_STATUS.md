# PHASE_5K_STATUS.md — Alpha Reality

The receipt for Phase 5K. The directive: move from founder
testing to real users; build the infrastructure to **receive**
real-user signal. The success line — *5 humans, 3 recoveries,
real friction, real trust signal* — is external-dependent; this
phase delivers every internal surface that signal needs to land
on.

Cross-references:
[`ALPHA_001_RUNBOOK.md`](../../alpha/ALPHA_001_RUNBOOK.md) (the
runbook the cohort actually walks),
[`alpha_report.md`](../../alpha/alpha_report.md) (the founder's
evidence ledger this CLI feeds into),
[`FIRST_72_HOURS.md`](../../alpha/FIRST_72_HOURS.md) (the
hour-by-hour curve),
[`PHASE_5J_STATUS.md`](PHASE_5J_STATUS.md) (the predecessor —
the installer that the cohort actually runs).

---

## What shipped

### 1. `alpha/users/` directory tree

Five cohort folders, each with a `TEMPLATE.md` and (in
`_TEMPLATE/`) the JSON schema the CLI copies:

```
alpha/users/
├── README.md                  the contract + boundary
├── _TEMPLATE/
│   └── status.json            the schema (fields, comments)
├── alpha-001/
│   └── TEMPLATE.md            the first cohort's template
├── alpha-002/
│   └── TEMPLATE.md            queued; opens when alpha-001 closes 3 rows
├── friends/
│   └── TEMPLATE.md            ad-hoc personal contacts
├── builders/
│   └── TEMPLATE.md            the multi-project-persona cohort
└── students/
    └── TEMPLATE.md            the multi-day-arc persona cohort
```

Per-tester fields (`status.json` schema): `handle` /
`cohort` / `install_date` / `platform` / `installer` / `install_ok`
/ `install_minutes` / `day1` / `day2` / `day3` / `first_recovery`
/ `first_resume_ok` / `kept_using` / `drop_reason` /
`feedback_returned` / `notes`. **Metadata only.** Never URLs,
filenames, queries, chat content.

Zero fake testers seeded — the directive's *No content* rule
holds. The folders fill with real handles only via `recall alpha
create`.

### 2. `app/core/alpha_cli.py` + dispatch

Three subcommands, ~280 LOC, stdlib only:

| Command | Action |
|---|---|
| `recall alpha create <handle> --cohort <name>` | copies the JSON template into `alpha/users/<cohort>/<handle>/`, fills `handle` + `cohort` + `install_date: <today>`, refuses to overwrite |
| `recall alpha status [--cohort <name>]` | one calm row per tester with a `YYY|R3`-style compact day/recovery summary |
| `recall alpha report [--cohort <name>]` | aggregate counts: users / returning / first-recovery / issues / blockers + platform breakdown + the directive's `5 humans / 3 recoveries / 2 returning` target check |

Validation:

- Cohort must be one of the five (`alpha-001`, `alpha-002`,
  `friends`, `builders`, `students`); typos rejected.
- Handle must be ≤ 24 chars, no `@`, no spaces, alphanumeric +
  `-` / `_` only — rejects email-shaped strings to keep PII
  off-disk.
- Refuses to overwrite an existing tester folder.

Wired into `recall.py`'s fast-path dispatch next to `stats` /
`doctor` / `founder` / `repair` / `reset` / `reinstall-check`.

### 3. `alpha/ALPHA_FEEDBACK_V2.md`

The tighter intake form. Six rows, each mapped to a concrete
artifact the founder must update if the row is filled:

| V2 row | Maps to |
|---|---|
| moment of delight | `alpha_report.md` Q5 |
| confusion | `alpha_report.md` Q5 + a row in `OPEN_PROBLEMS.md` |
| wrong recovery | `recovery_journal.json` with `wrong: true` |
| missed recovery | calibration ledger + the readiness-score trust dimension |
| install pain | `CLEAN_MACHINE_RUN.md` friction log |
| keep / remove | `alpha/users/<cohort>/<handle>/status.json` |

V2 supersedes v1 for cohorts opened after Phase 5K; v1 stays
live for testers already mid-week-one with the older form.

### 4. `docs/trust/ALPHA_MATRIX.md`

The install-validation matrix. 5 slots × 7 columns:

- 3 Windows clean VMs (Win 10, Win 11, fresh profile)
- 1 macOS Intel
- 1 macOS Apple Silicon

Columns: install time / doctor / extension / first capture /
first recovery / resume / status. Every cell `unknown` today;
each row's data drops into one cell of one slot when a
maintainer walks the corresponding row of
[`CLEAN_MACHINE_RUN.md`](../../docs/trust/CLEAN_MACHINE_RUN.md) or
[`MAC_OWNER_NEEDED.md`](../../docs/release/MAC_OWNER_NEEDED.md).

### 5. Extension *Connection* drawer (the long-named *repair drawer*)

A new top-of-Settings card on
[`SettingsPanel.tsx`](../../apps/extension/ui/src/components/SettingsPanel.tsx)
with:

- A breathing status dot (same pulse vocabulary as the popup
  header).
- *Daemon listening on 127.0.0.1:4545* line (real data — counts
  + today's count from `health.ingestedTotal` /
  `health.eventsToday`).
- A *Re-probe* button that calls `onRetry` (re-runs the popup's
  `/v1/health` fetch).
- An *Open Recall* button visible only when the daemon is down
  (routes through `openRecall()` — the three-rung ladder from
  Phase 5H, never a dead click).

The drawer reuses data already on the page; no new fetch. The
prop wiring (`connection` + `health` + `onRetry` from `App.tsx`)
adds 3 lines to the existing Settings invocation.

Extension build:
**286.85 kB JS / 91.58 kB gzipped** (+1.81 kB from the drawer).

---

## What is **not** in this phase

The directive's success line is external. What that means in
practice:

| Directive item | Status | Why deferred |
|---|---|---|
| 5 real humans installed | 0 of 5 | distribution channel hasn't opened; this phase builds the receiving infrastructure |
| 3 successful recoveries | 0 of 3 | downstream of the 5 humans |
| Real friction signal | 0 reports | downstream of the 5 humans |
| Real trust signal | 0 cohort-side rows | downstream; the local trust counters are already wired (`recovery_shown`, `recovery_accepted`, `resume_ok`, `resume_fail`, `resurface_opened` — see `app/core/stats.py`) and exportable via `recall stats --export` |
| Control room: alpha-growth / drop-reasons / install-success cards on the Next.js dashboard | deferred | `apps/admin/scripts/bake_data.py` + Next.js component work; meaningful effort against zero cohort data right now. The CLI's `recall alpha report` already serves the same information in a terminal-friendly form |
| Timeline chips on the recovery card | deferred (unchanged from Phase 5I) | `/v1/recovery/recent` doesn't return per-day timeline data; the *No placeholders* rule still applies |
| Launcher paper cuts | none surfaced | the directive said *only paper cuts*; without a visual walkthrough of the running launcher, no rough edge surfaced this phase. Documented as honest *nothing to fix* rather than fabricated polish |
| `correct_silence` trust counter | not added | derivable from existing counters (`digest_shown - recovery_shown` would need a new `digest_shown` counter); skipped this phase to keep engine surface unchanged — calibration data from cohort returns will tell whether the math suffices |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes (engine) | `python -m pyflakes app/ui app/core api` | zero findings |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.core.alpha_cli import run_alpha_cli"` | OK |
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED |
| repair --dry-run | `python recall.py repair --dry-run` | 4 rows + YELLOW summary |
| reinstall-check | `python recall.py reinstall-check` | clean |
| founder status | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged) |
| **alpha help** | `python recall.py alpha` | help text rendered |
| **alpha status (empty)** | `python recall.py alpha status` | *"No testers recorded yet."* (correct — zero entries) |
| **alpha report (empty)** | `python recall.py alpha report` | all counts zero; directive target check skipped (no users) |
| **alpha create rejection paths** | `recall alpha create kunal@email.com --cohort alpha-001` | rejected (handle PII check) |
| **alpha create rejection paths** | `recall alpha create tester-12 --cohort badname` | rejected (unknown cohort) |
| extension build | `cd apps/extension/ui && npm run build` | 286.85 kB JS / 91.58 kB gzipped |
| TS scan | `npx tsc --noEmit` | zero findings |
| control room build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load |

---

## Touched files

```
new code:
  app/core/alpha_cli.py                          (cohort CLI; ~280 LOC)

new directories + templates:
  alpha/users/README.md
  alpha/users/_TEMPLATE/status.json
  alpha/users/alpha-001/TEMPLATE.md
  alpha/users/alpha-002/TEMPLATE.md
  alpha/users/friends/TEMPLATE.md
  alpha/users/builders/TEMPLATE.md
  alpha/users/students/TEMPLATE.md

modified:
  recall.py                                      (fast-path dispatch for `alpha`)
  apps/extension/ui/src/components/SettingsPanel.tsx   (ConnectionDrawer)
  apps/extension/ui/src/App.tsx                  (pass connection/health/onRetry to SettingsPanel)

new docs:
  docs/engineering/PHASE_5K_STATUS.md            (this file)
  alpha/ALPHA_FEEDBACK_V2.md
  docs/trust/ALPHA_MATRIX.md

modified docs:
  docs/founder/PHASE_TRACKER.md
  docs/founder/ROADMAP_LIVE.md
  docs/release/CHANGELOG.md
  docs/DOC_INDEX.md
  docs/engineering/OPEN_PROBLEMS.md
```

---

## The shape of the next phase

The phase that closes the directive's success line is **5L —
Cohort In Hand**. Three external dependencies have to land in
order:

1. **Distribution opens.** The founder hand-shares the
   `alpha/launcher/` pack + `Recall-Setup-lite.exe` to five real
   humans.
2. **The matrix fills.** A Windows-VM maintainer walks 3 rows of
   `ALPHA_MATRIX.md`; a Mac maintainer walks 2.
3. **Returns trickle in.** Testers email back `FEEDBACK_V2.md` +
   `stats.json`. `recall alpha create` opens each row; founder
   hand-edits the `day1/2/3` flags as each tester reports.

Once *any* of those three lands, the `recall alpha status`
output stops being a blank table and starts being the cohort's
honest pulse — which is the *whole point* of building this
infrastructure now and not after the humans are already on the
hook.
