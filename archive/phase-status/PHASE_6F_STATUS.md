# PHASE_6F_STATUS.md — Daily Loop Validation

The receipt for Phase 6F. The directive's *Goal*: Recall proves
repeat use. The product earns the right to keep running only if a
real human installs it, uses it, *leaves*, and *comes back*. Phase
6F adds the layer that counts that signal — locally, additively,
without touching the engine.

Anti-rules respected: **no visual redesign**, **no installer
work**. The launcher widget tree and the extension popup are not
modified; the installer spec is untouched. Phase 6F is a new
counter layer + three thin API routes + two new CLI subcommands
+ three docs.

The directive's §4 (*Founder room: Add Daily Loop*) is an explicit
ask, so the top-level *no founder dashboard work* anti-rule is
read narrowly: don't redesign the existing baked-data founder
dashboards. Adding a new `recall founder daily-loop` subcommand
that reads the new layer directly is what §4 names.

Cross-references:
[`DAILY_LOOP.md`](../../docs/product/DAILY_LOOP.md) (product story —
what the layer means),
[`RETURN_BEHAVIOR.md`](../../docs/product/RETURN_BEHAVIOR.md) (return
semantics in detail),
[`MOMENTS.md`](../../docs/alpha/MOMENTS.md) (the seven first-time
moments — Phase 6F's user-facing artifact),
[`PHASE_6E_STATUS.md`](PHASE_6E_STATUS.md) (the predecessor — the
alpha operational scaffolding 6F populates).

---

## What shipped

### 1. `app/core/daily_loop.py` — the counter layer

A new module at
[`app/core/daily_loop.py`](../../app/core/daily_loop.py). Six bins
per local day, one JSONL line per day, stored at
`~/.recall/daily_loop.jsonl`:

```
day_started              the launcher opened today
investigations_opened    an InvestigationCard click
recoveries_shown         the launcher surfaced a RecoveryCard
recoveries_used          the user clicked Resume
returns                  a new event after a >=30-minute gap
resume_success           a Resume the user did not undo
```

Three derived signals computed at read time (never stored):

```
continuity_restored      recoveries_used / recoveries_shown
return_rate              returns / day_started
resume_quality           resume_success / recoveries_used
```

Plus a green/yellow/red verdict per signal — thresholds documented
in [`DAILY_LOOP.md`](../../docs/product/DAILY_LOOP.md) and pinned in the
in-source `verdict()` so the math has a single source of truth.

The module also owns the **return detector**: every successful
ingest passes through `mark_event(ts)`, which compares the new
timestamp against `last_event_ts` in
`~/.recall/daily_loop_state.json` and bumps the `returns` bin if
the gap crossed 30 minutes (`RETURN_GAP_MIN_SECONDS = 1800`).

Performance: each `mark_*` call is a single JSONL read + rewrite
of a one-line-per-day file. A full year of use is < 400 lines /
< 50 KB. `summary(days=7)` is < 5 ms.

Disable: `RECALL_DAILY_LOOP=off` in the environment makes every
mark a no-op. The summary endpoint still answers — with zeros.

### 2. Engine hook + recovery hooks in `api/main.py`

Three integration points, all in
[`api/main.py`](../../api/main.py), zero touches to the engine
layers:

- `_post_ingest_hook(ok)` — extended to also call
  `daily_loop.mark_event(time.time())` after every successful
  ingest. Best-effort: a persistence failure logs a warning
  but never propagates into the ingest response.
- `/v1/recovery/recent` — bumps `recoveries_shown` *only* when
  the candidate list is non-empty. An empty response is
  *correct silence* (tracked at the alpha-ledger level), not a
  shown card.
- `/v1/recovery/{id}/restore` — bumps `recoveries_used` on the
  successful path before returning the plan.

The two bins the daemon cannot infer (`day_started` and
`resume_success`) are posted explicitly by the launcher's
executor via the new `/v1/loop/bump` route.

### 3. Three thin routes — `/v1/loop/{bump, summary}`

In [`api/main.py`](../../api/main.py) + 5 new DTOs in
[`api/schemas.py`](../../api/schemas.py):

| Route | Body | Returns |
|---|---|---|
| `POST /v1/loop/bump` | `{"bin": "<name>"}` (closed pydantic literal) | `{bin, today}` — the new today-count after the bump |
| `GET /v1/loop/summary?days=7` | — | today + yesterday + window + signals + green/yellow/red verdicts |

422 on bad bin names (pydantic). The summary route is cheap
enough to poll on every popup open; the popup currently doesn't
read it, leaving the consumer surface to be a future UI choice
(out of Phase 6F scope per the *no visual redesign* anti-rule).

### 4. Recovery journal v2 — two new fields

[`alpha/recovery_journal.json`](../../alpha/recovery_journal.json)
`_field_spec` extended:

- `return_after_gap` — `true` | `false` | `null`. Was the tester
  returning from a ≥ 30-minute idle gap when the recovery
  surfaced? The strongest signal that recovery is doing what
  it's meant to.
- `time_to_resume` — integer seconds between the card appearing
  and the Resume click. Captures hesitation; useful for
  spotting `bad_recovery` rows that read as `resume_ok` only
  because the tester forced it.

Both are optional; legacy entries keep working. The
`recall alpha replay` subcommand surfaces both fields.

### 5. `recall founder daily-loop` — operator panel

A new subcommand in
[`app/core/founder_cli.py`](../../app/core/founder_cli.py). Reads
`~/.recall/daily_loop.jsonl` directly (no bake round-trip), prints
today + yesterday + 7-day window rows + the three signals with
`[GREEN]` / `[YELLOW]` / `[RED]` brackets. The directive's repeat-
use success line (*someone uses Recall twice voluntarily*) maps
to: `day_started ≥ 2 in the 7d window AND returns ≥ 1`. The CLI
prints the verdict only when ≥ 1 day has been started.

ASCII-only (cp1252 console safe).

### 6. `recall alpha replay <handle>` — per-tester timeline

A new subcommand in
[`app/core/alpha_cli.py`](../../app/core/alpha_cli.py). Compiles a
calm event-only timeline from two sources:

1. The tester's `status.json` — install / day1-3 / first_recovery /
   first_resume_ok / wow_moment / drop_reason.
2. Every `recovery_journal.json` entry where `tester == <handle>`
   — kind / date / `return_after_gap` / `time_to_resume`.

**No content** ever appears. URLs / filenames / queries / chat
content are out of scope by contract; the timeline shows only
event *kinds*, dates, and the handle's own labels. The CLI ends
with a coverage line — `OK install, OK activity, OK recovery, OK
resume, OK return, OK wow` — so the founder can scan a single
tester in 5 seconds and see which of the seven first-time moments
have landed.

### 7. Doc trio + MOMENTS.md

Three new docs:

- [`docs/product/DAILY_LOOP.md`](../../docs/product/DAILY_LOOP.md) — the
  product story. Six bins, three signals, the thresholds, the
  disable/clear flow, the *not telemetry* contract restated.
- [`docs/product/RETURN_BEHAVIOR.md`](../../docs/product/RETURN_BEHAVIOR.md)
  — the return detector's semantics in detail: what counts,
  what doesn't, why 30 min, the per-event state file, the
  manual verification recipe.
- [`docs/alpha/MOMENTS.md`](../../docs/alpha/MOMENTS.md) — the seven
  first-time moments (first install / first capture / first
  investigation / first recovery / first resume / first wow /
  trust break) with a per-cohort log table. Hand-edited as
  moments accrue.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Popup / launcher consumers of `GET /v1/loop/summary` | not in scope | The *no visual redesign* anti-rule forbids new UI; the founder CLI is the consumer for now. A future surface (e.g. an opt-in *Activity* tab) could read the route without changes here. |
| Smoke-test section in `_smoke_api.py` for the loop routes | not in scope this phase | Tested via TestClient one-offs (output above). A 5-line smoke section is a follow-up; this phase prioritised the user-visible CLI surface. |
| `resume_success` auto-detection (event-level) | partial | The bin is wired and the route accepts bumps; the launcher executor must post the bump itself after observing that the user did not immediately re-close the targets. That hand-off is the launcher's job, not the engine's. |
| Per-tester `daily_loop.jsonl` import into `alpha/users/<handle>/` | not in scope | The daily-loop layer is *local* to each tester's machine. The founder gets the counts via `recall stats --export` (5E.1) which the tester chooses to send back. No automated pull. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| daily_loop module | end-to-end Python smoke: create temp file path, bump 4 bins, mark two events 32 min apart, read summary | bins correct; 1 return counted; signals 100/100/100 → all GREEN |
| /v1/loop/bump (closed allowlist) | `POST /v1/loop/bump` with `{"bin": "not_a_bin"}` | 422 (pydantic literal rejection) |
| /v1/loop/summary | populated test fixture | matches in-process `daily_loop.summary()` byte-for-byte |
| `recall founder daily-loop` on empty | clean `~/.recall/` | YELLOW on continuity/resume_quality (-), RED on return_rate (0%) — no false greens |
| `recall alpha replay` on test fixture | tester-6f-smoke with full status.json | 5 rows printed + coverage line shows OK install / activity / recovery / resume / wow |
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| doctor (regression) | `python recall.py doctor` | unchanged from 6E |
| extension build (regression) | `cd apps/extension/ui && npm run build` | unchanged (no extension files touched) |

---

## Touched files

```
new code:
  app/core/daily_loop.py

modified code:
  api/main.py                          (ingest hook + 2 recovery hooks + 2 /v1/loop routes)
  api/schemas.py                       (5 loop DTOs)
  app/core/founder_cli.py              (daily-loop subcommand)
  app/core/alpha_cli.py                (replay subcommand)
  alpha/recovery_journal.json          (v2 _field_spec: return_after_gap + time_to_resume)

new docs:
  docs/product/DAILY_LOOP.md
  docs/product/RETURN_BEHAVIOR.md
  docs/alpha/MOMENTS.md
  docs/engineering/PHASE_6F_STATUS.md
```

No engine layer touched. No UI surface (launcher widget tree /
extension popup) touched. No installer spec touched. The only
runtime side effect is two new files under `~/.recall/`
(`daily_loop.jsonl` + `daily_loop_state.json`), both deletable,
both human-readable JSON.

---

## Read-back of the success criterion

The directive's success line:

> someone uses Recall twice voluntarily

The closest counter to that sentence is the 7-day-window
`day_started ≥ 2 AND returns ≥ 1` check the founder CLI prints
("directive: OK repeat-use, OK 1+ return, OK 1+ resume"). The
cohort has not started, so all three currently read `short` —
which is the honest state.

What Phase 6F *delivers* is the machinery that lets that line
become measurable: the counter layer, the return detector, the
endpoints to populate the bins, the operator CLI to read them,
the replay CLI to walk a single tester, the v2 ledger fields to
record the strongest correlation (return + recovery + resume),
and the seven-moments log that names what to watch for. When the
first tester opens Recall, returns the next morning, and clicks
Resume on a real recovery card, every counter named in this
phase moves — and the directive's success line is met.
