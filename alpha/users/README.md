# `alpha/users/` — per-user records

The alpha-001 cohort folder (and every cohort that follows) lives
here. Each tester gets a small, hand-edited folder with **no
content** about what they did — only **metadata** about whether the
install worked and whether Recall stayed installed. The boundary is
the same as [`docs/engineering/TRUST_LEDGER.md`](../../docs/engineering/TRUST_LEDGER.md):

> No filenames. No URLs. No queries. No chat content. No
> per-event timestamps. The launcher *titles* are the only thing
> a tester writes here — and only when they explicitly choose to
> share them.

## Structure

```
alpha/users/
├── alpha-001/        the first cohort
├── alpha-002/        the second cohort (queued)
├── friends/          ad-hoc personal contacts
├── builders/         the "builds-for-a-living" persona
└── students/         the "researching a topic" persona
```

Each subdirectory contains a `TEMPLATE.md` and, once any tester
joins that cohort, one folder per tester. The folder name is the
tester's **founder-assigned handle** (never PII):

```
alpha/users/alpha-001/
├── TEMPLATE.md             the shape every tester folder takes
├── tester-12/              one tester
│   ├── status.json         install date, platform, drop reason
│   ├── day1.md, day2.md    short notes; no captured content
│   └── feedback.md         end-of-week-one return
├── tester-13/
│   └── ...
```

## How a tester record is created

Three options, in order of preference:

1. **Via the CLI** — `recall alpha create <handle> --cohort alpha-001`.
   This copies the template, fills the install date, and writes a
   blank `status.json` the founder edits as the week unfolds.
2. **By hand** — `cp -r alpha/users/alpha-001/TEMPLATE
   alpha/users/alpha-001/<handle>` and fill the files.
3. **From a returned stats.json** — when a tester sends their
   `stats.json` back at end-of-week-one,
   `recall alpha report <handle>` ingests the counts into the
   matching `status.json` without ever touching content.

## What lives in a tester folder

| File | Purpose | Sensitivity |
|---|---|---|
| `status.json` | install_date · platform · install_ok · day1/2/3 booleans · first_recovery_date · kept_using · drop_reason | metadata only |
| `day1.md` / `day2.md` / `day3.md` | optional one-line founder note (*"reported their popup was empty on day 1"*) | metadata only |
| `feedback.md` | the tester's [`FEEDBACK.md`](../FEEDBACK.md) form, returned verbatim *only with their explicit OK* | tester text |
| `stats.json` | the `recall stats --export` output the tester chose to share | counts only |

Nothing else lives in a tester folder. **No log files. No event
logs. No screenshots that include filenames / URLs / queries.**
If a tester sends one of those by accident, the founder redacts
before saving (per [`alpha/FEEDBACK.md`](../FEEDBACK.md) § *what
is never sent*).

## Cohort assignment

The five cohort folders mirror the personas in
[`ALPHA_001_RUNBOOK.md`](../ALPHA_001_RUNBOOK.md):

- **alpha-001** — the **first** cohort. ≤ 5 testers. The runbook
  applies row-for-row.
- **alpha-002** — the **second** cohort. Queued; expected once
  alpha-001's first-week returns close.
- **friends** — ad-hoc personal contacts (the *founder* persona
  from the runbook is here).
- **builders** — the *builder* persona (three concurrent projects,
  micro-context separation stress).
- **students** — the *student* persona (multi-day arc, classic
  recovery shape).

The *researcher* and *non-productivity user* personas from the
runbook are slotted into `friends/` for now; once they earn enough
distinct testers each, they graduate to their own cohort dirs.

## The "no content, no telemetry" rule, restated

Two rules, both enforceable by grep:

1. **`alpha/users/**/*` may not contain a captured filename, URL,
   query string, or chat content.** A grep for `https?://`,
   `\.recall/events`, or `chrome://` should return zero matches.
2. **There is no automated push of any tester data into this
   folder.** Everything is hand-saved by the founder from
   tester-emailed artifacts.

If either rule ever breaks, that's the contract violation —
correct it before the next commit.
