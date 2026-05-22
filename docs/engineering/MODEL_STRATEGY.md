# MODEL_STRATEGY.md — getting the embedding stack under 150 MB

The 970 MB Recall bundle has one cause: the embedding stack ships
**torch (475 MB)** + **transformers (95 MB)** + **scipy + sklearn
+ numpy (~210 MB)** to power one model call —
`SentenceTransformer("all-MiniLM-L6-v2").encode(texts)`.

This document decides the route from there to a *<150 MB base
install*. Three concrete options, ordered by invasiveness; the
recommendation is at the bottom.

Pairs with [`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md)
(where the weight is) and
[`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md) (how to ship the
result).

---

## What Recall actually uses the model for

The embedding model is consumed by exactly **two** call sites:

1. **[`app/core/embeddings.py`](../../app/core/embeddings.py)** —
   wraps `SentenceTransformer` for the file indexer. Encodes ~800
   char chunks of text into a 384-d float vector and stores them
   in chroma.
2. **`/v1/search`** retrieval — runs the same encoder on the
   user's query, then chroma similarity search.

That is it. No fine-tuning. No multi-model orchestration. No
generation. The model is a **deterministic vector function** —
the same input always produces the same vector. This matters
because every replacement option is judged on whether it produces
the same vectors (or close enough that recall quality holds).

The smoke test ([`_smoke_api.py`](../../_smoke_api.py) § 11) is
the source of truth on quality: a fixed test corpus + queries
that must round-trip to the right files. Any swap below has to
keep that section passing.

---

## Option A — keep torch, use `torch+cpu`

PyPI's default `torch` includes CUDA scaffolding (~140 MB of
stubs the CPU-only build does not need).

| Pro | Con |
|---|---|
| Zero code change (it's a `requirements.txt` edit). | Saves at most ~140 MB unpacked → ~40 MB compressed. Final installer still ~120-150 MB. |
| Same vectors, same quality, same smoke results. | Still ships ~280 MB of torch + transformers; cannot drop further. |
| Reversible — `pip install torch` reverts. | Builds against the PyTorch wheel index, not pure PyPI. The build instructions get one extra line. |

`requirements.txt` change:

```
# pin to the CPU-only PyPI extra index
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.11.0+cpu
```

**Lands the installer at ~150 MB compressed.** Borderline on the
<150 goal. No engineering risk.

---

## Option B — ONNX runtime + bundled model

The `all-MiniLM-L6-v2` model has an officially-maintained ONNX
export. `onnxruntime` is **already in the bundle** (42 MB —
pulled in by chromadb's embedding-function abstraction). The
swap replaces torch + transformers' weight-loading + forward
pass with an `onnxruntime.InferenceSession.run(...)` call. The
fast `tokenizers` library (which is rust-backed and small,
~8 MB) stays — it handles the WordPiece tokenisation that ONNX
expects as int64 input.

**The replacement is ~80 LOC** in `app/core/embeddings.py`:

```python
# Before — sentence-transformers + torch
from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = _model.encode(texts, normalize_embeddings=True)

# After — onnxruntime + tokenizers
import onnxruntime as ort
from tokenizers import Tokenizer

_tok = Tokenizer.from_file(str(_MODEL_DIR / "tokenizer.json"))
_sess = ort.InferenceSession(str(_MODEL_DIR / "model.onnx"),
                              providers=["CPUExecutionProvider"])

def encode(texts: list[str]) -> np.ndarray:
    enc = _tok.encode_batch(texts)
    input_ids = np.array([e.ids for e in enc], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
    out = _sess.run(None, {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": np.zeros_like(input_ids),
    })
    # Mean-pool over the token dimension, then L2-normalise.
    last_hidden = out[0]
    summed = (last_hidden * attention_mask[..., None]).sum(axis=1)
    counts = attention_mask.sum(axis=1)[..., None].clip(min=1)
    pooled = summed / counts
    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    return pooled / norms.clip(min=1e-9)
```

`np` here is numpy (already in the bundle). The output vector is
**bit-identical** to sentence-transformers' default
`normalize_embeddings=True` output (sentence-transformers itself
uses mean-pool + L2-norm for this model — the wrapper is just
sugar).

| Pro | Con |
|---|---|
| Drops **torch (-475 MB)** + **transformers (-95 MB)**. | One real code change — needs smoke verification. |
| Re-uses `onnxruntime` already in the bundle. | Quantised int8 variant is even smaller but produces *very slightly* different vectors — must verify on Recall's smoke. |
| The model file (`model.onnx`, ~80 MB) ships **bundled**, not as a first-run download. | Bundle gets ~80 MB heavier on the model file but ~570 MB lighter on the runtime → net **-490 MB**. |
| Quality unchanged at FP32. | Int8 quantisation (~22 MB instead of 80 MB) is a follow-up. |

**Lands the installer at ~50-60 MB compressed.** Comfortably under
150. The model file is downloaded once *at build time* (~80 MB
ONNX export from `Xenova/all-MiniLM-L6-v2` on HF) and bundled.

---

## Option C — lazy first-run download (Split Distribution)

The most invasive but the smallest *base* install: don't bundle
the model at all. Ship Recall with *keyword-only* search
(`grep`-style over indexed text); the user gets full semantic
search by downloading the Retrieval Pack from Settings.

| Pro | Con |
|---|---|
| **Base installer under 50 MB compressed.** | Two artifacts to maintain instead of one. |
| Semantic search becomes an opt-in moment users actively choose. | First-run experience without the pack is *degraded* (keyword-only). |
| Avoids the "what's in 260 MB?" question entirely on first install. | The user has to make a download choice they may not understand. |

Detailed in [`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md). The
two-artifact split is the *product* answer; B is the *engineering*
answer.

---

## Lighter sentence models (briefly considered, rejected)

| Model | Param count | Size | Verdict |
|---|---:|---:|---|
| `all-MiniLM-L6-v2` (today) | 22 M | ~80 MB FP32 / ~22 MB int8 | the baseline; quality good for the use case |
| `all-MiniLM-L12-v2` | 33 M | ~120 MB | bigger but not dramatically better; **skip** |
| `bge-micro-v2` | 17 M | ~65 MB | newer, comparable quality, slightly worse on STS — close call; revisit if MiniLM is ever EOL'd |
| `nomic-embed-text-v1.5` | 137 M | ~520 MB | high quality but far too heavy for a local-first install |
| `model2vec` distillations | 8 M | ~30 MB | fast but lower recall on long-form text; **skip** for now |

The current model is the right one. The *runtime* is the
problem, not the model.

---

## Quantisation (a tier inside Option B)

Quantising `model.onnx` to int8 produces:

- **Size:** ~22 MB (vs ~80 MB FP32)
- **Quality:** within 1-2% on STS / classification benchmarks
- **Speed:** comparable on CPU; sometimes faster

Recall's quality smoke uses 30-ish test queries against a small
corpus; int8 vectors need to be checked against the same smoke
to ensure top-1 hit rates don't degrade. If they hold, **the
combined Tier-C+Q artifact is ~32 MB compressed**.

The conservative landing path:

1. Ship FP32 ONNX first (verifiable, predictable).
2. Replace with int8 only after a full smoke + a 24-hour real
   indexing run on a maintainer machine shows no quality loss.

---

## Recommendation

**Land Tier B (ONNX runtime + bundled FP32 model).**

Reasons in order of weight:

1. **It gets under the <150 MB goal with margin** (~50-60 MB
   compressed, vs Tier A's 180 MB or Tier A+B's 130-150 MB).
2. **It does not introduce a download-on-first-run failure
   mode**. The model ships in the installer; offline-first holds.
3. **The 80-line code change is bounded and reversible** — one
   module (`app/core/embeddings.py`) gets a new implementation
   behind the same interface.
4. **`onnxruntime` is already in the bundle.** The swap *removes*
   torch, transformers, sentence-transformers, and ~half of
   scipy/sklearn (their main consumer goes away).
5. **It's a precondition for the eventual Split Distribution.**
   Once the embedding stack is ONNX-only, splitting it into a
   *Retrieval Pack* becomes a build-time directory swap, not an
   engineering project.

The **Split Distribution doc** ([`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md))
takes the Tier-B artifact as input and shows how to slice it into
*Recall Core* (~30 MB) + *Recall Retrieval Pack* (~80 MB), with
the same single installer dispatching to either.

---

## Sequencing — what to do in what order

| # | Step | Net change | Builds passed |
|---|---|---|---|
| 1 | Apply Tier A excludes (`imageio_ffmpeg`, `pyarrow`, Qt6 unused modules, `tzdata`) | -300 MB unpacked | `_smoke_api.py` |
| 2 | Pin `torch==X+cpu` | -140 MB unpacked | `_smoke_api.py` |
| 3 | Land an ONNX-backed `app/core/embeddings.py` behind a feature flag (default off) | +80 MB (model) | `_smoke_api.py` §11 must show same top-1 hit rates |
| 4 | Flip the flag default on; rebuild | -460 MB unpacked | full smoke + offline-bootstrap test |
| 5 | Quantise to int8 | -60 MB unpacked | smoke quality re-check |
| 6 | (Optional) Split into Core + Retrieval Pack | base -80 MB; pack +80 MB | distribution + first-run test |

Steps 1-2 are *immediate*. Step 3 is the engineering moment. Steps
4-6 are the payoff.

> Cross-referenced by
> [`INSTALL_SIZE_AUDIT_V2.md`](INSTALL_SIZE_AUDIT_V2.md) (the
> bytes that fall away),
> [`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md) (the packaging
> result), and the *Performance* rows of
> [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md).
