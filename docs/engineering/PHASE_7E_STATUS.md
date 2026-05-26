# Phase 7E — Launcher Final Product Pass

**Status:** complete · **launcher frozen**
**Directive:** turn the launcher into a real product surface
— memory visible, hierarchy clear, single surface at 700×500.

> open Recall → see *I was working on this* and *I can
> continue* within 3 seconds.

---

## What shipped

### The big shift

7B.1 shipped a beautiful single-document workspace but
solved *floating overlays* by **removing memory from the
surface**. 7E restores memory. The launcher now always
shows *something memory-shaped* — even with no HIGH
recovery, Recent Memory + OTHER WORK carry the surface.

### New canvas

- **700 × 500** (was 740 × 500), hard clamp.
- Outer margin 12, inner card radius 24, padding 20/16/20/14.
- Manual two-offset rounded shadow (`QPainter` only, no
  `QGraphicsDropShadowEffect`) on the inner card.

### Hero with signal variants

[`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
gains back the `signal` parameter the 7B / 7B.1 surfaces
dropped:

- **HIGH** → filled lavender accent rail + filled `HIGH` pill
- **MED**  → soft-lavender accent rail + soft `MED` pill
- **LOW**  → outline-only accent rail + ghost `LOW` pill

Layout is one dense 110-px row: title (elided) + Resume
button on top, evidence text + confidence pill on the
bottom. The accent rail is the only chrome — no border, no
shadow, no card-inside-a-card.

### NEW: Recent Memory section

[`recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py)
introduces:

- `MemoryRow` dataclass — `time / source / label`.
- `RecentMemoryList` widget — up to 5 rows, 18 px each.

Live data path in
[`live.py:_load_recent_memory`](../../app/ui/launcher_v3/live.py):

```
EventStore.iter_events(days=2)
  → map each Event.payload to (time, source, label)
  → MemoryRow records
  → RecentMemoryList.populate
```

Source mapping handles ChatGPT / Claude / Gemini / Google /
DuckDuckGo / Bing / domain title-case. Label = title /
query / file basename / chat title.

This fixes the *memory invisible* problem the prior
launcher shapes had — the user can glance at the launcher
and confirm Recall actually saw what they did.

### OTHER WORK back

[`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
rebuilt from the 7B.1 zero-cost stub into real 36-px rows:

- Strength dot (lavender if `surfaces ≥ 3`, ink-4 otherwise).
- Title (elided).
- Last-seen mono caption right-aligned (`3d`, `5d`, `1w`,
  …) via `events.humanize_age`.
- 1-px hairline dividers between rows. No wrapping card.

Max 3 visible.

### Trust row (live counts)

[`minimal.py:TrustRow`](../../app/ui/launcher_v3/minimal.py)
is a 22-px row pinned at the bottom of the inner card with
four tiny pills:

- `LOCAL`
- `NO CLOUD`
- **`N EVENTS TODAY`** — derived from
  `EventStore.iter_events_for_date(today)` count
- **`M INVESTIGATIONS`** — derived from `threads.json` length

`LiveLauncher._populate_digest` calls
`trust.set_counts(events_today, investigations)` after
every refresh. Same disk reads the Phase 7D `recall
capture status` CLI uses, so the launcher's pill values
match the CLI's report.

### Tagline under search

A new 13-px (9-pt) muted lavender line
**`Recall noticed unfinished work`** lives directly under
the search bar — the launcher's posture line that always
shows. Anchors the launcher's promise on every open.

---

## Files touched

**New:**

- [`app/ui/launcher_v3/recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py)
- [`infra/scripts/capture/capture_launcher_7e.py`](../../infra/scripts/capture/capture_launcher_7e.py)
- [`docs/product/LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md)
- [`docs/engineering/PHASE_7E_STATUS.md`](PHASE_7E_STATUS.md) (this file)
- [`archive/launcher-7b1/README.md`](../../archive/launcher-7b1/README.md)
- 5 captures in `assets/screenshots/launcher-7e/`

**Rewritten:**

- [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
  — 700×500 window, new digest with hero+memory+other-work,
  tagline, trust row.
- [`app/ui/launcher_v3/recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py)
  — hero with HIGH/MED/LOW variants.
- [`app/ui/launcher_v3/investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
  — real 36-px rows with strength dot + last-seen.

**Edited:**

- [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
  — `_load_recent_memory`, `_load_trust_counts`,
  `_short_source`, `_short_label`, demo path updated for
  the new digest signature, 700×500 default size, drops
  the `_show_empty` swap on no-recovery (sections carry
  the surface).
- [`app/ui/launcher_v3/__init__.py`](../../app/ui/launcher_v3/__init__.py)
  — exports.

---

## Verification matrix

| Check                                                              | Result        |
|--------------------------------------------------------------------|---------------|
| `python -m pyflakes app/ui app/core api`                           | clean         |
| `import app.ui.launcher_v3` exports                                | 26            |
| `v3.MinimalWindow.DEFAULT_SIZE`                                    | `(700, 500)`  |
| `v3.RecoveryCardV3.HEIGHT`                                         | `110`         |
| `v3.InvestigationCardV3.HEIGHT`                                    | `36`          |
| `v3.InvestigationList.MAX_VISIBLE`                                 | `3`           |
| `v3.RecentMemoryList.MAX_VISIBLE`                                  | `5`           |
| Home capture shows hero + 5 memory rows + 3 OTHER WORK rows        | yes           |
| HIGH capture shows filled accent rail + filled HIGH pill           | yes           |
| MED capture shows soft accent rail + soft MED pill                 | yes           |
| LOW capture shows outline accent rail + ghost LOW pill             | yes           |
| No-hero capture shows Recent Memory + OTHER WORK only              | yes           |
| Trust row shows live counts (71 / 11, 48 / 8, 26 / 4 per capture)  | yes           |

---

## Success criterion

> open Recall → see unfinished work + recent memory +
> resume path + trust within 3 seconds.

Four things land in one glance on the `home.png` capture:

1. **Unfinished work** — the Continue hero (title + accent
   rail + Resume button) names the one thing to do.
2. **Recent memory** — 5 timestamped rows confirm Recall
   actually saw the day's browsing.
3. **Resume path** — the 116-px Resume button + the `1`
   shortcut chip make the next action obvious.
4. **Trust** — the bottom row carries `LOCAL · NO CLOUD ·
   N EVENTS TODAY · M INVESTIGATIONS`, all derived live
   from disk.

The launcher's audit chain now ends at
[`LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md).
**Launcher frozen.**
