"""Settings dialog — manage indexed folders and trigger reindex.

Scope is intentionally tiny: folder list, OCR toggle, Index Now /
Cancel. No model picker, no chunk-size knobs, no theme switcher. The
PRD called for one magical interaction; settings exists only to feed it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from ..core import autostart
from ..core.config import Config
from ..core.events import EventLogger, EventStore, forget_all, forget_window
from ..core.indexer import Indexer, IndexProgress
from ..core.ingest import IngestServer
from .styles import SETTINGS_QSS, TEXT_DIM


class IndexWorker(QThread):
    progress = pyqtSignal(object)
    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, indexer: Indexer, folders: List[str]) -> None:
        super().__init__()
        self.indexer = indexer
        self.folders = folders

    def run(self) -> None:
        try:
            result = self.indexer.index_folders(self.folders, progress_cb=self._cb)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(str(e))

    def _cb(self, p: IndexProgress) -> None:
        self.progress.emit(p)

    def stop(self) -> None:
        self.indexer.cancel()


class SettingsDialog(QDialog):
    def __init__(
        self,
        config: Config,
        indexer: Indexer,
        store_count: int = 0,
        parent=None,
        event_logger: Optional[EventLogger] = None,
        ingest_server: Optional[IngestServer] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.indexer = indexer
        # Episodic memory wiring. The store is read-only; the logger is
        # passed in so the toggle can flip its enabled flag live (no
        # restart required to disable capture).
        self.event_logger = event_logger
        self.event_store = EventStore(
            event_logger.base_dir if event_logger is not None
            else EventStore().base_dir
        )
        # Phase 1B browser memory wiring. The IngestServer reference
        # lets the dialog toggle the live server's enabled flag and
        # push exclude-list changes to it without a restart.
        self.ingest_server = ingest_server
        self._worker: Optional[IndexWorker] = None
        self.setWindowTitle("Recall — Settings")
        self.setStyleSheet(SETTINGS_QSS)
        self.setMinimumSize(580, 720)
        self._build()
        self._refresh_folder_list()
        self._refresh_status(store_count)

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        title = QLabel("Settings")
        title.setObjectName("settings_title")

        subtitle = QLabel(
            "Recall remembers files from these folders. Everything stays "
            "on this device — no cloud, no accounts, no telemetry."
        )
        subtitle.setObjectName("settings_subtitle")
        subtitle.setWordWrap(True)

        section_folders = QLabel("FOLDERS TO REMEMBER")
        section_folders.setObjectName("section")

        self.folder_list = QListWidget()

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add folder…")
        self.remove_btn = QPushButton("Remove")
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addStretch(1)

        section_prefs = QLabel("PREFERENCES")
        section_prefs.setObjectName("section")

        self.ocr_check = QCheckBox(
            "Remember text inside images (slower, requires Tesseract)"
        )
        self.ocr_check.setChecked(self.config.enable_ocr)

        self.autostart_check = QCheckBox("Start Recall when I log in")
        self.autostart_check.setChecked(self.config.launch_on_login)
        if not autostart.is_supported():
            self.autostart_check.setEnabled(False)
            self.autostart_check.setToolTip(
                "Launch on login is only available on Windows in this build."
            )

        # ── Episodic memory section (Phase 1A) ──────────────────────
        # A separate visual block from Preferences because privacy
        # controls deserve their own room. Three actions (open / forget
        # 24h / forget all) plus an on/off toggle. All operate on the
        # local event log only — nothing leaves the disk.
        section_episodic = QLabel("EPISODIC MEMORY")
        section_episodic.setObjectName("section")

        self.episodic_check = QCheckBox(
            "Remember my searches and opens (locally)"
        )
        self.episodic_check.setChecked(self.config.episodic_enabled)
        self.episodic_check.setToolTip(
            "Recall keeps a plain-text log of what you searched and opened "
            "in ~/.recall/events. Nothing is sent anywhere."
        )

        self.episodic_status = QLabel("")
        self.episodic_status.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 12px;"
        )

        episodic_btn_row = QHBoxLayout()
        self.episodic_open_btn = QPushButton("Open activity log…")
        self.episodic_open_btn.setToolTip(
            "Reveal the events folder in your file manager. Each day is "
            "a plain-text JSONL file you can read or delete by hand."
        )
        self.episodic_forget_24h_btn = QPushButton("Forget last 24 hours")
        self.episodic_forget_all_btn = QPushButton("Forget everything")
        episodic_btn_row.addWidget(self.episodic_open_btn)
        episodic_btn_row.addWidget(self.episodic_forget_24h_btn)
        episodic_btn_row.addWidget(self.episodic_forget_all_btn)
        episodic_btn_row.addStretch(1)

        # ── Browser Memory section (Phase 1B) ────────────────────
        # Local HTTP server that receives events from the bundled
        # extension. Distinct from Episodic Memory above so the user
        # can disable browser capture independently of launcher
        # capture (or vice-versa).
        section_browser = QLabel("BROWSER MEMORY")
        section_browser.setObjectName("section")

        self.browser_check = QCheckBox(
            "Capture browsing from the Recall browser extension"
        )
        self.browser_check.setChecked(self.config.browser_ingest_enabled)
        self.browser_check.setToolTip(
            "Page visits, searches, and chat sessions captured by the "
            "extension are written to the same local activity log "
            "(~/.recall/events). Nothing is ever sent to the network."
        )

        self.browser_status = QLabel("")
        self.browser_status.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 12px;"
        )

        # Excluded-domains list — small inline list with add/remove.
        self.excluded_label = QLabel("Domains never captured:")
        self.excluded_label.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; padding-top: 4px;"
        )
        self.excluded_list = QListWidget()
        self.excluded_list.setMaximumHeight(80)

        excluded_btn_row = QHBoxLayout()
        self.exclude_add_btn = QPushButton("Add domain…")
        self.exclude_remove_btn = QPushButton("Remove")
        excluded_btn_row.addWidget(self.exclude_add_btn)
        excluded_btn_row.addWidget(self.exclude_remove_btn)
        excluded_btn_row.addStretch(1)

        browser_action_row = QHBoxLayout()
        self.browser_forget_btn = QPushButton("Forget all browser events")
        self.browser_forget_btn.setToolTip(
            "Remove every captured browser_visit, browser_search, and "
            "chat_session from the activity log. Launcher events stay."
        )
        browser_action_row.addWidget(self.browser_forget_btn)
        browser_action_row.addStretch(1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")

        action_row = QHBoxLayout()
        self.index_btn = QPushButton("Refresh memory")
        self.index_btn.setObjectName("primary")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.hide()
        self.close_btn = QPushButton("Done")
        action_row.addWidget(self.index_btn)
        action_row.addWidget(self.cancel_btn)
        action_row.addStretch(1)
        action_row.addWidget(self.close_btn)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(6)
        root.addWidget(section_folders)
        root.addWidget(self.folder_list, 1)
        root.addLayout(btn_row)
        root.addSpacing(6)
        root.addWidget(section_prefs)
        root.addWidget(self.ocr_check)
        root.addWidget(self.autostart_check)
        root.addSpacing(6)
        root.addWidget(section_episodic)
        root.addWidget(self.episodic_check)
        root.addWidget(self.episodic_status)
        root.addLayout(episodic_btn_row)
        root.addSpacing(6)
        root.addWidget(section_browser)
        root.addWidget(self.browser_check)
        root.addWidget(self.browser_status)
        root.addWidget(self.excluded_label)
        root.addWidget(self.excluded_list)
        root.addLayout(excluded_btn_row)
        root.addLayout(browser_action_row)
        root.addSpacing(6)
        root.addWidget(self.status_label)
        root.addWidget(self.progress_label)
        root.addWidget(self.progress_bar)
        root.addLayout(action_row)

        self.add_btn.clicked.connect(self._add_folder)
        self.remove_btn.clicked.connect(self._remove_folder)
        self.index_btn.clicked.connect(self._start_index)
        self.cancel_btn.clicked.connect(self._cancel_index)
        self.close_btn.clicked.connect(self.accept)
        self.ocr_check.toggled.connect(self._toggle_ocr)
        self.autostart_check.toggled.connect(self._toggle_autostart)
        self.episodic_check.toggled.connect(self._toggle_episodic)
        self.episodic_open_btn.clicked.connect(self._open_episodic_folder)
        self.episodic_forget_24h_btn.clicked.connect(
            self._forget_episodic_24h
        )
        self.episodic_forget_all_btn.clicked.connect(
            self._forget_episodic_all
        )
        self.browser_check.toggled.connect(self._toggle_browser)
        self.exclude_add_btn.clicked.connect(self._add_excluded_domain)
        self.exclude_remove_btn.clicked.connect(self._remove_excluded_domain)
        self.browser_forget_btn.clicked.connect(self._forget_browser_events)

        self._refresh_episodic_status()
        self._refresh_excluded_list()
        self._refresh_browser_status()

    def _refresh_folder_list(self) -> None:
        self.folder_list.clear()
        for f in self.config.indexed_folders:
            self.folder_list.addItem(QListWidgetItem(f))

    def _refresh_status(self, count: int) -> None:
        if count > 0:
            self.status_label.setText(
                f"Remembering {count} passages across "
                f"{len(self.config.indexed_folders)} folder(s)."
            )
        else:
            self.status_label.setText(
                "No memories yet. Add a folder and click 'Refresh memory'."
            )

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose a folder to index")
        if not folder or folder in self.config.indexed_folders:
            return
        self.config.indexed_folders.append(folder)
        self.config.save()
        self._refresh_folder_list()

    def _remove_folder(self) -> None:
        item = self.folder_list.currentItem()
        if item is None:
            return
        folder = item.text()
        if folder in self.config.indexed_folders:
            self.config.indexed_folders.remove(folder)
            self.config.save()
        self._refresh_folder_list()

    def _toggle_ocr(self, checked: bool) -> None:
        self.config.enable_ocr = bool(checked)
        self.config.save()

    def _toggle_autostart(self, checked: bool) -> None:
        ok = autostart.set_enabled(bool(checked))
        if not ok and checked:
            # OS rejected the write — revert the checkbox so config stays honest.
            self.autostart_check.blockSignals(True)
            self.autostart_check.setChecked(False)
            self.autostart_check.blockSignals(False)
            self.config.launch_on_login = False
        else:
            self.config.launch_on_login = bool(checked)
        self.config.save()

    # -- episodic memory controls ---------------------------------------

    def _toggle_episodic(self, checked: bool) -> None:
        """Live toggle of the event logger's enabled flag — no restart
        needed. The persisted Config flag mirrors the live state so the
        choice survives across launches."""
        enabled = bool(checked)
        self.config.episodic_enabled = enabled
        self.config.save()
        if self.event_logger is not None:
            self.event_logger.set_enabled(enabled)
        self._refresh_episodic_status()

    def _open_episodic_folder(self) -> None:
        """Reveal the events folder in the OS file manager. The folder
        contains plain JSONL files — anyone with a text editor can audit
        what was captured."""
        path = self.event_store.base_dir
        try:
            path.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Couldn't open folder",
                f"Could not reveal {path}:\n{e}",
            )

    def _forget_episodic_24h(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Forget last 24 hours?",
            "This will permanently delete events captured in the last "
            "24 hours from the local activity log.\n\n"
            "Indexed file memories are not affected. This only removes "
            "the record of what you searched and opened.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        removed = forget_window(self.event_store.base_dir, hours=24)
        self._refresh_episodic_status(
            flash=f"Forgot {removed} event(s) from the last 24 hours."
        )

    def _forget_episodic_all(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Forget everything?",
            "This will permanently delete the entire local activity log "
            "(every searched query and every opened file).\n\n"
            "Indexed file memories are not affected. The log will start "
            "fresh from your next launcher action.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        removed = forget_all(self.event_store.base_dir)
        self._refresh_episodic_status(
            flash=f"Forgot all activity ({removed} day file(s) removed)."
        )

    def _refresh_episodic_status(self, flash: Optional[str] = None) -> None:
        if flash is not None:
            self.episodic_status.setText(flash)
            return
        # Count days captured (cheap — directory listing only).
        try:
            n_files = sum(
                1 for _ in self.event_store.base_dir.glob("*.jsonl")
            ) if self.event_store.base_dir.exists() else 0
        except OSError:
            n_files = 0
        if not self.config.episodic_enabled:
            self.episodic_status.setText(
                "Capture is paused. Existing log days are preserved."
            )
        elif n_files == 0:
            self.episodic_status.setText(
                "No activity captured yet. The log appears after your "
                "first search."
            )
        else:
            day_word = "day" if n_files == 1 else "days"
            self.episodic_status.setText(
                f"Capture is on. {n_files} {day_word} of activity on disk."
            )

        # Buttons are only meaningful when there's something to act on.
        has_data = n_files > 0
        self.episodic_open_btn.setEnabled(True)  # always: opens empty folder
        self.episodic_forget_24h_btn.setEnabled(has_data)
        self.episodic_forget_all_btn.setEnabled(has_data)

    # -- browser memory controls ----------------------------------------

    def _count_browser_events(self) -> int:
        """Cheap browser-event count (last 14 days). Used for the
        status line under the Browser Memory toggle."""
        try:
            return sum(
                1 for ev in self.event_store.iter_events(days=14)
                if ev.kind in {
                    "browser_visit", "browser_search", "chat_session"
                }
            )
        except Exception:
            return 0

    def _toggle_browser(self, checked: bool) -> None:
        """Live-flip ingestion. The HTTP server keeps listening
        regardless (so the extension's health check still works) — we
        just stop writing events when off."""
        enabled = bool(checked)
        self.config.browser_ingest_enabled = enabled
        self.config.save()
        if self.ingest_server is not None:
            self.ingest_server.set_enabled(enabled)
        self._refresh_browser_status()

    def _refresh_browser_status(self, flash: Optional[str] = None) -> None:
        if flash is not None:
            self.browser_status.setText(flash)
            return
        n_events = self._count_browser_events()
        running = (
            self.ingest_server is not None
            and self.ingest_server.is_running
        )
        port = (
            self.ingest_server.port if self.ingest_server is not None
            else self.config.browser_ingest_port
        )

        if not self.config.browser_ingest_enabled:
            line = f"Capture is paused. {n_events} browser events on disk."
        elif not running:
            line = (
                f"Server not running on port {port}. "
                "Restart Recall to retry."
            )
        elif n_events == 0:
            line = (
                f"Ready on 127.0.0.1:{port}. Install the Recall "
                "extension in Chrome or Edge to begin capture."
            )
        else:
            ev_word = "event" if n_events == 1 else "events"
            line = (
                f"Listening on 127.0.0.1:{port}. "
                f"{n_events:,} browser {ev_word} captured."
            )
        self.browser_status.setText(line)
        self.browser_forget_btn.setEnabled(n_events > 0)

    def _refresh_excluded_list(self) -> None:
        self.excluded_list.clear()
        for d in sorted(self.config.browser_excluded_domains):
            self.excluded_list.addItem(QListWidgetItem(d))

    def _add_excluded_domain(self) -> None:
        domain, ok = QInputDialog.getText(
            self,
            "Add excluded domain",
            "Domain (suffix-matched, e.g. mail.google.com or google.com):",
        )
        if not ok:
            return
        cleaned = (domain or "").strip().lower().lstrip(".")
        if not cleaned or cleaned in self.config.browser_excluded_domains:
            return
        self.config.browser_excluded_domains.append(cleaned)
        self.config.save()
        if self.ingest_server is not None:
            self.ingest_server.set_excluded_domains(
                self.config.browser_excluded_domains
            )
        self._refresh_excluded_list()

    def _remove_excluded_domain(self) -> None:
        item = self.excluded_list.currentItem()
        if item is None:
            return
        domain = item.text()
        if domain in self.config.browser_excluded_domains:
            self.config.browser_excluded_domains.remove(domain)
            self.config.save()
            if self.ingest_server is not None:
                self.ingest_server.set_excluded_domains(
                    self.config.browser_excluded_domains
                )
        self._refresh_excluded_list()

    def _forget_browser_events(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Forget all browser events?",
            "This will permanently remove every captured page visit, "
            "search, and chat session from the local activity log.\n\n"
            "Launcher events (your searches and file opens) are NOT "
            "affected — only the browser-side stream.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        removed = self._strip_browser_events_from_log()
        self._refresh_browser_status(
            flash=f"Removed {removed} browser event(s) from the log."
        )

    def _strip_browser_events_from_log(self) -> int:
        """Walk every per-day JSONL and rewrite it without any
        browser_visit / browser_search / chat_session lines. The launcher
        events on those same days are preserved, which is why we can't
        just delete the file."""
        import json

        BROWSER_KINDS = {"browser_visit", "browser_search", "chat_session"}
        if not self.event_store.base_dir.exists():
            return 0
        removed = 0
        for path in self.event_store.base_dir.glob("*.jsonl"):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            kept: list[str] = []
            for line in lines:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("kind") in BROWSER_KINDS:
                        removed += 1
                        continue
                except (json.JSONDecodeError, AttributeError):
                    pass
                kept.append(line)
            try:
                if kept:
                    path.write_text(
                        "\n".join(kept) + "\n", encoding="utf-8"
                    )
                else:
                    path.unlink()
            except OSError:
                pass
        return removed

    def _start_index(self) -> None:
        if not self.config.indexed_folders:
            QMessageBox.information(self, "No folders", "Add at least one folder first.")
            return
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = IndexWorker(self.indexer, list(self.config.indexed_folders))
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.cancel_btn.show()
        self.index_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.progress_label.setText("Scanning files…")
        self._worker.start()

    def _cancel_index(self) -> None:
        if self._worker is not None:
            self._worker.stop()
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Cancelling…")

    def _on_progress(self, p: IndexProgress) -> None:
        if p.files_total > 0:
            pct = int(p.files_done / p.files_total * 100)
            self.progress_bar.setValue(pct)
        name = p.current_file
        if len(name) > 50:
            name = name[:47] + "…"
        self.progress_label.setText(
            f"{p.files_done}/{p.files_total} files captured · {name}"
        )

    def _on_finished(self, p: IndexProgress) -> None:
        self.progress_bar.setValue(100)
        added = p.files_done - p.files_skipped
        self.progress_label.setText(
            f"Done. {added} new memory item(s) captured."
        )
        self._reset_buttons()

    def _on_failed(self, msg: str) -> None:
        QMessageBox.critical(self, "Couldn't refresh memory", msg)
        self.progress_label.setText("")
        self.progress_bar.hide()
        self._reset_buttons()

    def _reset_buttons(self) -> None:
        self.cancel_btn.hide()
        self.cancel_btn.setEnabled(True)
        self.index_btn.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
