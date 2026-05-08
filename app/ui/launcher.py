"""Floating Spotlight-style launcher with side-by-side preview pane.

Layout (results state):

  ┌─────────────────────────────────────────────────────────┐
  │  [search input]                                          │
  ├─────────────────────────────────────────────────────────┤
  │  ┌── results list ──┐  ┌── preview pane ──────────────┐ │
  │  │ row 1            │  │  filename                     │ │
  │  │ row 2 (selected) │  │  /full/path                   │ │
  │  │ row 3            │  │  ─────                        │ │
  │  │ ...              │  │  why matched                  │ │
  │  │                  │  │  ───── excerpt …              │ │
  │  │                  │  │  Related: …                   │ │
  │  └──────────────────┘  └──────────────────────────────┘ │
  ├─────────────────────────────────────────────────────────┤
  │  [footer]                                                │
  └─────────────────────────────────────────────────────────┘

Sizing — deterministic per state, via `self.resize(W, H)`:

  H_COMPACT  hint state
  H_EMPTY    no folders indexed
  H_RESULTS  results state (taller — accommodates preview pane)

Visual layering — outer launcher widget is fully transparent and
provides margin for a drop shadow; an inner card holds the visible UI
with rgba background. Shadow + translucency give the floating glass
look without platform-specific blur APIs.
"""

from __future__ import annotations

import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

from PyQt6.QtCore import (
    QEvent,
    QObject,
    QSize,
    QThread,
    QTimer,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QKeyEvent, QShowEvent
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.search import SearchEngine, SearchResult
from .styles import LAUNCHER_QSS
from .widgets import (
    DigestRow,
    MemoryGroup,
    PreviewPane,
    ResultItemWidget,
    cluster_results,
    derive_memory_title,
    explain_match,
    make_result_item,
)

MAX_RESULTS = 8
DEBOUNCE_MS = 90

# Visible card dimensions
CARD_WIDTH = 760
INPUT_H = 52
FOOTER_H = 34

H_COMPACT = 160
H_EMPTY = 220
H_RESULTS = 600
H_DIGEST = 460  # weekly review surface — RECENTLY ACTIVE + RESURFACED

DIGEST_RECENT_MAX = 4
DIGEST_RESURFACED_MAX = 2
RESURFACED_MIN_AGE_DAYS = 30

# Outer transparent margin around the card — leaves room for the drop
# shadow to render without clipping. Total launcher size = card + 2 × this.
SHADOW_MARGIN = 18

LAUNCHER_WIDTH = CARD_WIDTH + 2 * SHADOW_MARGIN

# Results state internal split
LIST_WIDTH = 320

_FOOTER_DEFAULT = (
    "↑↓ navigate    ↵ open    Ctrl+↵ reveal    "
    "Ctrl+C copy path    Ctrl+M copy memory    Esc close"
)
_FOOTER_FLASH_MS = 1500
_PLACEHOLDER = "What are you trying to remember?"


def _open_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    try:
        if sys.platform == "win32":
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
    except Exception:
        pass


def _reveal(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", str(p)], check=False)
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p.parent)], check=False)
    except Exception:
        pass


class _SearchWorker(QObject):
    finished = pyqtSignal(str, list)
    failed = pyqtSignal(str, str)

    def __init__(self, engine: SearchEngine) -> None:
        super().__init__()
        self.engine = engine

    def handle(self, query: str) -> None:
        try:
            results = self.engine.search(query, top_k=MAX_RESULTS)
            self.finished.emit(query, results)
        except Exception as e:
            self.failed.emit(query, str(e))


class Launcher(QWidget):
    request_settings = pyqtSignal()
    _request_search = pyqtSignal(str)

    def __init__(self, search_engine: SearchEngine) -> None:
        super().__init__()
        self.search_engine = search_engine
        self._latest_query = ""
        self._index_was_empty: bool | None = None
        self._state: str = "compact"
        self._rows: list[tuple[QListWidgetItem, ResultItemWidget]] = []
        self._indexed_files_cache: dict[str, float] | None = None

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._dispatch)

        self._thread = QThread(self)
        self._worker = _SearchWorker(search_engine)
        self._worker.moveToThread(self._thread)
        self._request_search.connect(self._worker.handle)
        self._worker.finished.connect(self._on_results)
        self._worker.failed.connect(self._on_failed)
        self._thread.start()

        self._build()
        self.resize(
            LAUNCHER_WIDTH,
            H_COMPACT + 2 * SHADOW_MARGIN,
        )

    # ------------------------------------------------------------------ build

    def _build(self) -> None:
        self.setObjectName("launcher")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(LAUNCHER_QSS)
        self.setFixedWidth(LAUNCHER_WIDTH)

        # Outer (transparent) layout — provides shadow margin
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN
        )
        outer.setSpacing(0)

        # Inner card — visible bg, border, shadow effect
        self.card = QWidget()
        self.card.setObjectName("launcher_card")
        self.card.setFixedWidth(CARD_WIDTH)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 130))
        self.card.setGraphicsEffect(shadow)

        outer.addWidget(self.card)

        root = QVBoxLayout(self.card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- search input ---------------------------------------------------
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText(_PLACEHOLDER)
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setFixedHeight(INPUT_H)
        self.setFocusProxy(self.search_input)

        # --- hint label (compact / no-results / error) ----------------------
        self.hint_label = QLabel("Type to recall something across your indexed memories.")
        self.hint_label.setObjectName("hint")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        self.hint_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # --- empty-index welcome -------------------------------------------
        self.empty_widget = QWidget()
        ev = QVBoxLayout(self.empty_widget)
        ev.setContentsMargins(0, 0, 0, 0)
        ev.setSpacing(2)
        empty_title = QLabel("Recall — your second brain for your laptop")
        empty_title.setObjectName("empty_title")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_body = QLabel(
            "No memories indexed yet. Open Settings from the tray icon "
            "to add a folder, then press Ctrl + Space to ask your computer "
            "what you forgot."
        )
        empty_body.setObjectName("empty_body")
        empty_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_body.setWordWrap(True)
        ev.addStretch(1)
        ev.addWidget(empty_title)
        ev.addWidget(empty_body)
        ev.addStretch(1)
        self.empty_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.empty_widget.hide()

        # --- digest panel (calm weekly review when input is empty) ---------
        self.digest_panel = QWidget()
        dp = QVBoxLayout(self.digest_panel)
        dp.setContentsMargins(0, 4, 0, 6)
        dp.setSpacing(0)

        recent_header = QLabel("Recently active")
        recent_header.setObjectName("digest_section")

        self.digest_list = QListWidget()
        self.digest_list.setObjectName("digest")
        self.digest_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.digest_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.digest_list.setUniformItemSizes(True)
        self.digest_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.digest_list.itemClicked.connect(self._on_digest_clicked)

        self.resurfaced_header = QLabel("Resurfaced this week")
        self.resurfaced_header.setObjectName("digest_section")

        self.resurfaced_list = QListWidget()
        self.resurfaced_list.setObjectName("digest")
        self.resurfaced_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resurfaced_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.resurfaced_list.setUniformItemSizes(True)
        self.resurfaced_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.resurfaced_list.itemClicked.connect(self._on_digest_clicked)

        dp.addWidget(recent_header)
        dp.addWidget(self.digest_list)
        dp.addWidget(self.resurfaced_header)
        dp.addWidget(self.resurfaced_list)
        dp.addStretch(0)

        self.digest_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.digest_panel.hide()

        # --- results body: list + preview side-by-side ---------------------
        self.results_body = QWidget()
        rb = QHBoxLayout(self.results_body)
        rb.setContentsMargins(0, 0, 0, 0)
        rb.setSpacing(0)

        self.results = QListWidget()
        self.results.setObjectName("results")
        self.results.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.results.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.results.setUniformItemSizes(True)
        self.results.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.results.setFixedWidth(LIST_WIDTH)

        self.preview = PreviewPane()
        self.preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        rb.addWidget(self.results)
        rb.addWidget(self.preview, 1)

        self.results_body.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.results_body.hide()

        # --- footer ---------------------------------------------------------
        self.footer = QLabel(_FOOTER_DEFAULT)
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setFixedHeight(FOOTER_H)
        self._footer_flash_timer = QTimer(self)
        self._footer_flash_timer.setSingleShot(True)
        self._footer_flash_timer.timeout.connect(
            lambda: self.footer.setText(_FOOTER_DEFAULT)
        )

        # --- assembly -------------------------------------------------------
        root.addWidget(self.search_input)
        root.addWidget(self.hint_label, 1)
        root.addWidget(self.empty_widget, 1)
        root.addWidget(self.digest_panel, 1)
        root.addWidget(self.results_body, 1)
        root.addWidget(self.footer)

        for _ in range(MAX_RESULTS):
            item = make_result_item()
            widget = ResultItemWidget()
            self.results.addItem(item)
            self.results.setItemWidget(item, widget)
            item.setHidden(True)
            self._rows.append((item, widget))

        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._on_enter)
        self.results.itemActivated.connect(self._open_item)
        self.results.itemClicked.connect(self._open_item)
        self.results.currentRowChanged.connect(self._on_row_changed)

    # -------------------------------------------------------- state transitions

    def _enter_state(self, state: str, target_card_h: int) -> None:
        if self._state == state:
            return
        self._state = state
        self.resize(LAUNCHER_WIDTH, target_card_h + 2 * SHADOW_MARGIN)

    def _hide_all_bodies(self) -> None:
        self.hint_label.hide()
        self.empty_widget.hide()
        self.digest_panel.hide()
        self.results_body.hide()

    def _show_compact(self, hint_text: str | None = None) -> None:
        if hint_text is not None:
            self.hint_label.setText(hint_text)
        if self._state != "compact":
            self._hide_all_bodies()
            self.hint_label.show()
        self._enter_state("compact", H_COMPACT)

    def _show_empty(self) -> None:
        if self._state != "empty":
            self._hide_all_bodies()
            self.empty_widget.show()
        self._enter_state("empty", H_EMPTY)

    def _show_digest(self) -> None:
        if self._state != "digest":
            self._hide_all_bodies()
            self.digest_panel.show()
        self._enter_state("digest", H_DIGEST)

    def _show_results(self) -> None:
        if self._state != "results":
            self._hide_all_bodies()
            self.results_body.show()
        self._enter_state("results", H_RESULTS)

    # ----------------------------------------------------------------- show

    def show_centered(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        self._refresh_empty_state()
        self.move(
            screen.center().x() - LAUNCHER_WIDTH // 2,
            screen.top() + int(screen.height() * 0.20),
        )
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self._activate_input)

    def _activate_input(self) -> None:
        if not self.isVisible():
            return
        self.activateWindow()
        self.search_input.setFocus(Qt.FocusReason.PopupFocusReason)
        self.search_input.selectAll()

    def showEvent(self, event: QShowEvent) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.search_input.setFocus(Qt.FocusReason.PopupFocusReason)
        self.search_input.selectAll()

    def _refresh_idle_state(self) -> None:
        """Pick the right "no query" state: welcome / digest."""
        try:
            empty = self.search_engine.store.count() == 0
        except Exception:
            empty = False
        self._index_was_empty = empty
        if empty:
            self._show_empty()
        else:
            self._populate_digest()
            self._show_digest()

    # back-compat alias used elsewhere in the file
    _refresh_empty_state = _refresh_idle_state

    def invalidate_digest(self) -> None:
        """Drop the cached indexed-files map so the next show() re-reads it.

        Called after the user runs onboarding or a manual reindex from
        settings — those flows add new memories the launcher should pick up.
        """
        self._indexed_files_cache = None

    def _populate_digest(self) -> None:
        """Fill both digest sections from the indexed files map.

        RECENTLY ACTIVE = top-N most recently modified.
        RESURFACED      = older items (>= 30 days), deterministic-shuffled
                          by today's date so the surface refreshes daily.
        """
        indexed = self._indexed_files()
        now = time.time()
        cutoff = now - RESURFACED_MIN_AGE_DAYS * 86400

        recent = sorted(
            ((p, m) for p, m in indexed.items() if m >= cutoff),
            key=lambda kv: kv[1],
            reverse=True,
        )[:DIGEST_RECENT_MAX]

        older = [(p, m) for p, m in indexed.items() if m < cutoff]
        if older:
            today_seed = int(now // 86400)
            rng = random.Random(today_seed)
            rng.shuffle(older)
            resurfaced: list[Tuple[str, float]] = older[:DIGEST_RESURFACED_MAX]
        else:
            resurfaced = []

        # If we have very little recent activity, pad from older to keep the
        # surface useful — but never duplicate.
        if len(recent) < DIGEST_RECENT_MAX:
            seen = {p for p, _ in recent} | {p for p, _ in resurfaced}
            extras = [
                (p, m) for p, m in
                sorted(indexed.items(), key=lambda kv: kv[1], reverse=True)
                if p not in seen
            ]
            need = DIGEST_RECENT_MAX - len(recent)
            recent = recent + extras[:need]

        self._fill_digest_list(self.digest_list, recent)
        self._fill_digest_list(self.resurfaced_list, resurfaced)

        # Hide the resurfaced section entirely when there's nothing to show
        # — quieter than an empty header.
        has_resurfaced = bool(resurfaced)
        self.resurfaced_header.setVisible(has_resurfaced)
        self.resurfaced_list.setVisible(has_resurfaced)

    def _fill_digest_list(
        self, list_widget: QListWidget, items: List[Tuple[str, float]]
    ) -> None:
        list_widget.clear()
        for path, mtime in items:
            row_w = DigestRow(path, mtime)
            row_w.clicked.connect(self._open_path_and_hide)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, DigestRow.DIGEST_ROW_HEIGHT))
            li.setData(Qt.ItemDataRole.UserRole, path)
            list_widget.addItem(li)
            list_widget.setItemWidget(li, row_w)
        # Size each list to fit its visible rows so the layout stays tight.
        h = max(1, len(items)) * DigestRow.DIGEST_ROW_HEIGHT + 8
        list_widget.setFixedHeight(h)

    def _on_digest_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(path, str):
            self._open_path_and_hide(path)

    def _open_path_and_hide(self, path: str) -> None:
        modifiers = QApplication.keyboardModifiers()
        if modifiers & (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier
        ):
            _reveal(path)
        else:
            _open_file(path)
        self.hide()

    # ------------------------------------------------------- focus / lifecycle

    def event(self, e: QEvent) -> bool:  # type: ignore[override]
        if e.type() == QEvent.Type.WindowDeactivate and self.isVisible():
            self.hide()
        return super().event(e)

    def shutdown(self) -> None:
        self._thread.quit()
        self._thread.wait(1500)

    # ---------------------------------------------------------- search flow

    def _on_text_changed(self, text: str) -> None:
        if not text.strip():
            self._latest_query = ""
            for item, _ in self._rows:
                item.setHidden(True)
            self.preview.show_empty()
            # Return to the ambient idle view (digest or welcome).
            self._refresh_idle_state()
            return
        self._search_timer.start(DEBOUNCE_MS)

    def _dispatch(self) -> None:
        query = self.search_input.text().strip()
        if not query:
            return
        self._latest_query = query
        self._request_search.emit(query)

    def _on_results(self, query: str, results: List[SearchResult]) -> None:
        if query != self._latest_query:
            return
        self._populate(query, results)

    def _on_failed(self, query: str, msg: str) -> None:
        if query != self._latest_query:
            return
        for item, _ in self._rows:
            item.setHidden(True)
        self.preview.show_empty()
        self._show_compact("Couldn't recall just now. Try different words.")

    def _populate(self, query: str, results: List[SearchResult]) -> None:
        if not results:
            for item, _ in self._rows:
                item.setHidden(True)
            self.preview.show_empty("Nothing comes to mind yet.")
            self._show_compact("Nothing comes to mind. Try different words.")
            return

        # Cluster: group results that share folder + content keywords.
        groups = cluster_results(results)

        for i, (item, widget) in enumerate(self._rows):
            if i < len(groups):
                widget.update_group(groups[i], query)
                item.setData(Qt.ItemDataRole.UserRole, groups[i])
                item.setHidden(False)
            else:
                item.setHidden(True)

        self._show_results()
        self.results.setCurrentRow(0)  # triggers _on_row_changed → preview update

    # ---------------------------------------------------------- preview

    def _on_row_changed(self, row: int) -> None:
        if row < 0 or row >= self.results.count():
            return
        item = self.results.item(row)
        if item is None or item.isHidden():
            return
        group = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(group, MemoryGroup):
            return
        # Related = same-folder peers from the index, excluding paths already
        # inside the cluster itself (those are listed under "Sources").
        already = set(group.all_paths)
        related = [
            p for p in self._related_files(group.primary.path, max_n=6)
            if p not in already
        ][:3]
        self.preview.update_group(group, self._latest_query, related)

    def _indexed_files(self) -> dict[str, float]:
        """Cached for the launcher's lifetime — `get_indexed_files` reads
        every metadata blob in the collection, so we only do it once."""
        if self._indexed_files_cache is None:
            try:
                self._indexed_files_cache = self.search_engine.store.get_indexed_files()
            except Exception:
                self._indexed_files_cache = {}
        return self._indexed_files_cache

    def _related_files(self, current_path: str, max_n: int = 3) -> list[str]:
        try:
            current = Path(current_path).resolve()
            parent = current.parent
        except Exception:
            return []
        peers: list[str] = []
        for p in self._indexed_files().keys():
            try:
                pp = Path(p)
                if pp.parent == parent and pp != current:
                    peers.append(p)
            except Exception:
                continue
        peers.sort(key=lambda x: Path(x).name.lower())
        return peers[:max_n]

    # ------------------------------------------------------ open / keyboard

    def _flash_footer(self, msg: str) -> None:
        self.footer.setText(msg)
        self._footer_flash_timer.start(_FOOTER_FLASH_MS)

    def _current_group(self) -> MemoryGroup | None:
        item = self.results.currentItem()
        if item is None or item.isHidden():
            return None
        g = item.data(Qt.ItemDataRole.UserRole)
        return g if isinstance(g, MemoryGroup) else None

    def _copy_selected_path(self) -> bool:
        group = self._current_group()
        if group is None:
            return False
        QApplication.clipboard().setText(group.primary.path)
        self._flash_footer(f"Path copied  ·  {group.primary.name}")
        return True

    def _copy_memory_summary(self) -> bool:
        """Copy a human memory blob — title, why, sources — to clipboard."""
        group = self._current_group()
        if group is None:
            return False
        title = derive_memory_title(group.primary)
        why = explain_match(self._latest_query, group.primary.chunk or group.primary.snippet)
        lines = [title, why, ""]
        if group.is_cluster:
            lines.append("Sources:")
            for p in group.all_paths:
                lines.append(f"- {p}")
        else:
            lines.append(f"Source: {group.primary.path}")
        QApplication.clipboard().setText("\n".join(lines))
        self._flash_footer(f"Memory copied  ·  {title}")
        return True

    def _on_enter(self) -> None:
        item = self.results.currentItem()
        if item is None or item.isHidden():
            for cand_item, _ in self._rows:
                if not cand_item.isHidden():
                    item = cand_item
                    break
        if item is not None and not item.isHidden():
            self._open_item(item)

    def _open_item(self, item: QListWidgetItem) -> None:
        group = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(group, MemoryGroup):
            return
        path = group.primary.path
        modifiers = QApplication.keyboardModifiers()
        if modifiers & (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier
        ):
            _reveal(path)
        else:
            _open_file(path)
        self.hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        key = event.key()
        mods = event.modifiers()
        if key == Qt.Key.Key_Escape:
            self.hide()
            return
        if (
            key == Qt.Key.Key_C
            and mods & Qt.KeyboardModifier.ControlModifier
            and self._state == "results"
        ):
            self._copy_selected_path()
            return
        if (
            key == Qt.Key.Key_M
            and mods & Qt.KeyboardModifier.ControlModifier
            and self._state == "results"
        ):
            self._copy_memory_summary()
            return
        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            visible = [i for i, (item, _) in enumerate(self._rows) if not item.isHidden()]
            if not visible:
                return
            row = self.results.currentRow()
            if row not in visible:
                row = visible[0]
            else:
                idx = visible.index(row)
                if key == Qt.Key.Key_Down and idx + 1 < len(visible):
                    row = visible[idx + 1]
                elif key == Qt.Key.Key_Up and idx > 0:
                    row = visible[idx - 1]
            self.results.setCurrentRow(row)
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_enter()
            return
        if (
            key == Qt.Key.Key_Comma
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.request_settings.emit()
            return
        super().keyPressEvent(event)
