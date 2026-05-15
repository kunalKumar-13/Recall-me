# Issue triage

This page is for **maintainers**. If you're a user, please
file your issue through the [bug-report
template](ISSUE_TEMPLATE/bug_report.md) or the
[feature-request template](ISSUE_TEMPLATE/feature_request.md);
this document describes how those reach a resolution.

## Triage cadence

- **First touch**: within 72 hours of submission. The first
  response acknowledges the report, applies the right labels,
  and either asks a follow-up or sets expectations.
- **Stale check**: every Friday. Any open issue with no
  activity in 14 days gets a status comment.
- **Closure**: when fixed, the closing PR references the
  issue with `Closes #N`. When wontfix, the closing comment
  cites the [decision-gate rule](../CLAUDE.md#global-engineering-rules)
  that excludes it.

## Labels

The canonical 24-label set lives at
[`ISSUE_LABELS.md`](ISSUE_LABELS.md). Apply at least one from
each axis (`kind/`, `area/`, `priority/`, `status/`) on first
touch.

## Decision tree

When a new issue lands, walk through these in order. The first
one that matches is the right path; don't double-route.

### 1. Is it a *stability bug* per [`STABILITY.md`](../STABILITY.md)?

A stability bug is anything that breaks one of the guarantees
in `STABILITY.md`:

- An exception leaked through to the user
- Determinism broken — same events producing different
  outputs across rebuilds
- The HTTP API returned a 5xx
- The launcher crashed on a user-visible action
- A telemetry call we don't intend
- A network call outside the documented embedding-model
  download

**Action.** Label `kind/bug` + `priority/p0`. Goes to the top
of the next-release milestone. The fix carries a smoke-test
section that proves the regression won't return.

### 2. Is it a *correctness* issue inside the engine?

Wrong recovery candidate. Thread that should have surfaced
didn't. Evolution segmentation looked off. Resurfacing
suggested something accidental.

**Action.** Label `kind/bug` + `area/recovery` (or the
relevant area). Priority depends on the signal-to-noise
ratio: a single false positive on edge data is `p2`; a
systematic mis-segmentation is `p1`.

For these issues, **always ask for the debug overlay output**:
`RECALL_DEBUG=1` for hover overlays, plus
`RECALL_EXPLAIN_RECOVERY=1` for recovery-specific reasoning.
The reporter's overlay text is what makes the bug
reproducible.

### 3. Is it a *performance* concern?

User says the launcher feels slow, recovery takes seconds,
search blocks the UI, etc.

**Action.** Label `kind/perf` + `priority/p1`. Ask for:

- The output of `python _smoke_api.py` from the user's
  machine — the perf-asserting sections (11, 20, 24, 28)
  carry the numbers
- Total event count: `find ~/.recall/events -name '*.jsonl' | xargs wc -l | tail -1`
- Whether `orjson` is installed

Cross-reference against [`CLAUDE.md`](../CLAUDE.md) §
*Performance budgets*. If the user's numbers exceed the
budget, the bug is real; if they're inside the budget, the
perception bug lives in the launcher's loading / feedback
states, not the engine.

### 4. Is it a *documentation* gap?

A user couldn't find something. A doc page is outdated. A
copy fix is needed.

**Action.** Label `kind/docs` + `area/docs`. Priority is
usually `p2` unless the gap is in install or onboarding,
where it's `p1` (it blocks new users).

### 5. Is it a *feature request*?

Walk through the [decision gate](../CLAUDE.md#global-engineering-rules):

- Does this improve continuity?
- Does this improve inevitability?
- Does this preserve calmness?
- Does this preserve trust?
- Does this preserve speed?

**If any answer is no**, the request is declined politely:

> Thanks for the suggestion. We've thought about this and
> can't take it on for now — it conflicts with rule N of
> the engineering charter (link to specific rule). We
> wrote up our position in [`docs/faq.mdx`](../apps/docs/faq.mdx)
> for the questions we get most often; it might explain
> why we're holding the line.

**If all answers are yes**, apply `kind/feature` and read
through the brief [`PHASE_4A_STATUS.md`](../PHASE_4A_STATUS.md)
deferred items — the request might already be queued. If not,
it joins the roadmap.

### 6. Is it a *security* report?

Treat as `priority/p0` regardless of severity. **Do not
discuss publicly** until the reporter has acknowledged the
disclosure window — see [`SECURITY.md`](../SECURITY.md).

### 7. None of the above?

Label `kind/question` and route to the answer or a doc link.
Most of these belong in the FAQ once we've answered the same
question three times.

## What gets immediately declined

These categories are part of the "things we will not build"
list in [`CLAUDE.md`](../CLAUDE.md). They are declined on
first touch with a link to the relevant rule, not held open
for discussion:

- **LLM chat over your files.** Recall is a memory layer,
  not an agentic system. We don't ship a "chat with your
  notes" feature.
- **Cloud sync** of any kind. Cloud-sync as an *opt-in
  premium* is also declined; the local-first guarantee is
  the product.
- **Multi-user / team features.** Recall is single-user
  by construction.
- **Telemetry** (even opt-in, even anonymous). The trust
  contract is that nothing leaves the machine; an
  opt-in telemetry feature breaks the contract for users
  who haven't audited every release.
- **Recommendation feeds.** *"Topics you might like to
  recall"* is the inverse of what the product does.
- **Notifications.** *"You have 3 unfinished threads!"*
  is dopamine mechanics; the digest is the right surface.
- **Dashboards.** Productivity analytics are out of scope.
- **Auth on the loopback API.** The bind is the boundary.

If a request fits one of these, close it with a one-paragraph
explanation and a link to the rule. **Closing politely is part
of the maintainer contract.**

## When to escalate

- A `priority/p0` open more than 24 hours.
- A security report (always — see `SECURITY.md`).
- A user with a verifiable correctness bug we can't
  reproduce.
- A philosophy disagreement that's reached three exchanges —
  escalate to the engineering charter and a maintainer-only
  decision.

## When *not* to engage

- Polemics about whether AI tools should exist. Cite the
  charter, close politely.
- Repeated requests for declined features. Lock the issue
  after the second polite decline; don't engage further.
- Off-topic discussions of competing tools. Useful in
  isolated forums; off-topic for our issue tracker.

## Friction we want to keep

A user who can't tell us how to reproduce their issue is not
a user we can help. The bug-report template asks for the boot
trace, the OS, and the smallest reproduction; **do not
under-ask** for the sake of being friendly. Polite firmness on
the reproduction step earns the user a faster fix.
