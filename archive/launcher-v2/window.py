"""Phase 6I — top-level v3 window.

A `QWidget` that hosts the warm-white page background + the Shell.
The directive's *floating* feel comes from the page colour leaking
around the columns; the columns paint themselves on top with
translucent white surfaces.

Callers (the capture pipeline + a future live wire-up) build their
own DigestColumn / EmptyDigest / SearchPanel and hand it to the
window via `set_center`. The window owns *layout only*.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from . import theme as T
from .shell import ContextColumn, Shell
from .sidebar import Sidebar


class LauncherWindow(QWidget):
    """The v3 window. Warm-white page background, single Shell child."""

    DEFAULT_SIZE = (1100, 720)

    def __init__(
        self,
        center: QWidget,
        *,
        sidebar: Optional[Sidebar] = None,
        context: Optional[ContextColumn] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("launcher_v3_window")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.resize(*self.DEFAULT_SIZE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._shell = Shell(center, sidebar=sidebar, context=context)
        layout.addWidget(self._shell)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        # Paint the warm-white page background. The shell + columns
        # paint themselves on top with translucent surfaces, so the
        # outermost paint is just the page colour with a soft
        # rounded edge (24-px) so the window reads as a *floating
        # card* even in a borderless capture.
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 24, 24)
        p.fillPath(path, QColor(T.BG))
        p.end()


__all__ = ["LauncherWindow"]
