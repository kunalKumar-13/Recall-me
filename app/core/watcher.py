"""Filesystem watcher — keeps the memory layer alive between launches.

Runs in the background. Bursts of file events (an editor saving, a `git
checkout`, a Dropbox sync) are batched: events accumulate in a dirty/
deleted set and are drained every `DEBOUNCE_SECONDS`, after which each
distinct file gets one re-index call.

Failure modes are silent on purpose. If `watchdog` isn't installed, the
launcher still works — it just won't auto-pick-up changes until the next
manual reindex from settings.
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from typing import List, Set

from .indexer import Indexer

DEBOUNCE_SECONDS = 8


class IndexWatcher:
    def __init__(self, indexer: Indexer, folders: List[str]) -> None:
        self.indexer = indexer
        self.folders = list(folders)
        self._observer = None
        self._dirty: Set[str] = set()
        self._deleted: Set[str] = set()
        self._lock = threading.Lock()
        self._drain_thread: threading.Thread | None = None
        self._running = False

    def start(self) -> bool:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            print(
                "[recall] watchdog not installed — background indexing disabled.",
                file=sys.stderr,
            )
            return False

        handler = self._make_handler(FileSystemEventHandler)
        self._observer = Observer()
        scheduled_any = False
        for folder in self.folders:
            try:
                if Path(folder).exists():
                    self._observer.schedule(handler, folder, recursive=True)
                    scheduled_any = True
            except Exception as e:
                print(
                    f"[recall] watcher: cannot watch {folder!r}: {e}",
                    file=sys.stderr,
                )
        if not scheduled_any:
            return False

        try:
            self._observer.start()
        except Exception as e:
            print(f"[recall] watcher: failed to start: {e}", file=sys.stderr)
            return False

        self._running = True
        self._drain_thread = threading.Thread(target=self._drain_loop, daemon=True)
        self._drain_thread.start()
        return True

    def stop(self) -> None:
        self._running = False
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=2)
            except Exception:
                pass
        self._observer = None

    def _make_handler(self, base_cls):
        watcher = self

        class _Handler(base_cls):
            def on_modified(self, event):
                if getattr(event, "is_directory", False):
                    return
                with watcher._lock:
                    watcher._dirty.add(event.src_path)
                    watcher._deleted.discard(event.src_path)

            def on_created(self, event):
                if getattr(event, "is_directory", False):
                    return
                with watcher._lock:
                    watcher._dirty.add(event.src_path)
                    watcher._deleted.discard(event.src_path)

            def on_deleted(self, event):
                if getattr(event, "is_directory", False):
                    return
                with watcher._lock:
                    watcher._deleted.add(event.src_path)
                    watcher._dirty.discard(event.src_path)

            def on_moved(self, event):
                if getattr(event, "is_directory", False):
                    return
                with watcher._lock:
                    watcher._deleted.add(event.src_path)
                    watcher._dirty.add(event.dest_path)

        return _Handler()

    def _drain_loop(self) -> None:
        while self._running:
            time.sleep(DEBOUNCE_SECONDS)
            with self._lock:
                dirty = list(self._dirty)
                deleted = list(self._deleted)
                self._dirty.clear()
                self._deleted.clear()
            for p in dirty:
                try:
                    self.indexer.index_file(p)
                except Exception:
                    pass
            for p in deleted:
                try:
                    self.indexer.remove_file(p)
                except Exception:
                    pass
