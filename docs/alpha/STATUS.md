# STATUS.md — the live alpha cohort board

The honest answer to *"where is the cohort?"* at any point in
time. This page is **hand-edited**: every cell flips off `unknown`
only when a real tester executed the step on a real machine.
Nothing here is generated; nothing here is telemetry; nothing
here is aggregated from anywhere except the corresponding
`alpha/users/<cohort>/<handle>/status.json` files.

The live computed view lives next door:

```
recall founder alpha-health
```

…which reads the same files and prints the five signals (installs
/ returning / first recoveries / trust % / drop reasons) with
green/yellow/red verdicts. This file is the *narrative*; the CLI
is the dashboard.

Pairs with [`PLAYBOOK.md`](PLAYBOOK.md) (the operations book) and
[`KNOWN_FAILURES.md`](KNOWN_FAILURES.md) (the failure catalogue).

---

## Cohort state — 2026-05-23

| Cohort | Installs | Returning | First recoveries | Drops | Status |
|---|---:|---:|---:|---:|---|
| `alpha-001` | 0 | 0 | 0 | 0 | ⬜ awaiting first install |
| `alpha-002` | 0 | 0 | 0 | 0 | ⬜ queued |
| `friends` | 0 | 0 | 0 | 0 | ⬜ awaiting first install |
| `builders` | 0 | 0 | 0 | 0 | ⬜ awaiting first install |
| `students` | 0 | 0 | 0 | 0 | ⬜ awaiting first install |
| **total** | **0** | **0** | **0** | **0** | **awaiting cohort start** |

Trust % — n/a (no recovery_journal entries yet).

---

## Directive success line — current state

The Phase 6E directive named four numbers as the success line:

| Target | Current | Verdict |
|---|---:|---|
| 5 humans | 0 | ⬜ |
| 3 recoveries | 0 | ⬜ |
| 1 wow | 0 | ⬜ |
| 1 failure story | 0 | ⬜ |

Every row is intentionally zero — the cohort hasn't started.
The numbers above flip green the moment the first tester returns
their first update and the founder records it via
`recall alpha update`.

---

## How to bring this file up to date

Every Monday morning, the founder:

1. Runs `recall alpha export` and pastes the totals into the
   Cohort-state table.
2. Runs `recall founder alpha-health` and copies the per-signal
   GREEN / YELLOW / RED into the directive-success table.
3. Edits the date in the section heading.
4. Commits the change.

No automation. The point of this file is the *interpretation* the
founder is willing to put their name on; a script can never do
that, and Recall's never-cloud rule means the data never leaves
the founder's laptop anyway.

---

## What this file is NOT

- **Not** a chart. The directive's *"no charts explosion"* rule
  applies here too: a table is enough.
- **Not** a public dashboard. This page is editable by anyone who
  has the repo; the cohort itself never reads it.
- **Not** a substitute for the daily morning loop in
  [`PLAYBOOK.md`](PLAYBOOK.md). Status is the *output*; the
  playbook is the *cadence*.
