# INSTALL_METRICS.md — what installing Recall costs

Five numbers a person can use to decide whether Recall is worth
the room on their machine: **installer size, install time, launch
time, memory, disk**.

Measured on the build machine after Phase 5F produced the real
artifact and Phase 5G ran it end-to-end. Replaced by per-machine
rows in [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md)
as those runs land.

---

## The five numbers (build machine — 2026-05-20)

| Metric | Value | Notes |
|---|---|---|
| **Installer size** | **260.8 MB** (273,512,213 bytes) | `Recall-Setup.exe`, lzma2 + solid compression |
| **Install time (silent)** | **66.0 s** (1.1 min) | `Recall-Setup.exe /VERYSILENT`, wall-clock |
| **Launch time** | **~3 s** to daemon-up | first launch on warm HF cache; cold-start may add ~80 MB model download on a clean machine |
| **Memory after warm-up** | **WS 623 MB / Priv 795 MB / 705 handles** | one process, ~10.7 s CPU during boot, idle afterwards |
| **Disk** | **976 MB** install dir + a few MB `~/.recall/` per active day | install dir is one folder under `%LOCALAPPDATA%\Programs\Recall\` |

Setup for the numbers above:

```
machine:   Windows 11 Pro 10.0.26200, x64
python:    bundled (PyInstaller-frozen 3.14.2)
network:   online; HF cache already warm
.recall:   moved out of the way to .recall.dev-backup, restored after
installer: SHA-256 7AFA53497A419444B11696D4E5494D3A1F2EAAAA229671448B9B6B96375FD975
```

---

## Where the 260.8 MB / 976 MB comes from

The installer compresses a one-folder PyInstaller bundle by ~3.7×
(lzma2 + solid). The bundle itself is dominated by the local ML
stack — the price of being *able to* search without leaving the
machine.

| Subtree | Approx. size | Why it's there |
|---|---|---|
| `_internal\torch\` | ~570 MB | sentence-transformers needs torch; torch ships ~half a GB of CPU kernels |
| `_internal\onnxruntime\` + `chromadb\` | ~100 MB | local vector DB |
| `_internal\transformers\` + `tokenizers\` | ~80 MB | the embedding model's runtime |
| `_internal\PyQt6\` (Qt6 binaries) | ~80 MB | the launcher + settings UI |
| `_internal\scipy\` + `numpy\` + `sklearn\` | ~70 MB | distance computations + clustering |
| All other Python + Recall code | ~80 MB | the actual application |

The embedding **model weights** (~80 MB) are *not* bundled — they
download once on first run into `%LOCALAPPDATA%\…\huggingface\` and
never again (`local_files_only=True` after).

## Where the 623 MB resident memory comes from

PyQt6 + a warm chromadb client + the embedding model in memory.
Once the warm-up thread completes, the working set settles —
idle memory is roughly the same as boot memory because nothing
gets unloaded.

This is *not* the per-query cost. It is the *standing* cost of
having Recall available the moment the user presses Ctrl+Space.

## What we want this to look like — *Later*

These numbers are acceptable for the alpha cycle. They are not
acceptable forever. The directive says so.

| Number | Today | Target | Path |
|---|---|---|---|
| Installer size | 260.8 MB | < 150 MB | lazy-load torch via a separate download channel; or ship a CPU-only minimal torch wheel |
| Disk install | 976 MB | < 400 MB | same path as installer size |
| Memory after warm-up | 623 MB | < 350 MB | defer the embedding model until first search; today it warms eagerly |
| Cold launch (clean machine) | unknown | < 8 s | measured during the clean-machine VM walk |
| Install time | 66 s | < 30 s | downstream of installer size |

Each target is a real engineering project, not a tuning knob —
the right place for it is the roadmap's *Later* column.

## Silent install caveats

For automated runs on a fresh machine, use the full task list:

```
Recall-Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART ^
                 /TASKS="desktopicon,startuplaunch" ^
                 /LOG=install.log
```

Without `/TASKS=`, Inno Setup's silent mode skips the optional
tasks (desktop icon, login launch). The wizard install keeps the
user's checks; the silent install does not — discovered during
Phase 5G's run on the build machine.

## How a maintainer reproduces these numbers

1. Build (or re-use) `Recall-Setup.exe` per
   [`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md).
2. Move any existing `~/.recall\` out of the way:
   `Move-Item ~/.recall ~/.recall.bak`
3. Install with the command above; record `wall = ... s`.
4. Launch the installed Recall; time `127.0.0.1:4545/v1/health`
   to first 200; record as *launch time*.
5. After ~10 s idle, `Get-Process Recall` → record `WS / Priv /
   handles`.
6. `Get-ChildItem $env:LOCALAPPDATA\Programs\Recall -Recurse
   -File | Measure-Object Length -Sum` → install size.
7. Uninstall with `unins000.exe /VERYSILENT`; restore the
   backup.

The script `infra/scripts/install_metrics.ps1` (a Phase-5H
deliverable; not yet written) would automate steps 2-7.

> Cross-referenced by
> [`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md)
> and [`READINESS_SCORE.md`](../founder/READINESS_SCORE.md).
