"""Phase 6I — RecoveryCardV3 + RecoveryPanel.

The directive's card spec:

  - title          (15 px, semibold, ink)
  - chip row       [2 tabs] [3 files] [returned after 2d]
  - confidence     badge (high / medium / low), right-aligned
  - Resume CTA     accent-filled pill with the `1` shortcut chip
  - hover lift     ≤ 2 px Y translate, soft drop deepens 1 step
  - focus ring     2 px accent ring inset
  - keyboard nav   Enter / Space → emit `restore`

The card is *taller* than v2's 76 px because chips + a real CTA pill
no longer share a single row. Spec: ~108-116 px.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, QEvent, pyqtSignal
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
from .surfaces import (
    ConfidenceBadge,
    Pill,
    TimelineChip,
    section_label,
)


# ── chip-row parser ───────────────────────────────────────────────


def parse_evidence_chips(evidence: str) -> List[Tuple[str, str]]:
    """Mirror of `app/ui/cards.py:_parse_evidence_chips`. Splits the
    engine's deterministic ``2 tabs · 3 files · reopened after a 2-day
    gap`` caption into chip labels.

    Each return tuple is ``(label, kind)`` where ``kind`` is one of
    ``count`` (tabs / files / chats) or ``time`` (the gap chip). The
    parser never invents data; an empty input returns an empty list.
    """
    if not evidence:
        return []
    out: List[Tuple[str, str]] = []
    for raw in evidence.split("·"):
        s = raw.strip()
        if not s:
            continue
        if "reopened after" in s.lower():
            # Compress "reopened after a 2-day gap" -> "2d gap"
            tail = s.lower().rsplit("after", 1)[-1].strip().strip("a ").strip()
            tail = (
                tail.replace("-day gap", "d gap")
                    .replace(" days gap", "d gap")
                    .replace(" day gap", "d gap")
                    .replace(" hours ago", "h ago")
            )
            out.append((tail, "time"))
        elif s.endswith("ago") or "ago" in s:
            out.append((s.replace(" ago", "h ago"), "time"))
        else:
            out.append((s, "count"))
    return out


# ── card widget ───────────────────────────────────────────────────


class _ResumePill(QWidget):
    """The CTA on the right of the card. Phase 6N adds three
    variants tied to the recovery's *signal* strength:

      - ``resume``   accent-filled (HIGH) — the user should act
      - ``continue`` accent-soft fill   (MED) — softer invite
      - ``review``   ghost / hairline   (LOW) — explicitly *review*

    Each variant carries the directive's exact verb. The keyboard-
    shortcut chip (`1`) stays the same across variants because the
    Enter / `1` activation contract is the same.
    """

    KIND_VERBS = {
        "resume": "Resume",
        "continue": "Continue",
        "review": "Review",
    }

    def __init__(
        self,
        *,
        kind: str = "resume",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._kind = kind if kind in self.KIND_VERBS else "resume"
        # Phase 6M.2 — the directive's *small pill, 36 px, not
        # giant* spec.
        self.setFixedHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(8)

        # Foreground colour varies per kind — accent-filled buttons
        # take white; the review/ghost variant uses the accent ink.
        fg = "white" if self._kind == "resume" else (
            T.ACCENT if self._kind == "continue" else T.INK_2
        )

        label = QLabel(self.KIND_VERBS[self._kind])
        f = QFont()
        f.setPointSizeF(10.5)
        f.setBold(True)
        label.setFont(f)
        label.setStyleSheet(
            f"color: {fg}; background: transparent; padding: 0;"
        )
        layout.addWidget(label)

        chip_bg = (
            "rgba(255, 255, 255, 0.20)" if self._kind == "resume"
            else "rgba(139, 127, 227, 0.18)" if self._kind == "continue"
            else "rgba(24, 17, 45, 0.06)"
        )
        chip = QLabel("1")
        chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip.setFixedSize(20, 20)
        chip.setStyleSheet(
            f"QLabel {{"
            f"  background: {chip_bg};"
            f"  color: {fg};"
            f"  border-radius: 6px;"
            f"  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"  font-size: 11px;"
            f"  font-weight: 600;"
            f"}}"
        )
        layout.addWidget(chip)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPen
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        if self._kind == "resume":
            # HIGH — accent-filled, strongest invitation.
            p.fillPath(path, QColor(T.ACCENT))
        elif self._kind == "continue":
            # MED — accent-soft fill + accent border. Less weight,
            # still clearly clickable.
            p.fillPath(path, QColor(T.ACCENT_SOFT))
            pen = QPen(QColor(139, 127, 227, 96))
            pen.setWidthF(1.0)
            p.setPen(pen)
            p.drawPath(path)
        else:
            # LOW — ghost button. No fill, a hairline border only.
            # The user is encouraged to *look* before acting.
            pen = QPen(QColor(24, 17, 45, 36))
            pen.setWidthF(1.0)
            p.setPen(pen)
            p.drawPath(path)
        p.end()


class RecoveryCardV3(QWidget):
    """The directive's premium recovery surface.

    Layout (per the spec at the top of this module):

        ┌──────────────────────────────────────────────────────────┐
        │  Continue  ●                                       HIGH  │
        │                                                          │
        │  WebSocket retry debugging                               │
        │                                                          │
        │  [2 tabs]  [3 files]  [2d gap]            ┌────────────┐ │
        │                                           │ ▶ Resume 1 │ │
        │  surfaced because you left this mid-flow  └────────────┘ │
        └──────────────────────────────────────────────────────────┘

    Emits ``restore(candidate_id, title, n_targets)`` on Enter / Space
    / click — same signal name as the v2 RecoveryCard so a future
    promotion is a one-line consumer change.
    """

    restore = pyqtSignal(str, str, int)

    # Phase 6M.2 — 92 px is the directive's recovery height. The
    # card is *minimum* 92; Phase 6N may push it slightly past
    # that when a confidence sentence is shown (still capped at
    # HEIGHT + 32 = 124 to prevent dashboard sprawl).
    HEIGHT = 92

    # Default sentence per signal — the directive's exact strings.
    # Override at the call site when the engine produces a more
    # specific reason.
    DEFAULT_SENTENCES = {
        "high":   "Recall thinks this was interrupted work",
        "medium": "Seen again after return",
        "low":    "Weak signal — review first",
    }

    # Map signal → CTA verb. The widget accepts `signal` as the
    # canonical recovery semantics; `confidence` stays for the
    # right-hand pill colour.
    _CTA_FOR_SIGNAL = {
        "high":   "resume",
        "medium": "continue",
        "low":    "review",
    }

    def __init__(
        self,
        candidate_id: str,
        title: str,
        evidence: str,
        time_label: str,
        *,
        confidence: str = "high",
        signal: Optional[str] = None,
        sentence: Optional[str] = None,
        n_targets: int = 0,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cid = candidate_id
        self._title = title
        self._n = n_targets
        self._confidence = confidence
        # Phase 6N — *signal* drives the CTA verb (resume / continue /
        # review) and the card's accent strength. When not provided
        # explicitly, derive from `confidence` for backwards-compat
        # with the pre-6N construction sites.
        self._signal = (signal or confidence).lower()
        if self._signal not in self._CTA_FOR_SIGNAL:
            self._signal = "high"
        self._hover = False
        self._focused = False

        self.setMinimumHeight(self.HEIGHT)
        self.setMaximumHeight(self.HEIGHT + 32)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # ── shadow (soft only) ──
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_SOFT_RADIUS)
        eff.setOffset(0, 2)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_SOFT_ALPHA))
        self.setGraphicsEffect(eff)

        # Phase 6M.2 + 6N — 2×2 grid with an optional sentence row
        # tucked under the chip strip:
        #
        #   ┌─────────────────────────────────────┬──────────┐
        #   │  title (left)                       │  HIGH    │
        #   ├─────────────────────────────────────┼──────────┤
        #   │  [chips]                            │ [Resume] │
        #   ├──────────────────────────────────────┴──────────┤
        #   │  Recall thinks this was interrupted work       │  ← 6N
        #   └────────────────────────────────────────────────┘
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 14, 20, 12)
        outer.setSpacing(0)

        # ── top row: title left · confidence top-right ──
        top = QHBoxLayout()
        top.setSpacing(10)
        title_lbl = QLabel(title)
        tf = QFont()
        tf.setPointSizeF(T.FS_HERO - 2)              # 18
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
        )
        title_lbl.setWordWrap(False)
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top.addWidget(title_lbl, 1)
        top.addWidget(ConfidenceBadge(confidence))
        outer.addLayout(top)

        outer.addStretch(1)

        # ── bottom row: chips · CTA pill (variant per signal) ──
        bottom = QHBoxLayout()
        bottom.setSpacing(T.CHIP_GAP)
        chip_strip = QHBoxLayout()
        chip_strip.setSpacing(T.CHIP_GAP)
        # Phase 6N — cap at 3 chips (directive's *Max 3 chips* rule).
        # The parser is the only source; we never fabricate.
        chips_parsed = parse_evidence_chips(evidence)[:3]
        for label, kind in chips_parsed:
            chip_strip.addWidget(_chip_for(label, kind))
        chip_strip.addStretch(1)
        bottom.addLayout(chip_strip, 1)
        bottom.addWidget(_ResumePill(kind=self._CTA_FOR_SIGNAL[self._signal]))
        outer.addLayout(bottom)

        # ── confidence sentence (Phase 6N) ──
        sentence_text = sentence if sentence is not None else (
            self.DEFAULT_SENTENCES.get(self._signal, "")
        )
        if sentence_text:
            outer.addSpacing(8)
            self._sentence_lbl = QLabel(sentence_text)
            self._sentence_lbl.setStyleSheet(
                f"color: {T.INK_3}; background: transparent;"
                f"font-size: {T.FS_META}px;"
            )
            outer.addWidget(self._sentence_lbl)
        else:
            self._sentence_lbl = None

        self._time_label = time_label  # informational; v3 surfaces the gap as a chip

    # ── paint ──

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), T.RADIUS_HERO, T.RADIUS_HERO)
        # Phase 6N — fill strength varies by signal:
        #   HIGH   accent-soft   (strongest invitation)
        #   MED    soft cream    (lighter — visually quieter)
        #   LOW    plain white   (no tint — *look first*)
        if self._signal == "high":
            fill = QColor(T.ACCENT_SOFT)
        elif self._signal == "medium":
            # A halfway tint — accent-soft mixed with white. Hand-
            # picked to read as "still recovery, just less so".
            fill = QColor(245, 242, 252)
        else:  # low
            fill = QColor(T.BG_RAISED)
        p.fillPath(path, fill)
        # Border — accent line strength varies by signal too. The
        # focus ring overrides everything (2 px accent).
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        elif self._signal == "high":
            pen = QPen(QColor(139, 127, 227, 80))
            pen.setWidthF(1.0)
        elif self._signal == "medium":
            pen = QPen(QColor(139, 127, 227, 48))
            pen.setWidthF(1.0)
        else:  # low
            pen = QPen(QColor(24, 17, 45, 24))
            pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    # ── interaction ──

    def enterEvent(self, _e: QEvent) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e: QEvent) -> None:  # type: ignore[override]
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


def _chip_for(label: str, kind: str) -> QWidget:
    """Pick the right chip widget for a parsed chip. Time chips get
    the mono-font TimelineChip; counts get the plain accent Pill."""
    if kind == "time":
        return TimelineChip(label, accent=True)
    return Pill(label, kind="count")


# ── panel (column container) ──────────────────────────────────────


class RecoveryPanel(QWidget):
    """Wraps the section header + a column of RecoveryCardV3
    widgets. The main column composes one or more panels."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(T.CARD_GAP)
        self._cards: List[RecoveryCardV3] = []

        self._header = section_label("Continue where you left off")
        self._layout.addWidget(self._header)

    def add_card(self, card: RecoveryCardV3) -> None:
        self._cards.append(card)
        self._layout.addWidget(card)

    def clear(self) -> None:
        for c in self._cards:
            c.setParent(None)
        self._cards.clear()


__all__ = [
    "RecoveryCardV3",
    "RecoveryPanel",
    "parse_evidence_chips",
]
