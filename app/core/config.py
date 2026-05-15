"""User configuration — folders to index and lightweight preferences.

Stored in ~/.recall/config.json. The Chroma index lives next to it in
~/.recall/chroma so that the index survives across project moves and never
gets shipped with the repo.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

CONFIG_DIR: Path = Path.home() / ".recall"
CONFIG_FILE: Path = CONFIG_DIR / "config.json"
CHROMA_DIR: Path = CONFIG_DIR / "chroma"
# Episodic memory log — append-only JSONL files, one per day, written
# by EventLogger and read by EventStore. Lives next to chroma so the
# whole memory layer is one folder the user can inspect or delete.
EVENTS_DIR: Path = CONFIG_DIR / "events"


@dataclass
class Config:
    indexed_folders: List[str] = field(default_factory=list)
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 100
    enable_ocr: bool = False
    launch_on_login: bool = False
    # Episodic memory — when True, the launcher records what you
    # searched, opened, and revealed into ~/.recall/events. When False,
    # the EventLogger becomes a no-op; existing event files stay until
    # the user explicitly chooses to forget them.
    episodic_enabled: bool = True

    # ── Phase 1B: browser ingestion ──────────────────────────────
    # The local HTTP server that accepts events from the browser
    # extension. Loopback-only; nothing external can ever reach it.
    browser_ingest_enabled: bool = True
    # Phase 1D pins the port at 4545 (memorable, well outside the
    # commonly-used dev port range). Hard-coded into the bundled
    # extension; changing it here requires editing both ends.
    browser_ingest_port: int = 4545
    # Domains the user has chosen to never capture. Matched as suffixes
    # so adding "google.com" silently filters mail.google.com, docs etc.
    browser_excluded_domains: List[str] = field(default_factory=list)

    # ── Phase 2B: passive resurfacing ────────────────────────────
    # When True the launcher's idle digest grows a quiet
    # "continue where you left off" section over unfinished thinking.
    # When False the engine is skipped entirely and no extra disk
    # state is created. The toggle is honoured live; existing
    # `~/.recall/resurfacing.json` history stays on disk and is only
    # removed via the explicit "Clear resurfacing history" control.
    resurfacing_enabled: bool = True

    # ── Phase 2C: memory threads ─────────────────────────────────
    # When True the idle digest grows an "Active memory threads"
    # section listing topics the user keeps returning to. When False
    # the engine is skipped (no event-log scan, no cache writes).
    # Existing `~/.recall/threads.json` stays on disk and is only
    # removed via the Settings "Clear thread cache" control.
    threads_enabled: bool = True

    # ── Phase 3A: thread evolution ───────────────────────────────
    # When True the launcher fetches a chronological evolution
    # strip after opening a thread. When False the API returns 404
    # for `/v1/threads/{id}/evolution` and the launcher skips the
    # fetch entirely. The on-disk cache at
    # `~/.recall/evolution.json` only stores derived data; it's
    # always safe to delete.
    evolution_enabled: bool = True

    # ── Phase 3B: continuity recovery ───────────────────────────
    # When True the launcher's idle digest leads with a
    # "Continue where you left off" recovery section that supports
    # one-click restoration of every URL/path the user was using.
    # When False the section is empty and the recovery engine is
    # skipped (no event-log scan, no cache writes — recovery has
    # no persistent cache, the surface is derived on demand).
    recovery_enabled: bool = True

    @classmethod
    def load(cls) -> "Config":
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                known = {f for f in cls.__dataclass_fields__}
                return cls(**{k: v for k, v in data.items() if k in known})
            except (OSError, ValueError):
                pass
        return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
