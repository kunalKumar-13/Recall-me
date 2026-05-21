# FOUNDER_DASHBOARD.md — the five questions

A founder needs five answers. This file is how Recall answers them
**without a single byte of telemetry** — because the product's
promise and the answers cannot both be true if Recall phones home.

The operating dashboard lives in [`apps/admin/`](../../apps/admin/); this
file explains *what it can and cannot know, and why.*

---

## 1. Did users install?

**Knowable — honestly.** GitHub publishes a `download_count` for
every release asset. `apps/admin/pull_release_stats.py` reads it.
Downloads of `Recall-Setup.exe` vs `Recall.dmg` give a true
Windows/macOS split. This needs no telemetry — GitHub already
counts it, the same way it counts stars.

## 2. Did they return?

**Not knowable automatically — by design.** "Returned after an
interruption" is the product's whole point, but measuring it across
machines would require each install to report activity. Recall will
not do that. It is knowable *one of two honest ways*:

- a cohort member voluntarily runs `recall stats` (a local,
  on-device command) and pastes the aggregate into their cohort
  thread;
- the founder asks, in a cohort check-in.

The dashboard records these as **cohort-reported**, never as a
silent metric.

## 3. Did recovery work?

**Cohort-reported only.** "Recovery shown / accepted / resume
success" are exactly the numbers a telemetry product would stream.
Recall's source of truth instead: the cohort member's own
`recall stats` output and their written feedback. Small-n and
honest beats large-n and extracted.

## 4. What broke?

**Reported, not collected.** No crash-reporter uploads stack traces.
Breakage reaches the founder through:

- the **Feedback Inbox** ([`apps/admin/FEEDBACK.md`](../../apps/admin/FEEDBACK.md))
  — pain / bug / confusing-moment entries;
- GitHub issues;
- cohort check-ins.

A user who hits a crash sees a calm recoverable state (STABILITY.md)
and can *choose* to report it. Recall never decides for them.

## 5. Why did they leave?

**Only by asking.** Churn is invisible to a local-first product —
and that is correct. The honest instrument is a short cohort exit
note, logged in the Feedback Inbox under `trust issue` / `confusing
moment`. A dashboard cannot infer a reason a user did not give.

---

## The trade Recall makes

A telemetry product knows more, sooner, about more users. Recall
knows less, slower, about fewer — and every number it knows, it can
name the source of. That is not a limitation to apologise for; it
is the product. A continuity tool that surveils its users to measure
whether they trust it has already lost.

> Founder's 30-second read: open
> [`apps/admin/DASHBOARD.md`](../../apps/admin/DASHBOARD.md).
