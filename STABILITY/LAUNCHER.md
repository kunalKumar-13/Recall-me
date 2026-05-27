# Phase 8C — Launcher Reality (Phase 10A amendment, 2026-05-27)

> **Phase 10A amendment.** The launcher visual
> surface was rebuilt in commit `3ae52e2`
> ([`app/ui/launcher_v3/darkframe.py`](../app/ui/launcher_v3/darkframe.py),
> 1996 LOC). Canvas is `(760, 520)` (was 720×460
> at the close of Phase 9). Four canonical states:
> Empty / Recovery / Search / Resume preview, each
> with a deterministic capture in
> [`assets/screenshots/launcher-final/`](../assets/screenshots/launcher-final/).
>
> This document is amended in two places:
> (1) the **render-timing table** below is now sourced
> from `DarkLauncher` instead of the Phase 9
> `LiveLauncher`; (2) the **state-coverage table**
> enumerates the four named states + their captures.
> The Phase 8C body — frozen-contract resolution,
> widget-tree walk, gap inventory — still holds.

## Phase 10A render timings

Five runs each, offscreen Qt, system fonts loaded
via `QFontDatabase.addApplicationFont` (the
production tray-icon path doesn't need the
bootstrap; live Qt populates the font database
from the OS):

| Operation                              | Median   | Min      | Max      |
|----------------------------------------|---------:|---------:|---------:|
| Cold construct (single sample)         |  110.9 ms|        — |        — |
| `DarkLauncher()` (warm)                |   1.4 ms |   1.1 ms |   2.0 ms |
| `set_state(STATE_EMPTY)`               |   2.9 ms |   2.2 ms |   6.5 ms |
| `set_state(STATE_RECOVERY)`            |   8.2 ms |   5.0 ms |  14.2 ms |
| `set_state(STATE_SEARCH)`              |   7.7 ms |   4.8 ms |   8.9 ms |
| `set_state(STATE_RESUME)`              |   4.1 ms |   3.6 ms |   6.9 ms |
| `render()` to 760×520 pixmap           |  19.3 ms |  15.0 ms |  66.8 ms |

Cold construct includes module import + Qt
backbone init + the system-font bootstrap.
Warm path is dominated by widget allocation +
the gradient bloom paint. State swaps stay
under one frame at 60 Hz (16.7 ms) for every
state except the worst-case recovery max
(14.2 ms — composition of HeroRecovery +
PreviewCard + three OtherRow widgets).

## Phase 10A state coverage

| State name (slug) | Composition                                                            | Capture                                                                                                            |
|-------------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `empty`           | bloom mark + serif-italic gradient + sub copy + Show example / Start working | [`assets/screenshots/launcher-final/empty.png`](../assets/screenshots/launcher-final/empty.png)                     |
| `recovery`        | `HeroRecovery` (eyebrow + title + chips + Resume/Review) + `PreviewCard` (PDF badge + excerpt + Open ↗) + 3 × `OtherRow` (strength dot + glyph + title + when) | [`assets/screenshots/launcher-final/recovery.png`](../assets/screenshots/launcher-final/recovery.png)               |
| `search`          | 4 `SearchGroup` (Investigation / Files / Returns / Events) × N `SearchResultRow` + `_MiniPreviewPane` | [`assets/screenshots/launcher-final/search.png`](../assets/screenshots/launcher-final/search.png)                   |
| `resume`          | `_CheckDisc` + RESTORED header + 5 × `_RestoredRow` + Undo/Done             | [`assets/screenshots/launcher-final/resume-preview.png`](../assets/screenshots/launcher-final/resume-preview.png)   |

All four captures are deterministic — re-running
the offscreen capture script produces
byte-similar PNGs modulo subpixel anti-aliasing
noise.

## Phase 10A widget tree

```
DarkLauncher (760 × 520)
  └── Frame
        ├── SearchBar       (60 px top row)
        │     ├── Glyph "search"
        │     ├── QLineEdit (placeholder | value)
        │     ├── [optional] N results mono label
        │     └── Kbd ⌃ + Kbd K
        ├── <one of four state widgets>
        │     ├── EmptyView      (_BloomMark + headline + serif accent + sub + button row)
        │     ├── RecoveryView   (HeroRecovery + PreviewCard | OTHER WORK + OtherRow × N)
        │     ├── SearchView     (_SearchGroupLabel + _SearchResultRow × N + _MiniPreviewPane)
        │     └── ResumeView     (_CheckDisc + RESTORED title + _RestoredListContainer + Undo/Done)
        └── Footer          (30 px bottom row)
              ├── _StatusDot  (5 px green halo)
              └── microtext
```

## Frozen contract — Phase 10A still holds

```python
from app.ui.launcher import Launcher          # still resolves
Launcher(FakeEngine()).__class__.__name__      # 'LiveLauncher'
Launcher(FakeEngine()).size()                  # 720 × 460 (LiveLauncher pre-migration)

from app.ui.launcher_v3.darkframe import DarkLauncher
DarkLauncher().size()                          # 760 × 520
```

The `LiveLauncher` size still reads 720×460
*because the production tray-icon boot path
hasn't been migrated yet* — see
[`LAUNCHER_MIGRATION.md`](../docs/engineering/LAUNCHER_MIGRATION.md).
After the migration (Phase 10B target),
`Launcher(...).size()` reads 760×520 + the
visual surface matches the four captures above.

The 5 frozen 7E.1 search-bar signals
(`query_changed`, `searchChanged`, `submit`,
`request_settings`, `request_close`) are
preserved on the new `darkframe.SearchBar`.
The Phase 9 `review` signal on the recovery
hero is preserved on `darkframe.HeroRecovery`.

---

# Phase 8C — Launcher Reality (original)

**Question:** does the frozen 7E.1 launcher actually
construct, layout, and render at a believable cost
across realistic event-count states?

**Method:** offscreen Qt
(`QT_QPA_PLATFORM=offscreen`) — construct
`LiveLauncher`, walk its widget tree, time the cold
construct, and confirm the public contract from
`AUDIT/LAUNCHER_FREEZE.md` still resolves.

**Scope:** behaviour at construction and immediately
after. Interactive flows (typing, scrolling, hover
overlays) are out of scope for 8C — they need a
human in front of a monitor.

---

## Frozen contract: still holds

```python
from app.ui.launcher import Launcher          # ✅ resolves
Launcher(FakeEngine()).__class__.__name__      # 'LiveLauncher'
Launcher(FakeEngine()).size()                  # 720 × 460
```

The 8B collapse (`launcher.py` → 18 lines) preserves
this. No call site needs to change. The legacy
`RECALL_LAUNCHER=legacy` fork is gone — there is one
launcher path now, and this is it.

---

## Cold-construct timing

| Run condition                         | Construct (ms) |
|---------------------------------------|----------------|
| Offscreen, in-process, warm imports   | 84.5 (median, 3 runs) |
| Offscreen, fresh Python (cold imports)| ~460 ms (single sample) |

The 84.5 ms warm number is what matters for daily
use — the tray-icon process boots once per OS
session and subsequent shows reuse the constructed
widget. The 460 ms cold number is the once-per-boot
cost.

---

## Widget tree (frozen)

`LiveLauncher` (object name `launcher_v3_live`)
holds exactly this tree at construction:

```
LiveLauncher                                     # 720×460 root
└─ QVBoxLayout
   ├─ MinimalShell                               # single root card
   │  └─ QVBoxLayout
   │     ├─ MinimalSearchBar                     # 7E.1 frozen contract
   │     │  └─ QHBoxLayout
   │     │     ├─ _SearchIcon
   │     │     ├─ QLineEdit                      # the actual input
   │     │     └─ QLabel                         # ⏎ hint
   │     ├─ _Tagline                             # one dim line of copy
   │     └─ QWidget (stacked)
   │        ├─ MinimalDigest                     # populated state
   │        │  ├─ QLabel                         # "On your radar"
   │        │  ├─ QLabel                         # subhead
   │        │  ├─ RecentMemoryList               # 5 rows max
   │        │  ├─ QLabel                         # divider
   │        │  └─ InvestigationList              # 3 rows max
   │        └─ MinimalEmpty                      # empty state
   │           └─ QLabel                         # single line
   └─ TrustRow                                   # 4 small labels, hairline
   plus overlays:
   ├─ ResumePreview                              # popover (hidden until invoked)
   ├─ RestoreToast                               # transient confirmation
   └─ 4 × QShortcut                              # ⏎ / Esc / ⌘K / ⌘,
```

The shell has exactly **one root card**. There is
no glass effect, no blur, no transparency, no second
card, no animated background. The hairline +
single-card aesthetic from Phase 7E.1 is preserved
verbatim.

---

## State coverage

The 8C directive asked for the launcher at "0 / 1 /
10 / 100 events." `LiveLauncher` does not load
events synchronously at construct time — it pulls
the digest payload through `engine` lazily when
shown. So the construction cost is **constant
regardless of event count**. The variable cost is
in `_load_recent_memory()` and the
investigation/resurfacing pull, both of which were
measured in `PERF.md`:

| Subsystem            | Cost (ms) |
|----------------------|-----------|
| `_load_recent_memory(5)` | 0.8 |
| `_load_trust_counts()`   | 0.9 |

Both read tail-of-file, both are O(rows-returned),
both stay sub-millisecond even with today's 208
events. At 10K events the JSONL tail read is still
bounded by what we return (5 rows) — not the file
size. Confirmed by reading `app/ui/launcher_v3/`
implementation during 8A's `LAUNCHER_MAP.md`
exercise.

---

## Empty state (0 events)

`MinimalEmpty` is shown when the digest payload is
empty. It is a single `QLabel`. No "get started"
button, no onboarding flow, no marketing copy.
This matches the CLAUDE.md "calm UX" rule:

> Empty states earn copy. A blank header strip is
> worse than a one-line explanation of why it's empty.

The copy is the one-line explanation. No more.

---

## Populated state (≥1 event)

`MinimalDigest` is shown. It contains:

- 1 header label ("On your radar")
- 1 subhead label
- `RecentMemoryList` capped at 5 rows
- 1 divider label
- `InvestigationList` capped at 3 rows

So the launcher displays **at most 8 user-readable
rows** in its populated state — the visual budget
holds regardless of how much data the engine has.

---

## Overlays

- **`ResumePreview`** — appears when the user
  triggers resume on a recovery candidate. Detailed
  in [`RESUME.md`](RESUME.md).
- **`RestoreToast`** — transient confirmation.
  3 s auto-dismiss.

Both are children of the launcher (constructed up
front, hidden by default), so showing them is a
visibility flip — no allocation cost.

---

## Keyboard shortcuts (frozen)

| Shortcut | Action                       |
|----------|------------------------------|
| `⏎`      | submit / open top result     |
| `Esc`    | dismiss / close              |
| `⌘K` / `Ctrl+K` | focus search bar      |
| `⌘,` / `Ctrl+,` | open settings         |

All four are `QShortcut` children of the root, set
up in `_install_shortcuts()`.

---

## What this proves

1. **The launcher constructs.** Every run, every
   time, at the public size.
2. **The public import contract holds.**
   `from app.ui.launcher import Launcher` → 
   `LiveLauncher` at `(720, 460)`. 8B's collapse did
   not break the surface.
3. **The widget tree is frozen.** One root card,
   one search bar, one digest area, one trust row,
   two overlays — nothing more.
4. **The display cost is bounded.** Max 8 rows of
   data regardless of event count.

## What this does NOT prove

- That the launcher renders pixel-correct on a real
  display server. Offscreen Qt skips the actual
  compositor. The Phase 7E.1 capture set in
  `assets/screenshots/launcher-7e/` is the pixel
  ground truth.
- That interactive flows work end-to-end (type →
  results → enter → restore). That's the resume
  walk in [`RESUME.md`](RESUME.md) and the manual
  smoke pass tagged in `RELEASE_READINESS.md`.
