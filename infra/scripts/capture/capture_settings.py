"""Capture the Settings dialog - Phase 5F.

Renders `app.ui.settings.SettingsDialog` offscreen with a synthetic
`Config` + stub `Indexer` so the visual state can be captured for
the alpha packet and docs site. Same harness as `capture_launcher`.

The fixture is intentionally minimal: no real indexing happens, no
ingest server is constructed, no event log is read. The dialog
renders against a default `Config` so the screenshot represents a
new install's settings landscape.

    python infra/scripts/capture/capture_settings.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from _render import ASSETS, app, render

from app.core.config import Config
from app.ui.settings import SettingsDialog


@dataclass
class _StubIndexer:
    """Just enough surface for the Settings dialog to construct.
    Index actions are never triggered in the capture run."""
    cancelled: bool = False

    def index_folders(self, _folders: List[str], **_kw):  # pragma: no cover
        return None

    def cancel(self) -> None:
        self.cancelled = True


def _fixture_config() -> Config:
    """A representative-but-empty Config so the screenshot is a fresh
    install's settings dialog, not the developer's own."""
    cfg = Config(
        indexed_folders=[
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
        ],
        enable_ocr=False,
        launch_on_login=True,
        episodic_enabled=True,
        browser_ingest_enabled=True,
        browser_excluded_domains=["mail.google.com"],
        resurfacing_enabled=True,
        threads_enabled=True,
    )
    return cfg


def main() -> None:
    _ = app()  # ensure QApplication is alive
    cfg = _fixture_config()
    dialog = SettingsDialog(
        config=cfg,
        indexer=_StubIndexer(),  # type: ignore[arg-type]
        store_count=2480,
        event_logger=None,
        ingest_server=None,
    )
    path = render(dialog, "settings-dialog")
    print(f"  wrote {path.relative_to(ASSETS.parent.parent)}")


if __name__ == "__main__":
    main()
