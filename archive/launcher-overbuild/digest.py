"""Phase 6I — DigestColumn + EmptyDigest.

Composes the centre column of the v3 shell. Two surfaces:

  - ``DigestColumn``  — Continue + Active investigations + Recent
                        returns + Trust, in that order. The
                        directive's *main view*.
  - ``EmptyDigest``   — the first-run empty surface (No work yet,
                        with the Phase 6D Show example / Start
                        normally button pair + a trust line).

Both surfaces are dynamic-sized: the column flexes between
`min_width` and a sensible max, and individual cards size to their
content (no hardcoded heights other than the `RecoveryCardV3.HEIGHT`
spec the directive named).
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .investigation_panel import InvestigationCardV3, InvestigationPanel
from .recovery_panel import RecoveryCardV3, RecoveryPanel
from .surfaces import GlassCard
from .trust_panel import TrustPanel


class DigestColumn(QWidget):
    """The populated digest. Section order is fixed by the directive.

    Cards are *added* via the panel methods rather than constructed in
    the column's __init__ so the caller controls the data source
    (capture script vs. live launcher vs. unit test)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.SECTION_GAP)

        self.recovery = RecoveryPanel()
        self.investigations = InvestigationPanel()
        self.trust = TrustPanel()

        layout.addWidget(self.recovery)
        layout.addWidget(self.investigations)
        layout.addWidget(self.trust)
        layout.addStretch(1)

    def populate(
        self,
        *,
        recoveries: List[RecoveryCardV3],
        investigations: List[InvestigationCardV3],
    ) -> None:
        self.recovery.clear()
        for c in recoveries:
            self.recovery.add_card(c)
        self.investigations.clear()
        for c in investigations:
            self.investigations.add_card(c)


class EmptyDigest(QWidget):
    """First-run empty surface.

    Headline:   *Recall notices unfinished work.*
    Body:       *Work normally.* / *Return later.* / *Recall fills itself.*
    Buttons:    *Show example*  +  *Start normally*
    Trust line: ``local only · 127.0.0.1:4545 · no cloud``

    The two buttons emit dedicated Qt signals (``show_example`` /
    ``start_normally``); the live launcher decides what to do with
    them — same contract as `app/ui/cards.py:EmptyCard`."""

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addStretch(1)

        card = GlassCard(radius=T.RADIUS_HERO)
        body = QVBoxLayout(card)
        body.setContentsMargins(36, 36, 36, 28)
        body.setSpacing(14)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # eyebrow dot + label
        head_row = QHBoxLayout()
        head_row.setSpacing(8)
        head_row.addStretch(1)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"QLabel {{ background: {T.ACCENT}; border-radius: 4px; }}"
        )
        eyebrow = QLabel("NO WORK YET")
        f = QFont()
        f.setPointSizeF(7.6)
        f.setBold(True)
        eyebrow.setFont(f)
        eyebrow.setStyleSheet(
            f"color: {T.ACCENT}; letter-spacing: 1.4px;"
            f"background: transparent;"
        )
        head_row.addWidget(dot)
        head_row.addWidget(eyebrow)
        head_row.addStretch(1)
        body.addLayout(head_row)

        headline = QLabel("Recall notices unfinished work.")
        hf = QFont()
        hf.setPointSizeF(17)
        hf.setBold(True)
        headline.setFont(hf)
        headline.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.addWidget(headline)

        sub = QLabel(
            "Work normally.  Return later.\nRecall fills itself."
        )
        sub.setStyleSheet(
            f"color: {T.INK_2}; font-size: 13px;"
            f"background: transparent; line-height: 1.55;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        body.addWidget(sub)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addStretch(1)
        primary = QPushButton("Show example")
        primary.setCursor(Qt.CursorShape.PointingHandCursor)
        primary.setFixedHeight(34)
        primary.setStyleSheet(
            f"QPushButton {{"
            f"  background: {T.ACCENT_SOFT};"
            f"  color: {T.ACCENT};"
            f"  border: 1px solid {T.ACCENT_LINE};"
            f"  border-radius: 10px;"
            f"  padding: 0 16px;"
            f"  font-size: 12px;"
            f"  font-weight: 600;"
            f"}}"
            f"QPushButton:hover {{ background: rgba(139, 127, 227, 50); }}"
        )
        primary.clicked.connect(self.show_example.emit)

        secondary = QPushButton("Start normally")
        secondary.setCursor(Qt.CursorShape.PointingHandCursor)
        secondary.setFixedHeight(34)
        secondary.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {T.INK_3};"
            f"  border: 1px solid {T.HAIRLINE};"
            f"  border-radius: 10px;"
            f"  padding: 0 14px;"
            f"  font-size: 12px;"
            f"  font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
        )
        secondary.clicked.connect(self.start_normally.emit)

        button_row.addWidget(primary)
        button_row.addWidget(secondary)
        button_row.addStretch(1)
        body.addLayout(button_row)

        trust_line = QLabel("local only · 127.0.0.1:4545 · no cloud")
        trust_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trust_line.setStyleSheet(
            f"color: {T.INK_4}; font-size: 10.5px; padding-top: 6px;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"background: transparent;"
        )
        body.addWidget(trust_line)

        # Centre the card in the column.
        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addWidget(card)
        wrap.addStretch(1)
        outer.addLayout(wrap)
        outer.addStretch(1)


__all__ = ["DigestColumn", "EmptyDigest"]
