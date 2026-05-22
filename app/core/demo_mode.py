"""Phase 6D — DemoMode state machine.

Owns the user's *choice* about whether the popup and the launcher
should show the canned demo experience on top of their real engine
state. The state lives at `~/.recall/demo.json` so the launcher and
the extension (via the API) agree on a single source of truth.

Five states:

- `disabled`   demo never offered (set by users who want zero
               first-run nudges; not yet wired to a setting).
- `available`  first-run default. The empty surface shows a
               *Show example* affordance.
- `active`     the user clicked Show example. Demo content overlays
               the empty engine state.
- `dismissed`  the user clicked Dismiss on the demo banner, OR a
               real event arrived (auto-transition; the demo
               disappears the moment real data exists).
- `completed`  reserved for a future "demo finished its arc"
               state when the user has clicked a demo card. Not
               currently distinguished from `dismissed`.

Rules:

- Real events override demo. The ingest hook calls
  :func:`mark_real_activity` after every successful ingest; if
  state was `active` it flips to `dismissed`. Demo never wins
  over reality.
- The fixture payload (:func:`demo_payload`) is fully deterministic
  — three threads (WebSocket / Proposal draft / Research),
  one recovery candidate, eight timeline events. No randomness,
  no AI, no generated text. Mirrors :mod:`app.core.demo_seed`'s
  scripted data.
- The state file is human-readable JSON. Deleting it returns the
  user to `available`.

This module has **no engine dependency**: it does not read events,
sessions, threads, recovery, or evolution. It is a thin overlay
that the API + UI consult — the engine itself never knows demo
mode exists.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import CONFIG_DIR

log = logging.getLogger("recall.core.demo_mode")

DEMO_FILE: Path = CONFIG_DIR / "demo.json"

# Allowed state vocabulary. Anything else in the file is treated as
# `available` so a corrupted file degrades gracefully.
_STATES = ("disabled", "available", "active", "dismissed", "completed")
_DEFAULT_STATE = "available"


# --------------------------------------------------------------- storage


def _read_file() -> Dict[str, Any]:
    """Return the persisted state dict, or an empty dict if the file
    is missing or unreadable. Never raises."""
    try:
        return json.loads(DEMO_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_file(data: Dict[str, Any]) -> None:
    """Persist atomically. Best-effort — failures are logged, not
    raised, because the rest of the product must keep working
    when the disk is full."""
    try:
        DEMO_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = DEMO_FILE.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp.replace(DEMO_FILE)
    except OSError as e:
        log.warning("demo_mode: persist failed (%s)", e)


# --------------------------------------------------------------- state


def state() -> str:
    """Current state. Defaults to `available` if the file is
    missing or its content is not recognised."""
    raw = _read_file().get("state")
    if isinstance(raw, str) and raw in _STATES:
        return raw
    return _DEFAULT_STATE


def is_active() -> bool:
    """Convenience: True iff the demo overlay should currently be
    rendered. Used by the API service-layer to decide whether
    to short-circuit to the demo payload."""
    return state() == "active"


def _set(new_state: str, *, extra: Optional[Dict[str, Any]] = None) -> str:
    """Internal setter. Persists `state` + `*_at` timestamps and
    returns the new state. Idempotent — re-setting the same state
    is cheap and writes nothing."""
    if new_state not in _STATES:
        raise ValueError(f"invalid demo state: {new_state!r}")
    current = _read_file()
    if current.get("state") == new_state and not extra:
        return new_state
    payload = dict(current)
    payload["state"] = new_state
    payload[f"{new_state}_at"] = int(time.time())
    if extra:
        payload.update(extra)
    _write_file(payload)
    log.info("demo_mode: state -> %s", new_state)
    return new_state


def activate() -> str:
    """User clicked *Show example*. Demo overlay turns on."""
    return _set("active")


def dismiss() -> str:
    """User clicked the demo banner's *Dismiss* OR a real event
    arrived while the demo was active."""
    return _set("dismissed")


def complete() -> str:
    """The demo's arc finished (e.g., the user clicked the demo's
    Resume button). Currently treated like `dismissed` by
    consumers; the state is preserved so a future surface can
    differentiate."""
    return _set("completed")


def disable() -> str:
    """Hard-off — never show the demo affordance again."""
    return _set("disabled")


def mark_real_activity() -> None:
    """Called by the ingest path after every successful event.
    If the demo was active, flip to `dismissed` so the next read
    surfaces real engine data. No-op in every other state.

    This is the *real events override demo* rule. The launcher
    and extension poll for state changes and fade the demo out
    on their next refresh.
    """
    if state() == "active":
        dismiss()


# --------------------------------------------------------------- fixture
#
# The canonical demo payload. Everything below is hand-written; no
# AI generation, no random selection, no engine touch. The three
# threads + one recovery + eight timeline events mirror the
# scripted stories in :mod:`app.core.demo_seed` so a future seed-
# backed mode (where the launcher actually reads from `events-demo/`)
# would show the same surface.


_RECOVERY = {
    "id": "demo-recovery-websocket",
    "thread_id": "demo-thread-websocket",
    "title": "WebSocket retry debugging",
    "preview_caption": "2 tabs · 2 files · reopened after a 2-day gap",
    "confidence": "high",
    "tab_count": 2,
    "file_count": 2,
    "gap_label": "2-day gap",
    "urls": [
        "https://stackoverflow.com/questions/57294879/websocket-retry-on-disconnect-best-practices",
        "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket",
    ],
    "files": [
        "~/code/ws-retry/client.py",
        "~/code/ws-retry/backoff.py",
    ],
    "chips": ["2 tabs", "2 files", "2d gap", "interrupted"],
}


_INVESTIGATIONS = [
    {
        "id": "demo-thread-websocket",
        "title": "WebSocket retry debugging",
        "timeline_summary": "4 sessions · 3 days",
        "surface_types": ["browser_visit", "browser_search", "open", "chat_session"],
    },
    {
        "id": "demo-thread-proposal",
        "title": "Healthcare pitch — proposal draft",
        "timeline_summary": "3 sessions · 10 days",
        "surface_types": ["open", "browser_visit", "chat_session"],
    },
    {
        "id": "demo-thread-rlhf",
        "title": "RLHF reward shaping",
        "timeline_summary": "3 sessions · 1 week",
        "surface_types": ["browser_visit", "browser_search"],
    },
]


# Eight timeline events. Times are seconds-ago at read time so
# `HH:MM` labels render against the user's clock; pure display,
# no scoring, no engine dependency.
_TIMELINE = [
    # WebSocket story — newest first
    {"kind": "browser_search",  "ago": 5 * 60,
     "label": "websocket backoff jitter", "detail": "google.com"},
    {"kind": "browser_visit",   "ago": 18 * 60,
     "label": "WebSocket — MDN", "detail": "developer.mozilla.org"},
    {"kind": "open",            "ago": 32 * 60,
     "label": "backoff.py", "detail": "~/code/ws-retry/"},
    {"kind": "chat_session",    "ago": 60 * 60,
     "label": "Backoff with jitter — review", "detail": "claude.ai"},
    # Proposal story
    {"kind": "open",            "ago": 95 * 60,
     "label": "notes.md", "detail": "~/Documents/healthcare-startup/"},
    {"kind": "browser_visit",   "ago": 120 * 60,
     "label": "Y Combinator — Healthcare companies", "detail": "ycombinator.com"},
    # Research story
    {"kind": "browser_search",  "ago": 150 * 60,
     "label": "rlhf reward shaping", "detail": "google.com"},
    {"kind": "browser_visit",   "ago": 180 * 60,
     "label": "Training language models to follow instructions...",
     "detail": "arxiv.org"},
]


def demo_payload(now: Optional[float] = None) -> Dict[str, Any]:
    """Return the canonical demo overlay payload.

    Consumers (the API service-layer and the UI test fixtures) hand
    this back as if it had come out of the engine. The data is
    fully deterministic apart from the *absolute* timestamps, which
    are derived from `now` so the rail's `HH:MM` labels read in the
    user's current hour-of-day. No randomness, no AI, no engine
    state read.
    """
    if now is None:
        now = time.time()
    timeline: List[Dict[str, Any]] = []
    for ev in _TIMELINE:
        ts = float(now) - float(ev["ago"])
        timeline.append({
            "kind": ev["kind"],
            "ts": ts,
            "label": ev["label"],
            "detail": ev["detail"],
        })
    return {
        "recovery": dict(_RECOVERY),
        "investigations": [dict(t) for t in _INVESTIGATIONS],
        "timeline": timeline,
        "trust": {
            "banner_title": "Example data",
            "banner_body": "Nothing here came from your device.",
        },
        "generated_at": int(now),
    }


__all__ = [
    "DEMO_FILE",
    "state",
    "is_active",
    "activate",
    "dismiss",
    "complete",
    "disable",
    "mark_real_activity",
    "demo_payload",
]
