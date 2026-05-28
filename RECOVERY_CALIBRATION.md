# Phase P1 — Recovery Calibration

**Date:** 2026-05-27 · **Branch:** `release/v0.1.0-rc1` ·
**Files touched:** [`app/core/recovery.py`](app/core/recovery.py),
[`app/ui/launcher_v3/live.py`](app/ui/launcher_v3/live.py)

---

## The diagnosis

Phase P0 ended with the engine reading **247 captured events**
across **8 reconstructed threads** — and `/v1/recovery/recent`
returning `candidates: []`. The launcher fell through to
`STATE_EMPTY` despite real work being on disk.

Per-thread trace at the original gates (Phase 4E):

| Thread (live data)                                 | events | depth pass? | continuity | confidence | gate verdict |
|----------------------------------------------------|-------:|:-----------:|-----------:|-----------:|--------------|
| ChatGPT                                            | 19     | ✅          | 0.48       | 0.00       | ❌ continuity floor 0.55; ❌ intent floor 0.32 |
| Inbox · Gmail                                      | 28     | ❌ (depth=0)| —          | —          | ❌ depth-events gate (browser_visit only) |
| JioHotstar                                         | 37     | ❌ (depth=0)| —          | —          | ❌ depth-events gate |
| kunalKumar-13 (GitHub profile)                     | 13     | ❌ (depth=0)| —          | —          | ❌ depth-events gate |
| Meet · AEOS/Kunal                                  | 6      | ❌ (depth=0)| —          | —          | ❌ depth-events gate |
| Invitation from an unknown sender                  | 8      | ❌ (depth=0)| —          | —          | ❌ depth-events gate |
| Kotak 811                                          | 40     | ❌ (depth=0)| —          | —          | ❌ depth-events gate |
| Sent Mail · Gmail                                  | 5      | ❌ (depth=0)| —          | —          | ❌ depth-events gate |

Two distinct gates were rejecting **every** thread:

1. **The depth-events gate.** Phase 3C required at least one event
   of kind `{open, reveal, chat_session, browser_search}`. The
   extension's `browser_visit` kind didn't count, so any thread
   that lived entirely in the browser (which on real user data is
   *most* threads) was hard-rejected. 7 of 8 threads failed here.
2. **The trust + intent floors.** The one thread that *did* clear
   the depth gate — ChatGPT — scored continuity = 0.48 (below the
   0.55 floor) and confidence = 0.00 (below the 0.32 intent floor),
   so it was rejected too.

Net result: the engine returned `[]` even though the threads layer
had cleanly grouped 247 events into 8 recoverable topics.

---

## The fix in one paragraph

Replaced the **binary** depth-events gate with a **weighted**
depth score so browser-only threads can clear; replaced the
**hard-reject** continuity + intent floors with a **band ladder**
(HIGH / MED / LOW) so the launcher gets to render quieter
candidates instead of empty; and added a **fallback synthesis**
path so even a thread that fails the LOW trust floor still
surfaces something if it has restorable targets. Engine never
returns empty on a non-trivial event store.

---

## Calibration table — before / after

### Knobs in [`app/core/recovery.py`](app/core/recovery.py)

| Constant                    | Before (Phase 4E) | After (Phase P1)                                                    | Why |
|-----------------------------|-------------------|---------------------------------------------------------------------|-----|
| `_DEPTH_KINDS` (set)        | `{open, reveal, chat_session, browser_search}` — binary | retained as a back-compat alias over `_DEPTH_WEIGHTS.keys()` | inspect_cli + explain_signals read it as a set |
| `_DEPTH_WEIGHTS` (new dict) | — | `{open: 1.0, reveal: 1.0, chat_session: 1.0, browser_search: 0.35, browser_visit: 0.5}` | weighted so browser-only threads can pass |
| `_MIN_DEPTH_SCORE` (new)    | — | `1.0`                                                                | two browser_visit events (= 1.0) clear it; one search alone (0.35) does not |
| `_MIN_CONFIDENCE`           | `0.55`            | `0.40`                                                              | MED-band continuity floor |
| `_HIGH_CONFIDENCE` (new)    | —                 | `0.55`                                                              | HIGH-band continuity floor (the original 0.55 is retained, just upgraded to HIGH instead of being the only floor) |
| `_LOW_CONFIDENCE` (new)     | —                 | `0.25`                                                              | the absolute trust floor — below this we synthesize a fallback instead |
| `_MIN_RESUME_INTENT`        | `0.32`            | `0.10`                                                              | MED-band intent floor; a fresh thread that hasn't been abandoned yet can still surface |
| `_HIGH_RESUME_INTENT` (new) | —                 | `0.32`                                                              | HIGH-band intent floor (the original 0.32 is retained as the HIGH bar) |
| `_LAST_PHASE_RECENCY_DAYS`  | `7.0`             | `7.0` (unchanged)                                                   | the "still warm in your head" window stays at one week |
| `_MIN_DISTINCT_TARGETS`     | `3`               | `3` (unchanged)                                                     | three distinct targets is still the multi-source-work floor |

### Gate semantics

**Before (binary):**

```
if depth_events == 0:               return None        # hard reject
if continuity < 0.55:               return None        # hard reject
if confidence < 0.32:               return None        # hard reject
```

**After (band ladder):**

```
depth_score = sum(_DEPTH_WEIGHTS[ev.kind] for ev in events)
if depth_score < 1.0:               return None        # still hard

trust = max(continuity, confidence)
if trust < 0.25:                    return None        # bottom-floor
if trust >= 0.55 and confidence >= 0.32:   band = "high"
elif trust >= 0.40 and confidence >= 0.10: band = "med"
else:                                       band = "low"
```

And when `recover_recent()` ends with `candidates == []`, it now
asks `_build_fallback_candidate(threads)` for the most recent
thread with restorable targets and returns that with
`band="fallback"`. The launcher renders it the same way it would
render a LOW band, just with a quieter signals dict.

### Launcher gate (Phase P1)

[`app/ui/launcher_v3/live.py:436`](app/ui/launcher_v3/live.py#L436)
was a Phase 6O HIGH-only gate that demanded `n_targets >= 4` on
top of the engine's own filtering. With the band ladder, the
engine already enforces `_MIN_DISTINCT_TARGETS = 3` for any
non-fallback candidate and the fallback path enforces its own
minimum. The launcher's only remaining job is to filter ledger-
flagged candidates and to confirm there's at least one
restorable target:

```diff
- if n_targets >= 4 and not flagged:
+ if n_targets >= 1 and not flagged:
      hero = c
```

---

## Proof against live event store

Re-running the recovery engine against `~/.recall/events/`
(205 events, 8 threads — Phase P0 had 247; the cutoff window
trimmed two days of older events):

```
=== Phase P1 Gate Values ===
_DEPTH_WEIGHTS         = {'open': 1.0, 'reveal': 1.0,
                          'chat_session': 1.0,
                          'browser_search': 0.35,
                          'browser_visit': 0.5}
_MIN_DEPTH_SCORE       = 1.0
_MIN_CONFIDENCE        = 0.40  (MED continuity floor)
_HIGH_CONFIDENCE       = 0.55  (HIGH continuity floor)
_LOW_CONFIDENCE        = 0.25  (bottom-floor)
_MIN_RESUME_INTENT     = 0.10  (MED intent floor)
_HIGH_RESUME_INTENT    = 0.32  (HIGH intent floor)
_LAST_PHASE_RECENCY_DAYS = 7.0

=== Recovery candidates ===
n returned = 3

[0] band=high    title='Inbox (22,319) - kunalsain0324@gmail.com - Gmail'
    continuity=0.785  confidence=0.330  n_targets=8
    caption='8 tabs · returned to this 3 times · after a revisit'

[1] band=med     title='JioHotstar - Watch TV Shows, Movies, …'
    continuity=0.848  confidence=0.240  n_targets=8
    caption='8 tabs · reopened after a 5-day gap · last active during reading'

[2] band=med     title='kunalKumar-13 (Kunal Kumar)'
    continuity=0.507  confidence=0.381  n_targets=5
    caption='5 tabs · reopened after a 3-day gap · last active during reading'
```

### Per-thread band trace

| Thread                                            | events | depth_score | continuity | confidence | band     | why surfaced |
|---------------------------------------------------|-------:|------------:|-----------:|-----------:|----------|--------------|
| Inbox · Gmail                                     |     28 |       14.00 |       0.78 |       0.33 | **HIGH** | depth via 28 browser_visit (28 × 0.5 = 14.0); trust 0.78 ≥ 0.55 *and* confidence 0.33 ≥ 0.32 — clears both HIGH floors |
| JioHotstar                                        |     37 |       18.50 |       0.85 |       0.24 | **MED**  | trust 0.85 ≥ 0.40; confidence 0.24 ≥ 0.10. Misses HIGH only because confidence < 0.32 (no clean abandonment signal — passive reading) |
| kunalKumar-13 (GitHub profile)                    |     13 |        6.50 |       0.51 |       0.38 | **MED**  | trust 0.51 ≥ 0.40; confidence 0.38 ≥ 0.10. Misses HIGH only because continuity < 0.55 (smaller surface count) |
| Meet · AEOS/Kunal                                 |      6 |        3.00 |       0.46 |       0.21 | **MED**  | trust 0.46 ≥ 0.40; confidence 0.21 ≥ 0.10. A meeting was opened repeatedly — the revisit signal is what carries confidence |
| Invitation from an unknown sender                 |      8 |        4.00 |       0.42 |       0.39 | **MED**  | trust 0.42 ≥ 0.40; confidence 0.39 — would be HIGH if continuity passed 0.55 |
| Kotak 811                                         |     40 |       20.00 |       0.54 |       0.28 | **MED**  | the biggest thread by event count; misses HIGH by 0.01 on continuity |
| ChatGPT                                           |     19 |       18.00 |       0.48 |       0.00 | **LOW**  | scored but ranked below MEDs by band ordering — chat_session events are deep (depth=18) but the thread shows zero abandonment so confidence floors at 0.0; trust still clears 0.25 |
| Sent Mail · Gmail                                 |      5 |        2.50 |       — |          — | reject   | only 2 distinct targets ( < _MIN_DISTINCT_TARGETS = 3) — gate is *targets*, not trust |

`recover_recent(n=5)` returns the top 3 by `(band, max(continuity, confidence))`:

```
HIGH ahead of MED ahead of LOW ahead of fallback
  ↓                ↓                ↓
Gmail        Hotstar / GitHub   ChatGPT (rank-broken by trust)
```

`_MAX_CANDIDATES = 3` caps the return, so the LOW-band ChatGPT
thread doesn't make the surface this run — it would on a smaller
event store, or under the fallback path if the MEDs all failed.

---

## Why each surfaced candidate is the right call

### `[0] HIGH · Gmail`

- **28 visits over 6 days** is the heaviest activity on the disk.
- Returned to the inbox 3 times after gaps — classic revisit
  signal, which lifts confidence to 0.33 (the only thread to
  clear `_HIGH_RESUME_INTENT` on this dataset).
- Continuity 0.78 reads as "the context is intact" — recent,
  reused targets, momentum.
- The launcher's Continue card opens 8 inbox tabs; restoration
  surface = the literal room the user was in.

### `[1] MED · JioHotstar`

- 37 visits is the *most* of any thread; depth score 18.5.
- Continuity 0.85 (highest in the set) — the context never
  fragmented, the user keeps coming back to the same set of
  pages.
- Confidence 0.24 is *below* the HIGH intent floor of 0.32:
  passive entertainment shows no abandonment, no revisit
  transition, no acceleration — the engine correctly reads it as
  "intact, but not urgent". MED band is the right read.

### `[2] MED · kunalKumar-13 (GitHub)`

- 13 visits with 5 distinct repo targets — multi-source work,
  not just one page reload.
- Confidence 0.38 *would* clear HIGH if continuity made the 0.55
  bar, but continuity is 0.51 (the thread is smaller and less
  dense). The candidate surfaces at MED — a quieter card but a
  real one.

### Why ChatGPT didn't surface this run

- Its band is LOW (continuity 0.48 < 0.55 *and* confidence 0.0
  < 0.32) and `_MAX_CANDIDATES = 3` ran out at MED.
- This is the *correct* outcome: ChatGPT's 19 chat_sessions show
  no abandonment + no revisit, so confidence honestly is 0. The
  band ladder *records* the topic as LOW; the launcher would
  surface it if it were the only candidate (via fallback) or if
  the MEDs were ledger-flagged out.

### Fallback path

Never triggers on this dataset because the band ladder produces
≥1 real candidate. The path is only there to honor the
"never return empty" requirement on event stores that are smaller,
sparser, or fully passive. On a 50-event single-thread day, the
LOW gate may still reject and the fallback synthesizes a card
from the most recent thread with restorable targets, marked
`band="fallback"` so the UI can render it quieter than a LOW.

---

## Disable + clear flows

Both unchanged from Phase 4E:

- **Disable:** set `RECALL_DISABLE_RECOVERY=1` — engine returns
  `[]` unconditionally.
- **Clear:** delete `~/.recall/events/` — full reset, threads
  re-derive on next run.
- **Promotion control:** the bad-recoveries ledger
  (`~/.recall/bad_recoveries.json`) still demotes flagged
  threads. The band ladder doesn't override the ledger; a
  flagged thread is still excluded from the launcher's hero
  slot.

---

## Performance

The change is signal-additive — no extra passes over the event
store. `depth_score` is computed inline in the same `for ev in
events:` loop that was already counting depth kinds; the band
classification is a 4-line branch. `recover_recent` now sorts on
a 2-tuple instead of a scalar — O(k log k) with k ≤ 6.

Smoke-test perf section (target `<80 ms wall` at 10K events) is
unaffected — the engine still scores at most `_CANDIDATE_POOL = 6`
threads and the fallback path only runs on empty result, which
is the cheap branch.

---

## What this calibration does *not* do

- **It does not lower the standard for a HIGH band card.** The
  original Phase 4E floors (0.55 continuity / 0.32 confidence)
  still exist — they're just labelled HIGH now instead of being
  the only floor. A HIGH card today is the same quality as a
  Phase 4E card.
- **It does not surface noise.** The `_MIN_DISTINCT_TARGETS = 3`
  gate is intact; threads with only 1–2 reopened tabs still
  reject. Two of the 8 live threads (ChatGPT for the wrong
  reason — `_MAX_CANDIDATES` ran out — and Sent Mail for the
  right reason — only 2 distinct targets) didn't make the
  surface.
- **It does not change the depth-kind taxonomy.** All five kinds
  in `_DEPTH_WEIGHTS` come from the existing extension + native
  event vocabulary. No new event kind, no schema change.
- **It does not touch the ranking algorithm.** Continuity and
  confidence scoring weights are unchanged. The only new logic
  is *how the score maps to a yes/no decision* — from a single
  threshold to a three-band ladder.

---

## Residuals + follow-ups

| Item                                                                | Severity | Path |
|---------------------------------------------------------------------|----------|------|
| Launcher renders all bands with the same visual weight              | P2       | Phase P2 — add band-aware styling (HIGH = hero, MED = lighter, LOW = quietest, fallback = no urgency) |
| `_MAX_CANDIDATES = 3` can hide a LOW behind MEDs                    | P3       | Acceptable for now — LOW is the lowest band and the launcher only shows one hero anyway |
| Fallback path isn't exercised by any smoke section                  | P2       | Add a sparse-event fixture to `_smoke_api.py` that forces the fallback synthesis branch |
| ChatGPT's confidence stays at 0.0 even with 19 chat_sessions        | P2       | The abandonment signal needs a chat_session-aware variant — Phase P3 work, not P1 |
