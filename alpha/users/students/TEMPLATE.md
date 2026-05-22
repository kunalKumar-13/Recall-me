# students — the multi-day-arc persona cohort

Mirrors [`alpha-001/TEMPLATE.md`](../alpha-001/TEMPLATE.md).
Specialised for the *student* persona from
[`ALPHA_001_RUNBOOK.md`](../../ALPHA_001_RUNBOOK.md): three hours
on one topic + a 4-day gap + a return.

This cohort is the **canonical** recovery shape — the persona
Recall was first designed for. Expected first-recovery date:
Day 5-6, after the gap.

What this cohort verifies:

- **multi-day arc handling** — does Recall surface the topic the
  tester returned to, with the *right* time-gap framing
  (*"reopened after a 4-day gap"*)?
- **the Resume click** — does the click reopen the *original*
  tabs + files from before the pause, not the most recent ones?
- **silence before Day 5** — a recovery card on Day 2 for a
  not-yet-paused topic is *too eager*; expected behaviour is
  silence until the gap.

If a students-cohort tester reports their first recovery on
Day 2-3, that is a *false positive* signal — the engine surfaced
something it should not have. Logged in the Q3 row of
[`alpha_report.md`](../../alpha_report.md) with `wrong: true`.
