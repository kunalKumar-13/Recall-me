"""Recall — an AI memory layer for your digital life.

Ask your computer what you forgot. The `Recall` class below is a thin
composition layer so the engine is one-line usable from a REPL or script.

    from app import Recall
    r = Recall()
    r.add_folder("/path/to/notes")
    r.index()
    for hit in r.search("the RL grading thing"):
        print(f"{hit.score:.0%}  {hit.path}")
"""

from __future__ import annotations

# Silence Hugging Face / transformers progress bars and info logs. Must run
# before any sentence-transformers import, so it lives at the top of the
# package. Each `setdefault` respects user overrides via the real env.
import os
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Bound the first-run download path so a flaky connection can't hang for
# minutes. After the first successful download these are unused — the
# loader uses local_files_only=True and never touches the network again.
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "10")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "5")

from pathlib import Path
from typing import Callable, List, Optional

from .core.config import CHROMA_DIR, Config
from .core.embeddings import EmbeddingModel
from .core.indexer import Indexer, IndexProgress
from .core.search import SearchEngine, SearchResult
from .db.store import VectorStore

__version__ = "0.1.0"


class Recall:
    """REPL-friendly facade that wires Config + Store + Model + Indexer + Search."""

    def __init__(self) -> None:
        self.config: Config = Config.load()
        self.store: VectorStore = VectorStore(CHROMA_DIR)
        self.model: EmbeddingModel = EmbeddingModel.get(self.config.embedding_model)
        self.indexer: Indexer = Indexer(self.config, self.store, self.model)
        self.search_engine: SearchEngine = SearchEngine(self.store, self.model)

    # --- folder management ----------------------------------------------------

    def add_folder(self, path: str) -> bool:
        """Add a folder to the index list. Returns False if missing or duplicate."""
        p = Path(path).expanduser().resolve()
        if not p.exists() or not p.is_dir():
            return False
        sp = str(p)
        if sp in self.config.indexed_folders:
            return False
        self.config.indexed_folders.append(sp)
        self.config.save()
        return True

    def remove_folder(self, path: str) -> bool:
        sp = str(Path(path).expanduser().resolve())
        if sp not in self.config.indexed_folders:
            return False
        self.config.indexed_folders.remove(sp)
        self.config.save()
        return True

    @property
    def folders(self) -> List[str]:
        return list(self.config.indexed_folders)

    # --- pipeline -------------------------------------------------------------

    def index(
        self,
        on_progress: Optional[Callable[[IndexProgress], None]] = None,
    ) -> IndexProgress:
        """Index every configured folder. Incremental — unchanged files are skipped."""
        return self.indexer.index_folders(
            self.config.indexed_folders, progress_cb=on_progress
        )

    def search(
        self,
        query: str,
        k: int = 8,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        return self.search_engine.search(query, top_k=k, min_score=min_score)

    # --- store ops ------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "chunks": self.store.count(),
            "folders": list(self.config.indexed_folders),
            "model": self.config.embedding_model,
        }

    def reset(self) -> None:
        """Delete every embedding. Folder list is preserved."""
        self.store.reset()


__all__ = [
    "Recall",
    "Config",
    "EmbeddingModel",
    "Indexer",
    "IndexProgress",
    "SearchEngine",
    "SearchResult",
    "VectorStore",
]
