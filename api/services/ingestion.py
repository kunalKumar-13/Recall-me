"""Ingestion service — validates + sanitizes + persists.

Centralises the field allowlist, the URL-scheme blocklist, and
the per-key length caps that previously lived inline in
`app/core/ingest.py`. Both the new versioned routes
(`/v1/events/*`) and the legacy `/events` route flow through this
one class so the rules are defined once.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple
from urllib.parse import urlparse

from app.core.ingest import (
    ALLOWED_KINDS,
    SCHEME_BLOCKLIST,
    _ALLOWED_KEYS,
    _FIELD_LIMITS,
)

from ..logging_config import log_with
from .storage import StorageService

log = logging.getLogger("recall.api.ingestion")


class IngestionService:
    """All event writes flow through this class.

    Owns three side-effects:

      1. The Settings-level "Browser memory" toggle (`enabled`).
      2. The domain exclude list (suffix-matched).
      3. The two counters surfaced on the `/v1/health` endpoint.

    Settings (`app/ui/settings.py`) calls `set_enabled` /
    `set_excluded_domains` / reads the counters directly on the
    APIService — which proxies to this class. Same surface as the
    pre-2A `IngestServer`, so the Settings UI is unchanged.
    """

    def __init__(
        self,
        storage: StorageService,
        excluded_domains: Optional[Iterable[str]] = None,
        enabled: bool = True,
    ) -> None:
        self.storage = storage
        self.enabled = enabled
        self._lock = threading.Lock()
        self._excluded_domains: set[str] = set()
        self.set_excluded_domains(excluded_domains or [])
        self.ingested_total = 0
        self.dropped_total = 0

    # -- live config ----------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)
        log_with(log, logging.INFO, "ingestion toggled", enabled=self.enabled)

    def set_excluded_domains(self, domains: Iterable[str]) -> None:
        cleaned = {
            d.strip().lower().lstrip(".")
            for d in domains
            if isinstance(d, str) and d.strip()
        }
        with self._lock:
            self._excluded_domains = cleaned
        log_with(
            log, logging.INFO, "exclude list updated",
            count=len(cleaned),
        )

    @property
    def excluded_domains(self) -> list[str]:
        with self._lock:
            return sorted(self._excluded_domains)

    def is_excluded(self, domain: str) -> bool:
        d = (domain or "").strip().lower()
        if not d:
            return False
        with self._lock:
            for ex in self._excluded_domains:
                if d == ex or d.endswith("." + ex):
                    return True
        return False

    # -- core write path -----------------------------------------------

    def ingest_typed(self, kind: str, payload: dict) -> Tuple[bool, Optional[str]]:
        """Write one validated event. Returns `(ingested, reason)`.

        `reason` is `None` on success and a short cause label on a
        drop. Bad input never raises — the HTTP layer returns 200
        with `ingested=0` and the cause in the response, so callers
        can tell the difference between "the daemon didn't store
        this" and "the daemon is down".
        """
        if not self.enabled:
            self.dropped_total += 1
            log_with(log, logging.DEBUG, "drop disabled", kind=kind)
            return False, "capture disabled"

        if kind not in ALLOWED_KINDS and kind not in ("open", "reveal"):
            self.dropped_total += 1
            return False, f"unknown kind: {kind}"

        # Resolve the URL scheme + domain once — both filters apply.
        url = (payload.get("url") or "").strip()
        domain = (payload.get("domain") or "").strip()
        if url:
            try:
                parsed = urlparse(url)
                scheme = (parsed.scheme or "").lower()
                if scheme in SCHEME_BLOCKLIST:
                    self.dropped_total += 1
                    log_with(
                        log, logging.DEBUG, "drop scheme",
                        scheme=scheme, kind=kind,
                    )
                    return False, f"blocked scheme: {scheme}"
                if not domain:
                    domain = (parsed.hostname or "").lower()
            except Exception:
                self.dropped_total += 1
                return False, "malformed url"

        if self.is_excluded(domain):
            self.dropped_total += 1
            log_with(
                log, logging.DEBUG, "drop excluded domain",
                domain=domain, kind=kind,
            )
            return False, f"excluded domain: {domain}"

        sanitized = self._sanitize_payload(payload, kind=kind)
        # Carry the freshly-derived domain forward so retrieval can
        # filter on it later. Same for the resolved domain when the
        # client didn't supply one.
        if domain and "domain" not in sanitized:
            sanitized["domain"] = domain

        if not self.storage.write(kind, sanitized):
            # Storage refused — usually because the logger is
            # disabled, but the toggle check at the top of this
            # method should have caught that. Either way, count
            # the drop.
            self.dropped_total += 1
            return False, "storage refused"

        self.ingested_total += 1
        log_with(
            log, logging.INFO, "ingested",
            kind=kind, domain=domain or "-",
        )
        return True, None

    def ingest_batch(self, items: list[tuple[str, dict]]) -> Tuple[int, int]:
        """Walk a list of `(kind, payload)` pairs. Returns
        `(received, ingested)`."""
        received = len(items)
        ingested = 0
        for kind, payload in items:
            ok, _ = self.ingest_typed(kind, payload)
            if ok:
                ingested += 1
        return received, ingested

    # -- sanitization ---------------------------------------------------

    def _sanitize_payload(self, payload: dict, kind: str) -> dict:
        """Keep only allowlisted keys; truncate strings to the per-
        field caps the schema documents."""
        out: dict = {}
        for k, v in payload.items():
            if k not in _ALLOWED_KEYS and k != "path":
                continue
            if isinstance(v, str):
                cap = _FIELD_LIMITS.get(k, 240) if k != "path" else 2048
                out[k] = v[:cap]
            elif isinstance(v, (int, float, bool)):
                out[k] = v
        # Stamp a freshly-derived `ts` only if the client didn't
        # provide one — the logger's append handles the canonical
        # form, but we keep payload.ts available for clients that
        # log retroactively (e.g. browser extension batching).
        if "ts" not in out and isinstance(payload.get("ts"), str):
            out["ts"] = payload["ts"][:32]
        return out
