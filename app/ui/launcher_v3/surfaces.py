"""Phase 6I — the launcher v3 surface system.

Seven primitives:

    GlassCard       a translucent white rounded surface with a soft drop
    FloatingPanel   a card sized to its content with the soft drop
                    AND a max-width clamp (the *floating* feel)
    SoftDivider     a 1-px hairline with breathing room above/below
    Pill            a small radius-12 lozenge — used by chips
    ConfidenceBadge a Pill variant tinted by confidence band
    TimelineChip    a Pill variant carrying a mono-font HH:MM stamp
                    or short relative-time label (e.g. ``2d gap``)
    StatusDot       a 6-px round indicator used in the sidebar's
                    section header next to ``Active investigations``
                    (live count + green/yellow/red dot)

Every primitive is a small composable QWidget. No engine code; no
recovery-logic touches. The widgets accept content + visual props
and paint themselves.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from . import theme as T


# ── primitives ────────────────────────────────────────────────────


class GlassCard(QWidget):
    """Solid rounded surface with a single soft drop. *Phase 6M.1
    refinement*: the previous translucent-white paint is replaced by
    a fully opaque white fill so cards read as physical objects on
    the paper-white page. The class name is kept (downstream code
    still imports `GlassCard`) but the *glass* feel is gone —
    every card is now a `SolidCard` underneath.

    `alpha` is kept on the signature for backwards-compat; values
    below 255 are silently clamped to 255 to enforce the
    *no transparency* refinement rule.
    """

    def __init__(
        self,
        *,
        radius: int = T.RADIUS_CARD,
        alpha: int = T.SURFACE_ALPHA_MID,
        shadow: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._radius = radius
        # Phase 6M.1: clamp to 255. The directive forbids
        # translucency outright.
        self._alpha = 255
        if shadow:
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(T.SHADOW_SOFT_RADIUS)
            eff.setOffset(0, T.SHADOW_SOFT_OFFSET)
            eff.setColor(QColor(0, 0, 0, T.SHADOW_SOFT_ALPHA))
            self.setGraphicsEffect(eff)
        # Allow downstream code to set its own layout; only the paint
        # path is owned by this class.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        # Phase 6M.1 — solid white fill.
        fill = QColor(255, 255, 255, 255)
        p.fillPath(path, fill)
        # 1-px soft-gray border for definition over the paper-white
        # background. Slightly stronger than the 6I value so cards
        # read as physical objects, per the directive.
        pen = QPen(QColor(24, 17, 45, 24))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


class FloatingPanel(GlassCard):
    """A GlassCard with a max-width cap so a wide screen does not
    stretch the surface to the edges. The launcher's three columns
    each render inside their own FloatingPanel."""

    def __init__(
        self,
        *,
        max_width: int = 720,
        radius: int = T.RADIUS_PANEL,
        alpha: int = T.SURFACE_ALPHA_HIGH,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(radius=radius, alpha=alpha, parent=parent)
        self.setMaximumWidth(max_width)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


class SoftDivider(QWidget):
    """1-px hairline with breathing room above and below. Used inside
    cards between header and body, and inside the sidebar between
    section groups."""

    def __init__(
        self,
        *,
        margin_v: int = 10,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedHeight(margin_v * 2 + 1)
        self._margin = margin_v

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        pen = QPen(QColor(24, 17, 45, 18))
        pen.setWidthF(1.0)
        p.setPen(pen)
        y = self._margin + 0.5
        p.drawLine(0, int(y), self.width(), int(y))
        p.end()


# ── badges & chips ────────────────────────────────────────────────


def _make_pill_label(
    text: str,
    *,
    fg: str,
    bg: str,
    border: Optional[str] = None,
    mono: bool = False,
) -> QLabel:
    """Build a single Qt label that paints a Pill — used by every
    chip-shaped surface. Avoids constructing a full custom widget
    when a QLabel + stylesheet is enough."""
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setFixedHeight(18)
    family = (
        "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
        if mono else "Segoe UI, system-ui, sans-serif"
    )
    border_decl = f"border: 1px solid {border};" if border else "border: 0;"
    lbl.setStyleSheet(
        f"QLabel {{"
        f"  background: {bg};"
        f"  color: {fg};"
        f"  {border_decl}"
        f"  border-radius: {T.RADIUS_PILL}px;"
        f"  padding: 0 8px;"
        f"  font-family: {family};"
        f"  font-size: {T.FS_LABEL}px;"
        f"  font-weight: 600;"
        f"  letter-spacing: 0.4px;"
        f"  text-transform: uppercase;"
        f"}}"
    )
    return lbl


class Pill(QWidget):
    """A small radius-12 lozenge. The base for chips, badges, and
    keyboard-shortcut labels. Pass the text + an optional `kind`
    (`accent` | `mute` | `count`)."""

    KIND_PALETTE = {
        "accent": (T.ACCENT, T.ACCENT_SOFT, T.ACCENT_LINE),
        "mute":   (T.INK_3, "#F3F0EC", T.HAIRLINE),
        "count":  (T.INK_2, "#EFEAE4", T.HAIRLINE),
    }

    def __init__(
        self,
        text: str,
        *,
        kind: str = "mute",
        mono: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        fg, bg, border = Pill.KIND_PALETTE.get(kind, Pill.KIND_PALETTE["mute"])
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_make_pill_label(text, fg=fg, bg=bg, border=border, mono=mono))


class ConfidenceBadge(QWidget):
    """The high / medium / low badge that sits in the right-meta
    column of a RecoveryCardV3.

    Matches `app/ui/cards.py:_ConfidenceBadge` colour vocabulary so
    a v3 capture and the live launcher show the same band semantics
    side-by-side."""

    PALETTE = {
        "high":   (T.ACCENT, T.ACCENT_SOFT, T.ACCENT_LINE, "high"),
        "medium": (T.WARN, T.WARN_SOFT, T.HAIRLINE, "med"),
        "low":    (T.INK_3, "#EFEAE4", T.HAIRLINE, "low"),
    }

    def __init__(
        self,
        level: str = "high",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        fg, bg, border, label = ConfidenceBadge.PALETTE.get(
            level, ConfidenceBadge.PALETTE["high"]
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_make_pill_label(label, fg=fg, bg=bg, border=border))


class TimelineChip(QWidget):
    """A mono-font chip carrying a short time-ish label.

    Used by:
      - the InvestigationCardV3 timeline strip (``09:20`` ``11:04``)
      - the RecoveryCardV3 chip row's *gap* chip (``2d gap``)
    """

    def __init__(
        self,
        text: str,
        *,
        accent: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        fg = T.ACCENT if accent else T.INK_3
        bg = T.ACCENT_SOFT if accent else "#F3F0EC"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_make_pill_label(text, fg=fg, bg=bg, mono=True))


class StatusDot(QLabel):
    """A 6-px round indicator. Used in the sidebar's section
    headers + the trust panel's daemon-connected line.

    Pass one of `accent` | `ok` | `warn` | `danger` | `mute`.
    """

    PALETTE = {
        "accent": T.ACCENT,
        "ok":     T.OK,
        "warn":   T.WARN,
        "danger": T.DANGER,
        "mute":   T.INK_4,
    }

    def __init__(
        self,
        kind: str = "accent",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        colour = StatusDot.PALETTE.get(kind, StatusDot.PALETTE["mute"])
        self.setFixedSize(8, 8)
        self.setStyleSheet(
            f"QLabel {{ background: {colour}; border-radius: 4px; }}"
        )


def section_label(text: str) -> QLabel:
    """The uppercase-tracked label used above every section. Same
    visual rhythm across the sidebar + the main column + the
    trust footer."""
    lbl = QLabel(text.upper())
    f = QFont()
    f.setPointSizeF(7.6)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color: {T.INK_3}; letter-spacing: 1.4px; "
        f"background: transparent; padding: 4px 0 6px;"
    )
    return lbl


__all__ = [
    "GlassCard",
    "FloatingPanel",
    "SoftDivider",
    "Pill",
    "ConfidenceBadge",
    "TimelineChip",
    "StatusDot",
    "section_label",
]
