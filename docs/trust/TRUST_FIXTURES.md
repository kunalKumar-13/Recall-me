# TRUST_FIXTURES.md — continuity trust calibration

Recall's recovery and resurfacing layers are not graded on how
*much* they surface. They are graded on whether what they surface
is *believable* — whether a user looks at a recovery card and
thinks "yes, that is exactly the work I lost."

That is a hard thing to unit-test with a number. So this file does
it with **named, deterministic fixtures**: concrete scenarios
where the *correct* behavior is known, written down, and explained.
A change that moves any fixture off its expected surface is a trust
regression, and must be justified the same way a moved perf budget
is (see [PERF.md](../engineering/PERF.md)).

Every fixture below is a real story in
[`app/core/demo_seed.py`](../../app/core/demo_seed.py) — the
`RECALL_DEMO_MODE=1` seed. Because the seeder is deterministic
(`_smoke_api.py` § 30 asserts byte-identical re-seeds), these
fixtures are reproducible: seed, then read the recovery /
resurfacing / threads surfaces and compare against the table.

---

## The four trust categories

| Category | What it means | Failure mode it guards against |
|---|---|---|
| **Excellent recovery** | A surfaced candidate that *is* the work the user lost | — |
| **Acceptable silence** | Real activity that is correctly *not* recovered | Surfacing weak work as if it were resumable |
| **Correct resurfacing** | Set-aside work surfaced quietly as "on your radar" | Treating dormant interest as urgent recovery |
| **Suppressed noise** | Passive / accidental activity that surfaces *nowhere* | Recovering browsing the user never "worked" in |

Recovery is the sharpest, most selective surface; resurfacing is
quieter and more permissive; threads is the most permissive. A
healthy system surfaces a topic at *most one* level too loud, and
usually exactly the right one.

---

## Fixture 1 — Excellent recovery

**Story:** WebSocket retry debugging. Four days, four sessions:
research (Stack Overflow, MDN, a GitHub issue) → an implementation
burst (`client.py`, `backoff.py` opened and reopened) → a Claude
chat reviewing backoff-with-jitter → a revisit today, ending with
`backoff.py` reopened mid-edit.

**Expected surface:** **recovers** as the top — and only — recovery
candidate. Continuity ≈ 0.72, confidence ≈ 0.68 (both clear the
Phase 4E floors: trust ≥ 0.55, resume-intent ≥ 0.32). Caption:
`2 tabs · reopened after a 2-day gap · after a revisit`.

**Why this is correct.** Every high-intent signal the engine looks
for is genuinely present: multi-day span, mixed surfaces (browser +
files + chat), repeated reopening of the *same* implementation
file, a deliberate return after a multi-day gap, and an
interruption that landed mid-edit. The user really did lose this
context, and really would want it back. The caption states
*specific, checkable evidence* ("reopened after a 2-day gap") — not
a vague adjective — so the user can confirm it against memory.

**Enforced by:** `_smoke_api.py` § 25.

---

## Fixture 2 — Acceptable silence (research is not resumable work)

**Story:** RLHF reading. Across a week the user searched for
reward shaping, read an arXiv paper, a Hugging Face blog post, and
an Alignment Forum post, then searched again for KL-penalty tuning.

**Expected surface:** crystallizes as a **thread**, surfaces in
**resurfacing** ("on your radar") — and is **not recovered**.

**Why this is correct.** This is reading, not work. It is almost
entirely `browser_visit` events with no file opens, no chat
session, no edits — it fails recovery's depth-event filter. The
*correct* recovery behavior here is **silence**: there is no
interrupted artifact to step back into. Surfacing it as
"Continue where you left off" would be a weak recovery — and one
weak recovery teaches the user the surface is noise. Resurfacing,
which is explicitly the home for "you were interested in this,"
catches it at the right volume.

**Enforced by:** the depth-event filter in
[`recovery.py`](../../app/core/recovery.py) (`_DEPTH_KINDS`); resurfacing
coverage in `_smoke_api.py` § 13.

---

## Fixture 3 — Acceptable silence (set-aside, not interrupted)

**Story:** Healthcare-agents startup. A ten-day arc — a pitch
deck, a market-sizing spreadsheet, a Claude chat on triage
routing, CDC data, notes, a YC companies page — then several days
dormant.

**Expected surface:** may form a **thread**; **not recovered**.

**Why this is correct.** The distinction recovery exists to draw
is *"unfinished"* vs *"done for now."* This work is real and
mixed-surface, but its last coherent block of activity is past the
Phase 4E `_LAST_PHASE_RECENCY_DAYS` window (7 days) — it has been
*set aside*, not *interrupted*. Recovery surfacing it would feel
like an archive lookup, not like re-entering a room. The honest
answer is silence; resurfacing remains free to mention it.

**Enforced by:** the last-phase recency guard in
[`recovery.py`](../../app/core/recovery.py).

---

## Fixture 4 — Suppressed noise (the false positive that must not happen)

**Story:** Casual browsing. A long-read Atlantic article and a
Wikipedia discography page, opened once, then the Atlantic article
revisited once more two days later.

**Expected surface:** **nothing** — not recovery, not resurfacing,
not a thread.

**Why this is correct.** This is the fixture that matters most.
It has a *surface-level* resemblance to Fixture 1 — there is even a
revisit after a gap. But it is pure passive consumption: two
`browser_visit` events on unrelated pages, no depth events, no
sustained engagement, fewer than the minimum distinct targets.
Recovering it would be a **noisy false positive** — the single
most trust-destroying thing the engine can do, because it proves
to the user that Recall does not know the difference between
*reading something* and *working on something*. The correct
output is total silence.

**Enforced by:** `_smoke_api.py` § 29 (shallow browsing rejected
by the depth filter).

---

## How to use these fixtures

- **Before changing a recovery or resurfacing heuristic**, run the
  demo seed and confirm all four fixtures still land on their
  expected surface. A heuristic that "improves recall" by moving
  Fixture 2, 3, or 4 onto the recovery surface has not improved
  anything — it has spent trust.
- **When adding a fixture**, add the story to `demo_seed.py`
  (bump `_SEED_VERSION`), document it here with an explicit
  "why this is correct," and, where practical, add a smoke
  assertion.
- **The asymmetry is deliberate.** A missed recovery (a Fixture-1
  story that fails to surface) costs the user one manual
  reconstruction. A wrong recovery (a Fixture-4 story that
  surfaces) costs the user their belief that the surface is worth
  looking at. The fixtures are weighted accordingly: bias toward
  silence.

---

*Trust is the product. These fixtures are how it is kept honest.*
