"""Capture the Phase 6K live launcher screens.

Six PNGs land in ``assets/screenshots/launcher-live/``:

  - ``overview``   the full 3-column shell, populated digest
  - ``continue``   the hero recovery card alone (large frame)
  - ``empty``      first-run empty surface (Show example / Start normally)
  - ``trust``      trust footer in isolation
  - ``focus``      digest with the recovery card in `_focused = True`
  - ``recovery``   digest with the recovery card centred + a single
                   active investigation (the *cohort-facing* shape)

The script constructs the same `LiveLauncher` class `app/main.py`
spins up at runtime, then drives the v3 widget tree directly via
fixture data. No API calls, no engine touch — the captures are
deterministic across machines.

    python infra/scripts/capture/capture_launcher_live.py
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from _render import Panel, render
from app.ui import launcher_v3 as v3


# ── fixtures ──────────────────────────────────────────────────────


def _recovery() -> v3.RecoveryCardV3:
    return v3.RecoveryCardV3(
        candidate_id="rc_live",
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


def _digest_window(*, focused: bool = False) -> v3.LauncherWindow:
    center = v3.DigestColumn()
    rec = _recovery()
    if focused:
        rec._focused = True  # noqa: SLF001
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
    win = v3.LauncherWindow(
        v3.EmptyDigest(),
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


def _recovery_only_window() -> v3.LauncherWindow:
    """Same shell, but one investigation only — the directive's
    `recovery` shot: the surface the cohort actually sees on a
    Monday morning when a single thread asks for attention."""
    center = v3.DigestColumn()
    center.populate(
        recoveries=[_recovery()],
        investigations=[v3.InvestigationCardV3(
            "t-ws", "ws", "WebSocket retry debugging",
            timeline=["09:20", "11:04", "2d gap"],
            surface_types=["tabs", "files"],
            last_touch="2h ago", strength=4,
        )],
    )
    win = v3.LauncherWindow(
        center,
        sidebar=v3.Sidebar(active_section="continue"),
        context=v3.ContextColumn(
            events_today=42,
            doctor_state="GREEN",
            extension_state="connected",
            protocol_state="registered",
            version="0.2.0",
        ),
    )
    win.resize(1180, 760)
    return win


def _continue_panel() -> QWidget:
    panel = Panel(bg="#F7F5F2")
    panel.setFixedWidth(720)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 40)
    layout.setSpacing(0)
    layout.addStretch(1)
    h = QHBoxLayout()
    h.addStretch(1)
    rec = _recovery()
    rec.setFixedWidth(560)
    h.addWidget(rec)
    h.addStretch(1)
    layout.addLayout(h)
    layout.addStretch(1)
    return panel


def _trust_panel_shot() -> QWidget:
    panel = Panel(bg="#F7F5F2")
    panel.setFixedWidth(560)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 30, 40, 30)
    layout.setSpacing(0)
    layout.addWidget(v3.TrustPanel(events_today=248, daemon_connected=True))
    return panel


def main() -> None:
    captures = (
        ("overview", _digest_window()),
        ("continue", _continue_panel()),
        ("empty", _empty_window()),
        ("trust", _trust_panel_shot()),
        ("focus", _digest_window(focused=True)),
        ("recovery", _recovery_only_window()),
    )
    for name, widget in captures:
        path = render(widget, name, subdir="launcher-live")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
