"""Capture the `recall doctor` output as a PNG - Phase 5G.

Runs the doctor CLI against the live daemon (or empty state if no
daemon is running) and renders the formatted text inside an
offscreen Qt widget styled like a terminal. The result is a real
deterministic capture of what a first user sees when they run
`recall doctor` from a Command Prompt.

    python infra/scripts/capture/capture_doctor.py
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from _render import ASSETS, app, render

from app.core.doctor import format_report, run_checks


_TERMINAL_QSS = """
QWidget#term_root {
  background: #0d1117;
  border-radius: 12px;
}
QLabel#term_text {
  color: #e6edf3;
  font-family: "Cascadia Mono", "Consolas", "Courier New", monospace;
  background: transparent;
  padding: 20px 28px;
}
"""


def _terminal(text: str) -> QWidget:
    root = QWidget()
    root.setObjectName("term_root")
    root.setStyleSheet(_TERMINAL_QSS)
    root.setMinimumWidth(720)

    col = QVBoxLayout(root)
    col.setContentsMargins(0, 0, 0, 0)

    lbl = QLabel(text)
    lbl.setObjectName("term_text")
    # Monospace font; size tuned to render comfortably at 2x.
    f = QFont()
    f.setFamily("Consolas")
    f.setPointSizeF(11.5)
    f.setStyleHint(QFont.StyleHint.Monospace)
    lbl.setFont(f)
    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    col.addWidget(lbl)

    return root


def main() -> None:
    _ = app()
    checks = run_checks()
    text = format_report(checks)
    widget = _terminal(text)
    path = render(widget, "doctor-output")
    print(f"  wrote {path.relative_to(ASSETS.parent.parent)}")


if __name__ == "__main__":
    main()
