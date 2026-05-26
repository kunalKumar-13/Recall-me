# Launcher Visual Merge — Phase 7B.1

The launcher rebuilds toward the **Stitch reference** —
calmer, document-shaped, single-focus. This document
supersedes [`LAUNCHER_SHIP_AUDIT.md`](LAUNCHER_SHIP_AUDIT.md)
(7B) as the live contract; the 7B audit stays for the
chain.

> **Success criterion:** Looks like product. Not utility.

---

## What 7B.1 changed vs 7B

7B locked the launcher to *one root card* with three regions
inside (search, hero row, OTHER WORK list). At product
distance that still read as a Raycast-shaped *utility* —
densely packed, command-palette feel, no breathing room.

The Stitch reference proves a different shape works better as
the launcher's first impression: a calm **document workspace**
where the centre carries either a *Continue document* (mini
document preview) or the *empty workspace* surface (infinity
glyph + 26-pt headline + two stacked CTAs). The OTHER WORK
list is **gone** from the visible surface; the launcher is a
single-focus tool.

| What                       | 7B                                    | **7B.1**                              |
|----------------------------|---------------------------------------|---------------------------------------|
| Window size                | 680 × 440                             | **740 × 500**                         |
| Outer gutter               | 14 px                                 | 16 px                                 |
| Centre composition         | search + hero row + OTHER WORK list   | **search + one document (or empty)**  |
| Hero                       | 88 px dense row (title + chips + Resume) | **220 px document preview** (eyebrow + title + bullet body + Resume) |
| OTHER WORK                 | vertical list of 44-px rows, max 3    | **removed from the visible surface**  |
| Search bar (right side)    | Ctrl K hint                            | **settings cog + close × + Ctrl K hint** |
| Search placeholder         | `Search work…`                        | **`Start typing to recover…`**        |
| Empty state glyph          | 16-px lavender square                 | **infinity lemniscate (∞) with halo** |
| Empty headline             | 16.5-pt *"Recall notices unfinished work"* | **20-pt (≈ 26 logical) *"Everything you've seen, searchable."*** |
| Empty sub                  | (none)                                | *"Your digital continuity layer."*    |
| Footer                     | single line, centred *local only · no cloud* | **two-cluster strip: trust line on left + tiny `Privacy · Demo · Docs · Browser` links on right** |
| Hotkeys                    | `Esc`, `Ctrl+K`, `1-9`                | **`Esc`, `Ctrl+K`, `Meta+K`, `1`** (2-9 gone — nothing to navigate) |

---

## Frozen contract

### Geometry

| What                                         | Value             |
|----------------------------------------------|-------------------|
| Window size                                  | **740 × 500** (hard clamp) |
| Outer margin (window edge → workspace)       | 16 px             |
| Workspace radius                             | 22 px             |
| Workspace padding                            | 24/20/24/16 (L/T/R/B) |
| Column min / max                             | 540 / 680 px      |
| Search → hero / empty gap                    | 20 px             |
| Hero / empty → bottom strip gap              | 10 px             |
| Continue document height                     | 220 px            |
| Continue document accent rail                | 6 px (rounded)    |
| Bottom strip height                          | 22 px             |

### Paint

| Surface          | Fill          | Border                                        | Shadow                    |
|------------------|---------------|-----------------------------------------------|---------------------------|
| Page             | `#F4F1EC`     | —                                             | —                         |
| Workspace        | `#FFFFFF`     | 1 px `#E4DED6`                                | painted offset (4 px / 20 α) |
| Search bar       | `#FAF7F1`     | 1 px `#E4DED6` (lavender 2 px on focus)       | none                      |
| Continue document| `#FBF8F2`     | 1 px `#E4DED6` (lavender 2 px on focus)       | none                      |
| Resume button    | `#8B7FE3`     | none                                          | inherits workspace        |
| Empty glyph halo | `#EDE9FB`     | —                                             | —                         |

**Forbidden.** Transparency, glass, blur, gradient fills,
shadows >.10 alpha.

### Typography

| Role             | Size       | Weight | Used for                                |
|------------------|------------|--------|-----------------------------------------|
| Empty headline   | 20 pt (≈26 logical) | 700 | *"Everything you've seen, searchable."* |
| Continue title   | 14.5 pt    | 700    | the document's title                    |
| Body             | 10.5 pt    | 400    | bullet rows + sub headline              |
| Search input     | 14 px      | 400    | placeholder + typed text                |
| Eyebrow / strip  | 7.5 pt     | 700    | `CONTINUE` / link row / trust line      |

The directive's *Title 26 · Hero 18 · Body 14 · Meta 11*
scale lands via Qt's point-based sizing — the empty
headline reads as 26-pt logical at typical Windows DPI.

---

## Per-region contract

### 1. Search bar

- Full-width row at the top, 52 px tall, radius 14.
- Soft warm-paper fill (`#FAF7F1`) inside the white workspace.
- Hand-drawn search glyph on the left.
- **Settings cog** + **Close ×** + **Ctrl K hint** on the right.
- Placeholder **`Start typing to recover…`**.
- Lavender 2-px focus ring. Ctrl K hint auto-hides on focus.

### 2. Continue document (when present)

- 220 px tall, radius 16, soft tinted fill (`#FBF8F2`).
- 6-px lavender accent rail clipped to the rounded corners.
- Inside: `CONTINUE` eyebrow + 14.5-pt bold title (elided) +
  bulleted body (up to 4 lines: file/tab/chat/search counts +
  the *returned after Nd* clause if present) + right-aligned
  fixed-width 116-px Resume button with the `1` shortcut.

### 3. Empty workspace

- Infinity lemniscate glyph (lavender + soft halo) centred.
- 20-pt bold headline *Everything you've seen, searchable.*
- 14-px sub *Your digital continuity layer.*
- Two stacked 200-px buttons: *Show example* (accent-filled)
  + *Start working* (warm-paper outline).

### 4. Bottom strip

- Single horizontal row pinned to the bottom of the workspace.
- Left: trust line *"End-to-end encrypted. Local storage only."*
- Right: tiny text links *Privacy · Demo · Docs · Browser*.
- Both clusters at 7.5-pt ink-3.

---

## State catalogue

| State        | Condition                                              | Capture                                                                |
|--------------|--------------------------------------------------------|------------------------------------------------------------------------|
| `empty`      | daemon healthy, no HIGH recovery, no demo overlay      | [`empty.png`](../../assets/screenshots/launcher-merge/empty.png)       |
| `active`     | daemon healthy + HIGH recovery exists                  | [`active.png`](../../assets/screenshots/launcher-merge/active.png)     |
| `resume`     | active state with the Continue document keyboard-focused | [`resume.png`](../../assets/screenshots/launcher-merge/resume.png)     |
| `demo`       | `demo_mode.is_active()` — canonical WebSocket trio     | [`demo.png`](../../assets/screenshots/launcher-merge/demo.png)         |
| `overflow`   | very long title — the document elides cleanly          | [`overflow.png`](../../assets/screenshots/launcher-merge/overflow.png) |

---

## Files

| File                                                                | Role                                |
|---------------------------------------------------------------------|-------------------------------------|
| [`theme.py`](../../app/ui/launcher_v3/theme.py)                     | unchanged from 7B                    |
| [`minimal.py`](../../app/ui/launcher_v3/minimal.py)                 | 740×500 workspace + new search + empty + bottom strip |
| [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)   | Continue document (220 px doc card)  |
| [`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py) | stubbed (engine path stays live; render is gone) |
| [`live.py`](../../app/ui/launcher_v3/live.py)                       | `DEFAULT_SIZE = (740, 500)`; settings/close wiring; hotkeys 2-9 removed; `_extract_gap_clause` helper |
| [`capture_launcher_merge.py`](../../infra/scripts/capture/capture_launcher_merge.py) | 5 captures |
| [`archive/launcher-raycast/`](../../archive/launcher-raycast/)      | 7B snapshots + per-file README       |

---

## What did NOT change

- The recovery engine + ranking layer (`recovery.py`,
  `bad_recoveries.py`, `inspect_cli.py`, `trust_cli.py`).
- The resume pipeline (`resume_preview.py`,
  `restore_toast.py`).
- The legacy launcher escape hatch
  (`RECALL_LAUNCHER=legacy`).
- The 7A extension surface.

7B.1 is paint + composition only.

---

## The freeze

The launcher's audit chain so far:

| Phase  | Audit doc                                          |
|--------|----------------------------------------------------|
| 6R     | `LAUNCHER_FINAL_AUDIT.md`                          |
| 7B     | `LAUNCHER_SHIP_AUDIT.md`                           |
| **7B.1** | **`LAUNCHER_VISUAL_MERGE.md`** (this document)   |

The Stitch reference made the visual problem concrete. The
launcher's next change should require either (a) a similarly
concrete external reference + an audit doc that supersedes
this one, or (b) a regression against one of the rows in the
*Per-region contract* table.

> Looks like product. Not utility.
