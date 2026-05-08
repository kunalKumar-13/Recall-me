# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Recall.

Build:    pyinstaller recall.spec
Output:   dist/Recall/Recall.exe   (Windows)
          dist/Recall/Recall       (macOS / Linux)

Notes:
  • `chromadb` and `sentence_transformers` import many submodules
    dynamically — `collect_submodules` is the reliable way to bundle
    them without runtime ImportError surprises.
  • The embedding model (~80 MB) is NOT bundled. First run downloads it
    once into the HF cache; subsequent runs use `local_files_only=True`
    and never touch the network.
  • An app icon at `app/assets/icon.ico` is picked up automatically.
    Generate one with `python scripts/build_icon.py` before building.
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

a = Analysis(
    ["recall.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "IPython", "jupyter", "notebook"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
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
