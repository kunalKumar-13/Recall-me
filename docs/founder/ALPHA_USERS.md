# ALPHA_USERS.md — public alpha board

The public-alpha roster. **Manual only** — there is no enrolment
server, no auto-sync, no analytics back-end. A row exists here
because the founder added it after talking to a person.

`user_id` is a founder-assigned handle (e.g. `a1-03`), never an
email, never a device id. A user can ask to be removed at any time;
removal is deleting the row.

Pairs with [`apps/admin/cohorts.json`](../../apps/admin/cohorts.json)
(the cohort registry) and the counts-only rollup from
`recall stats` exports.

---

## Board

| user_id | cohort | install date | days active | first recovery | feedback | status |
|---|---|---|---|---|---|---|
| _example_ | alpha-001 | 2026-06-01 | 4 | yes (day 3) | "didn't expect it to remember the SO tab" | active |

_No real users yet — alpha-001 opens once [`GO_NO_GO.md`](../release/GO_NO_GO.md)
clears. The example row shows the format; delete it when the first
real user lands._

## Column meanings

| Column | Source | Notes |
|---|---|---|
| `user_id` | founder-assigned | a handle, never PII |
| `cohort` | `cohorts.json` id | alpha-001, builders, … |
| `install date` | the user tells you | day granularity |
| `days active` | their `recall stats` → `daily_active_days` | voluntary export |
| `first recovery` | the user tells you, or their stats | the milestone moment |
| `feedback` | Feedback Inbox cross-ref | one-line gist |
| `status` | founder judgement | `invited` / `active` / `lapsed` / `removed` |

## Status lifecycle

```
invited  →  active  →  lapsed
                  ↘   removed   (user asked to leave)
```

- **invited** — sent an installer link; not confirmed running.
- **active** — installed, using it, exporting check-ins.
- **lapsed** — went quiet. Ask once (a cohort check-in), do not
  chase. Churn is allowed to be invisible.
- **removed** — the user asked out. Delete their row and any
  `apps/admin/imported/<cohort>/<user_id>.json`.

## Why a markdown table, not a database

A board the founder *maintains by hand* cannot silently grow into
surveillance. Every row got here because a human typed it. That is
the point — see [`FOUNDER_DASHBOARD.md`](FOUNDER_DASHBOARD.md).
