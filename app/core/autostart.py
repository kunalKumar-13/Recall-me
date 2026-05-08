"""Launch-on-login wiring.

Cross-platform stub with a Windows-first implementation. The Windows path
writes/removes a value under

    HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run

(per-user, no admin required). Other platforms return False from
`set_enabled()` so the settings checkbox can render disabled.

The launch command is computed from the running interpreter — it picks
up the PyInstaller bundle (`sys.frozen=True` → `sys.executable`) and the
source-tree run separately, so the same code works in both layouts.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "Recall"
_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _launch_command() -> str:
    """Build the autostart command line for the current installation."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle — sys.executable IS the Recall.exe.
        return f'"{sys.executable}"'
    # Source-tree run: invoke the script with the same Python interpreter.
    py = sys.executable or "python"
    script = None
    if sys.argv and sys.argv[0]:
        try:
            cand = Path(sys.argv[0]).resolve()
            if cand.exists() and cand.suffix.lower() == ".py":
                script = cand
        except OSError:
            pass
    if script is None:
        return f'"{py}" -m app.main'
    return f'"{py}" "{script}"'


# ----------------------------------------------------------------- supported


def is_supported() -> bool:
    return sys.platform == "win32"


# ----------------------------------------------------------------- query / set


def is_enabled() -> bool:
    if sys.platform == "win32":
        return _is_enabled_windows()
    return False


def set_enabled(enabled: bool) -> bool:
    """Apply the desired state. Returns True on success (idempotent)."""
    if sys.platform == "win32":
        return _set_enabled_windows(enabled)
    return False


# ----------------------------------------------------------------- Windows


def _is_enabled_windows() -> bool:
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH) as key:
            try:
                value, _kind = winreg.QueryValueEx(key, APP_NAME)
                return bool(value)
            except FileNotFoundError:
                return False
    except OSError:
        return False


def _set_enabled_windows(enabled: bool) -> bool:
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _REG_PATH,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        ) as key:
            if enabled:
                winreg.SetValueEx(
                    key, APP_NAME, 0, winreg.REG_SZ, _launch_command()
                )
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False
