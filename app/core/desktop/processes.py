"""Phase 6M — process-name resolver.

Resolves a Windows PID to the process executable name + the
parent PID, using only ``ctypes`` so the launcher's runtime
doesn't pick up a `psutil` dependency for this one signal.

On non-Windows hosts every function returns ``None`` — the
desktop watcher gracefully no-ops on those platforms (the
directive's *no engine work outside its budget* rule). A future
phase can drop in a `darwin.py` / `linux.py` sibling.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import os
import sys
from typing import Optional, Tuple

# --------------------------------------------------------------- platform

_IS_WINDOWS = sys.platform.startswith("win")


def _is_supported() -> bool:
    return _IS_WINDOWS


# --------------------------------------------------------------- Windows

if _IS_WINDOWS:
    _kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    _psapi = ctypes.windll.psapi        # type: ignore[attr-defined]
    _PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    def _open_process(pid: int):
        handle = _kernel32.OpenProcess(
            _PROCESS_QUERY_LIMITED_INFORMATION, False, pid,
        )
        return handle if handle else None

    def _close_handle(handle) -> None:
        try:
            _kernel32.CloseHandle(handle)
        except Exception:  # noqa: BLE001
            pass

    def _query_image_name(handle) -> Optional[str]:
        """``QueryFullProcessImageNameW`` — the full exe path of
        a running PID. Returns ``None`` when the handle is bad
        (process died, access denied)."""
        buf = ctypes.create_unicode_buffer(1024)
        size = wt.DWORD(len(buf))
        ok = _kernel32.QueryFullProcessImageNameW(
            handle, 0, buf, ctypes.byref(size),
        )
        return buf.value if ok else None


def exe_name_for_pid(pid: int) -> Optional[str]:
    """Return the basename of the EXE for the given PID, e.g.
    ``Code.exe``. Returns ``None`` on a non-Windows host or when
    the PID can't be opened."""
    if not _IS_WINDOWS or pid <= 0:
        return None
    handle = _open_process(pid)
    if handle is None:
        return None
    try:
        full = _query_image_name(handle)
        if not full:
            return None
        return os.path.basename(full)
    finally:
        _close_handle(handle)


def exe_path_for_pid(pid: int) -> Optional[str]:
    """Full image path of the running PID."""
    if not _IS_WINDOWS or pid <= 0:
        return None
    handle = _open_process(pid)
    if handle is None:
        return None
    try:
        return _query_image_name(handle)
    finally:
        _close_handle(handle)


def resolve(pid: int) -> Tuple[Optional[str], Optional[str]]:
    """Return ``(exe_name, exe_path)`` for a PID, or ``(None, None)``
    when unresolvable. Single round-trip helper used by
    ``windows.py``."""
    if not _IS_WINDOWS or pid <= 0:
        return (None, None)
    handle = _open_process(pid)
    if handle is None:
        return (None, None)
    try:
        full = _query_image_name(handle)
        if not full:
            return (None, None)
        return (os.path.basename(full), full)
    finally:
        _close_handle(handle)


__all__ = [
    "exe_name_for_pid",
    "exe_path_for_pid",
    "resolve",
]
