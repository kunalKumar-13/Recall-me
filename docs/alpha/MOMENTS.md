# MOMENTS.md — the seven first-time moments

The cohort lives or dies on whether seven specific moments
happen for each tester. Phase 6F names them. Each one is a
single row a founder records (date + handle + one-line note);
the cumulative list is the answer to *"does the recovery loop
actually work for real people?"*

This file is the per-cohort log. The headers below carry the
verbatim names from the directive; the table below them is
hand-edited as moments accrue.

Pairs with:

- [`PLAYBOOK.md`](PLAYBOOK.md) — the daily operations cadence.
- [`STATUS.md`](STATUS.md) — the live cohort board.
- [`KNOWN_FAILURES.md`](KNOWN_FAILURES.md) — the failure
  catalogue.
- `recall alpha replay <handle>` — emits a per-tester timeline
  that includes most of these moments automatically.

---

## The seven moments

| # | Moment | What it means | Status field |
|---|---|---|---|
| 1 | **First install** | Tester ran the installer to completion on a real machine. | `install_date` set + `install_ok="yes"` |
| 2 | **First capture** | First event landed in `~/.recall/events/` after install. Means the extension is talking to the daemon. | `extension` set + `day1="yes"` |
| 3 | **First investigation** | Tester opened an InvestigationCard in the launcher. Means the threads layer produced something the tester recognised as their own work. | `investigations_opened` bin in `daily_loop.jsonl` ≥ 1 |
| 4 | **First recovery** | Launcher surfaced a RecoveryCard. Means the recovery engine fired on this tester's real data. | `first_recovery` set (YYYY-MM-DD) |
| 5 | **First resume** | Tester clicked Resume on a recovery card, AND the reopened work matched what they actually wanted. | `first_resume_ok="yes"` + a `resume_ok` row in `recovery_journal.json` |
| 6 | **First wow** | Tester volunteered a sentence about a moment when the product surprised them positively (with their explicit OK to quote). | `wow_moment` set |
| 7 | **Trust break** | Tester reported a moment when they stopped trusting the product (bad recovery, missed obvious thing, surprise capture). This is the *failure story* the directive names — knowing where trust breaks is as load-bearing as knowing where it forms. | `drop_reason` set OR a `bad_recovery` row in `recovery_journal.json` |

The seven are deliberately ordered: 1-5 are the *positive arc*
that proves the product works at all; 6 is the moment the user
*chooses* to stay; 7 is the moment they could leave. A cohort
that produces 1-6 but never 7 is hiding something — every product
breaks trust eventually, and the founder must capture how when it
does.

---

## The log — alpha-001

The log is **empty** — the cohort has not started yet. Each entry
below will be one row, dated, with the founder's one-line note (no
URLs / filenames / queries / chat content). When the first
moment lands, the table replaces the placeholder paragraph below.

```
| Date       | Moment            | Tester        | One-line note |
|------------|-------------------|---------------|---------------|
| 2026-MM-DD | first install     | tester-NN     | ...           |
```

(Add rows as moments accrue.)

---

## The log — friends

Empty. Same shape; one table per cohort once the first moment
lands.

---

## The log — builders

Empty.

---

## The log — students

Empty.

---

## How a moment is recorded

Three steps, ≤ 2 minutes per tester per moment:

1. **Read** the tester's report (email / DM / chat). Pick the
   moment(s) the report names.
2. **Update** the matching `status.json` field via
   `recall alpha update`. For example:
   ```
   recall alpha update tester-12 --first_recovery 2026-05-25
   recall alpha update tester-12 --first_resume_ok yes
   ```
3. **Add** the row to this file under the right cohort header,
   with the date + handle + a one-line note (redacted).

The moments map onto the daily-loop bins for the ones the daemon
can detect automatically (capture / investigation / recovery /
resume). The two moments only humans can name — *wow* and *trust
break* — stay manual.

---

## What this file is NOT

- **Not** a numeric dashboard. The per-cohort tables are the
  *story*, not the metric. The metric lives in `recall founder
  daily-loop` and `recall alpha export`.
- **Not** a marketing artifact. Every quote is in the tester's
  own words with their explicit OK to share. If the tester is
  uncomfortable being quoted, the row gets a `(paraphrased)`
  flag.
- **Not** the failure catalogue. The *trust-break* row points to
  [`KNOWN_FAILURES.md`](KNOWN_FAILURES.md) for the full
  per-failure story; this file just names that it happened.
