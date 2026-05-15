"""First-run onboarding.

Replaces the old behavior of opening the settings dialog on a blank
config. The user sees a calm, premium welcome with sensible defaults
(Documents and Desktop pre-checked), a privacy reassurance, and one
button to start.

The initial index runs in the dialog's IndexWorker thread. The user
can close the dialog before it finishes — indexing continues.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.config import Config
from ..core.indexer import IndexProgress, Indexer
from .styles import (
    ACCENT,
    ACCENT_DIM,
    BG,
    BG_RAISED,
    BORDER,
    TEXT,
    TEXT_DIM,
    TEXT_DIMMER,
)


_ONBOARDING_QSS = f"""
QDialog {{ background: {BG}; color: {TEXT}; }}
QLabel {{ color: {TEXT}; }}
QLabel#title {{
    font-size: 22px;
    font-weight: 600;
    padding-bottom: 4px;
}}
QLabel#subtitle {{
    color: {TEXT_DIM};
    font-size: 13px;
    padding-bottom: 8px;
}}
QLabel#section {{
    color: {TEXT_DIMMER};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    padding-top: 6px;
    padding-bottom: 4px;
}}
QFrame#privacy_box {{
    background: rgba(40, 60, 90, 60);
    border: 1px solid rgba(100, 130, 200, 70);
    border-radius: 10px;
}}
QLabel#privacy_title {{
    color: {ACCENT};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}}
QLabel#privacy_body {{
    color: {TEXT_DIM};
    font-size: 12px;
}}
QCheckBox {{
    color: {TEXT};
    font-size: 13px;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG_RAISED};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QLabel#folder_path {{
    color: {TEXT_DIMMER};
    font-size: 11px;
}}
QPushButton {{
    background: {BG_RAISED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
}}
QPushButton:hover {{ background: rgba(50, 56, 78, 160); border-color: {ACCENT_DIM}; }}
QPushButton:disabled {{ color: {TEXT_DIMMER}; }}
QPushButton#primary {{
    background: {ACCENT_DIM};
    border-color: {ACCENT};
    color: {TEXT};
    font-weight: 600;
    padding: 9px 20px;
}}
QPushButton#primary:hover {{ background: {ACCENT}; }}
QProgressBar {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    border-radius: 5px;
    text-align: center;
    color: {TEXT};
    height: 14px;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QLabel#progress_msg {{
    color: {TEXT_DIM};
    font-size: 11px;
}}
"""


def _suggested_folders() -> List[Path]:
    """Cross-platform sensible defaults."""
    home = Path.home()
    candidates = [
        home / "Documents",
        home / "Desktop",
    ]
    return [c for c in candidates if c.exists()]


class _IndexWorker(QThread):
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


class _FolderRow(QWidget):
    def __init__(self, path: Path, checked: bool = True) -> None:
        super().__init__()
        self.path = path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.check = QCheckBox(self._display_name())
        self.check.setChecked(checked)

        path_lbl = QLabel(str(path))
        path_lbl.setObjectName("folder_path")

        layout.addWidget(self.check)
        layout.addStretch(1)
        layout.addWidget(path_lbl)

    def _display_name(self) -> str:
        return self.path.name or str(self.path)

    def is_checked(self) -> bool:
        return self.check.isChecked()


class OnboardingDialog(QDialog):
    """Shown once on first launch."""

    indexing_started = pyqtSignal(list)   # emits final folder list
    indexing_done = pyqtSignal(int)       # emits captured count when done

    def __init__(self, config: Config, indexer: Indexer) -> None:
        super().__init__()
        self.config = config
        self.indexer = indexer
        self._worker: Optional[_IndexWorker] = None
        self._extra_folders: List[Path] = []

        self.setWindowTitle("Welcome to Recall")
        self.setStyleSheet(_ONBOARDING_QSS)
        self.setMinimumSize(560, 540)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 22)
        root.setSpacing(8)

        title = QLabel("Welcome to Recall")
        title.setObjectName("title")

        subtitle = QLabel(
            "A local-first continuity layer.  Press Ctrl + Space anytime "
            "to find the tabs, files, and chats you were working with."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        # Privacy callout
        privacy = QFrame()
        privacy.setObjectName("privacy_box")
        pv = QVBoxLayout(privacy)
        pv.setContentsMargins(14, 10, 14, 12)
        pv.setSpacing(2)
        p_title = QLabel("PRIVATE BY DESIGN")
        p_title.setObjectName("privacy_title")
        p_body = QLabel(
            "Everything stays on this device. No accounts, no cloud sync, "
            "no telemetry. Your memory is yours alone."
        )
        p_body.setObjectName("privacy_body")
        p_body.setWordWrap(True)
        pv.addWidget(p_title)
        pv.addWidget(p_body)

        section = QLabel("PICK FOLDERS TO REMEMBER")
        section.setObjectName("section")

        # Folder rows
        self._folder_container = QWidget()
        self._folder_layout = QVBoxLayout(self._folder_container)
        self._folder_layout.setContentsMargins(0, 0, 0, 0)
        self._folder_layout.setSpacing(6)
        self._folder_rows: List[_FolderRow] = []

        for p in _suggested_folders():
            self._add_folder_row(p, checked=True)

        add_btn = QPushButton("+ Add another folder…")
        add_btn.clicked.connect(self._on_add_folder)

        # Progress (hidden until Start)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        self.progress_msg = QLabel("")
        self.progress_msg.setObjectName("progress_msg")
        self.progress_msg.hide()

        # Actions
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 8, 0, 0)
        self.skip_btn = QPushButton("Skip for now")
        self.start_btn = QPushButton("Start remembering")
        self.start_btn.setObjectName("primary")
        self.done_btn = QPushButton("Continue")
        self.done_btn.hide()

        actions.addWidget(self.skip_btn)
        actions.addStretch(1)
        actions.addWidget(self.start_btn)
        actions.addWidget(self.done_btn)

        self.skip_btn.clicked.connect(self.reject)
        self.start_btn.clicked.connect(self._on_start)
        self.done_btn.clicked.connect(self.accept)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(privacy)
        root.addWidget(section)
        root.addWidget(self._folder_container)
        root.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignLeft)
        root.addStretch(1)
        root.addWidget(self.progress_bar)
        root.addWidget(self.progress_msg)
        root.addLayout(actions)

    # ------------------------------------------------------------ folders

    def _add_folder_row(self, path: Path, checked: bool = True) -> None:
        if any(r.path == path for r in self._folder_rows):
            return
        row = _FolderRow(path, checked=checked)
        self._folder_layout.addWidget(row)
        self._folder_rows.append(row)

    def _on_add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pick a folder to remember")
        if not folder:
            return
        self._add_folder_row(Path(folder), checked=True)

    def _selected_folders(self) -> List[str]:
        return [str(r.path) for r in self._folder_rows if r.is_checked()]

    # ------------------------------------------------------------ index

    def _on_start(self) -> None:
        folders = self._selected_folders()
        if not folders:
            self.progress_msg.setText("Pick at least one folder, or click Skip.")
            self.progress_msg.show()
            return

        # Save config first so a crash mid-index doesn't lose folder selection.
        self.config.indexed_folders = folders
        self.config.save()

        self.start_btn.hide()
        self.skip_btn.hide()
        self.done_btn.show()
        self.progress_bar.show()
        self.progress_msg.setText("Building your memory… you can close this window any time.")
        self.progress_msg.show()

        self._worker = _IndexWorker(self.indexer, folders)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()
        self.indexing_started.emit(folders)

    def _on_progress(self, p: IndexProgress) -> None:
        if p.files_total > 0:
            pct = int(p.files_done / p.files_total * 100)
            self.progress_bar.setValue(pct)
        self.progress_msg.setText(
            f"Captured {p.files_done - p.files_skipped} of {p.files_total} files… "
            f"you can close this any time."
        )

    def _on_finished(self, p: IndexProgress) -> None:
        self.progress_bar.setValue(100)
        captured = p.files_done - p.files_skipped
        self.progress_msg.setText(
            f"Done — {captured} memory item(s) captured. Press Ctrl + Space to recall anything."
        )
        self.indexing_done.emit(captured)

    def _on_failed(self, msg: str) -> None:
        self.progress_msg.setText(f"Couldn't finish: {msg}")
