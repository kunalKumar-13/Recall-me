# alpha/failures — one file per incident

When Recall does something wrong, write it here.
One file per incident. Filename is the date +
short slug, e.g.:

```
2026-05-24-launcher-imported-demo-data.md
```

The `recall alpha review` CLI counts every `.md`
file in this folder (except `README.md` and any
`TEMPLATE.md`) as one failure incident.

## Five fields per file

Use this template — it lives at
[`TEMPLATE.md`](TEMPLATE.md).

```
# <one-line title>

**Reporter:** alpha-NNN     (your handle, not your name)
**Date:**     YYYY-MM-DD
**Severity:** P0 / P1 / P2  (see BUGS_OPEN.md)

## What happened

(One paragraph. Plain language. No screenshots
required unless they save a paragraph.)

## What you expected

(What you thought Recall would do at that moment.)

## What actually happened

(What it did instead. Be specific. Times,
counts, exact wording.)

## Repro

(Steps. Even three lines. "Open launcher, see X,
click Y, observe Z.")

## Notes

(Anything else: was the daemon up? Did doctor
show GREEN? Did it self-recover?)
```

## What counts as a failure

Any of:

- Recall crashed, hung, or refused to start.
- The launcher showed wrong work in the Continue
  card.
- The extension dropped its pairing without
  warning.
- Capture missed something it should have caught.
- A doctor row went RED without a clear cause.
- The product confused you in a way that felt
  like *its* fault, not yours.

## What does NOT count

These belong in [`../pack/FEEDBACK.md`](../pack/FEEDBACK.md),
not here:

- "I wish it did X."
- "The visual could be better."
- "I forgot to open it."

The line: **a failure is something the product
got wrong**, not something you wish it did
differently.

## Privacy boundary

The same boundary applies as the rest of
[`alpha/`](..): **metadata only.** Don't paste
URLs you visited. Don't paste filenames you
opened. Don't paste your queries. If a bug
requires content to reproduce, describe the
*shape* of the content ("a 4-tab GitHub
investigation with one ChatGPT chat") not the
specifics.

## How to file

Three options:

| Option                              | When                              |
|-------------------------------------|-----------------------------------|
| Drop a `.md` here, paste later      | Default                           |
| Open a GitHub issue                 | If you want it tracked publicly   |
| Email the founder                   | If it's sensitive                 |

If you file as a GitHub issue, copy the same
five fields. The issue is the canonical record;
this folder is the local working copy.

## Existing incidents

Filed during Phase 8E:

- [`2026-05-24-launcher-imported-demo-data.md`](2026-05-24-launcher-imported-demo-data.md)
  — BUG-001, the 8B archive over-reach. Self-reported
  by the founder during the 8C stability pass.
