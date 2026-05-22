# RETURN_BEHAVIOR.md — what a *return* is, in detail

The single most important signal for a continuity layer is
whether the user **came back**. Phase 6F adds the layer that
counts returns; this page is the precise semantic — what counts,
what does not, why the threshold is what it is, and how the
return signal travels through the rest of the system.

Pairs with [`DAILY_LOOP.md`](DAILY_LOOP.md) (the broader layer
this lives inside).

---

## The definition

A **return** is an ingest event whose timestamp is at least 30
minutes after the previous ingest event on this machine.

Three things to note:

1. **It is an *ingest* event** — not a launcher open, not a
   popup query. The user must have produced something in the
   browser / file system for a return to count. Idling with the
   launcher visible does not register.
2. **It is a *machine-local* gap** — not a thread gap, not a
   topic gap. The detector keeps a single `last_event_ts` and
   compares to it.
3. **30 minutes** — matches the session reconstructor's
   30-minute idle break. The two layers agree on what *left the
   desk* means; if you change one threshold, change both.

---

## The state file

`~/.recall/daily_loop_state.json` carries three keys:

```jsonc
{
  "last_event_ts":   1742934621.0,   // epoch seconds, the most recent event
  "last_return_ts":  1742928000.0,   // epoch seconds, the most recent return
  "last_return_gap_s": 47521.0       // seconds between last_event_ts and the event before it
}
```

This is a *fast-path cache*, not a source of truth. If the file
is missing, the next ingest is treated as the first event ever
seen — and no return is counted. The detector re-warms within
one event.

---

## The flow

```
POST /v1/events/{kind}
   |
   v
ingestion.ingest_typed(kind, payload)         ← engine layer
   |  ok
   v
_post_ingest_hook(ok=True)                    ← in api/main.py
   |
   v
demo_mode.mark_real_activity()                ← Phase 6D
   |
   v
daily_loop.mark_event(ts=time.time())         ← Phase 6F
       |
       v
   gap >= 30 min?  ── yes ──> bump `returns`, write last_return_ts
       |
       no
       |
       v
   write last_event_ts only
```

Every successful ingest goes through this hook. The hook is in
`api/main.py`, not in the engine layer — so deleting the hook
removes the return counter without touching events / sessions /
threads / recovery.

---

## What does NOT count as a return

A few cases the rule deliberately excludes:

- **First event ever.** No `last_event_ts` to compare against.
  The detector silently swallows the first event and starts
  counting from the second one.
- **An ingest race.** Two events on the same `time.time()` tick
  — the gap is zero, the threshold is not crossed.
- **A delayed event.** If the daemon dropped offline for an hour
  and then ingests a burst of buffered events, only the *first*
  of the burst crosses the threshold; the rest are within 30 s
  of each other.
- **A demo overlay event.** Demo mode never writes engine
  events. The demo overlay's `Show example` button does not
  produce a return.
- **A clock change.** If `last_event_ts` is *ahead* of `ts` (the
  user changed the system clock backward), the gap is negative
  and the detector treats it as "no return" — same outcome as
  the ingest race.

---

## Why 30 minutes

Three reasons:

1. **The session reconstructor already uses 30 min** as its idle
   break (`SESSION_GAP_MAX_SECONDS`). The two layers share a
   single definition of "left the desk" so a return and a new
   session line up.
2. **Sub-30-min "returns" are mostly tab-switches.** A user who
   alt-tabs to a different app for 12 minutes and comes back has
   not really *returned* — they are in the middle of a single
   working block.
3. **30+ minute gaps line up with how breaks actually feel.**
   Coffee, a meeting, lunch, end-of-day. The intuition the
   metric tracks is "I went away, and I came back."

A lower threshold (e.g. 10 min) is easy to plumb if a future
surface decides it's measuring something different — the
constant lives in `app/core/daily_loop.py` as
`RETURN_GAP_MIN_SECONDS`. Don't change it casually; downstream
documentation refers to the 30-minute number.

---

## How returns surface elsewhere

Five places:

| Surface | How it reads `returns` |
|---|---|
| `GET /v1/loop/summary` | Returns it inside the `today` / `yesterday` / `window` records. |
| `recall founder daily-loop` | Prints it on the per-row line and folds it into the `return_rate` signal. |
| `alpha/recovery_journal.json` | Each ledger entry can carry `return_after_gap: true` (Phase 6F). The two are correlated — a recovery that fires *during* a return is the strongest signal we have that the layer is doing its job. |
| `recall alpha replay <handle>` | Per-tester timeline includes `return -> <kind>` rows when the journal entry has `return_after_gap=true`. |
| (no UI) | The user's launcher / popup never display the `returns` count. The signal is for the founder during alpha, not for the user. |

---

## Local-only restated

The `returns` counter is local-only. Three reasons:

1. The state file lives in `~/.recall/`. Nothing in this code
   path writes anywhere else.
2. The bin is *counts only*. The actual gap value (e.g.
   `47521 s`) is computed for the alarm + persisted to
   `last_return_gap_s` for the next-event diff, but the user-
   facing surface only ever sees the count.
3. `recall alpha export` aggregates the bin into JSON, and the
   founder *chooses* whether to share that JSON. There is no
   automated upload.

If a future surface wants per-gap distributions (histograms of
how long users disappear for), the right home is a separate
opt-in counter — not the `returns` bin. The bin's contract is:
*one machine-local day, one count of "the user came back"*.

---

## Verification

To exercise the detector by hand:

```bash
# 1. Wipe the state so the next event is treated as the first.
rm ~/.recall/daily_loop_state.json
rm ~/.recall/daily_loop.jsonl

# 2. Post one event. No return counted.
curl -s -X POST http://127.0.0.1:4545/v1/events/browser \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com","title":"hi","domain":"example.com"}'

# 3. Wait 31+ minutes. Post a second event.
sleep 1900
curl -s -X POST http://127.0.0.1:4545/v1/events/browser \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com/2","title":"back","domain":"example.com"}'

# 4. Read the summary; the `returns` bin should be 1.
curl -s http://127.0.0.1:4545/v1/loop/summary | jq '.today.returns'
```

The exact same path the cohort exercises naturally; the manual
recipe is just a way to confirm the wiring without waiting.
