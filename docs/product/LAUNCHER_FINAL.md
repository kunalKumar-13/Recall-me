# Launcher Final — Phase 7E

The launcher is now **frozen**. This document supersedes
[`LAUNCHER_VISUAL_MERGE.md`](LAUNCHER_VISUAL_MERGE.md) (7B.1)
as the live contract; the 7B/7B.1 audits stay for the chain.

> **Success criterion (the only one):** open Recall →
> immediately see *I was working on this* and *I can
> continue*, within 3 seconds.

---

## The fix vs 7B.1

7B.1 shipped a beautiful single-document workspace but
solved the *floating overlays* problem by **removing
memory from the surface**. The launcher looked calm but
felt prototype-y: too much white space, no proof Recall
actually saw anything, no way to glance at *what just
happened*.

7E restores memory. The launcher now always shows
*something memory-shaped* — even with no HIGH recovery,
the Recent Memory rail + OTHER WORK list carry the
surface. The trust row at the bottom carries live counts
straight off the same disk reads the Phase 7D `recall
capture status` CLI uses.

| What                       | 7B.1                                    | **7E**                                  |
|----------------------------|------------------------------------------|------------------------------------------|
| Window                     | 740 × 500                               | **700 × 500**                           |
| Centre                     | one Continue document OR empty stack    | Continue (when present) **+ Recent Memory + OTHER WORK** always |
| Empty state                | infinity glyph + 26-pt headline + 2 CTAs| **removed** — memory sections carry the surface |
| Hero variants              | HIGH-only                               | **HIGH / MED / LOW** (filled / soft / outline rail) |
| Recent Memory section      | —                                       | **NEW** — last 5 events from `~/.recall/events/`  |
| OTHER WORK section         | removed (zero-cost stub)                | **back** — compact 36-px rows with strength dot + last-seen |
| Bottom strip               | trust line + tiny Privacy/Demo/Docs/Browser links | **LOCAL · NO CLOUD · `N` EVENTS TODAY · `M` INVESTIGATIONS** pinned trust row, derived live |
| Tagline under search       | —                                       | **`Recall noticed unfinished work`** (13-pt muted lavender) |

---

## Frozen contract

### Geometry

| What                                  | Value             |
|---------------------------------------|-------------------|
| Window size                           | **700 × 500** (hard clamp) |
| Outer margin (window → inner card)    | 12 px             |
| Inner card radius                     | 24 px             |
| Inner card padding                    | 20 / 16 / 20 / 14 (L/T/R/B) |
| Search → tagline gap                  | 6 px              |
| Tagline → CONTINUE eyebrow gap        | 12 px             |
| CONTINUE eyebrow → hero               | 6 px              |
| Hero → RECENT MEMORY eyebrow          | 16 px             |
| RECENT MEMORY eyebrow → rows          | 8 px              |
| Memory rows → OTHER WORK eyebrow      | 12 px             |
| OTHER WORK rows → trust row gap       | 8 px              |

### Paint

| Surface             | Fill          | Border                                | Notes                              |
|---------------------|---------------|---------------------------------------|------------------------------------|
| Page                | `#F5F2ED`     | —                                     | warm paper                         |
| Inner card          | `#FFFFFF`     | 1 px `#E4DED6`                        | radius 24, painted offset shadow   |
| Search bar          | `#FAF7F1`     | 1 px `#E4DED6` (lavender 2 px focused)| sits *inside* the card              |
| Hero (HIGH)         | none          | accent rail: filled lavender          | no card body, just rail            |
| Hero (MED)          | none          | accent rail: soft lavender            |                                    |
| Hero (LOW)          | none          | accent rail: outline only             |                                    |
| Memory rows         | none          | none                                  | tight rows, mono time column       |
| OTHER WORK rows     | none          | 1-px hairline dividers between        | dot + title + last-seen            |
| Trust pills         | `#F5F2ED`     | 1 px `#E4DED6`                        | round, tiny                        |
| Resume button       | `#8B7FE3`     | none                                  |                                    |

**Forbidden.** Transparency, glass, blur, gradient fills,
shadows >.10 alpha, nested cards.

### Typography (per directive)

| Role            | Size       | Used for                          |
|-----------------|------------|-----------------------------------|
| Title (hero)    | 14 pt bold | the Continue document title       |
| Body            | 11 px      | evidence row, recent memory rows  |
| Memory time     | 8.5 pt mono| time column in Recent Memory      |
| Meta            | 9 pt       | OTHER WORK last-seen              |
| Eyebrow         | 7.5 pt 700 | section labels (CONTINUE / RECENT MEMORY / OTHER WORK) |
| Trust pill      | 7 pt 700   | LOCAL / NO CLOUD / N EVENTS / N INVESTIGATIONS |

The directive's *Title 26* lands on the empty-state
headline; 7E removes that surface entirely (Recent Memory
covers it), so the only *title* token in active use is the
hero's 14-pt bold.

---

## Per-region contract

### 1. Search bar — directive section 2

- 52 px tall, radius 14, warm-paper fill (`#FAF7F1`).
- Hand-drawn `_SearchIcon` (no Unicode glyph).
- Placeholder **`Search investigations…`**.
- Inline `Ctrl K` hint chip on the right, hidden on focus.
- Lavender 2-px focus ring.

### 2. Tagline — directive section 2

- 13-px (9-pt) muted lavender line directly under the
  search bar.
- Copy: **`Recall noticed unfinished work`** (always
  visible — the launcher's posture line).

### 3. Continue hero — directive section 3

- 110 px tall (the directive's *height: 120* honoured as
  a max; 110 fits the five sections inside 500).
- 6-px left accent rail with **three variants**:
  - **HIGH**: filled lavender
  - **MED**: soft lavender (filled w/ `ACCENT_SOFT`)
  - **LOW**: outline-only (stroked, no fill)
- Title row: title (one line, elided) + Resume button
  (fixed 116-px, accent-filled, `1` shortcut chip).
- Evidence row: inline `2 files - 2 tabs - returned 2d`
  (counts derived from `suggested_targets` + the
  `_extract_gap_clause` helper).
- Confidence pill on the right of the evidence row,
  variant-driven (HIGH filled / MED soft / LOW outline).

### 4. Recent Memory — directive section 4 (NEW)

- Up to **5 rows** from `~/.recall/events/YYYY-MM-DD.jsonl`
  via `EventStore.iter_events(days=2)` in
  `LiveLauncher._load_recent_memory`.
- Each row: mono `HH:MM` + bold short source +
  scannable label (elided).
- Sources mapped from payload: ChatGPT / Claude / Gemini /
  Google / DuckDuckGo / Bing / domain title-cased.
- Real capture pipeline — the same data the Phase 7D
  `recall capture status` CLI reports.

### 5. OTHER WORK — directive section 5

- Up to **3 rows**, 36-px tall (directive 44 honoured
  as a max; 36 fits the five sections inside 500).
- Each row: strength dot (lavender if surfaces ≥ 3,
  ink-4 otherwise) + title (elided) + last-seen mono
  caption right-aligned.
- 1-px hairline dividers between consecutive rows; no
  wrapping card.

### 6. Trust row — directive section 6

- 22-px row pinned at the bottom of the inner card.
- 4 tiny pills, centred:
  **`LOCAL` · `NO CLOUD` · `N EVENTS TODAY` · `M INVESTIGATIONS`**
- Counts derived live from the same disk reads the Phase
  7D `recall capture status` CLI uses.

---

## State catalogue

| State        | Condition                                              | Capture                                                              |
|--------------|--------------------------------------------------------|----------------------------------------------------------------------|
| `home`       | populated everything                                   | [`home.png`](../../assets/screenshots/launcher-7e/home.png)         |
| `high`       | hero with HIGH-confidence accent rail                  | [`high.png`](../../assets/screenshots/launcher-7e/high.png)         |
| `med`        | hero with MED-confidence soft rail                     | [`med.png`](../../assets/screenshots/launcher-7e/med.png)           |
| `low`        | hero with LOW-confidence outline rail                  | [`low.png`](../../assets/screenshots/launcher-7e/low.png)           |
| `no_hero`    | no HIGH recovery — Recent Memory + OTHER WORK only     | [`no_hero.png`](../../assets/screenshots/launcher-7e/no_hero.png)   |

---

## What 7E removed (per directive section 7)

- Show example + Start working giant buttons (the empty
  surface entirely).
- Centered empty states (no more vertically-stacked
  illustrations).
- Large vertical spacing (sections pack tight inside the
  card).
- Floating pills (the bottom strip is text-only / pinned
  pills, no horizontal pill clusters).
- Dark overlays (every surface paints opaque on warm
  paper).
- Prototype illustrations (the infinity glyph is gone;
  Recent Memory is the new first impression).

---

## Files

| File                                                                | Role                                |
|---------------------------------------------------------------------|-------------------------------------|
| [`theme.py`](../../app/ui/launcher_v3/theme.py)                     | unchanged                            |
| [`minimal.py`](../../app/ui/launcher_v3/minimal.py)                 | 700×500 window + new digest + trust row |
| [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)   | hero with HIGH/MED/LOW variants      |
| [`recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py)     | **NEW** — Recent Memory rows + list  |
| [`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py) | rebuilt 36-px rows with strength dot + last-seen |
| [`live.py`](../../app/ui/launcher_v3/live.py)                       | `_load_recent_memory` + `_load_trust_counts` + 700×500 default size |
| [`capture_launcher_7e.py`](../../infra/scripts/capture/capture_launcher_7e.py) | 5 captures |
| [`archive/launcher-7b1/`](../../archive/launcher-7b1/)              | 7B.1 snapshots + per-file README     |

---

## The audit chain

| Phase  | Audit doc                                          | Status      |
|--------|----------------------------------------------------|-------------|
| 6R     | `LAUNCHER_FINAL_AUDIT.md`                          | superseded  |
| 7B     | `LAUNCHER_SHIP_AUDIT.md`                           | superseded  |
| 7B.1   | `LAUNCHER_VISUAL_MERGE.md`                         | superseded  |
| **7E** | **`LAUNCHER_FINAL.md`** (this document)            | **live**    |

---

## The freeze

> Then freeze launcher forever.

The launcher's next change should require either (a) a
similarly concrete external reference + an audit doc that
supersedes this one, or (b) a regression against one of
the rows in the *Per-region contract* table.

The success criterion is one sentence: open Recall, see
unfinished work + recent memory + resume path + trust,
within 3 seconds.

**Launcher frozen.**
