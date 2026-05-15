# Security policy

Recall is a local-first desktop application with a loopback HTTP
service. The threat model and disclosure process below are scoped to
that architecture.

## Threat model

### What Recall protects against

- **Remote attackers on the network.** The HTTP API binds to
  `127.0.0.1` only. The Chrome extension's `host_permissions` is
  locked to `http://127.0.0.1:4545/*`, so Chrome physically refuses
  to fetch any other URL from the worker. No code path opens an
  outbound connection except the one-time embedding-model download
  on first run.
- **Accidental data leakage.** No telemetry, no analytics, no
  error reporting, no model-update pings. ChromaDB and Hugging Face
  telemetry are explicitly disabled at boot.
- **Data leaving the device under any UI state.** Pausing capture
  drops events server-side. Domains in the user's blocklist are
  rejected client-side *and* server-side; server-side is
  authoritative.

### What Recall does **not** protect against

- **Other processes running as the same user.** A peer process can
  read `~/.recall/` directly, post events to the loopback API, or
  read the JSONL log. If your threat model includes hostile local
  processes, the correct mitigation is OS-level filesystem ACLs and
  running Recall under a separate user — not an auth layer on a
  loopback port.
- **Physical access to an unencrypted disk.** The event log and the
  vector index are plain files. Disk encryption is the user's
  responsibility.
- **Browser sandboxing escapes.** The extension is bound by Chrome's
  permission system. We trust that boundary.

## Disclosure

If you've found a security issue, **do not open a public GitHub
issue.** Email the maintainers at:

> `security@recall.computer`

(If no response within 72 hours, follow up on the same thread.)

Please include:

1. A description of the vulnerability.
2. The smallest reproduction you can isolate.
3. Your assessment of severity (denial-of-service vs data leak vs
   remote code execution).
4. Whether you've already disclosed elsewhere.

We will:

1. Acknowledge receipt within 72 hours.
2. Investigate and confirm or refute within 14 days.
3. Ship a fix in the next patch release if the report is valid.
4. Credit you in the release notes unless you ask us not to.

## Scope

In scope:

- The desktop application (`app/`, `api/` — currently at repo
  root; future home `apps/desktop/`).
- The Chrome extension (`apps/extension/`).
- The build pipeline (`recall.spec`, `infra/scripts/`,
  `infra/installers/`).
- The packaged releases on GitHub.

Out of scope:

- The marketing site (`apps/web/`) — that's a static Next.js
  export.
- The docs site (`apps/docs/`) — Mintlify-hosted, static.
- Third-party dependencies — please report those upstream.
- Findings that require an attacker already running as the same
  local user (see threat model above).

## Bounty

Recall is a community project with no commercial sponsor. We do not
have a bounty program. Credit and a thank-you in the release notes
are what we can offer.
