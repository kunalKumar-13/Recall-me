# Phase 8C — Launcher Reality

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
