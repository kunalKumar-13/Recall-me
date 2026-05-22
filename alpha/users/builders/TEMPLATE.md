# builders — the multi-project persona cohort

Mirrors [`alpha-001/TEMPLATE.md`](../alpha-001/TEMPLATE.md).
Specialised for the *builder* persona from
[`ALPHA_001_RUNBOOK.md`](../../ALPHA_001_RUNBOOK.md): three
concurrent projects, each with its own folder + tab cluster +
AI chat.

What this cohort stress-tests:

- **micro-context separation** — does Recall correctly thread
  three concurrent projects into three investigations, or does
  it merge them into one mush?
- **the *wrong recovery* failure mode** — a recovery card that
  reopens Project A's tabs while the tester was about to resume
  Project B. One such report drops the *Trust* dimension's score
  to 0.2 per the rule in
  [`READINESS_SCORE.md`](../../../docs/founder/READINESS_SCORE.md).
- **active-investigation count** — a healthy builders tester
  should see 3-5 active investigations by Day 3.

Same per-tester folder schema. The cohort filter only sharpens
the signal interpretation, not the data shape.
