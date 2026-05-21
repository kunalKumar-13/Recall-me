# TRUST_FIXTURES_DAILY.md — daily-loop calibration

[`TRUST_FIXTURES.md`](TRUST_FIXTURES.md) calibrates *what surfaces*;
[`TRUST_FIXTURES_CONTINUITY.md`](TRUST_FIXTURES_CONTINUITY.md)
calibrates *what groups together*. This file calibrates the **daily
loop**: at what time of day, in what state, the right surface is
offered — and when the right thing is *silence*.

Pairs with [`CONTINUITY_HEALTH.md`](../product/CONTINUITY_HEALTH.md). Every
fixture below is grounded in the deterministic demo seed
(`app/core/demo_seed.py`).

---

## Fixture A — Great morning recovery

**Scenario:** the WebSocket-debugging investigation was abandoned
mid-edit yesterday evening (`backoff.py` reopened, file still
dirty). The user opens the launcher at 9 a.m.

**Expected surface:** the digest header reads **"Continue today"**
(time-of-day swap, Phase 5B). The recovery card shows: WebSocket
retry debugging · 2 tabs · 2 files · *reopened after a 2-day gap*
· Resume. Click Resume → `backoff.py` opens with the surrounding
tabs.

**Why this is correct.** Morning is when the climb back into
yesterday's flow is hardest. *"Continue today"* names the right
question for the hour, and the card is the one strong answer the
engine has. The user did not need a notification to know there was
work to resume — they opened the launcher; Recall met them there.

## Fixture B — Correct silence (a fragmented day, no fake card)

**Scenario:** the previous day was casual — twelve unrelated
browser visits across news, music, and a Wikipedia rabbit-hole.
No file opens, no chat, no multi-day investigation. Morning.

**Expected surface:** the recovery section is **hidden** (no
candidate clears the trust floor); the digest shows threads /
resurfacing only.

**Why this is correct.** Phase 4E's *missed > weak* rule. A
fragmented day has no "next step" Recall can honestly hand back;
fabricating one would damage trust on a day when the user is most
likely to notice. The right surface for an empty morning is the
calm digest, not a noisy card.

## Fixture C — Great evening resume

**Scenario:** mid-afternoon the user was deep in the RLHF research
thread — three arXiv papers, two chats, repeated searches. They
were pulled into a meeting; the work stopped mid-flow. They reopen
the launcher at 7 p.m.

**Expected surface:** the digest header reads **"You paused here"**.
The recovery card shows the RLHF investigation, with the
behavior-evidence chip — *"3 tabs · 1 chat · returned to this 3
times"*. Resume reopens the tabs and the chat in their original
order.

**Why this is correct.** Evening is the recovery surface's other
peak — the user is closing the day's loops. The header swap
acknowledges they paused, not started. The card's evidence
(*"returned to this 3 times"*) is verifiable against memory: yes,
that was the thing I kept coming back to.

## Fixture D — Bad reopen (must not happen)

**Scenario:** the user briefly opened a stray PDF this morning by
accident — one click, never returned to it. They reopen the
launcher in the afternoon.

**Wrong behavior:** the recovery card surfaces the stray PDF as
*"Continue where you left off"* because it is the most recent
file event.

**Why the rule resists it.** A single open is not interrupted work
(`_MIN_DISTINCT_TARGETS = 3` since Phase 4E; `_MIN_EVENTS = 4`).
The depth-and-distinct-targets filters in
[`app/core/recovery.py`](../../app/core/recovery.py) reject this exact
shape. The cost of being wrong here is enormous: a bad reopen
teaches the user that the surface lies, which kills the daily loop
the rest of this file is trying to build. Recall would rather
show nothing — see Fixture B.

---

## The daily-loop principle

> **The right surface at the right hour, or no surface at all.**

A morning that opens with a fake card poisons the day. An evening
that misses the obvious resume poisons the week. The header swap is
the small visible part of a larger contract: Recall reads the time
of day, and the time-of-day reads back. When neither is sure,
silence wins.

Cross-referenced by [`PUBLIC_ALPHA.md`](../founder/PUBLIC_ALPHA.md) and
[`GO_NO_GO.md`](../release/GO_NO_GO.md) (gate 3, *first recovery works*).
