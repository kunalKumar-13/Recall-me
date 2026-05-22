"""INSTALL_SIZE_AUDIT_V2 - deep, name-resolved measurement.

V1 (`audit_install_size.py`) counted files per `_internal/<pkg>/`
subtree. V2 cross-references each install.log destination path
against the on-disk site-packages tree so every line of the
generated report carries a real byte count, not a wheel estimate.

    python infra/scripts/audit_install_size_v2.py

Reads:
    infra/packaging/windows/build_logs/install.log
    <python-user-base>/site-packages/

Writes:
    stdout (intended to be diffed into docs/engineering/INSTALL_SIZE_AUDIT_V2.md)
"""

from __future__ import annotations

import re
import site
import sys
from collections import defaultdict
from pathlib import Path

_LOG = (
    Path(__file__).resolve().parents[2]
    / "infra" / "packaging" / "windows" / "build_logs" / "install.log"
)


def _site_packages_dir() -> Path:
    """Locate the user-installed site-packages directory (Roaming
    on Windows). PyInstaller resolves Recall's deps from here at
    build time, so its tree is the closest mirror of what ended up
    bundled."""
    user_base = Path(site.USER_BASE)
    candidates = [
        user_base / "Python314" / "site-packages",
        user_base / "Python313" / "site-packages",
        user_base / "Python312" / "site-packages",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fallback - sys.path scan.
    for p in sys.path:
        p_ = Path(p)
        if p_.name == "site-packages" and p_.exists():
            return p_
    raise FileNotFoundError("could not locate site-packages")


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def _bundle_paths() -> list[str]:
    """The list of *destination* paths the installer wrote."""
    if not _LOG.exists():
        return []
    text = _LOG.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"Dest filename:\s+(.*)", text)


def _subtree(path: str) -> str:
    """Top-level dir under `_internal/`."""
    p = _normalize(path).lower()
    marker = "_internal/"
    i = p.find(marker)
    if i < 0:
        return "<root>"
    rest = p[i + len(marker):]
    sep = rest.find("/")
    return rest[:sep] if sep > 0 else rest


def _size_of(name: str, sp: Path) -> int:
    """Total bytes for a site-packages subdirectory."""
    sub = sp / name
    if not sub.exists() or not sub.is_dir():
        return 0
    total = 0
    for f in sub.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def main() -> int:
    bundle_dests = _bundle_paths()
    if not bundle_dests:
        print("install.log not found - run a silent install first.")
        return 1
    sp = _site_packages_dir()

    file_counts: dict[str, int] = defaultdict(int)
    for d in bundle_dests:
        file_counts[_subtree(d)] += 1
    total_files = sum(file_counts.values())

    # Resolve a size per subtree by matching against site-packages.
    sized: list[tuple[str, int, int]] = []
    for name, n in file_counts.items():
        # name is the dir under _internal/ as PyInstaller laid it
        # out. site-packages uses the same casing for actual package
        # dirs (transformers/, torch/, etc.) but PyInstaller also
        # makes a few synthetic dirs (`.dist-info`, `pil` for pillow,
        # etc.). We try direct lookup first, then a case-insensitive
        # pass, then fall back to 0 (PyInstaller-generated subtree).
        size_bytes = _size_of(name, sp)
        if size_bytes == 0:
            # Case-insensitive directory match.
            for child in sp.iterdir():
                if child.is_dir() and child.name.lower() == name:
                    size_bytes = _size_of(child.name, sp)
                    break
        sized.append((name, n, size_bytes))

    sized.sort(key=lambda x: -x[2])
    total_bytes = sum(s for _, _, s in sized)

    print(f"# Top subtrees inside the bundle (installer source map)")
    print(f"# {len(sized)} subtrees, {total_files:,} install entries, "
          f"~{total_bytes / 1e6:,.0f} MB resolved")
    print()
    print(f"{'subtree':38s}  {'files':>6}  {'MB':>8}  {'% of total':>10}")
    print("-" * 70)
    for name, n, sz in sized[:25]:
        pct = (sz / total_bytes * 100) if total_bytes else 0
        print(f"{name[:38]:38s}  {n:>6}  {sz/1e6:>8.1f}  {pct:>9.1f}%")
    print("-" * 70)
    print(f"{'(top 25)':38s}  "
          f"{sum(n for _, n, _ in sized[:25]):>6}  "
          f"{sum(s for _, _, s in sized[:25]) / 1e6:>8.1f}")
    print()

    # Top 20 individual largest files in site-packages that match
    # known subtrees - the actual "fat" inside torch, transformers,
    # PyQt6.
    print(f"# Top 20 single files (.dll / .pyd / .so / .lib) from the heaviest packages")
    print()
    fat_pkgs = {n for n, _, _ in sized[:6] if n not in {"<root>", "tzdata"}}
    fattest: list[tuple[Path, int]] = []
    for pkg in fat_pkgs:
        sub = sp / pkg
        if not sub.exists():
            continue
        for f in sub.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() in {".dll", ".pyd", ".so", ".lib", ".dylib"}:
                try:
                    fattest.append((f, f.stat().st_size))
                except OSError:
                    pass
    fattest.sort(key=lambda x: -x[1])
    print(f"{'file':74s}  {'MB':>8}")
    print("-" * 84)
    for f, sz in fattest[:20]:
        rel = f.relative_to(sp).as_posix()
        if len(rel) > 74:
            rel = "..." + rel[-71:]
        print(f"{rel:74s}  {sz/1e6:>8.1f}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
