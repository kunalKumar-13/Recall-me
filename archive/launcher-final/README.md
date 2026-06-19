# archive/launcher-final/

Phase 7B's *Launcher Production Freeze* paper trail. The 6R
shape (one card per section) was finalised cleanly but still
read as *a stack of floating overlays* rather than as a single
product object.

7B collapses the four-cards-on-a-page layout into a **single
white root card** with sections that earn their hierarchy
through spacing + the lavender accent rail — not through
per-section card chrome.

Nothing in active code paths imports from this directory.

---

## What lived here

### `minimal_6r.py` (was `app/ui/launcher_v3/minimal.py`)

The 6R minimal surface. Carried the per-section card pattern:
search bar, hero, and OTHER WORK each painted their own
1-px-bordered white card with a `0 12 32 .06` shadow against
a warm-paper page.

**Why removed.** Three white cards on a warm page read as
*three separate elements* rather than *one launcher*. The 7B
directive lists *"floating overlays"* and *"weak hierarchy"*
explicitly. The fix: collapse into one root card; let the
accent rail + the eyebrows do the hierarchy work that the
card borders were doing.

### `recovery_panel_6r.py` (was `app/ui/launcher_v3/recovery_panel.py`)

The 6R hero. Carried full card chrome (1-px border + 0 12 32
shadow + 22 radius) **plus** the 6-px lavender accent strip.

**Why removed.** Inside the new white root card, the chrome
becomes redundant — a card inside a card. The 7B hero keeps
the 6-px accent rail (the focal-point signal) and the tiny
HIGH pill and the fixed-width 112-px Resume button, but drops
the border and the shadow. The eyebrow + the accent rail
carry the *this is the focal section* message.

### `investigation_panel_6r.py` (was `app/ui/launcher_v3/investigation_panel.py`)

The 6R OTHER WORK list. Wrapped the three rows in a white card
with rounded corners + a hairline border + drop shadow.

**Why removed.** Same redundancy: a card inside the root
card. The 7B list paints the rows directly against the root
card with 1-px dividers between them. Same row geometry
(44 px), same dot + title + chevron — only the wrapping card
chrome went.

---

## What stayed in active code

- `theme.py` — every token still consumed (the page colour,
  accent, borders, motion scale).
- `live.py` — same widget tree composition; only the search
  card swap + Ctrl+K shortcut + timing logs landed in 7B.
- `resume_preview.py`, `restore_toast.py` — the resume
  pipeline from Phase 6P. Unchanged.

---

## How this folder fits the launcher's archive chain

The launcher's complete archive chain, oldest to newest:

| Folder                                          | Phase | What it preserved                            |
|-------------------------------------------------|-------|----------------------------------------------|
| [`archive/launcher-v2/`](../launcher-v2)       | 6L    | shell + sidebar + window (the 3-column shell) |
| [`archive/launcher-refine/`](../launcher-refine) | 6M.1 | v3/live/minimal capture scripts              |
| [`archive/launcher-overbuild/`](../launcher-overbuild) | 6O | minimal/recovery/investigation + 6M.2/6N captures |
| [`archive/resume-old/`](../resume-old)         | 6P    | stub `_on_restore` + `_on_demo_resume`       |
| [`archive/recovery-ranking/`](../recovery-ranking) | 6Q | ranking rationale + considered-and-rejected  |
| [`archive/launcher-debt/`](../launcher-debt)   | 6R    | 6P.1 + 6Q + 6O variants frozen out of 6R     |
| **`archive/launcher-final/`** (this folder)     | **7B**| the per-section card pattern from 6R         |

---

## The freeze

The 6R audit document
[`LAUNCHER_FINAL_AUDIT.md`](../../docs/product/LAUNCHER_FINAL_AUDIT.md)
says *"the launcher is closed for feature work after this
phase."* 7B kept that promise — no new features land — but
the *paint* needed one more pass. The new
[`LAUNCHER_SHIP_AUDIT.md`](../../docs/product/LAUNCHER_SHIP_AUDIT.md)
supersedes the 6R audit; both documents are kept (the 6R one
is part of the audit trail) but the live contract is 7B.

> launcher frozen forever.
