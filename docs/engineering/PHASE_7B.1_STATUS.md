# Phase 7B.1 — Launcher Visual Merge

**Status:** complete · **launcher rebuilt toward the Stitch reference**
**Directive:** rebuild launcher toward Stitch reference;
current launcher discarded visually; keep logic; replace surface.

> Looks like product. Not utility.

---

## What shipped

### New canvas

- **740 × 500** (was 680 × 440), hard clamp.
- Outer gutter 16 px (was 14).
- Single white workspace at radius 22 inside the gutter.
- Warm `#F4F1EC` page outside; no transparency, no glass.

### New search bar

- 52 px tall, soft warm-paper fill (`#FAF7F1`) inside the
  white workspace.
- Right cluster: **settings cog** + **close ×** + **Ctrl K**
  hint chip.
- Settings forwards to the existing `request_settings`
  signal so `app/main.py`'s settings flow lights up; close
  hides the launcher.
- Placeholder **`Start typing to recover…`**.

### Continue document

- 220 px tall calm card with a soft warm-paper tint
  (`#FBF8F2`) — reads as a *document preview*, not a
  command-palette row.
- 6-px lavender accent rail clipped to the rounded corners
  (rounded at top + bottom via clipPath).
- Inside: `CONTINUE` eyebrow + 14.5-pt bold title (elided) +
  bulleted body (file/tab/chat/search counts + the engine's
  *returned after Nd* clause if `preview_caption` carries
  one) + right-aligned fixed-width 116-px Resume button with
  the `1` shortcut chip.
- New `_extract_gap_clause` helper in `live.py` pulls the
  return-after-gap clause out of the engine's deterministic
  `preview_caption`.

### Empty workspace

- Infinity lemniscate glyph (two overlapping ellipses + a
  warm halo, painted via `QPainter`) — replaces the 7B
  lavender square.
- 20-pt bold headline *Everything you've seen, searchable.*
- 14-px sub *Your digital continuity layer.*
- Two stacked 200-px buttons: *Show example* (accent-filled)
  + *Start working* (warm-paper outline).

### Bottom strip

- Single 22-px horizontal row replacing the 7B centred
  footer.
- Left: trust line *End-to-end encrypted. Local storage only.*
- Right: tiny text links *Privacy · Demo · Docs · Browser*
  (links are inert in 7B.1 — placeholders for future deep
  links; this is the *Design UI now. Engine later.*
  pattern the extension already uses).

### Hotkeys + escape

- Removed 2-9 — there's nothing to navigate to in the
  single-focus surface.
- Kept Esc (hide), Ctrl/Cmd+K (focus search), `1` (Resume
  the Continue document).
- Esc still cascades through the resume preview if it's
  visible.

### Investigations stub

- `InvestigationCardV3` + `InvestigationList` reduced to
  zero-cost stubs so the engine path can keep constructing
  them while the launcher never renders any.
- `MinimalDigest.populate` accepts the investigations list
  for back-compat but discards it.

---

## Files touched

**New:**

- [`infra/scripts/capture/capture_launcher_merge.py`](../../infra/scripts/capture/capture_launcher_merge.py)
- [`docs/product/LAUNCHER_VISUAL_MERGE.md`](../product/LAUNCHER_VISUAL_MERGE.md)
- [`docs/engineering/PHASE_7B.1_STATUS.md`](PHASE_7B.1_STATUS.md) (this file)
- [`archive/launcher-raycast/README.md`](../../archive/launcher-raycast/README.md)
- 5 captures in `assets/screenshots/launcher-merge/`

**Rewritten:**

- [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
  — 740×500 workspace, search with settings/close/Ctrl K,
  infinity-glyph empty, bottom strip.
- [`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
  — Continue document (220 px doc card).
- [`app/ui/launcher_v3/investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
  — stubs (engine path stays live, no render).

**Edited:**

- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
  — `DEFAULT_SIZE = (740, 500)`; settings/close wiring;
  hotkeys 2-9 removed; `_extract_gap_clause` helper.

---

## Verification matrix

| Check                                                              | Result        |
|--------------------------------------------------------------------|---------------|
| `python -m pyflakes app/ui app/core api`                           | clean         |
| `v3.MinimalWindow.DEFAULT_SIZE`                                    | `(740, 500)`  |
| `v3.MinimalWindow.OUTER_MARGIN` / `ROOT_RADIUS`                    | `16 / 22`     |
| `v3.RecoveryCardV3.HEIGHT`                                         | `220`         |
| `v3.MinimalSearchBar.HEIGHT`                                       | `52`          |
| Empty capture shows infinity glyph + 26-pt headline + 2 buttons    | yes           |
| Active capture shows Continue document with eyebrow + bullets + Resume | yes      |
| Resume capture shows lavender focus ring on Continue document      | yes           |
| Demo capture shows the canonical WebSocket retry document          | yes           |
| Overflow capture shows the title eliding cleanly                   | yes           |
| Bottom strip shows trust line + Privacy/Demo/Docs/Browser links    | yes           |
| Ctrl K hint chip auto-hides on focus                               | yes           |
| Investigations stub renders nothing                                | yes (`HEIGHT = 0`) |

---

## Success criterion

The directive's single sentence: *Looks like product. Not
utility.*

Three things land in the new captures:

1. **Empty workspace is a destination, not a tool.** The
   infinity glyph + the 26-pt headline say *this is the
   surface*, not *this is a search box*.
2. **The Continue document reads as something to do.** The
   eyebrow + the bulleted body + the right-aligned Resume
   button compose like a document with an action, not a
   row in a command palette.
3. **The trust line + tiny links at the bottom are calm,
   not loud.** The footer no longer competes with the
   workspace; the workspace IS the focal point.

The launcher's audit chain now supersedes the 7B
`LAUNCHER_SHIP_AUDIT.md` with the new
[`LAUNCHER_VISUAL_MERGE.md`](../product/LAUNCHER_VISUAL_MERGE.md).
