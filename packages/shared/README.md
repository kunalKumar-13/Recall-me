# `packages/shared`

Constants, canonical vocabulary mappings, and small utility
helpers that two or more apps in the monorepo both need.

## Status

**Currently empty by design.** The canonical material exists
elsewhere:

| Material | Lives at | Why it's not here yet |
|---|---|---|
| Canonical vocabulary table (event / session / context / thread / evolution / recovery / restoration / continuity) | [`CLAUDE.md`](../../CLAUDE.md) § *Naming and terminology* | A single doc table is the cheapest source of truth until two apps both need to import the strings programmatically |
| Date / time formatters | `apps/desktop/app/core/events.py::humanize_age` | One implementation; not yet duplicated |
| Surface-kind labels (`tab`, `file`, `chat`, `search`) | `apps/web/app/components/ContinueWorking.tsx` + `apps/desktop/app/ui/launcher.py` | Hand-coded in both; could centralise if drift becomes a problem |

## Gate to start populating

A real shared dependency: when an app needs to import a
constant or helper that another app already defines. The first
such item moves here with a short docstring + a re-export
shim left at the original location for one release cycle.

## Allowed dependencies

None beyond the Python / TypeScript standard library. This
package is a leaf in the dependency graph; nothing in
`apps/*` should import a heavy library by way of `shared`.

## Owner

Everyone. Anyone can add to it; anyone can ask for additions to
be removed. Disputes are settled by the engineering charter,
not by precedent.
