# FOUNDER_METRICS.md — what the numbers answer

[`FOUNDER_DASHBOARD.md`](FOUNDER_DASHBOARD.md) is the *philosophy* —
why Recall measures the way it does. This file is the *mechanics*:
which metric, from `recall stats`, answers which founder question.

Every number here originates on a user's machine, in a counts-only
`stats.json` they *chose* to export (Phase 5E.1). Nothing is
streamed; nothing is inferred behind their back.

---

## Do installs survive?

| Question | Metric | Read it as |
|---|---|---|
| Did the install take? | `install_age_days` | > 0 means Recall has run on more than one day |
| Is it accumulating? | `events_total` | climbing over successive exports = a live install |
| Is it being used, not just installed? | `daily_active_days` | distinct days with activity |

A dead install exports `install_age_days` frozen and
`daily_active_days` flat across check-ins.

## Do users return?

| Question | Metric | Read it as |
|---|---|---|
| Sustained, not one-session? | `weekly_active_days` | distinct weeks touched — the honest retention signal |
| Daily habit forming? | `daily_active_days` vs `install_age_days` | ratio near 1 = near-daily use |

Recall cannot see *when* a user returns (no per-event timestamps
leave the machine). It sees *how many distinct days and weeks* they
were active — which is the retention question, answered without
surveillance.

## Do recoveries help?

| Question | Metric | Read it as |
|---|---|---|
| Is recovery surfacing? | `recoveries_shown` | 0 with a live install = recovery is too quiet, or the user has no resumable work |
| Do users act on it? | `recoveries_accepted` / `recoveries_shown` | the accept rate — the core value signal |
| Does Resume actually work? | `resume_success_rate` | low = restoration is failing (moved files, dead tabs) |

`recoveries_accepted` climbing is the single best sign Recall is
doing its job: a user saw an offered investigation and chose to
step back into it.

## Is the extension used?

| Question | Metric | Read it as |
|---|---|---|
| Is the browser feeding Recall? | `extension_connected_days` | distinct days with browser events |
| How much? | `browser_events` | total tabs + searches + chats captured |

`extension_connected_days` near 0 with healthy file activity means
the user installed the desktop app but never paired the extension —
a known friction point (the pairing CTAs of Phase 5A address it).

## Where does friction happen?

The metrics *locate* friction; the Feedback Inbox *explains* it.

| Pattern | Likely friction |
|---|---|
| `install_age_days` > 0, `events_total` tiny | onboarding picked no folders, or capture is off |
| `browser_events` 0, files flowing | extension never paired |
| `recoveries_shown` 0 over weeks | not enough multi-day work, or the gate is too strict |
| `resume_success_rate` low | restoration hitting moved/closed targets |
| `recoveries_shown` high, `recoveries_accepted` 0 | the cards are not believable — a trust problem |

The last row is the one to fear: it is the difference between Recall
being *seen* and being *trusted*. Pair it with the Feedback Inbox
([`apps/admin/FEEDBACK.md`](../../apps/admin/FEEDBACK.md)).

---

## Founder additions — Phase 5B

The four behavioural answers the daily-loop phase asked for. All
**aggregate only**; the per-user version of each lives on the
user's machine via `recall stats --today` and never leaves it.

| Founder metric | Aggregate definition | Question it answers |
|---|---|---|
| **Returning installs** | devices with `weekly_active_days >= 2` | did installs stick beyond the first sitting? |
| **Resume sessions** | sum of `recoveries_accepted` across devices | did the product *run* — were recoveries acted on? |
| **Continuity restored** | average `resume_success_rate` | when accepted, did Resume actually deliver? |
| **Daily reopen %** | average `daily_active_days ÷ install_age_days` | how often, as a share of an install's life, do users come back? |

`merge_stats.py` computes them; `cohort_summary.py` prints them.
Per-device counterparts (`continuity_restored_pct`,
`resume_success_rate_today`) are
[`CONTINUITY_HEALTH.md`](../product/CONTINUITY_HEALTH.md) territory — local
only, by contract ([`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)).

## The honest limit

These metrics answer their questions for the cohort members who
*chose* to export. They say nothing about a user who installed,
churned, and never sent a `stats.json` — and that is correct.
Recall would rather know less, honestly, than infer more by
watching. The whole instrument is in `app/core/stats.py`; the
boundary is in [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md).
