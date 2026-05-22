# PLAYBOOK.md — the alpha cohort playbook

The Phase 6E operations book. Recall is leaving founder-only mode;
real humans will install it, use it, leave it on, return to it,
maybe resume a recovery, and (in some cases) hit a wall and write
back about it. This file is the *playbook* — what happens at each
of those six moments, what the founder is responsible for, and
which field of `status.json` carries the receipt.

This is **operations**, not engineering. Nothing in this file
asks the engine for a new feature. Every step is something a
single person on a laptop can execute in under fifteen minutes a
day.

Pairs with:

- [`STATUS.md`](STATUS.md) — the live cohort state board.
- [`KNOWN_FAILURES.md`](KNOWN_FAILURES.md) — the failure
  catalogue.
- [`ALPHA_MATRIX.md`](../trust/ALPHA_MATRIX.md) — the
  install-validation matrix.
- [`recall alpha`](../../app/core/alpha_cli.py) — the CLI that
  writes `alpha/users/<cohort>/<handle>/status.json`.
- [`recall founder alpha-health`](../../app/core/founder_cli.py) — the
  green/yellow/red operator panel.

---

## The six moments

A tester moves through six states. Each one has a single founder
action and a single field that captures the result.

| # | Moment | Founder action | Status field |
|---|---|---|---|
| 1 | **Install** | Hand off `Recall-Setup-lite.exe` (or the macOS `.dmg`) + the `alpha/launcher/` pack. Time the install if the tester sends a wall-clock. | `install_ok`, `install_minutes`, `installer_version`, `platform` |
| 2 | **Use** | Tester browses + works for 1-3 days. Founder only writes a record when the tester *reports* — silence is silence. | `day1`, `day2`, `day3`, `extension` |
| 3 | **Leave** | Tester walks away (intentional break, gap, weekend). No founder action. | nothing — leaving is normal |
| 4 | **Return** | Tester opens Recall after the gap and reports what they see. | `day2` / `day3` flipped to `yes`, `first_recovery` filled if a card showed |
| 5 | **Resume** | Tester clicks Resume on a recovery card; reports whether the reopened work matched. | `first_resume_ok` (`yes` / `wrong work` / `partial`), plus a `recovery_journal.json` entry |
| 6 | **Report** | End-of-week debrief: wow / confusion / pain / trust break / missed recovery / wrong recovery. | `wow_moment`, `confusion`, `drop_reason`, `kept_using`, `feedback_returned` |

The six moments mirror the directive's six steps verbatim:
**install / use / leave / return / resume / report**.

---

## Per-tester fields

The full `status.json` shape after Phase 6E (anything not listed
here is documented in
[`alpha/users/README.md`](../../alpha/users/README.md)):

| Field | Type | Notes |
|---|---|---|
| `handle` | string | founder-assigned, never PII |
| `cohort` | string | one of: `alpha-001`, `alpha-002`, `friends`, `builders`, `students` |
| `install_date` | date | YYYY-MM-DD; set by `recall alpha create` |
| `platform` | string | e.g. `Windows 11`, `macOS 14 (Apple Silicon)` |
| `installer` | string | which artifact: `lite`, `full`, `.dmg` |
| `installer_version` | string | the artifact's version tag (e.g. `0.2.4-lite`) — Phase 6E addition |
| `extension` | string | one of: `chrome`, `edge`, `arc`, `none` — Phase 6E addition |
| `install_ok` | string | `yes` / `no` / `partial` |
| `install_minutes` | float | wall-clock seconds → minutes, the tester's number |
| `day1` / `day2` / `day3` | string | `yes` / `no` / `unknown` |
| `first_recovery` | string | date in YYYY-MM-DD, or `none yet` |
| `first_resume_ok` | string | `yes` / `wrong work` / `partial` / `unknown` |
| `kept_using` | string | `yes` / `no` / `unknown` |
| `wow_moment` | string | one sentence in the tester's words (with their explicit OK) — Phase 6E addition |
| `confusion` | string | one sentence — what they didn't understand — Phase 6E addition |
| `drop_reason` | string | freeform; aggregated by `recall alpha export` |
| `feedback_returned` | bool | did the tester send the end-of-week form |
| `notes` | string | freeform; never URLs / queries / filenames |

The boundary remains the same as in
[`alpha/users/README.md`](../../alpha/users/README.md): **metadata
only — never URLs / filenames / queries / chat content**. Every
tester-supplied string is the founder's own paraphrase or a quoted
sentence the tester explicitly approved.

---

## Daily operating loop

A five-to-ten-minute morning loop the founder runs every day a
cohort is active:

1. **Read** any tester email / DM / chat from the last 24h.
2. **Update** `status.json` for each tester who sent something:
   ```
   recall alpha update <handle> --day2 yes --first_recovery 2026-05-25
   recall alpha update <handle> --wow_moment "WebSocket recovery on day 2"
   ```
3. **Append** to `alpha/recovery_journal.json` whenever a tester
   reports a recovery decision. Use one of the six `kind` values:
   `shown` / `accepted` / `ignored` / `correct_silence` /
   `bad_recovery` / `resume_ok`.
4. **Glance** at the panel:
   ```
   recall founder alpha-health
   ```
   Every signal should be GREEN or trending up. RED on
   `drop reasons` (≥ 2 of the same kind) means stop and look —
   the cohort is hitting a wall.
5. **Skip** the loop on a quiet day. Silence is signal; not every
   day produces a tester update.

The cadence is documented in
[`alpha/ALPHA_001_RUNBOOK.md`](../../alpha/ALPHA_001_RUNBOOK.md); the
Phase 6E additions slot into the same runbook, they do not replace
it.

---

## The six recovery-ledger outcomes

Per the directive, every recovery decision a tester reports lands
in `alpha/recovery_journal.json` with one of six `kind` values:

| Kind | What happened | Trust impact |
|---|---|---|
| `shown` | Launcher surfaced a card; tester saw it. (No click yet.) | Denominator. |
| `accepted` | Tester clicked Resume. | Click happened. Quality captured by `resume_ok` / `bad_recovery`. |
| `ignored` | Tester saw the card and chose not to act. | Neutral — the notes carry the story. |
| `correct_silence` | Launcher correctly showed *no* card on a day the tester had no resumable work. | Positive — silence is the right answer. |
| `bad_recovery` | Card shown AND the reopened work was wrong. | **Trust cap** — one row caps the trust dimension at 0.2. |
| `resume_ok` | Tester clicked Resume AND the reopened work matched. | Positive — the smile. |

Trust % is computed as `(resume_ok + correct_silence) / shown`.
The percentage is printed by `recall founder alpha-health` and
included in the `recall alpha export` JSON.

---

## What never enters the loop

Restated here so it stays in the playbook the founder will read
every morning:

- **No URLs.** Not in `notes`. Not in `wow_moment`. Not in
  `recovery_journal.investigation`.
- **No filenames.** Not in `wow_moment`. Not in `confusion`. Not
  anywhere.
- **No queries.** Not in any field.
- **No chat content.** Not paraphrased, not quoted, not summarised.
- **No automated push.** Every entry in `alpha/users/` is
  hand-written by the founder.
- **No telemetry.** Cohort signal is what the founder asks the
  tester to share, and what the tester chooses to send back.

If a tester sends a URL by accident, redact before saving.

---

## Promoting a tester to a permanent cohort

When the same persona earns three distinct testers (e.g. three
researchers in `friends/`), the founder splits them into their own
cohort dir:

1. Add the cohort to `app.core.alpha_cli.COHORTS`.
2. Create `alpha/users/<cohort-name>/`.
3. `recall alpha update <handle> --cohort <new-cohort>` and
   move the folder by hand.

The matrix in [`ALPHA_MATRIX.md`](../trust/ALPHA_MATRIX.md) gains
a row when a new *machine* slot is added, not when a cohort is.
