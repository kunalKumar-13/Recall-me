# `packages/contracts`

Wire-format schemas + API contracts. The shapes that cross app
boundaries — event payloads, HTTP request/response models,
thread / evolution / recovery JSON envelopes.

## Status

**Currently empty by design.** The canonical material lives at:

- [`apps/desktop/api/schemas.py`](../../apps/desktop/api/schemas.py)
  — Pydantic models. **This file is the contract today.**
- Per-event JSON shape: see
  [`apps/docs/architecture/events.mdx`](../../apps/docs/architecture/events.mdx)
- Per-engine JSON envelopes: see the corresponding architecture
  pages under `apps/docs/architecture/`

The extension's TypeScript-side type definitions (e.g. the
`BrowserVisit` shape it builds before posting) are hand-coded
in `apps/extension/background.js` and are *not* generated from
the Pydantic models. This works today because the schema is
small and stable; it will not work the moment a third
language-bound consumer (a community CLI tool, a partner
integration) appears.

## Gate to start populating

Either of:

1. A third consumer of the `/v1/*` API surface exists (beyond
   the launcher and the extension), AND
2. Drift between the Pydantic models and the extension's
   hand-coded types has caused a real bug.

OR a partner / plugin starts taking a versioned dependency on
the schemas (which is when this package would be extracted and
published to `pypi` + `npm` simultaneously).

## What will land here (eventually)

```
packages/contracts/
├── events/                 (per-kind JSON schemas)
│   ├── browser_visit.schema.json
│   ├── browser_search.schema.json
│   ├── chat_session.schema.json
│   ├── open.schema.json
│   └── query.schema.json
├── api/                    (OpenAPI fragment per route)
│   └── v1.openapi.yaml
├── python/                 (generated Pydantic models)
└── typescript/             (generated TS types)
```

The JSON schemas are the source of truth; the language-specific
files are generated. This is the **only** package that needs a
build step to stay coherent, and that build step is the
sole reason it stays empty today — adding it before there's a
third consumer is overhead for nobody's benefit.

## Allowed dependencies

None. Contracts are pure data declarations; importing engine
code would invert the dependency direction.

## Owner

The API maintainer (currently whoever has most recently
shipped a `/v1/*` route).
