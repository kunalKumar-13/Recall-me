"""Phase 6O — Launcher Reset.

A single fixed-shape recovery hero. Nothing else.

The pre-reset module shipped three signal variants
(HIGH/MED/LOW), accent paint per variant, a confidence
sentence row, an evidence-chip parser with up to three chips,
and a top-right confidence badge. The reset directive deletes
all of it.

What stays:

  - One card. 100 px tall. Fixed.
  - Title (left, FS_HERO=20, bold)
  - One ambient meta line under the title — *"N tabs · M files · returned after Xd"*
  - Resume button (right, FS_META=12, accent fill, `1` shortcut chip)

The card only ever renders when the engine produced a HIGH-
confidence recovery; the launcher's state machine in
``minimal.py`` gates it. No `signal` parameter is exposed because
no other state surfaces here.

The pre-reset module + capture scripts live at
``archive/launcher-overbuild/`` with an explanation.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


# ── elider label ─────────────────────────────────────────────────


class _EliderLabel(QLabel):
    """A `QLabel` that elides its text with `…` when its width can't
    fit the full string. Standard `QLabel` truncates abruptly; this
    subclass paints `…` so a long recovery title degrades gracefully
    inside the 680-px window."""

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
        from PyQt6.QtCore import Qt as _Qt
        from PyQt6.QtGui import QFontMetrics
        if not self._full_text:
            return
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(
            self._full_text, _Qt.TextElideMode.ElideRight,
            max(0, self.width() - 4),
        )
        if elided != super().text():
            QLabel.setText(self, elided)


# ── Why-this link ────────────────────────────────────────────────


class _WhyLink(QLabel):
    """Tiny *Why this?* link rendered to the right of the meta row.

    Phase 6Q: clicking emits `activated(candidate_id, signals)`. The
    host launcher opens a `WhyThisSheet` overlay with the pure
    engine signals. No prose, no AI text."""

    activated = pyqtSignal(str, list)

    def __init__(
        self,
        candidate_id: str,
        signals: list,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Why this?", parent)
        self._cid = candidate_id
        self._signals = list(signals)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.ACCENT};"
            f"  background: transparent;"
            f"  font-size: {T.FS_META}px;"
            f"  font-weight: 600;"
            f"  padding: 0;"
            f"}}"
            f"QLabel:hover {{ text-decoration: underline; }}"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.activated.emit(self._cid, self._signals)
            e.accept()
            return
        super().mouseReleaseEvent(e)


# ── Resume button ────────────────────────────────────────────────


class _ResumeButton(QWidget):
    """A single Resume button. Accent-filled, fixed-width (110 px,
    per the 6P.1 directive: *Resume button: filled, right aligned,
    fixed width: 110*), with the `1` shortcut chip on the right
    edge. Same surface no matter the recovery — the directive's
    reset rule: there is only one CTA shape."""

    HEIGHT = 36
    WIDTH = 110

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
        label.setStyleSheet(
            "color: white; background: transparent; padding: 0;"
        )
        layout.addWidget(label, 1)

        chip = QLabel("1")
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setFixedSize(20, 20)
        chip.setStyleSheet(
            "QLabel {"
            "  background: rgba(255, 255, 255, 0.20);"
            "  color: white;"
            "  border-radius: 6px;"
            "  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            "  font-size: 11px;"
            "  font-weight: 600;"
            "}"
        )
        layout.addWidget(chip, 0)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        p.fillPath(path, QColor(T.ACCENT))
        p.end()


# ── card ─────────────────────────────────────────────────────────


class RecoveryCardV3(QWidget):
    """The single recovery hero. Fixed 100 px height. Title (left,
    bold) + one ambient meta line + Resume button (right). Nothing
    else.

    Emits ``restore(candidate_id, title, n_targets)`` on Enter /
    Space / `1` / click. Emits ``request_why(candidate_id, signals)``
    when the *Why this?* link is clicked.
    """

    restore = pyqtSignal(str, str, int)
    request_why = pyqtSignal(str, list)

    HEIGHT = 100

    def __init__(
        self,
        candidate_id: str,
        title: str,
        meta: str,
        *,
        n_targets: int = 0,
        signals: Optional[List[str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._signals: List[str] = list(signals or [])
        self._hover = False
        self._focused = False

        # The directive's *No dynamic growth* rule — `setFixedHeight`
        # not `setMinimumHeight`. The card never reflows.
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # 6P.1: stronger drop so the card reads as layered against
        # the warm page (`#F3F1ED`). Directive: 0 12 32 rgba(0,0,0,.08).
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_CARD_RADIUS)
        eff.setOffset(0, T.SHADOW_CARD_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_CARD_ALPHA))
        self.setGraphicsEffect(eff)

        # Layout — title + meta on the left, Resume on the right.
        # 6P.1 directive: padding 20. The left padding is bumped to
        # 24 so the title clears the 4-px accent strip.
        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 20, 20, 20)
        outer.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(6)
        text_col.addStretch(1)

        # Title sits in a constrained-width column (the card is
        # 680-px-minus-padding minus the Resume pill). Two
        # safeguards: drop a few points so the directive's `20` reads
        # as visually-weighted without overflowing on long titles
        # like "WebSocket retry debugging", and the `_EliderLabel`
        # below elides with `…` if the text still doesn't fit.
        title_lbl = _EliderLabel(title)
        tf = QFont()
        tf.setPointSizeF(T.FS_HERO - 4)     # 16 — fits the column
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
        )
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_lbl.setMinimumWidth(0)
        text_col.addWidget(title_lbl)

        # Phase 6Q — meta row gains a *Why this?* link on the right.
        # Click opens a tiny sheet that lists the engine's signals.
        # The link is hidden when no signals are available so the
        # row stays calm for thin fixtures (demo, headless smoke).
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(8)

        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"font-size: {T.FS_META}px;"   # 12
        )
        meta_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        meta_row.addWidget(meta_lbl, 1)

        if self._signals:
            why = _WhyLink(self._cid, self._signals)
            why.activated.connect(self.request_why.emit)
            meta_row.addWidget(why, 0)

        text_col.addLayout(meta_row)
        text_col.addStretch(1)

        outer.addLayout(text_col, 1)
        outer.addWidget(_ResumeButton(), 0, Qt.AlignmentFlag.AlignVCenter)

    # ── paint ──

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # 6P.1 — hero radius drops to 22 so the card reads as a
        # solid object instead of a pill. Directive: `radius: 22`.
        path.addRoundedRect(QRectF(self.rect()), 22, 22)
        # 6P.1 — pure white fill (no accent tint). The card now
        # carries weight through layering + the accent left strip,
        # not through a coloured wash.
        p.fillPath(path, QColor(T.BG_RAISED))
        # 6P.1 — solid warm-grey hairline border; lavender on focus.
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        else:
            pen = QPen(QColor(T.BORDER_RAISED))
            pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        # 6P.1 directive: *soft left accent strip · 4px · lavender*.
        # Painted inside the rounded border so it tucks behind the
        # card edge rather than poking past it.
        strip_w = 4
        strip = QPainterPath()
        # Clip the strip to the card's rounded rect so the top/
        # bottom corners follow the same curve.
        clip_path = QPainterPath()
        clip_path.addRoundedRect(QRectF(self.rect()), 22, 22)
        strip.addRect(QRectF(1, 1, strip_w, self.height() - 2))
        p.setClipPath(clip_path)
        p.fillPath(strip, QColor(T.ACCENT))
        p.end()

    # ── interaction ──

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

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
