# CONTINUITY_LANGUAGE.md — the one vocabulary

Recall has a launcher, an extension, a website, docs, onboarding,
and a recovery surface. They drifted: the launcher said *"Active
memory threads"*, the extension said *"Active investigations"*, the
same idea wore two names. This file ends that. It is the **single
source of truth for every word Recall shows a user.**

Rule: **if a word appears in a user-facing string, it is on this
list, spelled this way.** A PR that introduces a synonym is a bug.

This extends — and never contradicts — the engineering-side
terminology table in [`CLAUDE.md`](../../CLAUDE.md). Where CLAUDE.md names
the *code*, this file names the *product*.

---

## The user / engine split

Recall already has one deliberate split (CLAUDE.md): an **event** in
the code is a **moment** in the engine's mental model and a
**memory** in user copy. This file keeps exactly that pattern — one
internal word, one user-facing word, mapped explicitly. The split is
allowed *only* where it is written down here.

---

## Canonical terms

| User-facing word | Means | Internal / code word | Never say |
|---|---|---|---|
| **memory** | one captured thing, from the user's point of view | `event` (`moment` in docstrings) | "data point", "record", "log entry" |
| **investigation** | a topic the user keeps returning to | `thread` (engine, `/v1/threads`, threading.mdx) | "thread" *in user copy*, "project", "cluster", "topic cluster" |
| **artifact** | one file / tab / chat that belongs to an investigation | `target` (recovery `suggested_targets`) | "item", "object", "asset", "resource" |
| **recovery** | the surface that offers interrupted work to resume | `recovery` | "suggestions", "recommendations" |
| **resume** | the user action: re-enter a recovery | `restore` (engine: `RestorationPlan`) | "restore" *in user copy*, "reopen", "launch" |
| **resurfacing** | quiet reminder of work the user *set aside* | `resurfacing` | "notifications", "alerts", "feed" |
| **session** | a 30-minute block of related activity | `session` | "visit", "run" |
| **phase** | a coherent stretch within an investigation | `phase` / `evolution` | "stage", "step", "era" |
| **continuity** | the whole product promise — picking work back up | — | "productivity", "memory layer", "AI memory" |
| **the daemon** | the local Recall background process | `APIService` | "the server", "the backend", "the cloud" |

### Notes on the hard calls

- **investigation vs thread.** Same concept, and the surfaces
  genuinely disagreed. Resolution: **user-facing copy says
  "investigation"** (it answers *"what was I working on?"* — a human
  question); **code, the `/v1/threads` API, and architecture docs
  keep "thread"** (too deeply embedded, and precise for engineers).
  This is the same memory/event split, applied again. The launcher's
  *"Active memory threads"* header becomes **"Active
  investigations"**, matching the extension.

- **resume vs restore.** The *user* resumes; the *engine* computes a
  `RestorationPlan` and restores targets. Buttons and copy say
  **Resume**. `restore` survives only in code and the API.

- **memory vs event.** Unchanged from CLAUDE.md. Browser-extension
  copy, launcher empty states, and the website say **memory**;
  `events.py`, JSONL, and the API say **event**.

- **artifact.** New canonical word (Phase 4H/4I used it loosely).
  An investigation *is made of* artifacts. The recovery card counts
  them ("2 tabs · 2 files"); "tabs" and "files" are the everyday
  names for the two artifact kinds and stay — "artifact" is the
  collective noun, used in docs, not usually in the UI.

---

## Forbidden vocabulary

Never appears in any user-facing string, ever (also in CLAUDE.md):

> *AI memory*, *smart memory*, *intelligent recall*, *AI-powered*,
> *neural search*, *AI assistant*, *copilot*, *semantic search*,
> *dashboard*, *productivity score*.

Recall is a **local-first continuity operating system**. That is the
positioning line; it does not get paraphrased.

---

## Canonical surface phrases

The headline strings, fixed across launcher / extension / website:

| Where | Phrase |
|---|---|
| Recovery section | **Continue where you left off** |
| Investigations section | **Active investigations** |
| Resurfacing section | **On your radar** |
| Recovery action | **Resume** |
| Empty state | **Recall is ready.** / *Work a little, then come back later.* |
| Trust line | **Local only · no cloud · no telemetry** |
| Daemon down | **Recall isn't running** (never "error", never red) |

---

## How to use this file

- Writing a user-facing string? Every noun in it is in the table
  above, spelled that way.
- Found a synonym in the codebase? It is drift — fix it, cite this
  file.
- Adding a genuinely new concept? Add a row here *first*, then write
  the string. One word, one meaning, one spelling.

*One product. One vocabulary.*
