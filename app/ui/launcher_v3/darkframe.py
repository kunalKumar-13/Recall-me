"""Phase 10 — dark-cinematic launcher surface.

Faithful PyQt6 port of `Recall Launcher.html` + `launcher.jsx` from
the Phase 10 design pack. Four states share one Frame:

  EmptyView      bloom mark + serif-italic tagline + start buttons
  RecoveryView   hero (title + chips + Resume/Review) + side preview
                 card + other-work rows
  SearchView     grouped results list + mini preview pane
  ResumeView     check disc + restored item list + Undo/Done

Frame: 760 x 520, radius 20, surface ``#0F0D16`` with a layered
violet bloom painted in. Search bar + content area + footer bar.

This module is *visual only* -- it does not import any engine
modules. Wiring (engine -> view) happens in ``live.py`` so the
visual surface can be screenshot-rendered offscreen with stubbed
fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from PyQt6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


# ── public size + state names ─────────────────────────────────────

FRAME_W = 760
FRAME_H = 520

STATE_EMPTY = "empty"
STATE_RECOVERY = "recovery"
STATE_SEARCH = "search"
STATE_RESUME = "resume"


# ── font helpers ──────────────────────────────────────────────────
#
# The offscreen Qt platform on Windows reports zero font families
# until we explicitly load TTFs via ``QFontDatabase.addApplicationFont``.
# Capture scripts hit this path; live launchers on a real desktop
# don't, because the regular Qt platform plugin populates the font DB
# from the OS. ``_ensure_fonts`` is idempotent + cheap -- safe to call
# from widget construction.


def _ensure_fonts() -> None:
    """Idempotent system-font bootstrap. Loads Segoe UI / Arial /
    Consolas / Georgia from ``C:/Windows/Fonts/`` if the database is
    empty. No-op if any families are already known to Qt."""
    try:
        if QFontDatabase.families():
            return
    except Exception:
        return
    import os.path
    for path in (
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeuii.ttf",
        "C:/Windows/Fonts/seguisym.ttf",      # Segoe UI Symbol -- has ⌃ ⏎
        "C:/Windows/Fonts/seguiemj.ttf",      # Segoe UI Emoji fallback
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/georgiai.ttf",
    ):
        if os.path.isfile(path):
            try:
                QFontDatabase.addApplicationFont(path)
            except Exception:
                pass


def _resolve_family(primary: str, fallback: str) -> str:
    """Return ``primary`` if installed, else the first installed
    member of the ``fallback`` comma list, else a stdlib-safe
    default. Lazily probes the font database; safe to call before
    QApplication is constructed (returns the primary name)."""
    try:
        fams = set(QFontDatabase.families())
    except Exception:
        return primary
    if not fams:
        return primary
    if primary in fams:
        return primary
    for candidate in [c.strip().strip("'\"") for c in fallback.split(",")]:
        if candidate in fams:
            return candidate
    # Last resort: pick the first installed family rather than
    # returning a name Qt doesn't know (which paints tofu).
    return next(iter(fams))


def _font_family(kind: str) -> str:
    """One of: 'sans', 'mono', 'serif'. Resolved per call so
    ``_ensure_fonts`` can populate the database between calls."""
    _ensure_fonts()
    if kind == "mono":
        return _resolve_family(T.FAMILY_MONO, T.FAMILY_MONO_FALLBACK)
    if kind == "serif":
        return _resolve_family(T.FAMILY_SERIF, T.FAMILY_SERIF_FALLBACK)
    return _resolve_family(T.FAMILY_SANS, T.FAMILY_SANS_FALLBACK)


class _FontFamilies:
    """Attribute-style accessor that resolves font families lazily.
    ``_FONT.SANS`` returns the current best string family each access;
    that lets ``_ensure_fonts`` populate the database between calls."""

    def __getattr__(self, kind: str) -> str:
        lowered = kind.lower()
        if lowered in ("sans", "mono", "serif"):
            return _font_family(lowered)
        raise AttributeError(kind)


_FONT = _FontFamilies()


def _font(family: str, *, size: float, bold: bool = False,
          italic: bool = False, letter_spacing: float = 0.0) -> QFont:
    f = QFont(family)
    f.setPointSizeF(size)
    if bold:
        f.setWeight(QFont.Weight.DemiBold)
    if italic:
        f.setItalic(True)
    if letter_spacing:
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing,
                           100 + letter_spacing)
    return f


# ── painting helpers ──────────────────────────────────────────────


def _rounded_path(rect: QRectF, radius: float) -> QPainterPath:
    p = QPainterPath()
    p.addRoundedRect(rect, radius, radius)
    return p


def _qcolor(spec: str) -> QColor:
    """Accept either a ``#RRGGBB`` literal or an ``rgba(R, G, B, A)``
    string with A in 0..1. PyQt6's ``QColor`` parses the former
    natively; the latter we split by hand."""
    spec = spec.strip()
    if spec.startswith("rgba"):
        inside = spec[spec.index("(") + 1: spec.rindex(")")]
        parts = [s.strip() for s in inside.split(",")]
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        a = float(parts[3])
        c = QColor(r, g, b)
        c.setAlphaF(a)
        return c
    return QColor(spec)


# ── SVG glyphs ────────────────────────────────────────────────────
#
# All four states draw small line glyphs at 12-17 px. Each glyph is
# painted with a single 1.4-px round-cap stroke in the row's tint
# colour (accent on selected rows; muted/faint elsewhere). Glyphs
# are kept tiny + readable -- the JSX matches.


def _stroke_pen(color: QColor, width: float = 1.4) -> QPen:
    pen = QPen(color)
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _draw_glyph_search(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    p.drawEllipse(QPointF(s * 0.44, s * 0.44), s * 0.28, s * 0.28)
    p.drawLine(QPointF(s * 0.66, s * 0.66), QPointF(s * 0.92, s * 0.92))


def _draw_glyph_file(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    path = QPainterPath()
    path.moveTo(s * 0.22, s * 0.10)
    path.lineTo(s * 0.55, s * 0.10)
    path.lineTo(s * 0.78, s * 0.32)
    path.lineTo(s * 0.78, s * 0.88)
    path.lineTo(s * 0.22, s * 0.88)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.55, s * 0.10), QPointF(s * 0.55, s * 0.32))
    p.drawLine(QPointF(s * 0.55, s * 0.32), QPointF(s * 0.78, s * 0.32))


def _draw_glyph_tab(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    p.drawRoundedRect(QRectF(s * 0.10, s * 0.25, s * 0.80, s * 0.55),
                      2, 2)
    p.drawLine(QPointF(s * 0.10, s * 0.45), QPointF(s * 0.90, s * 0.45))


def _draw_glyph_thread(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    # three nodes
    nodes = [(s * 0.22, s * 0.22), (s * 0.78, s * 0.42), (s * 0.30, s * 0.78)]
    for cx, cy in nodes:
        p.drawEllipse(QPointF(cx, cy), s * 0.10, s * 0.10)
    p.drawLine(QPointF(nodes[0][0], nodes[0][1] + s * 0.10),
               QPointF(nodes[0][0] + s * 0.05, nodes[2][1] - s * 0.10))
    p.drawLine(QPointF(nodes[0][0] + s * 0.10, nodes[0][1] + s * 0.05),
               QPointF(nodes[1][0] - s * 0.10, nodes[1][1] - s * 0.05))
    p.drawLine(QPointF(nodes[1][0] - s * 0.05, nodes[1][1] + s * 0.10),
               QPointF(nodes[2][0] + s * 0.10, nodes[2][1] - s * 0.05))


def _draw_glyph_chat(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    path = QPainterPath()
    path.moveTo(s * 0.16, s * 0.30)
    path.cubicTo(s * 0.16, s * 0.22, s * 0.16, s * 0.16, s * 0.30, s * 0.16)
    path.lineTo(s * 0.70, s * 0.16)
    path.cubicTo(s * 0.84, s * 0.16, s * 0.84, s * 0.22, s * 0.84, s * 0.30)
    path.lineTo(s * 0.84, s * 0.54)
    path.cubicTo(s * 0.84, s * 0.65, s * 0.78, s * 0.68, s * 0.68, s * 0.68)
    path.lineTo(s * 0.40, s * 0.68)
    path.lineTo(s * 0.22, s * 0.84)
    path.lineTo(s * 0.22, s * 0.68)
    path.cubicTo(s * 0.16, s * 0.66, s * 0.16, s * 0.60, s * 0.16, s * 0.54)
    path.closeSubpath()
    p.drawPath(path)


def _draw_glyph_deck(p: QPainter, size: float, color: QColor) -> None:
    p.setPen(_stroke_pen(color))
    s = size
    p.drawRoundedRect(QRectF(s * 0.12, s * 0.18, s * 0.76, s * 0.50),
                      2, 2)
    p.drawLine(QPointF(s * 0.30, s * 0.80), QPointF(s * 0.70, s * 0.80))


def _draw_glyph_check(p: QPainter, size: float, color: QColor) -> None:
    pen = _stroke_pen(color, width=1.7)
    p.setPen(pen)
    s = size
    p.drawLine(QPointF(s * 0.22, s * 0.52),
               QPointF(s * 0.42, s * 0.72))
    p.drawLine(QPointF(s * 0.42, s * 0.72),
               QPointF(s * 0.80, s * 0.30))


GLYPHS = {
    "search":    _draw_glyph_search,
    "file":      _draw_glyph_file,
    "tab":       _draw_glyph_tab,
    "thread":    _draw_glyph_thread,
    "chat":      _draw_glyph_chat,
    "deck":      _draw_glyph_deck,
    "check":     _draw_glyph_check,
    "doc":       _draw_glyph_file,
    "research":  _draw_glyph_search,
    "search_sm": _draw_glyph_search,
}


class Glyph(QWidget):
    """Tiny SVG-style glyph rendered by ``GLYPHS[name]``. ``color``
    sets the stroke; defaults to the row's tint at paint time."""

    def __init__(self, name: str, *, size: int = 12,
                 color: Optional[str] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._name = name
        self._size = size
        self._color = color
        self.setFixedSize(size, size)

    def set_color(self, color: str) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        col = _qcolor(self._color or T.INK_MUTED)
        draw = GLYPHS.get(self._name, _draw_glyph_search)
        draw(p, self._size, col)
        p.end()


# ── Clickable label (Phase P0) ────────────────────────────────────


class _ClickableLabel(QLabel):
    """A QLabel that emits ``clicked`` on left-mouse release.
    Used by the preview card's "Open ↗" link so the host can route
    the click to the OS open helper."""

    clicked = pyqtSignal()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


# ── Kbd pill ──────────────────────────────────────────────────────


class Kbd(QLabel):
    """A small mono-font key pill (``⌃`` / ``K`` / ``⏎``).

    Painted via QSS so the label still reflows when the parent
    layout resizes."""

    def __init__(self, text: str, *, large: bool = False,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        font_size = 11 if large else 10.5
        self.setFont(_font(_FONT.MONO, size=font_size,
                           letter_spacing=2.0))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pad_v = 3 if large else 2
        pad_h = 7 if large else 6
        min_w = 22 if large else 20
        self.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.INK_MUTED};"
            f"  background: rgba(255, 255, 255, 0.04);"
            f"  border: 1px solid {T.LINE};"
            f"  padding: {pad_v}px {pad_h}px;"
            f"  border-radius: 5px;"
            f"  min-width: {min_w}px;"
            f"}}"
        )


# ── Buttons ───────────────────────────────────────────────────────


class PrimaryBtn(QWidget):
    """Lavender gradient pill. Emits ``clicked`` on left-mouse
    release. Optional ``kbd`` chip painted on the right."""

    clicked = pyqtSignal()

    def __init__(self, label: str, *, kbd: Optional[str] = None,
                 size: str = "md",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._label = label
        self._kbd = kbd
        self._size = size
        h = 30 if size == "sm" else 34
        fs = T.FS_BUTTON_SM if size == "sm" else T.FS_BUTTON
        pad_h = 12 if size == "sm" else 14
        # Width: approx ``label width + (kbd ? 20 : 0) + 2 * pad_h``
        approx_label_w = int(len(label) * (fs * 0.55)) + 4
        kbd_w = 22 if kbd else 0
        self.setFixedSize(approx_label_w + kbd_w + 2 * pad_h, h)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fs = fs
        self._hover = False

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        if self._hover:
            rect.translate(0, -1)
        # gradient fill
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0.0, QColor("#B79AFF"))
        grad.setColorAt(0.55, QColor(T.ACCENT))
        grad.setColorAt(1.0, QColor(T.ACCENT_DEEP))
        path = _rounded_path(rect, T.RADIUS_PILL)
        p.fillPath(path, QBrush(grad))
        # ring
        ring_pen = QPen(_qcolor("rgba(167, 139, 250, 0.4)"))
        ring_pen.setWidthF(1.0)
        p.setPen(ring_pen)
        p.drawPath(path)
        # label
        p.setPen(QColor("#0A0810"))
        p.setFont(_font(_FONT.SANS, size=self._fs, bold=True,
                        letter_spacing=-0.5))
        text_rect = rect.adjusted(14, 0, -14, 0)
        if self._kbd:
            text_rect = QRectF(rect.x() + 14, rect.y(),
                               rect.width() - 38, rect.height())
        p.drawText(text_rect,
                   Qt.AlignmentFlag.AlignVCenter
                   | Qt.AlignmentFlag.AlignLeft, self._label)
        # kbd chip on the right
        if self._kbd:
            chip_w = 18
            chip_h = 18
            chip_x = rect.x() + rect.width() - 14 - chip_w
            chip_y = rect.y() + (rect.height() - chip_h) / 2
            chip_rect = QRectF(chip_x, chip_y, chip_w, chip_h)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(10, 8, 16, int(0.25 * 255)))
            p.drawRoundedRect(chip_rect, 4, 4)
            p.setPen(QColor(10, 8, 16, int(0.85 * 255)))
            p.setFont(_font(_FONT.MONO, size=10, bold=True))
            p.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, self._kbd)
        p.end()


class GhostBtn(QWidget):
    """Outline pill (transparent fill, white-12% border).

    Same geometry as PrimaryBtn."""

    clicked = pyqtSignal()

    def __init__(self, label: str, *, size: str = "md",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._label = label
        self._size = size
        h = 30 if size == "sm" else 34
        fs = T.FS_BUTTON_SM if size == "sm" else T.FS_BUTTON
        pad_h = 12 if size == "sm" else 14
        approx_label_w = int(len(label) * (fs * 0.55)) + 4
        self.setFixedSize(approx_label_w + 2 * pad_h, h)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fs = fs
        self._hover = False

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        if self._hover:
            rect.translate(0, -1)
        path = _rounded_path(rect, T.RADIUS_PILL)
        # subtle fill
        fill_alpha = 0.05 if self._hover else 0.02
        p.fillPath(path, QColor(255, 255, 255, int(fill_alpha * 255)))
        # border
        border = _qcolor("rgba(255, 255, 255, 0.2)") if self._hover \
            else _qcolor(T.LINE_HI)
        pen = QPen(border)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        # label
        p.setPen(_qcolor(T.INK))
        p.setFont(_font(_FONT.SANS, size=self._fs,
                        letter_spacing=-0.5))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()


# ── Chip ──────────────────────────────────────────────────────────


class Chip(QWidget):
    """Hero evidence chip: ``[icon] label``.

    24-px tall pill with a 1-px hairline border."""

    HEIGHT = 24

    def __init__(self, glyph_name: str, label: str,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,
                           QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.setSpacing(6)
        g = Glyph(glyph_name, size=11, color=T.ACCENT)
        layout.addWidget(g)
        lbl = QLabel(label)
        lbl.setFont(_font(_FONT.SANS, size=T.FS_CHIP))
        lbl.setStyleSheet(f"color: {T.INK_2}; background: transparent;")
        layout.addWidget(lbl)
        # cache width using fontMetrics so the chip auto-sizes
        fm = lbl.fontMetrics()
        self.setFixedWidth(fm.horizontalAdvance(label) + 11 + 9 * 2 + 6)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_CHIP)
        p.fillPath(path, QColor(255, 255, 255, int(0.035 * 255)))
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


# ── SearchBar ─────────────────────────────────────────────────────


class SearchBar(QWidget):
    """Top 60-px row: search glyph + input/value + optional
    ``N results`` mono microtext + ⌃ K kbd pair. Border-bottom
    LINE.

    Public surface preserves the frozen 7E.1 contract:
      query_changed(str)
      searchChanged(str)     # alias
      submit(str)
      request_settings()
      request_close()
      focus(), clear(), selectAll()
    """

    query_changed = pyqtSignal(str)
    searchChanged = pyqtSignal(str)
    submit = pyqtSignal(str)
    request_settings = pyqtSignal()
    request_close = pyqtSignal()

    def __init__(self, *, value: str = "",
                 placeholder: str = "Search what you were working on…",
                 with_caret: bool = False,
                 results: Optional[int] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(T.H_SEARCH)
        self._with_caret = with_caret
        self._results = results
        outer = QHBoxLayout(self)
        outer.setContentsMargins(22, 0, 22, 0)
        outer.setSpacing(14)

        self._glyph = Glyph("search", size=17,
                            color=T.ACCENT if value else T.INK_MUTED)
        outer.addWidget(self._glyph)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        self._input.setText(value)
        self._input.setFrame(False)
        self._input.setFont(_font(_FONT.SANS, size=T.FS_SEARCH_INPUT,
                                  letter_spacing=-1.2))
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: transparent;"
            f"  color: {T.INK};"
            f"  border: none;"
            f"  selection-background-color: {T.ACCENT_SOFT};"
            f"}}"
        )
        self._input.textChanged.connect(self._on_changed)
        self._input.returnPressed.connect(
            lambda: self.submit.emit(self._input.text()))
        outer.addWidget(self._input, 1)

        if results is not None:
            self._results_lbl = QLabel(f"{results} results")
            self._results_lbl.setFont(_font(_FONT.MONO, size=10.5,
                                            letter_spacing=4.0))
            self._results_lbl.setStyleSheet(
                f"color: {T.INK_FAINT}; background: transparent;")
            outer.addWidget(self._results_lbl)

        outer.addWidget(Kbd("⌃"))
        outer.addWidget(Kbd("K"))

    # state helpers --------------------------------------------------

    def text(self) -> str:
        return self._input.text()

    def setText(self, value: str) -> None:
        self._input.setText(value)

    def focus(self) -> None:
        self._input.setFocus()

    def clear(self) -> None:
        self._input.clear()

    def selectAll(self) -> None:  # noqa: N802 — matches Qt naming
        self._input.selectAll()

    # internal -------------------------------------------------------

    def _on_changed(self, value: str) -> None:
        self._glyph.set_color(T.ACCENT if value else T.INK_MUTED)
        self.query_changed.emit(value)
        self.searchChanged.emit(value)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # bottom hairline
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawLine(0, self.height() - 1,
                   self.width(), self.height() - 1)
        p.end()


# ── Footer ────────────────────────────────────────────────────────


class Footer(QWidget):
    """Bottom 30-px row: dot + ``recall · local`` left, key hints
    right. Mono uppercase microtext."""

    def __init__(self, *, right_text: str = "",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(T.H_FOOTER)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(22, 0, 22, 0)
        outer.setSpacing(8)

        left_row = QHBoxLayout()
        left_row.setContentsMargins(0, 0, 0, 0)
        left_row.setSpacing(8)
        self._dot = _StatusDot()
        left_row.addWidget(self._dot)
        left_lbl = QLabel("RECALL · LOCAL")
        left_lbl.setFont(_font(_FONT.MONO, size=T.FS_MONO,
                               letter_spacing=6.0))
        left_lbl.setStyleSheet(f"color: {T.INK_DIM}; background: transparent;")
        left_row.addWidget(left_lbl)
        outer.addLayout(left_row)

        outer.addStretch(1)

        if right_text:
            right_lbl = QLabel(right_text)
            right_lbl.setFont(_font(_FONT.MONO, size=T.FS_MONO,
                                    letter_spacing=6.0))
            right_lbl.setStyleSheet(
                f"color: {T.INK_DIM}; background: transparent;")
            outer.addWidget(right_lbl)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawLine(0, 0, self.width(), 0)
        p.end()


class _StatusDot(QWidget):
    """5-px green dot with a soft glow halo."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(13, 13)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # halo
        halo = QRadialGradient(QPointF(6.5, 6.5), 6.5)
        halo.setColorAt(0.0, _qcolor(T.OK_GLOW))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(QPointF(6.5, 6.5), 6.5, 6.5)
        # dot
        p.setBrush(QColor(T.OK))
        p.drawEllipse(QPointF(6.5, 6.5), 2.5, 2.5)
        p.end()


# ── Frame ─────────────────────────────────────────────────────────


class Frame(QWidget):
    """760 x 520 dark window.

    Composed of: painted bloom background + painted top-edge gradient
    + a child vertical layout for search-bar / content / footer."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(FRAME_W, FRAME_H)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        # The frame's drop shadow is rendered by its parent (the
        # outer window paints the violet halo). Here we only paint
        # the window's *inside*: surface + radial blooms + top edge.
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.search_bar: Optional[SearchBar] = None
        self.content: Optional[QWidget] = None
        self.footer: Optional[Footer] = None

    def _swap(self, current: Optional[QWidget],
              new: QWidget, index: int) -> None:
        """Remove ``current`` from the layout + reparent so it stops
        painting immediately, then insert ``new`` at ``index``.
        ``deleteLater`` is async; ``setParent(None)`` is sync, which
        is what we need for a single-frame swap during state changes."""
        if current is not None:
            self._layout.removeWidget(current)
            current.setParent(None)
            current.deleteLater()
        self._layout.insertWidget(index, new,
                                  1 if isinstance(new, QWidget)
                                       and new.sizePolicy().verticalPolicy()
                                       == QSizePolicy.Policy.Expanding
                                       else 0)

    def set_search_bar(self, w: SearchBar) -> None:
        self._swap(self.search_bar, w, 0)
        self.search_bar = w

    def set_content(self, w: QWidget) -> None:
        idx = 1 if self.search_bar is not None else 0
        self._swap(self.content, w, idx)
        # Content area always stretches.
        w.setSizePolicy(QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Expanding)
        # Force stretch factor explicitly since _swap derived it
        # from the *new* widget's policy before our call.
        i = self._layout.indexOf(w)
        if i >= 0:
            self._layout.setStretch(i, 1)
        self.content = w

    def set_footer(self, w: Footer) -> None:
        idx = self._layout.count()
        self._swap(self.footer, w, idx)
        self.footer = w

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_FRAME)
        p.setClipPath(path)
        # base surface
        p.fillPath(path, QColor(T.SURFACE))
        # top-left bloom
        bloom1 = QRadialGradient(QPointF(rect.width() * 0.22, 0),
                                 max(rect.width() * 0.6, rect.height() * 0.4))
        bloom1.setColorAt(0.0, _qcolor("rgba(167, 139, 250, 0.18)"))
        bloom1.setColorAt(0.6, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(bloom1))
        # bottom-right bloom
        bloom2 = QRadialGradient(
            QPointF(rect.width(), rect.height()),
            max(rect.width() * 0.5, rect.height() * 0.5))
        bloom2.setColorAt(0.0, _qcolor("rgba(139, 127, 227, 0.10)"))
        bloom2.setColorAt(0.65, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(bloom2))
        # top-edge highlight (1-px violet glint)
        grad = QLinearGradient(0, 0, rect.width(), 0)
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        grad.setColorAt(0.5, _qcolor("rgba(167, 139, 250, 0.32)"))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, 0, rect.width(), 1), QBrush(grad))
        # outer border
        pen = QPen(_qcolor(T.LINE_HI))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setClipping(False)
        p.drawPath(path)
        p.end()


# ── EmptyView ─────────────────────────────────────────────────────


class _BloomMark(QWidget):
    """76-px memory bloom: concentric lavender rings + soft glow +
    bright centre disc."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(104, 104)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        # outer halo
        halo = QRadialGradient(QPointF(cx, cy), 52)
        halo.setColorAt(0.0, _qcolor("rgba(167, 139, 250, 0.35)"))
        halo.setColorAt(0.65, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(QPointF(cx, cy), 52, 52)
        # outer ring
        pen = QPen(_qcolor("rgba(167, 139, 250, 0.18)"))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), 32, 32)
        # inner ring
        pen = QPen(_qcolor("rgba(167, 139, 250, 0.30)"))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), 22, 22)
        # central bloom disc
        bloom = QRadialGradient(QPointF(cx, cy - 4), 16)
        bloom.setColorAt(0.0, QColor(255, 255, 255, int(0.95 * 255)))
        bloom.setColorAt(0.4, QColor("#C9B6FF"))
        bloom.setColorAt(1.0, QColor("#6B5FCB"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bloom))
        p.drawEllipse(QPointF(cx, cy), 11, 11)
        # bright dot
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(QPointF(cx, cy), 3.4, 3.4)
        p.end()


class _ServifGradientLabel(QLabel):
    """Static label that paints its text with a lavender gradient
    fill. Used for the *italic* accent word in the Empty tagline /
    Recovery hero / Resume header."""

    def __init__(self, text: str, *, font: QFont,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self._text = text
        self._font = font
        self.setFont(font)
        # measure with the actual font
        fm = self.fontMetrics()
        self._width = fm.horizontalAdvance(text)
        self._height = fm.height()
        self.setFixedSize(self._width + 4, self._height + 4)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#E6D8FF"))
        grad.setColorAt(0.5, QColor("#C9B6FF"))
        grad.setColorAt(1.0, QColor("#B79EFF"))
        p.setPen(QPen(QBrush(grad), 1))
        p.setFont(self._font)
        p.drawText(self.rect(),
                   Qt.AlignmentFlag.AlignVCenter
                   | Qt.AlignmentFlag.AlignLeft, self._text)
        p.end()


class EmptyView(QWidget):
    """Empty state — bloom mark, headline w/ serif italic accent,
    sub copy, Show example / Start working buttons."""

    show_example = pyqtSignal()
    start_working = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 0, 40, 0)
        outer.setSpacing(22)
        outer.addStretch(1)

        # bloom mark
        bloom_row = QHBoxLayout()
        bloom_row.addStretch(1)
        bloom_row.addWidget(_BloomMark())
        bloom_row.addStretch(1)
        outer.addLayout(bloom_row)

        # headline + serif italic
        title = QLabel("Everything you leave")
        title.setFont(_font(_FONT.SANS, size=T.FS_HERO_TITLE, bold=True,
                            letter_spacing=-2.2))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {T.INK}; background: transparent;")
        outer.addWidget(title)

        serif_row = QHBoxLayout()
        serif_row.addStretch(1)
        serif_lbl = _ServifGradientLabel(
            "becomes searchable.",
            font=_font(_FONT.SERIF, size=T.FS_HERO_TITLE + 4,
                       italic=True, letter_spacing=-2.0),
        )
        serif_row.addWidget(serif_lbl)
        serif_row.addStretch(1)
        outer.addLayout(serif_row)

        # sub copy
        sub = QLabel(
            "Recall sits quietly while you work, then brings\n"
            "everything back the moment you return.")
        sub.setFont(_font(_FONT.SANS, size=T.FS_ROW_TITLE,
                          letter_spacing=-0.5))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            f"color: {T.INK_MUTED}; background: transparent;")
        outer.addWidget(sub)

        # buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(T.GAP_BTN + 2)
        btn_row.addStretch(1)
        ghost = GhostBtn("Show example")
        ghost.clicked.connect(self.show_example.emit)
        primary = PrimaryBtn("Start working", kbd="⏎")
        primary.clicked.connect(self.start_working.emit)
        btn_row.addWidget(ghost)
        btn_row.addWidget(primary)
        btn_row.addStretch(1)
        outer.addLayout(btn_row)

        outer.addStretch(1)


# ── Recovery hero + preview + other-work rows ─────────────────────


@dataclass
class RecoveryProps:
    title_main: str = "WebSocket retry"
    title_accent: str = "debugging."
    eyebrow_meta: str = "Returned after 2 days"
    n_files: int = 2
    n_tabs: int = 2
    n_searches: int = 1
    last_active: str = "last active · implementation"


@dataclass
class PreviewProps:
    label: str = "pitch_healthcare_v3.pdf"
    excerpt_prefix: str = "Our vision is to build AI agents that"
    excerpt_highlight: str = "assist healthcare teams"
    excerpt_suffix: str = "by triaging patient queries…"
    meta: str = "~/notes · 4d"


@dataclass
class OtherWorkRow:
    glyph: str
    title: str
    when: str
    strength: str           # "high" | "med" | "low"


class HeroRecovery(QWidget):
    """The Continue card. Painted gradient surface + accent rail +
    eyebrow + title (with serif italic accent word) + chips +
    Resume/Review buttons."""

    resume_clicked = pyqtSignal()
    review_clicked = pyqtSignal()

    def __init__(self, props: RecoveryProps,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._props = props
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        outer = QVBoxLayout(self)
        # Phase 10D — softer hero padding (16 -> 22 top/bottom, 18 -> 22 sides)
        outer.setContentsMargins(22, 20, 22, 20)
        outer.setSpacing(0)

        # eyebrow row -- single source of metadata: the "Returned
        # after N days" clause. Phase 10D removes the duplicate
        # "last active · implementation" mono microtext that used
        # to sit on the actions row; the eyebrow already tells the
        # story.
        eyebrow = QHBoxLayout()
        eyebrow.setContentsMargins(0, 0, 0, 0)
        eyebrow.setSpacing(8)
        em = QLabel("CONTINUE")
        em.setFont(_font(_FONT.MONO, size=T.FS_EYEBROW,
                         letter_spacing=16.0))
        em.setStyleSheet(f"color: {T.ACCENT}; background: transparent;")
        eyebrow.addWidget(em)
        bullet = QLabel("•")
        bullet.setStyleSheet(f"color: {T.INK_FAINT}; background: transparent;")
        eyebrow.addWidget(bullet)
        meta = QLabel(props.eyebrow_meta)
        meta.setFont(_font(_FONT.SANS, size=T.FS_EYEBROW + 1,
                           letter_spacing=2.0))
        meta.setStyleSheet(f"color: {T.INK_MUTED}; background: transparent;")
        eyebrow.addWidget(meta)
        eyebrow.addStretch(1)
        outer.addLayout(eyebrow)
        outer.addSpacing(12)

        # title row: main + serif italic accent. Phase 10D bumps
        # FS_HERO_TITLE 22 -> 25 -- the hero reads as the page
        # headline of the surface, not just a card title.
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)
        title_main = QLabel(props.title_main + " ")
        title_main.setFont(_font(_FONT.SANS, size=T.FS_HERO_TITLE,
                                 bold=True, letter_spacing=-2.4))
        title_main.setStyleSheet(
            f"color: {T.INK}; background: transparent;")
        title_row.addWidget(title_main)
        title_accent = _ServifGradientLabel(
            props.title_accent,
            font=_font(_FONT.SERIF, size=T.FS_HERO_TITLE + 3,
                       italic=True, letter_spacing=-2.0),
        )
        title_row.addWidget(title_accent)
        title_row.addStretch(1)
        outer.addLayout(title_row)
        outer.addSpacing(16)

        # chips row
        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 0, 0, 0)
        chip_row.setSpacing(T.GAP_CHIP)
        chip_row.addWidget(Chip("file", f"{props.n_files} files"))
        chip_row.addWidget(Chip("tab", f"{props.n_tabs} tabs"))
        chip_row.addWidget(Chip("search_sm", f"{props.n_searches} search"))
        chip_row.addStretch(1)
        outer.addLayout(chip_row)

        outer.addStretch(1)

        # actions row -- Resume + Review only. The "last active"
        # microtext was duplicate metadata against the eyebrow's
        # "Returned after N days" clause and gone in Phase 10D.
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(T.GAP_BTN)
        resume = PrimaryBtn("Resume", kbd="⏎")
        resume.clicked.connect(self.resume_clicked.emit)
        review = GhostBtn("Review")
        review.clicked.connect(self.review_clicked.emit)
        actions.addWidget(resume)
        actions.addWidget(review)
        actions.addStretch(1)
        outer.addLayout(actions)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_CARD)
        # gradient surface
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0.0, QColor(T.CARD_HI))
        grad.setColorAt(1.0, QColor(T.CARD))
        p.fillPath(path, QBrush(grad))
        # accent rail (top 18 -> bottom 18, on left edge)
        rail = QRectF(rect.x(), rect.y() + 18, 2.0, rect.height() - 36)
        rail_grad = QLinearGradient(0, rail.y(), 0,
                                    rail.y() + rail.height())
        rail_grad.setColorAt(0.0, _qcolor(T.ACCENT))
        rail_grad.setColorAt(1.0, _qcolor("rgba(167, 139, 250, 0.2)"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(rail_grad))
        p.drawRoundedRect(rail, 2, 2)
        # 1-px border
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


class PreviewCard(QWidget):
    """Side preview card. Used in Recovery state (right column,
    220 px wide). Has a subtle corner glow + PDF badge + excerpt
    with highlighted phrase + a footer with ``Open`` link."""

    open_clicked = pyqtSignal()

    def __init__(self, props: PreviewProps,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._props = props
        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,
                           QSizePolicy.Policy.Expanding)
        outer = QVBoxLayout(self)
        # Phase 10D — preserve the design's padding, tighten inner
        # spacing slightly so the eyebrow + badge + excerpt read as
        # a clear three-step hierarchy.
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(11)

        # Phase 10D — eyebrow simplified from "PREVIEW · RELATED" to
        # just "PREVIEW", bumped slightly heavier so it reads as a
        # section label not a tooltip.
        eyebrow = QLabel("PREVIEW")
        eyebrow.setFont(_font(_FONT.MONO, size=T.FS_MONO_SM,
                              letter_spacing=18.0, bold=True))
        eyebrow.setStyleSheet(
            f"color: {T.INK_MUTED}; background: transparent;")
        outer.addWidget(eyebrow)

        # PDF badge row
        badge = QWidget()
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(7, 4, 7, 4)
        badge_layout.setSpacing(7)
        pdf_tag = QLabel("PDF")
        pdf_tag.setFont(_font(_FONT.MONO, size=8, bold=True,
                              letter_spacing=8.0))
        pdf_tag.setStyleSheet(
            "color: white; background: #E15050;"
            "padding: 1px 4px; border-radius: 2px;")
        badge_layout.addWidget(pdf_tag)
        label = QLabel(props.label)
        # Phase 10D — slightly heavier label weight (bold) so the
        # filename reads as the card's anchor; size unchanged so it
        # doesn't clip in the 220-px column.
        label.setFont(_font(_FONT.SANS, size=10, bold=True))
        label.setStyleSheet(f"color: {T.INK_2}; background: transparent;")
        badge_layout.addWidget(label)
        badge_layout.addStretch(1)
        badge.setStyleSheet(
            f"background: {T.DANGER_SOFT};"
            f"border: 1px solid rgba(229, 80, 80, 0.22);"
            f"border-radius: 5px;")
        outer.addWidget(badge)

        # excerpt — original size; Phase 10D bumps the highlight
        # marker contrast slightly so the eye lands on the
        # highlighted phrase first.
        excerpt = QLabel(
            f"{props.excerpt_prefix} "
            f"<mark style='background: rgba(167,139,250,0.26);"
            f" color: {T.INK}; padding: 1px 4px; border-radius: 3px;'>"
            f"{props.excerpt_highlight}</mark> "
            f"{props.excerpt_suffix}")
        excerpt.setFont(_font(_FONT.SANS, size=12,
                              letter_spacing=-0.3))
        excerpt.setStyleSheet(
            f"color: {T.INK_2}; background: transparent;"
            f"line-height: 155%;")
        excerpt.setWordWrap(True)
        excerpt.setTextFormat(Qt.TextFormat.RichText)
        outer.addWidget(excerpt, 1)

        # footer divider
        footer_line = QWidget()
        footer_line.setFixedHeight(1)
        footer_line.setStyleSheet(f"background: {T.LINE};")
        outer.addWidget(footer_line)

        foot = QHBoxLayout()
        foot.setContentsMargins(0, 4, 0, 0)
        foot.setSpacing(0)
        meta = QLabel(props.meta)
        meta.setFont(_font(_FONT.MONO, size=T.FS_MONO,
                           letter_spacing=4.0))
        meta.setStyleSheet(f"color: {T.INK_DIM}; background: transparent;")
        foot.addWidget(meta)
        foot.addStretch(1)
        open_lbl = _ClickableLabel("Open  ↗")
        open_lbl.setFont(_font(_FONT.SANS, size=11, bold=True))
        open_lbl.setStyleSheet(
            f"color: {T.ACCENT}; background: transparent;")
        open_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        open_lbl.clicked.connect(self.open_clicked.emit)
        foot.addWidget(open_lbl)
        outer.addLayout(foot)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_CARD)
        p.setClipPath(path)
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0.0, QColor(T.CARD_HI))
        grad.setColorAt(1.0, QColor(T.CARD))
        p.fillPath(path, QBrush(grad))
        # corner glow
        corner = QRadialGradient(
            QPointF(rect.width(), 0), 80)
        corner.setColorAt(0.0, _qcolor("rgba(167, 139, 250, 0.20)"))
        corner.setColorAt(0.65, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(corner))
        p.setClipping(False)
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


class OtherRow(QWidget):
    """One 32-px row under the *Other work* heading. Strength dot
    (lavender/grey/dim) + glyph + title + when label."""

    clicked = pyqtSignal()

    def __init__(self, row: OtherWorkRow,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._row = row
        self._hover = False
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 0, 12, 0)
        outer.setSpacing(12)
        # dot (paint via painter; spacer here)
        self._dot_pad = QWidget()
        self._dot_pad.setFixedSize(7, 7)
        outer.addWidget(self._dot_pad)
        outer.addWidget(Glyph(row.glyph, size=12, color=T.INK_FAINT))
        title = QLabel(row.title)
        title.setFont(_font(_FONT.SANS, size=T.FS_ROW_TITLE,
                            letter_spacing=-0.5))
        title.setStyleSheet(f"color: {T.INK_2}; background: transparent;")
        title.setMinimumWidth(1)
        outer.addWidget(title, 1)
        when = QLabel(row.when)
        when.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                           letter_spacing=4.0))
        when.setStyleSheet(f"color: {T.INK_DIM}; background: transparent;")
        outer.addWidget(when)

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        if self._hover:
            path = _rounded_path(rect, 9)
            p.fillPath(path, QColor(T.CARD_HOVER))
        # paint the strength dot in the gutter left of the glyph
        dot_x = 12 + 3.5
        dot_y = self.height() / 2
        if self._row.strength == "high":
            fill = _qcolor(T.ACCENT)
            ring = _qcolor("rgba(167, 139, 250, 0.20)")
            glow = True
        elif self._row.strength == "med":
            fill = _qcolor("#9685D8")
            ring = _qcolor("rgba(150, 133, 216, 0.18)")
            glow = False
        else:
            fill = _qcolor("#5D5773")
            ring = _qcolor("rgba(93, 87, 115, 0.18)")
            glow = False
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ring)
        p.drawEllipse(QPointF(dot_x, dot_y), 6.5, 6.5)
        if glow:
            halo = QRadialGradient(QPointF(dot_x, dot_y), 8)
            halo.setColorAt(0.0, _qcolor(T.ACCENT_SOFT))
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(halo))
            p.drawEllipse(QPointF(dot_x, dot_y), 8, 8)
        p.setBrush(fill)
        p.drawEllipse(QPointF(dot_x, dot_y), 3.5, 3.5)
        p.end()


class RecoveryView(QWidget):
    """State 2 — the Continue hero + side preview + other-work rows."""

    resume = pyqtSignal()
    review = pyqtSignal()
    row_clicked = pyqtSignal(int)
    # Phase P0 — forward the PreviewCard's Open ↗ click so the
    # launcher can route it to the OS open helper. Additive: existing
    # `resume` / `review` / `row_clicked` signals unchanged.
    preview_open = pyqtSignal()

    def __init__(self,
                 *,
                 recovery: Optional[RecoveryProps] = None,
                 preview: Optional[PreviewProps] = None,
                 other_work: Optional[List[OtherWorkRow]] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        recovery = recovery or RecoveryProps()
        preview = preview or PreviewProps()
        other_work = other_work or [
            OtherWorkRow("doc", "Healthcare proposal — outline v3",
                         "yesterday", "high"),
            OtherWorkRow("research", "RLHF reward model evaluation",
                         "3 days ago", "med"),
            OtherWorkRow("deck", "Startup deck — Y26 raise",
                         "last week", "low"),
        ]
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 16)
        outer.setSpacing(14)

        # hero + preview row
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(14)
        hero = HeroRecovery(recovery)
        hero.resume_clicked.connect(self.resume.emit)
        hero.review_clicked.connect(self.review.emit)
        row1.addWidget(hero, 1)
        # Phase P0 — capture the preview card so its Open ↗ link
        # forwards through this view's `preview_open` signal.
        preview_card = PreviewCard(preview)
        preview_card.open_clicked.connect(self.preview_open.emit)
        row1.addWidget(preview_card)
        outer.addLayout(row1, 1)

        # other work header
        ow_head = QHBoxLayout()
        ow_head.setContentsMargins(4, 0, 4, 0)
        ow_head.setSpacing(0)
        ow_lbl = QLabel("OTHER WORK")
        ow_lbl.setFont(_font(_FONT.MONO, size=T.FS_EYEBROW,
                             letter_spacing=16.0))
        ow_lbl.setStyleSheet(
            f"color: {T.INK_FAINT}; background: transparent;")
        ow_head.addWidget(ow_lbl)
        ow_head.addStretch(1)
        # Phase 10D — drop the synthetic "of 14" denominator. The
        # caller passes max 3 rows; the count is just "3 active"
        # so the surface stops faking a larger queue.
        count = QLabel(f"{len(other_work)} active")
        count.setFont(_font(_FONT.MONO, size=T.FS_EYEBROW,
                            letter_spacing=6.0))
        count.setStyleSheet(
            f"color: {T.INK_DIM}; background: transparent;")
        ow_head.addWidget(count)
        outer.addLayout(ow_head)

        # rows
        for idx, ow in enumerate(other_work):
            row = OtherRow(ow)
            row.clicked.connect(
                lambda _b=False, i=idx: self.row_clicked.emit(i))
            outer.addWidget(row)


# ── Search view ───────────────────────────────────────────────────


@dataclass
class SearchResultRow:
    glyph: str
    title: str
    meta: str
    score: int
    selected: bool = False


@dataclass
class SearchGroupSpec:
    label: str
    rows: List[SearchResultRow]


class _SearchGroupLabel(QLabel):
    def __init__(self, label: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(label, parent)
        self.setFont(_font(_FONT.MONO, size=T.FS_MONO_SM,
                           letter_spacing=14.0, bold=True))
        self.setStyleSheet(
            f"color: {T.INK_FAINT}; background: transparent;"
            f"padding: 6px 12px 4px;")


class _SearchResultRow(QWidget):
    clicked = pyqtSignal()

    def __init__(self, row: SearchResultRow,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._row = row
        self._hover = False
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 0, 12, 0)
        outer.setSpacing(10)
        glyph_color = T.ACCENT if row.selected else T.INK_MUTED
        outer.addWidget(Glyph(row.glyph, size=13, color=glyph_color))
        title = QLabel(row.title)
        title.setFont(_font(_FONT.SANS, size=T.FS_ROW_TITLE,
                            bold=row.selected, letter_spacing=-0.5))
        title.setStyleSheet(f"color: {T.INK}; background: transparent;")
        outer.addWidget(title, 1)
        meta = QLabel(row.meta)
        meta.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                           letter_spacing=4.0))
        meta.setStyleSheet(f"color: {T.INK_DIM}; background: transparent;")
        outer.addWidget(meta)
        score = QLabel(str(row.score))
        score.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                            bold=True, letter_spacing=2.0))
        score.setStyleSheet(
            f"color: {T.ACCENT if row.selected else T.INK_FAINT};"
            f"background: transparent;")
        score.setFixedWidth(24)
        score.setAlignment(Qt.AlignmentFlag.AlignRight
                           | Qt.AlignmentFlag.AlignVCenter)
        outer.addWidget(score)

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        if not self._row.selected:
            self._hover = True
            self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        if self._row.selected:
            path = _rounded_path(rect, 9)
            p.fillPath(path, _qcolor("rgba(167, 139, 250, 0.12)"))
            # left rail
            rail = QRectF(rect.x(), rect.y() + 8,
                          2.0, rect.height() - 16)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(_qcolor(T.ACCENT))
            p.drawRoundedRect(rail, 1.5, 1.5)
        elif self._hover:
            path = _rounded_path(rect, 9)
            p.fillPath(path, QColor(T.CARD_HOVER))
        p.end()


class _MiniPreviewPane(QWidget):
    """Search-state right column, 224 px wide. Investigation
    eyebrow pill, title, four faint preview lines, two chips,
    Resume button."""

    resume_clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(224)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,
                           QSizePolicy.Policy.Expanding)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        eyebrow = QLabel("PREVIEW")
        eyebrow.setFont(_font(_FONT.MONO, size=T.FS_MONO_SM,
                              letter_spacing=14.0))
        eyebrow.setStyleSheet(
            f"color: {T.INK_FAINT}; background: transparent;")
        outer.addWidget(eyebrow)

        # investigation pill
        pill = QWidget()
        pl = QHBoxLayout(pill)
        pl.setContentsMargins(7, 3, 7, 3)
        pl.setSpacing(7)
        dot = _AccentDot()
        pl.addWidget(dot)
        plbl = QLabel("INVESTIGATION")
        plbl.setFont(_font(_FONT.MONO, size=T.FS_MONO_SM,
                           letter_spacing=4.0))
        plbl.setStyleSheet(
            f"color: {T.ACCENT}; background: transparent;")
        pl.addWidget(plbl)
        pl.addStretch(1)
        pill.setStyleSheet(
            "background: rgba(167, 139, 250, 0.10);"
            "border: 1px solid rgba(167, 139, 250, 0.22);"
            "border-radius: 5px;")
        pill.setSizePolicy(QSizePolicy.Policy.Fixed,
                           QSizePolicy.Policy.Fixed)
        outer.addWidget(pill, 0, Qt.AlignmentFlag.AlignLeft)

        # title
        title = QLabel("WebSocket retry debugging")
        title.setFont(_font(_FONT.SANS, size=14, bold=True,
                            letter_spacing=-1.4))
        title.setStyleSheet(
            f"color: {T.INK}; background: transparent;")
        title.setWordWrap(True)
        outer.addWidget(title)

        # preview lines
        for w, dim in [("92%", False), ("80%", False),
                       ("86%", True), ("64%", True)]:
            outer.addWidget(_PreviewLine(w, dim))

        outer.addSpacing(2)

        # chips
        chips = QHBoxLayout()
        chips.setSpacing(4)
        chips.addWidget(Chip("file", "2 files"))
        chips.addWidget(Chip("tab", "2 tabs"))
        chips.addStretch(1)
        outer.addLayout(chips)

        outer.addStretch(1)

        resume = PrimaryBtn("Resume", kbd="⏎", size="sm")
        resume.clicked.connect(self.resume_clicked.emit)
        outer.addWidget(resume, 0, Qt.AlignmentFlag.AlignLeft)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_CARD_SM)
        p.setClipPath(path)
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0.0, QColor(T.CARD_HI))
        grad.setColorAt(1.0, QColor(T.CARD))
        p.fillPath(path, QBrush(grad))
        corner = QRadialGradient(QPointF(rect.width(), 0), 60)
        corner.setColorAt(0.0, _qcolor("rgba(167, 139, 250, 0.20)"))
        corner.setColorAt(0.65, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(corner))
        p.setClipping(False)
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


class _AccentDot(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(11, 11)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        halo = QRadialGradient(QPointF(cx, cy), 5)
        halo.setColorAt(0.0, _qcolor(T.ACCENT_GLOW))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(QPointF(cx, cy), 5, 5)
        p.setBrush(_qcolor(T.ACCENT))
        p.drawEllipse(QPointF(cx, cy), 2.5, 2.5)
        p.end()


class _PreviewLine(QWidget):
    def __init__(self, width_pct: str, dim: bool,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(4)
        self._pct = float(width_pct.rstrip("%")) / 100.0
        self._dim = dim

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width() * self._pct
        color = QColor(255, 255, 255,
                       int((0.04 if self._dim else 0.08) * 255))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawRoundedRect(QRectF(0, 0, w, self.height()), 3, 3)
        p.end()


class SearchView(QWidget):
    """State 3 — grouped result list + mini preview pane.

    Default fixture matches the design's "websocket retry" example."""

    selection_changed = pyqtSignal(int)
    open_selected = pyqtSignal()

    def __init__(self,
                 groups: Optional[List[SearchGroupSpec]] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        groups = groups or [
            SearchGroupSpec("Investigation", [
                SearchResultRow("thread",
                                "WebSocket retry debugging",
                                "2 days · 5 events", 98, selected=True),
            ]),
            SearchGroupSpec("Files", [
                SearchResultRow("file", "retry-handler.ts",
                                "~/code/socket.io · 2d", 94),
                SearchResultRow("file",
                                "websocket-fallback-strategy.md",
                                "~/notes · 2d", 91),
            ]),
            SearchGroupSpec("Returns", [
                SearchResultRow("chat", "ChatGPT — retry semantics",
                                "4 visits · 3d", 89),
            ]),
            SearchGroupSpec("Events", [
                SearchResultRow("tab",
                                "socket.io reconnect logic",
                                "stackoverflow · 5d", 84),
            ]),
        ]
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(10)

        # results list column
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        for g in groups:
            col.addWidget(_SearchGroupLabel(g.label))
            for r in g.rows:
                row = _SearchResultRow(r)
                col.addWidget(row)
        col.addStretch(1)

        col_w = QWidget()
        col_w.setLayout(col)
        outer.addWidget(col_w, 1)

        # mini preview pane
        outer.addWidget(_MiniPreviewPane())


# ── Resume state ──────────────────────────────────────────────────


@dataclass
class RestoredItem:
    glyph: str
    label: str
    meta: str
    status: str             # "opened" | "restored"


class _CheckDisc(QWidget):
    """44-px lavender disc with a white check mark."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(60, 60)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        # outer halo
        halo = QRadialGradient(QPointF(cx, cy), 30)
        halo.setColorAt(0.0, _qcolor("rgba(167, 139, 250, 0.55)"))
        halo.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(QPointF(cx, cy), 30, 30)
        # ring
        ring_pen = QPen(_qcolor("rgba(167, 139, 250, 0.45)"))
        ring_pen.setWidthF(1.0)
        p.setPen(ring_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), 22, 22)
        # disc gradient
        disc = QLinearGradient(cx, cy - 22, cx, cy + 22)
        disc.setColorAt(0.0, QColor("#B79AFF"))
        disc.setColorAt(1.0, QColor(T.ACCENT_DEEP))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(disc))
        p.drawEllipse(QPointF(cx, cy), 22, 22)
        # check mark
        p.translate(cx - 14, cy - 14)
        _draw_glyph_check(p, 28, QColor("#0A0810"))
        p.end()


class _RestoredRow(QWidget):
    def __init__(self, item: RestoredItem,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(34)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 4, 12, 4)
        outer.setSpacing(12)
        outer.addWidget(Glyph(item.glyph, size=12, color=T.ACCENT))
        label = QLabel(item.label)
        label.setFont(_font(_FONT.SANS, size=12.5, letter_spacing=-0.5))
        label.setStyleSheet(f"color: {T.INK}; background: transparent;")
        outer.addWidget(label, 1)
        meta = QLabel(item.meta)
        meta.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                           letter_spacing=4.0))
        meta.setStyleSheet(f"color: {T.INK_DIM}; background: transparent;")
        outer.addWidget(meta)
        status = QLabel(item.status.upper())
        status.setFont(_font(_FONT.MONO, size=T.FS_MONO_SM + 0.5,
                             bold=True, letter_spacing=10.0))
        status.setStyleSheet(
            f"color: {T.ACCENT}; background: transparent;")
        status.setFixedWidth(64)
        status.setAlignment(Qt.AlignmentFlag.AlignRight
                            | Qt.AlignmentFlag.AlignVCenter)
        outer.addWidget(status)


class ResumeView(QWidget):
    """State 4 — restoration confirmation."""

    undo_clicked = pyqtSignal()
    done_clicked = pyqtSignal()

    def __init__(self,
                 *,
                 items: Optional[List[RestoredItem]] = None,
                 title_main: str = "WebSocket retry debugging is",
                 title_accent: str = "open again.",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        items = items or [
            RestoredItem("file", "retry-handler.ts",
                         "~/code/socket.io", "opened"),
            RestoredItem("file", "websocket-fallback-strategy.md",
                         "~/notes", "opened"),
            RestoredItem("tab",
                         "github.com/socket.io · PR #482",
                         "browser · new window", "restored"),
            RestoredItem("tab",
                         "stackoverflow · reconnect logic",
                         "browser · new window", "restored"),
            RestoredItem("chat", "ChatGPT — retry semantics",
                         "session resumed", "opened"),
        ]
        outer = QVBoxLayout(self)
        outer.setContentsMargins(22, 20, 22, 16)
        outer.setSpacing(14)

        # header row
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(14)
        header.addWidget(_CheckDisc(), 0,
                         Qt.AlignmentFlag.AlignTop)
        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(3)
        em = QLabel("RESTORED")
        em.setFont(_font(_FONT.MONO, size=T.FS_EYEBROW,
                         letter_spacing=18.0, bold=True))
        em.setStyleSheet(f"color: {T.ACCENT}; background: transparent;")
        title_col.addWidget(em)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)
        title_lbl = QLabel(title_main + " ")
        title_lbl.setFont(_font(_FONT.SANS, size=T.FS_RESUME_TITLE,
                                bold=True, letter_spacing=-1.6))
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent;")
        title_row.addWidget(title_lbl)
        title_accent_lbl = _ServifGradientLabel(
            title_accent,
            font=_font(_FONT.SERIF, size=T.FS_RESUME_TITLE + 3,
                       italic=True, letter_spacing=-1.4),
        )
        title_row.addWidget(title_accent_lbl)
        title_row.addStretch(1)
        title_col.addLayout(title_row)
        header.addLayout(title_col, 1)
        stats_col = QVBoxLayout()
        stats_col.setContentsMargins(0, 0, 0, 0)
        stats_col.setSpacing(2)
        stats_col.addStretch(1)
        items_lbl = QLabel(f"{len(items)} ITEMS")
        items_lbl.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                                letter_spacing=6.0))
        items_lbl.setStyleSheet(
            f"color: {T.INK_MUTED}; background: transparent;")
        items_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_lbl = QLabel("0.4 SECONDS")
        time_lbl.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                               letter_spacing=6.0))
        time_lbl.setStyleSheet(
            f"color: {T.INK_DIM}; background: transparent;")
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        stats_col.addWidget(items_lbl)
        stats_col.addWidget(time_lbl)
        stats_col.addStretch(1)
        header.addLayout(stats_col)
        outer.addLayout(header)

        # restored list container
        list_w = _RestoredListContainer()
        list_layout = QVBoxLayout(list_w)
        list_layout.setContentsMargins(6, 6, 6, 6)
        list_layout.setSpacing(0)
        for it in items:
            list_layout.addWidget(_RestoredRow(it))
        list_layout.addStretch(1)
        outer.addWidget(list_w, 1)

        # footer row
        foot = QHBoxLayout()
        foot.setContentsMargins(2, 0, 2, 0)
        foot.setSpacing(0)
        last_active = QLabel("last active during implementation")
        last_active.setFont(_font(_FONT.MONO, size=T.FS_MONO + 0.5,
                                  letter_spacing=4.0))
        last_active.setStyleSheet(
            f"color: {T.INK_DIM}; background: transparent;")
        foot.addWidget(last_active)
        foot.addStretch(1)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(T.GAP_BTN)
        undo = GhostBtn("Undo", size="sm")
        undo.clicked.connect(self.undo_clicked.emit)
        done = PrimaryBtn("Done", kbd="⏎", size="sm")
        done.clicked.connect(self.done_clicked.emit)
        btn_row.addWidget(undo)
        btn_row.addWidget(done)
        foot.addLayout(btn_row)
        outer.addLayout(foot)


class _RestoredListContainer(QWidget):
    """Rounded dark container behind the list of restored rows."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = _rounded_path(rect, T.RADIUS_CARD_SM)
        p.fillPath(path, QColor(T.CARD))
        pen = QPen(_qcolor(T.LINE))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()


# ── DarkLauncher: the four-state assembly ─────────────────────────


class DarkLauncher(QWidget):
    """760 x 520 dark launcher window.

    Composition:
      Frame
        SearchBar (state-dependent)
        QStackedWidget [EmptyView, RecoveryView, SearchView, ResumeView]
        Footer (state-dependent text)
    """

    state_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(FRAME_W, FRAME_H)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._frame = Frame()
        layout.addWidget(self._frame)
        self._state = STATE_EMPTY
        self._view = EmptyView()
        self._search = SearchBar(with_caret=True)
        self._frame.set_search_bar(self._search)
        self._frame.set_content(self._view)
        self._frame.set_footer(Footer(
            right_text="PRESS ⌃ SPACE ANYWHERE"))

    def set_state(self, state: str,
                  *,
                  recovery: Optional[RecoveryProps] = None,
                  preview: Optional[PreviewProps] = None,
                  other_work: Optional[List[OtherWorkRow]] = None,
                  search_groups: Optional[List[SearchGroupSpec]] = None,
                  restored_items: Optional[List[RestoredItem]] = None,
                  ) -> None:
        if state == STATE_EMPTY:
            self._set_empty()
        elif state == STATE_RECOVERY:
            self._set_recovery(recovery=recovery, preview=preview,
                               other_work=other_work)
        elif state == STATE_SEARCH:
            self._set_search(search_groups=search_groups)
        elif state == STATE_RESUME:
            self._set_resume(items=restored_items)
        else:
            raise ValueError(f"unknown state: {state}")
        self._state = state
        self.state_changed.emit(state)

    def state(self) -> str:
        return self._state

    def search_bar(self) -> SearchBar:
        return self._search

    # state assemblers ----------------------------------------------

    def _set_empty(self) -> None:
        self._search = SearchBar(with_caret=True)
        self._frame.set_search_bar(self._search)
        view = EmptyView()
        self._frame.set_content(view)
        self._view = view
        self._frame.set_footer(Footer(
            right_text="PRESS ⌃ SPACE ANYWHERE"))

    def _set_recovery(self, *,
                      recovery: Optional[RecoveryProps],
                      preview: Optional[PreviewProps],
                      other_work: Optional[List[OtherWorkRow]]) -> None:
        self._search = SearchBar()
        self._frame.set_search_bar(self._search)
        view = RecoveryView(recovery=recovery, preview=preview,
                            other_work=other_work)
        self._frame.set_content(view)
        self._view = view
        self._frame.set_footer(Footer(
            right_text="⏎ RESUME · ↑↓ MOVE · ESC CLOSE"))

    def _set_search(self, *,
                    search_groups: Optional[List[SearchGroupSpec]]) -> None:
        self._search = SearchBar(value="websocket retry",
                                 with_caret=True, results=11)
        self._frame.set_search_bar(self._search)
        view = SearchView(groups=search_groups)
        self._frame.set_content(view)
        self._view = view
        self._frame.set_footer(Footer(
            right_text="↑↓ MOVE · ⏎ OPEN · ESC CLOSE"))

    def _set_resume(self, *,
                    items: Optional[List[RestoredItem]]) -> None:
        self._search = SearchBar()
        self._frame.set_search_bar(self._search)
        view = ResumeView(items=items)
        self._frame.set_content(view)
        self._view = view
        self._frame.set_footer(Footer(
            right_text="RECALL HAS HANDED CONTROL BACK TO YOU"))


__all__ = [
    "FRAME_W", "FRAME_H",
    "STATE_EMPTY", "STATE_RECOVERY", "STATE_SEARCH", "STATE_RESUME",
    "DarkLauncher",
    "Frame", "SearchBar", "Footer",
    "PrimaryBtn", "GhostBtn", "Chip", "Kbd",
    "EmptyView", "RecoveryView", "SearchView", "ResumeView",
    "RecoveryProps", "PreviewProps", "OtherWorkRow",
    "SearchGroupSpec", "SearchResultRow", "RestoredItem",
]
