# `assets/demos`

Demo scripts, recording cues, and the deterministic-seed
recipes that produce them.

## Contents

- **[`demo-script.md`](demo-script.md)** — the canonical
  90-second walkthrough. Three acts, one restoration moment,
  exact click sequence + timing + narration.
- **`launcher.gif`** — Phase 5H. 4-frame state cycle (loading →
  empty → first week → digest). Deterministic, generated from
  `assets/screenshots/launcher-*.png` by
  `infra/scripts/capture/generate_demo_gifs.py`.
- **`recovery.gif`** — Phase 5H. 2-frame focus animation
  (resting → keyboard-focused).
- **`extension.gif`** — Phase 5H. 4-frame popup state cycle
  (loading → empty → capturing → connected). Reflects the new
  Phase 5H state machine in `apps/extension/ui/src/App.tsx`.

Two deferred GIFs (live recording, not derivable from PNGs) live
in [`../../docs/release/RECORDING_PROTOCOL.md`](../../docs/release/RECORDING_PROTOCOL.md):
`install.gif` and `control-room.gif`.

## Capturing a demo

```bash
# 1. Seed a fresh demo event log (idempotent — runs once)
RECALL_DEMO_MODE=1 python recall.py

# 2. (re-seed forced, if you want a clean recording every time)
RECALL_DEMO_MODE=1 RECALL_DEMO_RESEED=1 python recall.py
```

The seeder writes to `~/.recall/events-demo/`, a dedicated
directory that never overlaps with the user's real event
log. See
[`apps/desktop/app/core/demo_seed.py`](../../app/core/demo_seed.py)
(currently still at repo root; future home
`apps/desktop/app/core/demo_seed.py`) for the script content.

## Why deterministic

A demo that drifts between recordings is a demo nobody can
re-shoot. Same seed → same events → same threads → same
recovery card → same preview caption → same restoration
sequence, every time. The brief was explicit: *"deterministic
sessions, preload threads, preload recoveries, …, create
ideal screenshots instantly."*

## Future contents

When demo recording becomes a routine workflow:

```
assets/demos/
├── demo-script.md              the canonical walkthrough
├── recording-checklist.md      pre-shoot checklist
├── 90s-canonical.mp4           the headline cut
├── 30s-loop.mp4                the homepage hero loop
└── 3min-deep-dive.mp4          the developer-audience cut
```

The video files are gitignored by default — they're produced
artefacts, not source. They live in releases / CDN; the repo
just records the scripts.
