# ALPHA_FEEDBACK_V2 — the tightened intake template

The v1 form ([`FEEDBACK.md`](FEEDBACK.md)) was 11 sections; what
the founder *acts on* lives in 6 of them. V2 is those 6, named
straight out of the Phase 5K directive: **moment of delight,
confusion, wrong recovery, missed recovery, install pain, keep /
remove**.

V2 supersedes v1 for cohorts opened after Phase 5K. Existing
alpha-001 testers who already received v1 may return either form;
both feed the same [`alpha_report.md`](alpha_report.md) rows.

Same boundary: no URLs / filenames / queries / chat content.
Only what *you* type, in your own words.

---

## You

> Pick a handle (anything — your name, a nickname, "tester-12").
> The founder uses it to dedupe entries; it never enters telemetry
> because there is no telemetry.

**Handle:** _____

**Install date:** _____

**Cohort:** alpha-001 / alpha-002 / friends / builders / students

**Platform:** Windows 10 / Windows 11 / macOS-Intel / macOS-Silicon
/ Linux / other: _____

---

## 1. Moment of delight

The single moment in the week when Recall made you think *"oh,
this is what it's for."* One sentence is plenty.

> _____

If there was no moment of delight, write *"none"* — that is a
real, honest signal.

---

## 2. Confusion

The single moment when you stopped using Recall and asked
*"wait, what?"* — about the installer, the launcher, the
extension, the docs, the popup, anything.

> _____

Three optional follow-ups if you want to be specific:

- **Where:** installer / launcher / popup / Settings / docs / _____
- **When:** day 0 / day 1 / day 2 / day 3+ / _____
- **What you expected vs what happened:** _____

---

## 3. Wrong recovery

Did the launcher ever surface a *Continue where you left off*
card that was about **the wrong work**?

- Yes / No / Didn't see any recovery cards

If yes, describe it in **categories** (not in URLs or filenames):

- *What you were actually doing:* _____  (e.g. *"writing a
  proposal"*, *"debugging a payment flow"*)
- *What Recall thought you were doing:* _____ (e.g. *"trip
  planning"*)
- *How wrong was it:* slightly off / different topic / unrelated
- *Did you click Resume anyway?* Yes / No

A single *unrelated* wrong recovery is the most actionable signal
in this whole form. It is what caps the Trust dimension's score
in [`READINESS_SCORE.md`](../docs/founder/READINESS_SCORE.md).

---

## 4. Missed recovery

Was there a moment when a recovery card **should have** shown up
but didn't? You were about to switch back to something Recall had
seen you abandon — and the launcher was silent.

- Yes / No / Don't know

If yes:

- *What you were trying to return to:* _____ (categories, not
  URLs)
- *How long since you last touched it:* hours / 1 day / 2 days /
  longer
- *Where you ended up finding it instead:* bookmarks / history /
  search / memory / never

Missed recoveries are harder to spot than wrong ones (Recall's
silence is louder than its wrong-cards). If you noticed one,
that's signal.

---

## 5. Install pain

Anything between *download* and *first Ctrl+Space*. The
SmartScreen warning, the folder picker, the extension setup, the
"is anything happening?" Day 1 moment.

- *Worst friction (≤ 1 sentence):* _____
- *Did it block you?* yes / no
- *Were you tempted to give up?* yes / no / _____

---

## 6. Keep / remove

End-of-week-one verdict. Pick one:

- **Keep installed** — still open the launcher reflexively
- **Keep, but rarely** — installed but seldom used
- **Removed** — uninstalled before the week ended
- **Will remove** — still installed but will uninstall

**Why:**

> _____

If you removed Recall, the single most useful sentence here is:
*"I would have kept it if..."*. Even one of those moves the
roadmap.

---

## What to attach (same as v1)

1. **`stats.json`** from `recall stats --export`. Counts only;
   contents in
   [`docs/engineering/TRUST_LEDGER.md`](../docs/engineering/TRUST_LEDGER.md).
2. **A screenshot of `recall doctor`** — `%LOCALAPPDATA%\Programs\Recall\Recall.exe
   doctor` (or use [`alpha/launcher/doctor_check.bat`](launcher/doctor_check.bat)).
3. **The extension popup state** — a screenshot of the popup as
   it looked at end of week.

Three small files. Hand back via the channel the founder gave you.

---

## What is *never* sent back

Same as v1:

- the event log (`%USERPROFILE%\.recall\events\`)
- the indexed-folder list
- any screenshot showing filenames / URLs / queries (redact before
  sending; the founder will refuse to look at non-export content)

The boundary is in
[`docs/engineering/TRUST_LEDGER.md`](../docs/engineering/TRUST_LEDGER.md).
If at any point this form asks you for something on the *never
sent* list, that is a bug, not a request — write it in the
*Confusion* row.

---

## How the founder reads V2

| V2 row | Maps to | Action when filled |
|---|---|---|
| 1. moment of delight | `alpha_report.md` Q5 ("what surprised you") | quoted into the report |
| 2. confusion | Q5 (where friction) + adds a row to [`OPEN_PROBLEMS.md`](../docs/engineering/OPEN_PROBLEMS.md) if it names a surface | both |
| 3. wrong recovery | Q3 ("did recovery help") + appends a row to [`recovery_journal.json`](recovery_journal.json) with `wrong: true` | both |
| 4. missed recovery | Q3 calibration ledger; readiness-score trust dimension takes the hit | report + score |
| 5. install pain | [`CLEAN_MACHINE_RUN.md`](../docs/trust/CLEAN_MACHINE_RUN.md) friction-log row | added to the install matrix |
| 6. keep / remove | `alpha/users/<cohort>/<handle>/status.json` `kept_using` + `drop_reason` | the row most likely to flip the cohort's Met? verdict |

V2 is **tighter**, not shorter — every row maps to a concrete
artifact the founder has to update if the row is filled. There
is no "thanks for the feedback" trash bin.

---

## Returning a partially-filled form

Fully expected. If a tester fills only rows 1 and 6 (delight +
keep/remove) that is *better* than nothing. The directive's
success line was *5 humans, 3 recoveries, real friction, real
trust signal* — even two of those rows from one tester counts as
real signal.
