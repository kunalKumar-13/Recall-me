"""Phase 6P — Restore feedback toast.

A small 3-second pill that surfaces after a restore. The body is
either the list of restored target names (`Restored · backoff.py
· client.py · MDN`) or a calm failure line
(`Could not reopen 1 item · Continue anyway`).

No modal. No progress bar. No checkmarks.
"""

from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlparse

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from . import theme as T


DEFAULT_VISIBLE_MS = 3000
MAX_NAMES = 3


def _name_for(kind: str, target: str) -> str:
    """A short, recognisable label for a single restored target.

    - file path  → basename
    - URL        → host (with `www.` stripped) or "..." fallback
    """
    if not target:
        return "?"
    if kind == "path":
        cleaned = target.replace("\\", "/").rstrip("/")
        last = cleaned.rsplit("/", 1)[-1]
        return last or cleaned
    try:
        host = urlparse(target).hostname or target
    except ValueError:
        host = target
    if host.startswith("www."):
        host = host[4:]
    return host


class RestoreToast(QWidget):
    """The toast pill. Host calls `flash_success(...)` or
    `flash_failure(...)`; the widget shows + auto-hides after
    `DEFAULT_VISIBLE_MS`."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_SOFT_RADIUS)
        eff.setOffset(0, T.SHADOW_SOFT_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_SOFT_ALPHA))
        self.setGraphicsEffect(eff)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(14, 8, 14, 8)
        outer.setSpacing(8)

        self._label = QLabel("")
        f = QFont()
        f.setPointSizeF(T.FS_META)
        f.setBold(True)
        self._label.setFont(f)
        self._label.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
        )
        outer.addWidget(self._label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        self.hide()

    # ── public ──────────────────────────────────────────────────────

    def flash_success(
        self,
        restored_names: List[str],
        *,
        requested: int,
        missing: int,
    ) -> None:
        head = "Restored"
        if missing and restored_names:
            head = f"Restored {len(restored_names)} of {requested}"
        names = restored_names[:MAX_NAMES]
        if missing and not restored_names:
            self.flash_failure(missing)
            return
        body = "  ·  ".join([head] + names)
        if missing:
            body += f"  ·  {missing} missing"
        self._show(body)

    def flash_failure(self, missing: int) -> None:
        if missing <= 0:
            body = "Nothing to restore"
        elif missing == 1:
            body = "Could not reopen 1 item  ·  Continue anyway"
        else:
            body = f"Could not reopen {missing} items  ·  Continue anyway"
        self._show(body)

    def flash_no_engine(self) -> None:
        self._show("Could not reach the engine  ·  try again")

    # ── internal ────────────────────────────────────────────────────

    def _show(self, text: str) -> None:
        self._label.setText(text)
        self.adjustSize()
        self.show()
        self.raise_()
        self._timer.start(DEFAULT_VISIBLE_MS)

    # ── paint ───────────────────────────────────────────────────────

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        p.fillPath(path, QColor(T.BG_RAISED))
        from PyQt6.QtGui import QPen
        pen = QPen(QColor(228, 222, 214))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


__all__ = ["RestoreToast", "_name_for"]
