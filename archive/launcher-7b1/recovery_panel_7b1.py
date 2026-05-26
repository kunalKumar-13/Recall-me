"""Phase 7B.1 — Launcher Visual Merge · Continue document.

The recovery hero is now a **document-preview card**, not a
command-palette row. Big, calm, document-feel:

    +-----------------------------------------------+
    |  CONTINUE                                     |
    |  WebSocket retry debugging                    |
    |                                               |
    |    .  2 files                                 |
    |    .  2 tabs                                  |
    |    .  returned after 2d                       |
    |                                               |
    |                            [ Resume      1 ]  |
    +-----------------------------------------------+

The 6-px lavender accent rail stays at the left edge — it's
the focal-point signal. A subtle white card body + 1-px
hairline gives the document its own object-shape inside the
white workspace. Padding is generous; the card breathes.

Pre-7B.1 variant (the 88-px command-palette row) lives at
``archive/launcher-raycast/recovery_panel_7b.py``.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

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


_BODY_MAX = 4
_RESUME_WIDTH = 116


def _body_from_targets(
    targets: List[Tuple[str, str]],
    extra: Optional[str] = None,
) -> List[str]:
    """Turn the candidate's targets into the document's bulleted
    body lines: *2 files / 2 tabs / 1 chat / 1 search* +,
    optionally, the *returned after Nd* clause appended last."""
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
    body: list[str] = []
    if files:
        body.append(f"{files} file{'s' if files != 1 else ''}")
    if tabs:
        body.append(f"{tabs} tab{'s' if tabs != 1 else ''}")
    if chats:
        body.append(f"{chats} chat{'s' if chats != 1 else ''}")
    if searches:
        body.append(f"{searches} search{'es' if searches != 1 else ''}")
    if extra:
        body.append(extra)
    return body[:_BODY_MAX]


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


# ── Resume button ────────────────────────────────────────────────


class _ResumeButton(QWidget):
    HEIGHT = 34
    WIDTH = _RESUME_WIDTH

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setFixedWidth(self.WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(8)

        label = QLabel("Resume")
        f = QFont()
        f.setPointSizeF(10.5)
        f.setBold(True)
        label.setFont(f)
        label.setStyleSheet("color: white; background: transparent; padding: 0;")
        layout.addWidget(label, 1)

        chip = QLabel("1")
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setFixedSize(18, 18)
        chip.setStyleSheet(
            "QLabel {"
            "  background: rgba(255, 255, 255, 0.20);"
            "  color: white;"
            "  border-radius: 5px;"
            "  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            "  font-size: 10px;"
            "  font-weight: 600;"
            "}"
        )
        layout.addWidget(chip, 0)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 9, 9)
        p.fillPath(path, QColor(T.ACCENT))
        p.end()


# ── card ─────────────────────────────────────────────────────────


class RecoveryCardV3(QWidget):
    """The 7B.1 Continue document. Document-preview card: eyebrow
    + 18-pt title + bulleted body + right-aligned Resume.

    Emits ``restore(candidate_id, title, n_targets)`` on Enter /
    Space / `1` / click.
    """

    restore = pyqtSignal(str, str, int)

    HEIGHT = 220
    ACCENT_STRIP_W = 6
    RADIUS = 16

    def __init__(
        self,
        candidate_id: str,
        title: str,
        *,
        body: Optional[List[str]] = None,
        targets: Optional[List[Tuple[str, str]]] = None,
        extra_clause: Optional[str] = None,
        n_targets: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._focused = False

        if body is not None:
            self._body = list(body)[:_BODY_MAX]
        elif targets is not None:
            self._body = _body_from_targets(targets, extra=extra_clause)
        else:
            self._body = []

        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        outer = QHBoxLayout(self)
        # The accent rail takes the leftmost 6 px; the document
        # content starts 18 px in so it breathes from the rail.
        outer.setContentsMargins(self.ACCENT_STRIP_W + 18, 18, 20, 18)
        outer.setSpacing(0)

        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        eyebrow = QLabel("CONTINUE")
        ef = QFont()
        ef.setPointSizeF(7.5)
        ef.setBold(True)
        eyebrow.setFont(ef)
        eyebrow.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"letter-spacing: 1.4px;"
        )
        col.addWidget(eyebrow)

        col.addSpacing(8)

        title_lbl = _EliderLabel(title)
        tf = QFont()
        tf.setPointSizeF(14.5)
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
            f"letter-spacing: -0.2px;"
        )
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        col.addWidget(title_lbl)

        col.addSpacing(14)

        # Body bullets — one per line, calm leading dot, no chips.
        for line in self._body:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)

            dot = QLabel()
            dot.setFixedSize(5, 5)
            dot.setStyleSheet(
                f"background: {T.ACCENT}; border-radius: 2px;"
            )
            row.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

            text = QLabel(line)
            bf = QFont()
            bf.setPointSizeF(10.5)
            text.setFont(bf)
            text.setStyleSheet(
                f"color: {T.INK_2}; background: transparent;"
            )
            row.addWidget(text, 1, Qt.AlignmentFlag.AlignVCenter)

            wrap = QWidget()
            wrap.setLayout(row)
            wrap.setFixedHeight(20)
            col.addWidget(wrap)

        col.addStretch(1)

        # Resume row — right-aligned, sits at the bottom-right.
        resume_row = QHBoxLayout()
        resume_row.setContentsMargins(0, 0, 0, 0)
        resume_row.setSpacing(0)
        resume_row.addStretch(1)
        resume_row.addWidget(_ResumeButton())
        col.addLayout(resume_row)

        outer.addLayout(col, 1)

    # ── paint ──

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 1. Document body — soft warm-paper tint inside the
        # white workspace so the card reads as a document.
        body = QPainterPath()
        body.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        p.fillPath(body, QColor("#FBF8F2"))
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        else:
            pen = QPen(QColor(T.BORDER_RAISED))
            pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(body)
        # 2. Accent rail — clipped to the rounded body so the
        # corners match.
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        p.setClipPath(clip)
        rail = QPainterPath()
        rail.addRect(QRectF(0, 0, self.ACCENT_STRIP_W, self.height()))
        p.fillPath(rail, QColor(T.ACCENT))
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


__all__ = ["RecoveryCardV3"]
