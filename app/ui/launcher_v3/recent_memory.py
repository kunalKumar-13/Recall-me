"""Phase 7E — Launcher Final Product Pass · RECENT MEMORY panel.

A new section between the Continue hero and OTHER WORK that
fixes the *"memory invisible"* problem the prior launcher
shapes had. Up to 5 rows from `~/.recall/events/YYYY-MM-DD.jsonl`,
rendered as:

  21:32   ChatGPT      RLHF reward shaping
  21:28   GitHub       websocket retry
  21:20   Stitch       launcher redesign
  21:11   Google       resume flow

Each row carries: time (mono `HH:MM`) + source (short bold
domain or platform) + label (the page / chat / search title).
Rows render directly on the inner card, no chrome, no
dividers — calm.

Data plumbing lives in ``LiveLauncher._populate_digest``;
this widget is geometry-only. The Phase 7D `recall capture
status` CLI proves the same data path lands on disk.
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
    QVBoxLayout,
    QWidget,
)

from . import theme as T


@dataclass(frozen=True)
class MemoryRow:
    """One row's data. Decoupled from the engine's `Event` type
    so the widget can stay Qt-only + the digest loader can map
    any source (live, demo, capture replay)."""

    time: str       # `HH:MM`
    source: str     # `ChatGPT` / `GitHub` / `Google` / domain
    label: str      # event title


class _Row(QWidget):
    """One memory row. 18 px tall, three-column grid."""

    HEIGHT = 18
    TIME_W = 50
    SOURCE_W = 90

    def __init__(
        self,
        row: MemoryRow,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 4, 0)
        layout.setSpacing(10)

        # Time column — mono so the columns line up regardless of
        # the row's text content.
        time = QLabel(row.time)
        tf = QFont()
        tf.setPointSizeF(8.5)
        time.setFont(tf)
        time.setStyleSheet(
            f"color: {T.INK_4}; background: transparent;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"letter-spacing: 0.2px;"
        )
        time.setFixedWidth(self.TIME_W)
        layout.addWidget(time, 0, Qt.AlignmentFlag.AlignVCenter)

        # Source — bold platform/host label.
        source = QLabel(row.source)
        sf = QFont()
        sf.setPointSizeF(9.0)
        sf.setBold(True)
        source.setFont(sf)
        source.setStyleSheet(
            f"color: {T.INK_2}; background: transparent;"
        )
        source.setFixedWidth(self.SOURCE_W)
        layout.addWidget(source, 0, Qt.AlignmentFlag.AlignVCenter)

        # Label — flex; elide if too long.
        from PyQt6.QtGui import QFontMetrics
        label = QLabel(row.label)
        lf = QFont()
        lf.setPointSizeF(9.5)
        label.setFont(lf)
        label.setStyleSheet(
            f"color: {T.INK_2}; background: transparent;"
        )
        label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred,
        )
        self._label = label
        self._raw_label = row.label
        layout.addWidget(label, 1, Qt.AlignmentFlag.AlignVCenter)

        self._fm = QFontMetrics(lf)

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        avail = max(0, self._label.width() - 4)
        elided = self._fm.elidedText(
            self._raw_label, Qt.TextElideMode.ElideRight, avail,
        )
        if elided != self._label.text():
            self._label.setText(elided)


class RecentMemoryList(QWidget):
    """Up to **5** memory rows, stacked directly on the inner
    card. Hidden entirely when no memory is available so the
    launcher's eyebrow doesn't surface a blank section."""

    MAX_VISIBLE = 5

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self._layout = layout
        self._rows: List[_Row] = []

    def populate(self, items: List[MemoryRow]) -> None:
        while self._layout.count():
            it = self._layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
        self._rows.clear()
        for row in items[: self.MAX_VISIBLE]:
            w = _Row(row)
            self._rows.append(w)
            self._layout.addWidget(w)


__all__ = ["MemoryRow", "RecentMemoryList"]
