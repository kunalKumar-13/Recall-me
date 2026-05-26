"""Phase 6P — Resume preview overlay.

A light overlay sheet that sits between *click Resume* and *the
OS opens tabs/files*. The user sees what's about to happen and
chooses Cancel or Resume now.

    ┌────────────────────────────────────────┐
    │  Continue                               │
    │  WebSocket retry debugging              │
    │                                         │
    │  Will reopen                            │
    │    · 2 tabs                             │
    │    · 2 files                            │
    │    · 1 search                           │
    │                                         │
    │  [ Cancel ]            [ Resume now ]   │
    └────────────────────────────────────────┘

No full dialog. No modal darkening of the host window. Just a
small panel painted on top of the digest column.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


def _classify_counts(
    targets: List[Tuple[str, str]],
) -> List[Tuple[str, int]]:
    """Bucket targets into (label, count) rows for the preview body.
    Same buckets the engine's `plan_for` uses; we reimplement the
    grouping locally so the preview never depends on a network round-
    trip — the launcher already has the candidate's targets in hand.
    """
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
    rows: list[Tuple[str, int]] = []
    if files:
        rows.append((f"{files} file{'s' if files != 1 else ''}", files))
    if chats:
        rows.append((f"{chats} chat{'s' if chats != 1 else ''}", chats))
    if tabs:
        rows.append((f"{tabs} tab{'s' if tabs != 1 else ''}", tabs))
    if searches:
        rows.append((f"{searches} search{'es' if searches != 1 else ''}", searches))
    return rows


class ResumePreview(QWidget):
    """The preview overlay. Painted on top of the host launcher's
    digest area; the host calls `open(...)` to populate + show, and
    listens for `accepted` / `cancelled`.

    Emits:
      - `accepted(candidate_id, title)` when the user presses Resume
      - `cancelled()` when the user presses Cancel or Esc
    """

    accepted = pyqtSignal(str, str)
    cancelled = pyqtSignal()

    WIDTH = 420

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._cid = ""
        self._title = ""
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedWidth(self.WIDTH)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_LIFT_RADIUS)
        eff.setOffset(0, T.SHADOW_LIFT_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_LIFT_ALPHA))
        self.setGraphicsEffect(eff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 18, 22, 16)
        outer.setSpacing(10)

        eyebrow = QLabel("CONTINUE")
        ef = QFont()
        ef.setPointSizeF(8.0)
        ef.setBold(True)
        eyebrow.setFont(ef)
        eyebrow.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"letter-spacing: 1.4px;"
        )
        outer.addWidget(eyebrow)

        self._title_lbl = QLabel("")
        tf = QFont()
        tf.setPointSizeF(T.FS_HERO - 4)
        tf.setBold(True)
        self._title_lbl.setFont(tf)
        self._title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        self._title_lbl.setWordWrap(True)
        outer.addWidget(self._title_lbl)

        outer.addSpacing(4)

        will_lbl = QLabel("Will reopen")
        will_lbl.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"font-size: {T.FS_META}px;"
        )
        outer.addWidget(will_lbl)

        self._rows_holder = QVBoxLayout()
        self._rows_holder.setContentsMargins(0, 0, 0, 0)
        self._rows_holder.setSpacing(4)
        outer.addLayout(self._rows_holder)

        outer.addSpacing(8)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.setFixedHeight(34)
        self._cancel_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {T.INK_2};"
            f"  border: 1px solid {T.HAIRLINE};"
            f"  border-radius: 10px;"
            f"  padding: 0 16px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
        )
        self._cancel_btn.clicked.connect(self._on_cancel)

        self._resume_btn = QPushButton("Resume now")
        self._resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._resume_btn.setFixedHeight(34)
        self._resume_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background: {T.ACCENT};"
            f"  color: white;"
            f"  border: none;"
            f"  border-radius: 10px;"
            f"  padding: 0 18px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 600;"
            f"}}"
            f"QPushButton:hover {{ background: #7A6FD4; }}"
        )
        self._resume_btn.clicked.connect(self._on_accept)

        buttons.addStretch(1)
        buttons.addWidget(self._cancel_btn)
        buttons.addWidget(self._resume_btn)
        outer.addLayout(buttons)

        self.hide()

    # ── public ──────────────────────────────────────────────────────

    def open(
        self,
        candidate_id: str,
        title: str,
        targets: List[Tuple[str, str]],
    ) -> None:
        """Populate + show. The host is responsible for positioning
        the widget — the overlay is geometry-agnostic."""
        self._cid = candidate_id
        self._title = title or "(untitled)"
        self._title_lbl.setText(self._title)
        self._populate_rows(targets)
        self.show()
        self.raise_()
        self._resume_btn.setFocus(Qt.FocusReason.PopupFocusReason)

    def close_preview(self) -> None:
        """Hide without firing either signal. Used by the host when
        the launcher is dismissed mid-preview."""
        self.hide()

    # ── populate ────────────────────────────────────────────────────

    def _populate_rows(self, targets: List[Tuple[str, str]]) -> None:
        while self._rows_holder.count():
            it = self._rows_holder.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
        rows = _classify_counts(targets)
        if not rows:
            empty = QLabel("nothing to reopen")
            empty.setStyleSheet(
                f"color: {T.INK_3}; background: transparent;"
                f"font-size: {T.FS_BODY}px;"
            )
            self._rows_holder.addWidget(empty)
            return
        for label, _ in rows:
            row = QLabel(f"·  {label}")
            row.setStyleSheet(
                f"color: {T.INK_2}; background: transparent;"
                f"font-size: {T.FS_BODY}px;"
                f"padding-left: 8px;"
            )
            self._rows_holder.addWidget(row)

    # ── paint ───────────────────────────────────────────────────────

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 18, 18)
        p.fillPath(path, QColor(T.BG_RAISED))
        from PyQt6.QtGui import QPen
        pen = QPen(QColor(228, 222, 214))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    # ── interaction ─────────────────────────────────────────────────

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() == Qt.Key.Key_Escape:
            self._on_cancel()
            return
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_accept()
            return
        super().keyPressEvent(e)

    def _on_cancel(self) -> None:
        self.hide()
        self.cancelled.emit()

    def _on_accept(self) -> None:
        cid, title = self._cid, self._title
        self.hide()
        self.accepted.emit(cid, title)


__all__ = ["ResumePreview", "_classify_counts"]
