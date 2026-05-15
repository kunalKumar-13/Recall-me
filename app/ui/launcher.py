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
from typing import List, Optional, Tuple

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

from ..core.api_client import APIClient, SearchResponse
from ..core.demo_data import DemoSearchEngine
from ..core.episodic import EpisodicResult, EpisodicRetriever
from ..core.events import EventLogger, EventStore, humanize_age
from ..core.evolution import ThreadEvolution
from ..core.microcontexts import MicroContext, MicroContextReconstructor
from ..core.recovery import (
    RecoveryCandidate,
    RestorationPlan,
    RestorationResult,
    RestorationStep,
)
from ..core.resurfacing import ResurfacedContext
from ..core.search import SearchEngine, SearchResult
from ..core.sessions import Session, SessionReconstructor
from ..core.threads import Thread
from .styles import LAUNCHER_QSS, TEXT_DIM
from .widgets import (
    BrowserActivityRow,
    ContextCard,
    DigestRow,
    EpisodicCard,
    EvolutionStrip,
    MemoryGroup,
    PreviewPane,
    QueryRow,
    RecoveryRow,
    ResultItemWidget,
    ResurfacedRow,
    SessionCard,
    SessionTimelineCard,
    ThreadRow,
    _activity_display,
    cluster_results,
    derive_memory_title,
    explain_match,
    make_context_item,
    make_episodic_item,
    make_result_item,
    make_session_item,
)

MAX_RESULTS = 8
# Episodic results live at the *top* of the same QListWidget as file
# rows. Three is a deliberately small number — the list still reads as
# a file launcher with two or three "memory" cards on top, never as a
# timeline.
EPISODIC_MAX = 3
# Phase 1F micro-context cards sit between episodic and session rows
# in the visual stack. A micro-context is tighter than a session
# (semantic topic, not 30-min temporal window); two is enough — the
# launcher is meant to answer "what was I mentally working on?" with
# at most a couple of competing candidates, never with a timeline.
CONTEXT_MAX = 2
# Phase 1E session cards sit between micro-contexts and file rows.
# We allow at most two so the launcher answers "what was I doing?"
# without ever becoming a timeline view. In practice 1 is the common
# case.
SESSION_MAX = 2
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
# Digest now hosts up to four sections (queries / browser activity /
# recently-active files / resurfaced files). Phase 1B bumps the cap
# again to make room for the new section without forcing internal
# scroll. _capped_card_height still clamps on small screens.
H_DIGEST = 540
DIGEST_RECENT_QUERIES_MAX = 4
DIGEST_RECENT_ACTIVITY_MAX = 3

# Adaptive results bounds. Floor lets a single result still feel like a
# proper command bar (not a blink); ceiling caps the launcher so a full
# 8-result set never dominates the screen.
H_RESULTS_MIN = 280
H_RESULTS_MAX = 480

DIGEST_RECENT_MAX = 4
DIGEST_RESURFACED_MAX = 2
RESURFACED_MIN_AGE_DAYS = 30

# Phase 2B resurfacing — hard ceiling matches the engine's own cap.
# Anything higher would push the digest past one screenful and turn a
# quiet section into a feed.
DIGEST_CONTINUE_MAX = 4

# Phase 2C: memory threads. The brief asks for an infrastructure
# aesthetic — show fewer than a dashboard would, even though the
# engine supports up to 20. Five is the sweet spot.
DIGEST_THREADS_MAX = 5

# Phase 3B: continuity recovery. The brief's ceiling is three; the
# launcher honours it. Recovery is the *primary* idle surface, but
# fewer is better — three resumable threads ON TOP is plenty.
DIGEST_RECOVERY_MAX = 3

# `RECALL_DEBUG=1` flips the "Why am I seeing this?" hover on resurfaced
# rows. We check the env once at import time so we never pay an env
# lookup on the hot render path.
_RESURFACING_DEBUG = bool(os.environ.get("RECALL_DEBUG"))

# `RECALL_EXPLAIN_RECOVERY=1` (Phase 3C) renders per-step reasons +
# suppression reasoning in the launcher's recovery acknowledgement.
# Separate from RECALL_DEBUG so a developer can flip explain-recovery
# without flipping every other hover overlay in the launcher.
_EXPLAIN_RECOVERY = bool(os.environ.get("RECALL_EXPLAIN_RECOVERY"))

# Outer transparent margin around the card — leaves room for the (now
# softer) drop shadow to render without clipping.
SHADOW_MARGIN = 16

LAUNCHER_WIDTH = CARD_WIDTH + 2 * SHADOW_MARGIN

# Results state internal split. The list keeps the full 320 px so titles
# and "why" lines stay legible; the preview pane shrinks instead — making
# it feel like contextual support rather than the dominant surface.
LIST_WIDTH = 320

# Footer copy. The action-hints line is shown only when results are
# on screen (it's only meaningful then); idle states show the
# diagnostic line instead. Bullet separators tie both visually
# together with the floating annotations elsewhere in the launcher.
_FOOTER_DEFAULT = "↑↓ navigate  ·  ↵ open  ·  esc close"
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
    """Runs file search locally + episodic / session / micro-context
    retrieval via the local memory API (Phase 2A).

    File search stays in-process because the embedding model and
    Chroma index are heavy state; the API only owns the event-log
    pipeline. All HTTP traffic is loopback-only.

    All four result sets are emitted in a single `finished` signal
    so the launcher updates atomically.
    """

    finished = pyqtSignal(str, list, list, list, list)
    failed = pyqtSignal(str, str)

    def __init__(
        self,
        engine: SearchEngine,
        api_client: APIClient,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.api_client = api_client

    def handle(self, query: str) -> None:
        try:
            file_results = self.engine.search(query, top_k=MAX_RESULTS)
            # One HTTP call returns episodic + sessions + contexts in
            # a single round-trip. The API client returns `None` on
            # transport failure; the launcher renders empty episodic
            # rows in that case rather than crashing.
            response: SearchResponse | None = self.api_client.search(
                query,
                n_episodic=EPISODIC_MAX,
                n_sessions=SESSION_MAX,
                n_contexts=CONTEXT_MAX,
            )
            if response is None:
                episodic_results: list = []
                session_results: list = []
                context_results: list = []
            else:
                episodic_results = response.episodic
                session_results = response.sessions
                context_results = response.contexts
            self.finished.emit(
                query,
                file_results,
                episodic_results,
                context_results,
                session_results,
            )
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

    def __init__(
        self,
        search_engine: SearchEngine,
        event_logger: EventLogger | None = None,
    ) -> None:
        super().__init__()
        self.search_engine = search_engine
        # Episodic memory wiring. A None logger (test paths, headless
        # smoke runs) becomes a disabled no-op so call sites never have
        # to null-check. The store reads from the same on-disk folder
        # the logger writes into; both are stateless w.r.t. each other.
        self.event_logger = event_logger or EventLogger(enabled=False)
        self.event_store = EventStore(self.event_logger.base_dir)
        # Demo mode is detected from the engine type, not an env var, so
        # the launcher never has to look at process-wide globals. The flag
        # only changes how missing-file open attempts are presented.
        self._demo_mode = isinstance(search_engine, DemoSearchEngine)
        # Phase 2A: retrieval moves behind the local memory API. The
        # launcher writes events directly via `event_logger` (for
        # latency) but reads everything else over HTTP. `EventStore`
        # is still kept as a fallback the digest reads use directly
        # when the API client returns nothing.
        self.api_client = APIClient(
            base_url=f"http://127.0.0.1:4545",
        )
        self._latest_query = ""
        self._index_was_empty: bool | None = None
        self._state: str = "compact"
        # Four row sets in the same QListWidget, layered top-to-bottom
        # per the product spec: episodic moments, then micro-context
        # cards, then session cards, then file rows. Arrow-key
        # navigation walks all four via row index, which is why we
        # keep them ordered consistently across passes.
        self._episodic_rows: list[tuple[QListWidgetItem, EpisodicCard]] = []
        self._context_rows: list[tuple[QListWidgetItem, ContextCard]] = []
        self._session_rows: list[tuple[QListWidgetItem, SessionCard]] = []
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
        self._worker = _SearchWorker(search_engine, self.api_client)
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
        # First-run state — the user has just installed Recall and the
        # index is empty. The copy here sets the trust tone for the
        # whole product: calm, factual, no hyperbole, no exclamation,
        # no "AI-powered" framing.
        self.empty_widget = QWidget()
        ev = QVBoxLayout(self.empty_widget)
        ev.setContentsMargins(0, 0, 0, 0)
        ev.setSpacing(2)
        empty_title = QLabel("Recall is ready.")
        empty_title.setObjectName("empty_title")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_body = QLabel(
            "Press Ctrl + , to open Settings and pick a folder to index. "
            "Captured activity from the browser extension will flow in "
            "automatically — nothing leaves your machine."
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

        # ── "Continue where you left off" — Phase 3B recovery ──
        # The PRIMARY idle surface. When recovery finds resumable
        # work (an interrupted thread with multiple targets ready
        # for one-click restore), it leads the digest. Hidden
        # cleanly when there's nothing real to recover — a clean
        # Monday morning shows no recovery cards rather than
        # fabricated ones.
        self.recovery_header = QLabel("Continue where you left off")
        self.recovery_header.setObjectName("digest_section")

        self.recovery_list = QListWidget()
        self.recovery_list.setObjectName("digest")
        self.recovery_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.recovery_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.recovery_list.setUniformItemSizes(True)
        self.recovery_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.recovery_list.itemClicked.connect(
            self._on_recovery_item_clicked
        )

        # ── "Active memory threads" — Phase 2C ──
        # The most stable, longest-lived topics the user keeps
        # returning to. Sits *below* recovery in the digest because
        # threads describe ongoing context; recovery describes
        # *resumable* context. The two are related but recovery
        # earns the top slot.
        self.threads_header = QLabel("Active memory threads")
        self.threads_header.setObjectName("digest_section")

        self.threads_list = QListWidget()
        self.threads_list.setObjectName("digest")
        self.threads_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.threads_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.threads_list.setUniformItemSizes(True)
        self.threads_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.threads_list.itemClicked.connect(self._on_thread_item_clicked)

        # ── "On your radar" — Phase 2B resurfacing ──
        # Phase 2B surfaced "Continue where you left off" cards; the
        # label has been re-pointed to Phase 3B recovery above.
        # Resurfacing still earns a slot — it catches *noticeable*
        # topics (returning after a break, repeated revisits) that
        # may not yet qualify as recoverable work. The vocabulary
        # shift ("on your radar") is deliberate: recovery is what
        # to *resume*; resurfacing is what to *notice*.
        self.resurface_header = QLabel("On your radar")
        self.resurface_header.setObjectName("digest_section")

        self.resurface_list = QListWidget()
        self.resurface_list.setObjectName("digest")
        self.resurface_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resurface_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.resurface_list.setUniformItemSizes(True)
        self.resurface_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.resurface_list.itemClicked.connect(
            self._on_resurface_item_clicked
        )

        # ── "Lately you searched" — episodic surface (Phase 1A) ──
        # Sourced from the local event log. Click a row to repopulate
        # the input and re-run that query. Hidden when the log has
        # nothing yet (first-run users see no empty section).
        self.recent_queries_header = QLabel("Lately you searched")
        self.recent_queries_header.setObjectName("digest_section")

        self.recent_queries_list = QListWidget()
        self.recent_queries_list.setObjectName("digest")
        self.recent_queries_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.recent_queries_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.recent_queries_list.setUniformItemSizes(True)
        self.recent_queries_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.recent_queries_list.itemClicked.connect(
            self._on_recent_query_item_clicked
        )

        # ── "Recent digital activity" — Phase 1B browser surface ──
        # Sourced from the same event log. Mixes browser_visit /
        # browser_search / chat_session into one chronological strip.
        # Click a row to open the captured URL in the system default
        # browser. Hidden entirely when the log has no browser events
        # (first-run users, or users with browser ingestion off).
        self.recent_activity_header = QLabel("Recent digital activity")
        self.recent_activity_header.setObjectName("digest_section")

        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setObjectName("digest")
        self.recent_activity_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.recent_activity_list.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self.recent_activity_list.setUniformItemSizes(True)
        self.recent_activity_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.recent_activity_list.itemClicked.connect(
            self._on_recent_activity_item_clicked
        )

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

        # Phase 3B: recovery leads. Threads + resurfacing follow.
        # The remaining sections (queries, activity, recent files,
        # resurfaced files) keep their order — they're chronological
        # references, ranked under the synthesis surfaces above.
        dp.addWidget(self.recovery_header)
        dp.addWidget(self.recovery_list)
        dp.addWidget(self.threads_header)
        dp.addWidget(self.threads_list)
        dp.addWidget(self.resurface_header)
        dp.addWidget(self.resurface_list)
        dp.addWidget(self.recent_queries_header)
        dp.addWidget(self.recent_queries_list)
        dp.addWidget(self.recent_activity_header)
        dp.addWidget(self.recent_activity_list)
        dp.addWidget(recent_header)
        dp.addWidget(self.digest_list)
        dp.addWidget(self.resurfaced_header)
        dp.addWidget(self.resurfaced_list)
        dp.addStretch(0)

        # Recovery + threads + resurfacing all start hidden — the
        # populate pass flips them on only when their engines return
        # at least one card. Blank headers would scream more loudly
        # than no headers at all.
        self.recovery_header.hide()
        self.recovery_list.hide()
        self.threads_header.hide()
        self.threads_list.hide()
        self.resurface_header.hide()
        self.resurface_list.hide()

        # ── Quiet first-week hint (Phase 4A) ──
        # When the user has indexed folders but no captured events
        # yet (recovery/threads/resurfacing all empty), the digest
        # would otherwise read as "broken" — a header strip with
        # nothing under it. This calm one-liner sits in that hole
        # so the surface feels intentional rather than empty.
        self.first_week_hint = QLabel(
            "Capture builds quietly. The launcher gains "
            "memory threads and recovery cards as you work; "
            "install the browser extension to feed it more."
        )
        self.first_week_hint.setObjectName("first_week_hint")
        self.first_week_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.first_week_hint.setWordWrap(True)
        self.first_week_hint.setStyleSheet(
            "QLabel#first_week_hint {"
            f"  color: {TEXT_DIM};"
            "  font-size: 11.5px;"
            "  font-style: italic;"
            "  padding: 16px 24px;"
            "}"
        )
        self.first_week_hint.hide()
        dp.insertWidget(0, self.first_week_hint)

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

        # ── Phase 3A: evolution strip ──
        # Slot sits between the input and the results body. It's a
        # zero-height placeholder until a thread is opened; the
        # `_render_evolution_strip` helper swaps in a real
        # `EvolutionStrip` widget for the lifetime of that search.
        self.evolution_strip_slot = QWidget()
        evo_layout = QVBoxLayout(self.evolution_strip_slot)
        evo_layout.setContentsMargins(0, 0, 0, 0)
        evo_layout.setSpacing(0)
        self.evolution_strip_slot.setFixedHeight(0)
        self.evolution_strip_slot.hide()
        # The id of the thread whose evolution is currently being
        # fetched / rendered. Cleared when the user clears the input
        # or opens a different thread.
        self._active_evolution_thread_id: Optional[str] = None

        # --- assembly -------------------------------------------------------
        root.addWidget(self.search_input)
        root.addWidget(self.hint_label, 1)
        root.addWidget(self.empty_widget, 1)
        root.addWidget(self.digest_panel, 1)
        root.addWidget(self.evolution_strip_slot)
        root.addWidget(self.results_body, 1)
        root.addWidget(self.footer)

        # Episodic rows live at the top of the same QListWidget. Pre-
        # allocated like file rows so populate is just a flat update —
        # no addItem / removeItem churn between queries.
        for _ in range(EPISODIC_MAX):
            item = make_episodic_item()
            widget = EpisodicCard()
            self.results.addItem(item)
            self.results.setItemWidget(item, widget)
            item.setHidden(True)
            self._episodic_rows.append((item, widget))

        # Phase 1F micro-context rows sit between episodic and
        # session rows. Same expand-then-act pattern as sessions —
        # first Enter expands the card, second Enter triggers
        # "Resume context".
        for _ in range(CONTEXT_MAX):
            item = make_context_item()
            widget = ContextCard()
            self.results.addItem(item)
            self.results.setItemWidget(item, widget)
            item.setHidden(True)
            widget.expanded_changed.connect(
                lambda expanded, it=item, w=widget:
                self._on_context_expanded(it, w, expanded)
            )
            widget.resume_clicked.connect(self._resume_context)
            self._context_rows.append((item, widget))

        # Phase 1E session rows sit between micro-contexts and file
        # rows. The card itself toggles between collapsed and expanded
        # heights; the QListWidgetItem's size hint is updated when the
        # card emits expanded_changed so the row visibly grows.
        for _ in range(SESSION_MAX):
            item = make_session_item()
            widget = SessionCard()
            self.results.addItem(item)
            self.results.setItemWidget(item, widget)
            item.setHidden(True)
            # Wire the card's two signals back to the launcher.
            widget.expanded_changed.connect(
                lambda expanded, it=item, w=widget:
                self._on_session_expanded(it, w, expanded)
            )
            widget.continue_clicked.connect(self._continue_session)
            self._session_rows.append((item, widget))

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
        self._refresh_default_footer()

    def _show_empty(self) -> None:
        if self._state != "empty":
            self._hide_all_bodies()
            self.empty_widget.show()
            # Leaving the results pane resets any open-thread context.
            self._clear_evolution_strip()
        self._enter_state("empty", H_EMPTY)
        self._refresh_default_footer()

    def _show_digest(self) -> None:
        if self._state != "digest":
            self._hide_all_bodies()
            self.digest_panel.show()
            # Same — digest is an idle surface; no thread is open.
            self._clear_evolution_strip()
        self._enter_state("digest", H_DIGEST)
        self._refresh_default_footer()

    def _show_results(self) -> None:
        if self._state != "results":
            self._hide_all_bodies()
            self.results_body.show()
        # Adaptive height: count visible episodic + session + file rows
        # separately. Session rows can be collapsed (≈38 px) or expanded
        # (≈196 px); we read each card's `desired_height` so the launcher
        # height tracks the actual on-screen size, not a fixed estimate.
        visible_files = sum(
            1 for it, _ in self._rows if not it.isHidden()
        )
        visible_episodic = sum(
            1 for it, _ in self._episodic_rows if not it.isHidden()
        )
        file_h = visible_files * (ResultItemWidget.ROW_HEIGHT + 4)
        episodic_h = visible_episodic * (EpisodicCard.EPISODIC_ROW_HEIGHT + 4)
        session_h = sum(
            card.desired_height + 4
            for it, card in self._session_rows
            if not it.isHidden()
        )
        list_h = max(1, file_h + episodic_h + session_h) + 12
        target = INPUT_H + list_h + FOOTER_H
        target = max(H_RESULTS_MIN, min(H_RESULTS_MAX, target))
        self._enter_state("results", target)
        self._refresh_default_footer()

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

        # Phase 2A — both digest data sources move behind the local
        # API. EventStore still exists as a fallback when the API
        # client returns nothing (e.g. service still booting), which
        # keeps the launcher usable during the first 100 ms of
        # uvicorn startup.
        try:
            recent_queries = self.api_client.recent_queries(
                n=DIGEST_RECENT_QUERIES_MAX, days=14
            )
            if not recent_queries:
                recent_queries = self.event_store.recent_queries(
                    n=DIGEST_RECENT_QUERIES_MAX, days=14
                )
        except Exception:
            recent_queries = []
        self._fill_recent_queries(recent_queries)
        has_queries = bool(recent_queries)
        self.recent_queries_header.setVisible(has_queries)
        self.recent_queries_list.setVisible(has_queries)

        try:
            recent_activity = self.api_client.recent_browser_activity(
                n=DIGEST_RECENT_ACTIVITY_MAX, days=7
            )
            if not recent_activity:
                recent_activity = self.event_store.recent_browser_activity(
                    n=DIGEST_RECENT_ACTIVITY_MAX, days=7
                )
        except Exception:
            recent_activity = []
        self._fill_recent_activity(recent_activity)
        has_activity = bool(recent_activity)
        self.recent_activity_header.setVisible(has_activity)
        self.recent_activity_list.setVisible(has_activity)

        # ── Phase 2B: passive resurfacing ──
        # Best-effort over HTTP. We never block the digest on this —
        # any transport or scoring failure returns `[]` and we hide
        # the section.
        try:
            resurfaced = self.api_client.resurface_idle(
                n=DIGEST_CONTINUE_MAX, timeout=0.5
            )
        except Exception:
            resurfaced = []
        self._fill_resurface_list(resurfaced)
        has_resurface = bool(resurfaced)
        self.resurface_header.setVisible(has_resurface)
        self.resurface_list.setVisible(has_resurface)

        # ── Phase 2C: memory threads ──
        # Stable, long-lived topics the user keeps returning to.
        # Strictly a digest surface — never appears inside live
        # search results.
        try:
            threads = self.api_client.threads_recent(
                n=DIGEST_THREADS_MAX, timeout=0.5
            )
        except Exception:
            threads = []
        self._fill_threads_list(threads)
        has_threads = bool(threads)
        self.threads_header.setVisible(has_threads)
        self.threads_list.setVisible(has_threads)

        # ── Phase 3B: continuity recovery (PRIMARY SURFACE) ──
        # Recovery answers "what should I resume?" — the launcher's
        # iconic moment. We fetch *after* threads so the threads
        # rebuild's cache is warm when recovery rebuilds it, which
        # keeps the combined cold-start path under budget on
        # 10K-event logs.
        try:
            recovery = self.api_client.recovery_recent(
                n=DIGEST_RECOVERY_MAX, timeout=0.6
            )
        except Exception:
            recovery = []
        self._fill_recovery_list(recovery)
        has_recovery = bool(recovery)
        self.recovery_header.setVisible(has_recovery)
        self.recovery_list.setVisible(has_recovery)

        # ── Phase 4A: quiet first-week hint ──
        # If all three synthesis surfaces (recovery, threads,
        # resurface) returned nothing AND the user has no recent
        # browser activity AND no recent queries, they're early.
        # Show one calm line instead of a header-strip with no
        # rows under it.
        all_synthesis_empty = (
            not has_recovery
            and not has_threads
            and not has_resurface
            and not has_queries
            and not has_activity
        )
        self.first_week_hint.setVisible(all_synthesis_empty)

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

    def _fill_recent_queries(self, events: list) -> None:
        """Render the "Lately you searched" section from a list of
        Event records. Each row is a `QueryRow` whose click signal
        repopulates the input."""
        self.recent_queries_list.clear()
        for ev in events:
            text = (ev.payload.get("text") or "").strip()
            if not text:
                continue
            row_w = QueryRow(text, ev.ts_epoch())
            row_w.clicked.connect(self._on_recent_query_clicked)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, QueryRow.QUERY_ROW_HEIGHT))
            li.setData(Qt.ItemDataRole.UserRole, text)
            self.recent_queries_list.addItem(li)
            self.recent_queries_list.setItemWidget(li, row_w)
        # Same Maximum-sizing pattern as the digest lists so the section
        # collapses gracefully on small screens.
        n = max(1, len(events))
        h = n * QueryRow.QUERY_ROW_HEIGHT + 6
        self.recent_queries_list.setMaximumHeight(h)
        self.recent_queries_list.setMinimumHeight(
            min(h, QueryRow.QUERY_ROW_HEIGHT + 6)
        )
        self.recent_queries_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_recent_query_item_clicked(self, item: QListWidgetItem) -> None:
        text = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(text, str):
            self._on_recent_query_clicked(text)

    def _on_recent_query_clicked(self, text: str) -> None:
        """Replay a past query: drop it back into the input. Qt's
        textChanged signal fires the normal debounce + search path,
        so the result list shows up exactly as if the user had typed
        it themselves."""
        self.search_input.setText(text)
        self.search_input.selectAll()
        self.search_input.setFocus(Qt.FocusReason.OtherFocusReason)

    def _fill_recent_activity(self, events: list) -> None:
        """Render the "Recent digital activity" section from a list of
        Event records (browser_visit / browser_search / chat_session)."""
        self.recent_activity_list.clear()
        for ev in events:
            payload = ev.payload or {}
            url = (payload.get("url") or "").strip()
            title, subtitle = _activity_display(ev.kind, payload)
            row_w = BrowserActivityRow(
                kind=ev.kind,
                title=title,
                subtitle=subtitle,
                ts_epoch=ev.ts_epoch(),
                url=url,
            )
            row_w.clicked.connect(self._on_recent_activity_clicked)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, BrowserActivityRow.ACTIVITY_ROW_HEIGHT))
            li.setData(Qt.ItemDataRole.UserRole, url)
            self.recent_activity_list.addItem(li)
            self.recent_activity_list.setItemWidget(li, row_w)
        n = max(1, len(events))
        h = n * BrowserActivityRow.ACTIVITY_ROW_HEIGHT + 6
        self.recent_activity_list.setMaximumHeight(h)
        self.recent_activity_list.setMinimumHeight(
            min(h, BrowserActivityRow.ACTIVITY_ROW_HEIGHT + 6)
        )
        self.recent_activity_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_recent_activity_item_clicked(self, item: QListWidgetItem) -> None:
        url = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(url, str) and url:
            self._on_recent_activity_clicked(url)

    # ── Phase 2B: resurfacing rows ────────────────────────────────────

    def _fill_resurface_list(
        self, contexts: List[ResurfacedContext]
    ) -> None:
        """Render the "Continue where you left off" section from a
        ranked list of `ResurfacedContext`s. Each card collapses to a
        single quiet row anchored on its newest openable target. The
        full openable-targets list stays on the data role so a future
        expansion (e.g. "show all sources") can reach it without
        another HTTP roundtrip."""
        self.resurface_list.clear()
        for ctx in contexts:
            # Pick the freshest openable target — that's what
            # "continue" should land on by default.
            target_kind = ""
            target = ""
            if ctx.openable_targets:
                target_kind, target = ctx.openable_targets[0]
            row = ResurfacedRow(
                label=ctx.label,
                time_label=ctx.time_label,
                kind=target_kind,
                target=target,
                why_lines=ctx.why,
                debug_hover=_RESURFACING_DEBUG,
            )
            row.clicked.connect(self._on_resurface_clicked)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, ResurfacedRow.RESURFACED_ROW_HEIGHT))
            # Store the target on the item so the QListWidget itemClicked
            # path also works (defense-in-depth: the row's own click
            # signal is the primary path).
            li.setData(Qt.ItemDataRole.UserRole, (target_kind, target))
            self.resurface_list.addItem(li)
            self.resurface_list.setItemWidget(li, row)
        n = max(1, len(contexts))
        h = n * ResurfacedRow.RESURFACED_ROW_HEIGHT + 6
        self.resurface_list.setMaximumHeight(h)
        self.resurface_list.setMinimumHeight(
            min(h, ResurfacedRow.RESURFACED_ROW_HEIGHT + 6)
        )
        self.resurface_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_resurface_item_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and len(data) == 2:
            kind, target = data
            if isinstance(target, str) and target:
                self._on_resurface_clicked(kind, target)

    def _on_resurface_clicked(self, kind: str, target: str) -> None:
        """Open the resurfaced target. URLs go through the browser
        path (same as `BrowserActivityRow`); filesystem paths go
        through the file-open path so launcher-style modifier-key
        reveal still works."""
        if not target:
            return
        if kind == "path":
            self._open_path_and_hide(target)
            return
        # URL — same flash + open + hide as the recent-activity row.
        self._on_recent_activity_clicked(target)

    # ── Phase 2C: memory threads ──────────────────────────────────────

    def _fill_threads_list(self, threads: List[Thread]) -> None:
        """Render the "Active memory threads" section. Each row is a
        two-line `ThreadRow` (title + dim timeline summary); click
        opens the thread by repopulating the input with its
        topic-key/title, which fires the existing retrieval pipeline.
        That's the open-thread flow: chronological reconstruction
        through the sessions + micro-contexts the search endpoint
        already returns."""
        self.threads_list.clear()
        for t in threads:
            row = ThreadRow(
                thread_id=t.id,
                topic_key=t.topic_key,
                title=t.title,
                timeline_summary=t.timeline_summary,
                why_lines=t.why,
                debug_hover=_RESURFACING_DEBUG,
            )
            row.clicked.connect(self._on_thread_clicked)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, ThreadRow.THREAD_ROW_HEIGHT))
            # Hold both id + topic so the QListWidget itemClicked
            # path can also fire (defense-in-depth: the row's own
            # signal is the primary path).
            li.setData(Qt.ItemDataRole.UserRole, (t.id, t.topic_key, t.title))
            self.threads_list.addItem(li)
            self.threads_list.setItemWidget(li, row)
        n = max(1, len(threads))
        h = n * ThreadRow.THREAD_ROW_HEIGHT + 6
        self.threads_list.setMaximumHeight(h)
        self.threads_list.setMinimumHeight(
            min(h, ThreadRow.THREAD_ROW_HEIGHT + 6)
        )
        self.threads_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_thread_item_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and len(data) == 3:
            thread_id, topic_key, title = data
            if isinstance(thread_id, str) and thread_id:
                self._on_thread_clicked(thread_id, topic_key, title)

    # ── Phase 3B: continuity recovery (primary surface) ───────────────

    def _fill_recovery_list(
        self, candidates: List[RecoveryCandidate]
    ) -> None:
        """Render the "Continue where you left off" section. Each
        row is a two-line `RecoveryRow` (title + time + target-count
        strip). Clicking a row triggers one-click restoration: every
        suggested target opens via the OS in sequence."""
        self.recovery_list.clear()
        for cand in candidates:
            # Bucket targets by surface kind so the row can render a
            # "3 tabs · 2 files · 1 chat" strip rather than an opaque
            # number. The buckets are heuristic — `url` covers the
            # browser-side surfaces; chats are URLs to chat.* hosts.
            n_tabs = 0
            n_files = 0
            n_chats = 0
            for kind, target in cand.suggested_targets:
                if kind == "path":
                    n_files += 1
                elif "chat" in target.lower() or "claude" in target.lower():
                    n_chats += 1
                else:
                    n_tabs += 1
            counts: list[Tuple[str, int]] = []
            if n_tabs:
                counts.append((
                    "tab" if n_tabs == 1 else "tabs", n_tabs
                ))
            if n_files:
                counts.append((
                    "file" if n_files == 1 else "files", n_files
                ))
            if n_chats:
                counts.append((
                    "chat" if n_chats == 1 else "chats", n_chats
                ))
            # Phase 3C: prefer the engine's deterministic
            # preview caption when present (it's already
            # composed: "3 tabs · 2 files · last active during
            # implementation"). Fall back to the bare time +
            # counts when an older API server is in play.
            if cand.preview_caption:
                time_label = cand.preview_caption
            else:
                time_label = (
                    f"Last active {humanize_age(cand.last_active_at)}"
                    if cand.last_active_at
                    else ""
                )
            # Debug-only hover combines `why` lines + unresolved
            # signal explanations from the engine.
            tip_lines = list(cand.why) + list(cand.unresolved_signals)
            row = RecoveryRow(
                candidate_id=cand.id,
                title=cand.title,
                time_label=time_label,
                target_counts=counts,
                why_lines=tip_lines,
                debug_hover=_RESURFACING_DEBUG,
                n_targets_total=len(cand.suggested_targets),
            )
            row.restore.connect(self._on_recovery_restore)
            li = QListWidgetItem()
            li.setSizeHint(QSize(0, RecoveryRow.RECOVERY_ROW_HEIGHT))
            li.setData(
                Qt.ItemDataRole.UserRole,
                (cand.id, cand.title, len(cand.suggested_targets)),
            )
            self.recovery_list.addItem(li)
            self.recovery_list.setItemWidget(li, row)
        n = max(1, len(candidates))
        h = n * RecoveryRow.RECOVERY_ROW_HEIGHT + 6
        self.recovery_list.setMaximumHeight(h)
        self.recovery_list.setMinimumHeight(
            min(h, RecoveryRow.RECOVERY_ROW_HEIGHT + 6)
        )
        self.recovery_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    def _on_recovery_item_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and len(data) == 3:
            candidate_id, title, n_targets = data
            if isinstance(candidate_id, str) and candidate_id:
                self._on_recovery_restore(candidate_id, title, n_targets)

    def _on_recovery_restore(
        self, candidate_id: str, title: str, n_targets: int
    ) -> None:
        """One-click restoration — Phase 3C orchestration.

        Resolve the candidate via the API to get its
        `RestorationPlan`, then walk `plan.steps` in the
        prescribed order (files → chats → tabs → searches). Each
        step's `target` opens through the OS-default handler;
        file targets are additionally logged so the next
        recovery pass sees the activity.

        The launcher gives the user one piece of feedback (the
        footer flash) up front, then a second piece on completion
        ('Restored 4 of 5 · 1 missing'). When
        `RECALL_EXPLAIN_RECOVERY=1` is set, per-step reasons +
        skip reasons are appended to the second flash.

        Restoration timing is tracked locally in a
        `RestorationResult`; nothing leaves the machine.
        """
        if not candidate_id:
            return

        # Resolve the orchestrated plan. The engine has no
        # on-disk cache, so the plan reflects current state.
        try:
            plan = self.api_client.recovery_restore(
                candidate_id, timeout=1.0
            )
        except Exception:
            plan = None

        if plan is None or not plan.steps:
            self._flash_footer(
                f"Nothing to restore  ·  {title[:50]}"
            )
            return

        n_steps = len(plan.steps)
        result = RestorationResult(
            candidate_id=candidate_id,
            title=plan.title or title,
            requested=n_steps,
        )

        # Acknowledge up front. The caption (Phase 3C) carries
        # the deterministic preview line, which is more
        # informative than a bare count.
        ack_extra = (
            f"  ({plan.preview_caption})"
            if plan.preview_caption else
            f"  ({n_steps} item{'s' if n_steps != 1 else ''})"
        )
        self._flash_footer(
            f"Restoring  ·  {(plan.title or title)[:36]}{ack_extra}"
        )

        # Execute the choreographed sequence. The plan's order
        # is intentional — files first ground the work, chats
        # provide context, tabs re-anchor reading material,
        # repeated searches come last.
        t0 = time.perf_counter()
        for step in plan.steps:
            target = (step.target or "").strip()
            if not target:
                result.skipped.append((step.kind, "", "empty target"))
                continue
            try:
                if step.kind == "path":
                    # File paths sometimes go missing between
                    # capture and restore — verify before logging
                    # an "open" event so we don't pollute the log
                    # with phantom restores.
                    if not Path(target).exists():
                        result.skipped.append(
                            (step.kind, target, "file no longer exists")
                        )
                        continue
                    self.event_logger.log_open(
                        target, Path(target).name
                    )
                    opened = _open_file(target)
                else:
                    opened = _open_file(target)
                if opened:
                    result.restored += 1
                else:
                    result.skipped.append(
                        (step.kind, target, "OS open failed")
                    )
            except Exception as exc:
                # Best-effort restoration — one bad target
                # should not block the rest.
                result.skipped.append(
                    (step.kind, target, type(exc).__name__)
                )
                continue
        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

        # Second acknowledgement — the completion summary. When
        # `RECALL_EXPLAIN_RECOVERY=1` is set, the skip list is
        # surfaced inline so a developer can see exactly what
        # didn't restore.
        self._announce_restoration_result(result)

        if result.restored > 0:
            QTimer.singleShot(350, self.hide)

    def _announce_restoration_result(
        self, result: RestorationResult
    ) -> None:
        """Render the completion flash and (when explain mode is
        on) the per-step skip list. Pure presentation — the
        launcher never persists the result."""
        if result.requested == 0:
            return
        if result.restored == result.requested:
            tail = f"Restored {result.restored}"
        elif result.restored == 0:
            tail = "Couldn't restore anything"
        else:
            tail = (
                f"Restored {result.restored} of {result.requested}  ·  "
                f"{len(result.skipped)} skipped"
            )
        self._flash_footer(
            f"{tail}  ·  {result.title[:40]}"
        )
        if _EXPLAIN_RECOVERY and result.skipped:
            # Developer-facing: print the skip list so
            # `python recall.py --debug` carries the trace.
            print(
                f"[recovery.restore] {result.title}  "
                f"requested={result.requested} restored={result.restored} "
                f"elapsed_ms={result.elapsed_ms}"
            )
            for kind, target, reason in result.skipped:
                print(
                    f"  · skipped  ({kind})  {target[:80]}  — {reason}"
                )

    def _on_thread_clicked(
        self, thread_id: str, topic_key: str, title: str
    ) -> None:
        """Open-thread flow.

        Two things happen together:

          1. The thread's title is typed into the search input. The
             retrieval pipeline answers with episodic moments,
             sessions, and micro-contexts — the chronological
             reconstruction the brief asks for.
          2. The launcher fetches the Phase 3A evolution for the
             thread and renders it as a horizontal strip above the
             results. The strip carries the phase chronology +
             transition cues; the results below carry the actual
             retrieval.
        """
        if not thread_id:
            return
        query = (title or topic_key or "").strip()
        if not query:
            return
        # Push the query into the input field — the input filter
        # already debounces and fires the search.
        try:
            self.search_input.setText(query)
            self.search_input.setFocus()
        except AttributeError:
            self._request_search.emit(query)

        # Fetch evolution best-effort. Failures hide the strip
        # entirely rather than render half a surface.
        self._active_evolution_thread_id = thread_id
        try:
            evo = self.api_client.thread_evolution(thread_id, timeout=0.5)
        except Exception:
            evo = None
        if evo is not None and evo.phases:
            self._render_evolution_strip(evo)
        else:
            self._clear_evolution_strip()

    def _render_evolution_strip(self, evo: ThreadEvolution) -> None:
        """Replace the contents of the evolution-strip slot with a
        fresh `EvolutionStrip` widget. Phase rows arrive shaped for
        the widget: `title`, `subtitle` (the time span), `transition`,
        and the debug `why` lines."""
        self._clear_evolution_strip(keep_active=True)
        if not evo.phases:
            self.evolution_strip_slot.setFixedHeight(0)
            self.evolution_strip_slot.hide()
            return

        rows: list[dict] = []
        for p in evo.phases:
            subtitle = humanize_age(p.end_at) if p.end_at else ""
            rows.append({
                "title":      p.title,
                "subtitle":   subtitle,
                "transition": p.transition,
                "why":        list(p.why),
            })
        strip = EvolutionStrip(rows, debug_hover=_RESURFACING_DEBUG)
        layout = self.evolution_strip_slot.layout()
        if layout is not None:
            layout.addWidget(strip)
        self.evolution_strip_slot.setFixedHeight(EvolutionStrip.STRIP_HEIGHT)
        self.evolution_strip_slot.show()

    def _clear_evolution_strip(self, keep_active: bool = False) -> None:
        """Tear down the current strip (if any) and shrink the slot
        back to zero. Called when the user clears the input or opens
        a different thread."""
        layout = self.evolution_strip_slot.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                w = child.widget() if child is not None else None
                if w is not None:
                    w.deleteLater()
        self.evolution_strip_slot.setFixedHeight(0)
        self.evolution_strip_slot.hide()
        if not keep_active:
            self._active_evolution_thread_id = None

    def _on_recent_activity_clicked(self, url: str) -> None:
        """Hand the URL to the OS default browser. Reuses the same
        os.startfile / open / xdg-open path as file opens — URLs are
        recognized by every major OS handler."""
        if not url:
            return
        # Acknowledge the action with a flash, then close.
        self._flash_footer(f"Opened in browser  ·  {url[:60]}")
        opened = _open_file(url)
        if opened:
            QTimer.singleShot(160, self.hide)
        else:
            self._flash_footer(f"Couldn't open  ·  {url[:60]}")

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
        # Episodic capture before the OS call.
        if is_reveal:
            self.event_logger.log_reveal(path, name)
        else:
            self.event_logger.log_open(path, name)

        opened = _reveal(path) if is_reveal else _open_file(path)
        if opened:
            # Past-tense confirmation — the OS open is essentially
            # synchronous on Windows, so by the time the user perceives
            # the flash, the action has actually completed.
            self._flash_footer(
                f"Opened in Explorer  ·  {name}" if is_reveal
                else f"Opened  ·  {name}"
            )
            QTimer.singleShot(160, self.hide)
        elif self._demo_mode:
            self._flash_footer(f"Demo memory  ·  {name}")
            QTimer.singleShot(700, self.hide)
        else:
            # Real file is gone (moved/deleted since indexing). Stay open
            # so the user can pick something else instead of dropping
            # them back to whatever was behind the launcher.
            self._flash_footer(f"Couldn't open  ·  {name}")

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
            for item, _ in self._episodic_rows:
                item.setHidden(True)
            for item, card in self._context_rows:
                card.set_expanded(False)
                item.setHidden(True)
            for item, card in self._session_rows:
                card.set_expanded(False)
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

    def _on_results(
        self,
        query: str,
        results: List[SearchResult],
        episodic_results: List[EpisodicResult],
        context_results: List[MicroContext],
        session_results: List[Session],
    ) -> None:
        self._loading_timer.stop()
        if query != self._latest_query:
            return
        # Footer is updated by the _show_results() call in _populate;
        # we only need to clear the loading flash here.
        if not self._footer_pinned:
            self._refresh_default_footer()
        # Episodic capture: log only the latest committed query (not
        # every keystroke and not stale results). The logger is a no-op
        # when episodic memory is disabled in Settings.
        self.event_logger.log_query(query, len(results))
        self._populate(
            query, results, episodic_results, context_results, session_results
        )

    def _on_failed(self, query: str, msg: str) -> None:
        self._loading_timer.stop()
        if not self._footer_pinned:
            self._refresh_default_footer()
        if query != self._latest_query:
            return
        # Capture the failed query too — useful for "what did I try?"
        # episodic recall, even when the search itself returned nothing.
        self.event_logger.log_query(query, 0)
        for item, _ in self._rows:
            item.setHidden(True)
        for item, _ in self._episodic_rows:
            item.setHidden(True)
        for item, card in self._context_rows:
            card.set_expanded(False)
            item.setHidden(True)
        for item, card in self._session_rows:
            card.set_expanded(False)
            item.setHidden(True)
        self.preview.show_empty()
        self._show_compact("Couldn't recall just now. Try different words.")

    def _populate(
        self,
        query: str,
        results: List[SearchResult],
        episodic_results: List[EpisodicResult] | None = None,
        context_results: List[MicroContext] | None = None,
        session_results: List[Session] | None = None,
    ) -> None:
        episodic_results = episodic_results or []
        context_results = context_results or []
        session_results = session_results or []

        # Empty in all four directions → compact "nothing matched"
        # state. We don't surface a session-or-context-only empty case
        # because those always imply one or more matching events that
        # episodic_results would also be reporting.
        if (
            not results
            and not episodic_results
            and not context_results
            and not session_results
        ):
            for item, _ in self._rows:
                item.setHidden(True)
            for item, _ in self._episodic_rows:
                item.setHidden(True)
            for item, card in self._context_rows:
                card.set_expanded(False)
                item.setHidden(True)
            for item, card in self._session_rows:
                card.set_expanded(False)
                item.setHidden(True)
            self.preview.show_empty("Nothing comes to mind yet.")
            self._show_compact("Nothing comes to mind. Try different words.")
            return

        # Fill episodic rows (top of the list).
        for i, (item, widget) in enumerate(self._episodic_rows):
            if i < len(episodic_results):
                widget.update_result(episodic_results[i])
                item.setData(Qt.ItemDataRole.UserRole, episodic_results[i])
                item.setHidden(False)
            else:
                item.setHidden(True)

        # Fill micro-context rows (between episodic and sessions).
        for i, (item, card) in enumerate(self._context_rows):
            if i < len(context_results):
                card.set_expanded(False)
                card.update_context(context_results[i])
                item.setData(Qt.ItemDataRole.UserRole, context_results[i])
                item.setSizeHint(QSize(0, card.desired_height))
                item.setHidden(False)
            else:
                card.set_expanded(False)
                item.setHidden(True)

        # Fill session rows (between contexts and files).
        for i, (item, card) in enumerate(self._session_rows):
            if i < len(session_results):
                card.set_expanded(False)  # always start collapsed on a fresh query
                card.update_session(session_results[i])
                item.setData(Qt.ItemDataRole.UserRole, session_results[i])
                item.setSizeHint(QSize(0, card.desired_height))
                item.setHidden(False)
            else:
                card.set_expanded(False)
                item.setHidden(True)

        # Fill file rows (below).
        groups = cluster_results(results) if results else []
        for i, (item, widget) in enumerate(self._rows):
            if i < len(groups):
                widget.update_group(groups[i], query)
                item.setData(Qt.ItemDataRole.UserRole, groups[i])
                item.setHidden(False)
            else:
                item.setHidden(True)

        self._show_results()
        # Land selection on the first visible row regardless of type.
        for i in range(self.results.count()):
            if not self.results.item(i).isHidden():
                self.results.setCurrentRow(i)
                break

    # ---------------------------------------------------------- preview

    def _on_row_changed(self, row: int) -> None:
        if row < 0 or row >= self.results.count():
            return
        item = self.results.item(row)
        if item is None or item.isHidden():
            return
        data = item.data(Qt.ItemDataRole.UserRole)

        # Dispatch on row type — episodic and file rows live in the
        # same QListWidget but their previews speak different shapes.
        if isinstance(data, EpisodicResult):
            # Pass up to two session neighbors so the preview can
            # show "around the same time" — gives episodic results
            # contextual depth without needing a timeline view.
            neighbors: list = []
            try:
                if data.session_id:
                    neighbors = [
                        ev
                        for ev in self.event_store.iter_events(days=2)
                        if ev.session_id == data.session_id
                        and (ev.payload.get("url") or "") != data.url
                    ][:2]
            except Exception:
                neighbors = []
            self.preview.show_episodic(data, neighbors=neighbors)
            return

        if isinstance(data, MicroContext):
            try:
                self.preview.show_context(data)
            except Exception:
                self.preview.show_empty(
                    "Context preview unavailable."
                )
            return

        if isinstance(data, Session):
            try:
                self.preview.show_session(data)
            except Exception:
                self.preview.show_empty(
                    "Session preview unavailable."
                )
            return

        if isinstance(data, MemoryGroup):
            already = set(data.all_paths)
            related = [
                p for p in self._related_files(data.primary.path, max_n=6)
                if p not in already
            ][:3]
            self.preview.update_group(data, self._latest_query, related)
            return

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
        """Timer callback for the flash timer — restore whichever footer
        text fits the current state (action hints in results, diagnostic
        line everywhere else)."""
        self._footer_pinned = False
        self._refresh_default_footer()

    def _flash_footer(self, msg: str) -> None:
        # A flash takes precedence over any in-flight loading indicator.
        self._loading_timer.stop()
        self._footer_pinned = True
        self.footer.setText(msg)
        self._footer_flash_timer.start(_FOOTER_FLASH_MS)

    def _refresh_default_footer(self) -> None:
        """Set the footer text to the contextually-correct default.

        Two modes:
          * Results state    → action hints (↑↓ ↵ esc) — these are the
                               keys the user actually needs at that moment.
          * Anywhere else    → quiet diagnostic line (memories / sessions /
                               last-active) — gives demos a "this thing is
                               alive" pulse without stealing attention.

        Skips entirely when a flash message is currently pinned, so
        confirmations like "Copied path …" never get clobbered.
        """
        if self._footer_pinned:
            return
        if self._state == "results":
            self.footer.setText(_FOOTER_DEFAULT)
        else:
            self.footer.setText(self._build_diagnostic())

    def _build_diagnostic(self) -> str:
        """Compose the tiny status line shown in idle states:

            "1,247 memories  ·  8 sessions  ·  Active 2m ago"

        All three segments are independent and any can be omitted —
        a fresh install with no folders and no events shows just
        "Ready." rather than a row of zeros.
        """
        parts: list[str] = []

        # Memories — uses the cached indexed_files dict so the second
        # paint is instant. The first call after launcher init may pay
        # one ChromaDB metadata read, but _populate_digest typically
        # warms the cache before we get here.
        try:
            n_files = len(self._indexed_files())
        except Exception:
            n_files = 0
        if n_files > 0:
            parts.append(f"{n_files:,} memories")

        # Sessions + last-active — derived from the local event log.
        # Skipped silently if no log exists or the user has disabled
        # episodic capture; nothing leaks across a privacy boundary.
        try:
            n_sessions = 0
            most_recent_ts: float | None = None
            seen_sessions: set[str] = set()
            for ev in self.event_store.iter_events(days=14):
                if ev.session_id:
                    seen_sessions.add(ev.session_id)
                if most_recent_ts is None:
                    most_recent_ts = ev.ts_epoch()
            n_sessions = len(seen_sessions)
        except Exception:
            n_sessions = 0
            most_recent_ts = None

        if n_sessions > 0:
            label = "session" if n_sessions == 1 else "sessions"
            parts.append(f"{n_sessions} {label}")
        if most_recent_ts:
            parts.append(f"Active {humanize_age(most_recent_ts)}")

        return "  ·  ".join(parts) if parts else "Ready."

    def _current_group(self) -> MemoryGroup | None:
        item = self.results.currentItem()
        if item is None or item.isHidden():
            return None
        g = item.data(Qt.ItemDataRole.UserRole)
        return g if isinstance(g, MemoryGroup) else None

    def _copy_selected_path(self) -> bool:
        item = self.results.currentItem()
        if item is None or item.isHidden():
            return False
        data = item.data(Qt.ItemDataRole.UserRole)

        # Episodic rows copy the captured URL — the closest analogue
        # to a file path.
        if isinstance(data, EpisodicResult):
            if not data.url:
                return False
            QApplication.clipboard().setText(data.url)
            self._flash_footer(f"Copied URL  ·  {data.title[:50]}")
            return True

        # Micro-context: same pattern as session — copy every openable
        # target. Useful for capturing a thread of attention.
        if isinstance(data, MicroContext):
            targets = [t for _, t in data.openable_targets()]
            if not targets:
                return False
            QApplication.clipboard().setText("\n".join(targets))
            self._flash_footer(
                f"Copied context  ·  {len(targets)} link(s) from {data.topic[:40]}"
            )
            return True

        # Session rows copy a newline-separated list of every URL +
        # path inside the session. Useful for sharing the context of
        # what the user was working on.
        if isinstance(data, Session):
            targets = [t for _, t in data.openable_targets()]
            if not targets:
                return False
            QApplication.clipboard().setText("\n".join(targets))
            self._flash_footer(
                f"Copied session  ·  {len(targets)} link(s) from {data.topic[:40]}"
            )
            return True

        if isinstance(data, MemoryGroup):
            QApplication.clipboard().setText(data.primary.path)
            self._flash_footer(f"Copied path  ·  {data.primary.name}")
            return True
        return False

    def _copy_memory_summary(self) -> bool:
        """Copy a human memory blob — title, why, sources — to clipboard.

        Only meaningful for file (MemoryGroup) selections; episodic rows
        already carry their own short-form payload, so Ctrl+M on them
        is a no-op rather than a confusing partial export.
        """
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
        self._flash_footer(f"Copied memory  ·  {title}")
        return True

    def _on_enter(self) -> None:
        item = self.results.currentItem()
        if item is None or item.isHidden():
            # Fall back to first visible row across both episodic + file
            # sets — walk the live QListWidget rather than self._rows so
            # episodic rows are reachable via Enter even when nothing is
            # explicitly selected.
            for i in range(self.results.count()):
                cand_item = self.results.item(i)
                if cand_item is not None and not cand_item.isHidden():
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
        data = item.data(Qt.ItemDataRole.UserRole)

        # Episodic rows open their captured URL in the system default
        # browser. Same micro-feedback grammar as file opens so the
        # confirmation vocabulary stays consistent across row types.
        if isinstance(data, EpisodicResult):
            url = data.url
            if not url:
                self._flash_footer("Nothing to open  ·  no URL captured")
                return
            opened = _open_file(url)
            display = data.title[:60]
            if opened:
                self._flash_footer(f"Opened in browser  ·  {display}")
                QTimer.singleShot(160, self.hide)
            else:
                self._flash_footer(f"Couldn't open  ·  {display}")
            return

        # Micro-context rows: same expand-then-act pattern as sessions.
        # First Enter expands the card, second Enter triggers Resume.
        if isinstance(data, MicroContext):
            card = self.results.itemWidget(item)
            if isinstance(card, ContextCard):
                if not card.expanded:
                    card.set_expanded(True)
                    return
                self._resume_context(data)
            return

        # Session rows: first Enter expands the card; second Enter
        # triggers Continue. This mirrors how Spotlight/Raycast handle
        # multi-action rows — never collapse two intents into one
        # ambiguous keystroke.
        if isinstance(data, Session):
            # Find the SessionCard widget for this row.
            card = self.results.itemWidget(item)
            if isinstance(card, SessionCard):
                if not card.expanded:
                    card.set_expanded(True)
                    return
                self._continue_session(data)
            return

        group = data
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
        # Episodic capture: log intent before the OS call. Pairs naturally
        # with the preceding query event so the event log reads as
        # "user searched X → user opened Y" — the smallest useful shape
        # of episodic memory.
        if is_reveal:
            self.event_logger.log_reveal(path, title)
        else:
            self.event_logger.log_open(path, title)

        opened = _reveal(path) if is_reveal else _open_file(path)
        if opened:
            # Past-tense confirmation. The OS open is synchronous on
            # Windows, so by the moment the user perceives the flash,
            # the action has actually completed. Reveals additionally
            # name the destination ("Opened in Explorer") so the user
            # knows where to look.
            filename = Path(path).name
            self._flash_footer(
                f"Opened in Explorer  ·  {filename}" if is_reveal
                else f"Opened  ·  {title}"
            )
            # Slightly longer than the previous 140 ms — the past-tense
            # message has more text and deserves to be readable.
            QTimer.singleShot(160, self.hide)
        elif self._demo_mode:
            # Demo paths intentionally don't exist on disk. Tell the
            # truth — calling it "opened" would be misleading even in
            # a demo, where the real value is the preview pane the
            # user just saw.
            self._flash_footer(f"Demo memory  ·  {title}")
            QTimer.singleShot(700, self.hide)
        else:
            # Real file is missing — likely moved or deleted since we
            # indexed it. Stay open so the user can pick something else.
            self._flash_footer(f"Couldn't open  ·  {title}")

    # -- Phase 1F micro-context helpers -----------------------------

    def _on_context_expanded(
        self,
        item: QListWidgetItem,
        card: ContextCard,
        expanded: bool,
    ) -> None:
        item.setSizeHint(QSize(0, card.desired_height))
        if self._state == "results":
            self._show_results()

    def _resume_context(self, ctx: MicroContext) -> None:
        """Reopen every captured URL/file inside the micro-context.

        Same handoff pattern as `_continue_session` — sequence of
        OS opens, no staggering, flash for acknowledgment, hide after
        220 ms. The micro-context is a tighter slice than a session,
        so 'Resume' rather than 'Continue' is the right verb.
        """
        targets = ctx.openable_targets()
        if not targets:
            self._flash_footer("No openable targets in this context")
            return

        opened = 0
        for _, target in targets:
            if _open_file(target):
                opened += 1

        topic = ctx.topic or "context"
        if opened > 0:
            self._flash_footer(
                f"Resuming  ·  {opened} of {len(targets)} reopened from {topic}"
            )
            QTimer.singleShot(220, self.hide)
        else:
            self._flash_footer(
                "Couldn't reopen  ·  paths may have moved"
            )

    # -- Phase 1E session helpers -----------------------------------

    def _on_session_expanded(
        self,
        item: QListWidgetItem,
        card: SessionCard,
        expanded: bool,
    ) -> None:
        """Update the QListWidgetItem's size hint so the row visibly
        grows/shrinks when the card toggles. Then re-run the adaptive
        height pass so the launcher resizes too."""
        item.setSizeHint(QSize(0, card.desired_height))
        if self._state == "results":
            self._show_results()

    def _continue_session(self, session: Session) -> None:
        """Reopen every captured URL/file in the session.

        OS file/URL handlers are async so we just hand them all off in
        sequence — the OS queues the launches itself. The flash makes
        the action feel intentional even when the OS opens are silent.
        """
        targets = session.openable_targets()
        if not targets:
            self._flash_footer("No openable targets in this session")
            return

        opened = 0
        for kind, target in targets:
            if _open_file(target):
                opened += 1

        topic = session.topic or "session"
        if opened > 0:
            self._flash_footer(
                f"Continuing  ·  {opened} of {len(targets)} reopened from {topic}"
            )
            QTimer.singleShot(220, self.hide)
        else:
            self._flash_footer(
                f"Couldn't reopen  ·  paths may have moved"
            )

    def _move_selection(self, delta: int) -> None:
        """Move the highlighted result by `delta` rows. No wraparound —
        at the edges the selection sticks. Walks every visible item in
        the QListWidget (episodic + file), so arrow keys flow through
        both row types as one continuous list."""
        if self._state != "results":
            return
        visible = [
            i for i in range(self.results.count())
            if not self.results.item(i).isHidden()
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
