# Phase 8C — Control Room Reality

**Question:** does the admin web app — the operator's
view onto Recall — actually load all its routes
without crashing, and do its loaders point at
files that exist?

**Method:** read [`Nav.tsx`](../../../apps/admin/web/components/Nav.tsx)
for the canonical route list, read the loader
barrel ([`lib/loaders/index.ts`](../../../apps/admin/web/lib/loaders/index.ts))
for the data layer, confirm every loader maps to a
real file under `lib/loaders/`, and run
`npx tsc --noEmit` over the whole project.

---

## Route inventory

13 routes, organised into 5 groups by `Nav.tsx`:

| Group     | Route             | Hotkey | Purpose |
|-----------|-------------------|--------|---------|
| overview  | `/`               | 1      | Overview |
| cohort    | `/users`          | 2      | Per-user (cohort) view |
| engine    | `/recovery`       | 3      | Recovery candidates surface |
| engine    | `/replays`        | 4      | Day replays |
| engine    | `/daily-loop`     | 5      | Daily loop log + state |
| engine    | `/trust`          | 6      | Trust ledger + reviews |
| ship      | `/release`        | 7      | Release readiness |
| ship      | `/system`         | 8      | System checks |
| ship      | `/extension`      | 9      | Extension pairing surface |
| ship      | `/launcher`       | 0      | Launcher inspect surface |
| ship      | `/desktop`        | —      | Desktop watcher (Phase 6M) |
| lab       | `/experiments`    | —      | Experiments shelf |
| lab       | `/docs`           | —      | Local docs view |

Every route directory contains a `page.tsx`:

```
apps/admin/web/app/
├── page.tsx                 # overview
├── users/page.tsx
├── recovery/page.tsx
├── replays/page.tsx
├── daily-loop/page.tsx
├── trust/page.tsx
├── release/page.tsx
├── system/page.tsx
├── extension/page.tsx
├── launcher/page.tsx
├── desktop/page.tsx
├── experiments/page.tsx
└── docs/page.tsx
```

---

## Loader inventory

10 loaders + 1 paths module + 1 fs helper, surfaced
through a single barrel
([`lib/loaders/index.ts`](../../../apps/admin/web/lib/loaders/index.ts)).
All routes import exclusively from the barrel.

| Loader              | Reads from                                  |
|---------------------|---------------------------------------------|
| `loadHealthSnapshot`| daemon `/v1/health` + local indicators      |
| `loadTrustSnapshot` | trust ledger files                          |
| `loadDailyLoop`     | `~/.recall/daily_loop.jsonl` + `daily_loop_state.json` |
| `loadAlpha`         | `alpha/users/` + journal                    |
| `loadJournalEntries`| `alpha/recovery_journal.json`               |
| `loadRelease`       | `apps/admin/release_state.json`             |
| `loadSystemSnapshot`| various OS + daemon probes                  |
| `loadLogSources` / `loadOneLog` | log tail files                  |
| `loadScreenshots`   | `assets/screenshots/`                       |
| `loadDesktop`       | desktop watcher events                      |

All filesystem paths are resolved through
[`lib/loaders/paths.ts`](../../../apps/admin/web/lib/loaders/paths.ts) —
one place to override `RECALL_HOME`, one place to
move a directory. The "loader rewrite is a one-file
edit" claim from the barrel comment holds.

---

## Path safety

`paths.ts` resolves:

| Constant              | Resolves to                              |
|-----------------------|------------------------------------------|
| `REPO_ROOT`           | three `..` up from `apps/admin/web`     |
| `ADMIN_DATA_DIR`      | `<repo>/apps/admin/data`                 |
| `ALPHA_DIR`           | `<repo>/alpha`                           |
| `RECALL_HOME`         | `$RECALL_HOME` or `~/.recall`            |
| `DAILY_LOOP_LOG`      | `<recall_home>/daily_loop.jsonl`         |
| `EVENTS_DIR`          | `<recall_home>/events`                   |
| `CONFIG_FILE`         | `<recall_home>/config.json`              |
| `SCREENSHOTS_DIR`     | `<repo>/assets/screenshots`              |
| `EXTENSION_MANIFEST`  | `<repo>/apps/extension/popup/manifest.json` |
| `LAUNCHER_V3_DIR`     | `<repo>/app/ui/launcher_v3`              |

The `RECALL_HOME` env override is real and is the
only way to point the control room at a non-default
data directory. Useful for review on a clean
machine without disturbing the live install.

---

## TypeScript build

```
cd apps/admin/web
npx tsc --noEmit
exit=0
```

Clean. No type errors across 13 routes + 10
loaders. This is the strongest single confidence
signal we get without an end-to-end browser walk.

---

## Server-side render path

Every loader runs server-side — Next.js App Router
calls them from `page.tsx` at request time. There
is no client-side data fetching for the loader
payload. This means:

1. **No CORS**, no API routes — the loaders are
   plain Node functions reading the local
   filesystem.
2. **Errors propagate as 500s** rather than blank
   pages. Each loader wraps its filesystem reads in
   try/catch so an absent file becomes an empty
   shape, not a crash.
3. **State is per-request.** Re-loading the page
   re-reads disk. No caching surprises.

This is exactly the local-first guarantee the
control room is meant to embody.

---

## Layout shell

`apps/admin/web/app/layout.tsx` wraps every route
with:

- `Nav` — the left rail (above)
- `TopBar` — page title + breadcrumb (new in 6J)
- `BottomBar` — daemon + repo state (new in 6J)
- `CommandPalette` — global ⌘K (new in 6J)
- `CopyDiagnostics` — copy-current-page-as-JSON
- `ShellClient` — client-side state container

All five shell components TypeScript-compile clean.

---

## What this proves

1. **13 routes, all present.** Nav.tsx says 13;
   the filesystem has 13.
2. **10 loaders, all wired through one barrel.**
   The "future loader move is a one-file edit"
   contract holds.
3. **TypeScript clean.** Zero errors across the
   whole project.
4. **Paths are centralised.** `paths.ts` is the
   single override point — `RECALL_HOME` works.

## What this does NOT prove

- That every route renders without an exception on
  empty data. Some loaders (Desktop, Daily Loop)
  expect specific files that may not exist on a
  fresh machine. The try/catch wrappers make this
  *survivable* but the empty-state copy hasn't
  been audited route-by-route. Open as `CTRL-001`.
- That the Command Palette indexes all 13 routes
  correctly. Last verified manually in 6J.
- That the control room behaves correctly in a
  multi-tab session against a busy daemon.
  Concurrent-loader stress test is `CTRL-002`.
