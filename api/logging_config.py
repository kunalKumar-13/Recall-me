"""Structured logging for the API service.

Default format is line-oriented and human-readable. Switch to JSON
by setting the `RECALL_LOG_FORMAT=json` env var — handy for piping
logs into a structured collector (jq + grep, or anything wire-
shaped).

Loggers are namespaced under `recall.api.*`:

  recall.api.boot           — service start / stop
  recall.api.ingestion      — event accept / reject decisions
  recall.api.retrieval      — search timings + result counts
  recall.api.reconstruction — session + micro-context builds
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any


class _JSONFormatter(logging.Formatter):
    """Serialize each record as a single JSON line.

    Extra fields are passed via `extra={"extras": {...}}` so they
    don't collide with stdlib LogRecord attributes.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extras = getattr(record, "extras", None)
        if isinstance(extras, dict):
            payload.update(extras)
        return json.dumps(payload, ensure_ascii=False)


_HUMAN_FMT = "%(asctime)s %(levelname)-5s %(name)s  %(message)s"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Idempotent — safe to call multiple times. Returns the root
    `recall.api` logger; children inherit handlers + level."""
    root = logging.getLogger("recall.api")
    root.setLevel(level)

    # Drop any existing handlers so re-running tests in the same
    # interpreter doesn't double-log.
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stderr)
    fmt = os.environ.get("RECALL_LOG_FORMAT", "text").lower()
    if fmt == "json":
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(_HUMAN_FMT))
    root.addHandler(handler)

    # Prevent uvicorn's verbose access logs from drowning ours.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root


def log_with(logger: logging.Logger, level: int, msg: str, **kwargs) -> None:
    """Convenience: log with structured extras.

    Usage:
        log_with(log, logging.INFO, "event accepted",
                 kind="browser_visit", domain="arxiv.org")
    """
    logger.log(level, msg, extra={"extras": kwargs})
