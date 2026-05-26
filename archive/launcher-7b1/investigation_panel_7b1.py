"""Phase 7B.1 — Launcher Visual Merge · investigation stub.

The OTHER WORK list **is no longer rendered in the launcher**.
7B.1's single-focus design surfaces only the one *Continue
document* (or nothing). The classes below are preserved at a
hidden, zero-cost stub so:

  - The engine + API contracts stay live (`InvestigationCardV3`
    is constructed by `LiveLauncher._thread_to_v3`, in case a
    future surface wants to render the list).
  - The keyboard layer in ``live.py`` can still ask the digest
    for ``self.row._titles`` without a `None` guard — the
    stub always returns an empty list.

Pre-7B.1 variant (the 44-px vertical list with hairline
dividers) lives at
``archive/launcher-raycast/investigation_panel_7b.py``.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget


class InvestigationCardV3(QWidget):
    """Stub — preserved so the engine path can keep constructing
    these objects, even though the launcher never renders them."""

    open_thread = pyqtSignal(str, str, str)

    HEIGHT = 0

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title
        # Zero-cost: no layout, no paint, no focus.
        self.setFixedHeight(0)
        self.setVisible(False)


class InvestigationList(QWidget):
    """Stub — `populate` ignores its input; `_titles` returns []."""

    activated = pyqtSignal(str, str, str)
    MAX_VISIBLE = 0

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(0)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setVisible(False)
        self._rows: List[InvestigationCardV3] = []

    @property
    def _titles(self) -> List[InvestigationCardV3]:
        return self._rows

    def populate(self, items: List[InvestigationCardV3]) -> None:
        # Discard the items — the launcher never renders OTHER WORK
        # in 7B.1. The engine still produces the data, just for
        # future consumers / the inspector / the trust review.
        for it in items:
            it.setParent(None)
        self._rows = []


# Back-compat alias.
InvestigationRow = InvestigationList


__all__ = [
    "InvestigationCardV3",
    "InvestigationList",
    "InvestigationRow",
]
