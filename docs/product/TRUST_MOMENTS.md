# TRUST_MOMENTS.md — the seven firsts

A continuity tool earns trust one *moment* at a time. There are
seven of them in a first user's life with Recall. Each is small;
each can go quietly right or loudly wrong. This file names what
each one is, what makes it land, and what specifically guards it.

Pairs with [`FIRST_WEEK.md`](../founder/FIRST_WEEK.md) (the temporal shape) and
[`TRUST_FIXTURES.md`](../trust/TRUST_FIXTURES.md) /
[`TRUST_FIXTURES_CONTINUITY.md`](../trust/TRUST_FIXTURES_CONTINUITY.md) /
[`TRUST_FIXTURES_DAILY.md`](../trust/TRUST_FIXTURES_DAILY.md) (the
calibration that keeps each first honest).

---

## 1. First launch

| | |
|---|---|
| What happens | The installer finishes, Recall opens, onboarding asks for folders. |
| What earns trust | A calm window, plain language, one screen. No wizard, no account, no email. |
| What breaks trust | A loud "AI-powered" splash, a permission prompt the user did not consent to, a console-style error. |
| Guarded by | [`app/ui/onboarding.py`](../../app/ui/onboarding.py) — single screen with sensible defaults; charter language rules; the empty-state copy. |

## 2. First event

| | |
|---|---|
| What happens | The user browses or opens a file; an event is appended to `~/.recall/events/YYYY-MM-DD.jsonl`. |
| What earns trust | The user can `cat` the file and read what was captured. It is exactly what the privacy line promised: URL + title + kind, no contents. |
| What breaks trust | An opaque binary database; surprising fields (clipboard, keystrokes, screenshots). |
| Guarded by | The plain-JSONL contract; the extension's `host_permissions` of *exactly one* URL; the launcher onboarding subtitle; [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md). |

## 3. First investigation

| | |
|---|---|
| What happens | A topic recurs over a few sessions; `ThreadBuilder` crystallises an investigation. The launcher shows it under *Active investigations*. |
| What earns trust | The investigation's title matches what the user would have named that topic themselves. |
| What breaks trust | An investigation called *"backoff.py"* when the user thinks of the work as *WebSocket retry debugging*. |
| Guarded by | Phase 4H session-anchored bucketing; the fixtures in [`TRUST_FIXTURES_CONTINUITY.md`](../trust/TRUST_FIXTURES_CONTINUITY.md) (correct merge / correct split / bad merge / bad split). |

## 4. First recovery

| | |
|---|---|
| What happens | The user is interrupted mid-flow; the next morning the launcher opens with *Continue today* and one card. The **first-recovery ceremony** (Phase 5C) fires once: *"Recall noticed unfinished work. Pick a card to resume."* |
| What earns trust | The card names something the user actually was doing, with evidence chips (*reopened after a 2-day gap*) they can verify against memory. |
| What breaks trust | A wrong card. Trust never recovers from this — the user concludes the surface is noise. |
| Guarded by | The Phase 4E recovery gates (`_MIN_CONFIDENCE`, `_MIN_RESUME_INTENT`, `_MIN_DISTINCT_TARGETS`); the Phase 4G evidence-specific captions; the Phase 4H bucketing. *Missed > weak.* |

## 5. First resume

| | |
|---|---|
| What happens | The user clicks Resume; files + chats + tabs reopen in the prescribed order; the footer flashes *"Restored 4 of 5"*. |
| What earns trust | The right things, in the right order. The work *physically* comes back. |
| What breaks trust | Targets opening in a chaotic order; a moved file failing silently; nothing happening at all. |
| Guarded by | The `RestorationPlan` ordering (files → chats → tabs → searches); the file-existence check before opening; the `Restored N of M` summary line. |

## 6. First export

| | |
|---|---|
| What happens | The user runs `recall stats --export`. A `stats.json` is written next to their working directory. |
| What earns trust | Reading the file: a dozen numbers, a version, a date. No paths, no titles, no queries. The boundary the docs promised. |
| What breaks trust | One unexpected field. One URL. One filename. One hash. |
| Guarded by | [`build_export()`](../../app/core/stats.py) — a single function that is the entire exportable surface; [`apps/admin/import_stats.py`](../../apps/admin/import_stats.py) re-validates on the founder side and rejects anything that is not counts-only; [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md). |

## 7. First uninstall

| | |
|---|---|
| What happens | The user runs the uninstaller. Recall is removed. `~/.recall/` is *left alone* by design — their memory is theirs. |
| What earns trust | Following [`apps/docs/uninstall.mdx`](../../apps/docs/uninstall.mdx) leaves zero residue except what the user chooses to keep. The user can delete `~/.recall/` themselves with one `rm -r`. |
| What breaks trust | An autostart entry that survives uninstall; a registry key left behind; a phantom service still listening. |
| Guarded by | Per-user install (no admin keys); the launch agent / Run-key registrations are removed by the uninstaller; the [uninstall doc](../../apps/docs/uninstall.mdx) walks every artefact. |

---

## The asymmetry

A first that goes *right* earns about one unit of trust. A first
that goes *wrong* costs roughly five — and #4 (a wrong recovery)
can be terminal on its own. The guards on every row above are
deliberately conservative for that reason: Recall would rather miss
one of these firsts than fake it.

The seven firsts compound: each one is more powerful if the
previous ones landed. A user whose **first event** they could `cat`
reads the **first investigation** generously. A user whose **first
recovery** named something real treats Recall as a tool they trust
afterwards — not as a system that might be wrong.

That compounding is the product.
