# PHASE_6E_STATUS.md — Alpha Reality

The receipt for Phase 6E. The directive's *Goal*: Recall leaves
founder-only mode. Real humans, real installs, real failures, real
recoveries. The Phase 6E scope is **operations** — the cohort
registry, the recovery ledger, the founder's green/yellow/red
panel, the playbook, the failure catalogue, the matrix extension.

**Anti-rules respected**: no engine work, no UI redesign. The
engine layers (events / sessions / contexts / resurfacing /
threads / evolution / recovery) are not touched. The launcher and
the popup are not redesigned. Every change in this phase is a
hand-edited JSON file, a CLI subcommand, or a markdown doc.

The 6D→6E handoff: 6D made a fresh install *look* alive via the
demo overlay; 6E builds the operational scaffolding to let real
testers install Recall, use it, leave it, return to it, click
Resume, and report back — without any single touchpoint requiring
new engine code.

Cross-references:
[`docs/alpha/PLAYBOOK.md`](../../docs/alpha/PLAYBOOK.md) (operations book),
[`docs/alpha/STATUS.md`](../../docs/alpha/STATUS.md) (cohort board),
[`docs/alpha/KNOWN_FAILURES.md`](../../docs/alpha/KNOWN_FAILURES.md)
(failure catalogue),
[`docs/trust/ALPHA_MATRIX.md`](../../docs/trust/ALPHA_MATRIX.md) (the
extended install + daily-use matrix),
[`PHASE_5K_STATUS.md`](PHASE_5K_STATUS.md) (the Phase 5K alpha
infrastructure 6E builds on).

---

## What shipped

### 1. Status template + tester record extended

[`alpha/users/_TEMPLATE/status.json`](../../alpha/users/_TEMPLATE/status.json)
gained three directive-named fields, all metadata, all optional:

- `installer_version` — which artifact tag a tester installed
  (e.g. `0.2.4-lite`).
- `extension` — `chrome` / `edge` / `arc` / `none`.
- `wow_moment` — one sentence; what surprised them, in their
  words (with their explicit OK).
- `confusion` — one sentence; what they didn't understand.

`TesterRecord` in
[`app/core/alpha_cli.py`](../../app/core/alpha_cli.py) gained the
matching attributes. Existing status.json files keep working —
the loader defaults missing keys to `None`.

### 2. `recall alpha update` + `recall alpha export`

Two new subcommands in the alpha CLI:

- `recall alpha update <handle> --<field> <value> [...]` —
  hand-applies the founder's latest read of a tester. Cross-cohort
  lookup by handle (with optional `--cohort` for disambiguation);
  rejects unknown fields against a closed allowlist
  (`_UPDATABLE_FIELDS`); type-coerces `install_minutes` to float
  and `feedback_returned` to bool; an empty-string value clears
  a field.
- `recall alpha export [--cohort <name>]` — JSON dump of the
  same metrics `report` prints in human form. Five top-level
  keys match the directive vocabulary verbatim: `installs`,
  `returning`, `recoveries`, `issues`, `trust`. Plus
  `drop_reasons` and a `cohorts` array of per-cohort summaries.
  Counts only — never URLs, filenames, queries, or any field the
  boundary rejects.

The `_compute_trust_pct()` helper reads
`alpha/recovery_journal.json` and aggregates the six Phase 6E
ledger outcomes; the export embeds the result. Legacy
journal entries (pre-6E `accepted` / `wrong` booleans) are
mapped onto the new vocabulary so old data still counts.

### 3. Recovery ledger schema, six outcomes

[`alpha/recovery_journal.json`](../../alpha/recovery_journal.json)
schema rewritten. The `_kind_vocabulary` block names the
directive's six outcomes:

```
shown            launcher surfaced a card; user just saw it.
accepted         tester clicked Resume.
ignored          tester saw the card and chose not to act.
correct_silence  launcher correctly showed no card on a no-work day.
bad_recovery     card shown AND reopened work was wrong.
resume_ok        tester clicked Resume AND reopened work matched.
```

The aggregator computes `trust % = (resume_ok + correct_silence) /
shown`. Legacy entries get mapped on read so the trust percentage
is always honest, even with rows written before 6E.

**Local only**, **export only** — the file is hand-edited, never
synced, never imported from telemetry (no telemetry exists).

### 4. Founder room — `recall founder alpha-health`

A new subcommand in
[`app/core/founder_cli.py`](../../app/core/founder_cli.py) that
reads the source-of-truth files directly (no `bake` round-trip
needed) and prints the directive's five signals with
green/yellow/red verdicts:

```
recall founder alpha-health

    [GREEN]   installs           5
    [GREEN]   returning          3  (>=2 of 3 days marked yes)
    [GREEN]   first recoveries   3
    [GREEN]   trust %            83%  (5/6 correct of shown)
    [YELLOW]  drop reasons       1
              1 x extension stayed disconnected
```

Thresholds (documented in-source):

- **GREEN** signal meets the alpha-001 floor (5 installs, ≥ 2
  returning, ≥ 3 first-recoveries, trust ≥ 80 %, no drop reason
  with count ≥ 2).
- **YELLOW** signal exists but is short of the floor.
- **RED** signal is meaningfully wrong (drop reason ≥ 2 of the
  same kind, or trust < 50 % with ≥ 5 shown).

The panel also prints the directive's alpha-001 success line —
*5 humans / 3 recoveries / 1 wow / 1 failure story* — with an
`OK` / `short` flag against the current numbers.

### 5. `docs/alpha/` — the operations trio

Three new docs:

- [`PLAYBOOK.md`](../../docs/alpha/PLAYBOOK.md) — the operations book.
  Six-moment tester lifecycle (install / use / leave / return /
  resume / report), the per-tester status.json field list, the
  daily morning loop, the six recovery-ledger outcomes, the
  *no content / no telemetry* contract restated.
- [`STATUS.md`](../../docs/alpha/STATUS.md) — the live cohort board.
  Hand-edited weekly from `recall alpha export` + `recall
  founder alpha-health`. Mirrors the directive's success-line
  table.
- [`KNOWN_FAILURES.md`](../../docs/alpha/KNOWN_FAILURES.md) — the
  failure catalogue. The trust contract: quote, don't paraphrase;
  never inflate; promote to engineering only when ≥ 2 testers
  hit the same wall.

### 6. `ALPHA_MATRIX.md` extended

[`docs/trust/ALPHA_MATRIX.md`](../../docs/trust/ALPHA_MATRIX.md) gained a
*Phase 6E — daily-use + browser matrix* section: 5 new rows
covering Windows 11 daily use × Chrome / Edge / Arc + macOS Intel
+ macOS Apple Silicon daily use. Each row carries two columns —
*Recovery appeared?* + *Resume worked?* — the only two
machine-level cohort questions Phase 6E adds on top of the
existing 5-row clean-install matrix. Honesty rule unchanged:
`unknown` until a real tester completes ≥ 3 days on the
machine + browser pair.

### 7. Captures

Three new PNGs in
[`assets/screenshots/alpha/`](../../assets/screenshots/alpha):

| File | What it shows |
|---|---|
| `alpha-control-room.png` | The `recall founder alpha-health` panel populated with a fixture cohort (5 installs, 3 returning, 3 recoveries, trust 83 %, one yellow drop reason). The directive's *operator control room*. |
| `alpha-status.png` | `recall alpha status` with 5 testers across `alpha-001` / `friends` / `builders` / `students`. The directive's per-tester view. |
| `alpha-empty.png` | The honest zero — `recall alpha status` with no testers yet. The state every fresh repo clone starts in. |

Captured offscreen via Consolas (mono) on a warm-white background
so the alpha screens sit next to the launcher / extension v2 sets
visually rather than reading as a terminal screenshot from a
different product.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Per-tester `feedback_returned` ingestion that auto-fills `status.json` from the tester's emailed form | partial | The `feedback_returned: bool` field exists; the *parsing* of an emailed form into the JSON is still a hand step (the boundary requires founder redaction anyway). |
| A `recall alpha import-journal` subcommand that ingests one ledger row at a time | not in scope | Hand-editing `alpha/recovery_journal.json` is fine; the daily loop is ≤ 5 minutes and the founder is the only writer. Adding a CLI for it is sugar, not capability. |
| `apps/admin/data/cohorts.json` auto-baked from the Phase 6E sources | not in scope | The existing `recall founder bake` script handles cohorts.json from its own inputs; the Phase 6E `alpha-health` panel **bypasses bake** and reads sources directly so it is always current. |
| End-to-end cohort install on three Windows VMs + two Mac slots (the `ALPHA_MATRIX.md` rows) | external | Same external dependency as 5K: a maintainer with the relevant hardware. Phase 6E's job is the *operational scaffolding*; the rows fill as real installs happen. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| Alpha CLI help | `python recall.py alpha help` | new subcommands listed: `create`, `update`, `status`, `report`, `export` |
| Alpha CLI smoke (create / update / status / export) | end-to-end run on a temp tester `tester-e2e-6e` | all four subcommands succeed; export JSON includes the directive keys (`installs`, `returning`, `recoveries`, `issues`, `trust`); tester record cleaned up |
| Founder CLI | `python recall.py founder alpha-health` | five signals printed with `[GREEN]` / `[YELLOW]` / `[RED]` brackets; directive success-line printed when ≥ 1 tester exists; ASCII-only, cp1252-safe |
| Recovery ledger schema | `json.loads(...)` of `alpha/recovery_journal.json` | parses; `_kind_vocabulary` block lists the six Phase 6E outcomes |
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| docs links | grep for the new doc paths | all four (`docs/alpha/PLAYBOOK.md`, `STATUS.md`, `KNOWN_FAILURES.md`, `ALPHA_MATRIX.md` Phase 6E section) referenced from `PHASE_6E_STATUS.md` |
| captures | `python infra/scripts/capture/capture_alpha.py` | 3 PNGs into `assets/screenshots/alpha/` |
| doctor (regression) | `python recall.py doctor` | unchanged — Phase 6E touched **no** doctor surface |
| extension build (regression) | `cd apps/extension/ui && npm run build` | unchanged from 6D (no extension files touched) |

---

## Touched files

```
new code:
  infra/scripts/capture/capture_alpha.py

modified code:
  app/core/alpha_cli.py            (update / export + new fields)
  app/core/founder_cli.py          (alpha-health subcommand)
  alpha/users/_TEMPLATE/status.json (4 new fields)
  alpha/recovery_journal.json      (schema rewrite for 6-kind vocabulary)
  docs/trust/ALPHA_MATRIX.md       (Phase 6E daily-use rows)

new docs:
  docs/alpha/PLAYBOOK.md
  docs/alpha/STATUS.md
  docs/alpha/KNOWN_FAILURES.md
  docs/engineering/PHASE_6E_STATUS.md

new captures:
  assets/screenshots/alpha/alpha-control-room.png
  assets/screenshots/alpha/alpha-status.png
  assets/screenshots/alpha/alpha-empty.png
```

No engine layer touched. No UI surface (launcher widget / extension
popup) touched. No `~/.recall/` file written by the Phase 6E code
paths — every artifact lives in the repo-tracked `alpha/`,
`docs/alpha/`, `assets/screenshots/alpha/`, or
`docs/engineering/PHASE_6E_STATUS.md`.

---

## Read-back of the success criterion

The directive's success line:

> 5 humans · 3 recoveries · 1 wow · 1 failure story

The current actual numbers are **0 / 0 / 0 / 0** — the cohort has
not started. What Phase 6E *delivers* is the operational
machinery that lets those numbers move:

- The CLI to record each install (`recall alpha create`).
- The CLI to apply daily founder reads (`recall alpha update`).
- The ledger to record each Resume decision
  (`alpha/recovery_journal.json` + six outcomes).
- The dashboard to surface the five signals
  (`recall founder alpha-health`).
- The playbook to drive the morning loop
  (`docs/alpha/PLAYBOOK.md`).
- The matrix to track machine + browser coverage
  (`docs/trust/ALPHA_MATRIX.md`).
- The catalogue to record failures honestly
  (`docs/alpha/KNOWN_FAILURES.md`).

When the founder hands off the first installer to the first
tester, every artifact above is ready. The directive's four
numbers move from `0` upward through the same surface that this
file describes.
