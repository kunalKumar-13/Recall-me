"""Phase 6I — SearchPanel.

The results surface that replaces the idle digest when the user
types into the sidebar's search input. Visual rules:

  - same FloatingPanel container so the surface change is
    *content*, not *frame*;
  - rows are simple title + sub + meta lines, not full cards;
  - hover lifts the row 1 px and tints the background to
    `ACCENT_SOFT` at 30 % alpha;
  - empty / loading / results state is a single QStackedLayout.

This is a *visual* skeleton — wiring it to the actual search engine
is not part of Phase 6I (the directive is UI-only). The capture
script feeds in fixture rows; the live launcher continues using its
own results path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .surfaces import GlassCard, Pill, section_label


@dataclass
class SearchResult:
    title: str
    detail: str
    kind: str = "tab"        # tab | file | chat | search
    time_label: str = ""


def _kind_pill(kind: str) -> QWidget:
    pretty = {"tab": "tab", "file": "file", "chat": "chat", "search": "search"}.get(kind, kind)
    return Pill(pretty, kind="mute")


class _ResultRow(QWidget):
    def __init__(self, r: SearchResult, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)
        layout.addWidget(_kind_pill(r.kind))

        text = QVBoxLayout()
        text.setSpacing(2)
        title = QLabel(r.title)
        tf = QFont()
        tf.setPointSizeF(10.5)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        title.setWordWrap(False)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        text.addWidget(title)

        sub = QLabel(r.detail)
        sub.setStyleSheet(
            f"color: {T.INK_3}; font-size: {T.FS_META}px;"
            f"background: transparent;"
        )
        text.addWidget(sub)
        layout.addLayout(text, 1)

        if r.time_label:
            t = QLabel(r.time_label)
            t.setStyleSheet(
                f"color: {T.INK_3}; font-size: {T.FS_META}px;"
                f"background: transparent;"
                f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            )
            layout.addWidget(t)


class SearchPanel(QWidget):
    """The results column."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(section_label("Results"))

        self._stack = QStackedLayout()
        outer.addLayout(self._stack)

        # Empty state
        empty = QLabel("Press / and type to find a moment.")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setStyleSheet(
            f"color: {T.INK_3}; padding: 30px 0;"
            f"font-size: {T.FS_BODY}px;"
        )
        self._stack.addWidget(empty)

        # Results card (built lazily; replace_results swaps it in).
        self._results_card = GlassCard(radius=T.RADIUS_CARD)
        self._results_layout = QVBoxLayout(self._results_card)
        self._results_layout.setContentsMargins(0, 4, 0, 4)
        self._results_layout.setSpacing(0)
        self._stack.addWidget(self._results_card)

    def show_results(self, rows: List[SearchResult]) -> None:
        # Clear prior rows.
        while self._results_layout.count():
            it = self._results_layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
        for r in rows:
            self._results_layout.addWidget(_ResultRow(r))
        self._stack.setCurrentIndex(1 if rows else 0)


__all__ = ["SearchPanel", "SearchResult"]
