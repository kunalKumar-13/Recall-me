# LAUNCHER_RESET.md — the product reset

The directive arrived with three repeated lines:

> We overbuilt.
> Stop adding.
> Delete complexity.

This doc is the directive-required audit of that reset. Three
sections: **what we removed**, **why the launcher failed**,
**the new philosophy**.

Pairs with
[`archive/launcher-overbuild/README.md`](../../archive/launcher-overbuild/README.md)
(the per-file rationale for every archived module) and
[`PHASE_6O_STATUS.md`](../engineering/PHASE_6O_STATUS.md) (the
engineering receipt).

---

## What we removed

The reset directive named a list. Every item below is gone from
the launcher's runtime surface; the code paths that produced
them moved to
[`archive/launcher-overbuild/`](../../archive/launcher-overbuild/).

| Surface | Where it lived | Removed because |
|---|---|---|
| **Returns strip** | `MinimalReturns` in `minimal.py` (Phase 6L) | The strip was *ambient*; the user already had a clearer signal — the daily-loop counters in the control room. The launcher doesn't need to surface its own ambient strip. |
| **Trust rows / trust line / `local only · 127.0.0.1:4545 · no cloud` footer** | `MinimalTrust` in `minimal.py` (Phase 6L) | The trust contract belongs on the marketing site (`apps/web/`) and the control room (`apps/admin/web/`). A user opening the launcher to act on a recovery doesn't need to re-read the contract every time. |
| **Confidence sentences** ("Recall thinks this was interrupted work" etc.) | `RecoveryCardV3.sentence` row (Phase 6N) | Anthropomorphises the engine. The user reads the title + chips and decides; the sentence didn't add information, only words. |
| **MED / LOW signal variants** | `RecoveryCardV3.signal` parameter, `_ResumePill(kind="continue"|"review")` (Phase 6N) | Three CTAs for what is fundamentally one decision (*open it or don't*) created false structure. The directive's rule: *Only HIGH recovery exists*. Below the bar, no card. |
| **Status indicators** | `StatusDot("accent")` on investigation pills (Phase 6L) | A coloured dot on each pill suggests state where there is none. Pills are titles, not health rows. |
| **Evidence chip count cap, chip styling, chip kinds** | `parse_evidence_chips()` + `_chip_for()` (Phase 6B-6N) | The reset hero shows one ambient meta line — *"2 tabs · 2 files · returned after 2d"* — rendered as plain text. Replacing chip widgets with a sentence is *less code, same information*. |
| **Preview cards on empty** | `MinimalEmpty._build_preview_card` (Phase 6N) | A fake recovery card on the empty surface tried to *teach* what a recovery looks like. The user learns by *using*; the preview was clutter that competed with the actual call-to-action buttons. |
| **Footers** | trust line + per-card meta footers (Phase 6L-6N) | Every footer was small and quiet; together they made the launcher read as *a page with sections*, not *a tool with one job*. |
| **Doctor info, metrics, recovery explanations** | nowhere in the launcher (the launcher never carried these) | Listed in the directive as confirmation that these belong in the control room, not the launcher. Re-affirmed. |
| **Investigation `sort_for_digest()` (4-tier priority)** | `investigation_panel.py` (Phase 6N) | The reset row shows the first three threads the engine returned. The order they came in is the order they show. A 4-tier priority sort suggests a *ranking* the launcher doesn't actually compute. |
| **`+N more` overflow chip** | `_OverflowChip` in `minimal.py` (Phase 6M.1-6M.2) | A `+2 more` chip implies follow-through (clicking expands a list). The launcher doesn't expand. Showing 3 + a chip = showing 4 false promises. Drop to 3 hard. |

---

## Why the launcher failed

Three failure modes accumulated over phases 6I → 6N. Each
individually small; together they turned a tool into a
dashboard.

### 1. *Every directive added something. No directive removed anything.*

Phase 6I built a 3-column shell. Phase 6K promoted it. Phase 6L
*simplified* — but only by archiving the side columns, not by
trimming the middle. Phase 6M.1 added typography polish + solid
cards + a vertically-centered empty card. Phase 6M.2 recovered
the geometry. Phase 6N added 3-state signal variants + a
confidence sentence + a preview card.

By the end of 6N the launcher carried:

- a header sized for a `H1`,
- a hero with three visual modes,
- a chip strip + a confidence sentence + a `+1 more` chip + a
  returns row + a trust line,
- a preview card on empty,
- a 4-tier sort priority on the investigation row.

Every individual piece had a directive that justified it. None
of those directives asked *"would removing this be better?"*
The reset asked.

### 2. *The launcher became a memory center, not a return-to-work tool.*

A *tool* asks one question: **what do I do next?** A *memory
center* asks several: *what did I do recently · what's still
open · what should I trust · what would I see if there was
data · what's the last time I came back*.

By 6N the launcher answered all of them. Opening it asked the
user to *read* — section labels, status badges, sentences,
preview cards. The reset cut every read down to the one
question: *resume now or not?* If yes → click. If no → close.

### 3. *Visual hierarchy inverted.*

The strongest signal — the recovery — was a single accent-
filled card among ~7 other surfaces by 6N. A user's eye landed
on whichever was tallest, brightest, or busiest — often the
preview card on empty, or the confidence sentence, or the
returns strip with mono timestamps. The Resume CTA had to
fight for attention against ambient information.

The reset puts the Resume CTA in a 100-px fixed-height card
with nothing else competing. The other 360 px of vertical
space is empty surface + a 3-title row. The eye lands on
Resume in under a second.

---

## The new philosophy

Three rules from the reset directive, reformulated as design
constraints the launcher honours from 6O forward:

### Rule 1 — One surface

Recall has many surfaces. The control room is the operator's
surface. The marketing site is the stranger's surface. The
launcher is the **user's surface** — the one they open dozens
of times a day to do one thing.

A surface that does one thing well is short. The reset
launcher is 680 × 460. It cannot grow.

### Rule 2 — HIGH or nothing

The launcher renders a hero card only when the engine is
**sure** (≥ 4 targets). Below the bar, the surface shows the
empty state. Half-confident heroes were the worst kind of
noise: they invited action on bad data.

The cost: some real recoveries don't surface. That's the right
cost. Showing a weak recovery is worse than showing none —
the user learns to trust the surface less. The reset chooses
silence over noise.

### Rule 3 — Add nothing the user doesn't act on

Every pixel on the launcher must support one of two actions:
**resume the recovery** or **dismiss and start fresh**.
Anything that *informs without inviting an action* belongs
somewhere else. The trust line informs but doesn't invite —
it moved to the marketing site. The daily-loop counters
inform but don't invite — they moved to the control room.
The returns strip informs but doesn't invite — it's gone.

The reset puts every surface back to its right venue. The
launcher gets the *one* surface that earned its place: the
recovery hero.

---

## What stays after the reset

The launcher carries exactly five things:

1. A **search bar** (top, capped 620 px wide, centred).
2. A **CONTINUE** section label and a single 100-px **hero
   card** (only when there is a HIGH-confidence recovery).
3. An **OTHER WORK** section label and a row of up to **three
   investigation titles** — bare text, equal width.
4. Or, when neither exists: a centred **headline + sub +
   Show example / Start normally** buttons.
5. A 680 × 460 paper-white window, soft outer shadow, radius
   24. Nothing more.

That's the directive. That's the launcher.

---

## Related

- [`PHASE_6O_STATUS.md`](../engineering/PHASE_6O_STATUS.md) —
  engineering receipt + verification matrix.
- [`archive/launcher-overbuild/README.md`](../../archive/launcher-overbuild/README.md)
  — per-file rationale for every archived module.
- [`assets/screenshots/launcher-reset/`](../../assets/screenshots/launcher-reset/)
  — the two reset captures: `populated.png` and `empty.png`.
- [`LAUNCHER_REGRESSION.md`](LAUNCHER_REGRESSION.md) (6M.2)
  + [`LAUNCHER_REVIEW.md`](LAUNCHER_REVIEW.md) (6M.1) — the
  prior audits this reset supersedes.
