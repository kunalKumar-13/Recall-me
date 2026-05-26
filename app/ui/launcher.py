"""Launcher adapter (Phase 8B — collapsed to one path).

Before 8B this module branched on `RECALL_LAUNCHER=legacy` and
re-exported a handful of constants from the legacy launcher. The
legacy tree moved to ``archive/launcher-old/`` in 8B; the
launcher is now exactly one thing — the v3 ``LiveLauncher``.

The import surface ``from app.ui.launcher import Launcher``
still resolves; that part of the contract is frozen
(``docs/product/LAUNCHER_CONTRACTS.md``).
"""

from __future__ import annotations

from .launcher_v3 import LiveLauncher as Launcher

__all__ = ["Launcher"]
