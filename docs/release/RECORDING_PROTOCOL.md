# RECORDING_PROTOCOL.md — how the two live demo GIFs get captured

Phase 5H produced three of the directive's five proof GIFs
deterministically from existing PNG state cycles
([`infra/scripts/capture/generate_demo_gifs.py`](../../infra/scripts/capture/generate_demo_gifs.py)).
Two cannot be produced that way — they need real motion that
PNGs can't represent:

- **`install.gif`** — the Inno Setup wizard from double-click to
  *Finish*.
- **`control-room.gif`** — the founder dashboard at
  `localhost:3000`, scrolled or panned across its sections.

This file is the recording recipe for each. The output of a
session under this protocol is a single GIF (≤ 5 MB, ≤ 12 s) that
drops into [`assets/demos/`](../../assets/demos) and is referenced
by the website per [`LANDING_GO_LIVE.md`](LANDING_GO_LIVE.md).

Pairs with [`assets/demos/README.md`](../../assets/demos/README.md)
(the deterministic side) and
[`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md) (the
clean-VM walk where install.gif gets recorded).

---

## Tools (one-time setup)

| Tool | Purpose | Get it |
|---|---|---|
| **ScreenToGif** (Windows) | the recorder; lets you trim to the second and export an optimised GIF | https://www.screentogif.com — free, open-source |
| **gifsicle** | post-export size optimiser; brings a 9 MB GIF down to 3-4 MB without visible loss | `winget install Gifsicle.Gifsicle` |
| (alternative) **PowerToys → Screen Recorder** | works for `.mp4` first, then convert with ffmpeg | shipped with Windows 11 PowerToys |

The deterministic GIFs in Phase 5H needed neither — Python + PIL
was enough. These two need a real recorder.

## Frame budget

Both GIFs should be **≤ 5 MB** and **≤ 12 seconds**, looping
once. The landing page autoplays them; bigger than that and the
page becomes the bottleneck for the install we're trying to
demo.

Target settings:

- Resolution: **1280 × 720** (downsampled if the source is
  larger).
- Frame rate: **8-12 fps** (low fps + long holds reads as calm,
  not laggy).
- Palette: **256 colours** (the default; do not enable dithering).
- Optimisation: `gifsicle -O3 --lossy=80` on the way out.

---

## install.gif — recording script

**Setup.** Clean Windows 10/11 VM (the same one used for
[`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md) row 1).
Resolution **1280 × 720**; light theme; default cursor; close all
other windows.

Copy `Recall-Setup.exe` (the signed-when-available build) onto
the desktop. Open ScreenToGif at 12 fps, recording the entire
screen.

**Beats** (≤ 12 s total):

| t (s) | Action | What the viewer sees |
|---|---|---|
| 0.0 | Press Record | empty desktop with `Recall-Setup.exe` |
| 0.5 | Double-click the installer | the *open file* security prompt (if it appears, click Yes) |
| 1.5 | Wizard *Welcome* page | the calm wizard opens |
| 3.0 | Click *Next* | task-selection page (desktop icon + autostart) |
| 4.5 | Click *Install* | progress bar starts |
| 4.5 → 9.0 | *let it run* (the bar fills; cursor still) | the meditation moment - this is most of the GIF |
| 9.5 | *Finish* page | Recall icon on desktop is visible |
| 10.0 | Stop recording | (post-trim: end on the *Finish* page) |

**Post-process.** In ScreenToGif:
1. *Reduce frame count* by 50% (keeps every other frame). Drops
   size in half; the wizard is mostly static so no visible loss.
2. *Crop* to just the wizard window + a small margin.
3. *Export* as GIF with 256-colour palette.
4. Run `gifsicle -O3 --lossy=80 -o install.gif install.gif`.

**Acceptance criteria** for the file:

- ≤ 5 MB on disk.
- Ends on a frame where the installer is *finished*, not
  mid-progress.
- No tooltip / notification / unrelated windows visible at any
  frame.
- Cursor is visible, slow, deliberate (no jittery mouse trail).

Drop the file at `assets/demos/install.gif`.

---

## control-room.gif — recording script

**Setup.** The same dev machine. `next dev` already running at
`localhost:3000` from `apps/admin/web/`. Browser at the same
1280 × 720, full-screen the page.

Mock data is the one already in `apps/admin/data/`; do not edit
it during the recording.

**Beats** (≤ 12 s total):

| t (s) | Action | What the viewer sees |
|---|---|---|
| 0.0 | Press Record | page top: header + the four overview cards |
| 1.0 | Slow scroll | Traction sparklines fade up |
| 3.0 | Hold | sparklines visible for a beat (the *Linear-internal calm* the visual rule promised) |
| 4.5 | Slow scroll | Cohorts row visible |
| 6.0 | Slow scroll | Release card with the GO/NO-GO state |
| 8.0 | Slow scroll | Trust + Feedback rows |
| 10.0 | Slow scroll | Founder Timeline at page bottom |
| 11.0 | Stop recording | (post-trim: hold the last frame for ~0.5 s) |

Use a smooth-scroll extension or the browser's `Page Down` key
(one tap per scroll beat). Do **not** use a mouse-wheel
scroll — it produces a jittery GIF.

**Post-process.** Same as install.gif: reduce, crop the browser
chrome away, export, `gifsicle`-optimise.

**Acceptance criteria:**

- ≤ 5 MB on disk.
- Shows at least four distinct sections of the control room.
- No browser URL bar / bookmarks bar visible (use F11 or crop).
- Page-render fonts are crisp (the GIF palette can quantise
  text; check the *captured* counters in the Traction row are
  still legible).

Drop the file at `assets/demos/control-room.gif`.

---

## Why GIFs, not videos

The landing page must autoplay without sound. A GIF respects
that constraint by definition; a `.mp4` requires `autoplay
muted` + a fallback poster image + browser-specific handling.
Two GIFs in `assets/demos/` are simpler than a video pipeline.

When the marketing site grows beyond Phase 5H's *Three sections,
not seven* directive, video may earn its place. Until then, GIFs
+ static screenshots are the entire motion budget.

## Failure handling

If a recording produces > 5 MB at acceptable quality, do one of:

1. Lower fps to 8.
2. Reduce duration (cut a beat).
3. Crop tighter.
4. Re-record at 1024 × 576.

Do **not** ship a 10 MB GIF "just for now". The landing page is
the front door; a slow load there is its own friction.

> Cross-referenced by [`LANDING_GO_LIVE.md`](LANDING_GO_LIVE.md)
> § 6 *Demo / proof assets* and
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) Phase 5H *deferred*.
