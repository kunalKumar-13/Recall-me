# <tester-handle> — alpha-001 record

The shape every tester folder takes inside `alpha-001/`. `recall
alpha create <handle> --cohort alpha-001` copies this template
into `alpha-001/<handle>/`; the founder hand-edits the markdown
files as the week unfolds.

The folder contains **metadata only** — never URLs, filenames,
queries, or chat content. The boundary is in
[`docs/engineering/TRUST_LEDGER.md`](../../../docs/engineering/TRUST_LEDGER.md).

---

## Fields (filled by the founder as the week runs)

```
handle:           <founder-assigned, e.g. tester-12; never PII>
cohort:           alpha-001
install_date:     YYYY-MM-DD
platform:         Windows 10 / Windows 11 / macOS-Intel / macOS-Silicon / Linux
installer:        Recall-Setup-lite.exe  (or -full)
install_ok:       yes / no / partial
install_minutes:  <wall time; the directive cap is 3 min>
day1:             yes / no / unknown   (tester opened launcher voluntarily)
day2:             yes / no / unknown
day3:             yes / no / unknown
first_recovery:   YYYY-MM-DD  /  none yet
first_resume_ok:  yes / no / wrong work
kept_using:       yes / no / unknown   (still installed after 7 days)
drop_reason:      install-fail / not-useful / privacy / other / n/a
feedback_returned: yes / no
notes:            one founder line; no content
```

The same fields appear in `status.json` (the machine-readable
twin); editing one should mean editing the other. The CLI keeps
them in sync.

---

## Files in a tester folder

| File | Always present | Contents |
|---|---|---|
| `status.json` | yes | the fields above, in JSON; CLI-edits this |
| `day1.md` | optional | one-line founder note: *"reported empty popup on day 1"* |
| `day2.md` | optional | *"saw first recovery; wrong title, right tabs"* |
| `day3.md` | optional | *"clicked Resume; right work"* |
| `feedback.md` | only if returned | the tester's `FEEDBACK.md` verbatim, **only with their explicit OK** |
| `stats.json` | only if returned | the `recall stats --export` output the tester sent |

Nothing else. The folder never contains:

- captured event logs
- screenshots with filenames / URLs / queries visible
- chat transcripts
- any file copied from `~/.recall/events/`

---

## Lifecycle

1. **Tester invited.** Founder runs `recall alpha create <handle>
   --cohort alpha-001`. CLI copies this template into
   `alpha-001/<handle>/`, fills `install_date: <today>` and
   leaves the rest blank.
2. **Tester installs.** Founder fills `install_ok` + `platform`
   + `install_minutes`.
3. **Days 1-3.** Founder fills the booleans + first-recovery
   date as the tester reports (or remains silent).
4. **End of week one.** Tester returns `FEEDBACK.md` + `stats.json`
   per [`feedback_link.txt`](../../launcher/feedback_link.txt).
   Founder saves them into the folder. Status fields complete.
5. **Decision row in `alpha_report.md`.** The folder's data feeds
   one row in [`alpha/alpha_report.md`](../../alpha_report.md)
   under Q1-5.

---

## How this is *not* used

- **Not an analytics database.** A tester is one folder; there is
  no SQL, no ID mapping, no longitudinal slicer beyond what the
  CLI prints.
- **Not a recruitment funnel.** No prospect-list, no "lead score".
  A folder exists only after a real tester accepts the invite.
- **Not a public artifact.** `alpha/users/` is repo-tracked so the
  state is auditable, but no folder is published; PRs that add
  PII or content get rejected.
