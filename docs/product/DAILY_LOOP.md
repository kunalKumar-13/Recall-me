# DAILY_LOOP.md — what *repeat use* looks like

A continuity layer earns the right to exist only if real people
return to it. Phase 6F adds the layer that names that signal —
**counts only**, local-only, six bins per day, three derived
signals. This file is the product-side story (what the layer
*means*). The engineering receipt is
[`PHASE_6F_STATUS.md`](../../archive/phase-status/PHASE_6F_STATUS.md); the
return semantics get their own page at
[`RETURN_BEHAVIOR.md`](RETURN_BEHAVIOR.md).

---

## The contract

> Recall counts its own surfaces — never the user's content.

Six bins, written to `~/.recall/daily_loop.jsonl` (one JSON line
per local day):

| Bin | Bumped when |
|---|---|
| `day_started` | The launcher opened (or the popup made a `/v1/health` call) for the first time today. |
| `investigations_opened` | The user clicked an InvestigationCard. |
| `recoveries_shown` | The launcher surfaced a RecoveryCard. |
| `recoveries_used` | The user clicked Resume on one. |
| `returns` | A new event landed after a ≥ 30-minute idle gap. |
| `resume_success` | A Resume the user did not immediately undo. |

Nothing else lands here. No URLs. No filenames. No queries. No
chat content. No titles. No per-event timestamps. Inspecting
`~/.recall/daily_loop.jsonl` with `cat` is the privacy contract
made tangible.

---

## The three signals

Computed at read time, never stored — so deleting the JSONL file
returns the user to a true zero.

| Signal | Formula | What it tells you |
|---|---|---|
| **continuity restored** | `recoveries_used / recoveries_shown` | Of the cards the launcher offered, what share did the user accept? |
| **return rate** | `returns / day_started` | Of the days the user opened Recall, what share included a return-after-gap? |
| **resume quality** | `resume_success / recoveries_used` | Of the Resume clicks, what share actually opened the right work? |

A 7-day window is the default aggregation. A *day* with zero
events is folded in as zero so a quiet week reads as "no data,"
not "broken."

---

## Green / yellow / red thresholds

Single source of truth — match the in-source `verdict()` in
[`app/core/daily_loop.py`](../../app/core/daily_loop.py).

| Signal | GREEN | YELLOW | RED |
|---|---|---|---|
| continuity restored | ≥ 60 % | ≥ 25 % | < 25 % |
| return rate | ≥ 30 % | ≥ 10 % | < 10 % |
| resume quality | ≥ 80 % | ≥ 50 % | < 50 % |

Empty signal (denominator = 0) prints as YELLOW with `-`. Never
as RED — silence is silence, not failure.

---

## The endpoints

`/v1/loop/*` — three thin routes. The launcher and the extension
populate the bins; the founder dashboard reads them back.

- `POST /v1/loop/bump` with body `{"bin": "<name>"}` — bumps one
  of the six bins. Closed allowlist; pydantic rejects anything
  else with a 422.
- `GET /v1/loop/summary?days=7` — returns today / yesterday /
  the 7-day window plus the three signals and their
  green/yellow/red verdicts.

The auto-counters do the heavy lifting:

- `/v1/events/*` (every ingest route) → `mark_event(ts)` →
  bumps `returns` if the gap crossed 30 min.
- `/v1/recovery/recent` → bumps `recoveries_shown` *only* when
  the response is non-empty (empty response = correct silence,
  tracked at the alpha-ledger level, not here).
- `/v1/recovery/{id}/restore` → bumps `recoveries_used`.

The two bins the daemon **cannot** know — `day_started` and
`resume_success` — are POSTed explicitly by the launcher.
`day_started` fires on launcher open. `resume_success` fires when
the launcher's executor opens the targets without the user
immediately re-closing them.

---

## Disable + clear

- **Disable**: set `RECALL_DAILY_LOOP=off` in the environment. Every
  `mark_*` becomes a no-op. The summary endpoint still returns —
  with zeros.
- **Clear**: delete `~/.recall/daily_loop.jsonl` and
  `~/.recall/daily_loop_state.json`. Counts start fresh. No engine
  layer reads them, so nothing else breaks.

---

## Performance budget

- One `mark_*` call → one `json.loads` on a per-day record + one
  rewrite. The file is one line per *local day*, so even a
  year of use is < 400 lines (< 50 KB).
- `summary(days=7)` → seven dict lookups + three percentage
  computations. **< 5 ms** on the smallest machines.
- The summary endpoint is therefore cheap enough to poll on
  every popup open if a future surface wants the live signal.

---

## What this layer is NOT

- **Not** telemetry. Nothing leaves the machine. The CLI dump is
  the *only* path data ever crosses an interface, and it crosses
  only into another local process.
- **Not** an engine layer in the sacred-hierarchy sense. The
  daily loop does not feed sessions / contexts / threads /
  recovery. It is *purely additive*: deleting `daily_loop.py`
  removes the counters without breaking anything downstream.
- **Not** a user dashboard. There is no UI for the user that
  shows these numbers. The signals are for the founder during
  alpha and for the maintainer afterwards.

---

## Related

- [`RETURN_BEHAVIOR.md`](RETURN_BEHAVIOR.md) — the return
  detector's semantics, in detail.
- [`docs/alpha/PLAYBOOK.md`](../alpha/PLAYBOOK.md) — how the
  daily-loop bins map onto the cohort operations cadence.
- [`PHASE_6F_STATUS.md`](../../archive/phase-status/PHASE_6F_STATUS.md) — the
  engineering receipt for this phase.
- `recall founder daily-loop` — the operator CLI that prints
  this layer in human form.
- `GET /v1/loop/summary` — the same data over HTTP.
