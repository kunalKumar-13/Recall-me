"""Phase 6L — minimal single-floating-surface launcher composition.

Replaces the 3-column shell from Phase 6I (archived to
``archive/launcher-v2/``) with a calm vertical stack:

    ┌────────────────────────────────────────────────┐
    │  search input                                   │   ← MinimalSearchBar
    ├────────────────────────────────────────────────┤
    │                                                 │
    │  CONTINUE                                       │
    │  WebSocket retry debugging          [HIGH]      │   ← Continue hero
    │  [2 tabs] [3 files] [2d gap]     [Resume 1]     │
    │                                                 │
    ├────────────────────────────────────────────────┤
    │  ACTIVE INVESTIGATIONS                          │
    │  ● WS retry · ● Proposal · ● RLHF · ● Healthcare│   ← Horizontal strip
    ├────────────────────────────────────────────────┤
    │  RECENT RETURNS                                 │
    │  ● yesterday — picked up WS retry               │   ← Recent returns
    │  ● Tue — RLHF research                          │
    ├────────────────────────────────────────────────┤
    │  ● local only · 127.0.0.1:4545 · no cloud       │   ← Trust line
    └────────────────────────────────────────────────┘

The directive's *understand in 5 seconds* rule shapes every choice:

- One primary CTA: Resume on the Continue card.
- Investigations are a *strip*, not a vertical column — at most 4
  visible; surplus rolls off rather than scrolling forever.
- Recent returns is a 2-3 line ambient strip, not a heatmap.
- No daemon / doctor / version / extension chips inside the
  launcher. System info lives in the founder control room.

Width clamped 760–860 px, single column, centred inside the
parent window. Outer gutter 32, between-section 24, inner card 14.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .investigation_panel import InvestigationCardV3
from .recovery_panel import RecoveryCardV3
from .surfaces import Pill, StatusDot, section_label


# ── search bar ────────────────────────────────────────────────────


class MinimalSearchBar(QWidget):
    """A single rounded input.

    Phase 6M.2 — capped at **640 px** wide and centred inside its
    parent (was full-width). The directive's recovery rule: the
    search input is a *utility*, not a page-wide hero — the
    Raycast / Arc launcher shape, not a Notion sidebar.
    """

    query_changed = pyqtSignal(str)

    MAX_WIDTH = 640

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Outer layout centres the input — left + right stretches push
        # the bar to the middle even when the parent column is wider
        # than `MAX_WIDTH`.
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Search investigations…")
        self._input.setFixedHeight(48)              # 6M.2 spec
        self._input.setMaximumWidth(self.MAX_WIDTH)
        # 6M.2 fix — keep a minimum width so the centering stretches
        # don't squeeze the placeholder text. The previous 0-min let
        # Qt size the input to its content (`Search investig…`).
        self._input.setMinimumWidth(360)
        self._input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: {T.BG_RAISED};"
            f"  color: {T.INK};"
            f"  border: 1px solid {T.HAIRLINE};"
            f"  border-radius: 16px;"               # 6M.2 spec
            f"  padding: 0 18px;"
            f"  font-size: {T.FS_BODY}px;"
            f"}}"
            f"QLineEdit:focus {{ border-color: {T.ACCENT_LINE}; }}"
        )
        self._input.textChanged.connect(self.query_changed.emit)
        layout.addWidget(self._input)
        layout.addStretch(1)

    def focus(self) -> None:
        self._input.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self._input.selectAll()


# ── horizontal investigations strip ──────────────────────────────


class _InvestigationPill(QWidget):
    """A single horizontal pill — title + small surface-count chip.

    Phase 6M.1 refinement: solid white fill (was translucent), 1-px
    soft-gray border, equal-width sizing managed by the parent
    strip. The pill's elided-text label keeps long thread titles
    from spilling into the next column.
    """

    activated = pyqtSignal(str, str, str)

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        *,
        surface_count: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        # Phase 6M.2 — height down to 44 (was 40); radius 14 in the
        # paint event. The pill is *slightly* taller so the row
        # bottom edge aligns with the new shorter hero card.
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        dot = StatusDot("accent")
        layout.addWidget(dot)

        label = QLabel(title)
        f = QFont()
        f.setPointSizeF(T.FS_TITLE - 1)             # 13 px after 6M.2 typography reduction
        f.setBold(True)
        label.setFont(f)
        label.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        label.setMinimumWidth(0)
        layout.addWidget(label, 1)

        if surface_count > 0:
            layout.addWidget(Pill(str(surface_count), kind="count"))

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPen
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        # Phase 6M.1 — solid white fill.
        p.fillPath(path, QColor(255, 255, 255, 255))
        pen = QPen(QColor(24, 17, 45, 24))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.activated.emit(self._tid, self._topic, self._title)

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.activated.emit(self._tid, self._topic, self._title)
            return
        super().keyPressEvent(e)


class _OverflowChip(QWidget):
    """The `+N more` chip the strip drops in when the cohort has more
    investigations than the 4-pill cap. Same shape as a pill so the
    row reads as 4 + 1 cards rather than 4 cards + an afterthought."""

    def __init__(self, count: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(80)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(0)
        lbl = QLabel(f"+{count} more")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSizeF(10.5)
        f.setBold(True)
        lbl.setFont(f)
        lbl.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
        )
        layout.addWidget(lbl, 1)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPen
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        # The overflow chip is a *dashed* hairline — visually quieter
        # than a real pill so the eye doesn't try to click it.
        from PyQt6.QtCore import Qt as _Qt
        pen = QPen(QColor(24, 17, 45, 28))
        pen.setStyle(_Qt.PenStyle.DashLine)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


class MinimalInvestigations(QWidget):
    """Horizontal strip of equal-width investigation pills.

    Phase 6M.1 refinement:

      - Pills *stretch* to fill the column equally (was flush-left).
      - Hard cap at 4 visible; surplus collapses into a single
        `+N more` chip so the strip never wraps and never scrolls.
      - The section label uses the directive's `FS_SECTION` size.
    """

    activated = pyqtSignal(str, str, str)

    # Phase 6M.2 — cap dropped to 3 (was 4). The recovery directive
    # explicitly: max 3 visible + `+N` overflow.
    MAX_VISIBLE = 3

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)
        outer.addWidget(section_label("Active investigations"))

        self._strip = QHBoxLayout()
        self._strip.setContentsMargins(0, 0, 0, 0)
        self._strip.setSpacing(T.CARD_GAP)
        outer.addLayout(self._strip)
        self._pills: List[_InvestigationPill] = []
        self._overflow: Optional[_OverflowChip] = None

    def populate(self, items: List[InvestigationCardV3]) -> None:
        # Clear prior pills + any overflow chip.
        for p in self._pills:
            self._strip.removeWidget(p)
            p.setParent(None)
        self._pills.clear()
        if self._overflow is not None:
            self._strip.removeWidget(self._overflow)
            self._overflow.setParent(None)
            self._overflow = None
        # Drain any trailing stretches left over from earlier
        # populate() calls.
        while self._strip.count():
            item = self._strip.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        visible = items[: self.MAX_VISIBLE]
        for card in visible:
            tid = getattr(card, "_tid", "")
            topic = getattr(card, "_topic", "")
            title = getattr(card, "_title", "")
            pill = _InvestigationPill(tid, topic, title, surface_count=0)
            pill.activated.connect(self.activated.emit)
            self._pills.append(pill)
            self._strip.addWidget(pill, 1)  # stretch=1 → equal width

        overflow_count = len(items) - len(visible)
        if overflow_count > 0:
            self._overflow = _OverflowChip(overflow_count)
            self._strip.addWidget(self._overflow, 0)


# ── recent returns ────────────────────────────────────────────────


class _ReturnRow(QWidget):
    """A single thin row: when (mono) · what.

    Phase 6M.2 — quieter than 6M.1: smaller mono when-label, 12-px
    body text, no leading dot. The row is *ambient*, not a card.
    """

    def __init__(
        self,
        when: str,
        what: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedHeight(22)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(10)

        w = QLabel(when)
        wf = QFont()
        wf.setPointSizeF(9.5)
        wf.setBold(True)
        w.setFont(wf)
        w.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
        )
        w.setFixedWidth(72)
        layout.addWidget(w)

        b = QLabel(what)
        b.setStyleSheet(
            f"color: {T.INK_3}; font-size: {T.FS_META}px;"  # 11
            f"background: transparent;"
        )
        layout.addWidget(b, 1)


class MinimalReturns(QWidget):
    """A short list of recent return events.

    Phase 6M.2 — quieter strip: **max 2 rows** (was 3), no header
    eyebrow, a single hairline divider above the rows. Hides
    itself when the list is empty (the directive's *hide if
    empty* rule).
    """

    MAX_ROWS = 2

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # 6M.2 — a single hairline above the rows. No section
        # label; the directive explicitly asks for the strip to
        # *feel ambient*, not labelled.
        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.Shape.HLine)
        self._divider.setStyleSheet(
            f"QFrame {{ border: none; background: {T.HAIRLINE}; max-height: 1px; }}"
        )
        self._divider.setFixedHeight(1)
        outer.addWidget(self._divider)

        self._wrap = QVBoxLayout()
        self._wrap.setContentsMargins(0, 4, 0, 0)
        self._wrap.setSpacing(0)
        outer.addLayout(self._wrap)
        self._rows: List[_ReturnRow] = []
        self.setVisible(False)

    def populate(self, items: List[tuple[str, str]]) -> None:
        """`items` is a small list of `(when, what)` pairs."""
        for r in self._rows:
            self._wrap.removeWidget(r)
            r.setParent(None)
        self._rows.clear()

        for when, what in items[: self.MAX_ROWS]:
            row = _ReturnRow(when, what)
            self._rows.append(row)
            self._wrap.addWidget(row)
        self.setVisible(len(self._rows) > 0)


# ── trust footer (slim) ──────────────────────────────────────────


class MinimalTrust(QLabel):
    """One quiet line. No surface, no shadow — just text."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("local only · 127.0.0.1:4545 · no cloud", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"color: {T.INK_4}; font-size: 10.5px;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"background: transparent; padding: 6px 0 0;"
        )


# ── empty surface (minimal) ───────────────────────────────────────


class MinimalEmpty(QWidget):
    """Phase 6M.1 — vertically-centred empty surface.

    The directive's exact shape:

      - lavender icon (the spark glyph the existing v2/v3 surfaces
        already use for the empty state)
      - headline: *Recall notices unfinished work.* (FS_HERO = 22)
      - sub: *Work normally. Return later. Recall fills itself.*
      - two buttons: Show example (primary) · Start normally
        (secondary)

    No surrounding card — the directive's *icon + text + buttons*
    list is laid out directly on the paper-white page, vertically
    centred. The Phase 6L card-wrapper was the source of the
    *dashboard* feeling that 6M.1 removes.
    """

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(18)
        outer.addStretch(1)

        # ── icon: accent-tinted square hosting a small lavender dot.
        # No glyph character — every system font has different
        # coverage, and rendering a Unicode glyph through an
        # offscreen Qt buffer drops to the replacement square when
        # the font lacks it. A painted dot is portable.
        icon_outer = QWidget()
        icon_outer.setFixedSize(48, 48)
        icon_outer.setStyleSheet(
            f"QWidget {{"
            f"  background: {T.ACCENT_SOFT};"
            f"  border-radius: 14px;"
            f"}}"
        )
        icon_dot = QLabel(icon_outer)
        icon_dot.setFixedSize(14, 14)
        icon_dot.move(17, 17)  # centered inside the 48×48 square
        icon_dot.setStyleSheet(
            f"QLabel {{"
            f"  background: {T.ACCENT};"
            f"  border-radius: 7px;"
            f"}}"
        )
        icon_row = QHBoxLayout()
        icon_row.addStretch(1)
        icon_row.addWidget(icon_outer)
        icon_row.addStretch(1)
        outer.addLayout(icon_row)

        headline = QLabel("Recall notices unfinished work.")
        hf = QFont()
        hf.setPointSizeF(T.FS_HERO)  # 22 (Phase 6M.1)
        hf.setBold(True)
        headline.setFont(hf)
        headline.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(headline)

        sub = QLabel("Work normally. Return later. Recall fills itself.")
        sub.setStyleSheet(
            f"color: {T.INK_2}; font-size: {T.FS_BODY}px;"
            f"background: transparent;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        outer.addWidget(sub)

        # Phase 6N — *Preview card*. A small, non-interactive
        # RecoveryCardV3 rendered with the demo fixture's exact
        # title + evidence chips, so the empty state shows what
        # a real recovery will look like the moment one exists.
        # The card is *visual only* (the directive's exact words):
        # no `restore` handler is wired, the pill is rendered as
        # the LOW-state ghost, and a small *PREVIEW* tag sits in
        # the top-right corner so the user can't mistake it for
        # live data. The card disappears automatically the moment
        # the launcher swaps from MinimalEmpty to MinimalDigest —
        # which happens the instant the engine reports a real
        # event count > 0.
        preview_wrap = QHBoxLayout()
        preview_wrap.addStretch(1)
        preview = self._build_preview_card()
        preview_wrap.addWidget(preview)
        preview_wrap.addStretch(1)
        outer.addSpacing(8)
        outer.addLayout(preview_wrap)
        outer.addSpacing(4)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch(1)
        from PyQt6.QtWidgets import QPushButton
        primary = QPushButton("Show example")
        primary.setCursor(Qt.CursorShape.PointingHandCursor)
        primary.setFixedHeight(38)
        primary.setStyleSheet(
            f"QPushButton {{"
            f"  background: {T.ACCENT_SOFT};"
            f"  color: {T.ACCENT};"
            f"  border: 1px solid {T.ACCENT_LINE};"
            f"  border-radius: 12px;"
            f"  padding: 0 20px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 600;"
            f"}}"
            f"QPushButton:hover {{ background: rgba(139, 127, 227, 50); }}"
        )
        primary.clicked.connect(self.show_example.emit)
        secondary = QPushButton("Start normally")
        secondary.setCursor(Qt.CursorShape.PointingHandCursor)
        secondary.setFixedHeight(38)
        secondary.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {T.INK_3};"
            f"  border: 1px solid {T.HAIRLINE};"
            f"  border-radius: 12px;"
            f"  padding: 0 18px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
        )
        secondary.clicked.connect(self.start_normally.emit)
        buttons.addWidget(primary)
        buttons.addWidget(secondary)
        buttons.addStretch(1)
        outer.addLayout(buttons)

        outer.addWidget(MinimalTrust())
        outer.addStretch(2)

    # ── Phase 6N — preview card builder ────────────────────────

    def _build_preview_card(self) -> QWidget:
        """A faded, non-interactive recovery preview. The directive's
        canonical fixture (*WebSocket retry debugging · 2 tabs · 2
        files · returned after 2d*) rendered through the same
        `RecoveryCardV3` widget the live launcher uses — so the
        empty state's preview is a *literal* preview, not an
        illustration.

        The card is dressed down:

          - its `signal` is forced to `low` (ghost CTA + plain white
            fill so the eye doesn't try to click);
          - a small *PREVIEW* caption sits *above* the card so the
            surface can't be mistaken for live data;
          - the card is clamped to ~440 px so it doesn't compete
            with the buttons below;
          - the `restore` signal is intentionally **not connected** —
            clicking does nothing.
        """
        wrap = QWidget()
        wrap.setMaximumWidth(440)
        wrap.setMinimumWidth(360)
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        caption = QLabel("PREVIEW")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet(
            f"color: {T.INK_4};"
            f"font-size: 9px;"
            f"font-weight: 600;"
            f"letter-spacing: 1.4px;"
            f"background: transparent;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
        )
        layout.addWidget(caption)

        card = RecoveryCardV3(
            candidate_id="preview",
            title="WebSocket retry debugging",
            evidence="2 tabs · 2 files · reopened after a 2-day gap",
            time_label="preview",
            confidence="low",
            signal="low",
            sentence="A real recovery will replace this",
            n_targets=4,
        )
        # Strip interactivity — the preview is *visual only*.
        card.setEnabled(False)
        card.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        card.setCursor(Qt.CursorShape.ArrowCursor)
        card.setMaximumWidth(440)
        layout.addWidget(card)
        return wrap


# ── populated body ────────────────────────────────────────────────


class MinimalDigest(QWidget):
    """The single-column populated body.

    Phase 6M.2 — the directive's exact vertical rhythm:

        Hero
        ↕ 16  (CARD_GAP between hero and investigations)
        Investigations
        ↕ 12  (CARD_GAP, but tighter than between)
        Returns
        ↕ 8   (RETURNS_GAP — quiet strip at the very bottom)
        Trust

    Explicit `addSpacing()` calls between widgets rather than
    one global `setSpacing()` because the rhythm isn't uniform.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Continue hero slot (filled by `populate`).
        self._hero_wrap = QVBoxLayout()
        self._hero_wrap.setContentsMargins(0, 0, 0, 0)
        self._hero_wrap.setSpacing(0)
        layout.addLayout(self._hero_wrap)
        self._hero: Optional[RecoveryCardV3] = None

        # 6M.2 spec: 16 px between hero and investigations.
        layout.addSpacing(T.SECTION_GAP)

        self.investigations = MinimalInvestigations()
        layout.addWidget(self.investigations)

        # 6M.2 spec: 12 px between investigations and returns.
        layout.addSpacing(T.CARD_GAP)

        self.returns = MinimalReturns()
        layout.addWidget(self.returns)

        layout.addStretch(1)

        # 6M.2 spec: 8 px between returns and trust.
        layout.addSpacing(T.RETURNS_GAP)
        layout.addWidget(MinimalTrust())

    def populate(
        self,
        *,
        hero: Optional[RecoveryCardV3],
        investigations: List[InvestigationCardV3],
        returns: List[tuple[str, str]] = (),
    ) -> None:
        # Hero swap.
        if self._hero is not None:
            self._hero_wrap.removeWidget(self._hero)
            self._hero.setParent(None)
            self._hero = None
        if hero is not None:
            self._hero = hero
            self._hero_wrap.addWidget(hero)
        self.investigations.populate(investigations)
        self.returns.populate(list(returns))


# ── shell + window ────────────────────────────────────────────────


class MinimalShell(QWidget):
    """The single-column compact shell.

    Phase 6M.2 geometry — the directive's *recovery* values:

      - column **min/max 600** (clamped at the inner content width;
        the previous 760-px column was the regression)
      - outer padding **20** (was 28)
      - section gap **16** (was 20)
      - window default **720 × 520** (set by `MinimalWindow`;
        was 820 × 640)

    Everything aligns to that grid; nothing in the launcher uses an
    ad-hoc gutter or one-off margin. The shell now reads as a
    Raycast / Arc utility, not a Notion-shaped page.
    """

    MIN_WIDTH = 520
    MAX_WIDTH = 640

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 20 px top / bottom (directive); horizontal stretch absorbs
        # the remaining width.
        outer = QHBoxLayout(self)
        outer.setContentsMargins(T.GUTTER, T.GUTTER, T.GUTTER, T.GUTTER)
        outer.setSpacing(0)
        outer.addStretch(1)

        column = QWidget()
        column.setMinimumWidth(self.MIN_WIDTH)
        column.setMaximumWidth(self.MAX_WIDTH)
        cl = QVBoxLayout(column)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(T.SECTION_GAP)

        self.search = search or MinimalSearchBar()
        cl.addWidget(self.search)

        cl.addWidget(center, 1)

        outer.addWidget(column)
        outer.addStretch(1)


class MinimalWindow(QWidget):
    """Top-level compact QWidget. Paper-white page background, a
    single rounded outer edge so the surface reads as a *card* even
    in a borderless capture.

    Phase 6M.2 — default size **720 × 520** (was 820 × 640). Max
    **760 × 560** (the directive's cap). Centered inside the parent
    screen by the live launcher's ``show_centered()``.
    """

    DEFAULT_SIZE = (720, 520)
    MAX_SIZE = (760, 560)

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("launcher_v3_window")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.resize(*self.DEFAULT_SIZE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._shell = MinimalShell(center, search=search)
        layout.addWidget(self._shell)

    @property
    def shell(self) -> MinimalShell:
        return self._shell

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # Phase 6M.2 — outer window radius down to 24 (was 28).
        path.addRoundedRect(QRectF(self.rect()), 24, 24)
        p.fillPath(path, QColor(T.BG))
        p.end()


__all__ = [
    "MinimalSearchBar",
    "MinimalInvestigations",
    "MinimalReturns",
    "MinimalTrust",
    "MinimalEmpty",
    "MinimalDigest",
    "MinimalShell",
    "MinimalWindow",
]
