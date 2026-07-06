# Recall — VS Code companion

The editor half of capture. When you settle on a file (2 s of focus,
or a save), one `open` event goes to the local Recall daemon — path
and filename only, never file contents. Threads, resurfacing and
recovery then see your *editing* continuity, not just your browsing.

Same contract as the browser extension:

- **Metadata only.** The document body is never read or sent.
- **One destination.** `http://127.0.0.1:4545` — configurable, loopback
  by default, and there is no other network code in the file.
- **Durable-ish.** An in-memory outbox batches to
  `POST /v1/events/batch` and retries every 30 s while the daemon is
  down (VS Code windows are long-lived; a restart loses at most a
  short backlog).
- **Quiet.** Flicking through tabs doesn't count — only files you
  settle on (2 s) or save. The same file within 5 minutes is one event.

## Install (no build step)

The folder is the extension — plain JavaScript, zero dependencies.

```bash
mkdir -p ~/.vscode/extensions
cp -r apps/vscode ~/.vscode/extensions/recall.recall-vscode-0.1.0
```

Restart VS Code. Check it's alive: open a file, wait 2 s, then

```bash
curl -s 127.0.0.1:4545/v1/health   # ingested_total climbs
```

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `recall.enabled` | `true` | Capture file opens/saves into `~/.recall/events` |
| `recall.endpoint` | `http://127.0.0.1:4545` | The local daemon |

Disable any time from Settings → Extensions → Recall.
