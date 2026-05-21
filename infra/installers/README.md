# `infra/installers`

Installer specs, signing notes, and the packaging recipes that
turn a built `apps/desktop` tree into a distributable artefact.

## Status

Currently empty. The PyInstaller spec
([`recall.spec`](../../recall.spec)) and the icon builder
([`infra/scripts/build_icon.py`](../scripts/build_icon.py)) live
adjacent to the Python tree at the repo root, in lockstep with
the deferred Python-tree move documented in
[`apps/desktop/README.md`](../../apps/desktop/README.md).

## What will land here

When the desktop tree moves under `apps/desktop/`:

```
infra/installers/
├── windows/
│   ├── recall.iss              Inno Setup wrapper
│   ├── signing.md              code-signing runbook
│   └── README.md
├── macos/
│   ├── Info.plist
│   ├── notarization.md
│   └── README.md
└── linux/
    ├── recall.desktop
    ├── appimage.md
    └── README.md
```

See [`RELEASE.md`](../../docs/release/RELEASE.md) § *Installer pipeline
(Windows)* for the current commands; that document is the
source of truth for the build invocation until the per-OS
directories above are populated.
