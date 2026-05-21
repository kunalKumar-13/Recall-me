# FOUNDER_OPERATIONS.md — the daily loop

Phase 5E.3 made `apps/admin/` operational. This file is the
runbook: what the founder actually *does* every day, the order of
the steps, and how long each one should take. There is one rule —
nothing here touches the network, ever.

Pairs with [`CONTROL_ROOM.md`](CONTROL_ROOM.md) (the UI's data
contract) and [`READINESS_SCORE.md`](READINESS_SCORE.md) (how the
GREEN / YELLOW / RED verdict is computed).

---

## The five-minute morning loop

1. **`recall founder status`** — the five-second view. Readiness
   score, health cards, alpha cohort tally, current phase.
2. **`recall founder release`** — if status was YELLOW/RED, the
   release breakdown shows *which dimension* is dragging.
3. **Skim feedback.** Open
   [`apps/admin/alpha/feedback.json`](../../apps/admin/alpha/feedback.json) —
   if a new entry is `trust`-tagged, drop everything else and read it.
4. **Look at the dashboard.** `cd apps/admin/web && npm run dev` →
   `localhost:3000`. The five-second view in a browser, with
   sparklines.

That is the loop. **Five minutes, every morning, no exceptions.**

## When a cohort export arrives

A cohort member sent you their `recall stats --export` file:

```bash
python apps/admin/import_stats.py <their_file.json> <cohort-id> <user-id>
python apps/admin/merge_stats.py          # → apps/admin/aggregate.json
python apps/admin/scripts/bake_data.py    # → apps/admin/data/*.json
```

(or just: `recall founder bake` does the last step on its own.)

`import_stats.py` rejects anything that is not a counts-only export,
so a malformed file fails loudly before it can corrupt the
aggregate.

## When a feedback message arrives

Edit
[`apps/admin/alpha/feedback.json`](../../apps/admin/alpha/feedback.json)
by hand. One row per item. Tags: `pain`, `bug`, `confusion`,
`trust`, `feature`. Quote the user's words verbatim; the founder's
interpretation goes in `note`.

Re-bake after editing — `recall founder bake` — and the
*Feedback Room* of the dashboard updates.

## When a phase closes

Two edits:

1. **[`docs/founder/PHASE_TRACKER.md`](PHASE_TRACKER.md)** — add the
   row to the *Completed phases* table and advance *Current phase*.
2. **[`apps/admin/timeline_input.json`](../../apps/admin/timeline_input.json)** —
   flip the closing phase from `now` → `done` (100%), and mark the
   next one `now`.

Re-bake. The *Founder Timeline* of the dashboard now shows the
correct state.

## When the release state changes

Edit [`apps/admin/release_state.json`](../../apps/admin/release_state.json):
- `installer` — `ready` / `partial` / `blocked`.
- `signing` — `signed` / `unsigned`.
- `mac` — `supported` / `preview` / `source-only`.
- `screenshots` — `complete` / `partial` / `missing`.
- `go_no_go` — `GO` / `PARTIAL` / `NO-GO`.
- `blocked[]` — strings, one blocker per line.

Re-bake. The *Release Room* + the readiness score update.

## The weekly sweep (Friday)

- **Skim every cohort's feedback row count.** Cohorts with zero new
  rows for two weeks should be marked `lapsed` in
  `alpha/users.json` and `cohorts.json`.
- **Recompute readiness.** `recall founder release` — if a
  dimension flipped GREEN ↔ YELLOW, write the reason in
  `alpha/notes.json` so the next morning loop sees it.
- **Snapshot traction.** Append today's row to
  [`apps/admin/traction_history.json`](../../apps/admin/traction_history.json).
  Once every week is enough; the dashboard's sparklines are
  *trend*, not *real-time*.

## When NOT to touch the admin

- **You are surprised by a number.** That is the dashboard doing
  its job. Read the relevant section's source file first; the
  dashboard never invents.
- **A metric you want isn't there.** Add it deliberately — a new
  row in `release_state.json` *and* a new section header in the
  Next.js page (or, more often, a new derivation inside
  [`bake_data.py`](../../apps/admin/scripts/bake_data.py)). Never
  add a one-off "quick number" to a JSON the dashboard does not
  read.
- **You feel like adding analytics.** Read
  [`../engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)
  again and then don't.

## The contract

Everything above runs on the founder's machine. There is no server
to log in to, no analytics vendor, no SaaS account. The whole
operator surface is `apps/admin/` + the JSON files it reads. If a
future change makes any of these steps require the network, that
change has violated this file.
