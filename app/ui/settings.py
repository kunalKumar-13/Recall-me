"""Settings dialog — manage indexed folders and trigger reindex.

Scope is intentionally tiny: folder list, OCR toggle, Index Now /
Cancel. No model picker, no chunk-size knobs, no theme switcher. The
PRD called for one magical interaction; settings exists only to feed it.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
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
from ..core.indexer import Indexer, IndexProgress
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
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.indexer = indexer
        self._worker: Optional[IndexWorker] = None
        self.setWindowTitle("Recall — Settings")
        self.setStyleSheet(SETTINGS_QSS)
        self.setMinimumSize(560, 520)
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
