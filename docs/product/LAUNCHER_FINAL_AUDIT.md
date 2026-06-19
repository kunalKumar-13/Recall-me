# Launcher Final Audit — Phase 6R

The launcher is closed for feature work after this phase. This
document is the **frozen-product** checklist — every condition
below must be true on the live binary before any future change
is allowed inside `app/ui/launcher_v3/`.

> **Success criterion:** open Recall · understand instantly ·
> click Resume · done.

---

## 1. Geometry

| What                                 | Value                          |
|--------------------------------------|--------------------------------|
| Window size                          | **680 × 440** (hard clamp)     |
| Window resize                        | **disabled** (`setFixedSize`)  |
| Outer margin around the page         | 12 px                          |
| Inner page radius                    | 22 px                          |
| Column min / max                     | 480 / 620                      |
| Outer padding inside the column      | 20 px                          |
| Search → hero gap                    | 20 px                          |
| Hero → OTHER WORK gap                | 16 px                          |
| OTHER WORK → footer gap              | 12 px                          |

Numbers came from the directive verbatim. Anything other than
the above is a regression.

---

## 2. Paint

| Surface          | Fill        | Border                          | Shadow                          |
|------------------|-------------|---------------------------------|---------------------------------|
| Page             | `#F4F1EC`   | 1 px `#E4DED6`                  | none                            |
| Search bar       | `#FFFFFF`   | **2 px** `#E7DED3` (lavender on focus, 2 px) | `0 8 24 rgba(0,0,0,.06)` |
| Hero card        | `#FFFFFF`   | 1 px `#E4DED6` (lavender on focus, 2 px)     | `0 12 32 rgba(0,0,0,.08)` |
| OTHER WORK card  | `#FFFFFF`   | 1 px `#E4DED6` + 1 px inter-row dividers     | `0 12 32 rgba(0,0,0,.08)` |
| Resume button    | `#8B7FE3`   | none                            | inherits card                   |
| HIGH badge       | `#EDE9FB`   | none                            | none                            |

**Forbidden.** Transparency, glass, blur, floating opacity
tricks. Every surface paints opaque. The launcher reads as
paper, not as a translucent overlay.

---

## 3. Hero contract

```
[ accent 6 ] [ Title (one line, elided) ] [ HIGH ]  [ Resume 112 ]
             [ chip ] [ chip ] [ chip ]
```

- **Max height** 88 px (`setFixedHeight`).
- **Left accent strip** 6 px (lavender, clipped to the rounded
  border).
- **Title** — one line, elided with `...` past the column
  width.
- **Chips** — max 3, derived from the candidate's
  `suggested_targets` via the same buckets the resume preview
  uses (`_chips_from_targets` in [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)).
- **Confidence badge** — tiny `HIGH` pill, top-right. The
  launcher only ever surfaces HIGH heroes (the 6O HIGH-only
  gate) so the badge is confirmation, not selection.
- **Resume button** — **fixed width 112 px** with a `1`
  shortcut chip.

**Removed** from the prior surface: subtitles, prose,
explanations, *Why this?* links, multi-line metadata, signal
parameters.

---

## 4. OTHER WORK contract

```
+-----------------------------------+
|  o  Title 1                    >  |
|  -------------------------------- |
|  o  Title 2                    >  |
|  -------------------------------- |
|  o  Title 3                    >  |
+-----------------------------------+
```

- **Vertical** list. Not pills, not bubbles, not horizontal.
- Each row **44 px tall** (`setFixedHeight`).
- Dot 6 px (lavender) + title + quiet right arrow.
- **Max 3 rows.** Anything past the third is dropped — no
  overflow chip, no scroll.
- Inter-row 1-px dividers; title elides with `...` when long.

---

## 5. Empty contract

```
        |__|  <- 16-px lavender square
   Recall notices unfinished work
        [ Show example   ]
        [ Start working  ]
```

- Stacked vertically, centred horizontally.
- 14-px gap between elements.
- Both buttons are **200-px fixed width**, equal-height (38 px).
- The buttons live **inside** the stack — no longer floating
  page furniture.
- Primary (*Show example*) is accent-filled; secondary
  (*Start working*) is a layered card with the warm hairline
  border.

---

## 6. Footer

```
        local only  ·  no cloud
```

- Single line. 18-px tall row, ~10-px text.
- Ink-3 colour. No icon, no badge, no link.
- Always present (populated digest **and** empty surface).

---

## 7. Visibility checks

Run each check on a real machine, not just captures. Any
failure blocks ship.

### Arm-length readability (≈ 60 cm)

- Search placeholder reads.
- Hero title reads.
- Resume label reads.
- Chips read.
- Footer is **quiet** (doesn't compete with the hero) but
  legible if you look at it.

### Dark-room readability

- The warm-paper page never inverts to grey or blends with a
  dark wallpaper.
- The lavender accent strip + HIGH badge + Resume button
  carry the same hue in low light.

### 50 % display scaling

- Hero fits within the column at 480 px (the minimum column
  width). Chips don't wrap.
- OTHER WORK rows stay 44 px tall.
- Search icon + placeholder don't collide.

### 125 % Windows scaling

- Window stays inside `680 × 440` per `setFixedSize`. The
  outer margin and footer still render.
- Text sizes are point-based so DPI scales them; the layout
  doesn't reflow.

### Title overflow (hero + OTHER WORK)

- The hero's title elides with `...` when it exceeds the
  available column width. The Resume button never gets shoved
  off the right edge.
- OTHER WORK row titles elide with `...` when they exceed the
  inter-dot-and-arrow column width.

Capture proof: [`assets/screenshots/launcher-final/overflow.png`](../../assets/screenshots/launcher-final/overflow.png).

### Empty state

- The four stacked elements stay centred vertically in the
  remaining space after the search bar + footer reserve.
- The buttons sit on the cross-axis centre; the launcher's
  primary affordance is *Show example*, never *Start
  working*.

Capture proof: [`empty.png`](../../assets/screenshots/launcher-final/empty.png).

### Demo state (`demo_mode.is_active()`)

- Surface reads as the populated digest — the demo overlay
  paints the canonical WebSocket hero + the three
  demo investigations through the **same** widget tree the
  live path uses.
- Clicking Resume on the demo hero runs through the same
  `ResumePreview` → toast cycle as a live restore (preserved
  from 6P).

### Resume state (post-click)

- ResumePreview opens; Cancel + Resume now buttons land
  visibly inside the launcher.
- RestoreToast pins to the bottom with up to 3 target names.
- Launcher hides ~400 ms after a successful toast (preserved
  from 6P).

---

## 8. Files

| File                                                                | Role                                |
|---------------------------------------------------------------------|-------------------------------------|
| [`theme.py`](../../app/ui/launcher_v3/theme.py)                     | `BG=#F4F1EC` · `BORDER_RAISED_STRONG=#E7DED3` · search shadow scale |
| [`minimal.py`](../../app/ui/launcher_v3/minimal.py)                 | 52-px search bar · stacked empty · footer · fixed 680×440 window |
| [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)   | hero card · `_Chip` · `_ConfidenceBadge` · 112-px Resume |
| [`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py) | vertical row + list + inter-row dividers |
| [`live.py`](../../app/ui/launcher_v3/live.py)                       | `setFixedSize(680, 440)` · `WA_TranslucentBackground = False` |
| [`capture_launcher_final.py`](../../infra/scripts/capture/capture_launcher_final.py) | 4 captures |
| [`archive/launcher-debt/README.md`](../../archive/launcher-debt/README.md) | what 6R archived + why |

---

## 9. Captures

Each capture in [`assets/screenshots/launcher-final/`](../../assets/screenshots/launcher-final)
is a proof:

- `hero.png` — populated digest. Header eyebrows + hero +
  vertical OTHER WORK + footer.
- `empty.png` — stacked onboarding. Logo + headline + two
  inside-the-stack buttons.
- `focus.png` — lavender focus ring on the search bar.
- `overflow.png` — hero and OTHER WORK titles both elide with
  `...`.

---

## 10. The freeze

> No more launcher phases after this. Launcher becomes frozen
> product surface.

Any future need to change the launcher's visible shape requires
a justification that survives the rule:

- Does it change something this document promises? Update the
  document and the captures in the same change.
- Does it add a feature? Argue why the launcher (not the engine
  or the extension) is the right home. Default-no.
- Does it remove a feature? Document what migrates and what
  closes. Archive the old code under `archive/launcher-*/`.

The directive's success line:

> open Recall, understand instantly, click Resume, done.

Anything that breaks any of those four is a regression. Fix
the regression before shipping.
