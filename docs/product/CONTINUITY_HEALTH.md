# CONTINUITY_HEALTH.md — the shape of a day

Recall does not score productivity. There is no streak, no grade,
no "you should have done more." But a day *does* have a continuity
shape — and seeing it (only on your own machine, computed only from
your own data) is part of trusting the tool.

This file names four day-shapes. They are read off the daily
counters in `~/.recall/counters.json` plus that day's event log;
the engine that produces them is `compute_today()` in
[`app/core/stats.py`](../../app/core/stats.py). They are **never
exported** — Phase 5B's `build_export()` continues to exclude
everything in this file. See [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md).

---

## The four day-shapes

| Shape | What it looks like | What it means |
|---|---|---|
| **Excellent day** | a recovery accepted, the resume succeeded, multiple investigations touched | continuity worked: you were offered the next step and stepped into it |
| **Fragmented day** | many events spread across many topics, no recovery accepted | a busy day, but the work did not crystallise — no single thread the engine could hand back |
| **Interrupted day** | high-momentum activity that stopped mid-flow; abandonment signals present; no resume yet | the kind of day recovery exists to catch *tomorrow* |
| **Recovered day** | a resume succeeded after a multi-day gap | the milestone moment — Recall remembered something you had genuinely set aside |

## Reading them off the numbers

`recall stats --today` prints the daily score. The day-shape is a
heuristic over those numbers, not a hard label:

| Today's numbers | Shape |
|---|---|
| `interrupted_work_recovered ≥ 1` and `continuity_restored_pct ≥ 50%` | **Excellent** |
| `recoveries_accepted ≥ 1`, last event in events log shows a multi-day gap before today on that thread | **Recovered** |
| `recoveries_shown ≥ 1` but `recoveries_accepted == 0`, `events_total` high, many distinct kinds | **Fragmented** |
| many `browser_visit`/`open` events, momentum signals present, no resume today | **Interrupted** |

None of these is good or bad. A **fragmented** day is just a
fragmented day; sometimes that is exactly what you needed.
A **recovered** day is the rarest and the one Recall is built for —
when it happens, it is enough.

## What this is not

- Not a streak. No counter resets you punish, no chain you fear
  breaking. The four shapes are independent — having an excellent
  day after a fragmented one does not "recover" anything.
- Not a grade. No score, no rank, no compared-to-yesterday.
- Not a feed. The shape of today is shown only when you open
  `recall stats --today` — never as a notification, never popping
  up in the launcher.
- **Not exported.** None of the counters or rates in this file ever
  leave your machine. The founder dashboard sees aggregate cohort
  totals (Phase 5E.1), never your day.

## Why bother naming the shapes?

A user who never sees Recall's reasoning will eventually mistrust
its silence. Naming the shapes gives the silence shape too — an
**interrupted** day with no recovery card is not a failure of the
tool; it is the tool waiting until tomorrow to be useful, which is
exactly what recovery is for.

If you want to see today: `recall stats --today`. The numbers come
from your machine and go nowhere else.
