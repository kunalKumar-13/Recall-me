"""Launcher cards — Phase 4K.

The launcher's idle digest is built from one consistent card. Every
surface — recovery, investigations, resurfacing, trust — is the same
48–56px row with the same three zones:

    ┌──────────────────────────────────────────────────────────┐
    │  ▣   Title line                                  2d ago   │
    │      behavior evidence / preview                Resume →  │
    └──────────────────────────────────────────────────────────┘
      ↑   ↑                                            ↑
    icon  middle: title + evidence                  right: meta
    chip                                            (time, state)

Plus the non-row cards: `EmptyCard` (calm full states — empty,
offline, first-week) and `SkeletonCard` (the loading placeholder).

Design rules, enforced here so they don't drift:

  • One row height band — 48–56px. `CARD_HEIGHT` is 54.
  • Hover is *paced* — a 120ms fade, never an instant flash
    (MOTION.md: 100–140ms hover).
  • Cards are keyboard-reachable: `StrongFocus`, a painted focus
    ring, Enter/Return activates.
  • No number is ever shown as a score. The "confidence indicator"
    is a single quiet dot — present or absent, never a percentage.

Vocabulary follows CONTINUITY_LANGUAGE.md: an *investigation* is the
user-facing name for a thread.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QVariantAnimation,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .styles import (
    ACCENT,
    BG_HOVER,
    MOTION_FAST_MS,
    MOTION_NORMAL_MS,
    MOTION_SLOW_MS,
    TEXT,
    TEXT_DIM,
    TEXT_DIMMER,
)

# Phase 5I bumps the row band to 58 (the 56–64 brief). One height for
# every digest card so the surface reads as evenly-rhythmed zones, not
# a list of irregular widgets.
CARD_HEIGHT = 58

# A small translation on hover (2–3 px lift, per the Phase 5I brief).
HOVER_LIFT_PX = 2.0

_ACCENT_RAIL = "rgba(139, 155, 255, 0.85)"
_OK = "#5fcf9e"
_WARN = "#d6a06a"


# --------------------------------------------------------------- glyphs


def _paint_glyph(p: QPainter, kind: str, x: float, y: float, s: float,
                 color: QColor) -> None:
    """Paint one small stroked glyph inside an `s`×`s` box at (x, y).

    Deliberately primitive — a few strokes each, no icon font, no
    SVG asset. The glyph names a surface; it never decorates.
    """
    pen = QPen(color)
    pen.setWidthF(1.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    cx, cy = x + s / 2, y + s / 2

    if kind == "recovery":
        # A resume triangle inside a soft arc.
        path = QPainterPath()
        path.moveTo(cx - s * 0.16, cy - s * 0.22)
        path.lineTo(cx + s * 0.24, cy)
        path.lineTo(cx - s * 0.16, cy + s * 0.22)
        path.closeSubpath()
        p.fillPath(path, color)
    elif kind == "investigation":
        # Two nodes joined by a path — a thread of work.
        p.drawEllipse(QRectF(x + s * 0.10, y + s * 0.16, s * 0.22, s * 0.22))
        p.drawEllipse(QRectF(x + s * 0.62, y + s * 0.58, s * 0.22, s * 0.22))
        path = QPainterPath()
        path.moveTo(x + s * 0.30, y + s * 0.30)
        path.cubicTo(
            x + s * 0.62, y + s * 0.30,
            x + s * 0.40, y + s * 0.66,
            x + s * 0.64, y + s * 0.66,
        )
        p.drawPath(path)
    elif kind == "resurface":
        # A quiet ring — noticed, not urgent.
        p.drawEllipse(QRectF(x + s * 0.20, y + s * 0.20, s * 0.60, s * 0.60))
        p.fillRect(QRectF(cx - 1, cy - 1, 2.2, 2.2), color)
    elif kind == "trust":
        # A small padlock.
        p.drawRoundedRect(
            QRectF(x + s * 0.26, y + s * 0.44, s * 0.48, s * 0.34), 2, 2
        )
        arc = QPainterPath()
        arc.moveTo(x + s * 0.36, y + s * 0.44)
        arc.lineTo(x + s * 0.36, y + s * 0.34)
        arc.cubicTo(
            x + s * 0.36, y + s * 0.18,
            x + s * 0.64, y + s * 0.18,
            x + s * 0.64, y + s * 0.34,
        )
        arc.lineTo(x + s * 0.64, y + s * 0.44)
        p.drawPath(arc)
    elif kind == "spark":
        # A four-point — the calm "ready / nothing yet" mark.
        for dx, dy in ((0, -0.30), (0, 0.30), (-0.30, 0), (0.30, 0)):
            p.drawLine(
                int(cx), int(cy),
                int(cx + dx * s), int(cy + dy * s),
            )


class _GlyphChip(QWidget):
    """The fixed left zone — a 30×30 rounded chip holding one glyph."""

    SIZE = 30

    def __init__(self, kind: str, tint: str = ACCENT) -> None:
        super().__init__()
        self._kind = kind
        self._tint = QColor(tint)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(self._tint)
        bg.setAlpha(28)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0, 0, self.SIZE, self.SIZE), 9, 9)
        if self._kind:
            _paint_glyph(p, self._kind, 6, 6, self.SIZE - 12, self._tint)
        p.end()


# --------------------------------------------------------------- base


class CardBase(QWidget):
    """Shared chrome for every digest row: the paced-hover fill, the
    keyboard focus ring, and the three-zone layout. Subclasses fill
    the zones; they never re-implement the chrome."""

    activated = pyqtSignal()

    def __init__(self, *, interactive: bool = True,
                 height: int = CARD_HEIGHT) -> None:
        super().__init__()
        self._interactive = interactive
        self._base_height = height
        self.setFixedHeight(height)
        self._hover = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(MOTION_FAST_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_hover_value)
        if interactive:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    # -- the three-zone layout ------------------------------------------

    def compose(
        self,
        chip: Optional[QWidget],
        middle: QWidget,
        right: Optional[QWidget],
    ) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 6, 14, 6)
        row.setSpacing(12)
        if chip is not None:
            row.addWidget(chip, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(middle, 1, Qt.AlignmentFlag.AlignVCenter)
        if right is not None:
            row.addWidget(right, 0, Qt.AlignmentFlag.AlignVCenter)

    # -- hover (paced) --------------------------------------------------

    def _on_hover_value(self, v: object) -> None:
        self._hover = float(v) if v is not None else 0.0
        self.update()

    def enterEvent(self, _event) -> None:  # type: ignore[override]
        if self._interactive:
            self._animate_hover(1.0)

    def leaveEvent(self, _event) -> None:  # type: ignore[override]
        if self._interactive:
            self._animate_hover(0.0)

    def _animate_hover(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(target)
        self._anim.start()

    # -- activation (mouse + keyboard) ----------------------------------

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if (
            self._interactive
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.activated.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if (
            self._interactive
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                                 Qt.Key.Key_Space)
        ):
            self.activated.emit()
            return
        super().keyPressEvent(event)

    # -- paint: hover fill + lift + focus ring --------------------------

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Hover lift — the rect drifts up 0–HOVER_LIFT_PX with the
        # paced hover value, so the card visibly elevates without
        # bouncing. Per the Phase 5I rule: 2–3 px only, no spring.
        lift = HOVER_LIFT_PX * self._hover
        rect = QRectF(
            1,
            1 - lift,
            self.width() - 2,
            self.height() - 2,
        )

        if self._hover > 0.001:
            fill = QColor(BG_HOVER)
            fill.setAlphaF(0.55 * self._hover)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(fill)
            p.drawRoundedRect(rect, 9, 9)

        if self.hasFocus():
            # Lavender focus ring — the only colour state on a card.
            # Slightly thicker than the at-rest hover so a keyboard
            # user always sees where they are.
            ring = QColor(ACCENT)
            ring.setAlphaF(0.92)
            pen = QPen(ring)
            pen.setWidthF(1.6)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect, 9, 9)
        p.end()


# --------------------------------------------------------------- helpers


def _text(s: str, *, size: float, color: str, weight: int = 400) -> QLabel:
    lbl = QLabel(s)
    lbl.setTextFormat(Qt.TextFormat.PlainText)
    f = lbl.font()
    f.setPointSizeF(size)
    f.setWeight(QFont.Weight(weight))
    lbl.setFont(f)
    lbl.setStyleSheet(f"color:{color};background:transparent;")
    return lbl


def _elide(s: str, limit: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def _middle(title: str, evidence: str, *, title_limit: int = 42) -> QWidget:
    """The shared middle zone — a title line and a dim evidence line."""
    w = QWidget()
    col = QVBoxLayout(w)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(2)
    col.addWidget(_text(_elide(title, title_limit), size=9.5,
                        color=TEXT, weight=600))
    if evidence:
        col.addWidget(_text(_elide(evidence, 56), size=8, color=TEXT_DIM))
    return w


def _meta(top: str, bottom: Optional[QWidget]) -> QWidget:
    """The shared right zone — a time line over a state affordance."""
    w = QWidget()
    col = QVBoxLayout(w)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(3)
    col.setAlignment(Qt.AlignmentFlag.AlignRight)
    t = _text(top, size=7.8, color=TEXT_DIMMER)
    t.setAlignment(Qt.AlignmentFlag.AlignRight)
    col.addWidget(t)
    if bottom is not None:
        col.addWidget(bottom, 0, Qt.AlignmentFlag.AlignRight)
    return w


class _StateDot(QWidget):
    """A single quiet dot — the only 'indicator' a card ever shows.
    Presence means 'high-trust'; it is never a number or a bar."""

    def __init__(self, color: str, label: str = "") -> None:
        super().__init__()
        self._color = QColor(color)
        self._label = label
        fm = QFontMetrics(self.font())
        self.setFixedSize(10 + (fm.horizontalAdvance(label) + 5 if label else 0), 12)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._color)
        p.drawEllipse(QRectF(2, 3, 6, 6))
        if self._label:
            pen = QPen(QColor(TEXT_DIMMER))
            p.setPen(pen)
            f = self.font()
            f.setPointSizeF(7.6)
            p.setFont(f)
            p.drawText(13, 10, self._label)
        p.end()


# --------------------------------------------------------------- cards


class _ResumePill(QWidget):
    """A small lavender pill on the right of a RecoveryCard. Renders as
    'Resume →' with a soft accent fill. Owns its own opacity + x-offset
    so the recovery card's entrance animation can slide it in from the
    right without affecting layout.
    """

    PILL_W = 76
    PILL_H = 22

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(self.PILL_W, self.PILL_H)
        self._x_offset = 0.0
        # An opacity effect lets us fade the pill without re-painting
        # the rest of the card.
        self._fx = QGraphicsOpacityEffect(self)
        self._fx.setOpacity(1.0)
        self.setGraphicsEffect(self._fx)

    @pyqtProperty(float)
    def xOffset(self) -> float:  # noqa: N802 - Qt property naming
        return self._x_offset

    @xOffset.setter
    def xOffset(self, value: float) -> None:  # noqa: N802
        self._x_offset = float(value)
        self.update()

    def setOpacity(self, value: float) -> None:
        self._fx.setOpacity(max(0.0, min(1.0, float(value))))

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(
            self._x_offset,
            0,
            self.PILL_W,
            self.PILL_H,
        )
        # Soft accent fill, no border.
        fill = QColor(ACCENT)
        fill.setAlphaF(0.18)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill)
        p.drawRoundedRect(rect, 7, 7)
        # Label.
        pen = QPen(QColor(ACCENT))
        p.setPen(pen)
        f = self.font()
        f.setPointSizeF(8.4)
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Resume  →")
        p.end()


class RecoveryCard(CardBase):
    """The strongest interrupted investigation — the digest's lead.

    Emits `restore(candidate_id, title, n_targets)` on activation
    (click, Enter, or Space).

    Phase 5I: a slightly taller row (top of the 56–64 band so it
    visually anchors the digest), a real *Resume* pill on the right,
    and an entrance animation that slides the pill in from the right
    over 220ms the first time the card is shown. The animation runs
    once per construction; if a card is hidden and re-shown (popup
    closed + reopened) the launcher constructs a fresh card.
    """

    RECOVERY_HEIGHT = 64

    restore = pyqtSignal(str, str, int)

    def __init__(
        self,
        candidate_id: str,
        title: str,
        evidence: str,
        time_label: str,
        *,
        high_trust: bool = True,
        n_targets: int = 0,
    ) -> None:
        super().__init__(height=self.RECOVERY_HEIGHT)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets

        chip = _GlyphChip("recovery", ACCENT)
        # The Resume pill replaces the tiny _StateDot label. For
        # low-trust recoveries we keep the calmer state-dot variant -
        # a Resume CTA on a hedged surface would over-promise.
        right: QWidget
        if high_trust:
            self._pill = _ResumePill()
            right = self._pill
        else:
            self._pill = None
            right = _StateDot(ACCENT, "Resume")
        self.compose(chip, _middle(title, evidence), _meta(time_label, right))

        # Recovery's quiet left signature — a thin lavender rail.
        self.activated.connect(
            lambda: self.restore.emit(self._cid, self._title, self._n)
        )
        # Animations are deferred to the first showEvent so they don't
        # play while the card is still off-screen.
        self._entrance_done = False
        self._pill_slide: QPropertyAnimation | None = None
        self._pill_fade: QVariantAnimation | None = None

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        if self._entrance_done or self._pill is None:
            return
        self._entrance_done = True
        # Slide the pill in from +20 px and fade in. Slow band (220ms)
        # per the Phase 5I "recovery open: 220ms" rule. No bounce; the
        # easing is calm-out, same curve the rest of the launcher uses.
        self._pill.xOffset = 20.0
        self._pill.setOpacity(0.0)
        self._pill_slide = QPropertyAnimation(self._pill, b"xOffset", self)
        self._pill_slide.setDuration(MOTION_SLOW_MS)
        self._pill_slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pill_slide.setStartValue(20.0)
        self._pill_slide.setEndValue(0.0)
        self._pill_slide.start()
        self._pill_fade = QVariantAnimation(self)
        self._pill_fade.setDuration(MOTION_NORMAL_MS)
        self._pill_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pill_fade.setStartValue(0.0)
        self._pill_fade.setEndValue(1.0)
        self._pill_fade.valueChanged.connect(
            lambda v: self._pill.setOpacity(float(v) if v is not None else 1.0)
        )
        self._pill_fade.start()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        rail = QColor(_ACCENT_RAIL)
        p.setBrush(rail)
        p.drawRoundedRect(QRectF(3, 11, 2.4, self.height() - 22), 1, 1)
        p.end()


class InvestigationCard(CardBase):
    """One ongoing investigation (a thread). Emits
    `open_thread(thread_id, topic_key, title)`."""

    open_thread = pyqtSignal(str, str, str)

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        evidence: str,
        time_label: str,
    ) -> None:
        super().__init__()
        chip = _GlyphChip("investigation", QColor("#b5a8ff").name())
        self.compose(chip, _middle(title, evidence), _meta(time_label, None))
        self.activated.connect(
            lambda: self.open_thread.emit(thread_id, topic_key, title)
        )


class ResurfaceCard(CardBase):
    """A passive 'on your radar' reminder. Emits `open_target(kind, target)`."""

    open_target = pyqtSignal(str, str)

    def __init__(
        self,
        label: str,
        evidence: str,
        time_label: str,
        kind: str,
        target: str,
    ) -> None:
        super().__init__()
        chip = _GlyphChip("resurface", QColor(TEXT_DIM).name())
        self.compose(chip, _middle(label, evidence), _meta(time_label, None))
        self.activated.connect(
            lambda: self.open_target.emit(kind, target)
        )


class TrustCard(CardBase):
    """The local-only trust row. Non-interactive — it states facts."""

    def __init__(
        self,
        connected: bool,
        events_today: int,
        address: str = "127.0.0.1:4545",
    ) -> None:
        super().__init__(interactive=False)
        chip = _GlyphChip("trust", QColor(_OK if connected else _WARN).name())
        title = "Local only" if connected else "Recall isn't running"
        evidence = (
            f"{address}  ·  {events_today} events today"
            if connected
            else f"{address}  ·  capture continues in the background"
        )
        dot = _StateDot(_OK if connected else _WARN,
                        "live" if connected else "offline")
        self.compose(chip, _middle(title, evidence, title_limit=48),
                     _meta("", dot))


class SkeletonCard(CardBase):
    """The loading placeholder — chip + two bars, no text, no motion
    beyond the digest's own reveal. Shown while the daemon is read."""

    def __init__(self) -> None:
        super().__init__(interactive=False)
        # Empty zones; everything is painted.
        self.compose(QWidget(), QWidget(), None)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        bar = QColor(TEXT_DIMMER)
        bar.setAlpha(40)
        p.setBrush(bar)
        # chip placeholder
        p.drawRoundedRect(QRectF(12, (self.height() - 30) / 2, 30, 30), 9, 9)
        # two text-line placeholders
        p.drawRoundedRect(QRectF(54, 17, 168, 8), 4, 4)
        soft = QColor(TEXT_DIMMER)
        soft.setAlpha(24)
        p.setBrush(soft)
        p.drawRoundedRect(QRectF(54, 31, 104, 7), 3.5, 3.5)
        p.end()


class EmptyCard(CardBase):
    """A calm full-state card — empty, offline, or first-week. Not a
    row: it is taller, centered, and self-explaining. Construct via
    the `empty()` / `offline()` / `first_week()` classmethods so the
    copy stays canonical."""

    def __init__(self, glyph: str, tint: str, title: str, body: str) -> None:
        super().__init__(interactive=False, height=132)
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(28, 16, 28, 16)
        wrap.setSpacing(6)
        wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chip = _GlyphChip(glyph, QColor(tint).name())
        chip_row = QHBoxLayout()
        chip_row.addStretch(1)
        chip_row.addWidget(chip)
        chip_row.addStretch(1)
        wrap.addLayout(chip_row)

        t = _text(title, size=10, color=TEXT, weight=600)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrap.addWidget(t)

        b = _text(body, size=8.4, color=TEXT_DIM)
        b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b.setWordWrap(True)
        wrap.addWidget(b)

    @classmethod
    def empty(cls) -> "EmptyCard":
        return cls(
            "spark", ACCENT,
            "Recall is ready.",
            "Work a little, then come back later — the investigations "
            "you can step back into will appear here.",
        )

    @classmethod
    def offline(cls) -> "EmptyCard":
        return cls(
            "trust", _WARN,
            "Recall isn't running",
            "Capture continues in the background — your memory is safe. "
            "Open the desktop app to see it here.",
        )

    @classmethod
    def first_week(cls) -> "EmptyCard":
        return cls(
            "investigation", QColor("#b5a8ff").name(),
            "Continuity is building",
            "Recall gains investigations and recovery cards as you work. "
            "Install the browser extension to feed it more.",
        )


__all__ = [
    "CARD_HEIGHT",
    "CardBase",
    "RecoveryCard",
    "InvestigationCard",
    "ResurfaceCard",
    "TrustCard",
    "SkeletonCard",
    "EmptyCard",
]
