# `infra/release`

Release pipeline assets — the channel manifests, update-feed
schemas, and signing infrastructure described in
[`RELEASE.md`](../../RELEASE.md) § *Auto-update architecture*.

## Status

Currently empty. The architecture is documented in
[`RELEASE.md`](../../RELEASE.md); the implementation is gated
on procuring a code-signing certificate.

## What will land here

Once a signing cert is in place:

```
infra/release/
├── manifests/
│   ├── stable.json.template
│   ├── preview.json.template
│   └── nightly.json.template
├── sign/
│   ├── sign-windows.ps1
│   └── verify-manifest.py
└── README.md
```

The manifests are the signed JSON files that
`apps/desktop/app/core/updater.py` (to-be-built) reads to
decide whether an update is available. See
[`RELEASE.md`](../../RELEASE.md) § *Auto-update architecture
(planned)* for the manifest schema.
