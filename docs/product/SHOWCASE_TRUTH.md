# Showcase Truth — Phase 6Q

A scripted three-investigation walk that verifies the
launcher surfaces *exactly* one hero — never two, never
none — and that the *Why this?* sheet reads as pure engine
signal, not prose.

> **Success criterion:** at the end of the walk, the tester
> says: *"Yes. That is exactly what I wanted back."*

---

## The three stories

The walk operates on three deliberately distinct topics so
the engine has to *choose* between them, not merge:

| #   | Topic                       | Shape                                 |
|-----|-----------------------------|---------------------------------------|
| 1   | Healthcare proposal draft   | open `notes.md` + browse YC tab       |
| 2   | RLHF notes                  | `browser_search` + `browser_visit`    |
| 3   | WebSocket retry debugging   | 2 files + 2 tabs + 1 chat + 1 search  |

Stories 1 and 2 are deliberately *under* the HIGH bar
(`n_targets < 4`) so they will *not* steal the hero slot. Story
3 has 5 distinct targets across browser + files + chat — the
canonical HIGH-confidence investigation.

The expectation: **only WebSocket gets the hero**; the other two
appear in OTHER WORK as bare titles.

---

## Steps

1. **Reset state.** Optional. Delete `~/.recall/bad_recoveries.jsonl`
   if you want a clean slate. Existing events stay; only the
   feedback ledger is cleared.

2. **Live in the three topics, then walk away.**

   Story 1:

   ```
   - open ~/Documents/healthcare-startup/notes.md
   - browse https://www.ycombinator.com/companies (healthcare filter)
   ```

   Story 2:

   ```
   - google "rlhf reward shaping"
   - read https://arxiv.org/abs/2203.02155
   ```

   Story 3:

   ```
   - google "websocket backoff jitter"
   - read https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
   - open ~/code/ws-retry/backoff.py
   - open ~/code/ws-retry/client.py
   - chat with claude.ai about backoff strategies
   ```

3. **Leave for ≥ 6 hours and ≤ 7 days.** This is the
   `_abandonment_score` sweet spot (peaks at the 24-hour mark
   per `recovery.py`). The overnight + next-day gap is the
   most recoverable interruption shape there is.

4. **Return. Open the launcher.**

   The expectation:

   ```
   CONTINUE
     WebSocket retry debugging          [ Resume ]   Why this?
     2 tabs - 2 files - reopened 2d ago

   OTHER WORK
     Healthcare proposal | RLHF notes | WebSocket retry debugging
   ```

   See the capture at
   [`assets/screenshots/launcher-truth/showcase.png`](../../assets/screenshots/launcher-truth/showcase.png).

5. **Click *Why this?*** A small sheet appears centred over
   the hero:

   ```
   SHOWN BECAUSE
     - unfinished work
     - returned after a 2-day gap
     - 5 targets involved
     - multiple surfaces engaged
   ```

   Pure engine signals. No AI text. No scoring numbers. The
   lines come from `recovery.explain_signals(candidate)` and
   nothing else.

   Capture:
   [`why_sheet.png`](../../assets/screenshots/launcher-truth/why_sheet.png).

6. **Verify the three invariants.**

   | Invariant                                                    | How to check                       |
   |--------------------------------------------------------------|-------------------------------------|
   | Only one hero is rendered                                    | inspect: hero slot has exactly 1 card |
   | The hero's title matches the strongest investigation         | `recall inspect <id>` returns `SHOW HERO` |
   | The two non-hero topics sit in OTHER WORK, not in the hero   | both appear as bare titles in the row |

7. **Confirm via the inspector.**

   ```
   recall inspect WebSocket
   ```

   Expected output:

   ```
     ------------------------------------------------------------
       Investigation
     ------------------------------------------------------------

       Title:
         WebSocket retry debugging

       Strength:
         HIGH

       Signals:
         - unfinished work
         - returned after a multi-day gap
         - 5 targets involved
         - multiple surfaces engaged

       Evidence:
         - 2 files
         - 1 chat
         - 2 tabs
         - 1 search

       Decision:
         SHOW HERO

     ------------------------------------------------------------
   ```

   And for the other two:

   ```
   recall inspect "Healthcare proposal"   -> Strength: MED · Decision: SHOW IN OTHER WORK
   recall inspect "RLHF"                  -> Strength: LOW · Decision: SUPPRESS
   ```

   (LOW topics may not appear in `recall inspect` at all if they
   fail the gate floors — see `INVESTIGATION_PRINCIPLES.md`.)

---

## Failure modes the showcase rules out

Each row below is a *real* class of failure the showcase
exists to catch. If any of these happen, do not ship.

| Failure                                          | Indicator                                  |
|--------------------------------------------------|---------------------------------------------|
| Two heroes surface                               | hero slot has 2 cards stacked              |
| Wrong topic surfaces as hero                     | hero title isn't WebSocket                 |
| No hero when WebSocket clearly qualified         | `_show_empty()` was called                 |
| *Why this?* renders prose ("The user seems to have…") | overlay has any line not from `explain_signals` |
| Hero is shown for a flagged thread               | ledger flag is ignored                     |
| OTHER WORK shows duplicate of the hero           | same `topic_key` rendered twice            |

The directive: **make Recall feel correct**. Each of those
failures breaks that promise.

---

## The ledger demotion path

The showcase also covers the user-feedback override:

1. With the WebSocket hero showing, click the (future)
   *Wrong recovery* control and choose `noise`.
2. The launcher writes
   `{"id": "...", "thread_id": "...", "reason": "noise", "ts": 1747...}`
   to `~/.recall/bad_recoveries.jsonl`.
3. Refresh the launcher. The WebSocket hero is gone; only
   OTHER WORK remains.

   Capture:
   [`ledger_demoted.png`](../../assets/screenshots/launcher-truth/ledger_demoted.png).

4. Run `recall trust review`. The ledger shows the entry and
   the bad % rate is non-zero.

The hero stays demoted for **14 days** (`_LEDGER_WINDOW_DAYS`),
giving the engine time to either improve or for the user to
forget. After 14 days the demotion lifts.

---

## What this proves

- Same events in → same hero out (deterministic).
- Only one hero at a time, by design.
- Every signal the launcher displays comes from the engine's
  pure-functional `explain_signals`. There is no second-source
  of truth.
- The launcher honours user feedback (`bad_recoveries.jsonl`)
  by demoting flagged threads.

If anywhere the showcase diverges from this document, treat
it as a regression. Fix the engine — never the launcher.

---

## See also

- [`INVESTIGATION_PRINCIPLES.md`](INVESTIGATION_PRINCIPLES.md)
  — the seven rules behind the ranking.
- [`PROMOTION_THRESHOLDS.md`](PROMOTION_THRESHOLDS.md) — the
  HIGH/MED/LOW band rules + the five overrides.
- [`RESUME_FLOW.md`](RESUME_FLOW.md) — what happens after the
  user clicks Resume on the hero.
- [`app/core/inspect_cli.py`](../../app/core/inspect_cli.py) —
  the `recall inspect` source.
- [`app/core/trust_cli.py`](../../app/core/trust_cli.py) —
  the `recall trust review` source.
