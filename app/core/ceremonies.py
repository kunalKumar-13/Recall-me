"""Once-only first-time moments — Phase 5C.

A tiny JSON-backed flag store at `~/.recall/ceremonies.json` that
remembers which one-time UI moments have already happened on this
install. The first real recovery, the first resume — they earn one
small acknowledgement from the launcher and then never again, so
the surface stays calm forever after.

No streaks, no replay, no "you did it!". A ceremony is *one
sentence*, shown once, by a `_flash_footer` call in the launcher.
Like the rest of the observability surface, never raises.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import CONFIG_DIR

_PATH: Path = CONFIG_DIR / "ceremonies.json"

# The known one-time keys. Adding a new ceremony adds a key here.
_KEYS = frozenset({
    "first_recovery",   # first time recovery surfaced a candidate
    "first_resume",     # first successful Resume click
})


class Ceremonies:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or _PATH

    def _read(self) -> dict[str, str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return {k: str(v) for k, v in data.items() if isinstance(k, str)}
        except (OSError, ValueError, TypeError):
            return {}

    def has(self, key: str) -> bool:
        """Has this ceremony already fired on this install?"""
        return key in self._read()

    def mark(self, key: str) -> None:
        """Record that this ceremony has fired. Silent on failure."""
        if key not in _KEYS:
            return
        try:
            data = self._read()
            data[key] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError):
            pass
