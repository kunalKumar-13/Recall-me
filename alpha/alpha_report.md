# alpha_report.md — alpha-001 evidence ledger

The single founder-side record of *what alpha-001 actually
showed*. One section per question; each section quotes the data
and the source, never a feeling.

Pairs with [`apps/admin/alpha/users.json`](../apps/admin/alpha/users.json)
(the roster), [`apps/admin/alpha/feedback.json`](../apps/admin/alpha/feedback.json)
(the inbox), and [`apps/admin/alpha/notes.json`](../apps/admin/alpha/notes.json)
(the founder notes). When this file disagrees with those, **those**
are the source of truth — this is the read.

---

## Status: **awaiting cohort data**

As of Phase 5H close (2026-05-21), **zero alpha-001 humans have
installed Recall.** The packet at [`alpha/`](README.md) exists.
The five-file no-terminal install pack at
[`alpha/launcher/`](launcher) exists. The five-persona runbook
at [`ALPHA_001_RUNBOOK.md`](ALPHA_001_RUNBOOK.md) exists. The
distribution channel (a hand-share to five testers) has not yet
opened.

This file is the framework that will be filled in as the cohort
moves through Day 0 → Day 7. Below: the five questions and how
each is answered.

---

## Q1. Did they install?

**Source of truth:** [`apps/admin/alpha/users.json`](../apps/admin/alpha/users.json)
— count of rows with `status: "active"` and a populated
`install_date`. **Today:** 0 of 0 invited.

When data arrives, fill:

| Tester | Cohort | Invited | Installed | Days to install | Notes |
|---|---|---|---|---|---|
| (handle) | alpha-001 | YYYY-MM-DD | YYYY-MM-DD | N | one line of context |

What counts as "installed" — `users.json.install_date` is
populated. Verified by the tester running `recall stats --export`
and the founder's import succeeding.

What counts as a failed install — invited ≥ 7 days, `install_date`
still null. The right action is a one-message check-in, not chasing.

---

## Q2. Did they return?

**Source of truth:** the `days_active` field in
[`users.json`](../apps/admin/alpha/users.json), set from the
voluntary `recall stats --export` files the tester chooses to
share. **Today:** 0 of 0 active.

When data arrives:

| Tester | Days active in week 1 | Daily reopen on day 3+ | Returned to launcher unprompted |
|---|---|---|---|
| (handle) | N / 7 | Yes / No | Yes / No / unknown |

The *return* signal is the strongest one in the cohort. A
continuity tool that the user does not reopen on day 2 has lost.
A continuity tool the user reopens on day 4 without being
reminded has won — even if no recovery card showed up.

---

## Q3. Did recovery help?

**Source of truth:** the `first_recovery` field in `users.json`
and the *trust* / *pain* feedback rows in
[`apps/admin/alpha/feedback.json`](../apps/admin/alpha/feedback.json).
**Today:** 0 first recoveries reported.

When data arrives:

| Tester | First recovery date | Was the work right? | Did Resume reopen the work? | Quote |
|---|---|---|---|---|
| (handle) | YYYY-MM-DD | Right / Wrong / Mostly | Yes / Partially / No | one sentence from FEEDBACK.md |

A *correct* first recovery is the product. Phase 4G's calibration
work was to keep the *correct silence* rate above the
*right recovery* rate above the *wrong recovery* rate. The
alpha-001 cohort is the first time those rates are measured
against real activity, not fixtures.

A single wrong recovery in week one — *if* the tester names it as
wrong — is a hard signal to recalibrate (per
[`READINESS_SCORE`](../docs/founder/READINESS_SCORE.md)'s rule
that a red `bad_recoveries` caps the trust dimension at 0.2).

---

## Q4. Did trust hold?

**Source of truth:** the *trust*-tagged rows in `feedback.json`,
plus the *what should not happen* list in
[`alpha/TRUST.md`](TRUST.md). **Today:** 0 trust-tagged rows.

Three sub-questions, each a row:

| Sub-question | Source | Today |
|---|---|---|
| Did anyone see a network call to anywhere other than `127.0.0.1:4545`? | trust-tagged feedback | none reported |
| Did `recall stats --export` ever produce content other than counts? | the export-side gate in `app/core/stats.py` | engine guarantee; not yet verified by cohort |
| Did anyone see "AI memory" / "smart memory" / a productivity score in the UI? | trust-tagged feedback | none reported |

A *yes* to any of those is a Trust Ledger violation, not a
preference issue. The right action is *fix and re-cut the
release*, not *iterate*.

---

## Q5. Where is the friction?

**Source of truth:** the *confusion* + *pain* rows in
`feedback.json`, plus the *Friction log* in
[`CLEAN_MACHINE_RUN.md`](../docs/trust/CLEAN_MACHINE_RUN.md).
**Today:** five friction items from the build-machine run (Phase
5G); zero from real testers.

Phase 5G's build-machine friction list is the *expected* baseline.
Anything new from the cohort is the *real* signal.

| Friction | Source | Status |
|---|---|---|
| Em-dash mangling in `recall doctor` strings (cp1252) | build-machine run | **fixed Phase 5H** |
| Doctor `versions` check finds no manifest from inside the frozen bundle | build-machine run | **fixed Phase 5H** |
| Silent install skips the autostart task without `/TASKS=` | build-machine run | documented in `INSTALL_METRICS.md` + `alpha/launcher/install.ps1` uses `/TASKS=...` |
| Stale instance lock after a forced kill reads GREEN | build-machine run | **fixed Phase 5H** |
| `recall://` deep-link not registered | build-machine run | **fixed Phase 5H** (verify on rebuild) |
| Popup stayed EMPTY despite captured events | build-machine run | **fixed Phase 5H** (state-machine invariant) |
| Hardcoded "WebSocket retry debugging" demo card | build-machine run | **fixed Phase 5H** (replaced with live event feed) |
| Open Recall was a dead click | build-machine run | **fixed Phase 5H** (`openRecall()` + visible-feedback button) |
| No transition state between EMPTY and populated | build-machine run | **fixed Phase 5H** (new `CapturingState`) |
| No glanceable capture verification | build-machine run | **fixed Phase 5H** (`DebugStrip` bottom counters) |
| Empty state dominated the popup | build-machine run | **fixed Phase 5H** (compact EMPTY surface) |

When cohort entries arrive, append per-tester rows with a
*reproducibility* note (one tester / N testers).

---

## How this file fills

The bake (`recall founder bake`) does **not** write this file —
that would couple a founder-narrative ledger to data refreshes.
This file is **hand-edited** by the founder, once per cohort
import, with the entries above pulled from the JSON sources.

The cadence:

1. **Day 7 of week one** for any tester — the
   [`FEEDBACK.md`](FEEDBACK.md) returns; the
   [`stats.json`](TRUST.md) arrives.
2. **Import**: `python apps/admin/import_stats.py <stats.json>
   <cohort> <handle>` (the trust-ledger gate).
3. **Merge**: `python apps/admin/merge_stats.py`.
4. **Bake**: `recall founder bake`.
5. **Hand-edit this file**: copy the tester's quote into Q3 / Q4
   / Q5 as applicable; tick the boxes in Q1 / Q2 from the
   merged aggregate.

A cohort closes when this file has at least three filled rows in
each section. Three is the floor below which the answers are
anecdote, not evidence.

---

## What "alpha-001 successful" looks like

The narrative the founder dashboard should be able to render at
cohort close:

> Five alpha-001 testers were invited. Four installed within
> three days. Three returned to Recall on day 2 unprompted; two
> returned on day 4. Two reported a *correct* first recovery
> within the first week; one reported the recovery was *for the
> wrong topic*; one had no recovery to evaluate; one did not
> return after day 2. Trust held — no contract-violation rows
> in feedback. Friction surfaced in three places: the SmartScreen
> warning, the empty Day 1 launcher, and the extension
> pairing UX on Edge.

That paragraph is the goal of this file. Until it can be written
truthfully, this is the **awaiting cohort data** version.
