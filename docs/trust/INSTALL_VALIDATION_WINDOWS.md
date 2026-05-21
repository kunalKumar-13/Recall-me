# INSTALL_VALIDATION_WINDOWS.md — Windows install proof (Phase 5A.1 cycle)

> **Superseded.** Phase 5F closed the long-standing gate-7 blocker
> by installing Inno Setup and producing a real `Recall-Setup.exe`.
> The current installer truth lives in
> [`INSTALL_PROOF_WINDOWS.md`](INSTALL_PROOF_WINDOWS.md). This file
> is kept as the **historical record of the Phase 5A.1 cycle** —
> the cycle in which the PyInstaller bundle first built, but the
> Inno Setup half was blocked.

Phase 5A wrote the Windows packaging. Phase 5A.1 was *proving it*.
This file is the validation record from that cycle: what was
actually built and run, and the clean-machine checklist that still
must be walked.

Honesty rule: a row is ✅ only if it was *executed*, not if it
*should* work.

---

## Build proof — this cycle

The build runs in two stages (`infra/packaging/windows/build.ps1`):

| Stage | Tool | This cycle | Notes |
|---|---|---|---|
| 1. App bundle | PyInstaller | ✅ **built — exit 0** | `recall.spec`, real run |
| 2. Installer | Inno Setup (`iscc`) | ⛔ not run | Inno Setup not installed on the build machine |

### Stage 1 — PyInstaller ✅

`python -m PyInstaller recall.spec` was executed against the real
dependency tree (PyQt6, chromadb, sentence-transformers,
transformers, torch, watchdog). A genuine build, not a dry run.

**Result — verified:**

- Exit code **0**. Log ends: *"Building COLLECT COLLECT-00.toc
  completed successfully."*
- `dist/proof/Recall/Recall.exe` produced — **86 MB** executable.
- Full one-folder bundle: **~987 MB** (`torch` + `chromadb` +
  `transformers` dominate; the embedding model is *not* bundled —
  it downloads once on first run).
- One expected, harmless warning: `Hidden import "_cffi_backend"
  not found` — `cffi` is an optional transitive dependency, not on
  any Recall code path.

**Finding for the installer step:** at ~987 MB uncompressed the
bundle is large. Inno Setup's `lzma2`/`solid` compression
(`recall.iss`) will shrink the `.exe` substantially, but the
*download size* is a real number to put in front of users —
`DOWNLOADS.md` should state it once stage 2 produces the actual
artifact.

### Stage 2 — Inno Setup

Not run: `iscc` is not installed here. **`Recall-Setup.exe` does not
yet exist.** Producing it needs Inno Setup 6 on the build machine —
this is the gate-7 blocker in `GO_NO_GO.md`.

---

## Clean-machine checklist

Walked on a *fresh* Windows 10/11 VM — no Python, no dev tools, a
profile that has never seen Recall. Each row needs a real run.

| # | Step | Status | Pass criteria |
|---|---|---|---|
| 1 | Clean machine prepared | ⬜ | fresh Windows VM, no Python installed |
| 2 | `Recall-Setup.exe` runs | ⬜ | double-click → installer wizard, **no admin prompt** |
| 3 | Install completes < 3 min | ⬜ | wizard finish, timed from double-click |
| 4 | Launcher opens | ⬜ | Ctrl + Space → launcher appears |
| 5 | Daemon starts | ⬜ | `127.0.0.1:4545/v1/health` returns ok |
| 6 | Onboarding works | ⬜ | folder pick → indexing starts |
| 7 | Browser extension pairs | ⬜ | popup shows *connected*, not *missing* |
| 8 | Autostart honored | ⬜ | reboot → Recall running in tray |
| 9 | Recovery appears | ⬜ | after real use, a recovery card shows |
| 10 | Resume works | ⬜ | clicking Resume reopens the work |
| 11 | Repair path | ⬜ | `Recall-Setup.exe /SILENT` over a broken install |
| 12 | Upgrade | ⬜ | installing a newer version keeps `~/.recall/` |
| 13 | Uninstall — no residue | ⬜ | uninstall removes the app; `~/.recall/` left (by design) |

Legend: ✅ pass · ❌ fail · ⬜ not yet run.

## Current verdict

**Not validated.** Stage 1 (the app bundle) was built for real this
cycle; stage 2 (the installer) and the entire clean-machine
checklist are unrun — there is no `Recall-Setup.exe` to run yet.

The honest status is *pre-alpha*: packaging is written and the
bundle builds; the one-double-click path is unproven. See
[`GO_NO_GO.md`](../release/GO_NO_GO.md) gates 1 and 7.

## To complete this validation

1. Install Inno Setup 6 on the build machine; run `build.ps1` →
   a real `Recall-Setup.exe`.
2. Spin up a clean Windows VM.
3. Walk rows 1–13 above, timing row 3.
4. Capture screenshots into `assets/screenshots/` as you go.
5. Fill every ⬜ with ✅/❌ and a one-line note.
