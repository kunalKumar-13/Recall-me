"""Capture the Phase 6D demo overlay screens.

Two outputs land in `assets/screenshots/demo/`:

  - ``demo-launcher.png`` — the launcher's demo digest (trust banner
    + the canonical *WebSocket retry debugging* RecoveryCard + the
    three demo InvestigationCards).
  - ``demo-transition.png`` — the same surface re-rendered *without*
    the trust banner, simulating the post-dismiss / post-real-ingest
    state where the demo overlay has just faded out and the digest
    has taken over.

The capture is fully deterministic: every label comes from
`app.core.demo_mode.demo_payload()`, and the widgets are the same
`RecoveryCard` / `InvestigationCard` the live launcher constructs
when `demo_mode.is_active()`.

    python infra/scripts/capture/capture_demo.py
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from _render import Panel, render
from app.core import demo_mode
from app.ui.cards import InvestigationCard, RecoveryCard
from app.ui.styles import (
    ACCENT,
    ACCENT_DIM,
    BORDER,
    TEXT,
    TEXT_DIM,
    TEXT_DIMMER,
)

PANEL_W = 460


def _section(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setFixedHeight(30)
    f = lbl.font()
    f.setPointSizeF(7.4)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color:{TEXT_DIMMER};letter-spacing:1.3px;"
        "background:transparent;padding:12px 16px 4px 16px;"
    )
    return lbl


def _trust_banner() -> QWidget:
    """The lavender-tinted *Example data — Nothing here came from
    your device.* row. Mirrors the runtime banner built by
    :meth:`app.ui.launcher.Launcher._build_demo_panel`."""
    payload = demo_mode.demo_payload()
    banner = QWidget()
    banner.setObjectName("demo_banner_capture")
    b = QHBoxLayout(banner)
    b.setContentsMargins(14, 10, 12, 10)
    b.setSpacing(10)

    dot = QLabel()
    dot.setFixedSize(8, 8)
    dot.setStyleSheet(f"background:{ACCENT};border-radius:4px;")

    title = QLabel(payload["trust"]["banner_title"])
    title.setStyleSheet(
        f"color:{TEXT};font-size:11px;font-weight:600;"
    )
    body = QLabel(payload["trust"]["banner_body"])
    body.setStyleSheet(f"color:{TEXT_DIM};font-size:11px;")

    dismiss = QLabel("Dismiss")
    dismiss.setStyleSheet(
        f"color:{ACCENT};font-size:11px;font-weight:600;"
    )
    dismiss.setCursor(Qt.CursorShape.PointingHandCursor)

    b.addWidget(dot)
    b.addWidget(title)
    b.addWidget(body, 1)
    b.addWidget(dismiss)
    banner.setStyleSheet(
        f"QWidget#demo_banner_capture {{ "
        f"background:{ACCENT_DIM}; "
        f"border:1px solid {BORDER}; "
        f"border-radius:10px; }}"
    )
    return banner


def _panel(*children: QWidget, top: int = 10, bottom: int = 14) -> Panel:
    panel = Panel()
    panel.setFixedWidth(PANEL_W)
    col = QVBoxLayout(panel)
    col.setContentsMargins(8, top, 8, bottom)
    col.setSpacing(6)
    for c in children:
        col.addWidget(c)
    return panel


def _demo_digest(with_banner: bool = True) -> QWidget:
    """The launcher's demo digest. When ``with_banner=False`` the
    trust banner is omitted, producing the post-transition shot —
    the surface a user sees the moment the demo has yielded to
    real data."""
    payload = demo_mode.demo_payload()
    rec = payload["recovery"]
    investigations = payload["investigations"]

    rec_card = RecoveryCard(
        candidate_id=rec["id"],
        title=rec["title"],
        evidence=rec["preview_caption"],
        time_label="just now",
        confidence=rec["confidence"],
        n_targets=rec["tab_count"] + rec["file_count"],
    )
    rec_card.setFixedHeight(rec_card.RECOVERY_HEIGHT)

    inv_widgets: list[QWidget] = []
    for inv in investigations:
        card = InvestigationCard(
            thread_id=inv["id"],
            topic_key=inv["id"],
            title=inv["title"],
            evidence=inv["timeline_summary"],
            time_label="active",
        )
        inv_widgets.append(card)

    children: list[QWidget] = []
    if with_banner:
        children.append(_trust_banner())
    children.extend([
        _section("Continue where you left off"),
        rec_card,
        _section("Active investigations"),
        *inv_widgets,
    ])
    return _panel(*children)


def main() -> None:
    for name, widget in (
        ("demo-launcher", _demo_digest(with_banner=True)),
        ("demo-transition", _demo_digest(with_banner=False)),
    ):
        path = render(widget, name, subdir="demo")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
