# ALPHA_001_RUNBOOK.md — five testers, four days, one honest week

The script the founder runs for the alpha-001 cohort. Five
personas, each with their own day-shape; the same packet, but
calibrated expectations.

This file is **for the founder**, not the testers. The testers
get [`alpha/README.md`](README.md) and the
[`alpha/launcher/`](launcher) pack. This runbook tells the
founder what each persona is likely to do, what to expect them
to report, and which of those reports is *signal* vs. *noise*.

Pairs with [`alpha_report.md`](alpha_report.md) (the evidence
ledger) and [`apps/admin/alpha/users.json`](../apps/admin/alpha/users.json)
(the cohort roster).

---

## The five personas

Five distinct day-shapes. Each persona is *one* tester, not a
type. The roster goal: pick five real humans whose week looks
like one of the rows below. Recruit asymmetrically — different
personas make different bugs visible.

| Persona | Day-shape | Why they matter |
|---|---|---|
| **founder** | many short context-switches across files + 30+ tabs across 6 hours; AI chats every few hours | the stress-test of recovery's *correct silence* rule — a high event volume with many half-finished arcs |
| **student** | three hours of one topic + a 4-day gap + a return | the canonical recovery shape (multi-day arc); the persona Recall was first designed for |
| **researcher** | one investigation kept open for two weeks, slowly accumulating; little switching | tests *active investigations* + threading; will be the slowest persona to see a recovery card |
| **builder** | three concurrent projects, each with its own folder + tab cluster + AI chat | tests micro-context separation; failure mode is *one wrong recovery merging two projects* |
| **non-productivity user** | reading, watching, hobby browsing; no "work" | the calibration test: should Recall stay silent here, or does it false-positive *"unfinished hobby"*? |

The same packet goes to all five. The runbook below names the
**expected differences** in what each tester sees.

---

## Day 0 — install

All five testers receive the same hand-off:

```
1. A folder with: Recall-Setup.exe + alpha/ packet.
2. One sentence ("Right-click install.ps1, click Run with PowerShell.").
3. A reminder that nothing leaves their machine.
```

The expected event sequence:

| Step | Expected | Friction to watch for |
|---|---|---|
| Right-click install.ps1 | PowerShell prompt about execution policy | first-time PS users will pause here |
| install.ps1 runs | ~60 s install, exit 0, "Recall installed" line | any RED line is a real fail |
| Open desktop shortcut | first-launch onboarding screen | "what do I pick for folders?" — see *student* below |
| Press Ctrl + Space | empty launcher | "is it broken?" → see *non-productivity user* below |
| Browser extension load (optional) | popup says *Recall is watching locally* | if popup says *Recall isn't running*, doctor → daemon |

### Per-persona Day 0 friction

- **founder**: will probably skip onboarding, pick folders by
  habit. Watch for: "I selected a folder and indexing took
  forever" — heavy folder is a 10+ min index on first run.
- **student**: will read every word of onboarding. Watch for:
  *"what does 'browser memory' mean?"* — copy clarity check.
- **researcher**: will ask *"can I add a folder later?"*. The
  answer is yes; the question is signal that Settings discovery
  needs work.
- **builder**: will pick 3-5 folders. Watch for: indexer hit
  ratio across folders (some too noisy, some too narrow).
- **non-productivity user**: will pick Desktop + Documents (the
  defaults) and quit. Watch for: confusion about what Recall is
  *for*. The honest answer is *"if you're not sure, Recall may
  not be for you"* — that is a successful Day 0, not a failed one.

---

## Day 1 — quiet capture

Nothing is supposed to *happen* on Day 1. That is the persona-test:

| Persona | Day 1 expected | Tell-tale |
|---|---|---|
| founder | popup shows CAPTURING, 50-200 events | tab + search activity dense |
| student | popup shows CAPTURING, 5-20 events | one topic, slow accretion |
| researcher | popup shows CAPTURING, 3-10 events | almost too quiet to notice |
| builder | popup shows CAPTURING, 80-300 events | three folders all firing |
| non-productivity user | popup shows CAPTURING, 30-80 events | YouTube + news + reddit dominate |

Every persona should see the popup *not* show EMPTY (the
invariant from `FRICTION_FIXES.md`). If a tester reports the
popup is still EMPTY after Day 1, that is a bug, not feedback.

### Founder action on Day 1

None. Resist the urge to check in. If a tester asks a question,
answer it once and stop. The week's signal needs unsupervised
real use.

---

## Day 2-3 — the first useful launcher

This is when the launcher's idle digest becomes interesting. The
**expected** state per persona:

| Persona | Expected digest | If different |
|---|---|---|
| founder | 1-2 recovery cards · 3-4 active investigations · resurface row | *no recovery card* = the persona has not yet abandoned work for 12+ hours; not a bug. |
| student | 0 recovery (gap not yet) · 1-2 active investigations | *recovery shown* = false-positive on a within-day pause |
| researcher | 0 recovery · 1 investigation (slowly fattening) | *the investigation title is wrong* = thread merging failure — investigate. |
| builder | 0-1 recovery (per project) · 3 investigations | *one recovery for the wrong project's work* = trust killer; calibrate. |
| non-productivity user | 0 recovery · 0 investigations · resurface only | *anything in Continue* = false-positive. Major signal. |

The single most important question to ask each tester at Day 3:

> *"When you opened the launcher, did the first thing you saw
> match what you were actually doing yesterday?"*

A *yes* is the win Phase 5G's `RECOVERY_STRESS.md` was set up to
verify. A *no* is the calibration data
[`alpha_report.md`](alpha_report.md) Q3 is built for.

---

## Day 3+ — the resume click

The product moment: the user opens the launcher, sees a recovery
card, clicks Resume, **and their work is back**.

Expected:

- Recall reopens the listed URLs (browser tabs).
- For file targets, the desktop launches the system handler
  (the path is in the card; the user double-clicks it).
- The recovery card disappears after a click (Phase 4G:
  *accept → consume*).

Per persona:

| Persona | Likely first-resume moment | Signal |
|---|---|---|
| founder | Day 3-4, *"oh, the WebSocket thing I dropped on Tuesday"* | works → Phase 5H trust gate clears |
| student | Day 5-6, after the 4-day gap their persona has | works → multi-day arc validated |
| researcher | Day 7+ (slow accretion) | likely no resume in week 1; valid |
| builder | Day 2 (frequent switching = lots of half-work) | works → micro-context separation works |
| non-productivity user | never | no signal; absence is correct |

The **wrong** outcome to listen for hardest: a Resume click that
reopens *the wrong work*. One occurrence per tester is the
[`READINESS_SCORE.md`](../docs/founder/READINESS_SCORE.md) rule
that caps Trust at 0.2 — a single red `bad_recoveries` flag.

---

## Day 7 — feedback return

The tester runs:

1. [`alpha/launcher/doctor_check.bat`](launcher/doctor_check.bat)
   and screenshots the output.
2. *Settings → Export stats* and saves `stats.json`.
3. Fills [`alpha/FEEDBACK.md`](FEEDBACK.md).
4. Sends all three to the founder via the channel they were
   given.

The founder side:

1. `python apps/admin/import_stats.py <stats.json> <cohort> <handle>`
   — the trust-ledger gate.
2. `python apps/admin/merge_stats.py` — fold into `aggregate.json`.
3. `recall founder bake` — refresh the control room.
4. Hand-edit [`alpha_report.md`](alpha_report.md): copy the
   tester's free-text quotes into the right Q1-5 section; tick
   the per-tester boxes.
5. Append a new row to [`alpha/recovery_journal.json`](recovery_journal.json)
   if the tester reported a real recovery moment (right or wrong).

---

## Expected events — the four moments per persona

The runbook ends with the shape the founder is listening for. Each
persona has a typical *first-of* date for four key events:

| Event | founder | student | researcher | builder | non-prod |
|---|---|---|---|---|---|
| first investigation | day 1 | day 2 | day 3-4 | day 1 | day 2-3 |
| first recovery card shown | day 2 | day 5-6 | week 2 | day 2 | (none) |
| first Resume click | day 3 | day 5-6 | week 2 | day 2-3 | (none) |
| first trust moment ("wait, it remembered that?") | day 3-5 | day 5-7 | week 2 | day 4-5 | (rare) |

The directive's success criterion is calibrated against this
table:

> *5 humans run Recall. 3 get recovery. 2 return voluntarily.
> 1 says "wait... it remembered that?"*

In this table: the *3 get recovery* number is the union of the
founder + student + builder columns. The *2 return voluntarily*
is anyone who reaches Day 4-5 still using Recall without prompt
(realistically the founder + builder + possibly student). The
*1 trust moment* is the single quote from
[`FEEDBACK.md`](FEEDBACK.md)'s *"What surprised you"* row.

Anything less than the success line is a real signal, not a
failure — the runbook ends there because the next call is the
founder's.

> Cross-referenced by
> [`alpha_report.md`](alpha_report.md) (the evidence ledger
> per Q1-5) and the runbook in
> [`docs/founder/FIRST_WEEK.md`](../docs/founder/FIRST_WEEK.md).
