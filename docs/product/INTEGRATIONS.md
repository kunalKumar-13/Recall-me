# Integrations — feeding Recall from any tool

Recall's memory has exactly one door: the local daemon at
`127.0.0.1:4545`. Anything that can make a loopback HTTP request can
contribute events — no SDK, no account, no cloud. The engine treats
every source the same: events → sessions → contexts → threads →
recovery.

## The door

```
POST http://127.0.0.1:4545/v1/events/batch
Content-Type: application/json

{ "events": [ { "kind": "...", "payload": { ... } }, ... ] }
```

- 1–500 events per request, applied in order, each filtered
  independently (scheme blocklist, domain excludes, field allowlist).
- Response: `{ "received": N, "ingested": M, "reason": ... }`.
- Accepted kinds and their payloads:

| kind | payload fields | meaning |
|---|---|---|
| `browser_visit` | `url, title, domain, browser` | a page you visited |
| `browser_search` | `url, query, engine, domain` | a search you ran |
| `chat_session` | `url, title, platform, domain` | an AI conversation |
| `open` | `path, title` | a file you worked in |
| `desktop_window` | `app, title, duration, focus_start, focus_end` | app focus |

Unknown fields are dropped server-side; unknown kinds are refused.
Timestamps: include `ts` (ISO 8601) to log retroactively — the
durable-outbox pattern — otherwise the daemon stamps arrival time.

## Built-in sources

- **Browser** — `apps/extension/` (Chrome · Edge · Brave · Arc):
  visits, searches, AI chats, SPA routes, durable offline outbox.
- **Files** — the daemon's folder watcher indexes configured folders
  for `GET /v1/search/files`.
- **Editor** — `apps/vscode/`: file opens and saves, settle-gated and
  deduped. See its README for the two-line install.

## Recipes

### Git — thread your commits and branch switches

Drop this in `.git/hooks/post-commit` (and symlink as
`post-checkout`), then `chmod +x` it:

```sh
#!/bin/sh
# Recall: log this repo moment (metadata only — repo path + subject).
MSG=$(git log -1 --pretty=%s | tr -d '"\\')
ROOT=$(git rev-parse --show-toplevel)
curl -s -m 1 -X POST http://127.0.0.1:4545/v1/events/batch \
  -H 'Content-Type: application/json' \
  -d "{\"events\":[{\"kind\":\"open\",\"payload\":{\"path\":\"${ROOT}\",\"title\":\"commit: ${MSG}\"}}]}" \
  >/dev/null 2>&1 || true
```

The `|| true` + 1-second timeout keep git instant when the daemon is
off. Quotes and backslashes are stripped from the subject to keep the
inline JSON honest — use a real JSON encoder in anything fancier.

### Anything else

One request makes any tool a memory source — a build script, a
notebook hook, a window manager:

```sh
curl -s -X POST http://127.0.0.1:4545/v1/events/batch \
  -H 'Content-Type: application/json' \
  -d '{"events":[{"kind":"open","payload":{"path":"~/notes/standup.md","title":"standup notes"}}]}'
```

## Reading memory back

The same daemon answers retrieval for any client:

| endpoint | answers |
|---|---|
| `GET /v1/search?q=` | episodic moments + sessions + contexts |
| `GET /v1/search/files?q=` | semantic file search over indexed folders |
| `GET /v1/threads/recent` | active threads |
| `GET /v1/recovery/recent` | resumable work |
| `POST /v1/recovery/{id}/restore` | the choreographed restoration plan |
| `GET /v1/events/today` | events captured today (UTC), by kind — verify your integration is landing |

Swagger for all of it: `http://127.0.0.1:4545/docs-api`.
