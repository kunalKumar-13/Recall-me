"""Capture the Phase 6I launcher v3 screens.

Five PNGs land in ``assets/screenshots/launcher-v3/``:

  - ``digest``    — full populated digest (recovery + 3 investigations +
                    trust footer) inside the three-column shell.
  - ``continue``  — recovery card in close-up (no investigations,
                    no trust footer) so the hero surface carries
                    the frame.
  - ``empty``     — the first-run empty surface, ``Recall notices
                    unfinished work.`` with Show example / Start
                    normally.
  - ``trust``     — the trust footer in isolation, full-width.
  - ``focused``   — same as digest but the recovery card is shown
                    in its `_focused = True` state (accent ring
                    visible) — the directive's *focus ring* spec.

The pipeline is the same as 6B / 6D — pure offscreen Qt, no engine
touch. The capture script constructs the v3 widget tree by hand;
no live launcher is involved.

    python infra/scripts/capture/capture_launcher_v3.py
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from _render import Panel, render
from app.ui import launcher_v3 as v3


# ── fixtures ──────────────────────────────────────────────────────


def _recovery_card() -> v3.RecoveryCardV3:
    return v3.RecoveryCardV3(
        candidate_id="rc_demo",
        title="WebSocket retry debugging",
        evidence="2 tabs · 2 files · reopened after a 2-day gap",
        time_label="just now",
        confidence="high",
        n_targets=4,
    )


def _investigations() -> List[v3.InvestigationCardV3]:
    return [
        v3.InvestigationCardV3(
            "t-ws", "ws", "WebSocket retry debugging",
            timeline=["09:20", "11:04", "2d gap"],
            surface_types=["tabs", "searches", "files", "chats"],
            last_touch="2h ago", strength=4,
        ),
        v3.InvestigationCardV3(
            "t-pp", "pp", "Healthcare pitch — proposal draft",
            timeline=["yesterday", "10:18"],
            surface_types=["files", "tabs", "chats"],
            last_touch="yesterday", strength=3,
        ),
        v3.InvestigationCardV3(
            "t-rl", "rl", "RLHF reward shaping",
            timeline=["1w", "Mon", "Tue"],
            surface_types=["searches", "tabs"],
            last_touch="3d ago", strength=2,
        ),
    ]


# ── window builders ───────────────────────────────────────────────


def _digest_window(*, focused: bool = False) -> v3.LauncherWindow:
    center = v3.DigestColumn()
    rec = _recovery_card()
    if focused:
        rec._focused = True  # noqa: SLF001 — explicit visual-state opt-in
    center.populate(recoveries=[rec], investigations=_investigations())
    win = v3.LauncherWindow(
        center,
        sidebar=v3.Sidebar(active_section="continue"),
        context=v3.ContextColumn(
            events_today=248,
            doctor_state="GREEN",
            extension_state="connected",
            protocol_state="registered",
            version="0.2.0",
        ),
    )
    win.resize(1180, 760)
    return win


def _empty_window() -> v3.LauncherWindow:
    empty = v3.EmptyDigest()
    win = v3.LauncherWindow(
        empty,
        sidebar=v3.Sidebar(active_section="continue"),
        context=v3.ContextColumn(
            events_today=0,
            doctor_state="YELLOW",
            extension_state="pairing",
            protocol_state="not yet",
            version="0.2.0",
        ),
    )
    win.resize(1180, 760)
    return win


def _continue_panel() -> QWidget:
    """Recovery card centred inside a Panel so the hero card carries
    the screenshot. The directive's *continue* shot."""
    panel = Panel(bg="#F7F5F2")
    panel.setFixedWidth(720)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(0)
    layout.addStretch(1)
    h = QHBoxLayout()
    h.addStretch(1)
    rec = _recovery_card()
    rec.setFixedWidth(560)
    h.addWidget(rec)
    h.addStretch(1)
    layout.addLayout(h)
    layout.addStretch(1)
    return panel


def _trust_panel_shot() -> QWidget:
    """Trust footer in isolation. Same warm-white panel."""
    panel = Panel(bg="#F7F5F2")
    panel.setFixedWidth(560)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 30, 40, 30)
    layout.setSpacing(0)
    layout.addWidget(v3.TrustPanel(events_today=248, daemon_connected=True))
    return panel


def main() -> None:
    captures = (
        ("digest", _digest_window()),
        ("continue", _continue_panel()),
        ("empty", _empty_window()),
        ("trust", _trust_panel_shot()),
        ("focused", _digest_window(focused=True)),
    )
    for name, widget in captures:
        path = render(widget, name, subdir="launcher-v3")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
