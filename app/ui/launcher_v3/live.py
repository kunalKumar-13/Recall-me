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
            return

        self._populate_recovery_state()

    def _populate_recovery_state(self) -> None:
        """Build a RecoveryProps + PreviewProps + OtherWorkRow[]
        triple from engine data, then enter STATE_RECOVERY."""
        if self._demo_active():
            self._populate_demo()
            return
        try:
            recoveries = self.api_client.recovery_recent(n=1) or []
        except Exception:  # noqa: BLE001
            recoveries = []
        try:
            threads = self.api_client.threads_recent(n=3) or []
        except Exception:  # noqa: BLE001
            threads = []

        # HIGH-only gate (Phase 6O) + ledger-flag demotion (Phase 6Q).
        hero = None
        if recoveries:
            c = recoveries[0]
            targets = list(getattr(c, "suggested_targets", []) or [])
            n_targets = len(targets)
            flagged = bool(
                (getattr(c, "signals", None) or {}).get("ledger_flagged", 0.0)
            )
            if n_targets >= 4 and not flagged:
                hero = c

        if hero is None:
            # No hero but daemon has events -- show empty for now.
            # (Future: STATE_RECOVERY w/ hero=None renders just the
            # Other work rail.)
            self.set_state(STATE_EMPTY)
            return

        targets = list(getattr(hero, "suggested_targets", []) or [])
        self._pending_cid = getattr(hero, "id", "")
        self._pending_title = getattr(hero, "title", "") or "(untitled)"
        self._pending_targets = list(targets)
        self._pending_demo = False

        recovery_props = self._engine_to_recovery_props(hero, targets)
        preview_props = self._engine_to_preview_props(hero)
        other_work = [self._thread_to_other_row(t) for t in threads[:3]]

        self.set_state(
            STATE_RECOVERY,
            recovery=recovery_props,
            preview=preview_props,
            other_work=other_work,
        )
        self._wire_recovery_view()

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
        """Hook the RecoveryView's resume + review signals to the
        engine-side restore flow. Called after every
        ``set_state(STATE_RECOVERY, ...)``."""
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
        string -> back to the idle surface."""
        self._request_search.emit(q)
        if not q.strip():
            # Restore the prior state.
            self._refresh_idle_state()
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
        """Engine -> SearchGroupSpec[] adapter. Phase 10B keeps this
        modest: the engine doesn't yet return a 4-bucket result
        shape, so we map the available hits onto the design's
        groups (Investigation / Files / Returns / Events)."""
        try:
            hits = self.search_engine.search(q, max_results=10) or []
        except Exception:  # noqa: BLE001
            hits = []
        groups: List[SearchGroupSpec] = []
        files_rows: List[SearchResultRow] = []
        for i, h in enumerate(hits[:5]):
            label = getattr(h, "title", None) or getattr(h, "label", None) \
                or getattr(h, "path", None) or "(untitled)"
            meta = getattr(h, "source", "") or getattr(h, "path", "") or ""
            score = int(round(float(getattr(h, "score", 0.0)) * 100))
            files_rows.append(SearchResultRow(
                glyph="file",
                title=str(label)[:60],
                meta=str(meta)[:48],
                score=max(0, min(99, score)) if score else 80 - i,
                selected=(i == 0),
            ))
        if files_rows:
            groups.append(SearchGroupSpec("Files", files_rows))
        # If we got nothing, show the design fixture so the surface
        # still reads as a populated search.
        if not groups:
            return []  # darkframe's default fixture fires
        return groups

    # ── resume flow ─────────────────────────────────────────────

    def _on_resume_clicked(self) -> None:
        """Resume / Review pressed on the recovery hero. The Phase 9
        merge keeps both bound to the same target: open the resume
        confirmation state and execute the plan."""
        if not self._pending_cid:
            return
        # Snapshot the prior state so `Done` can revert cleanly.
        self._pre_resume_state = STATE_RECOVERY
        self._execute_resume_plan()

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
