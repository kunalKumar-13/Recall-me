# TRUST_FIXTURES_CONTINUITY.md — investigation-grouping calibration

[`TRUST_FIXTURES.md`](TRUST_FIXTURES.md) calibrates *what surfaces*.
This file calibrates *what groups together* — whether Recall's idea
of "one investigation" matches the human's.

The failure this guards against has a precise shape:

> **The human sees one investigation. Recall sees several
> disconnected artifacts.**

The Phase 4H bug was exactly this — `backoff.py` became its own
thread, disconnected from the WebSocket debugging it was part of,
because a file open carries a *filename*, not a *topic*. A filename
is not an investigation.

The grouping rule (Phase 4H): browser visits, searches, and chat
sessions name a topic in their text, so each **session** is
anchored to its dominant topic. A file opened inside that session
**bridges** into that investigation. A file opened with no anchor
(a pure coding session, no browser activity) keeps its own key — a
standalone coding arc is genuinely its own thread until something
connects it. Deterministic, local, no embeddings.

The four fixtures below are the calibration. A change that moves
any of them is a continuity regression.

---

## Fixture A — Correct merge

**Scenario:** WebSocket retry debugging. Across four sessions the
user reads Stack Overflow / MDN / a GitHub issue, opens `client.py`
and `backoff.py`, has a Claude chat about backoff-with-jitter, and
revisits — each coding moment sitting in a session that also holds
WebSocket browser or chat activity.

**Correct behavior:** **one thread.** `backoff.py` and `client.py`
are members of the WebSocket investigation (10 events, 4 surfaces).
Its recovery candidate restores tabs *and* code — 5 targets, not 2.

**Why this is the right merge.** Every file open shares a session
with the investigation's anchor surfaces. Same-session
co-occurrence inside a 30-minute window is the strongest
deterministic "these belong together" signal there is — it is what
*working on something* physically looks like in the event log. The
human would never call `backoff.py` a separate investigation, and
now neither does Recall.

---

## Fixture B — Correct split

**Scenario:** The same WebSocket debugging, and — in unrelated
sessions across the same fortnight — RLHF research (arXiv, Hugging
Face, Alignment Forum).

**Correct behavior:** **two threads.** WebSocket and RLHF never
fold together.

**Why this is the right split.** They share no session, so neither
anchors the other; their topic tokens are distinct and the synonym
map does not connect them. There is no bridge signal — so there is
no merge. Splitting is the *default*; merging must be earned by a
concrete co-occurrence signal. Two genuinely separate
investigations stay separate, and the user's "Active memory
threads" list reads as two real arcs, not one blurred one.

---

## Fixture C — Bad merge (must not happen)

**Scenario:** A WebSocket debugging session in which the user also,
once, opens an unrelated `taxes-2025.xlsx`; and, separately, a
session where two unrelated browser topics co-occur.

**Wrong behavior:** pulling `taxes-2025.xlsx` into "WebSocket", or
fusing two distinct browser topics because they shared a session.

**Why the rule resists it.** Two guards. First, **only file
events bridge** — browser/search/chat events always keep their own
topic key, so two distinct browser topics in one session never
merge into each other. Second, a session's anchor is its
*dominant* topic by deterministic majority vote, so one stray file
open does not redefine anything. A bad merge is worse than a bad
split: it tells the user Recall does not understand their work at
all. The bias is deliberate — bridge conservatively, and only
along the one signal (a file, inside a session, toward that
session's clear topic) that a human would also read as "part of
the same sitting."

> A single stray file in a WebSocket session *will* be grouped
> under WebSocket. That is accepted: within one 30-minute sitting
> it genuinely was part of that working block. The guard is against
> merging *topics* and against letting *one* file rewrite a
> session — not against a session being one working context.

---

## Fixture D — Bad split (the Phase 4H bug)

**Scenario:** WebSocket debugging — but Recall reports `backoff.py`
as its own thread, titled `backoff.py`, disconnected from the
investigation.

**Why this was wrong.** A filename is not a topic. The user was
never "investigating backoff.py" — they were debugging WebSocket
retries, and `backoff.py` was where that work lived. Pre-4H,
recovery for the WebSocket thread restored its tabs but not its
code, because the code had been split off into its own universe.
The recovery felt like a list of objects, not like stepping back
into the room. This is the fixture Phase 4H exists to fix; it is
kept here as the named regression to never reintroduce.

---

## The principle

- **Splitting is the default; merging is earned.** No bridge
  signal → separate threads (Fixture B). This keeps bad merges
  (Fixture C) rare.
- **The one bridge signal is same-session co-occurrence**, file →
  session anchor. It is deterministic, local, inspectable — no
  embeddings, no similarity model.
- **A bad split disconnects the room; a bad merge fakes a room
  that was not there.** Both cost trust. The rule is tuned so the
  common, human-obvious case (Fixture A) merges and the genuinely
  separate case (Fixture B) does not.
- Recall should answer *"what was I trying to do?"* — not *"what
  files did I touch?"*

---

*Investigation coherence is continuity. These fixtures keep it
honest — alongside [`TRUST_FIXTURES.md`](TRUST_FIXTURES.md).*
