"""pynput → Qt signal bridge for the global hotkey.

Encapsulates two concerns:

  1. Cross-thread marshalling. pynput fires its callback on its own daemon
     thread; widgets must only be touched from the UI thread. We emit a
     signal from `HotkeyBridge` (a QObject living on the main thread) so
     Qt's queued connection delivers the slot safely.

  2. Failure isolation. If pynput is missing or hotkey registration fails
     (already-bound, permission denied, etc.), we warn to stderr and the
     rest of the app keeps working — the tray icon still launches the
     window. Hotkey conflicts shouldn't crash the product.
"""

from __future__ import annotations

import sys
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class HotkeyBridge(QObject):
    """Emit `triggered` whenever the registered hotkey fires."""

    triggered = pyqtSignal()


class HotkeyListener:
    def __init__(self, bridge: HotkeyBridge, combo: str = "<ctrl>+<space>") -> None:
        self.bridge = bridge
        self.combo = combo
        self._listener = None

    def start(self) -> bool:
        try:
            from pynput import keyboard
        except ImportError:
            print(
                "[recall] pynput not installed — global hotkey disabled.",
                file=sys.stderr,
            )
            return False

        def _fire() -> None:
            # Runs on the pynput daemon thread; signal is delivered queued
            # to whoever is on the UI thread.
            self.bridge.triggered.emit()

        try:
            self._listener = keyboard.GlobalHotKeys({self.combo: _fire})
            self._listener.daemon = True
            self._listener.start()
            return True
        except Exception as e:
            print(
                f"[recall] failed to register hotkey {self.combo!r}: {e}",
                file=sys.stderr,
            )
            return False

    def stop(self) -> None:
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
