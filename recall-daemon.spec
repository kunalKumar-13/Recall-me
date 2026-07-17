# PyInstaller spec — the bundled Recall engine (`recall-daemon`).
#
# One small headless binary: the FastAPI service, the seven-layer
# engine, capture ingest, and the desktop-focus watcher. Deliberately
# EXCLUDES the GUI (PyQt6) and the file-search stack (chromadb +
# sentence-transformers + torch, ~2 GB) — /v1/search/files answers
# `enabled: false` until the full stack is present, which the whole
# product treats as a calm state.
#
# Build:  pyinstaller --noconfirm recall-daemon.spec
# Test :  HOME=$(mktemp -d) dist/recall-daemon --service
# Ship :  apps/launcher/src-tauri/binaries/recall-daemon-<triple>

a = Analysis(
    ["recall.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # uvicorn's runtime imports are dynamic
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
        # the desktop probes are imported by platform dispatch
        "app.core.desktop.darwin",
        "app.core.desktop.watcher",
    ],
    excludes=[
        # GUI — never in the daemon
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        # the optional file-search stack (service.py degrades cleanly)
        "chromadb",
        "sentence_transformers",
        "torch",
        "transformers",
        "onnxruntime",
        "tokenizers",
        "scipy",
        "sklearn",
        "pandas",
        "matplotlib",
        "PIL",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="recall-daemon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
