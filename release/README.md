# Recall v0.1.0-rc1 — release kit

This folder is the **single front door** for anyone
holding an RC1 build of Recall. Every other file
in here points back to this one.

> Recall is a local-first continuity operating
> system. It reconstructs what you were mentally
> working on across your files, browser, chats,
> and time — on your machine, with no cloud, no
> telemetry, no AI chat.

---

## Start here

| If you want to…                          | Open                                 |
|------------------------------------------|--------------------------------------|
| Install Recall on this machine           | [INSTALL.md](INSTALL.md)             |
| Take the 5-minute guided walkthrough     | [QUICKSTART.md](QUICKSTART.md)       |
| Show someone what Recall does, fast      | [DEMO_FLOW.md](DEMO_FLOW.md)         |
| See what we ship and what's broken       | [KNOWN_ISSUES.md](KNOWN_ISSUES.md)   |
| Compare RC1 to the last preview          | [CHANGELOG_RC1.md](CHANGELOG_RC1.md) |
| Understand what's frozen vs. fluid       | [../VERSION.md](../VERSION.md)       |

---

## The 30-second pitch

You open three GitHub tabs, one StackOverflow
search, a ChatGPT conversation, and two local
files — then leave to a meeting. Two days later
you reopen your laptop. **Recall has already
grouped those into one thread and is ready to
restore it in one click.**

That's the entire product. No chat-with-your-files.
No AI assistant. No cloud. Just continuity.

---

## What you get in the RC1 download

| Artifact                          | Size       | Purpose                                |
|-----------------------------------|------------|----------------------------------------|
| `Recall-Setup-lite.exe`           | ~216 MB    | Windows installer — recommended        |
| `Recall-Setup-full.exe`           | ~261 MB    | Windows installer — larger, no shrink  |
| `apps/extension/popup/` (unpacked)| 296 KB     | Chrome / Edge / Brave / Arc extension  |
| `Recall-Windows-v0.1.zip`         | bundle     | Installer + extension in one zip       |

macOS preview is out of scope for RC1 — see the
[macOS owner note](../docs/release/MAC_OWNER_NEEDED.md).

---

## RC1 freeze summary

Eight surfaces are frozen for RC1:

- Launcher (Phase 7E.1 + 8B collapse)
- Extension popup (Phase 7A, 6 fixed regions)
- Capture pipeline (Phase 7D, 7 hops)
- Resume / recovery (Phase 4E, ≥0.55 trust gate)
- Control room (Phase 6J, 13 routes)
- Doctor CLI
- Demo (new in 8D: `recall demo run/reset/status`)
- Installer (Phase 5J PyInstaller bundle)

See [`../VERSION.md`](../VERSION.md) for the
frozen-surface contract and the canonical bug
ledger.

---

## What this kit does NOT cover

- Internal engineering charter — see
  [`../CLAUDE.md`](../CLAUDE.md).
- Layer architecture — see
  [`../docs/architecture/`](../docs/architecture/).
- Audit history — see
  [`../AUDIT/`](../AUDIT/) and
  [`../STABILITY/`](../STABILITY/).
- Release process / signing — see
  [`../docs/release/RELEASE.md`](../docs/release/RELEASE.md).

The release kit is **for users and reviewers**.
The repo is for contributors. Don't confuse the
two.
