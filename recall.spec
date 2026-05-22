# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Recall.

Build:    pyinstaller recall.spec
Output:   dist/Recall/Recall.exe   (Windows)
          dist/Recall/Recall       (macOS / Linux)

Phase 5J: Tier A excludes applied. Pruning out unused weight by
both submodule excludes (Python-level) and binary filter (DLL-level
post-Analysis). The savings target is ~309 MB unpacked / ~80 MB
compressed. See `docs/engineering/INSTALL_SIZE_AUDIT_V2.md` for
the byte-by-byte rationale.

Notes:
  - `chromadb` and `sentence_transformers` import many submodules
    dynamically; `collect_submodules` is the reliable way to bundle
    them without runtime ImportError surprises.
  - The embedding model (~80 MB) is NOT bundled. First run downloads
    it into the HF cache; subsequent runs use `local_files_only=True`.
  - An app icon at `app/assets/icon.ico` is picked up automatically.
"""

import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None
icon_path = os.path.join("app", "assets", "icon.ico")
icon_arg = icon_path if os.path.exists(icon_path) else None

hiddenimports = (
    collect_submodules("chromadb")
    + collect_submodules("sentence_transformers")
    + collect_submodules("transformers")
    + collect_submodules("tokenizers")
    + collect_submodules("pynput")
    + collect_submodules("watchdog")
)

datas = (
    collect_data_files("chromadb")
    + collect_data_files("sentence_transformers")
    + collect_data_files("tokenizers")
)

# Tier A excludes — Python-level. These submodules are never
# imported on any Recall code path; the audit (`INSTALL_SIZE_AUDIT_V2`)
# names each. Excluding them at the Python level prevents
# PyInstaller's hooks from pulling associated binaries.
TIER_A_EXCLUDES = [
    # Dev / interactive tools — never on a release path
    "tkinter",
    "matplotlib",
    "IPython",
    "jupyter",
    "notebook",
    # PyArrow — transitive via huggingface_hub for `datasets` only;
    # Recall does not call into datasets. ~88 MB on disk.
    "pyarrow",
    # FFmpeg binaries via imageio_ffmpeg — Recall has no media path.
    # ~88 MB on disk.
    "imageio_ffmpeg",
    "imageio",
    # PyQt6 modules Recall does not use — Quick / QML / 3D / PDF /
    # Designer. Recall is QtWidgets only.
    "PyQt6.QtQuick",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtQuick3D",
    "PyQt6.QtQuickControls2",
    "PyQt6.QtQml",
    "PyQt6.QtQmlModels",
    "PyQt6.QtQmlWorkerScript",
    "PyQt6.QtPdf",
    "PyQt6.QtPdfWidgets",
    "PyQt6.QtDesigner",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebChannel",
    "PyQt6.QtCharts",
    "PyQt6.QtDataVisualization",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSensors",
    "PyQt6.QtBluetooth",
    "PyQt6.QtNfc",
    "PyQt6.QtPositioning",
    "PyQt6.QtLocation",
    "PyQt6.QtTextToSpeech",
]

# Tier A binary filter — DLLs Qt6 ships that the Python-level
# excludes do not catch because they are loaded via Qt's plugin
# system. Patterns are matched against the destination path (case
# insensitive). The filter runs against `a.binaries` and `a.datas`
# before COLLECT - bundle never sees them.
TIER_A_BIN_PATTERNS = [
    # Qt Quick / QML / 3D / Pdf / Designer DLLs
    "qt6quick",
    "qt6qml",
    "qt6pdf",
    "qt6designer",
    "qt63d",
    "qt6multimedia",
    "qt6webengine",
    "qt6webchannel",
    "qt6charts",
    "qt6datavisualization",
    "qt6serialport",
    "qt6sensors",
    "qt6bluetooth",
    "qt6nfc",
    "qt6positioning",
    "qt6location",
    "qt6texttospeech",
    # Software OpenGL fallback (~20 MB; Recall uses HW Qt rendering)
    "opengl32sw.dll",
    # FFmpeg multimedia codecs (~30 MB combined). Recall has no
    # media path; Qt Multimedia is already excluded above; these
    # are the underlying codec DLLs Qt would dlopen.
    "avcodec-",
    "avformat-",
    "avutil-",
    "swresample-",
    "swscale-",
    # Qt Quick plugins / qmldir trees (under qml/, plugins/quick*)
    "qt6/qml/",
    "pyqt6/qt6/qml/",
    "/plugins/quick",
    # Qt PDF plugin
    "/plugins/pdf",
    # pyarrow native binaries (the Python-level exclude catches the
    # python import; this catches any straggler DLL/native module).
    "pyarrow/",
    "/pyarrow.libs/",
    # imageio_ffmpeg binaries
    "imageio_ffmpeg/",
]


def _excluded_binary(dest: str) -> bool:
    """True when the destination path matches a Tier A drop pattern."""
    p = dest.replace("\\", "/").lower()
    return any(pat in p for pat in TIER_A_BIN_PATTERNS)


a = Analysis(
    ["recall.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=TIER_A_EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Phase 5J — apply the post-Analysis binary filter. Each TOC entry
# is `(dest, source, kind)`; keep entries that don't match any
# drop pattern. Print a one-line summary so the build log carries
# the receipt.
_before_bin = len(a.binaries)
_before_data = len(a.datas)
a.binaries = [t for t in a.binaries if not _excluded_binary(t[0])]
a.datas = [t for t in a.datas if not _excluded_binary(t[0])]
print(
    f"[recall.spec] Tier A binary filter: "
    f"binaries {_before_bin} -> {len(a.binaries)} "
    f"({_before_bin - len(a.binaries)} dropped); "
    f"datas {_before_data} -> {len(a.datas)} "
    f"({_before_data - len(a.datas)} dropped)"
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Recall",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_arg,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Recall",
)
