# Promotion Thresholds — Phase 6Q

How the launcher decides whether a candidate is:

- **HIGH** — gets the hero card (CONTINUE), the Resume button,
  and the `1` keyboard shortcut.
- **MED** — appears in the OTHER WORK row but never as a hero.
- **LOW** — suppressed entirely.

The bands are *not* a model score — they are a deterministic
function of how many one-click targets the engine surfaced + a
small set of override signals.

---

## The bands

| Band | `n_targets` | Surface             | Why                                       |
|------|-------------|---------------------|-------------------------------------------|
| LOW  | 0-1         | suppressed          | one target is a bookmark, not an investigation |
| MED  | 2-3         | row only            | a context worth glancing at, not strong enough to *lead* with |
| HIGH | 4+          | hero, Resume CTA    | enough targets to *re-enter the room*     |

`n_targets = len(candidate.suggested_targets)`. The launcher reads
this directly in [`live.py:_populate_digest`](../../app/ui/launcher_v3/live.py)
and routes the candidate accordingly.

---

## Override rules

The base band is computed from `n_targets`. Five overrides can
push a candidate up or down a band:

### Override 1 — **unfinished overrides all**

If `candidate.unresolved_signals` contains a *"last phase … went
quiet"* line (the abandonment signal from `recovery._explain`),
the candidate promotes to **HIGH** regardless of target count.
The semantic: *we caught the user mid-flow with the context still
warm in their head*. A weaker target count doesn't change that
fact.

### Override 2 — **returned_after_gap boosts +1**

If `preview_caption` contains a `*reopened after a N-day gap*`
clause (see `recovery._behavior_clause`), the band is promoted
by one step: `LOW → MED`, `MED → HIGH`.

The reasoning: a *deliberate return after days* is the strongest
return-intent signal we can read. The user has already told the
engine "I'm coming back to this".

### Override 3 — **duplicate penalty**

If two candidates share the same `thread_id` *or* differ only by
target order (e.g., a second candidate that contains a proper
subset of the first's targets), the lower-ranked one is dropped
entirely. We never surface two cards for the same investigation.

### Override 4 — **noise penalty**

A candidate whose `recovery_confidence < _MIN_RESUME_INTENT`
(0.32) is suppressed entirely. This is enforced *inside* the
engine; the launcher never sees these candidates. Still listed
here so the contract is in one place.

### Override 5 — **ledger penalty**

If `~/.recall/bad_recoveries.jsonl` carries a `bad_recovery` entry
for the candidate's `thread_id` within the last 14 days, the band
is **demoted one step** (HIGH → MED, MED → LOW). The user told us
the recovery was wrong; we listen.

This is the only override that incorporates user feedback. It
lives in [`bad_recoveries.py`](../../app/core/bad_recoveries.py).

---

## Worked examples

### Example 1 — the canonical WebSocket

```
n_targets = 5        (2 files + 2 tabs + 1 search)
unresolved = "last phase (implementation) had momentum 0.61 and went quiet"
preview    = "2 tabs · 2 files · reopened after a 2-day gap · last active during implementation"
ledger     = clean
```

Base band: HIGH (5 ≥ 4). Override 1 confirms HIGH. Override 2
would promote MED → HIGH but it's already HIGH. **Final: HIGH.**

### Example 2 — the bookmark that isn't an investigation

```
n_targets = 1
unresolved = []
preview    = "1 tab · last active during research"
ledger     = clean
```

Base band: LOW (1 ≤ 1). No overrides apply. **Final: LOW
(suppressed).** The launcher shows nothing.

### Example 3 — the just-glanced thread

```
n_targets = 2
unresolved = []
preview    = "1 tab · 1 chat · last active during discussion"
ledger     = clean
```

Base band: MED. No overrides. **Final: MED.** Surfaces in OTHER
WORK; no hero, no Resume button.

### Example 4 — the wrong recovery the user marked

```
n_targets = 4
unresolved = ["last phase (research) had momentum 0.55 and went quiet"]
preview    = "3 tabs · 1 file · last active during research"
ledger     = bad_recovery on thread_id "abc" 3 days ago
```

Base band: HIGH. Override 1 confirms HIGH. Override 5 demotes
HIGH → MED. **Final: MED.** The launcher learned.

---

## Why these numbers

| Number              | Reason                                                                     |
|---------------------|----------------------------------------------------------------------------|
| HIGH at 4 targets   | Below 4, the *Will reopen* preview row is too short to feel like a context. *3 tabs* alone is a recommendation; *4 tabs · 2 files* is a room you re-enter. |
| MED at 2-3 targets  | Two distinct artefacts are the minimum for "I was juggling two things"; three is plenty. |
| LOW at 0-1 targets  | A single target is a bookmark, not work. The user can find it via search. |
| 14-day ledger window| Short enough to forget transient false positives once the engine improves; long enough to suppress a topic the user *clearly* doesn't want back. |

---

## What the launcher never does

- **Never invents a promotion.** A candidate the engine returns
  as LOW is never bumped to MED in the UI.
- **Never reorders by guess.** The launcher renders candidates in
  the order the engine returned them.
- **Never shows two heroes.** Even when two HIGH candidates exist,
  the launcher takes the first and the second falls to OTHER
  WORK.

The launcher is a strict consumer of the engine's decisions. If
the wrong thing surfaces, the bug is in the engine — fix it there.

---

## See also

- [`INVESTIGATION_PRINCIPLES.md`](INVESTIGATION_PRINCIPLES.md) —
  the seven rules that decide what becomes a candidate at all.
- [`app/core/recovery.py`](../../app/core/recovery.py) — engine.
- [`app/core/bad_recoveries.py`](../../app/core/bad_recoveries.py)
  — the ledger that drives Override 5.
- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
  — the launcher's HIGH-only gate.
