# SPLIT_DISTRIBUTION.md — four packs, two install paths

Once [`MODEL_STRATEGY.md`](MODEL_STRATEGY.md) lands the ONNX
embedding stack (Tier B), the bundle is no longer one
indivisible mass. This doc names the **four packs** Recall
breaks into and the **two install paths** the user picks
between.

The directive's success criterion was *<60 s install*. With the
Core pack alone, the target becomes *<30 s install* on the build
machine and *<60 s on a clean VM with a slow disk*.

---

## The four packs

| Pack | Size (compressed) | What's in it | Required? |
|---|---:|---|---|
| **Recall Core** | ~30 MB | launcher (PyQt6 Widgets only) · daemon (FastAPI) · chromadb · `app/core/*` engine · `app/ui/*` UI · `recall.py` · `Recall.exe` (PyInstaller-frozen) | **yes** — the product |
| **Recall Retrieval Pack** | ~80 MB | `onnxruntime` · ONNX-bundled `all-MiniLM-L6-v2` (~80 MB FP32, or ~22 MB int8 — see strategy doc) · `tokenizers` · the embedding bridge in `app/core/embeddings.py` | recommended; without it, file search falls back to keyword-match |
| **Recall Dev Tools** | ~5 MB | demo seed script (`app/core/demo_seed.py`), the capture pipeline (`infra/scripts/capture/*`), the size-audit scripts, pyflakes | no — maintainer-only |
| **Recall Demo Seed** | ~2 MB | the fixed demo event log + WebSocket-retry investigation that the smoke test uses | no — only for demos / docs screenshots |

**Total of all four: ~117 MB.** The today-bundle (970 MB
unpacked / 260 MB compressed) is *seven times bigger* than the
sum of all four packs combined.

The two heaviest pieces today — torch (475 MB) and Qt's full
multimedia / 3D / QML stack (~60 MB unused) — disappear entirely
in the Core + Retrieval Pack model.

---

## Two install paths

Same `Recall-Setup.exe`. Two checkboxes on the first wizard page.

### Minimal path (the default)

```
[x] Recall Core                                 (30 MB)
[ ] Recall Retrieval Pack  (semantic search)    (80 MB - downloaded after install)
[ ] Recall Dev Tools                             (5 MB)
[ ] Recall Demo Seed                             (2 MB)

  Total install: 30 MB · ~15 s
```

Default selection: Core only. The installer drops the user into
the first-launch screen; semantic search is *disabled* but file
indexing still runs (chromadb's default keyword + similarity).

A clear `Settings → Search → Enable semantic search` link points
to the Retrieval Pack download. The first time the user opens
the launcher with no semantic results for a sensible query, a
*calm* one-line hint appears in the footer: *"For semantic
search, install the Retrieval Pack — Settings → Search."* No
modal, no prompt, no badge.

### Advanced path (the "I know what I want" check-all)

```
[x] Recall Core                                 (30 MB)
[x] Recall Retrieval Pack                       (80 MB)
[ ] Recall Dev Tools                             (5 MB - for demo + capture)
[ ] Recall Demo Seed                             (2 MB)

  Total install: 110 MB · ~30 s
```

This is the path the *advanced reader* of the alpha packet picks
— equivalent to today's all-in-one install but smaller, since
torch is replaced by onnxruntime + the ONNX model.

The maintainer's own use is **Advanced + Dev Tools**, ~115 MB.

---

## Where each pack lives on disk

Same install root, four subdirectories:

```
%LOCALAPPDATA%\Programs\Recall\
├── Recall.exe                              # Core
├── _internal\                              # Core
│   ├── PyQt6\Qt6\bin\…                     # Core (Widgets only)
│   ├── chromadb\                           # Core
│   ├── fastapi\, uvicorn\, websockets\     # Core
│   ├── app\, api\                          # Core (Recall code)
│   └── …
├── retrieval\                              # Retrieval Pack (optional)
│   ├── onnxruntime\…
│   ├── tokenizers\…
│   ├── model.onnx                          # ~80 MB FP32 (or ~22 MB int8)
│   └── tokenizer.json
├── dev_tools\                              # Dev Tools (optional)
│   ├── capture\…
│   └── audit_install_size_v2.py
└── demo_seed\                              # Demo Seed (optional)
    └── demo-events.jsonl
```

`app/core/embeddings.py` checks for `retrieval/model.onnx` at
boot. If present, semantic search is on. If absent,
`app/core/search.py` falls back to keyword-rank — same query
shape, smaller result set, no crash. No conditional code
elsewhere.

---

## How the installer dispatches

The installer becomes an Inno Setup `[Components]` build instead
of a single one-folder dump. Each pack is a component name:

```iss
[Components]
Name: "core";       Description: "Recall Core";              Types: minimal full custom; Flags: fixed
Name: "retrieval";  Description: "Retrieval Pack (semantic search)"; Types: full custom
Name: "devtools";   Description: "Dev Tools (demo + capture)";       Types: full
Name: "demoseed";   Description: "Demo Seed";                        Types: full

[Types]
Name: "minimal"; Description: "Minimal install (30 MB)"
Name: "full";    Description: "Full install (~110 MB)"
Name: "custom";  Description: "Custom"
```

Existing installer scripting needs three changes:

1. `recall.spec`: produce two separate one-folder bundles (Core
   + Retrieval) under `dist/` instead of one.
2. `recall.iss`: switch the `[Files]` block from one `Source:`
   line to four (one per component, with `Components: <name>`).
3. `build.ps1`: a small `--components` flag that defaults to
   "core retrieval" and supports "core" (minimal-only build) +
   "all".

None of those touches engine code.

---

## What the user actually sees

### Minimal install — the default

1. Double-click `Recall-Setup.exe`. SmartScreen warns (still
   unsigned; see [`GO_NO_GO.md`](../release/GO_NO_GO.md) gate 7).
2. Wizard: *Welcome → Components (default: Core checked, others
   unchecked) → Install*.
3. **~15 s** to install. Recall opens; first-launch onboarding;
   user picks folders; **keyword search** works.
4. Day 2: user notices semantic search would be useful. Settings
   → Search → *Enable semantic search*. Downloads the Retrieval
   Pack (~80 MB). Re-indexes existing folders (cached chunks; no
   re-tokenisation needed since chromadb stored the raw text).

### Full install — for the maintainer / advanced tester

1. Wizard: *Welcome → Components → check Retrieval Pack → Install*.
2. **~30 s** to install. Everything works on first launch.
3. Same first-launch as today, just lighter on disk.

---

## Trade-offs vs the today-bundle

| Property | Today (970 MB / 260 MB) | Split (Core 30 MB) |
|---|---|---|
| First impression | 260 MB download is a lot to hand a stranger | 30 MB feels like a *small* app |
| Install time | ~66 s | ~15 s |
| Resident memory after warm-up | 623 MB (torch + chromadb warm) | ~150 MB (chromadb only) |
| Semantic search on Day 0 | yes | no (keyword only until pack installed) |
| Semantic search after pack | n/a — built in | yes; resident memory rises to ~300 MB |
| Offline first run | yes | yes (Core works offline; Pack only downloads if user chooses) |
| One-file distribution | yes | yes — same `Recall-Setup.exe`, the user picks components |
| Update story | install-over-install | per-pack updates possible (Core can patch without re-downloading the Pack) |

The trade-off the maintainer accepts in the Split model: **Day 0
file search is keyword-only by default.** The argument for it
being acceptable:

- The alpha cohort's actual Day 0-1 is described in
  [`alpha/SAMPLE_WORKFLOW.md`](../../alpha/SAMPLE_WORKFLOW.md):
  *"the first day shows nothing"*. Day 0 is not when semantic
  search earns its keep; it earns it on Day 3+.
- The *Continuity* product surface — recoveries, investigations,
  resurfacing — does **not** use the embedding model at all.
  Those are deterministic ledger-based reconstructions; they
  work identically with or without the Retrieval Pack.
- The pack is one click away in Settings, with a calm one-line
  prompt the first time semantic search would have helped.

---

## What this means for the alpha-001 cohort

The cohort gets the **Full install** (Core + Retrieval Pack) so
the alpha experience matches today's experience apart from the
faster install. The minimal-path benefit lands at *public alpha*,
when the website's *Download for Windows* button serves a 30 MB
file instead of a 260 MB one. [`LANDING_GO_LIVE.md`](../release/LANDING_GO_LIVE.md)
already names this as the right hero-button copy
("Download · 30 MB" not "Download · 260 MB").

---

## What this is not

- **Not a sync layer.** Each pack is downloaded once; no
  per-update streaming. The Trust Ledger contract holds.
- **Not a service tier.** No paid pack, no licensed pack, no
  "Pro version". *All* packs are local-first and open.
- **Not a plugin system.** The packs are file collections, not
  loadable extensions. No third-party packs.

The same single Recall, sliced for the install moment.

> Cross-referenced by
> [`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md) (the
> bytes), [`MODEL_STRATEGY.md`](MODEL_STRATEGY.md) (the engine
> precondition), [`LANDING_GO_LIVE.md`](../release/LANDING_GO_LIVE.md)
> (the hero-button consequence), and
> [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) § *Performance*.
