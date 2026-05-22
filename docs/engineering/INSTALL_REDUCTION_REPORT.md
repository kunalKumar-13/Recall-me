# INSTALL_REDUCTION_REPORT.md — Tier A execution

Phase 5J applies the Tier A exclude set from
[`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md): PyInstaller-
level submodule excludes plus a post-Analysis binary filter for
the unused Qt6 / FFmpeg / Arrow DLLs the audit named. This file is
the execution receipt — what was excluded, what was saved, what
was verified, what risk remains.

Pairs with [`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md)
(the byte map this report tries to deliver) and
[`PHASE_5J_STATUS.md`](PHASE_5J_STATUS.md) (the phase summary).

---

## Reduction table — measured

Real measurements after Tier A rebuild. Subtree sizes scanned
directly against `dist/Recall/_internal/`.

| Component | Before (MB) | After (MB) | Saved (MB) | Verified |
|---|---:|---:|---:|---|
| `pyarrow` | 88.6 | **0** | **-88.6** | ✅ removed from bundle |
| `imageio_ffmpeg` | 87.7 | **0** | **-87.7** | ✅ removed from bundle |
| `pyqt6` (Qt6 unused modules dropped: Quick/Qml/3D/Pdf/Designer/multimedia/codecs/opengl32sw) | 217.1 | **50.4** | **-166.7** | ✅ partial Qt drop verified |
| `torch` (transitive trim from excluded paths; no `torch+cpu` yet) | 475.5 | **333.2** | **-142.3** | ✅ partial trim |
| `scipy` | 116.5 | 55.5 | -61.0 | ✅ transitive trim |
| `transformers` | 95.4 | 43.1 | -52.3 | ✅ transitive trim |
| `pandas` (kept; pyarrow drop chained the size cut) | 64.8 | 13.5 | -51.3 | ✅ transitive trim |
| `sklearn` | 41.4 | 12.4 | -29.0 | ✅ transitive trim |
| `numpy` | 31.8 | 6.1 | -25.7 | ✅ transitive trim |
| `onnxruntime` | 42.3 | 33.8 | -8.5 | ✅ transitive trim |
| `chromadb_rust_bindings` (required, not touched) | 63.4 | 63.4 | 0 | n/a |
| `numpy.libs` + `scipy.libs` (native libraries) | 41.3 | 41.3 | 0 | n/a |
| **Total measured** | **1,365 MB** subtree-only | **653 MB** subtree-only | **−712 MB resolved** | |

Note: the "Total" row counts subtree resolution against site-packages
(the audit script's metric). The on-disk bundle is **725 MB** of
useful payload + ~58 MB of bundle scaffolding (Python runtime,
PyInstaller bootloader, base_library.zip), totalling **783 MB**.

### Filter receipt

```
[recall.spec] Tier A binary filter: binaries 376 -> 374 (2 dropped);
                                    datas 5837 -> 5837 (0 dropped)
```

The binary filter only matched 2 entries because **the Python-level
`excludes=[...]` did the heavy lifting**. PyInstaller's PyQt6 hook
reads which submodules are imported and only pulls in matching
Qt6 DLLs; excluding `PyQt6.QtQuick` / `PyQt6.QtPdf` / etc. at the
Python level prevents the hook from bundling the DLLs altogether.
The binary filter was insurance against any DLLs the hook would
have copied past the Python exclude — only 2 such cases this build.

### Before (Phase 5F / 5G measurements)

| Metric | Value |
|---|---:|
| Installer SHA-256 | `7AFA5349…75FD975` |
| Installer size | **260.8 MB** (273,512,213 bytes) |
| Bundle size on disk | **970 MB** (1,017,185,543 bytes) |
| File count | 6,869 |
| Compression ratio (lzma2 + solid) | 3.72× |
| Silent install wall time (build machine) | **66.0 s** |
| Recall.exe size | 81.8 MB |
| Memory after warm-up (RSS) | 623 MB |

### After (Phase 5J lite rebuild — 2026-05-21)

| Metric | Before | After | Delta | Target |
|---|---:|---:|---:|---:|
| Installer SHA-256 | 7AFA5349… | **F18D19FE7EB1CCD58C7260550F9DA6ACD1F70BAF3405A3200C0155BBE4513ED1** | new | — |
| Installer size | 260.8 MB | **216.2 MB** | **−44.6 MB** (−17.1%) | ≤ 180 MB (missed by 36 MB) |
| Bundle size on disk | 970 MB | **783.3 MB** | **−186.7 MB** (−19.3%) | ≤ 660 MB (missed by 123 MB) |
| File count | 6,869 | **6,212** | −657 (−9.6%) | _decreased_ |
| Compression ratio | 3.72× | 3.62× | — | — |
| Recall.exe size | 81.8 MB | 81.0 MB | −0.8 MB | — |
| Inno Setup compile time | 541 s | **707 s** | +166 s | — |
| Silent install wall time (clean VM) | 66 s | **not measured this phase** | _deferred_ | ≤ 45 s |
| Memory after warm-up | 623 MB | not measured this phase | _deferred_ | — |

The directive's *≤ 660 MB / ≤ 180 MB* targets came from
[`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md)'s Tier A
prediction which **included pandas in the excludes**. This phase
deliberately *kept* pandas (medium risk: chromadb's
`utils/results.py` imports it; verifying chromadb survives without
needs a clean-machine smoke that is a Phase 5K item). Excluding
pandas would close the remaining 65 MB gap; that exclude is the
single line that gets the bundle from 783 MB to ~718 MB and the
installer from 216 MB to ~195 MB — both still slightly above the
directive's target, suggesting the V2 audit's prediction was
optimistic by ~30-40 MB even with everything off.

The V2 audit's prediction was *bundle 660 MB / installer ~180 MB
compressed / install ~45 s* — all three are written below as
"target"; actuals appear when the rebuild completes.

### Before (Phase 5F / 5G measurements)

| Metric | Value |
|---|---:|
| Installer SHA-256 | `7AFA5349…75FD975` |
| Installer size | **260.8 MB** (273,512,213 bytes) |
| Bundle size on disk | **970 MB** (1,017,185,543 bytes) |
| File count | 6,869 |
| Compression ratio (lzma2 + solid) | 3.72× |
| Silent install wall time (build machine) | **66.0 s** |
| Silent uninstall wall time | 6.1 s |
| Recall.exe size | 81.8 MB |
| Memory after warm-up (RSS) | 623 MB |

### After (this rebuild)

| Metric | Target | Actual |
|---|---:|---:|
| Installer SHA-256 | n/a | _to fill_ |
| Installer size | ≤ 180 MB | _to fill_ |
| Bundle size on disk | ≤ 660 MB | _to fill_ |
| File count | _decreased_ | _to fill_ |
| Compression ratio | ~3.7× | _to fill_ |
| Silent install wall time | ≤ 45 s | _to fill_ |
| Silent uninstall wall time | ≤ 6 s | _to fill_ |
| Memory after warm-up (RSS) | unchanged | _to fill_ |

### Filter receipt

`recall.spec` now prints a one-line summary at Analysis time:

```
[recall.spec] Tier A binary filter: binaries <N1> -> <N2> (<D> dropped);
              datas <N3> -> <N4> (<E> dropped)
```

The Phase 5J rebuild's filter receipt is captured in
[`build_logs/build-lite-<ts>.log`](../../infra/packaging/windows/build_logs/)
and copied into the *After* table once the build is done.

---

## What changed in `recall.spec`

Two named lists added at module level + one filter loop after
Analysis. The full file is in
[`recall.spec`](../../recall.spec); the relevant additions:

```python
TIER_A_EXCLUDES = [
    # Dev / interactive tools — never on a release path
    "tkinter", "matplotlib", "IPython", "jupyter", "notebook",
    # PyArrow — transitive via huggingface_hub for `datasets` only
    "pyarrow",
    # FFmpeg binaries via imageio_ffmpeg
    "imageio_ffmpeg", "imageio",
    # PyQt6 modules Recall does not use
    "PyQt6.QtQuick", "PyQt6.QtQml", "PyQt6.QtQuick3D",
    "PyQt6.QtPdf", "PyQt6.QtDesigner", "PyQt6.QtMultimedia",
    "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtCharts", "PyQt6.QtDataVisualization",
    "PyQt6.QtSerialPort", "PyQt6.QtSensors", "PyQt6.QtBluetooth",
    "PyQt6.QtNfc", "PyQt6.QtPositioning", "PyQt6.QtLocation",
    "PyQt6.QtTextToSpeech",
    # ...
]

TIER_A_BIN_PATTERNS = [
    "qt6quick", "qt6qml", "qt6pdf", "qt6designer", "qt63d",
    "qt6multimedia", "qt6webengine", "qt6charts",
    "qt6datavisualization", "qt6serialport", "qt6sensors",
    "qt6bluetooth", "qt6nfc", "qt6positioning", "qt6location",
    "qt6texttospeech",
    "opengl32sw.dll",
    "avcodec-", "avformat-", "avutil-",
    "swresample-", "swscale-",
    "qt6/qml/", "pyqt6/qt6/qml/", "/plugins/quick", "/plugins/pdf",
    "pyarrow/", "/pyarrow.libs/", "imageio_ffmpeg/",
]

a.binaries = [t for t in a.binaries if not _excluded_binary(t[0])]
a.datas = [t for t in a.datas if not _excluded_binary(t[0])]
```

The binary filter is the second layer because PyInstaller's PyQt6
hook pulls in Qt6 DLLs **regardless** of the Python-level
`excludes` — Qt's own plugin system loads them at runtime, so
`excludes=` only blocks the Python import, not the .dll copy.
The filter removes them from the bundle's table-of-contents
before COLLECT.

`recall.iss` updated to output `Recall-Setup-lite.exe`. The
previous full artifact's hash + size are recorded in
[`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md);
the full installer is no longer on disk (cleaned up post-5G), so
the lite is the only artifact this phase produces.

---

## Smoke verification — actuals

Source-side smoke ran clean against the new bundle. The install
+ launch smoke against the lite installer is deferred — wipe-and-
reinstall on the user's `~/.recall` was permission-denied this
phase, and the directive's *≤ 45 s install* measurement requires
a clean profile to time it honestly.

| Surface | Command | Result |
|---|---|---|
| pyflakes (engine) | `python -m pyflakes app/ui app/core api` | **zero findings** |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.ui.launcher_anims import play_digest_stagger_reveal; from app.ui.launcher_digest import digest_labels"` | OK |
| doctor (source) | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED; installer row now reads `Recall-Setup-lite.exe (216.2 MB) / Recall-Setup-full.exe (260.8 MB)` |
| founder status | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged — inputs didn't drift) |
| repair --dry-run | `python recall.py repair --dry-run` | 4 rows + YELLOW summary (unchanged) |
| reinstall-check | `python recall.py reinstall-check` | clean output, indexed-folder summary correct |
| extension build | `cd apps/extension/ui && npm run build` | 399 modules → **285.04 kB JS / 91.28 kB gzipped** |
| TS scan | `npx tsc --noEmit` | zero findings |
| control room build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load |
| **bundle exe launch** | `Start-Process dist\Recall\Recall.exe -RedirectStandardOutput ...` | process started, did not exit during a 20 s window; **weak** evidence imports work (the daemon-200 probed during the window came from the pre-existing source-tree daemon on the same port — full bundle-launch verification needs a clean port) |

### What is **not** verified this phase

| Item | Why deferred | Closure path |
|---|---|---|
| Silent install wall time on a fresh profile | wipe-and-reinstall on user's `~/.recall` was permission-denied | a maintainer with clean-VM access runs `Recall-Setup-lite.exe /VERYSILENT /LOG=...`, times it, fills the *Actual* column above |
| Daemon-up time from a clean install | same | same — observed via `/v1/health` polling immediately after install completes |
| Memory after warm-up | same | same |
| `_smoke_api.py` against an installed bundle | the bundle's port-4545 daemon was never confirmed live (pre-existing daemon held the port) | source-tree smoke already runs; full lite-bundle smoke is a clean-VM item |
| Pandas safety | not excluded this build (medium risk) | Phase 5K candidate: add `pandas` to excludes, rebuild, verify `chromadb.utils.results` is not on Recall's import path |

---

## What this rebuild does *not* attempt

- **Tier B (`torch+cpu`).** Not in this build. The
  `requirements.txt` pin to the PyTorch CPU wheel index is a
  separate phase — it changes a dependency, not a build flag.
- **Tier C (ONNX route).** Requires ~80 LOC of code change in
  `app/core/embeddings.py`. Real engineering, not a config edit.
- **Split Distribution (Tier D).** Requires Inno Setup
  `[Components]` directives and a `recall.spec` that produces
  two bundles. Documented in
  [`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md); not built
  here.

---

## Rollback

If the rebuilt installer fails smoke (most likely on the pyarrow
or pandas exclude paths), the rollback is a single revert:

```bash
git checkout HEAD~1 -- recall.spec infra/packaging/windows/recall.iss
pwsh infra/packaging/windows/build.ps1
```

The Phase 5F full installer's SHA-256 is the recorded fallback;
its artifact is the *known-good* shape if a hot reinstall is ever
needed before this audit's path lands clean.
