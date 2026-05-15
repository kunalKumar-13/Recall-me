# Demo script — the 90-second Recall walkthrough

This is the canonical demo: 90 seconds, three acts, one
restoration moment. It's the script every public-facing
recording references. Click sequence and timing are exact.

## Prerequisites

1. Boot the launcher in full-demo mode so the event log is
   pre-seeded with the deterministic developer-life trace:

   ```
   RECALL_DEMO_MODE=1 python recall.py
   ```

   First boot writes ~30 events spanning four overlapping
   stories (websocket-retry debugging, RLHF research,
   healthcare startup, casual reading). The seed is
   idempotent — subsequent boots reuse the marker file and
   skip re-seeding.

2. Set the OS to **light mode**. Dark-mode capture is a
   second pass with the same script.

3. Window manager: launcher centered, browser visible behind
   it but unfocused. The launcher should never overlap the
   demo's cursor target.

---

## Act 1 — "It's just there." (0:00 → 0:25)

> **Narration (12 words):** *"Open the launcher anywhere with
> Ctrl-Space. Type the half-thought."*

| 0:00 | Cursor visible in a code editor (any file open). |
| 0:03 | Press **Ctrl + Space**. Launcher appears centered. |
| 0:05 | Launcher in **idle digest** state. Visible sections, in order: *Continue where you left off* (1 card), *Active memory threads* (2 cards), *On your radar* (1 card). |
| 0:08 | Cursor hovers the top recovery card. The card subtle-highlights. **Caption visible:** *"2 tabs · 2 files · 1 chat · after a revisit"* |
| 0:13 | Type **`websocket retry`** in the search input. Results render in <100ms. |
| 0:18 | Pause on results. Top row is an episodic moment (Stack Overflow visit). Below it: a session card, a micro-context card, then file rows. |
| 0:25 | Press **Esc**. Launcher hides. |

---

## Act 2 — "It knows what I was doing." (0:25 → 0:55)

> **Narration (14 words):** *"Open the launcher idle. The top
> card is yesterday's work — ready to resume in one click."*

| 0:25 | Press **Ctrl + Space**. Launcher returns to idle digest. |
| 0:28 | Camera focus on the *Continue where you left off* card. Caption reads — verbatim, deterministic — *"2 tabs · 2 files · 1 chat · after a revisit"*. |
| 0:32 | Click the card. |
| 0:33 | Launcher flashes the footer: **"Restoring · WebSocket retry on disconnect (5 items)"**. |
| 0:34 | Behind the launcher: Chrome focuses, opens the Stack Overflow tab. ~150ms later: the MDN reference tab. ~150ms later: Claude.ai chat. ~150ms later: the two `~/code/ws-retry/*.py` files in the editor. |
| 0:42 | Launcher footer updates: **"Restored 5 · WebSocket retry on disconnect"**. |
| 0:44 | Launcher hides automatically (350ms after first open). |
| 0:46 | The full restored workspace is visible. 2 browser tabs + 1 chat + 2 code files. *Re-entry into the mental room is complete.* |
| 0:55 | Hold on the restored state for 8 seconds. |

---

## Act 3 — "And it stays on my machine." (0:55 → 1:30)

> **Narration (18 words):** *"Everything stays on disk. No
> cloud. No telemetry. The retrieval engine is small enough
> to read in an afternoon."*

| 0:55 | Press **Ctrl + Space**. |
| 0:57 | Press **Ctrl + ,** to open Settings. |
| 0:59 | Settings dialog appears. Browser Memory section visible: *"Capture browser activity to ~/.recall/events"* — no toggle for "share data" because there's nothing to share. |
| 1:04 | Click *Open activity log…* — file manager opens, showing the per-day JSONL files at `~/.recall/events/`. |
| 1:08 | Camera focus: one JSONL line, plain text, hand-editable. **Caption:** *"Plain JSON. Delete a line, remove a day, forget a week."* |
| 1:14 | Close the file manager and Settings. |
| 1:16 | Return to a terminal. Type: |
|      | ```$ curl http://127.0.0.1:4545/v1/health``` |
| 1:19 | Output appears: `{"status":"ok","ingested_total":30,...}`. **Caption:** *"127.0.0.1:4545 — the only thing Recall binds. The bind is the boundary."* |
| 1:25 | Final card: the project tag in mono, simply: **MIT · loopback-only · state in ~/.recall**. |
| 1:30 | End. |

---

## Recording notes

- **Cursor speed:** moderate. The launcher's hover transitions
  are 250ms; cursor movement should let those breathe.
- **No zoom-in cuts.** A single steady frame the whole way
  through — the product is supposed to feel inevitable, and
  inevitable software doesn't need cinematography.
- **No music.** Mono narration over the recording. The product
  speaks for itself.
- **Length:** 90s ± 5s. Anything longer is too long; anything
  shorter and the restoration choreography doesn't read.

## Why these exact moments

The script was chosen to exercise exactly the surfaces a
sceptical first-time viewer most needs to see:

| Act | Skepticism it addresses |
|---|---|
| 1 | *"Yet another launcher."* — The idle digest surfaces real work, not a blank command bar. Search lands instant. |
| 2 | *"One click restoration? Sure."* — The choreographed open of 5 mixed targets in 8 seconds is the killer feature. It is intentionally the visual centerpiece. |
| 3 | *"Where does the data go?"* — Plain JSONL, loopback API, terminal proof. The boundary is *visibly* the bind. |

Skip any one of the three and the demo fails to do its job.

## Variants

| Name | Length | Use |
|---|---|---|
| **90s canonical** | 1:30 | This script. Homepage, README hero GIF, social cards. |
| **3-minute deep dive** | 3:00 | Same arc + a 90-second appendix walking through `architecture/recovery.mdx` rules so a developer audience sees the determinism. |
| **30-second loop** | 0:30 | Just Act 2 (restoration). Loops cleanly for the marketing site's hero. |

All variants reuse the same `RECALL_DEMO_MODE=1` seed.
Determinism means the demo never drifts between recordings.
