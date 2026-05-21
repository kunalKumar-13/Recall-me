# SURFACE_MAP.md — what each surface is for

Recall is one product with several surfaces. Each surface has
**exactly one job**. When a surface starts doing a second job, it
stops being calm — so this map is the boundary contract: if a change
makes a surface do something not in its "job" cell, it belongs on a
different surface.

Pairs with [`CONTINUITY_LANGUAGE.md`](CONTINUITY_LANGUAGE.md) (the
words) — this file is the roles.

---

## The surfaces

| Surface | One job | Says | Never does |
|---|---|---|---|
| **Website** | the *promise* | "you lose continuity, not files — Recall gives it back" | feature lists as specs, screenshots as proof-of-everything |
| **Launcher** | *active continuity* | "here is the work you can step back into, now" | search-engine results, settings, a dashboard |
| **Extension** | *lightweight continuity* | "a small glance at the same thing, in the browser" | a second launcher, analytics, capture controls beyond toggles |
| **Docs** | *explanation* | "here is exactly how each layer works" | marketing copy, persuasion |
| **Settings** | *control* | "turn capture on/off, choose folders, clear state" | surfacing memories, recovery, anything continuity |
| **Recovery** | the *return path* | "resume this interrupted investigation" | reminders, history, a feed |
| **Resurfacing** | a *passive reminder* | "you set this aside — still on your radar" | urging, notifying, ranking like recovery |

---

## How they relate

```
        Website  ──▶  the promise (before install)
                          │
                          ▼  install
        ┌─────────────────────────────────────┐
        │           the daemon                │
        │   capture → continuity engine       │
        └───────┬─────────────────┬───────────┘
                │                 │
          Launcher            Extension
       active continuity   lightweight continuity
                │                 │
        ┌───────┴───────┐         (same engine,
        │               │          smaller glance)
    Recovery       Resurfacing
   return path   passive reminder

        Docs  ──▶  explains every box above
        Settings ─▶ controls capture into the daemon
```

The **launcher and the extension read the same engine** — they are
not two products, they are two windows onto one. The launcher is the
full surface; the extension is the lightweight one. They must agree:
same investigation, same recovery, same words, same calm.

## The two continuity surfaces, side by side

| | Recovery | Resurfacing |
|---|---|---|
| Question | "what should I resume *now*?" | "what did I set aside?" |
| Tone | confident — it offers one strong thing | quiet — it just mentions |
| Volume | at most a few, high-trust only | a soft list |
| Failure to avoid | a wrong card (destroys trust) | nagging (destroys calm) |
| Launcher header | **Continue where you left off** | **On your radar** |

Recovery and resurfacing are deliberately different *temperatures*.
A change that makes resurfacing louder, or recovery chattier, has
broken the map.

---

## Boundary tests

Before adding anything to a surface, ask:

- **Launcher:** does this help the user *return to work*? If it's a
  setting, it goes to Settings. If it's an explanation, it goes to
  Docs. If it's a search feature, the launcher already searches —
  it does not need a second mode.
- **Extension:** is this the *same glance* the launcher gives, just
  smaller? If it's a new capability, it does not belong — the
  extension never leads the product.
- **Website:** does this communicate the *promise*? A spec table is
  not a promise.
- **Recovery:** is this a strong, resumable investigation? If it's
  "maybe interesting," it is resurfacing's job.

If a feature has no surface — that is the answer. Recall has enough
features (Phase 4J's first line). The work now is coherence.
