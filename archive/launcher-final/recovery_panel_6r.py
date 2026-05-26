"""Phase 6R — Launcher Finalization · hero card.

A single dense row. Title (one line, truncated) + up to **three
chips** + a tiny **HIGH** confidence badge + a fixed-width 112-px
**Resume** button. Nothing else.

  +-----------------------------------------------------------+
  |  | WebSocket retry debugging                       HIGH  |
  |  |  2 files   2 tabs   1 search          [ Resume   1 ]  |
  +-----------------------------------------------------------+
        |__ 6-px accent strip

Removed from the prior 6Q surface (kept here only as reference):

  - the *Why this?* link + signals parameter
  - the long meta caption ("2 tabs · 2 files · reopened after a
    2-day gap · last active during implementation")
  - the elided multi-word subtitle
  - any prose row beneath the title

Pre-6R variants live at `archive/launcher-debt/`.
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
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


_CHIP_MAX = 3            # directive: chips max 3
_RESUME_WIDTH = 112      # directive: Resume fixed width 112


# ── elider label ─────────────────────────────────────────────────


class _EliderLabel(QLabel):
    """A `QLabel` that paints `…` when its text can't fit. The hero
    title is rendered through this so a long investigation name
    degrades gracefully inside the 680-px window."""

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


# ── tiny HIGH badge ──────────────────────────────────────────────


class _ConfidenceBadge(QLabel):
    """A 38×16 pill carrying the word `HIGH`. Tiny by design — the
    launcher only ever surfaces HIGH heroes (the 6O HIGH-only
    gate), so the badge is confirmation, not selection."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("HIGH", parent)
        self.setFixedSize(38, 16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSizeF(7.5)
        f.setBold(True)
        self.setFont(f)
        self.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.ACCENT};"
            f"  background: {T.ACCENT_SOFT};"
            f"  border-radius: 8px;"
            f"  letter-spacing: 1.0px;"
            f"  padding: 0;"
            f"}}"
        )


# ── chip ─────────────────────────────────────────────────────────


class _Chip(QLabel):
    """A small calm pill: ink-3 text on a warm-paper fill, hairline
    border, radius 8. Used for the *2 files · 2 tabs · 1 search*
    evidence row underneath the title."""

    HEIGHT = 20

    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setFixedHeight(self.HEIGHT)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSizeF(7.8)
        f.setBold(True)
        self.setFont(f)
        self.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.INK_3};"
            f"  background: {T.BG};"
            f"  border: 1px solid {T.BORDER_RAISED};"
            f"  border-radius: 8px;"
            f"  padding: 0 8px;"
            f"  letter-spacing: 0.4px;"
            f"}}"
        )


# ── Resume button ────────────────────────────────────────────────


class _ResumeButton(QWidget):
    """Fixed-width 112-px accent-filled Resume. Trailing `1` chip is
    the keyboard shortcut hint. The single CTA shape — no variants."""

    HEIGHT = 32
    WIDTH = _RESUME_WIDTH

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setFixedWidth(self.WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        label = QLabel("Resume")
        f = QFont()
        f.setPointSizeF(10.0)
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


def _chips_from_targets(
    targets: List[Tuple[str, str]]
) -> List[str]:
    """Bucket the candidate's targets into chip labels. Same buckets
    `RecoveryEngine.plan_for` uses; reimplemented locally so the
    launcher doesn't take a network round trip just to render."""
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
    chips: list[str] = []
    if files:
        chips.append(f"{files} file{'s' if files != 1 else ''}")
    if tabs:
        chips.append(f"{tabs} tab{'s' if tabs != 1 else ''}")
    if chats:
        chips.append(f"{chats} chat{'s' if chats != 1 else ''}")
    if searches:
        chips.append(f"{searches} search{'es' if searches != 1 else ''}")
    return chips[:_CHIP_MAX]


class RecoveryCardV3(QWidget):
    """The frozen hero. Fixed 88-px height. Single dense row.

    Emits ``restore(candidate_id, title, n_targets)`` on Enter /
    Space / `1` / click. **No** `request_why` signal, **no**
    `signals` parameter — the prose surfaces moved out of the
    launcher in Phase 6R.
    """

    restore = pyqtSignal(str, str, int)

    HEIGHT = 88            # directive: hero max height 88
    ACCENT_STRIP_W = 6     # directive: left accent strip 6 px

    def __init__(
        self,
        candidate_id: str,
        title: str,
        *,
        chips: Optional[List[str]] = None,
        targets: Optional[List[Tuple[str, str]]] = None,
        n_targets: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._focused = False

        # Chips: caller may pass them explicitly, otherwise we
        # derive from `targets`. The cap is the directive's max 3.
        if chips is not None:
            self._chips = list(chips)[:_CHIP_MAX]
        elif targets is not None:
            self._chips = _chips_from_targets(targets)
        else:
            self._chips = []

        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_CARD_RADIUS)
        eff.setOffset(0, T.SHADOW_CARD_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_CARD_ALPHA))
        self.setGraphicsEffect(eff)

        # ── layout ──
        outer = QHBoxLayout(self)
        # Left padding clears the 6-px accent strip + a small inset.
        outer.setContentsMargins(self.ACCENT_STRIP_W + 12, 12, 14, 12)
        outer.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(8)

        # Title row: title + tiny confidence badge in the top-right.
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        title_lbl = _EliderLabel(title)
        tf = QFont()
        tf.setPointSizeF(13.5)
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
        )
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_lbl.setMinimumWidth(0)
        title_row.addWidget(title_lbl, 1)
        title_row.addWidget(_ConfidenceBadge(), 0, Qt.AlignmentFlag.AlignVCenter)

        text_col.addLayout(title_row)

        # Chips row — directive's *chips max 3*. Hidden entirely when
        # the candidate has no derivable chips so the row stays calm.
        if self._chips:
            chip_row = QHBoxLayout()
            chip_row.setContentsMargins(0, 0, 0, 0)
            chip_row.setSpacing(6)
            for label in self._chips:
                chip_row.addWidget(_Chip(label))
            chip_row.addStretch(1)
            text_col.addLayout(chip_row)

        outer.addLayout(text_col, 1)
        outer.addWidget(_ResumeButton(), 0, Qt.AlignmentFlag.AlignVCenter)

    # ── paint ──

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 18, 18)
        p.fillPath(path, QColor(T.BG_RAISED))
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        else:
            pen = QPen(QColor(T.BORDER_RAISED))
            pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        # Accent left strip — clipped to the card's rounded path so
        # the top + bottom corners follow the same curve.
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), 18, 18)
        p.setClipPath(clip)
        strip = QPainterPath()
        strip.addRect(QRectF(0, 0, self.ACCENT_STRIP_W, self.height()))
        p.fillPath(strip, QColor(T.ACCENT))
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
