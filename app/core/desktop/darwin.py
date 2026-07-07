"""Phase 6M sibling — foreground window probe (macOS).

Same contract as ``windows.py``: one call returns the currently
focused app + window title, or ``None``. Uses pyobjc's AppKit for
the frontmost application and Quartz's window list for the title —
both already ship with the desktop app for the tray/launcher stack.

Privacy contract restated for macOS:

  - ``NSWorkspace.frontmostApplication`` exposes only the app's
    name, pid and bundle path — never document contents.
  - The window *title* comes from ``kCGWindowName``, which macOS
    only reveals when the user has granted Screen Recording
    permission. Without it we fall back to the app name, so the
    layer degrades to app-level granularity instead of silently
    requesting scarier permissions.
  - Same aggregation rules as Windows apply downstream: blocks
    under the minimum focus duration never reach the JSONL.
"""

from __future__ import annotations

import sys
from typing import Optional

from .windows import ForegroundWindow

_IS_DARWIN = sys.platform == "darwin"

_APPKIT = None
_QUARTZ = None
if _IS_DARWIN:
    try:  # pragma: no cover — import availability is machine-specific
        import AppKit as _APPKIT  # type: ignore[no-redef]
        import Quartz as _QUARTZ  # type: ignore[no-redef]
    except Exception:  # noqa: BLE001 — no pyobjc → graceful no-op
        _APPKIT = None
        _QUARTZ = None


def is_supported() -> bool:
    """True when we're on macOS and pyobjc is importable."""
    return _IS_DARWIN and _APPKIT is not None and _QUARTZ is not None


def _frontmost_window_title(pid: int) -> str:
    """Best-effort title of the frontmost window owned by `pid`.

    The on-screen window list is ordered front-to-back, so the first
    layer-0 window owned by the pid is the focused one. ``kCGWindowName``
    is absent without Screen Recording permission — callers fall back
    to the app name."""
    if _QUARTZ is None:
        return ""
    try:
        wl = _QUARTZ.CGWindowListCopyWindowInfo(
            _QUARTZ.kCGWindowListOptionOnScreenOnly
            | _QUARTZ.kCGWindowListExcludeDesktopElements,
            _QUARTZ.kCGNullWindowID,
        )
        for w in wl or []:
            if int(w.get("kCGWindowOwnerPID", -1)) != pid:
                continue
            if int(w.get("kCGWindowLayer", 1)) != 0:
                continue
            return str(w.get("kCGWindowName") or "")
    except Exception:  # noqa: BLE001 — a failed tick is silent
        pass
    return ""


def probe_foreground() -> Optional[ForegroundWindow]:
    """Return the currently focused window or ``None``."""
    if not is_supported():
        return None
    try:
        app = _APPKIT.NSWorkspace.sharedWorkspace().frontmostApplication()
        if app is None:
            return None
        pid = int(app.processIdentifier())
        name = str(app.localizedName() or "")
        url = app.bundleURL()
        exe_path = str(url.path()) if url is not None else None
        title = _frontmost_window_title(pid) or name
        if not name and not title:
            return None
        return ForegroundWindow(
            hwnd=0,  # macOS has no HWND; identity comes from exe::title
            title=title,
            pid=pid,
            exe_name=name or None,
            exe_path=exe_path,
        )
    except Exception:  # noqa: BLE001
        return None


__all__ = ["is_supported", "probe_foreground"]
