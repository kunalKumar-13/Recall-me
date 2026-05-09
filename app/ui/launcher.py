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
from PyQt6.QtGui import QColor, QCursor, QFont, QKeyEvent, QShowEvent
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

from ..core.demo_data import DemoSearchEngine
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

# Visible card dimensions — tuned for command-bar restraint (Spotlight /
# Raycast / Linear-menu feel). Width is the single largest perceived-size
# lever, so it shrunk first; vertical sizing then follows from row heights.
CARD_WIDTH = 620
INPUT_H = 46
FOOTER_H = 28

# Idle-state heights are constant (the digest / hint / empty surfaces are
# stable shapes). The results state is adaptive — see _show_results.
H_COMPACT = 110
H_EMPTY = 180
H_DIGEST = 400

# Adaptive results bounds. Floor lets a single result still feel like a
# proper command bar (not a blink); ceiling caps the launcher so a full
# 8-result set never dominates the screen.
H_RESULTS_MIN = 280
H_RESULTS_MAX = 480

DIGEST_RECENT_MAX = 4
DIGEST_RESURFACED_MAX = 2
RESURFACED_MIN_AGE_DAYS = 30

# Outer transparent margin around the card — leaves room for the (now
# softer) drop shadow to render without clipping.
SHADOW_MARGIN = 16

LAUNCHER_WIDTH = CARD_WIDTH + 2 * SHADOW_MARGIN

# Results state internal split. The list keeps the full 320 px so titles
# and "why" lines stay legible; the preview pane shrinks instead — making
# it feel like contextual support rather than the dominant surface.
LIST_WIDTH = 320

# Footer keeps only the two universally-useful actions. Power keys
# (Ctrl+↵, Ctrl+C, Ctrl+M) still work — they're documented in Settings.
_FOOTER_DEFAULT = "↑↓ navigate     ↵ open     esc close"
_FOOTER_FLASH_MS = 1500
_PLACEHOLDER = "What are you trying to remember?"


def _open_file(path: str) -> bool:
    """Open `path` with the OS handler. Returns True only when we actually
    handed the file to the OS — False when the path is missing (demo
    memories, files moved/deleted since indexing) or the launch raised.
    Callers use the bool to decide whether to acknowledge success or
    surface a 'memory unavailable' message instead of silently closing.
    """
    p = Path(path)
    if not p.exists():
        return False
    try:
        if sys.platform == "win32":
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
        return True
    except Exception:
        return False


def _reveal(path: str) -> bool:
    p = Path(path)
    if not p.exists():
        return False
    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", str(p)], check=False)
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p.parent)], check=False)
        return True
    except Exception:
        return False


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


class _InputKeyFilter(QObject):
    """Single source of truth for keyboard contract on the search input.

    QLineEdit's handling of Enter / Esc / Up / Down has historically
    varied across Qt versions, IME states, and platform keyboard
    layouts — Enter sometimes fires returnPressed and propagates,
    sometimes consumes; Esc sometimes clears the selection and goes
    no further. Routing every navigation key through this filter makes
    the behavior deterministic regardless of Qt internals: arrows always
    move the result selection, Enter always opens, Esc always closes.
    """

    def __init__(self, launcher: "Launcher") -> None:
        super().__init__(launcher)
        self.launcher = launcher

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(obj, event)
        key = event.key()  # type: ignore[attr-defined]
        mods = event.modifiers()  # type: ignore[attr-defined]

        if key == Qt.Key.Key_Escape:
            self.launcher.hide()
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.launcher._on_enter()
            return True
        if key == Qt.Key.Key_Down:
            self.launcher._move_selection(1)
            return True
        if key == Qt.Key.Key_Up:
            self.launcher._move_selection(-1)
            return True
        if mods & Qt.KeyboardModifier.ControlModifier:
            # Only intercept Ctrl+C / Ctrl+M when the results pane is on
            # screen — otherwise let QLineEdit handle the user's normal
            # "copy selected input text" behaviour.
            if key == Qt.Key.Key_C and self.launcher._state == "results":
                if self.launcher._copy_selected_path():
                    return True
            elif key == Qt.Key.Key_M and self.launcher._state == "results":
                if self.launcher._copy_memory_summary():
                    return True
            elif key == Qt.Key.Key_Comma:
                self.launcher.request_settings.emit()
                return True
        return super().eventFilter(obj, event)


class Launcher(QWidget):
    request_settings = pyqtSignal()
    _request_search = pyqtSignal(str)

    def __init__(self, search_engine: SearchEngine) -> None:
        super().__init__()
        self.search_engine = search_engine
        # Demo mode is detected from the engine type, not an env var, so
        # the launcher never has to look at process-wide globals. The flag
        # only changes how missing-file open attempts are presented.
        self._demo_mode = isinstance(search_engine, DemoSearchEngine)
        self._latest_query = ""
        self._index_was_empty: bool | None = None
        self._state: str = "compact"
        self._rows: list[tuple[QListWidgetItem, ResultItemWidget]] = []
        self._indexed_files_cache: dict[str, float] | None = None
        # Suppress the auto-hide-on-deactivate during the opening
        # transition window. Without this the launcher self-closes on
        # Windows when the previously-focused app briefly fights for
        # foreground after the global hotkey released its key.
        self._suppress_deactivate_until: float = 0.0

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

        # Shadow is now markedly softer — premium through restraint, not
        # through visual weight. The launcher should feel like it's *near*
        # the surface, not pinned with a heavy halo.
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
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
        # Calmer copy — every word in the launcher chrome should earn its
        # space. The verbose original ("…across your indexed memories")
        # made the empty surface read like instructions.
        self.hint_label = QLabel("Type to recall something.")
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
        empty_title = QLabel("No memories yet")
        empty_title.setObjectName("empty_title")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_body = QLabel(
            "Open Settings from the tray icon to add a folder, then "
            "press Ctrl + Space to recall anything."
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
        # Flash timer (path-copied / memory-copied confirmations)
        self._footer_flash_timer = QTimer(self)
        self._footer_flash_timer.setSingleShot(True)
        self._footer_flash_timer.timeout.connect(self._reset_footer)
        # Loading-indicator timer — fires only if a search takes >300ms,
        # so quick searches never flash a "Recalling…" label.
        self._loading_timer = QTimer(self)
        self._loading_timer.setSingleShot(True)
        self._loading_timer.timeout.connect(self._show_loading_state)
        # Set when a flash message is on-screen, so the loading state
        # doesn't clobber the user's confirmation feedback.
        self._footer_pinned: bool = False

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
        # A single eventFilter on the input is the authoritative keyboard
        # contract — no separate returnPressed connection (which would
        # double-fire alongside the filter and cause Enter to open then
        # immediately try to re-open the now-hidden item).
        self._input_filter = _InputKeyFilter(self)
        self.search_input.installEventFilter(self._input_filter)
        self.results.itemActivated.connect(self._open_item)
        self.results.itemClicked.connect(self._open_item)
        self.results.currentRowChanged.connect(self._on_row_changed)

    # -------------------------------------------------------- state transitions

    def _current_screen_geometry(self):
        """Return the available geometry of whichever screen the cursor is
        on. Falls back to the primary screen if `screenAt` returns None
        (rare, but possible during fast monitor disconnects)."""
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        return screen.availableGeometry()

    def _capped_card_height(self, base_card_h: int) -> int:
        """Clamp the requested card height to fit the current screen.

        Even with the now-tighter H_RESULTS_MAX of 480 px, scaling and
        small displays can leave less room than we want — at 125% Windows
        scaling on a 720p panel the available height shrinks below 600 px
        once shadow gutter is accounted for. The body widgets all support
        internal scrolling, so a clamped card still renders correctly,
        just with slightly less visible at once.
        """
        avail_h = self._current_screen_geometry().height()
        # Reserve 60 px top + 60 px bottom margin, plus shadow gutter.
        max_card_h = avail_h - 120 - 2 * SHADOW_MARGIN
        # Never shrink below H_COMPACT — even small screens fit that.
        return max(H_COMPACT, min(base_card_h, max_card_h))

    def _enter_state(self, state: str, target_card_h: int) -> None:
        if self._state == state:
            return
        self._state = state
        capped = self._capped_card_height(target_card_h)
        self.resize(LAUNCHER_WIDTH, capped + 2 * SHADOW_MARGIN)

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
        # Adaptive height: the launcher only grows as tall as the visible
        # rows actually need. A single result reads as a tight command-bar
        # answer, not a half-empty workspace; a full 8-row set is bounded
        # so the launcher never feels like a dashboard.
        visible = sum(
            1 for it, _ in self._rows if not it.isHidden()
        )
        per_row = ResultItemWidget.ROW_HEIGHT + 4  # row + QSS margin
        list_h = max(1, visible) * per_row + 12
        target = INPUT_H + list_h + FOOTER_H
        target = max(H_RESULTS_MIN, min(H_RESULTS_MAX, target))
        self._enter_state("results", target)

    # ----------------------------------------------------------------- show

    def show_centered(self) -> None:
        # Open on whichever screen the cursor is on (multi-monitor) — the
        # primary-screen lookup made the launcher always appear on the
        # wrong display in dual-monitor setups.
        geo = self._current_screen_geometry()
        # Re-evaluate the idle state first so the height (and any cap from
        # _capped_card_height) is right before we position.
        self._refresh_empty_state()

        total_w = self.width()
        total_h = self.height()

        # Center horizontally on the cursor's screen.
        target_x = geo.center().x() - total_w // 2

        # Vertical position: 18% from top by default. Then clamp so the
        # launcher never extends past the screen edges, even on small
        # displays at >125% scaling.
        desired_y = geo.top() + int(geo.height() * 0.18)
        max_y = geo.bottom() - total_h - 24    # 24 px from bottom
        min_y = geo.top() + 24                 # 24 px from top
        if max_y < min_y:
            # Tiny screen: pin to top with a small inset.
            target_y = min_y
        else:
            target_y = max(min_y, min(desired_y, max_y))

        self.move(target_x, target_y)

        # Open a 300ms window during which WindowDeactivate events are
        # ignored. Windows frequently dispatches a deactivate as the
        # previously-focused application releases foreground; without
        # this guard the launcher would close itself before the user can
        # type a single character.
        self._suppress_deactivate_until = time.monotonic() + 0.30

        self.show()
        self.raise_()
        self.activateWindow()

        # Two-stage focus restoration. The 0ms tick runs as soon as the
        # show event is processed; the 60ms tick is a safety net for
        # Windows' SetForegroundWindow restrictions, which sometimes
        # delay activation by one event-loop frame after the global
        # hotkey released its key. Each kick is idempotent and bails if
        # the launcher has been hidden in between.
        QTimer.singleShot(0, self._activate_input)
        QTimer.singleShot(60, self._activate_input)

    def _activate_input(self) -> None:
        if not self.isVisible():
            return
        # Re-raise + re-activate every kick: rapid open/close cycles
        # can change z-order between show() and this callback firing.
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        # selectAll() does double duty: makes any existing query
        # overwriteable on first keystroke (so a user can re-launch and
        # immediately type a fresh query without manually clearing) and
        # ensures the cursor is visibly placed when the input is empty.
        self.search_input.selectAll()

    def showEvent(self, event: QShowEvent) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.search_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
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
        # Size each list to fit its visible rows. Use *Maximum* not Fixed
        # so that on small screens (where the launcher itself is capped)
        # the lists shrink gracefully and show their internal scrollbar
        # instead of forcing layout overflow.
        h = max(1, len(items)) * DigestRow.DIGEST_ROW_HEIGHT + 8
        list_widget.setMaximumHeight(h)
        list_widget.setMinimumHeight(min(h, DigestRow.DIGEST_ROW_HEIGHT + 8))
        list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_digest_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(path, str):
            self._open_path_and_hide(path)

    def _open_path_and_hide(self, path: str) -> None:
        modifiers = QApplication.keyboardModifiers()
        is_reveal = bool(
            modifiers
            & (
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.MetaModifier
            )
        )
        name = Path(path).name
        # Acknowledge the action before attempting it — even when the OS
        # open is fast, this beat makes the action feel deliberate, and
        # gives us a place to land the demo-mode message when the curated
        # paths don't exist on disk.
        self._flash_footer(
            f"{'Revealing' if is_reveal else 'Opening'} {name}…"
        )
        opened = _reveal(path) if is_reveal else _open_file(path)
        if opened:
            QTimer.singleShot(140, self.hide)
        elif self._demo_mode:
            self._flash_footer(f"Demo memory opened · {name}")
            QTimer.singleShot(700, self.hide)
        else:
            # Real file is gone (moved/deleted since indexing). Stay open
            # so the user can pick something else instead of dropping
            # them back to whatever was behind the launcher.
            self._flash_footer(f"Couldn't open · {name}")

    # ------------------------------------------------------- focus / lifecycle

    def event(self, e: QEvent) -> bool:  # type: ignore[override]
        if (
            e.type() == QEvent.Type.WindowDeactivate
            and self.isVisible()
            and time.monotonic() >= self._suppress_deactivate_until
        ):
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
        # Start the loading-state timer; if results arrive within 300ms we
        # cancel it and the user never sees a "Recalling…" flash. Slower
        # searches (cold-start model load) get gentle feedback instead of
        # silently feeling frozen.
        self._loading_timer.start(300)
        self._request_search.emit(query)

    def _on_results(self, query: str, results: List[SearchResult]) -> None:
        self._loading_timer.stop()
        if query != self._latest_query:
            return
        # Only restore the footer if a flash isn't in flight.
        if not self._footer_pinned:
            self.footer.setText(_FOOTER_DEFAULT)
        self._populate(query, results)

    def _on_failed(self, query: str, msg: str) -> None:
        self._loading_timer.stop()
        if not self._footer_pinned:
            self.footer.setText(_FOOTER_DEFAULT)
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

    def _show_loading_state(self) -> None:
        """Subtle 'Recalling…' label shown only when a search exceeds 300ms.
        The 300ms threshold means quick queries never see this; it appears
        on first-search-after-cold-start (when the embedding model loads)
        so the launcher never feels frozen."""
        if not self._footer_pinned:
            self.footer.setText("Recalling…")

    def _reset_footer(self) -> None:
        """Timer callback for the flash timer — restore the default footer
        text and release the pin."""
        self._footer_pinned = False
        self.footer.setText(_FOOTER_DEFAULT)

    def _flash_footer(self, msg: str) -> None:
        # A flash takes precedence over any in-flight loading indicator.
        self._loading_timer.stop()
        self._footer_pinned = True
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
            return
        # No openable row right now. Most common cause: the user typed
        # a query and pressed Enter before the debounce + worker round
        # trip finished. Silent no-op here is exactly the trust-killing
        # behaviour the demo brief called out, so we acknowledge the
        # press by surfacing the in-flight state. (When a search has
        # actually returned zero hits, the launcher is already in
        # "compact" with the explanatory hint, so we skip the flash
        # there to avoid double-stating.)
        in_flight = (
            self._search_timer.isActive() or self._loading_timer.isActive()
        )
        if in_flight and self.search_input.text().strip():
            self._flash_footer("Recalling…")

    def _open_item(self, item: QListWidgetItem) -> None:
        group = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(group, MemoryGroup):
            return
        path = group.primary.path
        title = derive_memory_title(group.primary)
        modifiers = QApplication.keyboardModifiers()
        is_reveal = bool(
            modifiers
            & (
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.MetaModifier
            )
        )
        # "Opening…" / "Revealing…" beat is shown unconditionally — it's
        # the visible acknowledgment that Enter actually did something.
        # Without this the launcher could appear to silently dismiss on
        # platforms where the OS open call is instantaneous.
        self._flash_footer(
            f"{'Revealing' if is_reveal else 'Opening'} {title}…"
        )
        opened = _reveal(path) if is_reveal else _open_file(path)
        if opened:
            # 140ms keeps the acknowledgment visible just long enough to
            # register without ever feeling laggy. The launcher is gone
            # before the OS file handler steals focus.
            QTimer.singleShot(140, self.hide)
        elif self._demo_mode:
            # Demo paths intentionally don't exist on disk. Replace the
            # "Opening…" beat with a clean confirmation so the demo flow
            # reads as deliberate, then hide on a slightly longer beat
            # so the message is readable in screen recordings.
            self._flash_footer(f"Demo memory opened · {title}")
            QTimer.singleShot(700, self.hide)
        else:
            # Real file is missing — likely moved or deleted since we
            # indexed it. Stay open and tell the truth: silently closing
            # is the trust killer the user explicitly called out.
            self._flash_footer(f"Couldn't open · {title}")

    def _move_selection(self, delta: int) -> None:
        """Move the highlighted result by `delta` rows. No wraparound —
        at the edges the selection sticks. Shared between the input
        filter (primary path) and `keyPressEvent` (defense-in-depth)."""
        if self._state != "results":
            return
        visible = [
            i for i, (item, _) in enumerate(self._rows) if not item.isHidden()
        ]
        if not visible:
            return
        row = self.results.currentRow()
        if row not in visible:
            row = visible[0] if delta >= 0 else visible[-1]
        else:
            idx = visible.index(row)
            new_idx = max(0, min(len(visible) - 1, idx + delta))
            row = visible[new_idx]
        self.results.setCurrentRow(row)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        """Defense-in-depth keyboard handler. The input filter is the
        primary route in normal operation (the search input always has
        focus), but if focus somehow lands on the launcher widget itself
        these handlers ensure the keyboard contract still holds."""
        key = event.key()
        mods = event.modifiers()
        if key == Qt.Key.Key_Escape:
            self.hide()
            return
        if mods & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_C and self._state == "results":
                self._copy_selected_path()
                return
            if key == Qt.Key.Key_M and self._state == "results":
                self._copy_memory_summary()
                return
            if key == Qt.Key.Key_Comma:
                self.request_settings.emit()
                return
        if key == Qt.Key.Key_Down:
            self._move_selection(1)
            return
        if key == Qt.Key.Key_Up:
            self._move_selection(-1)
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_enter()
            return
        super().keyPressEvent(event)
