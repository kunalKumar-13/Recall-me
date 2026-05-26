"""Phase 6M — foreground window probe (Windows).

Returns the *current* foreground window's title + PID + exe path
in a single call. Uses ``ctypes`` so the launcher runtime stays
dependency-free.

On non-Windows hosts every function returns ``None`` and the
watcher quietly skips its tick — same graceful-no-op rule as
``processes.py``.

Privacy contract restated:

  - We read **only** the window title the OS exposes via
    ``GetWindowTextW``. No accessibility-API tree walk, no UI
    Automation snapshot, no clipboard read.
  - The watcher's batching layer (``sessions.py``) caps the
    minimum focus duration so a 200-ms alt-tab never makes it
    to the JSONL.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import sys
from dataclasses import dataclass
from typing import Optional

from .processes import resolve as _resolve_pid


_IS_WINDOWS = sys.platform.startswith("win")


@dataclass
class ForegroundWindow:
    """A single foreground-window probe result."""

    hwnd: int
    title: str
    pid: int
    exe_name: Optional[str]
    exe_path: Optional[str]

    @property
    def stable_key(self) -> str:
        """Identity used by the watcher to detect *which* window is
        focused. Two windows of the same EXE with different titles
        get separate focus sessions; same title in the same EXE
        does not. ``hwnd`` is intentionally **not** part of the
        key because reopening a doc can reuse the same window
        handle."""
        return f"{self.exe_name or '-'}::{self.title}"


# --------------------------------------------------------------- Windows API


if _IS_WINDOWS:
    _user32 = ctypes.windll.user32  # type: ignore[attr-defined]

    _user32.GetWindowTextLengthW.argtypes = [wt.HWND]
    _user32.GetWindowTextLengthW.restype = ctypes.c_int
    _user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
    _user32.GetWindowTextW.restype = ctypes.c_int
    _user32.GetForegroundWindow.restype = wt.HWND
    _user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
    _user32.GetWindowThreadProcessId.restype = wt.DWORD


def _get_window_text(hwnd) -> str:
    length = _user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    _user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value or ""


def is_supported() -> bool:
    """True when the platform exposes a foreground-window probe
    this module knows about."""
    return _IS_WINDOWS


def probe_foreground() -> Optional[ForegroundWindow]:
    """Return the currently focused window or ``None``. The watcher
    polls this on a calm cadence (default 2 s) and aggregates the
    results via ``sessions.py`` before writing anything to disk."""
    if not _IS_WINDOWS:
        return None
    hwnd = _user32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wt.DWORD(0)
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    title = _get_window_text(hwnd)
    exe_name, exe_path = _resolve_pid(pid.value)
    return ForegroundWindow(
        hwnd=int(hwnd),
        title=title,
        pid=int(pid.value),
        exe_name=exe_name,
        exe_path=exe_path,
    )


__all__ = [
    "ForegroundWindow",
    "is_supported",
    "probe_foreground",
]
