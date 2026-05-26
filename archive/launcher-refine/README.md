# archive/launcher-refine/

Three capture scripts archived during **Phase 6M.1 — Launcher
Refinement**. Each produced its phase's defining screenshots
when the surface looked the way it did at that moment;
keeping them lets a future maintainer regenerate the *before*
images for a side-by-side comparison.

The directive's *delete unused widgets / old spacing helpers /
duplicate chips / legacy styles* rule pointed at the launcher
code path itself; Phase 6M.1's refit cleaned that code in
place. What landed here are the **capture scripts** whose
fixtures referenced layout values that no longer match the
refined launcher.

| File | What it produced | Why archived |
|---|---|---|
| `capture_launcher_v3.py` | the original 6I gallery (3-column shell + sidebar + context column) | The shell + sidebar + context-column widgets moved to `archive/launcher-v2/` in Phase 6L. The script imports them and would error today; Phase 6M.1 finalises the archive by moving the script alongside its fixtures. |
| `capture_launcher_live.py` | the 6K *launcher-live* set (overview / continue / empty / trust / focus / recovery) | Same 3-column composition; same import issue. The 6K shots in `assets/screenshots/launcher-live/` stay on disk as the historical reference. |
| `capture_launcher_minimal.py` | the 6L *launcher-minimal* set (hero / empty / investigations / resume) | The minimal layout is still alive; the **shape** the script captured (920 × 720 window, 760–860 width range, looser spacing, the *Surfaced because* footer line, translucent card paint) was refined out in 6M.1. The 6L shots in `assets/screenshots/launcher-minimal/` stay as the previous-shape reference. |

## Why we kept the files at all

Same reason as `archive/launcher-v2/`: the launcher's visual
language has layers, and *capturing the previous shape* is the
quickest way to show a maintainer what the refinement
actually changed. The files here are reference, not a code
path. Nothing in `app/`, `infra/`, `apps/`, or any active
capture pipeline imports from this directory.

## What replaced them

The Phase 6M.1 capture script lives at
`infra/scripts/capture/capture_launcher_refined.py` and writes
into `assets/screenshots/launcher-refined/`. Five PNGs
(hero / empty / investigations / resume / focused) — the
directive's exact list.

## Why we *didn't* move the launcher code

`app/ui/launcher_v3/` is still the launcher. Phase 6M.1's
diff lives there:

- `theme.py` — new token values (paper white, solid cards,
  tightened shadow, refined typography, 28 / 20 / 12 spacing).
- `surfaces.py:GlassCard` — solid white paint (the *glass* feel
  is gone; the class name kept for backwards-compat).
- `minimal.py` — refit pills (equal width + `+N more` overflow),
  refit empty surface (no card wrapper; vertically centred
  icon + headline + sub + buttons), refit shell (760 max width,
  28 outer padding).
- `recovery_panel.py` — bottom-aligned action row, dropped the
  *Surfaced because you left this mid-flow.* footer line,
  solid accent fill.

Nothing moved out of `app/ui/launcher_v3/`. The directive's
*archive/launcher-refine/* slot is for the **capture scripts**
that fixture the previous shape.
