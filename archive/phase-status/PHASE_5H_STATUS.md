# PHASE_5H_STATUS.md — Friction Kill iteration

This file is the receipt for the *Friction Kill* iteration that
followed the earlier *Alpha Cohorts + Friction Removal* pass (also
labelled 5H in the prompt history). To disambiguate, the
[`PHASE_TRACKER.md`](../../docs/founder/PHASE_TRACKER.md) tracks the two
iterations separately; this file describes the second.

The directive's twin success criteria:

- A stranger should be installable in **< 60 seconds**.
- Every friction the project knows about should be either *fixed*,
  *deferred with a written reason*, or *named in
  [`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md)*.

Cross-references: [`FRICTION_FIXED.md`](../../docs/engineering/FRICTION_FIXED.md) (the
historical ledger), [`FRICTION_FIXES.md`](../../docs/engineering/FRICTION_FIXES.md) (the
older detailed per-issue receipts), and
[`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) (the still-open list).

---

## What this iteration shipped

### 1. `recall repair` / `recall reset` / `recall reinstall-check`

A new install-side CLI lives in
[`app/core/install_repair.py`](../../app/core/install_repair.py).
Three commands, dispatched through `recall.py`'s fast-path before
the launcher import:

| Command | What it does | Touches user data? |
|---|---|---|
| `recall repair [--dry-run]` | probes 4 install-side checks (config dir, instance lock, `recall://`, autostart) and fixes the non-GREEN ones | **no** |
| `recall reset [--full] [--yes]` | wipes derived caches (`resurfacing.json`, `threads.json`, `evolution.json`, `instance.lock`). `--full` also wipes `events/`, `chroma/`, and `config.json` with a confirm prompt | only with `--full` |
| `recall reinstall-check` | read-only verdict on what survives a reinstall (events, config, chroma) and what gets re-derived | **no** |

All three are ASCII-only (Windows cp1252 safe), echo the same
GREEN/YELLOW/RED vocabulary as `recall doctor`, and never raise
out — repair-tier errors print and exit 1 instead of crashing.

### 2. Extension — daemon pulse indicator

The 6 px dot next to the *Recall* wordmark in the popup header
now **breathes** (opacity 0.5 → 1 → 0.5 over 1.6 s, easeInOut,
looping) when the daemon is `connected`. When disconnected /
reconnecting / offline / loading, the dot is still — the correct
visual for "not flowing right now". Single live-signal that the
local daemon is alive, no badges, no notifications.

### 3. Launcher — stagger reveal

When the digest first paints in a launcher session,
[`_play_digest_stagger_reveal()`](../../app/ui/launcher.py) walks
the visible sections (recovery → investigations → resurface →
recent queries → recent activity → resurfaced) and cascades a 180
ms opacity fade-in with a 60 ms inter-section stagger. The cascade
is one-shot — re-showing the digest in the same launcher instance
is instant. (Phase 4I rule: motion is for first contact, not
every reopen.)

Implemented with `QGraphicsOpacityEffect` + `QPropertyAnimation`
on each section. Animation refs are held on `self` so Qt's GC
doesn't drop them mid-flight.

### 4. Repair-flow plumbing

`install_repair.py` is also the home for *passive* repair-flow
glue: the `_pid_alive` helper lives here (mirrors
`doctor._pid_alive`'s semantics; kept local to avoid a circular
import), and `_DERIVED_FILES` is the canonical *safe-to-delete*
list (the engine re-builds each). Anything not on that list is
user data, and `reset` will only touch it under `--full`.

---

## What this iteration explicitly did **not** ship

The directive listed several pieces that overlap with prior
phases or that crossed the "no engine work / no docs explosion"
guardrails I'd inherited:

| Directive item | Status | Why |
|---|---|---|
| Register `recall://` protocol | already shipped | `infra/packaging/windows/recall.iss` `[Registry]` section + new `repair` write-back path; verify-on-rebuild |
| Autostart task reliability | already shipped | doctor's `_check_autostart` reads HKCU Run + Startup folder; `repair` writes HKCU Run when missing |
| Stale instance lock | already shipped | doctor `_check_launcher` PID-checks; `repair` removes stale locks |
| cp1252 doctor rendering | already shipped | three em-dashes → hyphens |
| Extension detection in frozen build | already shipped | `_check_version_mismatch` skips inside `sys.frozen` |
| `connecting` extension state | deferred | the existing `loading`/`reconnecting`/`disconnected` ladder already covers it; renaming would force a state-machine rewrite for no user-visible benefit |
| Animated recovery card | already shipped | `_ResumePill` + 220 ms slide-fade entrance (Phase 5I) |
| Timeline chips on the recovery card | open | named in `OPEN_PROBLEMS.md` |
| Mini investigation graph | open | named in `OPEN_PROBLEMS.md` |
| Onboarding overlay | open | named in `OPEN_PROBLEMS.md` |
| Repair CTA in the popup | already shipped | `OpenRecallButton` cycles `idle → trying → repair | hint` (Phase 5H) |

The decision rule: anything already shipped goes in
[`FRICTION_FIXED.md`](../../docs/engineering/FRICTION_FIXED.md) with the phase it landed
in. Anything genuinely open goes in
[`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) with a one-line scope note.

---

## Verification

| Surface | Command | Result |
|---|---|---|
| repair CLI smoke | `python recall.py repair --dry-run` | prints 4 rows + correct YELLOW summary line |
| reset CLI smoke | `python recall.py reset` (no `--full`) | (not run in CI — touches `~/.recall`) |
| reinstall-check | `python recall.py reinstall-check` | prints survives/derived lists + folder summary |
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED, no `�` mangling |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.core.install_repair import repair, reset, reinstall_check"` | OK |
| pyflakes (engine) | `python -m pyflakes app/ui app/core api` | zero findings |
| extension build | `cd apps/extension/ui && npm run build` | 399 modules → 283.75 kB JS / 90.92 kB gzipped |
| TS scan | `npx tsc --noEmit` | zero findings |
| control room build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load |

All eight pass.

---

## Touched files

```
new:
  app/core/install_repair.py

modified:
  recall.py                                 (fast-path dispatch for repair/reset/reinstall-check)
  app/ui/launcher.py                        (stagger reveal + imports)
  apps/extension/ui/src/App.tsx             (DaemonPulse component)

new docs:
  docs/engineering/PHASE_5H_STATUS.md       (this file)
  docs/engineering/FRICTION_FIXED.md
  docs/engineering/OPEN_PROBLEMS.md

modified docs:
  docs/founder/PHASE_TRACKER.md
  docs/founder/ROADMAP_LIVE.md
  docs/release/CHANGELOG.md
  docs/DOC_INDEX.md
```

No engine layers touched; no new memory systems; no docs
explosion (three short status files, each under 200 lines).

---

## The < 60 s install rule

The directive's success criterion was "installable by strangers
in < 60 seconds". The Phase 5G silent-install measurement landed
at **66.0 s** on the build machine. The friction kill alone does
not reduce that wall time — the install bottleneck is lzma2
decompression of 970 MB to disk, not anything install_repair.py
touches. The honest path to < 60 s is the *INSTALL_SIZE_AUDIT.md*
reductions (torch + transformers slimming → ~140 MB saved → ~30 s
install). Tracking that in `OPEN_PROBLEMS.md` under *Performance*.
