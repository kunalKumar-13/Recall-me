# archive/launcher-debt/

Phase 6R's *Launcher Finalization* audit trail. Four files
were frozen out of the runtime surface; the launcher is now
**closed for feature work**.

Nothing in active code paths imports from this directory.

---

## What lived here

### `minimal_6p1.py` (was `app/ui/launcher_v3/minimal.py`)

The 6P.1 visibility recovery surface. Carried:

- A 56-px layered search bar with the hand-drawn icon + lavender
  focus ring.
- An empty surface with a 4-element stack (logo · headline · sub
  · 140-px buttons) where the *Show example / Start normally*
  buttons sat **outside** the centred stack — they read as
  floating page furniture rather than as part of the
  onboarding card.
- An `_InvestigationsCard` wrapping the OTHER WORK row as a
  white card.

**Why removed.** Phase 6R froze the layout: 52-px search bar
(was 56), 88-px hero cap (was 100), vertical OTHER WORK rows
(was horizontal titles), Show example + Start working
inside the centred onboarding stack (no longer floating), and
a single-line footer the previous variant did not have. The
new `minimal.py` is final.

### `recovery_panel_6q.py` (was `app/ui/launcher_v3/recovery_panel.py`)

The 6Q hero. Carried the *Why this?* link + the optional
`signals` parameter that fed [`WhyThisSheet`](why_sheet_6q.py).

**Why removed.** Phase 6R's hero spec: *title only · one line ·
truncate · chips max 3 · Resume fixed 112 · confidence badge
tiny*. The directive explicitly *removes prose · removes
explanations · removes why-this links*. The card is now a
single dense row; the signals path is the engine's job, not
the launcher's.

### `investigation_panel_6o.py` (was `app/ui/launcher_v3/investigation_panel.py`)

The 6O reset's bare-text horizontal row with `MAX_VISIBLE = 3`
equal-width titles.

**Why removed.** Phase 6R: OTHER WORK now renders as a
*vertical list*, not a horizontal row. Each row is 44 px tall,
left-aligned with a small accent dot + title + a quiet right
arrow. The horizontal row read as *adrift text* at arm's
length; the vertical list reads as *a list of things you can
click*.

### `why_sheet_6q.py` (was `app/ui/launcher_v3/why_sheet.py`)

The 6Q *Why this?* overlay that listed engine signals.

**Why removed.** Same reason as the link: *remove
explanations · remove why-this links*. The signals layer
(`recovery.explain_signals` + `recall inspect <id>`) still
exists for the inspector + the trust review CLI; only the
launcher-side overlay disappears.

---

## What stayed in active code

The engine-side signals layer is untouched:

- [`recovery.explain_signals(candidate)`](../../app/core/recovery.py)
  still returns the deterministic signal lines.
- [`recall inspect <id>`](../../app/core/inspect_cli.py) still
  renders them.
- [`bad_recoveries.thread_is_flagged`](../../app/core/bad_recoveries.py)
  still drives Override 5 inside the launcher's HIGH-only
  promotion gate.

Only the *launcher's surface* changed.

---

## Why this folder exists

The directive's closing line:

> No more launcher phases after this.
> Launcher becomes frozen product surface.

This archive is the record of how the launcher arrived at
its frozen shape. Three previous archives carry the same
shape:

- [`archive/launcher-v2/`](../launcher-v2) — Phase 6L shell
  + sidebar + window helpers retired when the launcher went
  single-column.
- [`archive/launcher-overbuild/`](../launcher-overbuild) —
  Phase 6O reset deleted six layers that had accumulated
  across 6I → 6N.
- [`archive/launcher-refine/`](../launcher-refine) —
  Phase 6M.1 refinement deleted the v3 / live / minimal
  capture scripts.

This one closes the series. The launcher is done.
