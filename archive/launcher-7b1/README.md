# archive/launcher-7b1/

Phase 7E's *Launcher Final Product Pass* paper trail. 7B.1
shipped the Stitch-aligned single-document workspace —
calm, beautiful, but it solved the *"floating overlays"*
problem by **removing memory from the surface**.

7E reverses that. Memory is the whole point — and the user
should see it. The new launcher restores OTHER WORK *and*
introduces a brand-new RECENT MEMORY section wired to the
real capture pipeline (`~/.recall/events/YYYY-MM-DD.jsonl`).
The hero gains back its HIGH/MED/LOW signal variants. The
empty/onboarding state goes away in favour of always
showing *something* memory-shaped.

Nothing in active code paths imports from this directory.

---

## What lived here

### `minimal_7b1.py` (was `app/ui/launcher_v3/minimal.py`)

The 7B.1 single-workspace layout — search + Continue
document + bottom strip (Privacy/Demo/Docs/Browser links).
Empty workspace = infinity glyph + 26-pt headline + 2
buttons.

**Why archived.** 7E's window is 700×500 (was 740×500),
the empty surface is gone (replaced by always-on memory
sections), the bottom strip becomes a 4-pill trust row
with live counts, and a brand-new RECENT MEMORY section
sits between the hero and OTHER WORK.

### `recovery_panel_7b1.py` (was `app/ui/launcher_v3/recovery_panel.py`)

The 7B.1 220-px Continue document — eyebrow + bullet body
+ Resume.

**Why archived.** 7E's hero is 110 px tall (the directive
asks for max 120 — we landed at 110 to fit five new
sections inside 500), the body returns to inline evidence
(`2 files - 2 tabs - returned 2d`) instead of a bulleted
list, the confidence pill becomes a variant-driven badge
(HIGH/MED/LOW), and the **left accent rail varies per
signal**: HIGH → filled lavender, MED → soft lavender,
LOW → outline only.

### `investigation_panel_7b1.py` (was `app/ui/launcher_v3/investigation_panel.py`)

The 7B.1 stub — `HEIGHT = 0`, hidden, `populate()`
discarded inputs. Reflected the *single-focus tool*
posture.

**Why archived.** OTHER WORK is back. The new
`InvestigationCardV3` is a real 36-px row: strength dot +
title + last-seen caption (right-aligned).
`InvestigationList` caps at 3 and renders directly on the
inner card with 1-px hairline dividers between rows.

---

## What 7E added

Three new things on top of the rebuilt three:

1. **`RecentMemoryRow` + `RecentMemoryList`** — the new
   section that fixes *"memory invisible"*. Reads real
   events from `EventStore.iter_events_for_date(today)`
   via `LiveLauncher._populate_digest`. Up to 5 rows,
   each `HH:MM  source  label`.
2. **`TrustRow`** — 4 tiny pinned pills at the bottom:
   `LOCAL · NO CLOUD · N EVENTS TODAY · M INVESTIGATIONS`.
   Counts derived live from the same disk reads the
   Phase 7D `recall capture status` CLI uses.
3. **`signal` parameter back on `RecoveryCardV3`** —
   HIGH/MED/LOW drives the accent-rail variant. The 6O
   HIGH-only gate is preserved in the engine; the variant
   exists so the launcher can read the engine's
   `recovery_confidence` band when the gate widens in
   future.

---

## How this folder fits the chain

The launcher's complete archive chain, oldest to newest:

| Folder                                          | Phase   | What it preserved                            |
|-------------------------------------------------|---------|----------------------------------------------|
| [`archive/launcher-v2/`](../launcher-v2)       | 6L      | 3-column shell + sidebar + window           |
| [`archive/launcher-refine/`](../launcher-refine) | 6M.1   | v3/live/minimal capture scripts             |
| [`archive/launcher-overbuild/`](../launcher-overbuild) | 6O | minimal/recovery/investigation + 6M.2/6N captures |
| [`archive/resume-old/`](../resume-old)         | 6P      | stub `_on_restore` + `_on_demo_resume`      |
| [`archive/recovery-ranking/`](../recovery-ranking) | 6Q    | ranking rationale + considered-and-rejected |
| [`archive/launcher-debt/`](../launcher-debt)   | 6R      | 6P.1 / 6Q / 6O variants frozen out of 6R    |
| [`archive/launcher-final/`](../launcher-final) | 7B      | 6R per-section-card pattern                 |
| [`archive/launcher-raycast/`](../launcher-raycast) | 7B.1 | 7B command-palette feel                     |
| **`archive/launcher-7b1/`** (this folder)       | **7E**  | 7B.1 single-document Stitch workspace        |

---

## The freeze

> Then freeze launcher forever.

The 7B.1 `LAUNCHER_VISUAL_MERGE.md` claimed the same
thing. What 7E adds is the *memory surface* the 7B.1
shape was missing — RECENT MEMORY wired to the real
event log, OTHER WORK back as compact rows, trust counts
live at the bottom.

The new
[`LAUNCHER_FINAL.md`](../../docs/product/LAUNCHER_FINAL.md)
is the post-freeze contract. Both prior audits
(`LAUNCHER_SHIP_AUDIT.md` from 7B, `LAUNCHER_VISUAL_MERGE.md`
from 7B.1) are marked superseded.

> open Recall → see unfinished work + recent memory +
> resume path + trust within 3 seconds.
