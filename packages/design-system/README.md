# `packages/design-system`

The codified visual contract: colour tokens, typography scale,
spacing scale, motion ramp, elevation ladder, and the small set
of UI primitives that recur across surfaces.

## Status

**Currently empty by design.** The canonical material lives at:

- [`apps/docs/architecture/visual-system.mdx`](../../apps/docs/architecture/visual-system.mdx)
  — the source of truth for tokens
- [`apps/web/tailwind.config.ts`](../../apps/web/tailwind.config.ts)
  — the web codification of the colour + spacing tokens
- [`apps/desktop/app/ui/styles.py`](../../apps/desktop/app/ui/styles.py)
  — the Qt codification of the same tokens for the launcher

Centralising into this package requires the two codifications
to agree token-for-token. They mostly do today; small drift
exists (the launcher uses Qt `QSS`-friendly hex variants, the
web uses CSS RGB tuples).

## Gate to start populating

When the visual contract gains a third consumer (a Storybook,
a second front-end surface, an embed widget), OR when token
drift between Qt and Tailwind causes a visible bug.

## What will land here (eventually)

```
packages/design-system/
├── tokens/
│   ├── colors.ts            (web export)
│   ├── colors.py            (Qt export, generated from .ts)
│   ├── spacing.ts/.py
│   ├── motion.ts/.py
│   └── elevation.ts/.py
├── primitives/
│   ├── KbdChip.tsx          (the launcher-style kbd pill)
│   ├── HairlineRow.tsx      (the launcher row pattern)
│   └── (no Qt primitives — those live in apps/desktop/app/ui/widgets.py)
└── README.md
```

The generated `.py` files exist so the launcher stays in sync
without forcing the design-system to ship as a Python package
on PyPI. A small build step (`infra/scripts/build_tokens.py`)
translates the TypeScript source of truth into the Qt-friendly
constants the launcher reads.

## Allowed dependencies

Tailwind / TypeScript on the web side. Pure Python stdlib on the
desktop side. No app-specific imports.

## Owner

The visual-system steward (whoever currently has authority to
say "this spacing change is approved"). Sits with the engineer
who most recently audited
[`visual-system.mdx`](../../apps/docs/architecture/visual-system.mdx).
