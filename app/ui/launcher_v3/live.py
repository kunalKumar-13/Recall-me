"""Phase 6K — LiveLauncher (+ Phase 6P resume pipeline).

The v3 widget tree wired to live API data + the existing single-
instance / event-logger contract that `app/main.py` constructs the
launcher with.

Public API mirrors the legacy ``Launcher`` class:

  - ``LiveLauncher(search_engine, event_logger=None)`` constructor
  - ``show_centered() / hide()``               window lifecycle
  - ``invalidate_digest()``                    drop cached digest
  - ``_refresh_idle_state()``                  recompute idle surface
  - ``request_settings``                       Qt signal
  - ``_request_search``                        Qt signal (search input)

The actual data fetch lives in private helpers that read from the
loopback API via `app.core.api_client.APIClient`. When the daemon
isn't reachable (test paths, headless smoke), the loader returns
empty lists and the surface degrades to the EmptyDigest — never
raises.

Keyboard layer:

  - ``1-9``      jump to a digest section / card
  - ``↑ / ↓``    move focus
  - ``Enter``    activate the focused card
  - ``Escape``   hide the launcher

Phase 6P inserts the resume pipeline:

  - ``RecoveryCardV3.restore`` opens ``ResumePreview``
  - The preview's ``accepted`` signal triggers the actual restore
    via ``api_client.recovery_restore`` + per-step OS open
  - Result is announced via ``RestoreToast``
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
# Cost: one `time.perf_counter()` pair when the flag is on,
# otherwise nothing.
_TIMING_DEBUG = bool(os.environ.get("RECALL_DEBUG"))

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from .investigation_panel import InvestigationCardV3
from .minimal import MinimalDigest, MinimalEmpty, MinimalSearchBar, MinimalShell
from .recent_memory import MemoryRow
from .recovery_panel import RecoveryCardV3
from .restore_toast import RestoreToast, _name_for
from .resume_preview import ResumePreview

log = logging.getLogger("recall.ui.launcher_v3.live")


# `RECALL_EXPLAIN_RECOVERY=1` writes per-step skip reasons to stdout
# so a developer can inspect what didn't restore. Same env var the
# legacy launcher honours — kept consistent for parity.
_EXPLAIN_RECOVERY = bool(os.environ.get("RECALL_EXPLAIN_RECOVERY"))


def _short_source(payload: dict, kind: str) -> str:
    """Pick a short, scannable source label for the Recent Memory
    row. Prefers the captured `platform`, falls back to the host,
    and capitalises the first letter so the column reads cleanly
    (e.g. `Chatgpt` → ChatGPT-style abbreviation handled manually
    below for the few well-known platforms)."""
    if kind == "chat_session":
        plat = (payload.get("platform") or payload.get("domain") or "").strip()
        lowered = plat.lower()
        if "claude" in lowered:
            return "Claude"
        if "openai" in lowered or "chatgpt" in lowered:
            return "ChatGPT"
        if "gemini" in lowered:
            return "Gemini"
        if "perplexity" in lowered:
            return "Perplexity"
        return plat.title() or "Chat"
    if kind == "browser_search":
        eng = (payload.get("engine") or payload.get("domain") or "").strip()
        lowered = eng.lower()
        if "google" in lowered:
            return "Google"
        if "duckduckgo" in lowered:
            return "DuckDuckGo"
        if "bing" in lowered:
            return "Bing"
        return eng.title() or "Search"
    if kind == "browser_visit":
        host = (payload.get("domain") or "").strip()
        if not host:
            return "Tab"
        # Strip a leading www. + the TLD for compactness.
        host = host.split(".")[0] if "." in host else host
        return host.title() if host.islower() else host
    if kind in ("open", "reveal"):
        return "File"
    if kind == "desktop_window":
        return (payload.get("app") or "Desktop").title()
    return kind.replace("_", " ").title()


def _short_label(payload: dict, kind: str) -> str:
    """The Recent Memory row's right-hand label."""
    if kind == "browser_search":
        return (payload.get("query") or "search").strip()
    if kind in ("browser_visit", "chat_session", "desktop_window"):
        return (payload.get("title") or payload.get("domain") or "").strip()
    if kind in ("open", "reveal"):
        path = (payload.get("path") or "").strip()
        return path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] or path
    if kind == "query":
        return (payload.get("text") or "").strip()
    return ""


def _load_recent_memory(max_rows: int = 5) -> list:
    """Load the most-recent events from disk and map them into
    `MemoryRow` records. The launcher renders these directly; the
    `recall capture status` CLI surfaces the same data path."""
    try:
        from app.core.events import EventStore
        from app.core.config import EVENTS_DIR
    except Exception:  # noqa: BLE001
        return []
    store = EventStore(EVENTS_DIR)
    rows: list = []
    seen = 0
    from datetime import datetime, timezone
    # `iter_events(days=2)` yields newest-first across today + yesterday
    # so a late-evening launcher open still has a populated rail when
    # today has zero events.
    for ev in store.iter_events(days=2):
        payload = ev.payload or {}
        source = _short_source(payload, ev.kind)
        label = _short_label(payload, ev.kind)
        if not source or not label:
            continue
        ts = ev.ts_epoch()
        if ts <= 0:
            continue
        t = datetime.fromtimestamp(ts, tz=timezone.utc)
        rows.append(MemoryRow(
            time=t.strftime("%H:%M"),
            source=source[:12],
            label=label,
        ))
        seen += 1
        if seen >= max_rows:
            break
    return rows


def _load_trust_counts() -> tuple:
    """Return `(events_today, investigations)` for the trust row.
    Same disk reads the Phase 7D `recall capture status` CLI uses,
    so the launcher's pill values match the CLI's report."""
    events_today = 0
    investigations = 0
    try:
        from app.core.events import EventStore
        from app.core.config import EVENTS_DIR, CONFIG_DIR
        from datetime import datetime, timezone
        import json
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        store = EventStore(EVENTS_DIR)
        for _ in store.iter_events_for_date(today):
            events_today += 1
        threads_path = CONFIG_DIR / "threads.json"
        if threads_path.exists():
            try:
                data = json.loads(threads_path.read_text(encoding="utf-8"))
                investigations = len(data.get("threads") or [])
            except (OSError, ValueError, TypeError):
                investigations = 0
    except Exception:  # noqa: BLE001
        pass
    return events_today, investigations


def _extract_gap_clause(preview_caption: str) -> Optional[str]:
    """Pluck the *returned after Nd* / *reopened after a N-day gap*
    clause from the engine's deterministic preview caption so the
    Continue document's body can carry it as its last bullet.
    Returns None when no gap clause is present."""
    if not preview_caption:
        return None
    for part in preview_caption.split("·"):
        part = part.strip()
        lowered = part.lower()
        if "gap" in lowered or "returned" in lowered or "reopened" in lowered:
            return part
    return None


def _open_target(kind: str, target: str) -> bool:
    """Open one restoration target through the OS handler. Returns
    True only when the open actually dispatched — False when the
    file path is missing or the launch raised.

    URLs are handed straight to the OS default browser; file paths
    are existence-checked first so a phantom file (moved/deleted
    since capture) doesn't blow up the chain.
    """
    if not target:
        return False
    if kind == "path":
        p = Path(target)
        if not p.exists():
            return False
        try:
            if sys.platform == "win32":
                os.startfile(str(p))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(p)], check=False)
            else:
                subprocess.run(["xdg-open", str(p)], check=False)
            return True
        except Exception:
            return False
    # URL path.
    try:
        if sys.platform == "win32":
            os.startfile(target)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", target], check=False)
        else:
            subprocess.run(["xdg-open", target], check=False)
        return True
    except Exception:
        return False


class LiveLauncher(QWidget):
    """The v3 launcher, wired to live data.

    Construct exactly the same way the legacy launcher was —
    `LiveLauncher(search_engine, event_logger)` — and the existing
    `app/main.py` lifecycle (global hotkey, tray icon, single-
    instance lock) hooks in unchanged.
    """

    request_settings = pyqtSignal()
    _request_search = pyqtSignal(str)

    # Phase 7E — Launcher Final Product Pass. 700 × 500, hard
    # clamp. Single warm page outside; one white inner card with
    # radius 24 + 24-px padding holds search + Continue + Recent
    # Memory + OTHER WORK + trust row, all on one surface.
    DEFAULT_SIZE = (700, 500)

    def __init__(
        self,
        search_engine,
        event_logger=None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.search_engine = search_engine
        self.event_logger = event_logger
        # Import lazily so a Qt-free `from app.ui.launcher import
        # Launcher` doesn't pull the API client into env vars.
        from app.core.api_client import APIClient
        self.api_client = APIClient(base_url="http://127.0.0.1:4545")

        self.setObjectName("launcher_v3_live")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        # Phase 6R — *No transparency, no blur, no glass*. The
        # launcher paints a solid warm page; the translucency flag
        # is off so the page reads as paper, not a floating panel.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        # Hard clamp — directive: min = max.
        self.setFixedSize(*self.DEFAULT_SIZE)

        # Phase 6L — single-column composition. Search bar lives at
        # the top of the shell; the centre stack swaps between the
        # populated digest and the empty surface.
        self._search = MinimalSearchBar()
        self._search.query_changed.connect(self._on_query_changed)
        # Phase 7B.1 — the search row owns the settings + close
        # icons (rendered on the right edge of the bar). Settings
        # forwards to the legacy `request_settings` signal so the
        # existing app/main.py wiring picks it up; close hides the
        # launcher.
        self._search.request_settings.connect(self.request_settings.emit)
        self._search.request_close.connect(self.hide)

        self._digest = MinimalDigest()
        self._empty = MinimalEmpty()
        self._empty.show_example.connect(self._on_show_example)
        self._empty.start_normally.connect(self._on_start_normally)

        self._center_stack = QStackedLayout()
        center_wrap = QWidget()
        center_wrap.setLayout(self._center_stack)
        self._center_stack.addWidget(self._empty)
        self._center_stack.addWidget(self._digest)

        self._shell_widget = MinimalShell(center_wrap, search=self._search)
        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.setSpacing(0)
        wrap.addWidget(self._shell_widget)

        # Phase 6P — resume pipeline overlays. The preview floats on
        # top of the digest; the toast pins to the bottom of the
        # window. Both parented to `self` so they sit above the
        # stacked center.
        self._preview = ResumePreview(self)
        self._preview.accepted.connect(self._on_preview_accept)
        self._preview.cancelled.connect(self._on_preview_cancel)

        self._toast = RestoreToast(self)

        # The candidate currently being previewed. We hold the full
        # set of suggested_targets so the accept path doesn't have to
        # call back into the API just to enumerate them.
        self._pending_targets: List[Tuple[str, str]] = []
        self._pending_title: str = ""
        self._pending_cid: str = ""

        # Keyboard layer — `Escape` hides, `Ctrl/Cmd+K` focuses
        # search, `1` resumes the visible Continue document. The
        # 2-9 hotkeys from 6R/7B are gone: 7B.1 surfaces only one
        # Continue document (single-focus tool), there's nothing
        # to navigate to.
        QShortcut(QKeySequence("Esc"), self, activated=self._on_escape)
        QShortcut(
            QKeySequence("Ctrl+K"), self,
            activated=lambda: self._search.focus(),
        )
        QShortcut(
            QKeySequence("Meta+K"), self,
            activated=lambda: self._search.focus(),
        )
        QShortcut(
            QKeySequence("1"), self,
            activated=lambda: self._activate_card(0),
        )

        self._refresh_idle_state()

    # ── lifecycle (legacy API mirror) ────────────────────────────────

    def show_centered(self) -> None:
        """Show the launcher centred on the active screen. The legacy
        launcher does deep multi-monitor work; the v3 keeps it simple
        and centres on the primary screen."""
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
        # Refresh on every show so a digest that filled while the
        # launcher was hidden surfaces immediately.
        QTimer.singleShot(0, self._refresh_idle_state)
        if _TIMING_DEBUG:
            ms = round((time.perf_counter() - t0) * 1000, 1)
            print(
                f"[recall.launcher.timing] show_centered  {ms} ms  "
                f"(budget 400)",
                file=sys.stderr, flush=True,
            )

    def invalidate_digest(self) -> None:
        """Drop any cached payload; the next `_refresh_idle_state`
        re-fetches from the API."""
        self._cached_digest = None

    def _refresh_idle_state(self) -> None:
        """Pick between empty / digest based on what the daemon
        returns. Demo overlay is honoured: when `demo_mode.is_active()`
        and the engine is otherwise empty, the digest path receives
        the demo payload via `_load_digest`."""
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
            self._show_empty()
        else:
            self._populate_digest()
            self._show_digest()

    # ── center-stack swap ───────────────────────────────────────────

    def _show_empty(self) -> None:
        self._center_stack.setCurrentIndex(0)

    def _show_digest(self) -> None:
        self._center_stack.setCurrentIndex(1)

    # ── data load ───────────────────────────────────────────────────

    def _demo_active(self) -> bool:
        try:
            from app.core import demo_mode
            return demo_mode.is_active()
        except Exception:  # noqa: BLE001
            return False

    def _populate_digest(self) -> None:
        if self._demo_active():
            self._populate_demo()
            return
        # Live data path. The api_client never raises on a dead
        # daemon — it returns [] / None — so this stays calm.
        try:
            recoveries = self.api_client.recovery_recent(n=1) or []
        except Exception:  # noqa: BLE001
            recoveries = []
        try:
            threads = self.api_client.threads_recent(n=3) or []
        except Exception:  # noqa: BLE001
            threads = []

        # Phase 6O HIGH-only gate + Phase 6Q ledger demotion (see
        # `signals.ledger_flagged`). Phase 7E: the launcher now
        # renders the Continue hero + Recent Memory + OTHER WORK
        # together — single surface, no swap to an empty view.
        # The hero is hidden when no HIGH recovery clears the gate;
        # OTHER WORK + Recent Memory carry the surface.
        hero: Optional[RecoveryCardV3] = None
        if recoveries:
            c = recoveries[0]
            targets = list(getattr(c, "suggested_targets", []) or [])
            n_targets = len(targets)
            flagged = bool(
                (getattr(c, "signals", None) or {}).get("ledger_flagged", 0.0)
            )
            if n_targets >= 4 and not flagged:
                hero = self._recovery_to_v3(c, n_targets, targets)

        inv_cards = [self._thread_to_v3(t) for t in threads[:3]]
        memory_rows = _load_recent_memory(max_rows=5)
        events_today, investigations = _load_trust_counts()

        # Phase 7E: always show the digest. The Recent Memory + OTHER
        # WORK sections handle the empty-recovery case; the empty
        # surface only fires when the daemon is genuinely empty.
        self._digest.populate(
            hero=hero,
            memory=memory_rows,
            investigations=inv_cards,
        )
        self._shell_widget.trust.set_counts(events_today, investigations)
        self._show_digest()

    def _populate_demo(self) -> None:
        from app.core import demo_mode
        payload = demo_mode.demo_payload()
        rec = payload["recovery"]
        # The demo payload's suggested_targets are synthesized so
        # the preview body + the hero's chip row have rows to
        # render. Tabs + files are the canonical mix for the
        # WebSocket story.
        demo_targets: List[Tuple[str, str]] = []
        for url in rec.get("urls", []) or []:
            demo_targets.append(("url", url))
        for path in rec.get("files", []) or []:
            demo_targets.append(("path", path))
        hero = RecoveryCardV3(
            candidate_id=rec["id"],
            title=rec["title"],
            targets=demo_targets,
            extra_clause=_extract_gap_clause(rec.get("preview_caption", "")),
            n_targets=rec["tab_count"] + rec["file_count"],
        )
        self._wire_hero_restore(hero, rec["title"], demo_targets, demo=True)
        inv_cards: List[InvestigationCardV3] = []
        for inv in payload["investigations"]:
            inv_cards.append(InvestigationCardV3(
                inv["id"], inv["id"], inv["title"],
                last_seen=str(inv.get("last_seen", "")) or "active",
                strong=len(inv.get("surface_types") or []) >= 3,
            ))
        # Phase 7E — demo gets a synthetic Recent Memory rail built
        # from the demo payload's timeline so the launcher's new
        # section reads identically to a live populated state.
        memory_rows: list = []
        from datetime import datetime, timezone
        for ev in payload.get("timeline", []):
            t = datetime.fromtimestamp(float(ev.get("ts", 0.0)), tz=timezone.utc)
            memory_rows.append(MemoryRow(
                time=t.strftime("%H:%M"),
                source=str(ev.get("detail", ""))[:12].title(),
                label=str(ev.get("label", "")),
            ))
        self._digest.populate(
            hero=hero,
            memory=memory_rows[:5],
            investigations=inv_cards,
        )
        self._shell_widget.trust.set_counts(
            len(payload.get("timeline", [])),
            len(payload.get("investigations", [])),
        )

    def _recovery_to_v3(
        self,
        c,
        n_targets: int,
        targets: List[Tuple[str, str]],
    ) -> RecoveryCardV3:
        title = getattr(c, "title", "") or "(untitled)"
        cid = getattr(c, "id", "")
        # Phase 7B.1 — the Continue document needs the *returned
        # after Nd* clause from the engine's preview caption so
        # the body's last bullet reads as engagement context
        # rather than a bare count. Extract the clause if present;
        # otherwise the body is just file/tab/chat/search counts.
        caption = getattr(c, "preview_caption", "") or ""
        extra = _extract_gap_clause(caption)
        card = RecoveryCardV3(
            candidate_id=cid,
            title=title,
            targets=targets,
            extra_clause=extra,
            n_targets=n_targets,
        )
        self._wire_hero_restore(card, title, targets, demo=False)
        return card

    def _wire_hero_restore(
        self,
        card: RecoveryCardV3,
        title: str,
        targets: List[Tuple[str, str]],
        *,
        demo: bool,
    ) -> None:
        """Bind the card's `restore` signal to the preview-open path.
        Capture `title` + `targets` in the closure so the preview
        opens with the right payload — and the plan execution doesn't
        need to round-trip to the API just to enumerate steps."""
        def _open_preview(cid: str, _t: str, _n: int) -> None:
            self._open_preview(cid, title, targets, demo=demo)
        card.restore.connect(_open_preview)

    def _thread_to_v3(self, t) -> InvestigationCardV3:
        # Phase 7E — the OTHER WORK row carries a `last_seen` caption
        # (right-aligned mono) + a strength dot. `updated_at` is the
        # thread's most-recent event timestamp; humanize_age gives us
        # *3d*, *5d*, *1w* — same column the audit's mock fixtures
        # show.
        last_seen = ""
        try:
            from app.core.events import humanize_age
            ts = float(getattr(t, "updated_at", 0.0) or 0.0)
            if ts > 0:
                last_seen = humanize_age(ts)
        except Exception:  # noqa: BLE001
            pass
        surfaces = list(getattr(t, "surface_types", []) or [])
        return InvestigationCardV3(
            getattr(t, "id", ""),
            getattr(t, "topic_key", "") or "",
            getattr(t, "title", "") or "(untitled)",
            last_seen=last_seen,
            strong=len(surfaces) >= 3,
        )

    # ── input ────────────────────────────────────────────────────────

    def _on_query_changed(self, q: str) -> None:
        # Phase 6K wires the typing path to the legacy search engine
        # only via a signal. The full inline-results panel is a
        # follow-up (the directive's search_panel.py is built but
        # not wired to live episodic results in this phase).
        self._request_search.emit(q)

    def _activate_card(self, idx: int) -> None:
        # Phase 6O — `1` targets the hero (when shown); `2-4`
        # target the n-th investigation title. The OTHER WORK
        # row caps at 3, so hotkeys 5-9 never have a target.
        cards: List[QWidget] = []
        if self._digest._hero is not None:  # noqa: SLF001
            cards.append(self._digest._hero)  # noqa: SLF001
        cards.extend(self._digest.row._titles)  # noqa: SLF001
        if 0 <= idx < len(cards):
            cards[idx].setFocus(Qt.FocusReason.ShortcutFocusReason)

    # ── Phase 6P resume pipeline ────────────────────────────────────

    def _open_preview(
        self,
        candidate_id: str,
        title: str,
        targets: List[Tuple[str, str]],
        *,
        demo: bool,
    ) -> None:
        """Show the preview overlay. Captures the candidate so the
        accept path can execute without re-asking the API."""
        self._pending_cid = candidate_id
        self._pending_title = title
        self._pending_targets = list(targets)
        self._pending_demo = demo
        self._preview.open(candidate_id, title, targets)
        self._position_preview()

    def _position_preview(self) -> None:
        """Centre the preview horizontally; pin vertically so the
        bottom of the card sits ~24 px above the window bottom."""
        if not self._preview.isVisible():
            return
        self._preview.adjustSize()
        x = (self.width() - self._preview.width()) // 2
        y = max(60, self.height() - self._preview.height() - 28)
        self._preview.move(x, y)

    def _position_toast(self) -> None:
        if not self._toast.isVisible():
            return
        self._toast.adjustSize()
        x = (self.width() - self._toast.width()) // 2
        y = self.height() - self._toast.height() - 18
        self._toast.move(x, y)

    def _on_preview_cancel(self) -> None:
        self._pending_cid = ""
        self._pending_title = ""
        self._pending_targets = []

    def _on_preview_accept(self, candidate_id: str, title: str) -> None:
        """The user confirmed Resume. Execute the plan and announce
        the result via the toast."""
        targets = list(self._pending_targets)
        demo = bool(getattr(self, "_pending_demo", False))
        self._pending_cid = ""
        self._pending_title = ""
        self._pending_targets = []
        self._pending_demo = False

        if demo:
            # Demo mode never reaches into the engine. We acknowledge
            # the click with a toast but make no OS calls and dismiss
            # the overlay so the user lands on the real (still empty)
            # engine state.
            try:
                from app.core import demo_mode
                demo_mode.dismiss()
            except Exception:  # noqa: BLE001
                pass
            self._flash_toast_success([_name_for(k, t) for k, t in targets[:3]],
                                       requested=len(targets), missing=0)
            QTimer.singleShot(400, self._refresh_idle_state)
            return

        # Resolve the plan. The engine returns it ordered files →
        # chats → tabs → searches.
        try:
            plan = self.api_client.recovery_restore(candidate_id, timeout=1.0)
        except Exception:  # noqa: BLE001
            plan = None

        if plan is None:
            self._flash_toast_no_engine()
            return
        if not plan.steps:
            self._flash_toast_failure(0)
            return

        restored_names: List[str] = []
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
                            self.event_logger.log_open(target, Path(target).name)
                        except Exception:  # noqa: BLE001
                            pass
                ok = _open_target(step.kind, target)
                if ok:
                    restored_names.append(_name_for(step.kind, target))
                else:
                    skipped.append((step.kind, target, "open_failed"))
            except Exception as exc:  # noqa: BLE001
                skipped.append((step.kind, target, type(exc).__name__))
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        log.info(
            "resume %s · requested=%d restored=%d skipped=%d ms=%.1f",
            title, len(plan.steps), len(restored_names), len(skipped), elapsed_ms,
        )
        if _EXPLAIN_RECOVERY and skipped:
            for kind, target, reason in skipped:
                print(f"  · skipped  ({kind})  {target[:80]}  — {reason}")

        if restored_names:
            self._flash_toast_success(
                restored_names[:3],
                requested=len(plan.steps),
                missing=len(skipped),
            )
            # Give the toast a moment, then hide. The user is now in
            # the editor / browser — the launcher shouldn't be on top.
            QTimer.singleShot(400, self.hide)
        else:
            self._flash_toast_failure(len(skipped))

    def _flash_toast_success(
        self, names: List[str], *, requested: int, missing: int,
    ) -> None:
        self._toast.flash_success(names, requested=requested, missing=missing)
        self._position_toast()

    def _flash_toast_failure(self, missing: int) -> None:
        self._toast.flash_failure(missing)
        self._position_toast()

    def _flash_toast_no_engine(self) -> None:
        self._toast.flash_no_engine()
        self._position_toast()

    def _on_escape(self) -> None:
        """Esc closes the preview first if visible; otherwise hides
        the whole launcher. Phase 6R removed the *Why this?* sheet
        from the cascade — see `archive/launcher-debt/why_sheet_6q.py`."""
        if self._preview.isVisible():
            self._preview.close_preview()
            self._on_preview_cancel()
            return
        self.hide()

    def _on_show_example(self) -> None:
        try:
            from app.core import demo_mode
            demo_mode.activate()
        except Exception:  # noqa: BLE001
            pass
        self._refresh_idle_state()

    def _on_start_normally(self) -> None:
        try:
            from app.core import demo_mode
            demo_mode.dismiss()
        except Exception:  # noqa: BLE001
            pass
        self._refresh_idle_state()

    # ── geometry hooks ──────────────────────────────────────────────

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        self._position_preview()
        self._position_toast()

    # ── key handling ────────────────────────────────────────────────

    def keyPressEvent(self, e: QKeyEvent) -> None:  # type: ignore[override]
        if e.key() == Qt.Key.Key_Escape:
            self._on_escape()
            return
        super().keyPressEvent(e)


__all__ = ["LiveLauncher"]
