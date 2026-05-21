# INSTALL_PROOF_WINDOWS.md — Phase 5F build proof

Phase 5F's directive: *no assumptions, no pretending*. This file
records what was actually built and measured in this cycle, plus
the clean-machine checklist that must be walked before
[`GO_NO_GO.md`](../release/GO_NO_GO.md) gate 1 flips to GO.

Pairs with [`INSTALL_VALIDATION_WINDOWS.md`](INSTALL_VALIDATION_WINDOWS.md)
(the Phase 5A.1 cycle, superseded) and
[`MAC_VERIFICATION.md`](../release/MAC_VERIFICATION.md) (the macOS
mirror, all `unknown`).

Honesty rule: a row is ✅ only if it was *executed*, not if it
*should* work.

---

## Build proof — this cycle (2026-05-20)

The build runs in two stages
([`infra/packaging/windows/build.ps1`](../../infra/packaging/windows/build.ps1)):

| Stage | Tool | This cycle | Notes |
|---|---|---|---|
| 1. App bundle | PyInstaller 6.x | ✅ **built — exit 0** | `recall.spec`, Python 3.14 |
| 2. Installer | Inno Setup 6.7.2 | ✅ **built — exit 0** | `recall.iss`, ISCC at `%LOCALAPPDATA%\Programs\Inno Setup 6\` (winget per-user install) |

### Stage 1 — PyInstaller ✅

`python -m PyInstaller recall.spec` was executed against the real
dependency tree (PyQt6, chromadb, sentence-transformers,
transformers, torch, watchdog). A genuine build, not a dry run.

**Result — verified:**

- Exit code **0**. Log ends:
  *"Building COLLECT COLLECT-00.toc completed successfully."*
- `dist\Recall\Recall.exe` produced — **81.8 MB** (85,744,829
  bytes).
- Full one-folder bundle: **970 MB** (1,017,185,543 bytes) across
  **6,865 files**. The bulk is `torch` (~570 MB), `chromadb` +
  `onnxruntime` (~100 MB), `transformers` + `tokenizers` (~80 MB).
  The embedding model is *not* bundled — it downloads once on
  first run.
- PyInstaller wall time: **~14:50** (start-of-analysis to
  COLLECT-done). Dominated by the analyze phase (heavy submodule
  collection for torch + sklearn + chromadb).
- Three benign warnings (kept as record, not blockers):
  - *"Hidden import `_cffi_backend` not found"* — optional
    transitive dependency; not on any Recall code path.
  - *"Core Pydantic V1 functionality isn't compatible with
    Python 3.14 or greater."* — Recall pins Pydantic v2;
    Pydantic v1 is pulled transitively by an upstream and is
    not used by Recall code.
  - *"websockets.legacy is deprecated"* — websockets v14
    deprecation notice; non-blocking.

### Stage 2 — Inno Setup ✅

`ISCC.exe infra\packaging\windows\recall.iss` ran end-to-end with
exit 0. The wizard banner BMPs at `infra/packaging/assets/` were
not present (a Phase 5A leftover); the `.iss` was patched to omit
`WizardImageFile` / `WizardSmallImageFile` and point
`SetupIconFile` at the existing `app/assets/icon.ico`. Inno Setup's
default wizard banner is used until branded BMPs are added — a
"Later" polish item.

**Result — verified:**

- Exit code **0**. Log ends: *"Successful compile (541.109 sec).
  Resulting Setup program filename is:
  `C:\…\dist\installer\Recall-Setup.exe`."*
- `dist\installer\Recall-Setup.exe` produced — **260.8 MB**
  (273,512,213 bytes).
- **SHA-256:** `7AFA53497A419444B11696D4E5494D3A1F2EAAAA229671448B9B6B96375FD975`
- Compression ratio: **3.72×** (970 MB bundle → 261 MB installer
  via `lzma2` + `solid`).
- Inno Setup compile wall time: **541.1 s** (~9 minutes;
  dominated by `lzma2` on the torch/scipy/sentence-transformers
  binaries).
- Per-user install (`PrivilegesRequired=lowest`) — **no admin
  prompt**. Bundled the entire one-folder PyInstaller output
  recursively.

### Run log

The build's full stdout/stderr for this cycle is preserved at
`infra/packaging/windows/build_logs/build-20260520-172738.log`
(PyInstaller stage) and
`infra/packaging/windows/build_logs/iscc-rerun.log` (Inno Setup
stage). End-to-end wall time across both stages: **~24 minutes
on this build machine** — PyInstaller ~15 min, Inno Setup ~9 min.

---

## Clean-machine checklist

Walked on a *fresh* Windows 10/11 VM — no Python, no dev tools, a
profile that has never seen Recall. Each row needs a real run on
that VM. This is what flips gate 1 of
[`GO_NO_GO.md`](../release/GO_NO_GO.md).

| # | Step | Status | Pass criteria |
|---|---|---|---|
| 1 | Clean machine prepared | ⬜ | fresh Windows VM, no Python, never seen Recall |
| 2 | `Recall-Setup.exe` runs | ⬜ | double-click → installer wizard, **no admin prompt** |
| 3 | Install completes < 3 min | ⬜ | wizard *Finish*, timed from double-click |
| 4 | Launcher opens | ⬜ | Ctrl + Space → launcher appears |
| 5 | Daemon starts | ⬜ | `127.0.0.1:4545/v1/health` returns ok |
| 6 | Onboarding works | ⬜ | folder pick → indexing starts |
| 7 | Browser extension pairs | ⬜ | popup shows *connected*, not *missing* |
| 8 | Autostart honored | ⬜ | reboot → Recall in tray; `recall doctor` `autostart=GREEN` |
| 9 | Recovery appears | ⬜ | after real use, a recovery card shows |
| 10 | Resume works | ⬜ | clicking Resume reopens the work |
| 11 | Repair path | ⬜ | `Recall-Setup.exe /SILENT` over a broken install |
| 12 | Upgrade | ⬜ | installing a newer version keeps `~/.recall/` |
| 13 | Uninstall — no residue | ⬜ | uninstall removes the app; `~/.recall/` left (by design) |

Legend: ✅ pass · ❌ fail · ⬜ not yet run.

### Capture targets during the walk

- **Screenshots** under `assets/screenshots/` for: settings dialog
  on a fresh install, the first-recovery moment, the extension
  popup *Connected* state against a real daemon. Replaces the
  fixture renders for the three surfaces where a "real install"
  changes the visual.
- **Timings** for rows 3, 5, 7 — recorded as one-line notes next
  to each row when this checklist is walked.
- **`recall doctor` outputs** — at three points: immediately after
  install, after a reboot, after a week of use. Each output
  pasted into [`EXTENSION_VALIDATION.md`](EXTENSION_VALIDATION.md)
  alongside the popup state.

---

## Current verdict

**Stage 1 + 2 of the build are GO. The clean-machine walk is
NO-GO.** The artifact exists; the artifact has not yet been
proven on a machine that is not the build machine. That is the
gate-1 distinction.

The honest status is *pre-alpha, installer-ready*: a stranger
could download `Recall-Setup.exe`, double-click, and (probably)
end up with a working Recall. Until rows 1-13 are walked on a
clean VM, *probably* is the right word.

## To complete this validation

1. Spin up a fresh Windows 10/11 VM (Hyper-V, VirtualBox, or a
   reset-protected partition).
2. Copy `dist\installer\Recall-Setup.exe` over. Nothing else.
3. Walk rows 1-13 above, timing row 3 with a stopwatch.
4. Fill every ⬜ with ✅/❌ and a one-line note (with the SHA-256
   of the artifact at the top of the table, so the record names
   exactly which build was tested).
5. Capture the listed screenshots into `assets/screenshots/` and
   update [`assets/screenshots/README.md`](../../assets/screenshots/README.md).
6. Update [`apps/admin/release_state.json`](../../apps/admin/release_state.json):
   `go_no_go: NO-GO` → `go_no_go: GO`, and `recall founder bake`
   to refresh the dashboard.

## What is *not* in this proof

Honest exclusions, so this document is never confused with a
gate it has not flipped:

- **SmartScreen / code signing.** The artifact is **unsigned**.
  On first run, Windows SmartScreen will show *"Windows protected
  your PC"*. The user clicks *More info → Run anyway*. Closing
  this needs an EV certificate (gate 7's remaining half).
- **The bundle is not slimmed.** ~970 MB is the cost of bundling
  torch + chromadb + sentence-transformers. A diet (lazy-loading
  the embedding subsystem, or shipping a pure-Python search-only
  variant) is a *Later* item — not blocking the alpha.
- **No macOS proof.** Mac status is in
  [`MAC_VERIFICATION.md`](../release/MAC_VERIFICATION.md) — every
  row `unknown`.
- **No Linux proof.** Linux is source-only; no packaged artifact
  exists.
- **No "this user clicked install" record.** Cohort exports
  (`recall stats --export`) are the only post-install signal that
  ever leaves a user's machine — and only when the user chooses
  to send.

Each of those is named so the omissions cannot be mistaken for
unstated wins.
