# Phase 7B — Launcher Production Freeze

**Status:** complete · **launcher is now a shipping product**
**Directive:** turn the launcher into shipping product. No new
features, no control room, no extension, no alpha, no docs
except the audit.

> open Recall · see remembered work · press Resume · leave.

---

## What shipped

### Single root card

The 6R *three white cards on a warm page* pattern read as
*three floating overlays* at arm's length. 7B collapses
everything into **one white root card** sitting on the warm
page, with sections hierarchised by the lavender accent rail
+ section eyebrows.

- `MinimalWindow` paints the full-bleed warm page (`#F4F1EC`)
  then a single white root card with radius 22 inside the
  14-px outer margin. Manual drop shadow (two offset rounded
  fills) replaces `QGraphicsDropShadowEffect` — no software
  rasterise pass on the hot path.
- `MinimalShell` provides the 20-px internal padding.
- Search bar, hero, OTHER WORK list all paint *inside* the
  root card without their own card chrome.

### Search bar

- 52 px tall, radius 14, **warm-paper fill** (`#F4F1EC`)
  inside the white root so the affordance reads as distinct.
- Hand-drawn `_SearchIcon` (no Unicode glyph dependency).
- Inline `Ctrl K` hint chip on the right, hidden on focus.
- Lavender 2-px focus ring (was the same in 6R; preserved).
- Placeholder **`Search work…`**.

### Hero — no card chrome

- Fixed 88 px height. **No border, no shadow** — only the
  6-px lavender accent rail on the left (rounded ends).
- Title row (title + HIGH + Resume) + chips row beneath.
- Focus ring is a 1-px lavender outline + brightened accent
  rail — calmer than a heavy border.

### OTHER WORK list — no wrapping card

- 44-px rows painted directly on the root with 1-px hairline
  dividers between consecutive rows. No wrapping card chrome.
- Max 3 visible. Dot + title (elided) + chevron.

### Ctrl/Cmd+K

`QShortcut("Ctrl+K", …)` + `QShortcut("Meta+K", …)` in
`LiveLauncher.__init__` focuses + selects-all the search
input from anywhere inside the launcher.

### Performance timing

`RECALL_DEBUG=1` writes a one-line log to stderr per
`show_centered`:

```
[recall.launcher.timing] show_centered  187.4 ms  (budget 400)
```

Cost: one `time.perf_counter()` pair when the flag is on,
nothing otherwise.

### Captures

Five PNGs in
[`assets/screenshots/launcher-ship/`](../../assets/screenshots/launcher-ship/):

- `hero.png` — populated digest
- `empty.png` — stacked onboarding
- `focus.png` — search bar with the lavender focus ring
- `demo.png` — canonical trio (WebSocket / proposal / RLHF)
- `overflow.png` — long titles elide cleanly

### Archived

Three 6R variants snapshotted into
[`archive/launcher-final/`](../../archive/launcher-final/)
with per-file README documenting the per-section-card era:

- `minimal_6r.py`
- `recovery_panel_6r.py`
- `investigation_panel_6r.py`

### Documentation

- [`docs/product/LAUNCHER_SHIP_AUDIT.md`](../product/LAUNCHER_SHIP_AUDIT.md)
  — **supersedes** `LAUNCHER_FINAL_AUDIT.md` as the live
  contract. Carries the 6R → 7B delta table + the frozen
  paint / geometry / motion / per-region tables + the
  visibility pass + the performance budgets.

---

## Files touched

**New:**

- `infra/scripts/capture/capture_launcher_ship.py`
- `docs/product/LAUNCHER_SHIP_AUDIT.md`
- `docs/engineering/PHASE_7B_STATUS.md` (this file)
- `archive/launcher-final/README.md`
- 5 captures under `assets/screenshots/launcher-ship/`

**Rewritten:**

- [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
- [`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
- [`app/ui/launcher_v3/investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)

**Edited:**

- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
  — Ctrl/Cmd+K shortcuts; `RECALL_DEBUG=1` timing log on
  `show_centered`.

**Untouched:**

- `theme.py`, `live.py` (apart from the two additions above),
  `resume_preview.py`, `restore_toast.py`, `search_panel.py`,
  the trust / signals / inspector layers in `app/core/`.

---

## Verification matrix

| Check                                                              | Result        |
|--------------------------------------------------------------------|---------------|
| `python -m pyflakes app/ui app/core api`                           | clean         |
| `import app.ui.launcher_v3 as v3`                                  | 23 exports    |
| `v3.MinimalWindow.DEFAULT_SIZE`                                    | `(680, 440)`  |
| `v3.MinimalWindow.OUTER_MARGIN` / `ROOT_RADIUS`                    | `14 / 22`     |
| `v3.RecoveryCardV3.HEIGHT`                                         | `88`          |
| `v3.MinimalSearchBar.HEIGHT`                                       | `52`          |
| `v3.InvestigationCardV3.HEIGHT`                                    | `44`          |
| `v3.InvestigationList.MAX_VISIBLE`                                 | `3`           |
| Hero capture shows no card chrome, only accent rail                | yes           |
| OTHER WORK capture shows 1-px dividers, no wrapping card           | yes           |
| Search capture shows warm-paper fill + Ctrl K hint                 | yes           |
| Focus capture shows lavender 2-px focus ring                       | yes           |
| Overflow capture shows hero + OTHER WORK both elide                | yes           |
| Demo capture shows the directive's canonical trio                  | yes           |

---

## Success criterion

The directive's four-step user journey:

1. **Open Recall.** 680 × 440 warm-paper page with a single
   white root card on top. No resize.
2. **See remembered work.** The CONTINUE eyebrow + 6-px
   lavender accent rail direct the eye to the hero.
3. **Press Resume.** Fixed-width 112-px button on the right
   of the hero; `1` shortcut chip.
4. **Leave.** Esc hides; the resume pipeline carries the
   user the rest of the way (Phase 6P preserved).

All four land inside the frozen surface. The launcher is
closed for feature work. **Launcher frozen forever.**
