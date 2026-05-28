"""Phase 10B — LiveLauncher slotted on top of DarkLauncher.

The host-facing launcher. Same public API as the legacy
``Launcher`` class:

  - ``LiveLauncher(search_engine, event_logger=None)``  constructor
  - ``show_centered() / hide()``                        window lifecycle
  - ``invalidate_digest()``                             drop cached payload
  - ``_refresh_idle_state()``                           recompute idle surface
  - ``request_settings``                                Qt signal
  - ``_request_search``                                 Qt signal (search input)

Internally, ``LiveLauncher`` subclasses
``darkframe.DarkLauncher`` -- the Phase 10A visual surface -- and
adds engine glue: API client, disk readers, restore-plan
execution, keyboard wiring. The visual surface
(``Frame`` / ``SearchBar`` / ``EmptyView`` / ``RecoveryView`` /
``SearchView`` / ``ResumeView`` / ``Footer``) lives entirely in
``darkframe.py``.

Four states map to engine conditions:

  empty       no events captured OR demo active w/ no hero
  recovery    HIGH recovery candidate above trust gate +
              "Other work" thread rail
  search      search bar has text (engine search results
              feed ``SearchGroupSpec[]``)
  resume      post-restore confirmation -- ~3 s after the user
              clicks Resume

The pre-10B ``MinimalShell`` / ``MinimalDigest`` /
``MinimalSearchBar`` / ``RecoveryCardV3`` / ``ResumePreview`` /
``RestoreToast`` composition is gone; the migration sheet at
[`LAUNCHER_MIGRATION.md`](../../../docs/engineering/LAUNCHER_MIGRATION.md)
catalogues which paint modules become dead-after-this-commit.

Phase 9's ``Phase 9`` recovery hero ``review`` signal is
preserved on ``HeroRecovery`` (now in ``darkframe``); same effect
(open preview surface) as ``resume`` per Phase 9's note.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Phase 7B — `RECALL_DEBUG=1` writes a one-line timing log to
# stderr for every `show_centered` so the directive's *<400 ms
# launcher open* budget can be confirmed on a real machine.
_TIMING_DEBUG = bool(os.environ.get("RECALL_DEBUG"))

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget

from .darkframe import (
    DarkLauncher,
    OtherWorkRow,
    PreviewProps,
    RecoveryProps,
    RestoredItem,
    SearchGroupSpec,
    SearchResultRow,
    STATE_EMPTY,
    STATE_RECOVERY,
    STATE_SEARCH,
    STATE_RESUME,
)

log = logging.getLogger("recall.ui.launcher_v3.live")


# `RECALL_EXPLAIN_RECOVERY=1` writes per-step skip reasons to stdout
# so a developer can inspect what didn't restore. Same env var the
# legacy launcher honours — kept consistent for parity.
_EXPLAIN_RECOVERY = bool(os.environ.get("RECALL_EXPLAIN_RECOVERY"))


# ── module-level helpers (engine glue, unchanged from pre-10B) ────


def _short_source(payload: dict, kind: str) -> str:
    """Pick a short, scannable source label for the Other work row.
    Prefers the captured ``platform``, falls back to the host
    derived from the URL, then to the event kind."""
    plat = (payload.get("platform") or "").strip()
    if plat:
        return plat[:14]
    url = (payload.get("url") or "").strip()
    if url:
        try:
            from urllib.parse import urlparse
            host = urlparse(url).hostname or ""
            host = host.replace("www.", "")
            if host:
                return host[:14]
        except Exception:  # noqa: BLE001
            pass
        eng = (payload.get("engine") or payload.get("domain") or "").strip()
        if eng:
            return eng[:14]
    if kind == "open":
        path = payload.get("path") or ""
        if path:
            return Path(path).name[:14]
    return kind[:14] if kind else ""


def _short_label(payload: dict, kind: str) -> str:
    """Short title for the Other work row. Prefers ``title``,
    falls back to ``query``, then ``path``, then ``url``."""
    for key in ("title", "query", "path", "url"):
        v = (payload.get(key) or "").strip()
        if v:
            return v
    return kind


def _load_recent_memory(max_rows: int = 5) -> list:
    """Read the latest events from ~/.recall/events/*.jsonl and
    project them onto the Other work row schema."""
    rows: list = []
    try:
        recall = Path(os.path.expanduser("~/.recall/events"))
        files = sorted(recall.glob("*.jsonl"))[-3:]
    except Exception:  # noqa: BLE001
        return rows
    import json
    from datetime import datetime, timezone
    samples: list = []
    for f in files:
        try:
            for line in f.read_text(encoding="utf-8").splitlines()[-30:]:
                try:
                    ev = json.loads(line)
                except (ValueError, TypeError):
                    continue
                ts = ev.get("ts")
                samples.append((ts, ev))
        except OSError:
            continue
    samples.sort(key=lambda x: x[0] or "", reverse=True)
    seen_urls: set = set()
    for ts, ev in samples:
        kind = ev.get("kind", "")
        payload = ev.get("payload") or {}
        label = _short_label(payload, kind)
        if not label:
            continue
        if label in seen_urls:
            continue
        seen_urls.add(label)
        # humanize timestamp
        when = ""
        try:
            t = datetime.fromisoformat((ts or "").replace("Z", "+00:00"))
            delta = datetime.now(timezone.utc) - t
            secs = int(delta.total_seconds())
            if secs < 3600:
                when = f"{max(1, secs // 60)}m ago"
            elif secs < 86400:
                when = f"{secs // 3600}h ago"
            else:
                when = f"{secs // 86400}d ago"
        except Exception:  # noqa: BLE001
            pass
        glyph = "file"
        if kind == "chat_session":
            glyph = "chat"
        elif kind == "browser_search":
            glyph = "search_sm"
        elif kind == "browser_visit":
            glyph = "tab"
        rows.append({"label": label[:64], "when": when, "glyph": glyph})
        if len(rows) >= max_rows:
            break
    return rows


# ── Phase P2 — Recent activity rail ────────────────────────────────


def _humanize_when_iso(ts: str) -> str:
    """Render an ISO timestamp as the same micro-time the rail uses."""
    if not ts:
        return ""
    try:
        from datetime import datetime, timezone
        t = datetime.fromisoformat((ts or "").replace("Z", "+00:00"))
        secs = int((datetime.now(timezone.utc) - t).total_seconds())
        if secs < 60:
            return "just now"
        if secs < 3600:
            return f"{max(1, secs // 60)}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:  # noqa: BLE001
        return ""


def _glyph_for_event(kind: str) -> str:
    """Pick the launcher glyph for one event-row in the rail."""
    if kind in ("open", "reveal"):
        return "file"
    if kind == "chat_session":
        return "chat"
    if kind == "browser_search":
        return "research"
    if kind == "browser_visit":
        return "tab"
    return "doc"


def _strength_for_event(kind: str, idx: int) -> str:
    """Rail strength dot. Newer + active-signal events read brighter.

    Phase P2 — the strength ladder is purely visual; the rail is
    sorted newest-first and the first row reads HIGH so the eye
    lands there, then steps down. `chat_session` always reads
    HIGH because it's the strongest active signal we have."""
    if kind == "chat_session":
        return "high"
    if idx == 0:
        return "high"
    if idx <= 2:
        return "med"
    return "low"


def _event_to_row_target(ev_payload: dict, kind: str) -> Optional[Tuple[str, str]]:
    """Pick the openable `(kind, target)` for one event payload.
    Returns None when the event has nothing the OS can open
    (so the row stays clickable but the launcher swallows it
    instead of misfiring)."""
    pl = ev_payload or {}
    if kind in ("open", "reveal"):
        path = (pl.get("path") or "").strip()
        if path:
            return ("path", path)
        return None
    url = (pl.get("url") or "").strip()
    if url:
        return ("url", url)
    return None


def _load_recent_activity(max_rows: int = 4) -> List[dict]:
    """Phase P2 — read the latest events off disk and project each
    onto a dict carrying the OtherWorkRow fields plus a
    `(target_kind, target)` tuple so the row's click handler has
    something to open.

    Caps at `max_rows` projected rows but considers up to ~120
    raw events so dedupe by `(kind, label)` lands on the freshest
    surface per topic.
    """
    rows: List[dict] = []
    try:
        recall = Path(os.path.expanduser("~/.recall/events"))
        files = sorted(recall.glob("*.jsonl"))[-3:]
    except Exception:  # noqa: BLE001
        return rows
    import json
    samples: list = []
    for f in files:
        try:
            for line in f.read_text(encoding="utf-8").splitlines()[-60:]:
                try:
                    ev = json.loads(line)
                except (ValueError, TypeError):
                    continue
                samples.append((ev.get("ts") or "", ev))
        except OSError:
            continue
    samples.sort(key=lambda x: x[0] or "", reverse=True)
    seen: set = set()
    idx = 0
    for ts, ev in samples:
        kind = ev.get("kind", "")
        payload = ev.get("payload") or {}
        label = _short_label(payload, kind)
        if not label:
            continue
        dedupe_key = (kind, label.lower())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        when = _humanize_when_iso(ts)
        target = _event_to_row_target(payload, kind)
        rows.append({
            "label": label[:60],
            "when": when or "recent",
            "glyph": _glyph_for_event(kind),
            "strength": _strength_for_event(kind, idx),
            "target": target,  # Optional[(kind, target)]
        })
        idx += 1
        if len(rows) >= max_rows:
            break
    return rows


def _load_trust_counts() -> tuple:
    """Return ``(events_today, investigation_count)`` for the
    launcher footer. Reads disk directly so the daemon doesn't
    have to be alive."""
    events_today = 0
    investigations = 0
    try:
        from datetime import date
        recall = Path(os.path.expanduser("~/.recall/events"))
        today = recall / f"{date.today().isoformat()}.jsonl"
        if today.exists():
            events_today = sum(
                1 for _ in today.read_text(encoding="utf-8").splitlines() if _
            )
    except Exception:  # noqa: BLE001
        pass
    try:
        threads = Path(os.path.expanduser("~/.recall/threads.json"))
        if threads.exists():
            import json
            data = json.loads(threads.read_text(encoding="utf-8"))
            investigations = len(data.get("threads", []))
    except Exception:  # noqa: BLE001
        pass
    return events_today, investigations


def _extract_gap_clause(preview_caption: str) -> Optional[str]:
    """Pull the ``returned after Nd`` clause from the engine's
    deterministic preview caption."""
    if not preview_caption:
        return None
    parts = [p.strip() for p in preview_caption.split("·")]
    for p in parts:
        if "return" in p.lower() or "after" in p.lower():
            return p
    return None


def _open_target(kind: str, target: str) -> bool:
    """Open a path / URL via the OS. Returns True on apparent
    success, False if the open failed."""
    if not target:
        return False
    target = target.strip()
    try:
        if kind == "path":
            if sys.platform.startswith("win"):
                os.startfile(target)  # type: ignore[attr-defined]
                return True
            if sys.platform == "darwin":
                subprocess.Popen(["open", target])
                return True
            subprocess.Popen(["xdg-open", target])
            return True
        # URL kinds (url / tab / chat / search)
        import webbrowser
        return webbrowser.open(target, new=2, autoraise=True)
    except Exception:  # noqa: BLE001
        return False


def _glyph_for_episodic(kind: str) -> str:
    """Map an event kind onto a darkframe glyph name. The search
    result-row uses these as the icon column."""
    if kind in ("open", "reveal"):
        return "file"
    if kind == "chat_session":
        return "chat"
    if kind == "browser_search":
        return "search_sm"
    if kind == "browser_visit":
        return "tab"
    return "doc"


def _humanize_thread_when(updated_at: float) -> str:
    """``updated_at`` is a unix epoch float. Return ``3d`` / ``5d``
    / ``last week`` style microtext for the Other work column."""
    if updated_at <= 0:
        return ""
    try:
        from app.core.events import humanize_age
        return humanize_age(float(updated_at))
    except Exception:  # noqa: BLE001
        return ""


# ── LiveLauncher (Phase 10B) ──────────────────────────────────────


class LiveLauncher(DarkLauncher):
    """The Phase 10B production launcher.

    Subclasses ``darkframe.DarkLauncher`` to inherit the dark
    cinematic visual surface (Frame + SearchBar + Footer + four
    state widgets) and adds engine glue: APIClient, disk readers,
    restore-plan execution, OS-open helper, keyboard shortcuts.

    Constructor + signals + ``show_centered`` / ``invalidate_digest``
    + ``_refresh_idle_state`` are wire-compatible with the pre-10B
    surface so ``app/main.py`` doesn't change.
    """

    # Host-facing signals (preserved across the migration).
    request_settings = pyqtSignal()
    _request_search = pyqtSignal(str)

    # Phase 10B canvas. Matches darkframe.FRAME_W / FRAME_H exactly.
    DEFAULT_SIZE = (760, 520)

    def __init__(
        self,
        search_engine,
        event_logger=None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.search_engine = search_engine
        self.event_logger = event_logger
        from app.core.api_client import APIClient
        self.api_client = APIClient(base_url="http://127.0.0.1:4545")

        self.setObjectName("launcher_v3_live")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Pre-Resume state snapshot so `Done` reverts cleanly.
        self._pre_resume_state: str = STATE_EMPTY

        # Pending-restore bookkeeping (captured at the moment the
        # user clicks Resume / Review so plan execution doesn't
        # need to re-ask the engine).
        self._pending_targets: List[Tuple[str, str]] = []
        self._pending_title: str = ""
        self._pending_cid: str = ""
        self._pending_demo: bool = False

        # Phase P2 — parallel to the RecoveryView's other-work rail.
        # Holds the (kind, target) tuple for each row so a click
        # at index i can open the right thing.
        self._row_targets: List[Optional[Tuple[str, str]]] = []

        # Forward the search bar's frozen public signals to the host.
        sb = self.search_bar()
        sb.request_settings.connect(self.request_settings.emit)
        sb.request_close.connect(self.hide)
        sb.query_changed.connect(self._on_query_changed)
        sb.submit.connect(self._on_search_submit)

        # Keyboard layer.
        QShortcut(QKeySequence("Esc"), self, activated=self._on_escape)
        QShortcut(QKeySequence("Ctrl+K"), self,
                  activated=lambda: self.search_bar().focus())
        QShortcut(QKeySequence("Meta+K"), self,
                  activated=lambda: self.search_bar().focus())
        QShortcut(QKeySequence("1"), self,
                  activated=self._on_hotkey_one)

        # Initial state derivation.
        self._refresh_idle_state()

    # ── lifecycle (legacy API mirror) ────────────────────────────

    def show_centered(self) -> None:
        """Show the launcher centred on the active screen."""
        t0 = time.perf_counter() if _TIMING_DEBUG else 0.0
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.show()
            return
        geo = screen.availableGeometry()
        x = geo.center().x() - self.width() // 2
        y = geo.top() + int(geo.height() * 0.16)
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self._refresh_idle_state)
        if _TIMING_DEBUG:
            ms = round((time.perf_counter() - t0) * 1000, 1)
            print(
                f"[recall.launcher.timing] show_centered  {ms} ms  "
                f"(budget 400)",
                file=sys.stderr, flush=True,
            )

    def invalidate_digest(self) -> None:
        """Drop any cached payload; the next ``_refresh_idle_state``
        re-fetches from the API."""
        self._cached_digest = None

    # ── state derivation ─────────────────────────────────────────

    def _demo_active(self) -> bool:
        try:
            from app.core import demo_mode
            return demo_mode.is_active()
        except Exception:  # noqa: BLE001
            return False

    def _refresh_idle_state(self) -> None:
        """Pick between empty / recovery based on what the daemon
        returns. Demo overlay is honoured: when ``demo_mode.is_active()``
        the recovery state receives a synthetic payload."""
        # Don't pre-empt search or resume states.
        if self.state() in (STATE_SEARCH, STATE_RESUME):
            return

        try:
            empty = self.search_engine.store.count() == 0
        except Exception:  # noqa: BLE001
            empty = True

        # Belt-and-braces: drop a demo overlay that survived a real
        # ingest. Same rule as the legacy launcher.
        try:
            from app.core import demo_mode
            if not empty and demo_mode.is_active():
                demo_mode.dismiss()
        except Exception:  # noqa: BLE001
            pass

        if empty and not self._demo_active():
            self.set_state(STATE_EMPTY)
            self._wire_empty_view()
            return

        self._populate_recovery_state()

    def _populate_recovery_state(self) -> None:
        """Build a RecoveryProps + PreviewProps + OtherWorkRow[]
        triple from engine data, then enter STATE_RECOVERY.

        Phase P2 — the launcher *never* falls through to STATE_EMPTY
        when the event store has any captured data. The hero is
        either: (a) the real recovery candidate, (b) a thread-
        derived QuickResume hero synthesised from the top thread,
        or (c) a minimal Recent-activity hero built from the
        freshest event. The other-work rail always carries recent
        cross-source activity so the surface is useful immediately."""
        if self._demo_active():
            self._populate_demo()
            return
        try:
            recoveries = self.api_client.recovery_recent(n=3) or []
        except Exception:  # noqa: BLE001
            recoveries = []
        try:
            threads = self.api_client.threads_recent(n=6) or []
        except Exception:  # noqa: BLE001
            threads = []

        # Phase P1: band-aware acceptance. Engine guarantees
        # _MIN_DISTINCT_TARGETS for non-fallback bands; fallback
        # synthesises its own minimum. We accept any non-flagged
        # candidate with at least one restorable target.
        hero = None
        for c in recoveries:
            targets = list(getattr(c, "suggested_targets", []) or [])
            flagged = bool(
                (getattr(c, "signals", None) or {}).get("ledger_flagged", 0.0)
            )
            if targets and not flagged:
                hero = c
                break

        # Phase P2 — the rail is always populated from recent
        # disk activity so the launcher carries cross-source
        # *RECENT ACTIVITY* even when recovery surfaces a hero.
        # The rail is the "RECENT ACTIVITY" surface from the
        # directive; threads alone would only show topic groups.
        activity_rows = _load_recent_activity(max_rows=4)
        other_work: List[OtherWorkRow] = []
        self._row_targets: List[Optional[Tuple[str, str]]] = []
        for row in activity_rows:
            other_work.append(OtherWorkRow(
                glyph=row["glyph"],
                title=row["label"],
                when=row["when"],
                strength=row["strength"],
            ))
            self._row_targets.append(row["target"])

        if hero is not None:
            # Real recovery candidate available — use it as the hero
            # so the QUICK RESUME slot fires the orchestrated plan.
            targets = list(getattr(hero, "suggested_targets", []) or [])
            self._pending_cid = getattr(hero, "id", "")
            self._pending_title = getattr(hero, "title", "") or "(untitled)"
            self._pending_targets = list(targets)
            self._pending_demo = False
            recovery_props = self._engine_to_recovery_props(hero, targets)
            preview_props = self._engine_to_preview_props(hero)
        elif threads:
            # No recovery hero — synthesise a QUICK RESUME hero
            # from the top thread so the launcher still has a
            # primary action. The thread carries
            # representative_targets which the click handler
            # opens directly (bypasses the orchestrated plan since
            # there's no candidate id behind it).
            top = threads[0]
            recovery_props, preview_props, t_targets = \
                self._thread_to_quick_resume(top)
            self._pending_cid = ""  # no candidate -> direct-open path
            self._pending_title = getattr(top, "title", "") or "(thread)"
            self._pending_targets = list(t_targets)
            self._pending_demo = False
        else:
            # No threads either, but at least one event sits on
            # disk (caller checked `count > 0`). Build a
            # Recent-activity hero off the freshest activity row
            # so the surface still has a primary action: open the
            # most recent thing the user touched.
            recovery_props, preview_props, ev_targets = \
                self._activity_to_recent_hero(activity_rows)
            self._pending_cid = ""
            self._pending_title = recovery_props.title_main + \
                " " + recovery_props.title_accent
            self._pending_targets = list(ev_targets)
            self._pending_demo = False

        # Fall back to thread-derived rows when the disk-read
        # activity rail came up empty (rare — only if event files
        # exist but are unreadable).
        if not other_work:
            other_work = [self._thread_to_other_row(t) for t in threads[:4]]
            # Build row-target list from the thread's representative
            # targets so clicks still open something.
            self._row_targets = []
            for t in threads[:4]:
                rts = list(getattr(t, "representative_targets", []) or [])
                self._row_targets.append(rts[0] if rts else None)

        self.set_state(
            STATE_RECOVERY,
            recovery=recovery_props,
            preview=preview_props,
            other_work=other_work,
        )
        self._wire_recovery_view()

    # ── Phase P2 — synthesise hero when no recovery hero exists ─────

    def _thread_to_quick_resume(
        self, thread,
    ) -> Tuple[RecoveryProps, PreviewProps, List[Tuple[str, str]]]:
        """Project a Thread onto (RecoveryProps, PreviewProps,
        targets) for the QUICK RESUME hero when the engine has no
        recovery candidate."""
        title = getattr(thread, "title", "") or "(thread)"
        title_main, title_accent = _split_title_accent(title)
        rts = list(getattr(thread, "representative_targets", []) or [])
        n_files = sum(1 for k, _ in rts if k == "path")
        n_tabs = sum(1 for k, t in rts
                     if k != "path" and "search" not in (t or "").lower())
        n_searches = sum(1 for k, t in rts
                         if k != "path" and "search" in (t or "").lower())
        when = _humanize_thread_when(
            float(getattr(thread, "updated_at", 0.0) or 0.0)
        )
        eyebrow = f"Active · {when}" if when else "Active thread"
        recovery_props = RecoveryProps(
            title_main=title_main,
            title_accent=title_accent,
            eyebrow_meta=eyebrow,
            n_files=n_files,
            n_tabs=n_tabs,
            n_searches=n_searches,
            last_active=f"last active · {when}" if when else "last active",
        )
        # Preview the first file if the thread has one; else the
        # first URL's host as a stand-in label.
        file_t = next((t for k, t in rts if k == "path"), None)
        url_t = next((t for k, t in rts if k != "path"), None)
        defaults = PreviewProps()
        if file_t:
            label = Path(file_t).name
            meta = f"~{Path(file_t).parent.name}"
        elif url_t:
            try:
                from urllib.parse import urlparse
                host = urlparse(url_t).hostname or ""
                label = host.replace("www.", "")[:40] or url_t[:40]
            except Exception:  # noqa: BLE001
                label = url_t[:40]
            meta = "browser"
        else:
            label = defaults.label
            meta = defaults.meta
        preview_props = PreviewProps(
            label=label,
            excerpt_prefix=defaults.excerpt_prefix,
            excerpt_highlight=defaults.excerpt_highlight,
            excerpt_suffix=defaults.excerpt_suffix,
            meta=meta,
        )
        return recovery_props, preview_props, rts

    def _activity_to_recent_hero(
        self, activity_rows: List[dict],
    ) -> Tuple[RecoveryProps, PreviewProps, List[Tuple[str, str]]]:
        """Last-resort hero built off the freshest event row when no
        thread is available — so the launcher still shows the
        user's most recent action as a one-click resume."""
        defaults_r = RecoveryProps()
        defaults_p = PreviewProps()
        if not activity_rows:
            return defaults_r, defaults_p, []
        top = activity_rows[0]
        label = top["label"]
        when = top["when"]
        target = top.get("target")
        title_main = label[:32]
        title_accent = "again."
        recovery_props = RecoveryProps(
            title_main=title_main,
            title_accent=title_accent,
            eyebrow_meta=f"Latest activity · {when}",
            n_files=1 if target and target[0] == "path" else 0,
            n_tabs=1 if target and target[0] != "path" else 0,
            n_searches=0,
            last_active=f"last active · {when}",
        )
        preview_props = PreviewProps(
            label=label[:40],
            excerpt_prefix=defaults_p.excerpt_prefix,
            excerpt_highlight=defaults_p.excerpt_highlight,
            excerpt_suffix=defaults_p.excerpt_suffix,
            meta=when,
        )
        targets: List[Tuple[str, str]] = []
        if target:
            targets.append(target)
        return recovery_props, preview_props, targets

    def _populate_demo(self) -> None:
        from app.core import demo_mode
        payload = demo_mode.demo_payload()
        rec = payload["recovery"]
        demo_targets: List[Tuple[str, str]] = []
        for url in rec.get("urls", []) or []:
            demo_targets.append(("url", url))
        for path in rec.get("files", []) or []:
            demo_targets.append(("path", path))

        n_files = len([t for k, t in demo_targets if k == "path"])
        n_tabs = len([t for k, t in demo_targets if k == "url"])
        gap_clause = (_extract_gap_clause(rec.get("preview_caption", ""))
                      or "Returned after 2 days")
        title = rec.get("title", "WebSocket retry debugging")
        # Split title into main + accent if the title contains the
        # canonical "debugging" suffix; otherwise use the whole
        # title as title_main and a generic accent.
        title_main, title_accent = _split_title_accent(title)

        recovery_props = RecoveryProps(
            title_main=title_main,
            title_accent=title_accent,
            eyebrow_meta=gap_clause,
            n_files=n_files,
            n_tabs=n_tabs,
            n_searches=0,
            last_active="last active · demo",
        )
        preview_props = PreviewProps()  # demo uses the default fixture

        other_work: List[OtherWorkRow] = []
        strengths = ["high", "med", "low"]
        for i, inv in enumerate(payload.get("investigations", [])[:3]):
            other_work.append(OtherWorkRow(
                glyph="doc",
                title=inv.get("title", "(thread)"),
                when=str(inv.get("last_seen", "")) or "active",
                strength=strengths[min(i, 2)],
            ))

        self._pending_cid = rec.get("id", "demo")
        self._pending_title = title
        self._pending_targets = list(demo_targets)
        self._pending_demo = True

        self.set_state(
            STATE_RECOVERY,
            recovery=recovery_props,
            preview=preview_props,
            other_work=other_work,
        )
        self._wire_recovery_view()

    def _engine_to_recovery_props(
        self, c, targets: List[Tuple[str, str]],
    ) -> RecoveryProps:
        title = getattr(c, "title", "") or "(untitled)"
        title_main, title_accent = _split_title_accent(title)
        gap = (_extract_gap_clause(getattr(c, "preview_caption", "") or "")
               or "Continue where you left off")
        n_files = sum(1 for k, _ in targets if k == "path")
        n_tabs = sum(1 for k, t in targets if k != "path"
                     and "search" not in (t or "").lower())
        n_searches = sum(1 for k, t in targets
                         if k != "path" and "search" in (t or "").lower())
        return RecoveryProps(
            title_main=title_main,
            title_accent=title_accent,
            eyebrow_meta=gap,
            n_files=n_files,
            n_tabs=n_tabs,
            n_searches=n_searches,
            last_active="last active · implementation",
        )

    def _engine_to_preview_props(self, c) -> PreviewProps:
        """Engine -> PreviewProps adapter. The Phase 10A PreviewCard
        renders a file label + an excerpt with a highlighted phrase.
        Engine doesn't surface excerpts yet (Phase 10C scope), so
        we use the engine's suggested top file as the label and
        the default excerpt copy."""
        targets = list(getattr(c, "suggested_targets", []) or [])
        file_target = next((t for k, t in targets if k == "path"), None)
        if file_target:
            label = Path(file_target).name
        else:
            label = "pitch_healthcare_v3.pdf"
        defaults = PreviewProps()
        return PreviewProps(
            label=label,
            excerpt_prefix=defaults.excerpt_prefix,
            excerpt_highlight=defaults.excerpt_highlight,
            excerpt_suffix=defaults.excerpt_suffix,
            meta="~/notes · 4d",
        )

    def _thread_to_other_row(self, t) -> OtherWorkRow:
        title = getattr(t, "title", "") or "(untitled)"
        when = _humanize_thread_when(float(getattr(t, "updated_at", 0.0) or 0.0))
        surfaces = list(getattr(t, "surface_types", []) or [])
        if len(surfaces) >= 3:
            strength = "high"
        elif len(surfaces) == 2:
            strength = "med"
        else:
            strength = "low"
        glyph = "doc"
        if "chat" in surfaces:
            glyph = "chat"
        elif "search" in surfaces:
            glyph = "research"
        return OtherWorkRow(
            glyph=glyph,
            title=title[:60],
            when=when or "recent",
            strength=strength,
        )

    def _wire_recovery_view(self) -> None:
        """Hook the RecoveryView's resume + review + preview-open
        + row-click signals to the engine-side handlers. Called
        after every ``set_state(STATE_RECOVERY, ...)``."""
        view = self._view
        if hasattr(view, "resume"):
            try:
                view.resume.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.resume.connect(self._on_resume_clicked)
        if hasattr(view, "review"):
            try:
                view.review.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.review.connect(self._on_resume_clicked)
        # Phase P0 — preview card's Open ↗ now opens the previewed
        # file via the OS open helper instead of being decorative.
        if hasattr(view, "preview_open"):
            try:
                view.preview_open.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.preview_open.connect(self._on_preview_open)
        # Phase P2 — RECENT ACTIVITY rail rows fire `row_clicked(int)`
        # which previously went nowhere. Each click now opens the
        # underlying target via `_row_targets[i]`.
        if hasattr(view, "row_clicked"):
            try:
                view.row_clicked.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.row_clicked.connect(self._on_other_row_clicked)

    def _wire_empty_view(self) -> None:
        """Hook the EmptyView's Show example / Start working buttons
        so they activate / dismiss demo mode. Phase P0 — these were
        dead since the Phase 10B migration."""
        view = self._view
        if hasattr(view, "show_example"):
            try:
                view.show_example.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.show_example.connect(self._on_show_example)
        if hasattr(view, "start_working"):
            try:
                view.start_working.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.start_working.connect(self._on_start_working)

    def _wire_resume_view(self) -> None:
        """Hook the ResumeView's undo + done signals after every
        ``set_state(STATE_RESUME, ...)``."""
        view = self._view
        if hasattr(view, "done_clicked"):
            try:
                view.done_clicked.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.done_clicked.connect(self._on_resume_done)
        if hasattr(view, "undo_clicked"):
            try:
                view.undo_clicked.disconnect()
            except (TypeError, RuntimeError):
                pass
            view.undo_clicked.connect(self._on_resume_undo)

    # ── search flow ─────────────────────────────────────────────

    def _on_query_changed(self, q: str) -> None:
        """Typing toggles between recovery and search states. Empty
        string -> back to the idle surface.

        Phase P2 — when the user clears the search bar we want to
        return to the recovery surface immediately. The default
        `_refresh_idle_state` guards against re-entering when
        already in SEARCH/RESUME, so on clear we route directly
        through `_populate_recovery_state`."""
        self._request_search.emit(q)
        if not q.strip():
            # Force a recompute of the idle surface even though we
            # are currently in SEARCH — the user just *left* search
            # and the rail needs to repaint.
            try:
                empty = self.search_engine.store.count() == 0
            except Exception:  # noqa: BLE001
                empty = True
            if empty and not self._demo_active():
                self.set_state(STATE_EMPTY)
                self._wire_empty_view()
            else:
                self._populate_recovery_state()
            return
        # Build a SearchGroupSpec list from the engine. The
        # adapter is intentionally tiny: take the first 10 hits +
        # bucket by surface kind.
        groups = self._search_engine_to_groups(q)
        self.set_state(STATE_SEARCH, search_groups=groups)

    def _on_search_submit(self, _q: str) -> None:
        """Enter on the search bar activates the top selected row.
        For now we just forward the query; the inline-row activation
        path is engine-side."""
        return

    def _search_engine_to_groups(self, q: str) -> List[SearchGroupSpec]:
        """Engine -> SearchGroupSpec[] adapter.

        Phase P0 — the launcher's `search_engine` is the ChromaDB
        file index (used by the desktop file-search path). That
        only returns files matching the query, never browser
        events. The user has no chatgpt-named files on disk, but
        has 19 chatgpt browser events; the previous wiring missed
        all of them.

        The daemon's blended `/v1/search` already runs episodic +
        contexts + sessions retrieval over the event store, so the
        launcher routes through `api_client.search(q)` instead and
        falls back to the file index only when the daemon is down.

        Buckets map to the design's four groups:
          Investigations  micro-contexts (label + match_count)
          Files           file-event episodic hits (kind=open|reveal)
          Returns         sessions (revisited topics)
          Events          remaining episodic hits (browser / chat / search)
        """
        groups: List[SearchGroupSpec] = []
        resp = None
        try:
            resp = self.api_client.search(q, n_episodic=8, n_sessions=3, n_contexts=4)
        except Exception:  # noqa: BLE001
            resp = None

        if resp is not None:
            inv_rows: List[SearchResultRow] = []
            for i, c in enumerate(resp.contexts[:4]):
                inv_rows.append(SearchResultRow(
                    glyph="thread",
                    title=(c.label or c.topic or "(thread)")[:60],
                    meta=(c.time_label or "")[:48],
                    score=80 + (3 - i) * 4,
                    selected=(len(inv_rows) == 0),
                ))
            file_rows: List[SearchResultRow] = []
            event_rows: List[SearchResultRow] = []
            for h in resp.episodic:
                row = SearchResultRow(
                    glyph=_glyph_for_episodic(h.kind),
                    title=(h.title or h.subtitle or h.url or "(untitled)")[:60],
                    meta=(h.subtitle or h.url or "")[:48],
                    score=max(0, min(99, int(round(h.score * 100)))) if h.score else 70,
                    selected=False,
                )
                if h.kind in ("open", "reveal"):
                    file_rows.append(row)
                else:
                    event_rows.append(row)
            ret_rows: List[SearchResultRow] = []
            for i, s in enumerate(resp.sessions[:3]):
                ret_rows.append(SearchResultRow(
                    glyph="chat",
                    title=(s.label or s.topic or "(session)")[:60],
                    meta=(s.time_label or "")[:48],
                    score=max(0, min(99, int(round(s.score * 100)))) if s.score else 82,
                    selected=False,
                ))
            # Promote the first inv row to selected only if it exists; else
            # promote the first file / event / return row so the surface
            # always has a focus highlight.
            if not inv_rows:
                first_pool = file_rows or event_rows or ret_rows
                if first_pool:
                    first_pool[0] = SearchResultRow(
                        glyph=first_pool[0].glyph,
                        title=first_pool[0].title,
                        meta=first_pool[0].meta,
                        score=first_pool[0].score,
                        selected=True,
                    )
            if inv_rows:
                groups.append(SearchGroupSpec("Investigations", inv_rows))
            if file_rows:
                groups.append(SearchGroupSpec("Files", file_rows[:4]))
            if ret_rows:
                groups.append(SearchGroupSpec("Returns", ret_rows))
            if event_rows:
                groups.append(SearchGroupSpec("Events", event_rows[:4]))
            if groups:
                return groups

        # Daemon unreachable -- degrade to the file index so search
        # at least shows file matches.
        try:
            hits = self.search_engine.search(q, max_results=8) or []
        except Exception:  # noqa: BLE001
            hits = []
        file_rows = []
        for i, h in enumerate(hits[:5]):
            label = getattr(h, "title", None) or getattr(h, "label", None) \
                or getattr(h, "path", None) or "(untitled)"
            meta = getattr(h, "source", "") or getattr(h, "path", "") or ""
            score = int(round(float(getattr(h, "score", 0.0)) * 100))
            file_rows.append(SearchResultRow(
                glyph="file",
                title=str(label)[:60],
                meta=str(meta)[:48],
                score=max(0, min(99, score)) if score else 80 - i,
                selected=(i == 0),
            ))
        if file_rows:
            groups.append(SearchGroupSpec("Files", file_rows))
        return groups

    # ── resume flow ─────────────────────────────────────────────

    def _on_resume_clicked(self) -> None:
        """Resume / Review pressed on the recovery hero. The Phase 9
        merge keeps both bound to the same target: open the resume
        confirmation state and execute the plan.

        Phase P2 — when the hero was synthesised from a thread or
        the freshest activity row, there's no candidate id so the
        engine-side `/v1/recovery/{id}/restore` path doesn't apply;
        we open `self._pending_targets` directly and synthesise a
        RestoredItem list so the Resume confirmation surface still
        reads correctly."""
        # Snapshot the prior state so `Done` can revert cleanly.
        self._pre_resume_state = STATE_RECOVERY
        if self._pending_cid:
            self._execute_resume_plan()
            return
        if self._pending_targets:
            self._execute_direct_resume()
            return
        # Nothing to restore — flash the empty resume state instead
        # of staying silent on the click.
        self.set_state(STATE_RESUME, restored_items=[])
        self._wire_resume_view()

    def _execute_direct_resume(self) -> None:
        """Open `self._pending_targets` via the OS open helper and
        flash the Resume confirmation surface. Used when the hero
        is synthesised (no candidate id behind it)."""
        targets = list(self._pending_targets)
        items: List[RestoredItem] = []
        for kind, target in targets:
            target = (target or "").strip()
            if not target:
                continue
            ok = False
            try:
                if kind == "path" and not Path(target).exists():
                    items.append(self._step_to_restored_item(kind, target, False))
                    continue
                if kind == "path" and self.event_logger is not None:
                    try:
                        self.event_logger.log_open(target, Path(target).name)
                    except Exception:  # noqa: BLE001
                        pass
                ok = _open_target(kind, target)
            except Exception:  # noqa: BLE001
                ok = False
            items.append(self._step_to_restored_item(kind, target, ok))
        self.set_state(STATE_RESUME, restored_items=items)
        self._wire_resume_view()

    def _on_other_row_clicked(self, idx: int) -> None:
        """Phase P2 — RECENT ACTIVITY rail row clicked. Open the
        row's underlying target via the OS open helper. No state
        change; the row open feels like a Spotlight/Raycast hit."""
        targets = getattr(self, "_row_targets", None) or []
        if idx < 0 or idx >= len(targets):
            return
        target = targets[idx]
        if target is None:
            return
        kind, value = target
        _open_target(kind, value)
        # Log the open the same way file-search does when the user
        # opens a hit from the search surface — so the rail click
        # leaves a breadcrumb in the event log.
        if kind == "path" and self.event_logger is not None:
            try:
                self.event_logger.log_open(value, Path(value).name)
            except Exception:  # noqa: BLE001
                pass
        self.hide()

    def _execute_resume_plan(self) -> None:
        title = self._pending_title
        targets = list(self._pending_targets)
        candidate_id = self._pending_cid
        demo = bool(self._pending_demo)

        if demo:
            # Demo never reaches the engine.
            try:
                from app.core import demo_mode
                demo_mode.dismiss()
            except Exception:  # noqa: BLE001
                pass
            items = self._targets_to_restored_items(targets, all_ok=True)
            self.set_state(STATE_RESUME, restored_items=items)
            self._wire_resume_view()
            QTimer.singleShot(400, self._refresh_idle_state)
            return

        try:
            plan = self.api_client.recovery_restore(candidate_id, timeout=1.0)
        except Exception:  # noqa: BLE001
            plan = None

        items: List[RestoredItem] = []
        if plan is None or not getattr(plan, "steps", None):
            # No plan -- enter resume state with an empty list so
            # the user gets explicit feedback rather than silence.
            self.set_state(STATE_RESUME, restored_items=items)
            self._wire_resume_view()
            return

        skipped: List[Tuple[str, str, str]] = []
        t0 = time.perf_counter()
        for step in plan.steps:
            target = (step.target or "").strip()
            if not target:
                skipped.append((step.kind, "", "empty"))
                continue
            try:
                if step.kind == "path":
                    if not Path(target).exists():
                        skipped.append((step.kind, target, "missing"))
                        continue
                    if self.event_logger is not None:
                        try:
                            self.event_logger.log_open(target,
                                                       Path(target).name)
                        except Exception:  # noqa: BLE001
                            pass
                ok = _open_target(step.kind, target)
                items.append(self._step_to_restored_item(step.kind, target, ok))
                if not ok:
                    skipped.append((step.kind, target, "open_failed"))
            except Exception as exc:  # noqa: BLE001
                skipped.append((step.kind, target, type(exc).__name__))
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        log.info(
            "resume %s · requested=%d restored=%d skipped=%d ms=%.1f",
            title, len(plan.steps),
            len(plan.steps) - len(skipped), len(skipped), elapsed_ms,
        )
        if _EXPLAIN_RECOVERY and skipped:
            for kind, target, reason in skipped:
                print(f"  · skipped  ({kind})  {target[:80]}  — {reason}")

        self.set_state(STATE_RESUME, restored_items=items)
        self._wire_resume_view()

    def _step_to_restored_item(
        self, kind: str, target: str, ok: bool,
    ) -> RestoredItem:
        if kind == "path":
            label = Path(target).name
            meta = str(Path(target).parent)
            glyph = "file"
            status = "opened" if ok else "missing"
        elif "chat" in (target or "").lower():
            label = target
            meta = "session resumed"
            glyph = "chat"
            status = "opened" if ok else "skipped"
        else:
            label = target
            meta = "browser · new window"
            glyph = "tab"
            status = "restored" if ok else "skipped"
        return RestoredItem(glyph=glyph, label=label[:64],
                            meta=meta[:48], status=status)

    def _targets_to_restored_items(
        self, targets: List[Tuple[str, str]], *, all_ok: bool,
    ) -> List[RestoredItem]:
        out: List[RestoredItem] = []
        for kind, target in targets:
            out.append(self._step_to_restored_item(kind, target, all_ok))
        return out

    def _on_resume_done(self) -> None:
        """Dismiss the Resume state and hide the launcher -- the
        user is now in the editor / browser."""
        self._pending_cid = ""
        self._pending_title = ""
        self._pending_targets = []
        self._pending_demo = False
        # Hide first, then refresh the next time the user opens.
        self.hide()
        QTimer.singleShot(0, self._refresh_idle_state)

    def _on_resume_undo(self) -> None:
        """Reverse the resume. The api_client undo endpoint is the
        engine-side concern; here we just revert to the recovery
        surface and let the engine decide what's recoverable."""
        try:
            self.api_client.recovery_undo(self._pending_cid, timeout=1.0)
        except Exception:  # noqa: BLE001
            pass
        # Revert to the prior idle state.
        self._refresh_idle_state()

    # ── keyboard ────────────────────────────────────────────────

    def _on_escape(self) -> None:
        """Esc handling:
          - in SEARCH state with text: clear the search bar
          - in RESUME state: revert to recovery
          - otherwise: hide the launcher
        """
        st = self.state()
        if st == STATE_SEARCH:
            self.search_bar().clear()
            self._refresh_idle_state()
            return
        if st == STATE_RESUME:
            self._on_resume_undo()
            return
        self.hide()

    def _on_hotkey_one(self) -> None:
        """`1` activates the recovery hero's Resume button when
        the launcher is in STATE_RECOVERY."""
        if self.state() == STATE_RECOVERY:
            self._on_resume_clicked()

    # ── empty-state buttons (Phase P0) ──────────────────────────

    def _on_show_example(self) -> None:
        """Empty-state "Show example" button -- activate demo
        overlay so the user sees a populated launcher
        immediately. The same demo_mode the legacy launcher used."""
        try:
            from app.core import demo_mode
            demo_mode.activate()
        except Exception:  # noqa: BLE001
            pass
        self._refresh_idle_state()

    def _on_start_working(self) -> None:
        """Empty-state "Start working" button -- if demo mode is
        active, dismiss it; otherwise just hide the launcher so
        the user can start capturing. Either way, refresh state."""
        try:
            from app.core import demo_mode
            if demo_mode.is_active():
                demo_mode.dismiss()
        except Exception:  # noqa: BLE001
            pass
        self.hide()

    # ── preview-card open (Phase P0) ────────────────────────────

    def _on_preview_open(self) -> None:
        """The Open ↗ link inside the recovery state's preview
        card. Opens the first path-target the engine surfaced for
        the candidate; falls back to the first URL if the
        candidate is browser-led."""
        targets = list(self._pending_targets)
        file_t = next((t for k, t in targets if k == "path"), None)
        if file_t:
            _open_target("path", file_t)
            return
        url_t = next((t for k, t in targets if k != "path"), None)
        if url_t:
            _open_target("url", url_t)

    # ── key handling ────────────────────────────────────────────

    def keyPressEvent(self, e: QKeyEvent) -> None:  # type: ignore[override]
        if e.key() == Qt.Key.Key_Escape:
            self._on_escape()
            return
        super().keyPressEvent(e)


def _split_title_accent(title: str) -> Tuple[str, str]:
    """Split a thread title into a main phrase + a 1-2 word
    serif-italic accent for the hero. Tries to peel off the
    last word for emphasis; falls back to a generic
    "in progress." accent on short titles."""
    words = (title or "").strip().split()
    if not words:
        return ("Continue", "in progress.")
    if len(words) >= 2:
        return (" ".join(words[:-1]), words[-1] + ".")
    return (words[0], "in progress.")


__all__ = ["LiveLauncher"]
