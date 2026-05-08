"""Lazy-loaded sentence-transformers wrapper.

The model (~80MB) is loaded on first use rather than at import so the
launcher stays snappy on cold start. Embeddings are L2-normalized so the
default cosine distance in Chroma behaves like a similarity score.

Loading is **offline-first**. We always try to load from the local cache
with `local_files_only=True` first. After the first successful download
this path always succeeds, so subsequent runs make zero network calls —
no HEAD requests, no metadata sync, nothing that can hang on slow DNS or
HF outages. The online path is exercised only when the cache is genuinely
missing (first install, or user nuked their HF cache).

If both offline and online loads fail, we raise `EmbeddingModelMissing`
with a short, user-readable message. The caller (search worker thread)
surfaces it via the launcher's failure path; the UI thread is never
blocked because the search runs on a `QThread`.
"""

from __future__ import annotations

import sys
import threading
from typing import List, Sequence


class EmbeddingModelMissing(RuntimeError):
    """The embedding model is neither cached locally nor downloadable."""


class EmbeddingModel:
    _instance: "EmbeddingModel | None" = None
    _instance_lock = threading.Lock()

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None
        self._load_lock = threading.Lock()

    @classmethod
    def get(cls, model_name: str = "all-MiniLM-L6-v2") -> "EmbeddingModel":
        with cls._instance_lock:
            if cls._instance is None or cls._instance.model_name != model_name:
                cls._instance = cls(model_name)
            return cls._instance

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            from sentence_transformers import SentenceTransformer

            # Path 1: local cache, no network. The expected fast path on
            # every run after the first install.
            offline_err: Exception | None = None
            try:
                self._model = SentenceTransformer(
                    self.model_name, local_files_only=True
                )
                return
            except Exception as e:
                offline_err = e

            # Path 2: cache miss → one-time online download. Bounded by
            # HF_HUB_DOWNLOAD_TIMEOUT / HF_HUB_ETAG_TIMEOUT (set in
            # app/__init__.py) so it can't hang indefinitely.
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as online_err:
                print(
                    f"[recall] could not load embedding model "
                    f"{self.model_name!r}\n"
                    f"  offline: {offline_err}\n"
                    f"  online:  {online_err}",
                    file=sys.stderr,
                )
                raise EmbeddingModelMissing(
                    "Embedding model is not cached and could not be "
                    "downloaded. Connect to the internet on the first run; "
                    "Recall is fully offline after that."
                ) from online_err
            else:
                print(
                    f"[recall] downloaded embedding model "
                    f"{self.model_name!r}; future runs are fully offline.",
                    file=sys.stderr,
                )

    def encode(self, texts: Sequence[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []
        self._ensure_loaded()
        vectors = self._model.encode(
            list(texts),
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vectors.tolist()

    def encode_one(self, text: str) -> List[float]:
        return self.encode([text])[0]
