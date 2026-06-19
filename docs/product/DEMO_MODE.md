# DEMO_MODE — Recall's demo path

**Audience:** anyone who has Recall installed but
no captured history yet — testers, reviewers,
contributors, the founder showing it off in a
meeting.

**Promise:** one command, a believable lived-in
trace, the "Continue where you left off" surface
populated within seconds, and a clean reset when
you're done.

---

## The one command

```bash
python recall.py demo run
```

That's the whole demo. It seeds
`~/.recall/events-demo/` with a deterministic
30-event trace across 12 sessions — a believable
mix of developer, researcher, and casual browsing
work. Idempotent: running it twice does not
duplicate data.

To boot the launcher against the demo store:

```bash
# PowerShell
$env:RECALL_DEMO_MODE = "1"
python recall.py

# bash / zsh
RECALL_DEMO_MODE=1 python recall.py
```

The launcher's empty state becomes a populated
digest with a recovery card, three investigation
threads, and a today rail — all derived from the
same canonical script every time.

---

## The flow

The demo trace follows the user-facing arc the
directive specified:

1. **Seed WebSocket investigation** — the canonical
   3-thread story (WebSocket retry / proposal
   draft / research deep-dive). Sourced from
   `app/core/demo_seed.py:_SCRIPT`.
2. **Open GitHub** — one of the trace events is a
   real-shape GitHub visit, captured as a
   `browser_visit` with the right domain.
3. **Open ChatGPT** — another event is a
   `chat_session` against chat.openai.com,
   exercising the chat-session capture path.
4. **Leave** — the trace anchors `hours_ago`
   relative to *now*, so events read as "2h ago"
   / "yesterday" / "3 days ago" regardless of when
   you seed.
5. **Resume** — open the launcher; the recovery
   card surfaces the WebSocket thread as the
   "continue" target.
6. **Reset** — `python recall.py demo reset`
   clears `~/.recall/events-demo/` and the seed
   marker. Next `demo run` rebuilds from scratch.

The trace is **deterministic**. Same script, same
events, same order — every run on every machine.

---

## Subcommands

```
recall demo run             seed the demo event log (idempotent)
recall demo run --force     reseed even if marker says we're current
recall demo reset           clear the demo event log + marker
recall demo status          show seed state + day-file row counts
```

All three are read/write to `~/.recall/events-demo/`
only. **Your real `~/.recall/events/` is never
touched.** Boundary enforced by
`app/core/demo_seed.py:DEMO_EVENTS_DIR`.

---

## What the seed contains

| Property         | Value                                           |
|------------------|-------------------------------------------------|
| Total events     | 30                                              |
| Total sessions   | 12                                              |
| Day-files        | 9 (anchored to today and the 10 days prior)     |
| Seed version     | 4E.1                                            |
| Storage          | `~/.recall/events-demo/YYYY-MM-DD.jsonl`        |
| Marker           | `~/.recall/events-demo/.seeded` (JSON metadata) |
| Source script    | `app/core/demo_seed.py:_SCRIPT`                 |

The trace is split across three life-streams:

- **Developer** — WebSocket retry investigation
  spanning GitHub, StackOverflow, ChatGPT, local
  files.
- **Researcher** — a multi-day reading session
  with cross-references.
- **Founder / casual** — proposal draft, calendar
  scans, Notion notes.

Any reasonable search query lands on at least one
of the three streams. The launcher's resurfacing
layer picks the WebSocket stream as the top hero
because it has the most events + the freshest
"interrupted" signal.

---

## Boundary guarantee

The demo path is **fully isolated** from the user's
real history:

| Concern                   | Guarantee                                |
|---------------------------|------------------------------------------|
| Real event log            | Untouched. Demo writes to `events-demo/`. |
| Real Chroma index         | Untouched. Demo does not index files.    |
| Real config               | Untouched. `RECALL_DEMO_MODE` is an env-var, not a config write. |
| Real recovery state       | Untouched. Recovery is derived on demand from whichever event log is active. |
| Network                   | None. The seeder writes JSON to disk only. |

You can run the demo while your real Recall is
running; the two never collide because they read
different directories.

---

## Resetting between sessions

If you want a clean demo (fresh "Continue" card,
no stale dates):

```bash
python recall.py demo reset
python recall.py demo run
```

This is what the screenshot capture harness uses
between runs.

---

## Demo screenshots

The frozen demo capture set lives at
[`assets/screenshots/demo/`](../../assets/screenshots/demo):

| File                          | What it shows                                  |
|-------------------------------|------------------------------------------------|
| `demo-launcher.png`           | The launcher populated by the demo trace      |
| `demo-extension.png`          | The extension popup against the demo state    |
| `demo-extension-empty.png`    | The extension's "no demo seeded yet" state    |
| `demo-transition.png`         | The moment the demo overlay transitions out   |

These are checked into the repo so the landing
page can render the demo state without booting
Recall.

---

## What the demo is NOT

- **Not a tutorial.** No tooltips, no walkthrough,
  no overlay copy. The product looks the same
  with or without the demo — the difference is
  *content*, not chrome.
- **Not random.** Calling `demo run` ten times
  produces the same 30 events in the same order.
- **Not a benchmark.** The script is small (30
  events). Performance budgets are calibrated for
  10K-event stores.
- **Not a feature flag.** `RECALL_DEMO_MODE=1`
  swaps the data directory; nothing else changes
  about how Recall behaves.

---

## Troubleshooting

| Symptom                                  | Fix                                       |
|------------------------------------------|-------------------------------------------|
| `recall demo run` says "already current" | Already seeded. Add `--force` to reseed.  |
| Launcher shows empty state after seed    | Forgot `RECALL_DEMO_MODE=1`. Set it, restart. |
| `recall demo status` shows 0 day-files   | Demo dir was cleared. Re-run `demo run`.  |
| Boot fails with `ModuleNotFoundError`    | Re-run `pip install -r requirements.txt`. |
| Demo trace looks dated                   | `demo reset && demo run` re-anchors to "now". |

---

## Related

- [VERSION.md](../release/VERSION.md) — what RC1 freezes
- [QUICKSTART.md](../release/rc1/QUICKSTART.md) — the
  install → demo → resume walkthrough
- `app/core/demo_seed.py` — the script source
- `app/core/demo_cli.py` — the CLI dispatcher
