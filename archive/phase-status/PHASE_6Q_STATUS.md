# Phase 6Q — Continuity Truth

**Status:** complete
**Directive:** Make Recall feel correct. Not pretty. Not bigger.
Correct.
**Scope:** investigation quality only. No launcher redesign,
no extension redesign, no control-room work.

---

## What shipped

### Investigation principles

[`docs/product/INVESTIGATION_PRINCIPLES.md`](../../docs/product/INVESTIGATION_PRINCIPLES.md)
codifies the seven rules the engine has always (mostly) been
following:

1. Same topic returns → merge
2. One-off visit → suppress
3. Passive browsing → suppress
4. Deep work → promote
5. Unfinished work → strongest signal
6. Multi-day return → boost
7. Casual reopen loops → decay

The 9 anti-noise gates are listed with their constants +
where each lives in `recovery.py`.

### Promotion thresholds

[`docs/product/PROMOTION_THRESHOLDS.md`](../../docs/product/PROMOTION_THRESHOLDS.md)
documents the LOW (0-1) / MED (2-3) / HIGH (4+) bands plus
the five overrides:

1. `unfinished overrides all` — promote to HIGH.
2. `returned_after_gap` — boost +1 band.
3. Duplicate penalty — drop the lower-ranked one.
4. Noise penalty — `_MIN_RESUME_INTENT` floor, engine-side.
5. Ledger penalty — demote -1 band if `bad_recoveries.jsonl`
   flagged the thread within 14 days.

### Investigation inspector CLI

`recall inspect <id>` prints a deterministic ASCII card with
the investigation's title, strength band, signal lines,
evidence, and decision (`SHOW HERO` / `SHOW IN OTHER WORK` /
`SUPPRESS`). Accepts a `candidate_id`, `thread_id`, or title
substring. ASCII-only (no Unicode rules — survives `cp1252`).

Source: [`app/core/inspect_cli.py`](../../app/core/inspect_cli.py).

### *Why this?* sheet on the hero card

The hero now carries a small lavender *Why this?* link on the
right of its meta row. Clicking opens a centred sheet:

```
SHOWN BECAUSE
  - unfinished work
  - returned after a 2-day gap
  - 5 targets involved
  - multiple surfaces engaged
```

Lines come from `recovery.explain_signals(candidate)` —
deterministic, pure. **No AI text. No prose. No scoring
numbers.**

Sources: [`app/ui/launcher_v3/why_sheet.py`](../../app/ui/launcher_v3/why_sheet.py),
[`recovery.py:explain_signals`](../../app/core/recovery.py).

### Wrong-recovery ledger

`~/.recall/bad_recoveries.jsonl` — append-only JSONL with four
allowed reasons (`wrong_topic`, `already_done`, `noise`,
`duplicate`). Engine writes `signals.ledger_flagged = 1.0` on
candidates whose thread appears within the last 14 days; the
launcher honours the flag by skipping HIGH promotion.

Trust contract: **no content** (only `thread_id`, `reason`,
`ts`), **local-only**, **inspectable** (plain JSONL).

Source: [`app/core/bad_recoveries.py`](../../app/core/bad_recoveries.py).

### Trust review CLI

`recall trust review` prints the 14-day ledger summary +
three rates:

- **bad %** — `bad_total / shown`
- **silence %** — `(shown - accepted - bad_total) / shown`
- **resume %** — `accepted / shown`

Reads `~/.recall/bad_recoveries.jsonl` + `~/.recall/counters.json`.
No network.

Source: [`app/core/trust_cli.py`](../../app/core/trust_cli.py).

### Showcase verification

[`docs/product/SHOWCASE_TRUTH.md`](../../docs/product/SHOWCASE_TRUTH.md)
— the three-investigation scripted walk (proposal · RLHF ·
WebSocket). Only ONE hero must appear; the other two sit in
OTHER WORK. Documents the failure modes the showcase exists
to catch.

### Captures

Four PNGs in [`assets/screenshots/launcher-truth/`](../../assets/screenshots/launcher-truth):

- `hero_with_why.png` — hero card with the *Why this?* link
- `why_sheet.png` — the open sheet listing four engine signals
- `showcase.png` — one HIGH hero + three OTHER WORK titles
- `ledger_demoted.png` — same digest after a ledger flag —
  hero suppressed, only OTHER WORK survives

### Cleanup

[`archive/recovery-ranking/README.md`](../recovery-ranking/README.md)
documents:

- What 6Q kept untouched (every existing gate + every existing
  weight).
- What 6Q added (the `ledger_flagged` signal, the inspector +
  trust CLIs, the *Why this?* sheet).
- What 6Q considered and rejected (learned ranker, second
  freshness half-life, chat-heavy bump, engine-side
  duplicate de-dup).

---

## Files touched

**New:**

- [`app/core/bad_recoveries.py`](../../app/core/bad_recoveries.py)
- [`app/core/inspect_cli.py`](../../app/core/inspect_cli.py)
- [`app/core/trust_cli.py`](../../app/core/trust_cli.py)
- [`app/ui/launcher_v3/why_sheet.py`](../../app/ui/launcher_v3/why_sheet.py)
- [`infra/scripts/capture/capture_launcher_truth.py`](../../infra/scripts/capture/capture_launcher_truth.py)
- [`docs/product/INVESTIGATION_PRINCIPLES.md`](../../docs/product/INVESTIGATION_PRINCIPLES.md)
- [`docs/product/PROMOTION_THRESHOLDS.md`](../../docs/product/PROMOTION_THRESHOLDS.md)
- [`docs/product/SHOWCASE_TRUTH.md`](../../docs/product/SHOWCASE_TRUTH.md)
- [`archive/recovery-ranking/README.md`](../recovery-ranking/README.md)

**Edited:**

- [`recall.py`](../../recall.py) — added `inspect` + `trust`
  subcommand dispatch.
- [`app/core/recovery.py`](../../app/core/recovery.py) —
  `signals.ledger_flagged` + `explain_signals()` helper.
- [`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py) —
  optional `signals` parameter + `_WhyLink` widget + `request_why`
  signal.
- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py) —
  Override-5 ledger demotion + Why-sheet overlay + escape
  cascade (sheet > preview > hide).
- [`app/ui/launcher_v3/__init__.py`](../../app/ui/launcher_v3/__init__.py) —
  exports.

---

## Verification matrix

| Check                                                              | Result        |
|--------------------------------------------------------------------|---------------|
| `python -m pyflakes app/ui app/core api`                           | clean         |
| `python recall.py inspect` (usage)                                 | exits 2, prints usage |
| `python recall.py inspect WebSocket` (no events)                   | exits 1, prints "no candidate" card |
| `python recall.py trust review`                                    | prints 14-day ledger card |
| `bad_recoveries.record` rejects unknown `reason`                   | yes           |
| `bad_recoveries.thread_is_flagged` honours the 14-day window       | yes           |
| `RecoveryCardV3(signals=[...])` shows *Why this?* link             | yes           |
| `RecoveryCardV3(signals=[])` hides the link                        | yes           |
| `WhyThisSheet` paints inside the launcher window                   | yes (capture) |
| Showcase capture has exactly one hero                              | yes           |
| Ledger-demoted capture suppresses the hero                         | yes           |

---

## Success criterion

> User says: *"Yes. That is exactly what I wanted back."*

Three things have to be true for that sentence to land:

1. The hero must be the topic the user *was* working on (not a
   plausible neighbour). Phase 6Q codified the 7 rules + the
   9 gates that make this deterministic.
2. The launcher must show *why* it picked this without
   hand-waving. Phase 6Q's *Why this?* sheet renders only
   pure engine signals; the launcher cannot make anything up.
3. When the engine is wrong, the user can teach it. Phase 6Q's
   ledger + the `recall trust review` rates give the user
   both a way to flag a wrong recovery *and* a way to see
   how often the engine is right.

All three land in this phase.
