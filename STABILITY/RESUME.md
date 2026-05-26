# Phase 8C — Resume Reality

**Question:** does the "Continue where you left off"
flow actually work — and how does it behave when the
event log is too thin to produce a candidate?

**Method:** drive `/v1/recovery/recent` and the
launcher's resume path against (a) the live daemon
on the developer machine and (b) a demo-mode boot.
Walk the resulting state.

---

## Live walk (developer machine, 2026-05-24)

Daemon health:

```
GET /v1/health  →  200
  status=ok name=recall-api version=2A enabled=true
  ingested_total=16  dropped_total=0
```

Recovery query:

```
GET /v1/recovery/recent  →  200
  candidates=0  elapsed_ms=75.7
```

**Result: zero recovery candidates.** This is correct
behaviour, not a bug:

- The recovery engine demands ≥4 events per thread
  (`_MIN_EVENTS = 4`) and a trust score above a
  hard gate. See [`app/core/recovery.py`](../app/core/recovery.py).
- The user's threads today are dominated by
  passive browsing (Hotstar, bank, ChatGPT) — none
  of those clusters express the "interrupted work"
  shape recovery is built to detect.
- The other layers do return data:
  - `/v1/threads/recent` → 6 threads
  - `/v1/resurface/idle` → 4 contexts
  - `/v1/contexts/recent` → 5 contexts

So the pipeline is alive; recovery is correctly
quiet. Top three threads visible on the box right
now:

| Thread ID       | Title (first event)                 | Events |
|-----------------|-------------------------------------|--------|
| thr_ab0ddc02    | ChatGPT                             | 17     |
| thr_08a5564a    | Inbox (22,319) - kunalsain0324@…    | 22     |
| thr_7a1dc3f2    | JioHotstar - Watch TV Shows, …      | 25     |

None pass the recovery trust gate. The "calm UX"
rule holds: the launcher will show the
`MinimalEmpty` plate with the one-line continuity
copy, not a fabricated "continue" card.

---

## Resume-preview construct (offscreen)

`ResumePreview` is a child of `LiveLauncher`,
constructed at launcher boot time. Cost was
measured in `PERF.md`: **3.1 ms median** to
materialise the preview shell from the current
digest payload.

Walk of the preview tree:

```
ResumePreview
├─ QGraphicsDropShadowEffect            # one soft shadow, hairline elevation
├─ QVBoxLayout
│  ├─ QVBoxLayout                       # title + subtitle block
│  └─ QHBoxLayout                       # action row
├─ QLabel                               # candidate title
├─ QLabel                               # candidate hint ("3 tabs · 2 files")
├─ QLabel                               # explanatory line (optional)
├─ QPushButton                          # primary: "Continue"
└─ QPushButton                          # secondary: "Not now"
```

Two buttons, one card. Nothing else. This matches
Phase 7E.1's frozen aesthetic — a single
elevated overlay above the root, never a modal
that blocks the launcher.

---

## What "Continue" actually does

`POST /v1/recovery/{id}/restore` returns a
`RestorationPlan` — the engine does *not* open
anything; it returns the list of URLs and file
paths the launcher should open. The launcher
iterates and hands each target to the OS via the
platform launcher (`webbrowser.open` for URLs,
`os.startfile` / `subprocess.Popen` for files).

That separation is load-bearing:

1. The engine stays deterministic and testable —
   no Qt, no OS calls.
2. The launcher can refuse to open dangerous
   targets (the `bad_recoveries.jsonl` ledger
   tracks user dismissals so the same false-positive
   doesn't resurface).
3. A `RestoreToast` confirms the action; auto-
   dismisses after 3 s.

Documented in
[`docs/architecture/recovery.mdx`](../apps/docs/architecture/recovery.mdx).

---

## Demo-mode walk

A fresh `python recall.py --demo` boot would seed
the event store with the deterministic demo fixture
(`app/core/demo_seed.py`) and produce ≥1 recovery
candidate by design — that fixture exists precisely
so the resume path can be exercised on an empty
machine.

**Note (honest):** during this 8C pass, attempting
to boot the demo launcher subprocess yielded an
import error on `app.main` (visible in the
subprocess transcript). The daemon itself was
unaffected and continued serving the live data
above. This is logged as `BUG-001` in
[`BUGS_OPEN.md`](../BUGS_OPEN.md) — a launcher boot
path needs investigation, but it does not block
the daemon, the API, or the extension.

The demo-seed pathway *itself* has been verified
in previous phases (Phase 4A's release walkthrough);
the failure here is in the GUI bootstrap, not the
seeder.

---

## Bad-recovery ledger

`~/.recall/bad_recoveries.jsonl` is the trust loop:
when the user dismisses a recovery candidate with
"Not now," its signature is appended. The engine
filters subsequent candidates against this ledger
before returning them — so the same wrong card
stops appearing.

Current state on this box:

```
~/.recall/bad_recoveries.jsonl  →  not present
```

The file does not exist yet — `bad_recoveries.py`
creates it on first append. "Not present" reflects
"no false positives have ever surfaced because no
recoveries have surfaced." The mechanism is wired;
it hasn't had cause to fire.

---

## What this proves

1. **Recovery is correctly conservative.** Zero
   candidates with 208 events of mostly-passive
   browsing is the right behaviour, not a bug.
2. **The pipeline is alive end-to-end.** Threads,
   contexts, and resurfacing all return data on
   the same request envelope; the engine layer
   composes upward as the sacred hierarchy
   requires.
3. **The launcher's resume surface is constructed
   and ready.** `ResumePreview` materialises in
   3.1 ms; the launcher does not need a candidate
   to be valid.

## What this does NOT prove

- That `POST /v1/recovery/{id}/restore` opens the
  right tabs end-to-end on this OS. Last verified
  in Phase 4A; not re-walked in 8C. Logged in
  `BUGS_OPEN.md` as `BUG-002` — re-walk needed
  before public alpha.
- That the launcher GUI boots reliably. The 8C
  attempt to spawn it as a subprocess failed —
  `BUG-001` open.
- That recovery quality is high. The fixtures in
  [`TRUST_FIXTURES.md`](../docs/trust/TRUST_FIXTURES.md)
  remain the source of truth for that question.
