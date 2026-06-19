# DEMO_FLOW — showing Recall to someone in 3 minutes

For when you want to walk a colleague, friend, or
investor through what Recall does. Optimised for
a single screen-share + a deterministic story.

The flow uses **demo mode** so the populated state
is identical every time. No "let me find a good
example" — the canonical WebSocket / proposal /
research trio is always there.

---

## Before they arrive

```bash
# Reset to a clean state so the demo opens fresh.
python recall.py demo reset
python recall.py demo run

# PowerShell — point the launcher at the demo log.
$env:RECALL_DEMO_MODE = "1"
```

Open the launcher once to warm imports (tray icon
or hotkey). Close it. You are ready.

Total prep time: 15 seconds.

---

## The 3-minute walk

### Beat 1 — the promise (20 seconds)

> "This is Recall. It's not an AI assistant. It's
> not search. It reconstructs what you were
> working on, locally, on this machine.
> Nothing leaves the laptop."

Show them:

- The tray icon in the system tray.
- The browser extension icon in the toolbar.

Both are quiet. No badges, no counts, no red
dots. This is the point.

### Beat 2 — the empty open (20 seconds)

Open the extension popup. Show them the **green
daemon dot** and the **"Recall is watching
locally"** copy.

Say:

> "This is what the extension looks like before
> Recall has anything to say. The dot tells you
> the engine is alive. The copy explains what's
> happening. There's no notification, no
> dashboard, no inbox."

### Beat 3 — the populated launcher (60 seconds)

Open the launcher (Alt+Space by default).

You'll see:

- A **Continue card** at the top (the WebSocket
  recovery — 5 tabs, 2 files).
- Two or three **investigation threads** below
  it (proposal, research).
- A handful of **recent memories** in the digest.
- A small **trust row** at the bottom.

Walk through each:

> "The continue card is the headline — Recall
> thinks I was mid-thread on a WebSocket bug, and
> I can reopen all five tabs and both files in
> one click. The investigations are the other
> things on my radar — not as urgent. The
> memories below are just what I touched
> recently."

Hover the continue card briefly. Don't click it
yet.

### Beat 4 — the one-click resume (30 seconds)

Click **Continue**.

The five demo URLs open in tabs (the demo trace
uses real-looking URLs — GitHub, StackOverflow,
ChatGPT — so the tabs actually load). The local
file targets in the demo trace are placeholders
and won't open, which is fine — say so:

> "In a real install, this would also open the
> two local files I was editing. In the demo I'm
> running it just opens the URLs."

The launcher closes. The toast confirms.

### Beat 5 — the calm (10 seconds)

Open the launcher again. The continue card is
gone — Recall doesn't nag you with the same
thread twice in one session.

> "And that's it. The product doesn't push, doesn't
> ping. It composes, it offers, you decide. If
> you ignore a continue card, it learns and
> doesn't surface that exact thread again."

### Beat 6 — the architecture pitch (40 seconds)

Optional, depending on audience.

> "Three things make this work. **One:** capture
> is local — a browser extension + a desktop
> watcher write JSONL to `~/.recall/`. **Two:**
> the engine is seven composable layers — events,
> sessions, contexts, resurfacing, threads,
> evolution, recovery — each one a deterministic
> transformation of the layer below. **Three:**
> the launcher is the only UI primitive. No
> dashboards, no chat, no inbox."

If they ask "where's the AI?" — say:

> "The only model is a sentence-transformer
> embedding, used once for file search. Every
> other layer is heuristic. No LLM, no
> probabilistic ranking, no learned weights in
> the hot path."

---

## After the demo

Reset:

```bash
$env:RECALL_DEMO_MODE = $null
python recall.py demo reset
```

Your real Recall (if you have one) is untouched —
the demo wrote only to `~/.recall/events-demo/`.

---

## Questions you'll get

| Question                             | Short answer |
|--------------------------------------|--------------|
| "Where does this run?"               | "Entirely on the local machine. The only outbound call is a one-time embedding model download." |
| "Can I chat with my files?"          | "No. Different product. See `CLAUDE.md`." |
| "Is there a cloud version?"          | "No. Never will be." |
| "How is this different from Rewind / Recall.ai?" | "Different problem: continuity (what was I mentally working on?) vs total recall (what did I see at 3:42pm?)." |
| "What about cross-device?"           | "Out of scope for v0.1. The locality is the product." |
| "Where's the AI assistant?"          | "There isn't one. The whole point is no chat surface — just the launcher and the continue card." |
| "How do I uninstall everything?"     | "Standard Windows uninstall + `rm -rf ~/.recall/`." |

---

## Anti-patterns — don't do this

- **Don't show them `recall doctor`.** It's an
  operator tool. Looks like a sysadmin demo.
- **Don't open the control room.** That's for
  contributors. Looks like a dashboard product.
- **Don't promise multi-device.** It's not.
- **Don't say "AI memory."** Recall doesn't have
  memory in the AI sense — it has a log + a
  composition pipeline.
- **Don't skip the empty extension state.** The
  point of the product is calmness; the empty
  state is the proof.

---

## If something goes wrong mid-demo

| Surface           | Recovery                                     |
|-------------------|----------------------------------------------|
| Continue card missing | Re-run `recall demo reset && recall demo run`, restart launcher |
| Daemon dot grey   | Start Recall from the Start menu             |
| Extension blank   | Reload the extension from `chrome://extensions` |
| Launcher slow     | First open warms imports — second open is the real timing |

The deterministic demo trace means you can always
get back to the canonical state in one command.

---

## Related

- [QUICKSTART.md](QUICKSTART.md) — the same flow
  but with real capture instead of demo seed
- [../DEMO_MODE.md](../../product/DEMO_MODE.md) — full demo
  CLI reference
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — what to
  preemptively mention if it comes up
