"""Phase 7E — Launcher Final Product Pass · hero.

A compact 110-px Continue card sitting *inside* the white
inner card. Three signal variants drive the left accent rail:

    HIGH  →  filled lavender rail + `HIGH` filled pill
    MED   →  soft lavender rail + `MED` outline pill
    LOW   →  outline rail (no fill) + `LOW` ghost pill

Layout (all inside one row):

    | TITLE                                  Resume   1 |
    |  evidence row - file / tab counts        HIGH    |
    \\
     accent rail (variant)

Pre-7E variant (220-px Continue document w/ bulleted body)
lives at ``archive/launcher-7b1/recovery_panel_7b1.py``.
"""

from __future__ import annotations

from typing import List, Literal, Optional, Tuple

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


Signal = Literal["high", "med", "low"]

_RESUME_WIDTH = 96
_REVIEW_WIDTH = 80


# ── evidence helper ──────────────────────────────────────────────


def _evidence_from_targets(
    targets: List[Tuple[str, str]],
    extra: Optional[str] = None,
) -> str:
    """Turn the candidate's targets into an inline evidence row:
    *2 files - 2 tabs - returned 2d*. Same buckets the resume
    preview uses."""
    files = chats = tabs = searches = 0
    chat_hosts = (
        "claude.ai", "chat.openai.com", "chatgpt.com",
        "gemini.google.com", "perplexity.ai", "poe.com",
    )
    search_hosts = (
        "google.com/search", "duckduckgo.com/?q=",
        "bing.com/search", "kagi.com/search",
    )
    for kind, target in targets:
        if kind == "path":
            files += 1
            continue
        lowered = (target or "").lower()
        if any(h in lowered for h in chat_hosts):
            chats += 1
        elif any(h in lowered for h in search_hosts):
            searches += 1
        else:
            tabs += 1
    parts: list[str] = []
    if files:
        parts.append(f"{files} file{'s' if files != 1 else ''}")
    if tabs:
        parts.append(f"{tabs} tab{'s' if tabs != 1 else ''}")
    if chats:
        parts.append(f"{chats} chat{'s' if chats != 1 else ''}")
    if searches:
        parts.append(f"{searches} search{'es' if searches != 1 else ''}")
    if extra:
        parts.append(extra)
    return "  -  ".join(parts)


# ── elider label ─────────────────────────────────────────────────


class _EliderLabel(QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self._full_text = text

    def setText(self, text: str) -> None:  # type: ignore[override]
        self._full_text = text
        super().setText(text)
        self._reflow()

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        self._reflow()

    def _reflow(self) -> None:
        from PyQt6.QtGui import QFontMetrics
        if not self._full_text:
            return
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(
            self._full_text, Qt.TextElideMode.ElideRight,
            max(0, self.width() - 4),
        )
        if elided != super().text():
            QLabel.setText(self, elided)


# ── confidence pill ──────────────────────────────────────────────


def _confidence_pill(signal: Signal) -> QLabel:
    """Tiny pill that matches the signal variant's tone."""
    text = {"high": "HIGH", "med": "MED", "low": "LOW"}[signal]
    pill = QLabel(text)
    pill.setFixedHeight(16)
    pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pill.setContentsMargins(8, 0, 8, 0)
    f = QFont()
    f.setPointSizeF(7.5)
    f.setBold(True)
    pill.setFont(f)
    if signal == "high":
        pill.setStyleSheet(
            f"QLabel {{"
            f"  color: white; background: {T.ACCENT};"
            f"  border-radius: 8px; padding: 0 8px;"
            f"  letter-spacing: 1.0px;"
            f"}}"
        )
    elif signal == "med":
        pill.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.ACCENT}; background: {T.ACCENT_SOFT};"
            f"  border-radius: 8px; padding: 0 8px;"
            f"  letter-spacing: 1.0px;"
            f"}}"
        )
    else:  # low
        pill.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.INK_3}; background: transparent;"
            f"  border: 1px solid {T.BORDER_RAISED};"
            f"  border-radius: 8px; padding: 0 8px;"
            f"  letter-spacing: 1.0px;"
            f"}}"
        )
    return pill


# ── Resume + Review buttons ─────────────────────────────────────
#
# Phase 9 — the recovery hero ships with a *pair* of buttons:
# a filled `Resume` (primary action, lavender fill) and a flat
# `Review` (secondary action, ghost outline). The pair sits in
# the title row so the user can either commit (Resume) or open
# the resume-preview overlay (Review) without leaving the hero.


class _PillButton(QWidget):
    """Shared pill geometry. Variant controls fill vs outline."""

    HEIGHT = 30
    clicked = pyqtSignal()

    def __init__(
        self,
        label: str,
        *,
        width: int,
        variant: Literal["filled", "ghost"] = "filled",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._variant = variant
        self.setFixedHeight(self.HEIGHT)
        self.setFixedWidth(width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)
        lbl = QLabel(label)
        f = QFont()
        f.setPointSizeF(10.5)
        f.setBold(variant == "filled")
        lbl.setFont(f)
        if variant == "filled":
            lbl.setStyleSheet(
                "color: white; background: transparent; padding: 0;"
            )
        else:
            lbl.setStyleSheet(
                f"color: {T.INK_2}; background: transparent; padding: 0;"
            )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl, 1)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        if self._variant == "filled":
            p.fillPath(path, QColor(T.ACCENT))
        else:
            pen = QPen(QColor(T.HAIRLINE_STRONG))
            pen.setWidthF(1.0)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path)
        p.end()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


def _ResumeButton() -> _PillButton:
    return _PillButton("Resume", width=_RESUME_WIDTH, variant="filled")


def _ReviewButton() -> _PillButton:
    return _PillButton("Review", width=_REVIEW_WIDTH, variant="ghost")


# ── card ─────────────────────────────────────────────────────────


class RecoveryCardV3(QWidget):
    """The 7E Continue hero. 110-px row sitting inside the white
    inner card. Title row (title + Resume) + evidence row (counts
    + confidence pill), with a 6-px left accent rail painted in
    the signal variant.

    Emits ``restore(candidate_id, title, n_targets)`` on Enter /
    Space / `1` / Resume click. ``review(candidate_id)`` fires
    when the user clicks the secondary `Review` button (the
    Phase 9 hero pair) -- intended for the launcher to surface
    the resume-preview overlay without committing to a restore.
    """

    restore = pyqtSignal(str, str, int)
    review = pyqtSignal(str)

    HEIGHT = 110
    ACCENT_STRIP_W = 6

    def __init__(
        self,
        candidate_id: str,
        title: str,
        *,
        targets: Optional[List[Tuple[str, str]]] = None,
        extra_clause: Optional[str] = None,
        signal: Signal = "high",
        n_targets: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._signal: Signal = signal
        self._focused = False
        self._evidence = (
            _evidence_from_targets(targets or [], extra=extra_clause)
            if targets is not None or extra_clause
            else ""
        )

        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        outer = QHBoxLayout(self)
        # Left padding clears the 6-px accent rail + 12-px inset.
        outer.setContentsMargins(self.ACCENT_STRIP_W + 14, 16, 14, 14)
        outer.setSpacing(12)

        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        # ── title row ──
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_lbl = _EliderLabel(title)
        tf = QFont()
        tf.setPointSizeF(14.0)
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
            f"letter-spacing: -0.2px;"
        )
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_row.addWidget(title_lbl, 1)
        review_btn = _ReviewButton()
        review_btn.clicked.connect(
            lambda: self.review.emit(self._cid)
        )
        resume_btn = _ResumeButton()
        resume_btn.clicked.connect(
            lambda: self.restore.emit(self._cid, self._title, self._n)
        )
        title_row.addWidget(review_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        title_row.addSpacing(8)
        title_row.addWidget(resume_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        col.addLayout(title_row)

        col.addStretch(1)

        # ── evidence row + confidence pill ──
        ev_row = QHBoxLayout()
        ev_row.setContentsMargins(0, 0, 0, 0)
        ev_row.setSpacing(10)
        ev_lbl = QLabel(self._evidence or "")
        ev_lbl.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"font-size: 11px;"
        )
        ev_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        ev_row.addWidget(ev_lbl, 1)
        ev_row.addWidget(_confidence_pill(self._signal), 0, Qt.AlignmentFlag.AlignVCenter)
        col.addLayout(ev_row)

        outer.addLayout(col, 1)

    # ── paint ──

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # The hero sits directly on the inner white card — no card
        # body, no shadow, no border on the row itself. Only the
        # left accent rail is painted, varied by signal.
        rail = QPainterPath()
        rail.addRoundedRect(
            QRectF(0, 6, self.ACCENT_STRIP_W, self.height() - 12),
            3, 3,
        )
        if self._signal == "high":
            p.fillPath(rail, QColor(T.ACCENT))
        elif self._signal == "med":
            p.fillPath(rail, QColor(T.ACCENT_SOFT))
        else:  # low
            # Outline-only rail — paint the stroke, leave fill empty.
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(1.2)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(rail)
        # Focus ring — a calm lavender outline around the row.
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(1.0)
            p.setPen(pen)
            outline = QPainterPath()
            outline.addRoundedRect(
                QRectF(self.ACCENT_STRIP_W + 6, 4,
                       self.width() - self.ACCENT_STRIP_W - 8,
                       self.height() - 8),
                10, 10,
            )
            p.drawPath(outline)
        p.end()

    # ── interaction ──

    def focusInEvent(self, _e) -> None:  # type: ignore[override]
        self._focused = True
        self.update()

    def focusOutEvent(self, _e) -> None:  # type: ignore[override]
        self._focused = False
        self.update()

    def keyPressEvent(self, e: QKeyEvent) -> None:  # type: ignore[override]
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space, Qt.Key.Key_1):
            self.restore.emit(self._cid, self._title, self._n)
            return
        super().keyPressEvent(e)

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.restore.emit(self._cid, self._title, self._n)


__all__ = ["RecoveryCardV3", "Signal"]
