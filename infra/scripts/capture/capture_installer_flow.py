"""Capture the installer flow as a PNG - Phase 5G.

The installer runs as a GUI wizard. Driving the wizard via UI
automation is brittle; for the alpha cycle the meaningful evidence
is *what the installer actually did* on this machine - timing,
target directory, icons created, exit status.

This script reads the silent-install log produced by
`Recall-Setup.exe /LOG=...` and renders a clean terminal-style
panel showing the milestone lines. Same harness as
`capture_doctor.py`.

Input log:  infra/packaging/windows/build_logs/install.log
Output:     assets/screenshots/installer-flow.png

    python infra/scripts/capture/capture_installer_flow.py
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from _render import ASSETS, app, render

_LOG = Path(__file__).resolve().parents[3] / "infra" / "packaging" / "windows" / "build_logs" / "install.log"

# One-shot phrases - each appears exactly once in the log.
_ONE_SHOT = (
    "Setup version:",
    "Windows version:",
    "Administrative install mode:",
    "Install mode root key:",
    "Starting the installation process.",
    "Creating new uninstall log:",
    "Installation process succeeded.",
    "Need to restart Windows?",
    "Log closed.",
)


def _milestones() -> list[str]:
    if not _LOG.exists():
        return ["(install.log not found - run a silent install first)"]
    lines = _LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = []
    seen: set[str] = set()
    for raw in lines:
        line = raw.strip()
        for phrase in _ONE_SHOT:
            if phrase in line and phrase not in seen:
                # Strip the timestamp prefix - keep only the message.
                out.append(line[24:] if len(line) > 24 else line)
                seen.add(phrase)
                break
    icons = sorted({
        ln.strip()[24:] for ln in lines
        if "Dest filename:" in ln and ".lnk" in ln
    })
    if icons:
        out.append("")
        out.append("Icons created:")
        for ic in icons:
            out.append(f"  {ic}")
    return out


_TERMINAL_QSS = """
QWidget#term_root {
  background: #0d1117;
  border-radius: 12px;
}
QLabel#term_text {
  color: #e6edf3;
  font-family: "Cascadia Mono", "Consolas", "Courier New", monospace;
  background: transparent;
  padding: 22px 28px;
}
QLabel#term_title {
  color: #7d8590;
  font-family: "Cascadia Mono", "Consolas", monospace;
  background: transparent;
  padding: 22px 28px 6px 28px;
}
"""


def _panel(text: str) -> QWidget:
    root = QWidget()
    root.setObjectName("term_root")
    root.setStyleSheet(_TERMINAL_QSS)
    root.setMinimumWidth(820)

    col = QVBoxLayout(root)
    col.setContentsMargins(0, 0, 0, 0)

    title = QLabel(
        "> Recall-Setup.exe /VERYSILENT  /LOG=install.log    "
        "# Phase 5G silent install on the build machine"
    )
    title.setObjectName("term_title")
    tf = QFont()
    tf.setFamily("Consolas")
    tf.setPointSizeF(10.5)
    tf.setStyleHint(QFont.StyleHint.Monospace)
    title.setFont(tf)
    col.addWidget(title)

    body = QLabel(text)
    body.setObjectName("term_text")
    bf = QFont()
    bf.setFamily("Consolas")
    bf.setPointSizeF(10.5)
    bf.setStyleHint(QFont.StyleHint.Monospace)
    body.setFont(bf)
    body.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    col.addWidget(body)

    return root


def main() -> None:
    _ = app()
    text = "\n".join(_milestones())
    widget = _panel(text)
    path = render(widget, "installer-flow")
    print(f"  wrote {path.relative_to(ASSETS.parent.parent)}")


if __name__ == "__main__":
    main()
