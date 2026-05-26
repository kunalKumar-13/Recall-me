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

# Phase 6B bumps the hover lift slightly (3 → 4 px max, per the
# directive's "hover lift: 4 px max" line for the Resume pill /
# floating-card feel). Still inside the calm band.
HOVER_LIFT_PX = 3.0

# Phase 6B — the accent rail and status dots retuned for the warm-
# white surface. The lavender (#8b7fe3) matches the new `ACCENT`
# token in styles.py; status dots stay close to their prior hues
# but with slightly higher saturation so they read on white.
_ACCENT_RAIL = "rgba(139, 127, 227, 0.88)"
_OK = "#4fa784"     # matches the extension's --ok
_WARN = "#c98a5e"   # matches the extension's --warn


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
            # Phase 6B — hover fill is a faint accent-tinted lavender
            # on warm white. BG_HOVER (warm beige) reads as a flash
            # on the new light theme; a low-alpha accent reads as a
            # gentle highlight instead. Same paced timing.
            fill = QColor(ACCENT)
            fill.setAlphaF(0.10 * self._hover)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(fill)
            p.drawRoundedRect(rect, 12, 12)

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


class _EvidenceChip(QWidget):
    """Phase 6B — a small soft pill for one preview chip (e.g.
    *"2 tabs"*, *"3 files"*, *"2d gap"*). Replaces the prior
    middle-dot-separated evidence text for `RecoveryCard`.

    No outline; soft accent-tinted fill (or neutral for the gap
    chip). The split into separate widgets is the directive's
    "Use chips" line — *Instead of: '2 tabs · 3 files · after 2
    days' / Use chips: [2 tabs] [3 files] [2d gap]*.
    """

    HEIGHT = 18

    def __init__(self, label: str, *, kind: str = "count") -> None:
        super().__init__()
        self._label = label
        # *count* chips (tabs / files / chats) use the accent tint;
        # *time* chips (the gap "2d gap") use the neutral surface.
        if kind == "time":
            self._fg = QColor(TEXT_DIM)
            self._bg_alpha = 0.55
            self._bg = QColor("#f4efea")   # BG_HOVER (warm beige)
        else:
            self._fg = QColor(ACCENT)
            self._bg_alpha = 1.0
            self._bg = QColor("#ede9fb")   # ACCENT_DIM (soft accent)
        f = self.font()
        f.setPointSizeF(7.8)
        fm = QFontMetrics(f)
        self._w = fm.horizontalAdvance(label) + 14
        self.setFixedSize(self._w, self.HEIGHT)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(self._bg)
        bg.setAlphaF(self._bg_alpha)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0, 0, self._w, self.HEIGHT), 6, 6)
        f = self.font()
        f.setPointSizeF(7.8)
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        p.setPen(QPen(self._fg))
        p.drawText(
            QRectF(0, 0, self._w, self.HEIGHT),
            Qt.AlignmentFlag.AlignCenter,
            self._label,
        )
        p.end()


def _middle_with_chips(
    title: str,
    chips: list[tuple[str, str]],
    *,
    title_limit: int = 42,
) -> QWidget:
    """Phase 6B — like `_middle`, but the evidence row is a horizontal
    layout of small soft pills instead of one dim text line.

    `chips` is a list of `(label, kind)` tuples; `kind` is "count"
    (accent pill) or "time" (neutral pill).
    """
    w = QWidget()
    col = QVBoxLayout(w)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(4)
    col.addWidget(_text(_elide(title, title_limit), size=9.5,
                        color=TEXT, weight=600))
    if chips:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)
        for label, kind in chips[:4]:
            row.addWidget(_EvidenceChip(label, kind=kind))
        row.addStretch(1)
        col.addLayout(row)
    return w


def _parse_evidence_chips(evidence: str) -> list[tuple[str, str]]:
    """Phase 6B — split the engine's deterministic preview caption
    (e.g. *"2 tabs · 3 files · reopened after a 2-day gap"*) into
    `(label, kind)` chip tuples. Tokens containing *day(s) gap*,
    *ago*, *return*, *reopened* are *time* chips; everything else
    is a *count* chip. Pure parsing — never invents data.
    """
    parts = [seg.strip() for seg in (evidence or "").split("·") if seg.strip()]
    out: list[tuple[str, str]] = []
    for p in parts:
        low = p.lower()
        if any(k in low for k in ("gap", "ago", "return", "reopened", "day")):
            # Compact the time chip to "Nd gap" / "Nh ago" shape.
            short = (
                p.replace("reopened after a ", "")
                .replace("reopened after ", "")
                .replace("returned after ", "")
                .replace("-day gap", "d gap")
                .replace(" day gap", "d gap")
                .replace(" days gap", "d gap")
                .replace(" hours ago", "h ago")
                .replace(" minutes ago", "m ago")
                .strip()
            )
            out.append((short, "time"))
        else:
            out.append((p, "count"))
    return out


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


def _meta_with_confidence(
    top: str, confidence: str, bottom: Optional[QWidget]
) -> QWidget:
    """Phase 6A — like `_meta`, but the time line is followed by a
    small *confidence badge* before the bottom widget. Used by the
    `RecoveryCard` so the user reads the trust band next to the
    Resume affordance.
    """
    w = QWidget()
    col = QVBoxLayout(w)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(2)
    col.setAlignment(Qt.AlignmentFlag.AlignRight)
    t = _text(top, size=7.8, color=TEXT_DIMMER)
    t.setAlignment(Qt.AlignmentFlag.AlignRight)
    col.addWidget(t, 0, Qt.AlignmentFlag.AlignRight)
    col.addWidget(_ConfidenceBadge(confidence), 0, Qt.AlignmentFlag.AlignRight)
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


class _ConfidenceBadge(QWidget):
    """Phase 6A — a small pill next to the title that names the
    recovery's confidence band: *high* (lavender), *medium* (amber),
    *low* (muted gray).

    The level is **derived** at the launcher's call site from
    existing candidate data — no engine-side confidence field. The
    badge is *display only*; nothing here computes trust.
    """

    HEIGHT = 14

    # One color per level. *high* uses the accent lavender so the
    # badge reads as "act on this"; *medium* uses the warn amber;
    # *low* uses the dimmed text grey so the user reads it as a hint,
    # not a recommendation.
    _COLOR = {
        "high": ACCENT,
        "medium": _WARN,
        "low": TEXT_DIMMER,
    }
    _LABEL = {
        "high": "high",
        "medium": "med",
        "low": "low",
    }

    def __init__(self, level: str) -> None:
        super().__init__()
        self._level = level if level in self._COLOR else "high"
        f = self.font()
        f.setPointSizeF(7.6)
        fm = QFontMetrics(f)
        self._w = fm.horizontalAdvance(self._LABEL[self._level]) + 14
        self.setFixedSize(self._w, self.HEIGHT)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self._COLOR[self._level])
        bg = QColor(color)
        bg.setAlphaF(0.16)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0, 0, self._w, self.HEIGHT), 4, 4)
        f = self.font()
        f.setPointSizeF(7.6)
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        p.setPen(QPen(color))
        p.drawText(
            QRectF(0, 0, self._w, self.HEIGHT),
            Qt.AlignmentFlag.AlignCenter,
            self._LABEL[self._level],
        )
        p.end()


def derive_recovery_confidence(n_targets: int) -> str:
    """UI-side mapping from candidate target count to a confidence
    band. Pure display logic — no engine-side score is computed
    here; this is the *displayed* read of an existing signal.

      - >= 4 targets: high (a real multi-surface investigation)
      - 2-3 targets:  medium (a partial but plausible thread)
      - 0-1 targets:  low (a hint, not a recommendation)
    """
    if n_targets >= 4:
        return "high"
    if n_targets >= 2:
        return "medium"
    return "low"


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
    over 220ms the first time the card is shown.

    Phase 6A: an inline *confidence* badge in the meta column above
    the time label. Levels are *high* / *medium* / *low* and are
    derived UI-side from the candidate's target count (see
    `derive_recovery_confidence`) — no engine-side trust field.
    The *low* band keeps the calmer `_StateDot` variant; *medium*
    and *high* both render the full Resume pill because the user
    has enough evidence to act.
    """

    # Phase 6A bumps this from 64 to 76 to fit the new
    # *confidence badge* between the time label and the Resume
    # pill in the meta column. Still inside the launcher's calm
    # row band; the digest does not need to scroll because of it.
    RECOVERY_HEIGHT = 76

    restore = pyqtSignal(str, str, int)

    def __init__(
        self,
        candidate_id: str,
        title: str,
        evidence: str,
        time_label: str,
        *,
        confidence: str = "high",
        n_targets: int = 0,
    ) -> None:
        super().__init__(height=self.RECOVERY_HEIGHT)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._confidence = confidence if confidence in _ConfidenceBadge._COLOR else "high"

        chip = _GlyphChip("recovery", ACCENT)
        # The Resume pill replaces the tiny _StateDot label for
        # high/medium recoveries; low-confidence recoveries keep the
        # quieter state-dot - a Resume CTA on a hedged surface would
        # over-promise.
        right: QWidget
        if self._confidence == "low":
            self._pill = None
            right = _StateDot(ACCENT, "Resume")
        else:
            self._pill = _ResumePill()
            right = self._pill
        meta = _meta_with_confidence(time_label, self._confidence, right)
        # Phase 6B - the evidence string is split into chip widgets
        # so the row reads as `[2 tabs] [3 files] [2d gap]` rather
        # than the prior dim text line. The split is pure parsing on
        # `·`; if evidence is empty (a rare degenerate candidate)
        # the chip row is dropped.
        chips = _parse_evidence_chips(evidence)
        if chips:
            self.compose(chip, _middle_with_chips(title, chips), meta)
        else:
            self.compose(chip, _middle(title, evidence), meta)

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
    copy stays canonical.

    Phase 6B grew an optional *Show example* button on the EMPTY
    variant; Phase 6D pairs it with a quieter *Start normally*
    secondary action so a user who'd rather wait for real data can
    decline the demo cleanly. Both buttons fire dedicated signals
    (`show_example` / `start_normally`); the live launcher owns the
    actual demo-mode wiring, so this widget remains engine-free.
    """

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    def __init__(
        self,
        glyph: str,
        tint: str,
        title: str,
        body: str,
        *,
        height: int = 132,
        show_example_button: bool = False,
    ) -> None:
        super().__init__(interactive=False, height=height)
        wrap = QVBoxLayout(self)
        # Phase 6B - generous outer padding (24) per the directive's
        # spacing rhythm; the empty surface should breathe.
        wrap.setContentsMargins(28, 24, 28, 22)
        wrap.setSpacing(10)
        wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chip = _GlyphChip(glyph, QColor(tint).name())
        chip_row = QHBoxLayout()
        chip_row.addStretch(1)
        chip_row.addWidget(chip)
        chip_row.addStretch(1)
        wrap.addLayout(chip_row)

        t = _text(title, size=11, color=TEXT, weight=600)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrap.addWidget(t)

        b = _text(body, size=9, color=TEXT_DIM)
        b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b.setWordWrap(True)
        wrap.addWidget(b)

        if show_example_button:
            from PyQt6.QtWidgets import QPushButton
            primary = QPushButton("Show example")
            primary.setObjectName("example_button")
            primary.setCursor(Qt.CursorShape.PointingHandCursor)
            primary.setFixedHeight(34)
            primary.clicked.connect(self.show_example.emit)

            # Phase 6D — the *Start normally* secondary action.
            # Same height, transparent fill (styled by the new
            # QSS `secondary_button` id) — a quiet decline that
            # never reads louder than the primary.
            secondary = QPushButton("Start normally")
            secondary.setObjectName("secondary_button")
            secondary.setCursor(Qt.CursorShape.PointingHandCursor)
            secondary.setFixedHeight(34)
            secondary.clicked.connect(self.start_normally.emit)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(8)
            btn_row.addStretch(1)
            btn_row.addWidget(primary)
            btn_row.addWidget(secondary)
            btn_row.addStretch(1)
            wrap.addSpacing(4)
            wrap.addLayout(btn_row)

    @classmethod
    def empty(cls) -> "EmptyCard":
        # Phase 6B - the launcher's identity surface. Headline says
        # *what Recall does* in five words; body says *what the user
        # does* in three short clauses. The Show example button is
        # the only first-run CTA on the whole surface.
        return cls(
            "spark", ACCENT,
            "Recall notices unfinished work.",
            "Work normally.  Return later.\n"
            "Recall fills itself.",
            height=210,
            show_example_button=True,
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
    "derive_recovery_confidence",
]
