"""Audit the installed Recall bundle by file count + subtree.

Reads `infra/packaging/windows/build_logs/install.log` (the Inno Setup
detailed log from a `/LOG=` install) and groups every "Dest filename"
entry by its top-level subdirectory inside `_internal/`. Produces the
counts behind `docs/engineering/INSTALL_SIZE_AUDIT.md`.

Sizes are not in the install log; this script is the *file-count*
column. Pair with the PyInstaller wheel-size table in
`INSTALL_SIZE_AUDIT.md` for the byte column.

    python infra/scripts/audit_install_size.py
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

_LOG = (
    Path(__file__).resolve().parents[2]
    / "infra" / "packaging" / "windows" / "build_logs" / "install.log"
)


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def _subtree(path: str) -> str:
    """Return the top-level folder inside _internal/ for the given dest path."""
    p = _normalize(path).lower()
    marker = "_internal/"
    i = p.find(marker)
    if i < 0:
        return "<root>"
    rest = p[i + len(marker):]
    sep = rest.find("/")
    return rest[:sep] if sep > 0 else rest


def main() -> int:
    if not _LOG.exists():
        print(f"install log not found: {_LOG}")
        return 1
    text = _LOG.read_text(encoding="utf-8", errors="replace")
    dests = re.findall(r"Dest filename:\s+(.*)", text)
    groups: dict[str, int] = defaultdict(int)
    for d in dests:
        groups[_subtree(d)] += 1
    total = sum(groups.values())
    print(f"total file entries in install.log: {total}")
    print()
    print(f'{"subtree":40s}  {"files":>6}  {"%":>5}')
    print("-" * 56)
    for name, cnt in sorted(groups.items(), key=lambda x: -x[1])[:30]:
        pct = (cnt / total * 100) if total else 0
        print(f"{name:40s}  {cnt:>6}  {pct:>4.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
