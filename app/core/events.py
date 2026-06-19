"""Append-only local event log — Recall's episodic memory layer.

Stores user-visible launcher activity (queries, file opens, reveals)
as plain JSONL files at `~/.recall/events/YYYY-MM-DD.jsonl`. Five
ground rules, written down so they don't drift:

  1. Plain JSON, line-per-event. Anyone with a text editor can audit
     exactly what was captured. The format is a contract with the user,
     not just a serialization choice.

  2. One file per day. Makes "forget yesterday" a single `os.remove()`
     and keeps the working set small (a heavy day is well under 1 MB).

  3. Logger-must-never-raise. The launcher must not crash, hang, or
     stutter because we couldn't append to a log line. All write paths
     swallow OSError and continue silently.

  4. Off-switch is honored synchronously. When `Config.episodic_enabled`
     flips to False (via the Settings toggle), `set_enabled(False)` makes
     every subsequent `log()` a no-op before it touches the disk.

  5. Nothing leaves the disk. There is no network in this module. The
     events folder is read by `EventStore` and the Settings "open log"
     button — no other code path.

Schema:

    {
      "ts": "2026-05-10T14:32:11Z",       # UTC ISO 8601
      "session_id": "s_20260510_143211",  # weakly sortable
      "kind": "query" | "open" | "reveal",
      "payload": { ... }                  # shape depends on kind
    }

Session inference:
    A new `session_id` is allocated whenever the gap from the previous
    event exceeds `SESSION_GAP_SECONDS`. Sessions are purely temporal in
    Phase 1A — no topic clustering. Topical sessions come later, derived
    from this same data.
"""

from __future__ import annotations

import calendar
import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from .config import EVENTS_DIR

# orjson is a 5-10x faster C-backed JSON parser. At 10K-event scale
# the per-line `json.loads()` is the dominant cost in `_cached_or_parse`,
# so we use orjson when available and fall back to stdlib so the
# package keeps installing on systems without the wheel.
try:
    import orjson as _orjson  # type: ignore

    def _loads(line: str):
        return _orjson.loads(line)

    _JSON_DECODE_ERRORS: tuple = (_orjson.JSONDecodeError, TypeError, AttributeError)
except ImportError:  # pragma: no cover - exercised on minimal installs
    _orjson = None

    def _loads(line: str):
        return json.loads(line)

    _JSON_DECODE_ERRORS = (json.JSONDecodeError, TypeError, AttributeError)

SESSION_GAP_SECONDS = 30 * 60   # 30 minutes
_TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _fast_iso_to_epoch(ts_str: str) -> float:
    """Parse our canonical `YYYY-MM-DDTHH:MM:SSZ` shape into a Unix
    epoch float, ~10× faster than `datetime.strptime` + timestamp().

    Phase 1F's micro-context reconstructor benchmarks 5K events; at
    that scale, stdlib's strptime dominates the call profile. This
    fast path lifted reconstruct() from 244ms → <50ms.
    """
    try:
        if len(ts_str) < 20:
            return 0.0
        y = int(ts_str[0:4])
        mo = int(ts_str[5:7])
        d = int(ts_str[8:10])
        h = int(ts_str[11:13])
        mi = int(ts_str[14:16])
        s = int(ts_str[17:19])
        return float(calendar.timegm((y, mo, d, h, mi, s, 0, 0, 0)))
    except (ValueError, IndexError, TypeError):
        return 0.0


# --------------------------------------------------------------- model


@dataclass
class Event:
    """One user action, frozen in time."""

    ts: str            # UTC ISO 8601, second resolution
    session_id: str
    kind: str          # "query" | "open" | "reveal"
    payload: dict      # kind-specific; see EventLogger.log_* helpers

    @classmethod
    def now(cls, kind: str, payload: dict, session_id: str) -> "Event":
        return cls(
            ts=datetime.now(timezone.utc).strftime(_TS_FORMAT),
            session_id=session_id,
            kind=kind,
            payload=payload,
        )

    def ts_epoch(self) -> float:
        """Best-effort conversion of `ts` to a Unix timestamp. Returns
        0.0 if the field is malformed — callers compare against `now`,
        so a zeroed timestamp falls into "ancient" and is harmless.

        Result is cached on the instance after first call — the value
        is deterministic w.r.t. `ts`, and the `strptime` parse cost
        is the dominant per-event cost at 5K-event scale. Caching
        flipped Phase 1F reconstruction from ~250ms to <30ms for the
        same input.
        """
        cached = getattr(self, "_ts_epoch_cache", None)
        if cached is not None:
            return cached
        result = _fast_iso_to_epoch(self.ts)
        object.__setattr__(self, "_ts_epoch_cache", result)
        return result

    def searchable_text(self) -> str:
        """Lowercase concatenation of every text-bearing payload
        field, suitable for substring filtering. Cached on the
        instance so the Phase 2A retrieval pipeline's quick-reject
        loop pays the build cost once per event across an entire
        request batch.

        At 10K-event scale this saved ~150ms per query vs.
        rebuilding the string on every scan.
        """
        cached = getattr(self, "_searchable_text_cache", None)
        if cached is not None:
            return cached
        self._build_search_cache()
        return self._searchable_text_cache  # type: ignore[attr-defined]

    def searchable_title(self) -> str:
        """Lowercased `title` + `query` portion of the payload.
        Cached. Used by the scorer's title-weighted keyword match."""
        cached = getattr(self, "_searchable_title_cache", None)
        if cached is not None:
            return cached
        self._build_search_cache()
        return self._searchable_title_cache  # type: ignore[attr-defined]

    def searchable_rest(self) -> str:
        """Lowercased non-title/query payload fields, joined.
        Cached. Used by the scorer's secondary keyword match."""
        cached = getattr(self, "_searchable_rest_cache", None)
        if cached is not None:
            return cached
        self._build_search_cache()
        return self._searchable_rest_cache  # type: ignore[attr-defined]

    def _build_search_cache(self) -> None:
        """Materialize all three searchable views in one pass.
        Touching `payload.items()` 3x was a measurable hot path at
        10K-event scale; a single pass amortizes the cost."""
        p = self.payload or {}
        title_parts: list[str] = []
        rest_parts: list[str] = []
        for k, v in p.items():
            if not isinstance(v, str) or not v:
                continue
            if k == "title" or k == "query":
                title_parts.append(v)
            else:
                rest_parts.append(v)
        title_lc = " ".join(title_parts).lower()
        rest_lc = " ".join(rest_parts).lower()
        combined = title_lc + " " + rest_lc if rest_lc else title_lc
        object.__setattr__(self, "_searchable_title_cache", title_lc)
        object.__setattr__(self, "_searchable_rest_cache", rest_lc)
        object.__setattr__(self, "_searchable_text_cache", combined)


# --------------------------------------------------------------- writer


class EventLogger:
    """Thread-safe, append-only writer.

    The lock serializes both session-id allocation and the file append
    so concurrent log calls (e.g. UI thread + background worker) never
    interleave bytes inside a JSONL line. Writes are synchronous — the
    log is small enough that fsync-on-append is acceptable, and we'd
    rather not lose the last action to a crash.
    """

    def __init__(
        self,
        base_dir: Path = EVENTS_DIR,
        enabled: bool = True,
    ) -> None:
        self.base_dir = base_dir
        self.enabled = enabled
        self._lock = threading.Lock()
        self._session_id: Optional[str] = None
        self._last_event_ts: Optional[float] = None

    # -- toggling --------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        """Honored synchronously. After this call, log() is a no-op
        until set_enabled(True) is called again."""
        self.enabled = enabled

    # -- session inference -----------------------------------------------

    def _ensure_session_locked(self) -> str:
        """Allocate a new session_id if the inter-event gap exceeded
        SESSION_GAP_SECONDS. Caller must hold `self._lock`.

        Session IDs include microsecond resolution so two consecutive
        sessions can't collide even when the gap is forced shorter than
        one second (e.g. test paths or programmatic resets). In normal
        use this is overkill; in edge cases it's the right default.
        """
        now = time.time()
        if (
            self._session_id is None
            or self._last_event_ts is None
            or (now - self._last_event_ts) > SESSION_GAP_SECONDS
        ):
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%d_%H%M%S_%f"
            )
            self._session_id = f"s_{stamp}"
        self._last_event_ts = now
        return self._session_id

    # -- write path ------------------------------------------------------

    def _today_path(self) -> Path:
        d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.base_dir / f"{d}.jsonl"

    def log(self, kind: str, payload: Optional[dict] = None) -> None:
        """Append one event to today's JSONL file. Best-effort."""
        if not self.enabled:
            return
        with self._lock:
            session_id = self._ensure_session_locked()
            event = Event.now(kind, payload or {}, session_id)
            try:
                self.base_dir.mkdir(parents=True, exist_ok=True)
                with self._today_path().open("ab") as f:
                    if _orjson is not None:
                        f.write(_orjson.dumps(asdict(event)))
                    else:
                        f.write(
                            json.dumps(
                                asdict(event), ensure_ascii=False
                            ).encode("utf-8")
                        )
                    f.write(b"\n")
            except OSError:
                # Logger must never raise — the launcher will keep
                # running with one fewer line in the activity log,
                # which is the right tradeoff.
                pass

    # -- typed convenience helpers --------------------------------------
    # These exist so the launcher never has to remember payload shapes.
    # Keep them tiny — anything non-trivial about a payload belongs at
    # the call site, not here.

    def log_query(self, text: str, result_count: int) -> None:
        self.log("query", {"text": text, "result_count": int(result_count)})

    def log_open(self, path: str, title: Optional[str] = None) -> None:
        self.log("open", {"path": path, "title": title or ""})

    def log_reveal(self, path: str, title: Optional[str] = None) -> None:
        self.log("reveal", {"path": path, "title": title or ""})


# --------------------------------------------------------------- reader


class EventStore:
    """Read-only view over the event log.

    Phase 1A shipped without caching — the per-day JSONL files were
    small enough that a fresh parse on every read was fine. Phase 2A
    added a heavier retrieval pipeline (episodic + session
    reconstruction read the same files within a single request), so a
    short-TTL per-file cache was added: identical reads within the
    `_file_cache_ttl_seconds` window reuse a pre-parsed `list[Event]`.

    Cache freshness (Phase 4F): a cached parse is reused only when
    the file's `(mtime, size)` is unchanged since the parse. Every
    write the system makes is an *append* via `EventLogger`, and an
    append always grows the file — so the size check alone detects
    every real write immediately, with the mtime check as a second
    signal. The TTL is now only a paranoia backstop for the
    pathological case of an in-place same-length overwrite that
    also preserves mtime (hand-edits change mtime; the logger only
    appends) — so it can be generous.

    Phase 4F history: the TTL was 0.5 s, tuned to "cover one
    launcher request". That made it load-bearing for correctness
    and far too short for *reuse* — two launcher searches more than
    half a second apart each re-parsed the whole log (~80 ms at
    10K events). Adding the size check moved correctness onto
    `(mtime, size)` and freed the TTL to be a 60 s backstop, so
    sustained interactive use stays on the warm path.
    """

    # Paranoia backstop only — correctness rides on the (mtime,
    # size) check below. 60 s keeps a day of intermittent launcher
    # use almost entirely on the warm path: one re-parse per minute
    # of idle, never one per search.
    _file_cache_ttl_seconds: float = 60.0
    _file_cache_max_entries: int = 32

    def __init__(self, base_dir: Path = EVENTS_DIR) -> None:
        self.base_dir = base_dir
        # value: (cached_at_monotonic, events, file_mtime, file_size)
        self._file_cache: dict[
            str, tuple[float, list[Event], float, int]
        ] = {}
        self._cache_lock = threading.Lock()

    def _files_for(self, days: int) -> List[Path]:
        """Per-day files for today and the prior `days - 1` days, in
        newest-first order so iter_events can yield newest-first
        without globbing the whole directory."""
        out: List[Path] = []
        today = datetime.now(timezone.utc).date()
        for delta in range(max(1, days)):
            d = today - timedelta(days=delta)
            p = self.base_dir / f"{d.strftime('%Y-%m-%d')}.jsonl"
            if p.exists():
                out.append(p)
        return out

    def iter_events(self, days: int = 7) -> Iterator[Event]:
        """Yield events from the last `days` days, newest first.

        Lines that fail to parse (truncated writes, manual edits) are
        skipped silently — by design the log is auditable, which means
        the user might have hand-edited it, and we should never crash
        because of that.
        """
        for path in self._files_for(days):
            yield from self._iter_file(path, reverse=True)

    def iter_events_for_date(self, date_str: str) -> Iterator[Event]:
        """Yield every event captured on a specific UTC date.

        `date_str` is `YYYY-MM-DD` — matches the filename of the
        per-day JSONL file. Order is chronological (oldest first),
        which is what reconstruction wants. Missing or unreadable
        files yield nothing; never raises.

        Added in Phase 2A for per-day reconstruction; works
        identically against the legacy logs Phase 1A wrote.
        """
        path = self.base_dir / f"{date_str}.jsonl"
        if not path.exists():
            return
        yield from self._iter_file(path, reverse=False)

    def _iter_file(self, path: Path, reverse: bool) -> Iterator[Event]:
        # Cache-first read. Both `iter_events` (multi-file, newest-
        # first) and `iter_events_for_date` (single file, chronological)
        # route through here, so a single parse can serve both within
        # one request.
        events = self._cached_or_parse(path)
        if events is None:
            return
        if reverse:
            for ev in reversed(events):
                yield ev
        else:
            for ev in events:
                yield ev

    def _cached_or_parse(self, path: Path) -> Optional[list[Event]]:
        """Return the parsed event list for `path`, using the cache
        when fresh enough. Cache hit requires both:

          1. TTL not expired (cheap monotonic clock check).
          2. File's mtime unchanged since the cached parse (cheap
             stat() — handles writes that beat the TTL window).

        Returns `None` if the file is unreadable; callers treat that
        as "no events".
        """
        key = str(path)
        now = time.monotonic()

        try:
            st = path.stat()
            file_mtime = st.st_mtime
            file_size = st.st_size
        except OSError:
            return None

        with self._cache_lock:
            cached = self._file_cache.get(key)
            if cached is not None:
                ts, events, cached_mtime, cached_size = cached
                if (
                    cached_mtime == file_mtime
                    and cached_size == file_size
                    and (now - ts) < self._file_cache_ttl_seconds
                ):
                    return events

        # Phase 4C — broaden file-read failure handling. The
        # original `except OSError` covered disk-level failures
        # (file gone, permission denied) but not encoding
        # corruption from a hand-edit that wrote a non-UTF-8
        # byte. Either way the right answer is the same:
        # treat as "no events from this file" and keep going.
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return None

        events: list[Event] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                rec = _loads(line)
                events.append(Event(
                    ts=rec.get("ts", ""),
                    session_id=rec.get("session_id", ""),
                    kind=rec.get("kind", ""),
                    payload=rec.get("payload") or {},
                ))
            except _JSON_DECODE_ERRORS:
                # Most common: a truncated line at the tail of
                # a file the user `cat`-edited or a partial
                # write that didn't flush. Skip and continue.
                continue
            except Exception:
                # Belt-and-braces: anything else (a malformed
                # record that parses but then violates
                # `Event`'s dataclass invariants, a memory
                # error on a freakishly long line) is treated
                # the same as a parse failure. The STABILITY.md
                # contract is that one bad line never aborts a
                # whole file's read.
                continue

        with self._cache_lock:
            # Drop oldest entries if we're at capacity. Simple FIFO,
            # not LRU — the cache is small and a query touches at most
            # 14 files, so eviction is rare.
            if len(self._file_cache) >= self._file_cache_max_entries:
                oldest_key = min(
                    self._file_cache,
                    key=lambda k: self._file_cache[k][0],
                )
                del self._file_cache[oldest_key]
            self._file_cache[key] = (now, events, file_mtime, file_size)
        return events

    def invalidate_cache(self, path: Optional[Path] = None) -> None:
        """Drop a specific file's parse cache (or everything when
        `path` is None). Called by `EventLogger` after appending so
        the next read picks up the new line."""
        with self._cache_lock:
            if path is None:
                self._file_cache.clear()
            else:
                self._file_cache.pop(str(path), None)

    # -- common queries the launcher uses --------------------------------

    def recent_queries(self, n: int = 5, days: int = 14) -> List[Event]:
        """Last N *distinct* queries (newest first). De-duped on the
        normalized text so a user who searched the same phrase twice
        doesn't see it twice in the digest."""
        seen: set[str] = set()
        out: List[Event] = []
        for ev in self.iter_events(days=days):
            if ev.kind != "query":
                continue
            text = (ev.payload.get("text") or "").strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(ev)
            if len(out) >= n:
                break
        return out

    def recent_browser_activity(
        self, n: int = 4, days: int = 7
    ) -> List[Event]:
        """Last N distinct browser-side events (newest first).

        Mixes browser_visit / browser_search / chat_session into a single
        chronological stream and dedupes by url+kind so reloading the
        same page doesn't crowd the digest. Used by the launcher's
        "Recent digital activity" idle section.
        """
        BROWSER_KINDS = {"browser_visit", "browser_search", "chat_session"}
        seen: set[tuple[str, str]] = set()
        out: List[Event] = []
        for ev in self.iter_events(days=days):
            if ev.kind not in BROWSER_KINDS:
                continue
            url = (ev.payload.get("url") or "").strip().lower()
            key = (ev.kind, url) if url else (ev.kind, str(id(ev)))
            if key in seen:
                continue
            seen.add(key)
            out.append(ev)
            if len(out) >= n:
                break
        return out


# --------------------------------------------------------------- forget


def forget_window(base_dir: Path, hours: int) -> int:
    """Delete events newer than `hours` ago across all per-day files.

    Returns the number of events actually removed. Used by the Settings
    "Forget last 24 hours" button. Files that become empty after
    filtering are removed entirely.
    """
    if hours <= 0 or not base_dir.exists():
        return 0
    cutoff_epoch = time.time() - hours * 3600
    cutoff_dt = datetime.fromtimestamp(cutoff_epoch, timezone.utc)
    today = datetime.now(timezone.utc).date()

    removed = 0
    # Only files dated >= cutoff date can possibly contain newer events.
    d = cutoff_dt.date()
    while d <= today:
        p = base_dir / f"{d.strftime('%Y-%m-%d')}.jsonl"
        d += timedelta(days=1)
        if not p.exists():
            continue
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        kept: List[str] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                ts_str = rec.get("ts", "")
                ev_dt = datetime.strptime(ts_str, _TS_FORMAT).replace(
                    tzinfo=timezone.utc
                )
                if ev_dt.timestamp() >= cutoff_epoch:
                    removed += 1
                    continue
            except (json.JSONDecodeError, ValueError, TypeError):
                # Keep malformed lines — refusing to delete what we can't
                # parse is the safer default in a privacy tool.
                pass
            kept.append(line)
        try:
            if kept:
                p.write_text("\n".join(kept) + "\n", encoding="utf-8")
            else:
                p.unlink()
        except OSError:
            pass
    return removed


def forget_all(base_dir: Path) -> int:
    """Delete every per-day event file under `base_dir`. Returns the
    number of files removed. The base directory itself is left in
    place so the next log call doesn't need to recreate it."""
    if not base_dir.exists():
        return 0
    removed = 0
    for p in base_dir.glob("*.jsonl"):
        try:
            p.unlink()
            removed += 1
        except OSError:
            pass
    return removed


# --------------------------------------------------------------- helpers


def humanize_age(epoch_ts: float, now: Optional[float] = None) -> str:
    """Format an event timestamp as a memory-shaped relative time.
    Mirrors the launcher widget's format_relative_time so the digest
    reads in the same vocabulary as the file rows."""
    if not epoch_ts:
        return ""
    if now is None:
        now = time.time()
    delta = now - epoch_ts
    if delta < 0:
        return "just now"
    if delta < 60:
        return "moments ago"
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    days = delta / 86400
    if days < 2:
        return "yesterday"
    if days < 7:
        return f"{int(days)}d ago"
    weeks = max(1, int(days // 7))
    return f"{weeks}w ago"
