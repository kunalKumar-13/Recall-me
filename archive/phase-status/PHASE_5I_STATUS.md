# PHASE_5I_STATUS.md — Install Speed + Real World Loop

The receipt for Phase 5I. The directive asked for the install
under 60 s and a real first-week loop. **The install timing did
not change this phase** — the engineering changes that close
that target are mapped in [`INSTALL_SIZE_AUDIT_V2.md`](../../docs/engineering/INSTALL_SIZE_AUDIT_V2.md)
and [`MODEL_STRATEGY.md`](../../docs/engineering/MODEL_STRATEGY.md). This phase did the
**measurement, strategy, and packaging design** that the install-speed
work needs as input, plus the **real-world loop** documents and the
extension's quick-resume + investigation-surface chips.

Cross-references: [`FRICTION_FIXED.md`](../../docs/engineering/FRICTION_FIXED.md) (cumulative
ledger), [`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) (still-named
work), [`SPLIT_DISTRIBUTION.md`](../../docs/engineering/SPLIT_DISTRIBUTION.md) (the
packaging target the model-strategy doc enables).

---

## What shipped

### Measurement layer

**[`infra/scripts/audit_install_size_v2.py`](../../infra/scripts/audit_install_size_v2.py)** —
a deep cross-reference of `install.log` against the on-disk
site-packages tree. Generates a real-MB table per `_internal/`
subtree plus a top-20-largest-files report. Produces the data
that [`INSTALL_SIZE_AUDIT_V2.md`](../../docs/engineering/INSTALL_SIZE_AUDIT_V2.md) is
written against. Runs in <2 seconds, stdlib only.

**[`docs/engineering/INSTALL_SIZE_AUDIT_V2.md`](../../docs/engineering/INSTALL_SIZE_AUDIT_V2.md)** —
the V2 audit. Real measurements (not wheel estimates). Names:

- **`torch_cpu.dll` is 265.8 MB** — 27% of the entire installer.
- **`imageio_ffmpeg` is 87.7 MB** of FFmpeg binaries; Recall has
  no media path → fully excludable.
- **`pyarrow` is 88.6 MB** of Arrow IPC + Flight + parquet
  runtime; transitive via huggingface_hub → excludable with one
  verification step.
- **Qt 6 unused modules** (`Quick`, `Qml`, `Quick3DRuntimeRender`,
  `Pdf`, `Designer`, `opengl32sw`, `avcodec-61`) total ~60 MB → low-risk excludes.
- **Tier A (PyInstaller excludes only): -309 MB unpacked → installer at ~180 MB compressed.**
- **Tier B (`torch+cpu` swap): -140 MB more → installer at ~150 MB.**
- **Tier C (ONNX route, drops torch entirely): -490 MB total → installer at ~50 MB.**

### Strategy layer

**[`docs/engineering/MODEL_STRATEGY.md`](../../docs/engineering/MODEL_STRATEGY.md)** —
three concrete routes from 970 MB to <150 MB, each with code
sketch + risk + reversibility. The recommendation is **Tier B
(ONNX runtime + bundled FP32 model)** for the alpha hand-off,
quantising to int8 as a follow-up.

**[`docs/engineering/SPLIT_DISTRIBUTION.md`](../../docs/engineering/SPLIT_DISTRIBUTION.md)** —
four packs (*Core* / *Retrieval Pack* / *Dev Tools* / *Demo Seed*),
two install paths (*Minimal 30 MB* / *Full ~110 MB*), Inno Setup
`[Components]` mapping, and the file-system layout the engine reads
to decide whether semantic search is available.

### Real-world loop layer

**[`alpha/FIRST_72_HOURS.md`](../../alpha/FIRST_72_HOURS.md)** — the
hour-by-hour *trust / confusion / drop-risk / aha* curve for the
first 72 hours of cohort use. Names the *Day 0 install-fail* peak,
the *Day 1 quiet-capture* trust dip, the *Day 2 digest-fills* trust
spike, and the *Day 3+ resume-click* aha. Cross-referenced with each
hour the four critical surfaces (installer / popup `CapturingState`
/ launcher stagger / recovery click) have to be working.

### Launcher split — the first slice

**[`app/ui/launcher_anims.py`](../../app/ui/launcher_anims.py)** —
the first slice extracted from `launcher.py` (2.5 KLOC). Contains
`play_digest_stagger_reveal(launcher)`, a module-level function
that takes the launcher instance and reads its attributes. The
launcher method becomes a one-line call.

This is the *Begin split / Move only one slice* row of the
directive. The eventual `app/ui/launcher/{window, digest, cards,
animations, state, recovery}.py` layout is on the roadmap; this
phase does **one** module. The pattern is established: extract a
self-contained capability, pass `launcher` as an argument, wire
it back through a one-line call.

`QPropertyAnimation` + `QGraphicsOpacityEffect` + `QEasingCurve`
imports moved with it; `launcher.py` lost the now-unused 3-line
import block. Net: launcher.py is **~50 lines shorter**.

### Extension — Phase 5I additions

**Quick-resume hotkey.** Pressing **`1`** (no modifier) in the
popup fires `onResume` on the visible recovery card (if any). The
Resume button shows a small `1` indicator with `aria-keyshortcuts="1"`
+ `title="Resume (press 1)"`. The handler skips when the user is
typing in an input (defensive — there are no inputs in the popup
today, but the guard is cheap).

**Investigation surface chips.** `InvestigationCard` grew a row of
small tags below the summary listing the *surface types* that
investigation has touched (`tabs` / `searches` / `chats` / `files`).
Real data from `investigation.surfaces` — no fake placeholders.
Max four chips so the row never wraps awkwardly.

---

## What did not ship this phase (and why)

Three directive items were deliberately deferred:

| Directive item | Status | Reason |
|---|---|---|
| Actually rebuild the installer with Tier A excludes | open | the rebuild is 24 minutes on this machine + needs a smoke pass; tracked as the first item in [`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) § *Performance* now that the savings math is concrete |
| Switch to `torch+cpu` | open | same; tracked |
| Land the ONNX embedding stack | open | real engineering (~80 LOC swap in `app/core/embeddings.py`) + a smoke quality re-check; named in `MODEL_STRATEGY.md` as the recommended path |
| Timeline chips on the recovery card | deferred | `/v1/recovery/recent` does not currently return per-day activity data; would need engine-side work to expose it. The directive's *No fake placeholders* rule prevents shipping with hardcoded dates. |
| Repair drawer | deferred | the existing `DisconnectedState` + `OpenRecallButton` already provide the repair UX; a separate drawer would duplicate without adding signal. Documented in `OPEN_PROBLEMS.md` |
| Full `app/ui/launcher/` package restructure | partial | only the *animations* slice landed; the full split into `window.py` / `digest.py` / `state.py` / `recovery.py` is incremental work for the next phase |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes (engine) | `python -m pyflakes app/ui app/core api` | **zero findings** |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.ui.launcher_anims import play_digest_stagger_reveal"` | OK |
| extension build | `cd apps/extension/ui && npm run build` | 399 modules → **284.51 kB JS / 91.11 kB gzipped** (~0.76 kB growth from the hotkey + chips + indicator) |
| TS scan | `npx tsc --noEmit` | zero findings |
| control room build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load |
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED (unchanged) |
| repair CLI smoke | `python recall.py repair --dry-run` | 4 rows, correct YELLOW summary |
| reinstall-check | `python recall.py reinstall-check` | survives + re-derived + folder list |
| founder status | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged — inputs didn't drift) |
| audit V2 | `python infra/scripts/audit_install_size_v2.py` | top-25 + top-20-files report; ~1.5 s runtime |

---

## Touched files

```
new code:
  app/ui/launcher_anims.py                  (the first launcher slice)
  infra/scripts/audit_install_size_v2.py    (the V2 measurement tool)

modified:
  app/ui/launcher.py                        (3-import drop + call replaced by 1-line)
  apps/extension/ui/src/App.tsx             ("1" hotkey + handler dep on recovery)
  apps/extension/ui/src/components/ContinueCard.tsx   (Resume "[1]" indicator)
  apps/extension/ui/src/components/InvestigationCard.tsx  (surface-type chips)

new docs:
  docs/engineering/PHASE_5I_STATUS.md       (this file)
  docs/engineering/INSTALL_SIZE_AUDIT_V2.md
  docs/engineering/MODEL_STRATEGY.md
  docs/engineering/SPLIT_DISTRIBUTION.md
  alpha/FIRST_72_HOURS.md

modified docs:
  docs/founder/PHASE_TRACKER.md
  docs/founder/ROADMAP_LIVE.md
  docs/release/CHANGELOG.md
  docs/DOC_INDEX.md
  docs/engineering/OPEN_PROBLEMS.md
```

Five new docs sounds like an explosion; in context, each maps to
a directive deliverable (audit / strategy / packaging / loop /
status). The directive listed all five by name; this phase did
not produce a sixth.

---

## What the *<60 s install* number is now

**Unchanged at 66.0 s** on the build machine. The number moves
the moment any of the following three is applied:

| Action | Expected new install time |
|---|---|
| Tier A excludes (`recall.spec` edit + rebuild) | ~45 s |
| Tier A + B (`torch+cpu`) | ~30 s |
| Tier A + Tier C (ONNX route) | ~15-20 s |

The 60-s line crosses at Tier A alone — *one `excludes=` block in
`recall.spec`*. The biggest *single edit* in the whole project's
performance work is one Python list. The reason it isn't done in
this phase is the 24-minute rebuild + the smoke verification
that has to pair with it — both real but small. They are
[`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) row 8 today.
