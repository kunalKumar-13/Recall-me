# `assets/screenshots`

Product captures used by the marketing site, the docs site, and
the GitHub README. Light + dark variants for every captured
surface.

## Status

Currently empty. The captures need to come from a real running
launcher; they can't be generated from text-only tooling.

## Capture list (Phase 4B target)

Each row produces two PNGs (`-light.png` and `-dark.png`) at a
consistent retina-equivalent resolution.

| Surface | Source state | File slug |
|---|---|---|
| Launcher idle (digest) | Ctrl+Space, empty query, after the demo seeder has run | `launcher-digest` |
| Launcher search results | `rlhf reward shaping` query | `launcher-search` |
| Recovery card (closed) | One row visible in *Continue where you left off* | `launcher-recovery-row` |
| Recovery in-progress (Restored flash) | Mid-restoration footer flash | `launcher-recovery-restore` |
| Continuity timeline (open thread) | After clicking a thread row | `launcher-evolution-strip` |
| Resurfacing section | *On your radar* with two cards | `launcher-resurfacing` |
| Browser-memory panel in Settings | Settings → Browser Memory open | `settings-browser-memory` |
| First-run state | Fresh install, no folders indexed | `first-run-empty` |
| First-week hint | Folders indexed, no events yet | `first-week-hint` |
| Browser extension popup | Connected, N captured | `extension-popup` |

## Capture procedure

1. `RECALL_DEMO_MODE=1 python recall.py` — boots the launcher
   with the deterministic demo seed (see
   [`apps/desktop/app/core/demo_seed.py`](../../apps/desktop/app/core/demo_seed.py)).
   The seed produces a lived-in event log: developer + research
   + brainstorming + debugging traces with timestamps anchored
   to "yesterday" relative to capture time.
2. Set the OS to light or dark mode before capturing.
3. Press the keybinding for each surface above; capture the
   window crop (not the full screen).
4. Save to `assets/screenshots/<slug>-<mode>.png`.
5. The Mintlify and Next.js builds reference these paths from
   their respective `public/` mirrors; update both at the same
   time.

## Naming convention

`<surface-slug>-<light|dark>.png` — lowercase, hyphenated, no
version suffix. Versions are tracked through git, not through
filenames.
