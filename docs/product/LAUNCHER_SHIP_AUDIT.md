# Launcher Ship Audit — Phase 7B

The launcher is now a **shipping product**. This document
supersedes [`LAUNCHER_FINAL_AUDIT.md`](LAUNCHER_FINAL_AUDIT.md)
(Phase 6R) as the live contract; the 6R audit stays for the
audit chain.

> **Success criterion (the only one):** open Recall · see
> remembered work · press Resume · leave.

---

## What 7B changed vs 6R

6R froze the layout but kept the *per-section card* pattern —
search, hero, and OTHER WORK each painted their own bordered,
shadowed white card on the warm-paper page. At arm's length
that read as *three floating overlays*, not as *one product
object*.

7B collapses the layout into **one white root card**. The
sections sit inside it; hierarchy comes from the lavender
accent rail on the hero + the section eyebrows, not from
per-section card chrome.

| What                      | 6R                        | **7B**                              |
|---------------------------|---------------------------|-------------------------------------|
| Surface architecture      | page + 3 white cards      | **page + 1 white root card**        |
| Search bar paint          | white card, border+shadow | warm-paper fill inside the root, hairline border |
| Hero paint                | white card, border+shadow | **no chrome** — only the 6-px accent rail |
| OTHER WORK paint          | white card wrapper        | rows-on-root with 1-px dividers     |
| Window background         | `#F4F1EC` painted at radius 22 | `#F4F1EC` full-bleed; root card on top |
| Window margin             | 12 px                     | 14 px                               |
| Search hint (Ctrl+K)      | —                         | inline `Ctrl K` chip on the right   |
| Ctrl/Cmd+K hotkey         | —                         | focuses the search input            |
| Boot timing               | not measured              | `RECALL_DEBUG=1` logs `show_centered` ms |

---

## Frozen contract

### Geometry

| What                                         | Value             |
|----------------------------------------------|-------------------|
| Window size                                  | **680 × 440** (hard clamp) |
| Window resize                                | disabled (`setFixedSize`) |
| Outer margin (window edge → root card)       | 14 px             |
| Root card radius                             | 22 px             |
| Root card padding (top/sides)                | 20 px             |
| Root card padding (bottom)                   | 18 px             |
| Search → hero gap                            | 20 px             |
| Hero → OTHER WORK gap                        | 16 px             |
| OTHER WORK → footer gap                      | 12 px             |
| Column min / max                             | 480 / 620 px      |

### Paint

| Surface          | Fill        | Border                                | Shadow                          |
|------------------|-------------|---------------------------------------|---------------------------------|
| Page             | `#F4F1EC`   | —                                     | —                               |
| Root card        | `#FFFFFF`   | 1 px `#E4DED6`                        | painted offset rect (3 px / 18 α) |
| Search bar       | `#F4F1EC`   | **2 px** `#E7DED3` (lavender 2 px on focus) | none — sits on root        |
| Hero             | **none**    | **none** — only the 6-px accent rail  | none                            |
| OTHER WORK rows  | none        | 1-px hairline dividers between rows   | none                            |
| Resume button    | `#8B7FE3`   | none                                  | inherits root                   |
| HIGH badge       | `#EDE9FB`   | none                                  | none                            |

**Forbidden.** Transparency, glass, blur, gradient fills,
shadows >.10 alpha. Every surface paints opaque.

### Motion

Inherited from Phase 7A's extension scale (kept consistent
across the two surfaces):

| Token             | ms  |
|-------------------|-----|
| `--motion-fast`   | 120 |
| `--motion-normal` | 180 |
| `--motion-slow`   | 240 |

One easing curve everywhere:
`cubic-bezier(0.32, 0.72, 0, 1)`.

---

## Per-region contract

### 1. Search bar

- 52 px tall, radius 14, warm-paper fill (`#F4F1EC`).
- Hand-drawn `_SearchIcon` (`QPainter` circle + handle).
- Inline `Ctrl K` hint chip on the right — hidden on focus.
- Lavender 2-px focus ring (`T.ACCENT`).
- Placeholder **`Search work…`**.
- **Ctrl/Cmd+K** focuses + selects all from anywhere in the
  launcher.

### 2. Continue hero

- Fixed **88 px** height. No card chrome.
- **6-px lavender accent rail** on the left, rounded ends,
  brighter on focus.
- Title row: title (one line, elided) + tiny **HIGH** pill +
  fixed-width 112-px Resume button.
- Chips row: max 3, derived from `suggested_targets` via
  `_chips_from_targets`.
- Hidden entirely when the engine doesn't surface a HIGH
  candidate (the directive's *Hide hero if weak* rule).

### 3. OTHER WORK list

- Vertical list of up to **3** rows sitting directly on the
  root card.
- Each row: 44 px, lavender 6-px dot + title (elided) +
  quiet right chevron.
- **1-px hairline dividers** between rows. No wrapping card.

### 4. Empty surface

- Centred stack: lavender square · headline ·
  *Show example* (primary) · *Start working* (secondary,
  warm-paper fill).
- Buttons 200-px fixed width, 38-px tall, inside the stack
  (no longer floating page furniture).

### 5. Footer

- Single line `local only  ·  no cloud`, ~10 px ink-3,
  centred. Pinned to the bottom of the root card on every
  surface.

### 6. Demo state

The directive's canonical trio:

- **Hero:** *WebSocket retry debugging* (4 targets)
- **OTHER WORK row 1:** *Healthcare pitch — proposal draft*
- **OTHER WORK row 2:** *RLHF reward shaping notes*

Capture: [`demo.png`](../../assets/screenshots/launcher-ship/demo.png).

---

## Visibility pass

| Check                       | How verified                                  |
|-----------------------------|-----------------------------------------------|
| 100 % display scaling       | base capture proves baseline geometry         |
| 125 % Windows scaling       | point-based typography (`FS_HERO=20pt`, …); Qt scales without reflow |
| 150 % Windows scaling       | same — `setFixedSize(680, 440)` is logical pixels, scaled by the platform |
| Arm-length readability      | hero title is 13.5 pt bold + the accent rail draws the eye |
| Dark-room readability       | warm `#F4F1EC` page doesn't compete with dark wallpapers; lavender accent retains hue at low brightness |
| Bright-room readability     | white root card + 1-px hairline give a crisp outline against any wallpaper |
| Title overflow              | hero + OTHER WORK both elide with `...` — see `overflow.png` |
| Empty state                 | stacked, buttons centred inside the root      |
| Demo state                  | canonical trio renders inside the same root card |

The DPI captures aren't generated by the offscreen pipeline —
PyQt's offscreen QPA fixes DPI, so a "1.25x" PNG would lie
about real Windows behaviour. The contract is *point-based
typography + `setFixedSize` in logical pixels*; Windows scales
both correctly.

---

## Performance budgets

| Path                                | Budget   | How verified                                      |
|-------------------------------------|----------|---------------------------------------------------|
| Launcher open (`show_centered`)     | **<400 ms** | `RECALL_DEBUG=1` logs `[recall.launcher.timing] show_centered  N ms  (budget 400)` to stderr |
| Search input → debounced search emit | **<100 ms** | `MinimalSearchBar.query_changed` fires on every keystroke; no debounce client-side, the API client carries the timeout |

**No jank** clause: the root card paints itself via a
single `QPainter.fillPath` + manual shadow (two offset
rounded fills) — no `QGraphicsDropShadowEffect`, no software
rasterise pass. The previous per-section cards each carried
a drop-shadow effect, which is the path the directive's
*no jank* rule excludes.

---

## What this proves

Open Recall on a real machine. Three things land in the same
glance:

1. **See remembered work** — the CONTINUE eyebrow + the
   accent rail draw the eye to the hero before anything else
   competes for attention.
2. **Press Resume** — fixed-width 112-px button on the right
   of the hero; carries the `1` keyboard shortcut chip.
3. **Leave** — Esc hides; the launcher gets out of the way.

Anywhere this audit's table values diverge from the live
binary is a regression. The launcher is **frozen forever**.

---

## Files

| File                                                                | Role                                |
|---------------------------------------------------------------------|-------------------------------------|
| [`theme.py`](../../app/ui/launcher_v3/theme.py)                     | unchanged from 6R                    |
| [`minimal.py`](../../app/ui/launcher_v3/minimal.py)                 | single-root-card window + simplified search + footer |
| [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)   | hero with **no card chrome**, only accent rail |
| [`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py) | rows + 1-px dividers, no wrapping card |
| [`live.py`](../../app/ui/launcher_v3/live.py)                       | Ctrl/Cmd+K → search focus; `RECALL_DEBUG=1` timing log |
| [`capture_launcher_ship.py`](../../infra/scripts/capture/capture_launcher_ship.py) | 5 captures |
| [`archive/launcher-final/README.md`](../../archive/launcher-final/README.md) | what 7B archived + why |

---

## The freeze

The 6R audit's last line said *"the launcher is closed for
feature work after this phase."* 7B kept that — no new
features — but the *paint* needed one more pass.

This audit replaces 6R as the live contract. Any future
change requires:

- Updating this document + the captures in the same commit.
- A regression test against every row of the *Visibility
  pass* + *Per-region contract* tables.
- Default-no on adding any feature; *delete-yes* on any
  paint that drifts from this contract.

**Launcher frozen forever.**
