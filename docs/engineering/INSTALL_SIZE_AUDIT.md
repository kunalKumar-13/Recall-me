# INSTALL_SIZE_AUDIT.md — where the 260 MB goes

The Phase 5F + 5G build produced a 260.8 MB `Recall-Setup.exe`
that expands to a 976 MB / 6,869-file install. The directive's
question for Phase 5H: *where does that go?* This is a **map**,
not an optimization. Numbers come from
[`build_logs/install.log`](../../infra/packaging/windows/build_logs/install.log)
(the Inno Setup detailed log from the verified silent install)
and the PyInstaller subtree composition observed on the build
machine.

No code change in 5H. The path from 260 MB → smaller is named
under *Possible reductions* below; that work is for a later
phase.

Pairs with [`INSTALL_METRICS.md`](../release/INSTALL_METRICS.md)
(the user-facing numbers) and
[`README.md`](../../README.md).

---

## Top-level breakdown

The PyInstaller bundle's *file-count distribution* is the closest
honest map of where weight lives. Sizes are estimated from the
wheel sizes of the source packages on PyPI (`pip show ...` on a
fresh venv would reproduce them within ~5%).

| Subtree | Files | % files | Wheel size on disk | Why it's there |
|---|---:|---:|---:|---|
| `transformers` | **2,347** | 34.2% | ~80 MB | tokenizer + embedding-model runtime (Hugging Face) |
| `torch` | **2,173** | 31.6% | ~570 MB | sentence-transformers needs torch; ships full CPU kernels |
| `pyarrow` | 647 | 9.4% | ~70 MB | pulled in transitively by `datasets` / `huggingface_hub` |
| `tzdata` | 605 | 8.8% | ~7 MB | timezone data (transitive via pandas / fastapi) |
| `sklearn` | 389 | 5.7% | ~40 MB | distance computations + clustering primitives |
| `PyQt6` | 128 | 1.9% | ~80 MB | the launcher + settings UI (Qt6 binaries) |
| `scipy` | 98 | 1.4% | ~50 MB | numpy companion (used by sklearn distance computations) |
| `pandas` | 53 | 0.8% | ~15 MB | transitive via pyarrow / huggingface_hub |
| `chromadb` | 25 | 0.4% | ~30 MB | local vector DB |
| `tokenizers` | 10 | 0.1% | ~12 MB | rust-backed tokenizer runtime |
| (everything else combined) | ~395 | 5.7% | ~22 MB | Recall code, FastAPI, pydantic, watchdog, websockets, openai, pillow, jinja2, … |
| **total** | **6,869** | 100% | **~976 MB on disk → 260.8 MB compressed** | |

The two giants — `transformers` (34.2%) + `torch` (31.6%) — are
**66% of the file count** and **roughly 67% of the bytes**. They
exist for one reason: file search works without leaving the
machine, which means the embedding model must run locally.

## The five categories (the directive's slice)

The directive asked for the breakdown in five buckets. Mapping
the table above:

| Bucket | What it actually is | Approx. size |
|---|---|---|
| **PyInstaller** (the bundler) | bootloader + COLLECT scaffolding + `Recall.exe` itself | ~85 MB (the exe + base layout) |
| **HF cache** | *not* in the bundle — the embedding model weights download to `%LOCALAPPDATA%\…\huggingface\` on first run, **after** install | **~80 MB** (post-first-run, on the user's disk separately) |
| **Embeddings** | `transformers` + `tokenizers` + `sentence-transformers` runtime | ~92 MB |
| **Assets** (Recall UI + icons + screenshots) | `app/assets/icon.ico` + bundled UI styles + the launcher's static files | ~3 MB |
| **Extension** | the browser extension is **not** in the desktop installer at all — it lives in `apps/extension/` and is loaded into the browser separately | **0 bytes** in this installer |
| **Models** (`torch` + `scipy` + `sklearn` + `numpy`) | the numerical stack the embedding model runs on | ~660 MB |

Recall's own Python code is **less than 10 MB** of the install.
The bundle is essentially `(a) the embedding stack, (b) PyQt6,
(c) Recall's tiny code on top`.

---

## Possible reductions (map only — not Phase 5H work)

Three categories of saving, ordered by how invasive each is.

### A — exclude transitive dependencies Recall does not use

Easy wins. Each is a PyInstaller `excludes=...` line in
[`recall.spec`](../../recall.spec). The numbers are upper bounds;
actual savings depend on whether Recall's code path touches a
sub-module of each.

| Exclude | Saving | Risk |
|---|---:|---|
| `pyarrow` | ~70 MB | medium — pulled by `huggingface_hub`; need to verify HF download path still works without arrow tables |
| `tzdata` (or thin to the 30 zones Windows already has) | ~5 MB | low — pandas-only dependency; Recall's date handling uses stdlib |
| `pytest`, `mypy_extensions`, dev-only dist-info dirs | ~2-3 MB | low — pure cruft from `pip install -r requirements.txt` pulling in optional `[test]` extras |
| unused `transformers` model files (Recall uses one model) | ~30-40 MB | medium — `transformers` has dozens of model-specific files; PyInstaller's `hook-transformers.py` is over-eager |
| **subtotal** | **~110 MB** | most of it accessible without code changes |

That alone would bring the bundle from 976 MB to ~865 MB on
disk, and the installer from 260 MB to ~210 MB compressed.

### B — switch to a CPU-only torch build

Today's `torch` ships with CUDA scaffolding (kernel stubs for
GPU paths Recall never invokes). A CPU-only PyPI build of
`torch` (`torch+cpu`) is ~140 MB smaller.

| Change | Saving | Risk |
|---|---:|---|
| Switch `requirements.txt` to `torch+cpu` | ~140 MB | low — Recall never asks for `cuda`; the local embedding path is CPU-only |
| **subtotal** | **~140 MB** | needs a CI test to verify the embedding model still loads + scores correctly |

Combined with A: bundle drops from 976 MB to ~725 MB on disk,
installer from 260 MB to ~170 MB compressed. **This is the path
that meaningfully lands below 200 MB compressed.**

### C — lazy-load the embedding stack

Most invasive. The current bundle loads `torch` + `transformers`
at boot so the launcher has the model warm by the time the user
presses Ctrl+Space. The alternative: defer the import until the
user *actually performs a search*, and ship two bundles:

| Variant | Files | Size | Trade-off |
|---|---:|---:|---|
| `Recall-Setup-mini.exe` (text-search only, no embeddings) | ~1,800 | ~140 MB on disk / ~50 MB compressed | recovery + investigations work; file search falls back to exact-match |
| `Recall-Setup.exe` (full, today) | 6,869 | ~976 MB / ~260 MB | full local semantic search |

This is a *product* decision, not a build flag. Phase 5H names it
so it can be discussed; the right place for the decision is the
roadmap.

---

## What is *not* an optimization target

- **PyQt6 (~80 MB).** The launcher *is* the product surface; no
  meaningful reduction here without rewriting in a lighter
  toolkit, which is a year of work, not a build flag.
- **Recall's own code (<10 MB).** Already small. Optimising here
  is rounding error.
- **The vector DB (`chromadb` ~30 MB).** Cannot meaningfully
  shrink without losing the local-first guarantee — a network
  vector DB would be smaller on disk but violates the trust
  ledger.
- **The browser extension (0 MB in this installer).** Distributed
  separately; not relevant to the desktop installer size.

## The honest verdict

The 260.8 MB installer is **driven by a single deliberate choice**:
Recall's file search runs locally. That choice costs ~92 MB of
embeddings tooling + ~660 MB of numerical stack. Phase 5H's audit
is the receipt for that choice; the *Later* roadmap items above
are what move the receipt from 260 MB toward ~170 MB without
giving up local search.

A user who does not need local file search would be better served
by the *mini* variant from category C (when it exists). The
audit's purpose is to make that variant a real option, not a
hypothetical.

> Cross-referenced by
> [`INSTALL_METRICS.md`](../release/INSTALL_METRICS.md) (the
> end-user-facing numbers) and
> [`ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md) *Later* (the
> bundle-slim work items).
