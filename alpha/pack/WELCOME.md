# Welcome to the Recall alpha

You're one of five (or fewer) people running RC1
before anyone else.

This pack is **everything you need**:

| File                                  | When to open it                          |
|---------------------------------------|------------------------------------------|
| [INSTALL.md](INSTALL.md)              | Right now. 10 minutes.                   |
| [DAY0.md](DAY0.md)                    | After install. The first hour.           |
| [DAY1.md](DAY1.md)                    | Tomorrow morning. The real test.         |
| [DAY3.md](DAY3.md)                    | Three days in. Does it stick?            |
| [FEEDBACK.md](FEEDBACK.md)            | Whenever you have a thought.             |
| [UNINSTALL.md](UNINSTALL.md)          | If you stop using it.                    |

---

## What Recall is

> A continuity layer for your own thinking — local,
> on your machine, with no cloud.

It captures what you do across your browser and
files, composes it into "threads," and offers a
**one-click Continue card** when you come back
to interrupted work.

That's it. No AI assistant. No chat-with-your-files.
No dashboard. No notifications.

## What we're asking from you

Five things, in order:

1. **Install** (10 min) — [INSTALL.md](INSTALL.md).
2. **Browse normally** for a day.
3. **Leave** — go to a meeting, sleep, weekend.
4. **Return** and open the launcher (Alt+Space).
5. **Report** — even one sentence in
   [FEEDBACK.md](FEEDBACK.md).

The whole point is to see whether step 4 produces
a moment of *"oh, it knew."*

If it doesn't, that's also data — file it as a
failure in
[`alpha/failures/`](../failures/README.md) or
just email it.

## What we promise

- Your data **never leaves your machine**.
  Recall makes exactly one outbound network call
  in its lifetime: the first-boot embedding-model
  download (~80 MB from Hugging Face). After that,
  every byte stays local.
- No telemetry. No analytics. No "we noticed you
  didn't open Recall today" emails.
- You can `python recall.py reset` and wipe
  everything in two seconds.
- The whole codebase is open at
  [github.com/kunalKumar-13/Recall-me](https://github.com/kunalKumar-13/Recall-me).

## What we don't promise

- That every recovery card will be right.
  Phase 8C marked recovery quality as the
  pillar with the largest verification debt.
- That it works on every browser yet. We've
  verified Chrome. Edge / Brave / Arc are
  inferred — if you use one of those, you're
  doing the verification for us.
- That the macOS preview is signed. It isn't.
  Gatekeeper will warn.

## How to ask for help

| Channel        | When to use                              |
|----------------|------------------------------------------|
| GitHub issue   | Reproducible bug, install failure        |
| `FEEDBACK.md`  | Thoughts, confusion, wow moments         |
| Email founder  | Sensitive feedback or NDA-adjacent       |

## A note on scope

Recall does **one thing**: tell you what you were
mentally working on, and offer you a clean way
back. It does not search your files
semantically. It does not summarise your day. It
does not write your code.

If you find yourself wishing it did one of those
things — that's worth writing down in
[FEEDBACK.md](FEEDBACK.md). But don't expect us
to add it. The
[`CLAUDE.md`](../../CLAUDE.md) "Things we will
not build" list is short and load-bearing.

## What "alpha" means here

- **Five users.** Not 50. Not 500. Cohort small
  enough to read every word of feedback.
- **Three weeks.** That's the window. After that
  we decide: stable tag, second alpha cohort, or
  pivot.
- **One success metric:** did any of you get a
  *"continue this"* moment that was actually
  what you wanted to continue?

That's the whole bar. Everything else is
infrastructure.

---

Open [INSTALL.md](INSTALL.md). See you on the
other side.
