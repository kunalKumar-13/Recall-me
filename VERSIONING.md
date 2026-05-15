# Versioning policy

Recall follows [Semantic Versioning 2.0.0](https://semver.org/).
The version number is `MAJOR.MINOR.PATCH`, where:

- **MAJOR** is bumped only when something a careful user could
  notice changes incompatibly — usually a removed HTTP route, a
  changed event-log schema, or a launcher keybinding that used to
  do one thing and now does another.
- **MINOR** is bumped for any additive feature or layer: a new
  endpoint, a new engine layer (events → sessions → … →
  recovery), a new launcher surface.
- **PATCH** is bumped for bug fixes, perf work, docs, and
  cosmetic changes.

The pre-1.0.0 cycle (current) uses the same shape but treats
`0.MINOR.PATCH` as the "real" version pair — `0.MINOR` is the
"big release" axis and `PATCH` is the "polish release" axis.

## What the major version protects

Recall ships three public surfaces. Each carries a stability
guarantee tied to the major version:

| Surface | Stability guarantee |
|---|---|
| Loopback HTTP API (`/v1/*`) | All routes in the canonical list (`CLAUDE.md` § *Repository map*) keep their request + response shape across a major. New fields are additive; removing or repurposing a field requires a new `/v2/` prefix. |
| Event-log schema (JSONL) | The five canonical `kind` values + their payload shapes are stable. Adding new optional fields is additive; existing fields keep their names and types. |
| Launcher keybindings | `Ctrl + Space`, `Enter`, `Ctrl + Enter`, `Ctrl + C`, `Ctrl + M`, `Esc`, `Ctrl + ,` keep their meaning across a major. |

Everything else — internal class names, `~/.recall/` cache
formats (other than `events/`), Settings labels, motion timings —
is below the stability line. Caches can change shape between
minors; users keep working because the engine always re-derives.

## What's not part of versioning

- Internal phase numbers (Phase 1A, 2B, 3C, …) are historical
  build-cycle markers. They are *not* the version. Phase numbers
  are referenced in `CHANGELOG.md` for traceability; they do not
  flow into the user-facing release number.
- Launcher binary builds carry the version as `MAJOR.MINOR.PATCH`
  with the build channel appended (`-stable`, `-preview`,
  `-nightly`) — see [`RELEASE.md`](RELEASE.md).

## Public 1.0.0

Recall reaches 1.0.0 when:

1. The 29-section smoke test runs green on Windows, macOS, and
   Linux.
2. The Windows installer is signed and a documented release
   pipeline produces it reproducibly.
3. The seven engine layers (events → recovery) carry no known
   correctness bugs against the `_smoke_api.py` fixtures.
4. The docs cover every public HTTP route with a working code
   sample.
5. There is at least one community contributor outside the
   founding maintainer set.

Until all five are true, the project stays in 0.x and minor bumps
*may* break compatibility. Once 1.0.0 ships, breakage requires a
new major.

## Deprecation policy

When something is going to be removed in the next major, the
sequence is:

1. The replacement ships in a minor.
2. The old surface gets a `DeprecationWarning` log + a docs note
   for at least one minor cycle.
3. The next major removes the old surface entirely.

No silent removals.
