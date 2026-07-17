"""Headless service mode — `recall.py --service`.

Starts only what the daemon needs to capture and serve real work:

  • the local memory API on 127.0.0.1:4545 (ingestion + retrieval),
  • the filesystem index watcher over the configured folders,
  • event capture (the EventLogger behind the API).

It does **not** import PyQt6, build a QApplication, show a launcher,
register the global hotkey, or raise a tray icon. That keeps it safe
to run from a macOS LaunchAgent at login without a GUI session.

This module is dispatched from `recall.py` before `app.main` is
imported, so the Qt stack is never loaded in service mode.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from .core.config import CHROMA_DIR, CONFIG_DIR, Config
from .core.events import EventLogger
from api import APIService  # type: ignore[import-not-found]

# The file-search stack (chromadb + sentence-transformers + torch) is
# optional at runtime: the bundled daemon ships without it to stay
# small, and /v1/search/files answers `enabled: false` — a calm
# state, not an error. Importing lazily inside run() keeps the
# frozen binary from even trying to load torch at boot.

log = logging.getLogger("recall.service")

INSTANCE_LOCK = CONFIG_DIR / "instance.lock"


# ---------------------------------------------------------------- single-instance
# Reimplemented here (rather than imported from app.main) so service
# mode stays free of the Qt import that app.main carries at module top.


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


def _acquire_lock() -> Optional[Path]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if INSTANCE_LOCK.exists():
        try:
            other = int(INSTANCE_LOCK.read_text(encoding="utf-8").strip() or "0")
        except (OSError, ValueError):
            other = 0
        if other and other != os.getpid() and _pid_alive(other):
            return None
    try:
        INSTANCE_LOCK.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        return None
    return INSTANCE_LOCK


def _release_lock() -> None:
    try:
        if INSTANCE_LOCK.exists():
            if INSTANCE_LOCK.read_text(encoding="utf-8").strip() == str(os.getpid()):
                INSTANCE_LOCK.unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- entrypoint


def run_service() -> int:
    """Run the headless daemon until SIGTERM/SIGINT. Returns an exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )
    log.info("recall service starting (pid=%s, python=%s)", os.getpid(),
             sys.version.split()[0])

    lock = _acquire_lock()
    if lock is None:
        log.warning("another Recall instance is already running — exiting.")
        return 0

    config = Config.load()
    log.info("config loaded: %d indexed folder(s), port=%d",
             len(config.indexed_folders), config.browser_ingest_port)

    # Capture: the EventLogger is the sink behind every /v1/events/* route.
    event_logger = EventLogger(enabled=config.episodic_enabled)

    # File index + watcher: keep ~/.recall/chroma in step with the
    # configured folders so file search stays fresh across reboots.
    # The whole stack is optional — a bundled daemon without the
    # embedding packages runs everything else at full fidelity.
    watcher = None
    search_engine = None
    try:
        from .core.embeddings import EmbeddingModel
        from .core.indexer import Indexer
        from .core.search import SearchEngine
        from .core.watcher import IndexWatcher
        from .db.store import VectorStore

        store = VectorStore(CHROMA_DIR)
        model = EmbeddingModel.get(config.embedding_model)
        indexer = Indexer(config, store, model)
        search_engine = SearchEngine(store, model)

        if config.indexed_folders:
            # Watcher-forward indexing: the watcher embeds files as
            # they are created or modified, so real work from today
            # onward is captured into file search. We deliberately do
            # NOT run a full historical index pass here — folders are
            # large, file search is secondary to event capture, and
            # any prior pass is already on disk in ~/.recall/chroma.
            watcher = IndexWatcher(indexer, list(config.indexed_folders))
            started = watcher.start()
            log.info("watcher running: %s (%d folder(s))",
                     started, len(config.indexed_folders))
            if not started:
                watcher = None
        else:
            log.info("no indexed folders configured — watcher idle.")
    except Exception:
        log.info("file-search stack unavailable — "
                 "/v1/search/files will answer enabled:false")

    # Local memory API — ingestion (capture) + retrieval. Same wiring as
    # the GUI path in app.main, minus everything Qt.
    api = APIService(
        event_logger=event_logger,
        port=config.browser_ingest_port,
        excluded_domains=config.browser_excluded_domains,
        enabled=config.browser_ingest_enabled,
        resurfacing_enabled=getattr(config, "resurfacing_enabled", True),
        threads_enabled=getattr(config, "threads_enabled", True),
        evolution_enabled=getattr(config, "evolution_enabled", True),
        recovery_enabled=getattr(config, "recovery_enabled", True),
        # Same store + model the watcher indexes into — the daemon now
        # answers /v1/search/files for every client (launcher,
        # extension, editors) instead of keeping file search in-process.
        file_search_engine=search_engine,
    )
    api_started = api.start()
    log.info("api service: %s on 127.0.0.1:%d",
             "running" if api_started else "NOT started", config.browser_ingest_port)

    # Desktop focus capture — explicit opt-in (config + RECALL_DESKTOP).
    # Windows and macOS have probes; anywhere else this is a quiet no-op.
    desktop_watcher = None
    if getattr(config, "desktop_capture_enabled", False):
        from .core.desktop.watcher import start_watcher as start_desktop_watcher

        desktop_watcher = start_desktop_watcher(event_logger)
        log.info("desktop watcher: %s",
                 "running" if desktop_watcher else "not started")
    else:
        log.info("desktop watcher: disabled by config.")

    # Block until a termination signal. launchd sends SIGTERM on logout
    # or `launchctl bootout`; Ctrl-C sends SIGINT when run by hand.
    stop = threading.Event()

    def _on_signal(signum, _frame):
        log.info("received signal %s — shutting down.", signum)
        stop.set()

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)

    log.info("recall service ready.")
    try:
        stop.wait()
    finally:
        if watcher is not None:
            try:
                watcher.stop()
            except Exception:
                pass
        if desktop_watcher is not None:
            try:
                desktop_watcher.stop()  # flushes any open focus block
            except Exception:
                pass
        try:
            api.stop()
        except Exception:
            pass
        _release_lock()
        log.info("recall service stopped.")
    return 0
