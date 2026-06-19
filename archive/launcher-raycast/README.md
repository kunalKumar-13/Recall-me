# archive/launcher-raycast/

Phase 7B.1's *Launcher Visual Merge* paper trail. 7B
("Launcher Production Freeze") shipped a single-root-card
launcher with a Raycast/Linear command-palette feel — search
bar on top, dense recovery row, a vertical list of OTHER WORK
investigations beneath, footer at the bottom.

7B.1 throws that visual language away. The launcher now reads
as a **document workspace**, not a command palette:

  - Empty state centres a circular infinity glyph + a 26-pt
    headline *"Everything you've seen, searchable."* The
    launcher's first impression is *the surface itself*, not
    *the command bar*.
  - When a recovery exists, the centre carries one calm
    **document preview** card (large eyebrow + 18-pt title +
    body lines + Resume), not a dense info row.
  - The OTHER WORK list is **gone**. The launcher is a
    single-focus tool: continue the one thing, or get out of
    the way. Tiny text links at the bottom expose Privacy /
    Demo / Docs / Browser without competing for attention.

Nothing in active code paths imports from this directory.

---

## What lived here

### `minimal_7b.py` (was `app/ui/launcher_v3/minimal.py`)

The 7B "production freeze" surface — 680×440 root card, 52-px
search with the inline Ctrl K chip, the empty surface stack
with logo + headline + Show example / Start working.

**Why archived.** 740×500 canvas + a different empty
composition (infinity glyph, 26-pt headline) + a different
bottom strip (text links, not a footer pill) means the
window/shell/empty pieces all need new layouts.

### `recovery_panel_7b.py` (was `app/ui/launcher_v3/recovery_panel.py`)

The 7B 88-px hero row — title + chips + Resume, only the
6-px lavender accent rail as chrome.

**Why archived.** The new hero reads as a *document preview*
— eyebrow + 18-pt title + a small bulleted body list + a
right-aligned Resume button. The widget is ~220 px tall, not
88, so the geometry, the layout, and the chrome all change.

### `investigation_panel_7b.py` (was `app/ui/launcher_v3/investigation_panel.py`)

The 7B vertical-list OTHER WORK panel.

**Why archived.** The OTHER WORK list is **removed from the
launcher's visible surface in 7B.1**. The class is preserved
(at a thinner, unused stub) so the engine + the API
contracts stay live; only the launcher surface dropped the
render.

---

## How this folder fits the chain

The launcher's complete archive chain, oldest to newest:

| Folder                                                | Phase | What it preserved                            |
|-------------------------------------------------------|-------|----------------------------------------------|
| [`archive/launcher-v2/`](../launcher-v2)             | 6L    | 3-column shell + sidebar + window           |
| [`archive/launcher-refine/`](../launcher-refine)     | 6M.1  | v3/live/minimal capture scripts             |
| [`archive/launcher-overbuild/`](../launcher-overbuild) | 6O   | minimal/recovery/investigation + 6M.2/6N captures |
| [`archive/resume-old/`](../resume-old)               | 6P    | stub `_on_restore` + `_on_demo_resume`      |
| [`archive/recovery-ranking/`](../recovery-ranking)   | 6Q    | ranking rationale + considered-and-rejected |
| [`archive/launcher-debt/`](../launcher-debt)         | 6R    | 6P.1 / 6Q / 6O variants frozen out of 6R    |
| [`archive/launcher-final/`](../launcher-final)       | 7B    | 6R per-section-card pattern                 |
| **`archive/launcher-raycast/`** (this folder)         | **7B.1** | the command-palette feel that 7B inherited |

---

## The visual merge

Phase 7B told the launcher *to be frozen forever*. 7B.1
unfroze it because the Stitch reference proved the calmer
"document workspace" feel reads as *shipped product* in a
way the Raycast/command-palette feel doesn't. The new
[`LAUNCHER_VISUAL_MERGE.md`](../../docs/product/LAUNCHER_VISUAL_MERGE.md)
documents the new contract and supersedes the 7B
`LAUNCHER_SHIP_AUDIT.md` as the live launcher specification.

> Looks like product. Not utility.
