# archive/recovery-ranking/

Phase 6Q's *Continuity Truth* audit paper trail. The 6Q
directive shipped:

1. The 7 [investigation principles](../../docs/product/INVESTIGATION_PRINCIPLES.md)
   as the working contract.
2. The 5 [promotion-threshold overrides](../../docs/product/PROMOTION_THRESHOLDS.md)
   (unfinished, returned-after-gap, duplicate, noise, ledger).
3. The [`bad_recoveries.jsonl`](../../app/core/bad_recoveries.py)
   ledger + Override 5 demotion.
4. The [`recall inspect`](../../app/core/inspect_cli.py) +
   [`recall trust review`](../../app/core/trust_cli.py) CLIs.
5. The deterministic
   [`explain_signals()`](../../app/core/recovery.py) helper +
   the [*Why this?* sheet](../../app/ui/launcher_v3/why_sheet.py).

This folder documents what the *pre-6Q* ranking carried that
6Q either kept, demoted, or considered and rejected.

---

## What 6Q kept untouched

- The trust gates in `recovery._score_thread` (events ≥ 4,
  recovery window 14 d, last-phase recency 7 d, depth-kind
  floor, distinct-target floor, `_MIN_CONFIDENCE = 0.55`,
  `_MIN_RESUME_INTENT = 0.32`). These are the gates that
  define what *becomes* a candidate at all and they survived
  intact.
- The continuity / confidence weights
  (`_W_RECENCY`, `_W_TARGET_REUSE`, …, `_C_ABANDONMENT`, …).
  No weight changed in 6Q.
- The `_behavior_clause` preview-caption generator. Same
  inputs in, same captions out.
- The `_classify_targets` bucket helper. Files/chats/tabs/
  searches still bucketed the same way.

---

## What 6Q added (not deleted)

| Surface                       | Source                                          |
|-------------------------------|-------------------------------------------------|
| `signals.ledger_flagged`      | `RecoveryEngine._score_thread`                  |
| `explain_signals(candidate)`  | `recovery.py` (deterministic, pure)             |
| Override 5 (ledger demotion)  | `LiveLauncher._populate_digest`                 |
| *Why this?* link + sheet      | `RecoveryCardV3` + `WhyThisSheet`               |
| `recall inspect <id>` CLI     | `app/core/inspect_cli.py`                       |
| `recall trust review` CLI     | `app/core/trust_cli.py`                         |
| `bad_recoveries.jsonl` ledger | `app/core/bad_recoveries.py`                    |

---

## What 6Q considered and rejected

### 1. A learned ranker

> *"Train a small model on user feedback and let it re-rank
> recoveries."*

**Rejected.** Three reasons:

- The CLAUDE.md charter is explicit: *"No randomness, no
  learned weights, no probabilistic assignment in any
  production path."* A model would break the determinism
  guarantee.
- A model trained on `bad_recoveries.jsonl` would have N
  on the order of dozens for an alpha user — vastly
  insufficient signal.
- The user-facing benefit ("the launcher learns from your
  feedback") is delivered by the deterministic Override 5
  *without* any of the determinism cost.

### 2. A "freshness" half-life

> *"Apply an exponential half-life to a thread's score so
> stale threads decay."*

**Rejected.** Already covered by `_RECOVERY_WINDOW_DAYS = 14`
+ `_LAST_PHASE_RECENCY_DAYS = 7` + the `_RECENCY_HALFLIFE_DAYS`
inside the continuity score. Adding *another* decay layer
would compound the suppressions and starve recoveries.

### 3. A "promotion bump" for chat-heavy threads

> *"Chats are the strongest 'work that mattered' signal —
> boost threads with chat events."*

**Rejected.** Surface breadth already rewards chat presence
via `_W_SURFACE_BREADTH`. Adding a second per-surface bump
would double-count. The 6Q principles doc names this
explicitly: *deep work → promote* (rule 4) is one signal,
not two.

### 4. A "duplicate" engine-side de-dup pass

> *"Two candidates whose target sets overlap > 80 % should
> merge."*

**Considered, deferred.** The current engine already returns
at most 3 candidates and the launcher only renders 1 hero —
the duplicate problem is bounded. If it ever surfaces in
practice, the right home is
[`recovery.py:recover_recent`](../../app/core/recovery.py),
not the launcher.

---

## How this folder evolves

When a future phase removes a ranking experiment, drop a
short rationale here. The folder is the audit trail for
*how* Recall's ranking became what it is — same shape as
[`archive/launcher-overbuild/`](../launcher-overbuild) and
[`archive/resume-old/`](../resume-old).
