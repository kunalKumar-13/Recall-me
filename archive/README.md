# `archive`

Deprecated systems and historical artefacts kept for context.
This is the **read-only** corner of the repo — anything in
here was removed from active service for a reason and isn't
imported by anything still running.

## Status

Currently empty.

## What goes here

- Pre-2A components that the smoke test no longer exercises.
- Earlier experimental layers superseded by the seven-layer
  hierarchy.
- Old design-system tokens that lost out to the current ones.
- Anything that's been retired but is worth keeping searchable
  rather than rebuilding from `git log`.

## What does *not* go here

- Code referenced by anything in `apps/*` or `packages/*`. If
  it's still imported, it lives where it's imported from.
- Generated artefacts (`build/`, `dist/`, `node_modules/`).
- Documentation. Old docs are versioned via git; they don't
  need a copy in `archive`.

## Adding to archive

A PR that archives a system includes:

1. The `git mv` of the files into `archive/<system-name>/`.
2. A `archive/<system-name>/README.md` recording when it was
   active, why it was retired, and what replaced it.
3. The removal of any remaining references in the live tree
   ([`AUDIT_REPORT.md`](../docs/engineering/AUDIT_REPORT.md) tracks the
   standing list).
