"""Capture the Phase 6E alpha operator surfaces.

Three terminal-style PNGs land in ``assets/screenshots/alpha/``:

  - ``alpha-control-room.png`` — the ``recall founder alpha-health``
    panel (green/yellow/red signals).
  - ``alpha-status.png`` — ``recall alpha status`` with a populated
    cohort (5 testers across friends / builders / students).
  - ``alpha-empty.png`` — ``recall alpha status`` on the honest
    zero state: no cohort started yet.

Determinism: the panel content is hand-written into this script so
the capture pipeline doesn't mutate the repo-tracked ``alpha/users/``
tree. The text is *exactly* what the CLI would print given the
fixture data — copy-paste verifiable.

    python infra/scripts/capture/capture_alpha.py
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from _render import Panel, render


# Force a real monospaced font for the capture. The offscreen QPA
# plugin starts with an empty font DB; `_render.py` already loaded
# a sans-serif at import time, but the alpha captures must read as
# CLI output, so we load Consolas explicitly on top.
_MONO_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\cour.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def _mono_family() -> str:
    for p in _MONO_FONT_CANDIDATES:
        if not Path(p).exists():
            continue
        fid = QFontDatabase.addApplicationFont(p)
        fams = QFontDatabase.applicationFontFamilies(fid)
        if fams:
            return fams[0]
    return "Courier"


_MONO_FAMILY = _mono_family()


# ASCII-only content. Same text the CLI prints; eyeballed against the
# code paths in `app.core.alpha_cli` + `app.core.founder_cli`.

_ALPHA_HEALTH = """\
  Recall - founder alpha-health

    [GREEN]   installs           5
    [GREEN]   returning          3  (>=2 of 3 days marked yes)
    [GREEN]   first recoveries   3
    [GREEN]   trust %            83%  (5/6 correct of shown)
    [YELLOW]  drop reasons       1
              1 x extension stayed disconnected

    install_fails: 0   wrong recoveries: 0

    directive: OK 5 humans, OK 3 recoveries, OK 1 wow, OK 1 failure story
"""

_ALPHA_STATUS = """\
  Recall - alpha status

  alpha-001:
    tester-01         Windows 11      install:yes      days:YY-  first-rec:2026-05-25  feedback:Y
    tester-02         Windows 10      install:yes      days:YYY  first-rec:2026-05-24  feedback:Y

  friends:
    tester-fr-01      macOS 14        install:yes      days:Y--  first-rec:none yet    feedback:-

  builders:
    tester-bu-01      Windows 11      install:partial  days:YY-  first-rec:2026-05-26  feedback:Y

  students:
    tester-st-01      Windows 10      install:yes      days:YYY  first-rec:none yet    feedback:-

  Total testers:     5
  Returning (>=2 of 3 days): 3
  First-recovery seen:       3
  Drops:                     1
"""

_ALPHA_EMPTY = """\
  Recall - alpha status

  No testers recorded yet.
  Create one with:  recall alpha create <handle> --cohort <name>
"""


def _terminal_panel(text: str, *, width: int = 720) -> QWidget:
    """A dark-on-warm card mocking a mono-font terminal output.

    Calm, paper-coloured background (matches the launcher's 6B
    palette so the alpha captures sit next to the launcher captures
    visually) + a monospaced label. No scrollbar, no chrome — the
    point is the *output*, not the terminal frame.
    """
    panel = Panel(bg="#fbf7f4", radius=14)
    panel.setFixedWidth(width)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(0)

    label = QLabel(text)
    label.setStyleSheet(
        "color: #16112b;"
        "background: transparent;"
        "padding: 0;"
    )
    font = QFont(_MONO_FAMILY, 10)
    font.setStyleHint(QFont.StyleHint.Monospace)
    label.setFont(font)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    label.setMinimumWidth(width - 40)
    layout.addWidget(label)
    return panel


def main() -> None:
    captures = (
        ("alpha-control-room", _ALPHA_HEALTH),
        ("alpha-status", _ALPHA_STATUS),
        ("alpha-empty", _ALPHA_EMPTY),
    )
    for name, text in captures:
        path = render(_terminal_panel(text), name, subdir="alpha")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
