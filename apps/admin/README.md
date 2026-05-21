# apps/admin — the operator dashboard

An internal founder dashboard for Recall. It answers *who installed,
who stayed, what broke, what recovered* — **without telemetry,
without a server, without a single byte leaving a user's machine.**

If you are looking for the dashboard itself, open
[`DASHBOARD.md`](DASHBOARD.md).

## The hard rule

Recall's charter ([`CLAUDE.md`](../../CLAUDE.md) § *Things we will
not build*) declines analytics, telemetry, error reporting, and
usage pings — including aggregate or "anonymous" ones. This
dashboard does not bend that rule. It has **no collection
mechanism**: nothing here listens, nothing here is uploaded to, no
Recall install reports to anything.

Instead it composes three honest sources:

| Source | What it gives | Why it's allowed |
|---|---|---|
| **GitHub release API** | download counts, per platform | a public property of the *release*, not of any user — GitHub already counts it |
| **Cohort check-ins** | usage counts, funnel steps | a cohort member *voluntarily* runs `recall stats` locally and pastes the aggregate; the founder logs it |
| **Feedback Inbox** | bugs, pain, trust issues | a person *sent* it; the founder typed it in |

That is the entire data model. There is no fourth source, and there
will not be one.

## Files

| File | Role |
|---|---|
| `DASHBOARD.md` | the founder's 30-second view — six sections |
| `pull_release_stats.py` | fetches GitHub download counts → `release_stats.json` (`[auto]`) |
| `release_stats.json` | generated; the only auto-updated data |
| `cohorts.json` | the public-alpha cohort registry + voluntary check-ins |
| `FEEDBACK.md` | the hand-logged feedback inbox |

## Using it

```bash
# refresh the one automatic section (Release Monitor)
python apps/admin/pull_release_stats.py
```

Then open `DASHBOARD.md`. To fold in a cohort check-in: a member
runs `recall stats` (a local, on-device command — counts only, no
content), shares the output, and you append it to that cohort's
`checkins` array in `cohorts.json`. To log feedback: add an entry
to `FEEDBACK.md`.

## What this is not

- Not a web service. It is markdown + one read-only script.
- Not analytics. The metrics that *would* need telemetry — daily
  active devices, recovery-accepted rate, crash counts — show as
  `[cohort]` or `[—]` in the dashboard, never silently estimated.
- Not a growth tool. It is a *talk-to-your-users* tool with a
  scoreboard attached.

The companion docs are [`FOUNDER_DASHBOARD.md`](../../docs/founder/FOUNDER_DASHBOARD.md)
(the five questions and why some have no automatic answer),
[`PHASE_TRACKER.md`](../../docs/founder/PHASE_TRACKER.md), and
[`ROADMAP_LIVE.md`](../../docs/founder/ROADMAP_LIVE.md).
