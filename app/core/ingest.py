"""Localhost-only HTTP ingestion server for browser-extension events.

This module is the bridge between the bundled Chrome/Edge extension
and the existing `EventLogger`. The extension POSTs JSON to a fixed
loopback port; the server validates, sanitizes, and hands the result
to `EventLogger.log()`. From there, browser visits, searches, and
chat sessions live in the same per-day JSONL files as launcher
queries — one continuous local memory stream.

Hard rules:
  1. Bind only to 127.0.0.1. The server is unreachable from any
     other machine on any network.
  2. Append-only writes. The HTTP server cannot read the event log,
     it cannot delete events, it cannot rotate files. The only thing
     it ever does is hand sanitized payloads to `EventLogger.log()`.
  3. Schema-typed sanitization. The extension can send arbitrary
     JSON; we keep only the fields we recognize, truncate to safe
     lengths, and drop anything else on the floor.
  4. Per-domain exclude list applies server-side, not just at the
     extension. The extension's filter is a courtesy; the server's
     is the authoritative one.
  5. URL-scheme blocklist drops chrome://, file://, etc. before they
     ever reach disk.
  6. The server never raises into the request handler. Bad input
     returns a 400 with a short error; the daemon stays up.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterable, Optional
from urllib.parse import urlparse

from .events import EventLogger

# Default port chosen from the IANA dynamic range. Picked once and
# hard-coded into both the daemon and the extension. Changing it
# requires updating the extension manifest's host_permissions.
DEFAULT_PORT = 49827
LOOPBACK = "127.0.0.1"

# The only event kinds the ingest server will accept. Matches what
# the extension is allowed to send. Anything else is dropped
# silently — the extension can't grow new shapes without us
# explicitly opting them in here.
ALLOWED_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
})

# URL schemes we never store. Browsers expose plenty of internal
# pages with these schemes (settings, extension internals, local
# files). Capturing them is privacy-noisy and rarely useful.
SCHEME_BLOCKLIST: frozenset[str] = frozenset({
    "chrome",
    "chrome-extension",
    "chrome-search",
    "chrome-devtools",
    "edge",
    "extension",
    "moz-extension",
    "about",
    "file",
    "data",
    "blob",
    "view-source",
    "javascript",
})

# Per-key string truncation limits. URLs can be long (especially
# with tracking params); titles + queries are usually short. The
# limits are generous enough to be informative and small enough
# that an event line stays well under 4 KB.
_FIELD_LIMITS: dict[str, int] = {
    "url": 2048,
    "title": 500,
    "tab_title": 500,
    "query": 500,
    "domain": 240,
    "engine": 60,
    "platform": 60,
    "source": 60,
}

# Whitelisted payload keys per event kind. The handler drops any
# key not listed here so the extension cannot push arbitrary
# metadata into the event log.
_ALLOWED_KEYS: frozenset[str] = frozenset(_FIELD_LIMITS.keys())


# --------------------------------------------------------------- handler


class _IngestRequestHandler(BaseHTTPRequestHandler):
    """One HTTP request handler instance per connection."""

    # The HTTPServer subclass below pins this attribute so the handler
    # has a reference back to the IngestServer it belongs to.
    server: "IngestHTTPServer"

    # Silence the noisy default per-request log line that
    # BaseHTTPRequestHandler writes to stderr.
    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return

    # ------- response helpers -------

    def _cors_headers(self) -> None:
        """Permissive CORS for chrome-extension://* + http://localhost
        callers. Localhost-binding already isolates the server from
        the network; CORS is just so the browser doesn't refuse the
        XHR/fetch."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "POST, OPTIONS, GET"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    # ------- verbs -------

    def do_OPTIONS(self) -> None:  # noqa: N802 (HTTP verb, by convention)
        # CORS preflight. No body, just the headers.
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            srv = self.server.ingest_server
            self._send_json(200, {
                "status": "ok",
                "name": "recall-ingest",
                "enabled": srv.enabled,
                "ingested_total": srv.ingested_total,
                "dropped_total": srv.dropped_total,
            })
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/events":
            self._send_json(404, {"error": "not found"})
            return

        # Cap request size at 64 KB so a misbehaving client can't
        # blow up memory by sending a huge body.
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        if length <= 0 or length > 64 * 1024:
            self._send_json(400, {"error": "invalid content length"})
            return

        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid json"})
            return

        # Accept either a single event object or an array of events
        # so the extension can batch when convenient.
        if isinstance(data, dict):
            events = [data]
        elif isinstance(data, list):
            events = data
        else:
            self._send_json(400, {"error": "expected object or array"})
            return

        ingested = self.server.ingest_server.ingest(events)
        self._send_json(
            200,
            {"received": len(events), "ingested": ingested},
        )


class IngestHTTPServer(ThreadingHTTPServer):
    """HTTPServer subclass that pins a back-reference to the
    IngestServer so the handler can call into it without a closure."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address,
        request_handler,
        ingest_server: "IngestServer",
    ) -> None:
        super().__init__(server_address, request_handler)
        self.ingest_server = ingest_server


# --------------------------------------------------------------- server


class IngestServer:
    """Wraps the HTTP server with the per-event policy:

    - kind allowlist
    - URL scheme blocklist
    - domain exclude list (suffix match)
    - field allowlist + length truncation
    - hand-off to EventLogger

    Lifecycle:
      start() — binds and starts a daemon thread; returns False if
                bind fails (port in use, permissions, etc.). Failure
                is non-fatal for the parent app.
      stop()  — shuts the server down; safe to call multiple times.

    The server stays *resident* even when `enabled=False` — toggling
    only changes whether incoming events are written. That way the
    browser extension's health check still succeeds and the user
    can flip the switch without restarting either side.
    """

    def __init__(
        self,
        event_logger: EventLogger,
        port: int = DEFAULT_PORT,
        excluded_domains: Optional[Iterable[str]] = None,
        enabled: bool = True,
    ) -> None:
        self.event_logger = event_logger
        self.port = port
        self.enabled = enabled
        self._lock = threading.Lock()
        self._excluded_domains: set[str] = set()
        self.set_excluded_domains(excluded_domains or [])
        self._http: Optional[IngestHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self.ingested_total = 0
        self.dropped_total = 0

    # -- live config ------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def set_excluded_domains(self, domains: Iterable[str]) -> None:
        cleaned = {
            d.strip().lower().lstrip(".")
            for d in domains
            if isinstance(d, str) and d.strip()
        }
        with self._lock:
            self._excluded_domains = cleaned

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

    # -- core write path -------------------------------------------------

    def ingest(self, raw_events: list) -> int:
        """Validate + write a batch. Returns the count actually written.

        Bad events (wrong kind, blocked scheme, excluded domain,
        malformed JSON) are silently dropped — the response carries
        the count so the client knows roughly how many were lost,
        but we never raise back into the network.
        """
        if not self.enabled:
            self.dropped_total += len(raw_events)
            return 0

        n_written = 0
        for raw in raw_events:
            if not self._is_acceptable(raw):
                self.dropped_total += 1
                continue
            payload = self._sanitize_payload(raw.get("payload") or {})
            self.event_logger.log(raw["kind"], payload)
            n_written += 1
        self.ingested_total += n_written
        return n_written

    def _is_acceptable(self, raw) -> bool:
        if not isinstance(raw, dict):
            return False
        kind = raw.get("kind")
        if kind not in ALLOWED_KINDS:
            return False
        payload = raw.get("payload")
        if not isinstance(payload, dict):
            return False

        # Scheme check on the URL.
        url = (payload.get("url") or "").strip()
        domain = (payload.get("domain") or "").strip()
        if url:
            try:
                parsed = urlparse(url)
                scheme = (parsed.scheme or "").lower()
                if scheme in SCHEME_BLOCKLIST:
                    return False
                # If the extension didn't include domain, derive it
                # so we can apply the exclude list.
                if not domain:
                    domain = (parsed.hostname or "").lower()
            except Exception:
                return False

        if self.is_excluded(domain):
            return False
        return True

    def _sanitize_payload(self, payload: dict) -> dict:
        """Keep only allowlisted keys; truncate strings to per-field
        caps; coerce non-string scalars through harmlessly."""
        out: dict = {}
        for k, v in payload.items():
            if k not in _ALLOWED_KEYS:
                continue
            if isinstance(v, str):
                cap = _FIELD_LIMITS.get(k, 240)
                out[k] = v[:cap]
            elif isinstance(v, (int, float, bool)):
                out[k] = v
            # silently drop anything else (lists, nested objects)
        return out

    # -- lifecycle -------------------------------------------------------

    def start(self) -> bool:
        if self._http is not None:
            return True
        try:
            self._http = IngestHTTPServer(
                (LOOPBACK, self.port),
                _IngestRequestHandler,
                self,
            )
        except OSError:
            self._http = None
            return False

        self._thread = threading.Thread(
            target=self._http.serve_forever,
            name="recall-ingest",
            daemon=True,
        )
        self._thread.start()
        return True

    def stop(self) -> None:
        if self._http is not None:
            try:
                self._http.shutdown()
                self._http.server_close()
            except Exception:
                pass
            self._http = None
        self._thread = None

    @property
    def is_running(self) -> bool:
        return self._http is not None
