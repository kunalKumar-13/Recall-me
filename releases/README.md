# releases/

Staging for Recall release artifacts. A release is *assembled* here,
checksummed, then uploaded to GitHub Releases — this folder is the
pre-flight bench, not the distribution channel.

## Layout

```
releases/
├── windows/      Recall-Setup.exe  (stable channel)
├── preview/      pre-release builds (preview channel)
├── checksums/    SHA256SUMS + artifact manifest, generated
├── make_checksums.py        hashes artifacts → checksums/
└── RELEASE_NOTES_v0.2.0.md  the draft notes for the next tag
```

The `windows/` and `preview/` folders are **build outputs** — they
are git-ignored; only the scripts, notes, and this README are
tracked. An artifact exists here only on a build machine, briefly,
between `build.ps1` and the GitHub upload.

## Assembling a release

1. Build the installer — `pwsh infra/packaging/windows/build.ps1`
   produces `dist/installer/Recall-Setup.exe`.
2. Copy it into `releases/windows/` (stable) or `releases/preview/`.
3. `python releases/make_checksums.py` — writes
   `checksums/SHA256SUMS` and `checksums/manifest.json`.
4. Finalise `RELEASE_NOTES_v0.2.0.md`.
5. Create the GitHub release; attach the artifact + `SHA256SUMS`.

## Verifying

Every published artifact has a SHA-256 in `SHA256SUMS`. A user
verifies with `Get-FileHash` (Windows) or `shasum -a 256` — see
[`DOWNLOADS.md`](../docs/release/DOWNLOADS.md).

## Channels

| Channel | Folder | Audience |
|---|---|---|
| stable | `windows/` | public alpha users |
| preview | `preview/` | cohort builders, testing pre-release fixes |

The release ladder is governed by [`RELEASE.md`](../docs/release/RELEASE.md);
the public-alpha gate by [`GO_NO_GO.md`](../docs/release/GO_NO_GO.md).
