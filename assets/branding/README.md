# `assets/branding`

Logo source files, icon variants, brand-mark notes, and the
generative artefacts that produce them.

## Status

Currently empty. The existing brand assets are scattered:

| Asset | Lives at | Notes |
|---|---|---|
| App icon (Windows `.ico`) | `apps/desktop/app/assets/icon.ico` (after Python-tree move; currently `app/assets/icon.ico`) | Generated from a single SVG source by [`infra/scripts/build_icon.py`](../../infra/scripts/build_icon.py) |
| Marketing logo (light + dark) | Embedded in `apps/web/app/components/Logo.tsx` | SVG, inline |
| Docs site logo | Mintlify config references `/logo/dark.svg` + `/logo/light.svg` | TODO: those files don't exist yet; the docs site is rendering placeholders |
| Favicon | `apps/web/public/favicon.svg` | Single source |

## What will land here

```
assets/branding/
├── source/
│   └── recall-mark.svg          source of truth
├── icon/
│   ├── icon-16.png .. icon-512.png
│   └── icon.ico                 Windows
├── logo/
│   ├── wordmark-light.svg
│   ├── wordmark-dark.svg
│   ├── mark-light.svg
│   └── mark-dark.svg
└── brand-notes.md               colour pairings, clear-space, don'ts
```

The `source/recall-mark.svg` is the single source of truth;
everything else is generated from it. The build step lives in
[`infra/scripts/build_icon.py`](../../infra/scripts/build_icon.py)
(extended to produce all variants when this directory is
populated).
