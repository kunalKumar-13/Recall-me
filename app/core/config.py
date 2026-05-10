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
    # Default port chosen from the unprivileged dynamic range. Hard-
    # coded so the bundled extension can connect without configuration;
    # change requires updating both ends.
    browser_ingest_port: int = 49827
    # Domains the user has chosen to never capture. Matched as suffixes
    # so adding "google.com" silently filters mail.google.com, docs etc.
    browser_excluded_domains: List[str] = field(default_factory=list)

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
