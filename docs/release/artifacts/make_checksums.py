"""Generate SHA-256 checksums + an artifact manifest for a release.

Hashes every file staged in this folder's `windows/` and `preview/`
subdirectories and writes (paths resolved relative to this file, so
the script runs from any working directory):

  • checksums/SHA256SUMS    — `<sha256>  <name>` lines,
                              the format `shasum -c` reads
  • checksums/manifest.json — name, size, sha256, channel

    python docs/release/artifacts/make_checksums.py

Run it after staging artifacts and before creating the GitHub
release. The published `SHA256SUMS` is what a user checks a download
against (see DOWNLOADS.md).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANNELS = {"windows": HERE / "windows", "preview": HERE / "preview"}
OUT = HERE / "checksums"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict] = []
    sums_lines: list[str] = []

    for channel, folder in CHANNELS.items():
        if not folder.exists():
            continue
        for path in sorted(folder.iterdir()):
            if not path.is_file() or path.name.startswith("."):
                continue
            digest = sha256(path)
            artifacts.append({
                "name": path.name,
                "channel": channel,
                "size_bytes": path.stat().st_size,
                "sha256": digest,
            })
            sums_lines.append(f"{digest}  {path.name}")

    (OUT / "SHA256SUMS").write_text(
        "\n".join(sums_lines) + ("\n" if sums_lines else ""),
        encoding="utf-8",
    )
    (OUT / "manifest.json").write_text(
        json.dumps({
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    if not artifacts:
        print("  no artifacts staged — checksums/ written empty.")
        print("  stage Recall-Setup.exe into the windows/ folder first.")
    else:
        for a in artifacts:
            mb = a["size_bytes"] / (1024 * 1024)
            print(f"  {a['name']}  ({a['channel']}, {mb:.1f} MB)")
            print(f"    {a['sha256']}")
    print(f"  wrote {OUT.name}/SHA256SUMS + manifest.json")


if __name__ == "__main__":
    main()
