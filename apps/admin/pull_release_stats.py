"""Release-stats puller — the dashboard's one automatic data source.

Reads GitHub's *public* per-asset `download_count` for every Recall
release and writes `release_stats.json` next to this script. The
dashboard's Release Monitor section reads that file.

This is NOT telemetry. GitHub counts release-asset downloads for
every public repository — the same way it counts stars. The count
is a property of the *release*, not of any user's machine; nothing
is collected from anyone. It is the only number in the founder
dashboard that updates without a human typing it.

    python apps/admin/pull_release_stats.py

Unauthenticated (60 requests/hour — ample for a manual tool). Set
GITHUB_TOKEN in the environment to raise that if needed.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "kunalKumar-13/Recall-me"
API = f"https://api.github.com/repos/{REPO}/releases"
OUT = Path(__file__).resolve().parent / "release_stats.json"

# Map an asset filename to a platform bucket for the Windows/macOS split.
_PLATFORM = {
    ".exe": "windows",
    ".dmg": "macos",
}


def _platform_for(asset_name: str) -> str:
    lower = asset_name.lower()
    for ext, plat in _PLATFORM.items():
        if lower.endswith(ext):
            return plat
    return "other"


def fetch_releases() -> list[dict]:
    """GET the releases list. Returns [] on any failure — a founder
    tool must never crash because the network blipped."""
    req = urllib.request.Request(API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "recall-admin",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, ValueError, OSError) as e:
        print(f"  could not reach GitHub: {e}", file=sys.stderr)
        return []


def summarize(releases: list[dict]) -> dict:
    by_platform = {"windows": 0, "macos": 0, "other": 0}
    per_release: list[dict] = []
    total = 0
    for rel in releases:
        rel_total = 0
        assets = []
        for a in rel.get("assets", []) or []:
            count = int(a.get("download_count") or 0)
            plat = _platform_for(a.get("name", ""))
            by_platform[plat] = by_platform.get(plat, 0) + count
            rel_total += count
            assets.append({
                "name": a.get("name", ""),
                "platform": plat,
                "downloads": count,
            })
        total += rel_total
        per_release.append({
            "tag": rel.get("tag_name", "?"),
            "name": rel.get("name", ""),
            "published_at": rel.get("published_at", ""),
            "prerelease": bool(rel.get("prerelease", False)),
            "downloads": rel_total,
            "assets": assets,
        })
    return {
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "repo": REPO,
        "release_count": len(releases),
        "total_downloads": total,
        "downloads_by_platform": by_platform,
        "releases": per_release,
    }


def main() -> None:
    print(f"Recall — release stats from {REPO}")
    data = summarize(fetch_releases())
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    if data["release_count"] == 0:
        print("  no releases published yet — Release Monitor is empty.")
    else:
        bp = data["downloads_by_platform"]
        print(f"  releases:  {data['release_count']}")
        print(f"  downloads: {data['total_downloads']}  "
              f"(windows {bp['windows']} · macos {bp['macos']})")
    print(f"  wrote {OUT.name}")


if __name__ == "__main__":
    main()
