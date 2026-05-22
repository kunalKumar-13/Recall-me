# FIRST_72_HOURS.md — what the cohort actually feels, hour by hour

The directive: map the *trust / confusion / drop-risk / aha-moment*
curve for the first 72 hours of using Recall. The cohort drops if
none of those four lines hit the right level at the right time.

This is the **tester-facing** companion to
[`ALPHA_001_RUNBOOK.md`](ALPHA_001_RUNBOOK.md) (the founder's
table) and [`SAMPLE_WORKFLOW.md`](SAMPLE_WORKFLOW.md) (the
end-of-week summary). It zooms in on the first 72 hours because
that is when **drop-risk peaks** — past Day 3, the user has
either bought in or uninstalled.

---

## Day 0 — install (minute 0 → minute 5)

### What the user does

1. Runs `install.ps1` from the `alpha/launcher/` pack. ~30-60 s.
2. SmartScreen warns. *More info → Run anyway*.
3. Recall opens to the first-launch screen.
4. Picks folders. Optionally enables browser memory. *Done*.

### Trust / confusion / drop-risk / aha

| Curve | Level | Why |
|---|---|---|
| **Trust** | medium | The SmartScreen warning costs ~10 trust points. The "no admin password" path *returns* most of them. |
| **Confusion** | medium-low | Folder picker is calm; the *what is Recall about to read?* question is concrete and answerable. |
| **Drop-risk** | **high** | If the install itself fails — SmartScreen really blocks, install hangs, no shortcut appears — Day 0 is the most likely uninstall moment. |
| **Aha** | none | Recall has nothing to show yet. Aha cannot land here. |

### Friction the cohort is most likely to report

- *"It said Windows protected my PC."* — expected; the alpha
  packet's [`INSTALL.md`](INSTALL.md) calls it out. If a tester
  reports it as a problem, the answer is "see the note about
  SmartScreen". If they report not seeing the note, that's a doc
  bug.
- *"I don't know what folders to pick."* — Documents + Desktop
  are pre-checked. If they ask, the folders are the only thing
  Recall ever reads from. Recovery message: *the launcher's
  Settings dialog lets you change folders anytime*.

### What ends Day 0

The launcher closes; the user goes back to whatever they were
doing. Recall is invisible. **The Day 0 success line:** *the
tester does not uninstall before going to sleep.*

---

## Day 1 — quiet capture (hour 1 → hour 24)

### What the user does

Normal work. Edit files, open browser tabs, search the web, use
AI chats. Recall is in the tray; nothing prompts them.

### Trust / confusion / drop-risk / aha

| Curve | Level | Why |
|---|---|---|
| **Trust** | **medium-low** ↓ | Recall is *doing something* but the user can't *see* it. Without the Phase 5H *DaemonPulse* + *CapturingState* the popup shows, trust slides further here. |
| **Confusion** | medium | *"Is anything happening?"* The tray icon doesn't blink. The launcher is empty on Ctrl+Space. |
| **Drop-risk** | medium | The "this app does nothing" verdict forms here. The DaemonPulse + the popup's *Recent activity* feed are the two surfaces that fight this. |
| **Aha** | none yet | Day 1 is too early for recovery; investigations need at least 2-3 visits to the same topic. |

### What the user should see

- **Tray icon**, with the breathing accent.
- **Popup**: `CapturingState` — *Recall is watching locally · N
  events captured · Recent activity (top 5)*. The Phase 5H state
  machine's purpose is exactly this surface — Day 1 is when it
  earns its weight.
- **Launcher (Ctrl+Space)**: still mostly empty by design. The
  message is *"Recall is ready. Work a little, then come back
  later."* — the calm first-week-hint from `app/ui/cards.py`.

### What ends Day 1

The user has gone through one work-rest cycle. Recall has
captured 30-200 events (depending on persona — see
[`ALPHA_001_RUNBOOK.md`](ALPHA_001_RUNBOOK.md)). **The Day 1
success line:** *the tester opened the launcher at least once
voluntarily.*

---

## Day 2 — the first useful launcher (hour 24 → hour 48)

### What the user does

Mid-day or end-of-day, presses Ctrl+Space. **For the first time
the launcher actually shows things:** active investigations, the
*On your radar* row, possibly a recovery card if they abandoned
work the day before.

This is the moment Recall earns its first *aha*. The Phase 5I
stagger-reveal lands here — the digest sections fade in top-down
over ~600 ms, which is the second the user notices *"oh, this is
actually doing something."*

### Trust / confusion / drop-risk / aha

| Curve | Level | Why |
|---|---|---|
| **Trust** | **high** ↑ | Three calm sections, all *correctly named* (the investigation titles come from the user's own page titles and queries, not from a model inventing them). |
| **Confusion** | medium-low | *"What's the difference between Continue and Active investigations?"* — answered by [`SAMPLE_WORKFLOW.md`](SAMPLE_WORKFLOW.md), but worth asking. |
| **Drop-risk** | **low** | Past this hour, the cohort is in. The investigations are *enough* to keep Recall open even before the first recovery click. |
| **Aha** | **possible** | If a recovery card surfaces and the user clicks Resume and the right work is back, this is *the* aha. It might be Day 2 for the founder persona, Day 3+ for the student. |

### What can go wrong

- **The investigation title is wrong.** *"Trip planning"* but the
  user was researching trip insurance. The smoke calibration
  ([`docs/trust/TRUST_FIXTURES_CONTINUITY.md`](../docs/trust/TRUST_FIXTURES_CONTINUITY.md))
  catches obvious cases. A real wrong title from a tester is a
  *calibration data row* — log it in
  [`recovery_journal.json`](recovery_journal.json) with
  `wrong: true`.
- **No recovery card on Day 2.** Not a failure — Phase 4G's rule
  is *correct silence > wrong recovery*. The *Active
  investigations* and *On your radar* sections carry Day 2 if
  recovery is silent.

### What ends Day 2

The user has seen the digest fill, possibly clicked Resume,
possibly not. **The Day 2 success line:** *the tester opened the
launcher and the first row was a real piece of work they did
yesterday.*

---

## Day 3+ — the resume click (hour 48 → hour 72)

### What the user does

Mid-day on Day 3, switches tasks without bookmarking. Next
morning, presses Ctrl+Space *before* reaching for bookmarks or
browser history.

### Trust / confusion / drop-risk / aha

| Curve | Level | Why |
|---|---|---|
| **Trust** | **highest of the week** | The Resume click reopens *exactly* the tabs + files from before the switch. The user spent ~5 seconds and got back ~10 minutes of context. |
| **Confusion** | low | The flow is one click. If the work returns wrong, Confusion spikes; otherwise low. |
| **Drop-risk** | very low | Past a correct Resume click, the cohort uses Recall reflexively. The retention curve flattens. |
| **Aha** | **the aha** | *"Wait — it remembered that?"* The directive's success-criterion quote is the literal goal of this moment. |

### What the founder is listening for at Day 3

Three free-text questions, all in [`FEEDBACK.md`](FEEDBACK.md):

1. *"Did you click Resume on a recovery card?"*
2. *"Was the work the right work?"*
3. *"What surprised you?"*

A *yes / right / "I forgot I had been doing that"* on those three
lines is the alpha-001 victory condition for one tester.

---

## The 72-hour summary curve

```
                Day 0       Day 1       Day 2       Day 3+
Trust            ▒▒▒░       ▒▒░░       ▒▒▒▒▒      ▒▒▒▒▒▒▒
Confusion        ▒▒░░       ▒▒▒░       ▒▒░░       ▒░░░░░░
Drop-risk        ▒▒▒▒▒▒     ▒▒▒░       ▒▒░░       ▒░░░░░░
Aha              ░░░░░░     ░░░░░░     ▒▒▒░       ▒▒▒▒▒▒▒
```

The drop-risk curve is the most important read. It is highest on
Day 0 (install can fail), still elevated on Day 1 (Recall feels
absent), and falls sharply on Day 2 (the digest finally has
content). By Day 3 a tester who is still installing Recall when
they boot their machine is *probably going to keep it*.

The aha-curve trails by one day — the moment "this app is doing
something" is Day 2; the moment "this app remembered that for
me" is Day 3+.

---

## What this asks of the build

Three things across the build surfaces have to be working at the
right hour to keep the drop-risk line falling:

| Hour | What must work | Where it lives |
|---|---|---|
| 0-5 (install) | Silent install in <60 s, no admin prompt, no crash on first launch | `recall.iss` + `dist/installer/Recall-Setup.exe` |
| 12-24 (Day 1) | DaemonPulse breathing in the popup; CapturingState's *Recent activity* feed; `events_today` count | `apps/extension/ui/src/App.tsx` + popup state machine |
| 24-48 (Day 2) | The digest stagger-reveal animates; *Continue / Active / On your radar* sections fill from real events | `app/ui/launcher.py` + `_populate_digest` |
| 48-72 (Day 3+) | A *correct* first recovery card; Resume click reopens the right tabs + files | `app/core/recovery.py` + `_on_recovery_restore` |

If any of those four surfaces is broken at its hour, the cohort
loses a tester. Build verification's job is to test *each* of
them before the alpha-001 hand-off.

---

## What this is not

- Not a marketing onboarding script. The launcher onboarding
  ([`app/ui/onboarding.py`](../app/ui/onboarding.py)) is the
  in-app surface. This file is the founder's mental model.
- Not a measurement instrument. The numbers in
  [`alpha_report.md`](alpha_report.md) come from voluntary
  exports, not from instrumentation embedded here.
- Not a script the cohort reads. The cohort reads
  [`SAMPLE_WORKFLOW.md`](SAMPLE_WORKFLOW.md). This file is the
  founder reading what *they* should expect from each cohort
  tester.

> Cross-referenced by
> [`ALPHA_001_RUNBOOK.md`](ALPHA_001_RUNBOOK.md) (the persona
> table that lives one zoom level out),
> [`alpha_report.md`](alpha_report.md) (the post-cohort
> evidence ledger), and
> [`FIRST_WEEK.md`](../docs/founder/FIRST_WEEK.md) (the broader
> seven-day picture).
