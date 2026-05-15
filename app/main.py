"""Application entry point.

Boot-stage diagnostics are available behind a flag:

  RECALL_DEBUG=1 python recall.py        (env var)
  python recall.py --debug               (CLI flag)

When DEBUG is on, every stage logs `>> name` on entry and `[OK]/[SLOW]
name (Nms)` on exit. When off, only failures and stages that exceeded
1 s are printed — so a hang still surfaces, but the normal happy path
is silent.

Failures always print a full traceback regardless of DEBUG.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, Qt
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .core import autostart
from .core.config import CHROMA_DIR, CONFIG_DIR, Config
from .core.demo_data import DemoSearchEngine
from .core import demo_seed as _demo_seed
from .core.embeddings import EmbeddingModel
from .core.events import EventLogger
from .core.indexer import Indexer
from .core.search import SearchEngine
from .core.watcher import IndexWatcher
# Phase 2A — the local memory API replaces the Phase 1B stdlib
# IngestServer. Exposes the same surface (start/stop, set_enabled,
# set_excluded_domains, counters) so Settings doesn't need to know.
from api import APIService  # type: ignore[import-not-found]

# Demo mode — when enabled, the launcher uses an in-memory dataset of
# curated sample memories so the product can be demonstrated immediately
# without indexing real files. Activated via env var or --demo flag.
DEMO_MODE = (
    os.environ.get("RECALL_DEMO", "").strip().lower() in {"1", "true", "yes", "on"}
    or "--demo" in sys.argv
)

# Phase 4B — RECALL_DEMO_MODE=1 is the public-readiness variant. It
# triggers the same in-memory file-search demo *and* seeds the event
# log with a deterministic developer/researcher/founder/casual-
# browsing trace (`app.core.demo_seed`) so the launcher's idle
# digest lights up with "Continue where you left off" / active
# threads / "On your radar" content immediately. Used by the
# screenshot-capture pipeline and by anyone who wants to evaluate
# Recall without waiting a week for real activity to accumulate.
DEMO_FULL_MODE = (
    os.environ.get("RECALL_DEMO_MODE", "").strip().lower()
    in {"1", "true", "yes", "on"}
)
if DEMO_FULL_MODE:
    DEMO_MODE = True  # full mode is a superset of file-only demo
from .db.store import VectorStore
from .ui.hotkey import HotkeyBridge, HotkeyListener
from .ui.launcher import Launcher
from .ui.onboarding import OnboardingDialog
from .ui.settings import SettingsDialog

INSTANCE_LOCK = CONFIG_DIR / "instance.lock"
SLOW_THRESHOLD_MS = 1000


# ---------------------------------------------------------------- diagnostics

_DEBUG = (
    os.environ.get("RECALL_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    or "--debug" in sys.argv
)


def _log(msg: str) -> None:
    """Quiet in production; printed when DEBUG is on."""
    if _DEBUG:
        print(f"[boot] {msg}", file=sys.stderr, flush=True)


def _log_always(msg: str) -> None:
    """Always print. Used for failures and slow-stage warnings."""
    print(f"[boot] {msg}", file=sys.stderr, flush=True)


@contextmanager
def _step(name: str):
    """Wrap a boot stage. Always prints failures + tracebacks; prints
    timing only in DEBUG, except [SLOW] which is shown unconditionally."""
    _log(f">> {name}")
    t0 = time.time()
    try:
        yield
    except BaseException:
        elapsed_ms = int((time.time() - t0) * 1000)
        _log_always(f"[FAIL] {name} ({elapsed_ms}ms)")
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise
    elapsed_ms = int((time.time() - t0) * 1000)
    if _DEBUG:
        marker = "[OK]" if elapsed_ms < SLOW_THRESHOLD_MS else "[SLOW]"
        _log(f"{marker} {name} ({elapsed_ms}ms)")
    elif elapsed_ms >= SLOW_THRESHOLD_MS:
        _log_always(f"[SLOW] {name} ({elapsed_ms}ms)")


# ---------------------------------------------------------------- single-instance


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    except Exception:
        return False
    return True


def acquire_single_instance_lock() -> Optional[Path]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if INSTANCE_LOCK.exists():
        try:
            other_pid = int(INSTANCE_LOCK.read_text(encoding="utf-8").strip() or "0")
        except (OSError, ValueError):
            other_pid = 0
        if other_pid and other_pid != os.getpid() and _pid_alive(other_pid):
            return None
    try:
        INSTANCE_LOCK.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        return None
    return INSTANCE_LOCK


def release_single_instance_lock() -> None:
    try:
        if INSTANCE_LOCK.exists():
            content = INSTANCE_LOCK.read_text(encoding="utf-8").strip()
            if content == str(os.getpid()):
                INSTANCE_LOCK.unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- tray icon


def _make_tray_icon() -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#7c8cff"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(4, 4, 56, 56, 14, 14)
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "R")
    p.end()
    return QIcon(pix)


# ---------------------------------------------------------------- app shell


class RecallApp(QObject):
    def __init__(
        self,
        qapp: QApplication,
        config: Config,
        store: VectorStore,
        model: EmbeddingModel,
        indexer: Indexer,
        search_engine: SearchEngine,
        launcher: Launcher,
        tray: QSystemTrayIcon,
        event_logger: EventLogger,
    ) -> None:
        super().__init__()
        self.qapp = qapp
        self.config = config
        self.store = store
        self.model = model
        self.indexer = indexer
        self.search_engine = search_engine
        self.launcher = launcher
        self.launcher.request_settings.connect(self.show_settings)
        self.tray = tray
        self.tray.setToolTip("Recall — ask your computer what you forgot")
        self._build_tray_menu()
        self.tray.activated.connect(self._on_tray_activated)
        self.hotkey: Optional[HotkeyListener] = None
        self.watcher: Optional[IndexWatcher] = None
        self.event_logger = event_logger
        # Phase 2A — the local memory API. Replaces Phase 1B's
        # IngestServer; same Settings-facing surface so existing
        # UI hooks don't change. Initialised in the boot stage so
        # bind failures show up as recognisable [FAIL] / [SLOW]
        # lines under RECALL_DEBUG.
        self.ingest_server: Optional[APIService] = None

    def _build_tray_menu(self) -> None:
        menu = QMenu()
        open_action = QAction("Open Recall  (Ctrl+Space)", self)
        open_action.triggered.connect(self.show_launcher)
        settings_action = QAction("Settings…", self)
        settings_action.triggered.connect(self.show_settings)
        quit_action = QAction("Quit Recall", self)
        quit_action.triggered.connect(self.qapp.quit)
        menu.addAction(open_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_launcher()

    def show_launcher(self) -> None:
        _log("show_launcher()")
        self.launcher.show_centered()

    def toggle_launcher(self) -> None:
        if self.launcher.isVisible():
            self.launcher.hide()
        else:
            self.show_launcher()

    def show_settings(self) -> None:
        _log("show_settings()")
        if self.launcher.isVisible():
            self.launcher.hide()
        dlg = SettingsDialog(
            self.config,
            self.indexer,
            self.store.count(),
            event_logger=self.event_logger,
            ingest_server=self.ingest_server,
        )
        dlg.exec()
        # Settings may have added folders or run a refresh — refresh the
        # digest cache so the next launcher show reflects new memories.
        self.launcher.invalidate_digest()

    def maybe_first_run(self) -> None:
        if not self.config.indexed_folders:
            QTimer.singleShot(300, self._show_onboarding)

    def _show_onboarding(self) -> None:
        _log("first run → showing onboarding")
        if self.launcher.isVisible():
            self.launcher.hide()
        dlg = OnboardingDialog(self.config, self.indexer)
        dlg.indexing_started.connect(self._reset_watcher_for_folders)
        dlg.indexing_done.connect(self._on_onboarding_done)
        dlg.exec()
        # If folders are now configured, ensure the watcher is up to date.
        if self.config.indexed_folders:
            self._reset_watcher_for_folders(self.config.indexed_folders)
            # The user may have closed the dialog before indexing finished;
            # invalidate the digest cache so the launcher picks up whatever
            # was captured.
            self.launcher.invalidate_digest()

    def _on_onboarding_done(self, captured: int) -> None:
        """Called when initial indexing completes inside the onboarding dialog."""
        self.launcher.invalidate_digest()
        if self.tray.supportsMessages():
            self.tray.showMessage(
                "Recall is ready",
                f"{captured} memory item(s) captured. "
                f"Press Ctrl + Space to recall anything.",
                self.tray.icon(),
                4000,
            )

    def start_watcher(self) -> None:
        if not self.config.indexed_folders:
            return
        self.watcher = IndexWatcher(self.indexer, list(self.config.indexed_folders))
        started = self.watcher.start()
        _log(f"   watcher running: {started}")

    def _reset_watcher_for_folders(self, folders) -> None:
        if self.watcher is not None:
            try:
                self.watcher.stop()
            except Exception:
                pass
        self.watcher = IndexWatcher(self.indexer, list(folders))
        self.watcher.start()

    def cleanup(self) -> None:
        if self.hotkey is not None:
            try:
                self.hotkey.stop()
            except Exception:
                pass
        if self.watcher is not None:
            try:
                self.watcher.stop()
            except Exception:
                pass
        if self.ingest_server is not None:
            try:
                self.ingest_server.stop()
            except Exception:
                pass
        try:
            self.launcher.shutdown()
        except Exception:
            pass


# ---------------------------------------------------------------- entrypoint


def _warm_up_model(model: EmbeddingModel) -> None:
    """Run on a daemon thread at boot. First user query then feels instant."""
    try:
        model.encode_one("warmup")
        _log("warm-up: model ready")
    except Exception as e:
        _log_always(f"warm-up failed: {e}")


def main() -> int:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    if _DEBUG:
        _log("=" * 60)
        _log(f"Recall startup — pid={os.getpid()}, platform={sys.platform}")
        _log(f"python={sys.version.split()[0]}, cwd={os.getcwd()}")
        _log(f"config dir: {CONFIG_DIR}")
        _log("=" * 60)

    try:
        with _step("acquire single-instance lock"):
            lock = acquire_single_instance_lock()
            if lock is None:
                _log_always("another instance is already running — exiting.")
                return 0

        with _step("create QApplication"):
            QApplication.setQuitOnLastWindowClosed(False)
            qapp = QApplication(sys.argv)
            qapp.setApplicationName("Recall")
            qapp.setOrganizationName("Recall")

        with _step("check QSystemTrayIcon availability"):
            available = QSystemTrayIcon.isSystemTrayAvailable()
            _log(f"   isSystemTrayAvailable() = {available}")
            if not available:
                _log_always("WARNING: system tray not available; tray icon will not appear.")

        with _step("load Config"):
            config = Config.load()
            _log(
                f"   indexed_folders={len(config.indexed_folders)}, "
                f"model={config.embedding_model!r}"
            )

        with _step("initialize VectorStore"):
            store = VectorStore(CHROMA_DIR)
            count = store.count()  # forces lazy-client open
            _log(f"   chroma path: {CHROMA_DIR}")
            _log(f"   index size: {count} chunks")

        with _step("construct EmbeddingModel wrapper"):
            model = EmbeddingModel.get(config.embedding_model)

        with _step("construct Indexer + SearchEngine"):
            indexer = Indexer(config, store, model)
            if DEMO_MODE:
                _log("   DEMO_MODE active — using curated in-memory dataset")
                search_engine = DemoSearchEngine()
            else:
                search_engine = SearchEngine(store, model)

        with _step("construct EventLogger (episodic memory)"):
            if DEMO_FULL_MODE:
                # Phase 4B — point the logger at a dedicated demo
                # event dir and pre-seed it with a deterministic
                # trace. Never touches the user's real event log.
                event_logger = _demo_seed.event_logger_for_demo()
                _log(
                    "   DEMO_FULL_MODE active — seeded demo events into "
                    f"{event_logger.base_dir}"
                )
            else:
                # Honors the persisted on/off preference. The Settings
                # toggle calls set_enabled() on this instance live, so
                # a restart isn't required to disable capture.
                event_logger = EventLogger(enabled=config.episodic_enabled)
                _log(f"   episodic_enabled={config.episodic_enabled}")

        with _step("construct Launcher widget"):
            launcher = Launcher(search_engine, event_logger=event_logger)

        with _step("construct QSystemTrayIcon"):
            tray = QSystemTrayIcon(_make_tray_icon())

        with _step("RecallApp wiring"):
            app = RecallApp(
                qapp,
                config,
                store,
                model,
                indexer,
                search_engine,
                launcher,
                tray,
                event_logger=event_logger,
            )

        with _step("show tray icon"):
            tray.show()
            _log(f"   tray.isVisible() = {tray.isVisible()}")

        with _step("start embedding model warm-up thread"):
            threading.Thread(
                target=_warm_up_model, args=(model,), daemon=True
            ).start()

        with _step("register global hotkey (Ctrl+Space)"):
            bridge = HotkeyBridge()
            bridge.triggered.connect(app.toggle_launcher)
            hotkey = HotkeyListener(bridge)
            started = hotkey.start()
            app.hotkey = hotkey
            _log(f"   hotkey registered: {started}")
            if not started:
                _log_always(
                    "WARNING: Ctrl+Space hotkey not registered. "
                    "Use the tray icon to open the launcher."
                )

        with _step("start background filesystem watcher"):
            app.start_watcher()

        with _step("start local memory API (Phase 2A)"):
            # FastAPI service bound to 127.0.0.1 only. Owns ingestion,
            # episodic retrieval, session reconstruction, and
            # micro-context reconstruction. The launcher consumes it
            # over HTTP; the bundled extension POSTs to the same
            # service. No external network surface.
            api_service = APIService(
                event_logger=event_logger,
                port=config.browser_ingest_port,
                excluded_domains=config.browser_excluded_domains,
                enabled=config.browser_ingest_enabled,
                resurfacing_enabled=getattr(
                    config, "resurfacing_enabled", True
                ),
                threads_enabled=getattr(
                    config, "threads_enabled", True
                ),
                evolution_enabled=getattr(
                    config, "evolution_enabled", True
                ),
                recovery_enabled=getattr(
                    config, "recovery_enabled", True
                ),
            )
            started = api_service.start()
            app.ingest_server = api_service  # legacy attribute name
            _log(
                f"   api service: {'running' if started else 'NOT started'} "
                f"on 127.0.0.1:{config.browser_ingest_port} "
                f"(docs at /docs-api)"
            )
            if not started:
                _log_always(
                    "WARNING: local memory API could not bind to "
                    f"127.0.0.1:{config.browser_ingest_port} "
                    "(port in use?). Launcher retrieval will fall back to "
                    "empty results until the next restart."
                )

        with _step("sync launch-on-login from config"):
            if autostart.is_supported() and config.launch_on_login:
                ok = autostart.set_enabled(True)
                _log(f"   autostart re-applied: {ok}")

        with _step("connect aboutToQuit cleanup"):
            def _on_quit() -> None:
                _log("aboutToQuit → cleanup()")
                app.cleanup()
                release_single_instance_lock()
            qapp.aboutToQuit.connect(_on_quit)

        with _step("schedule first-run check"):
            app.maybe_first_run()

        if _DEBUG:
            _log("=" * 60)
            _log("ALL BOOT STAGES OK — entering Qt event loop.")
            _log("=" * 60)

        rc = qapp.exec()
        _log(f"<< Qt event loop exited (rc={rc})")
        return rc

    except BaseException:
        _log_always("--- startup aborted ---")
        return 1


if __name__ == "__main__":
    sys.exit(main())
