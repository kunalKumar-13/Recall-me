# KNOWN_FAILURES.md — the failure catalogue

Real installs produce real failures. This page is the catalogue:
every distinct failure pattern a tester has reported, what it
looks like, what we believe causes it, and (where known) the fix
or the workaround. Updated as the cohort runs.

The directive's success criterion explicitly names **1 failure
story** as part of the alpha-001 close-out. That isn't a bug in
the criterion: knowing what *doesn't* work is as important to
trust as knowing what does. A product that pretends to never fail
isn't honest enough to leave running all day for years.

Pairs with:

- [`PLAYBOOK.md`](PLAYBOOK.md) — the daily cadence the founder
  uses to *catch* failures.
- [`STATUS.md`](STATUS.md) — the live cohort board where
  `drop_reason` aggregates land.
- [`recall doctor`](../../app/core/doctor.py) — the 10-check
  diagnostics the tester runs when something is wrong.
- [`OPEN_PROBLEMS.md`](../engineering/OPEN_PROBLEMS.md) — the
  engineering backlog. A failure here graduates to a row there
  when it's confirmed across ≥ 2 testers.

---

## Catalogue (now)

The catalogue is **empty** — no tester has yet reported a failure
because the cohort has not yet shipped. Every row that lands here
will have:

| Column | Meaning |
|---|---|
| **Code** | Short kebab-case id (e.g. `extension-not-found-edge`) for cross-references. |
| **First seen** | YYYY-MM-DD the founder first heard about it. |
| **Cohort / tester** | Which cohort + handle reported it (multiple are aggregated; the *first* observer is named). |
| **Symptom** | What the tester saw, in their words (with their OK). |
| **Reproducible?** | Yes / No / Sometimes. |
| **Suspected cause** | Founder's best read. |
| **Fix or workaround** | Where it stands now. |
| **Linked status field** | Which `drop_reason` or `confusion` value the founder used so the panel surfaces it. |

When the first row lands, this section becomes a table; until
then, the empty paragraph above is the truthful state.

---

## The trust contract for this page

A failure entry is the *founder's interpretation* of a tester
report. Two rules:

1. **Quote, don't paraphrase, when possible.** If the tester
   sent a sentence the founder can quote verbatim (with their
   OK), the *Symptom* column carries that exact sentence. If
   not, the founder writes their own one-sentence read and
   marks the row with `(paraphrased)`.
2. **Never inflate.** A single tester saying *"it didn't show me
   anything"* is a single tester's read. Promotion to
   [`OPEN_PROBLEMS.md`](../engineering/OPEN_PROBLEMS.md) waits
   for ≥ 2 distinct testers reporting the same symptom on
   different machines.

---

## How a failure flows

```
Tester sends a report
       |
       v
Founder reads, redacts (no URLs / filenames / queries / chat)
       |
       v
`recall alpha update <h> --drop_reason "<short label>"`
   `recall alpha update <h> --confusion "<one sentence>"`
       |
       v
New row in this catalogue (Code + Symptom + Suspected cause)
       |
       v   (after >= 2 testers report the same symptom)
       |
       v
docs/engineering/OPEN_PROBLEMS.md — engineering ticket
```

`recall founder alpha-health` reads the `drop_reason` aggregation
on every run, so a recurring failure climbs from YELLOW to RED as
the count grows. That is the alarm; this page is the explanation.

---

## What is explicitly *not* a failure here

Cases that look like failures but are not:

- **"Recall didn't show a recovery card today."** Often correct
  behaviour. Log it as a `correct_silence` row in
  `recovery_journal.json`, not as a failure here.
- **"The popup is empty on day 1."** Expected. The user hasn't
  produced events yet. The 6D *demo mode* is the affordance for
  this; record the tester's reaction to the *Show example* /
  *Start normally* choice instead.
- **"Recall used 2 MB of RAM."** Not a failure unless the tester
  has a specific resource concern.

These show up in the cohort as `wow_moment` / `confusion` rows on
the tester's `status.json`, not as catalogue entries here.
