# Investigation Principles — Phase 6Q

How Recall decides what counts as *the work the user was doing*,
and what it refuses to surface. The directive: **make Recall feel
correct**. Not pretty. Not bigger. Correct.

This document is the working contract between the engine and the
launcher. The engine's job is to honour every rule below; the
launcher's job is to show *exactly* what the engine returns and
nothing else.

> An investigation is not a sum of clicks. It is a coherent
> period of *mental work* on a topic the user has not yet
> finished.

---

## The seven rules

### 1. Same topic returns → **merge**

If the user touches the same `topic_key` across multiple
sessions, the threads layer merges them into one investigation.
The user thinks of *the WebSocket bug* — not *Monday's WebSocket
bug and Wednesday's WebSocket bug*. The engine matches.

Lives in: [`threads.py:ThreadBuilder.events_for_topic`](../../app/core/threads.py).

### 2. One-off visit → **suppress**

A single browser visit + close is *consumption*, not *work*.
Until a topic accumulates either (a) ≥ 4 distinct events, or
(b) ≥ 3 distinct targets, it does not exist as an investigation.

Floors in [`recovery.py`](../../app/core/recovery.py):
- `_MIN_EVENTS = 4`
- `_MIN_DISTINCT_TARGETS = 3`

### 3. Passive browsing → **suppress**

A thread that is *only* `browser_visit` events with no
`open`, `reveal`, `chat_session`, or `browser_search` is reading
material. The user did not act on it. It does not earn a recovery
card.

Floor: `_DEPTH_KINDS = {open, reveal, chat_session, browser_search}`.
A thread must contain at least one event whose `kind` is in
`_DEPTH_KINDS`, or it is suppressed.

### 4. Deep work → **promote**

The more surfaces engaged (browser + files + chats), the higher
the continuity score. Recall optimises for *what was I mentally
working on?* — a topic that pulled in files + a Claude session +
two search queries is the canonical investigation shape.

Driver: `_W_SURFACE_BREADTH = 0.15`, `s_surface = min(1.0, (len(surfaces) - 1) / 3.0)`.

### 5. Unfinished work → **strongest signal**

The strongest single tell that an investigation is recoverable is
*momentum that stopped abruptly*. The `_abandonment_score`
heuristic looks for:

- the last evolution phase had momentum ≥ 0.4 (real activity, not
  drift), AND
- activity stopped between 6 hours and 7 days ago.

Peak score lands around the 24-hour mark — the *overnight + next
day* gap is the most recoverable interruption shape there is.
Past 7 days the score returns to 0 (it's no longer *interrupted*,
it's *set aside*).

Weight: `_C_ABANDONMENT = 0.35` — the largest single weight in
the recovery-confidence formula.

### 6. Multi-day return → **boost**

If the user *deliberately came back* to a topic days later
(`reopened after a 2-day gap` signal in `_behavior_clause`), that
is the clearest return-intent signal the engine can see. Multi-day
returns are surfaced in the preview caption *with the gap stated*
so the user can verify against memory: *"reopened after a 2-day
gap"* not *"recurring topic"*.

Source: `_behavior_clause` in [`recovery.py`](../../app/core/recovery.py).

### 7. Casual reopen loops → **decay**

A user who reopens the same tab six times in five minutes is
*stuck*, not *iterating*. The `_unresolved_score` captures
repetition but the trust gates above keep noise out: a thread of
*"the user reopened the same URL six times"* fails the distinct-
target floor (rule 2) and never reaches the recovery surface.

A thread that survives the floors but consists of identical
opens scattered across days carries the *unresolved* signal,
which contributes only `0.15` to the confidence score — enough
to nudge a real investigation, never enough to elevate noise.

---

## Anti-noise gates (all must pass)

These are the *minimum bar* for a topic to be considered a
recovery candidate. The engine evaluates them top-to-bottom and
suppresses on the first failure.

| # | Gate                                | Lives in                               |
|---|-------------------------------------|----------------------------------------|
| 1 | Thread has ≥ `_MIN_EVENTS = 4`      | `recovery.py:_score_thread`            |
| 2 | Thread is ≤ `_RECOVERY_WINDOW_DAYS = 14` old | `recovery.py:_score_thread`     |
| 3 | Last evolution phase ≤ `_LAST_PHASE_RECENCY_DAYS = 7` | `recovery.py:_score_thread` |
| 4 | ≥ 2 surfaces (or ≥ 6 events on one) | `recovery.py:_score_thread`            |
| 5 | ≥ 1 event in `_DEPTH_KINDS`         | `recovery.py:_score_thread`            |
| 6 | ≥ `_MIN_DISTINCT_TARGETS = 3`       | `recovery.py:_score_thread`            |
| 7 | `max(continuity, confidence) ≥ 0.55`| `recovery.py:_MIN_CONFIDENCE`          |
| 8 | `recovery_confidence ≥ 0.32`        | `recovery.py:_MIN_RESUME_INTENT`       |
| 9 | At least one openable target        | `recovery.py:_suggested_targets`       |

A topic that passes all nine becomes a candidate. The top three
by `max(continuity, recovery_confidence)` are returned.

---

## Promotion bands

Once a candidate is returned, the launcher promotes it to one of
three bands based on how many *targets* it carries (`n_targets =
len(suggested_targets)`). The bands are documented in detail in
[`PROMOTION_THRESHOLDS.md`](PROMOTION_THRESHOLDS.md).

| Band | n_targets | Surface           |
|------|-----------|-------------------|
| LOW  | 0-1       | suppressed        |
| MED  | 2-3       | row only          |
| HIGH | 4+        | hero (Continue)   |

**`unfinished` overrides all** — a candidate with
`unresolved_signals` containing `"last phase had momentum X and
went quiet"` reaches the HIGH band even if it would otherwise sit
in MED. `returned_after_gap` boosts the band by +1 (MED → HIGH).
Duplicate visits within the same hour incur a penalty.

---

## What this document is for

When a user reports *"Recall surfaced the wrong thing"*, the
debugger walks these rules top to bottom and finds the one the
engine got wrong. When a contributor proposes a new scoring tweak,
the question is *"which of these seven rules does it serve?"* If
the answer is *none*, the tweak does not land.

The success criterion for Phase 6Q:

> User says: "Yes. That is exactly what I wanted back."

Not *plausible*. Not *interesting*. *Exact*.

---

## See also

- [`PROMOTION_THRESHOLDS.md`](PROMOTION_THRESHOLDS.md) —
  band rules + override logic.
- [`RESUME_FLOW.md`](RESUME_FLOW.md) — what happens after the
  user clicks Resume on a promoted candidate.
- [`SHOWCASE_TRUTH.md`](SHOWCASE_TRUTH.md) — the three-story
  scripted verification that *only one hero* surfaces at a time.
- [`app/core/recovery.py`](../../app/core/recovery.py) — the
  engine that implements every rule above.
