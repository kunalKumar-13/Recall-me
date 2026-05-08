"""Folder → text → chunks → embeddings → vector store.

Indexing is incremental: a file is re-embedded only when its mtime is newer
than the latest mtime stored for any of its chunks. This keeps repeated
"Index now" runs cheap.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional

from ..db.store import VectorStore
from .chunker import chunk_text
from .config import Config
from .embeddings import EmbeddingModel
from .parsers import CODE_EXTS, get_parser, is_supported

MAX_FILE_SIZE_MB = 25
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".idea", ".vscode", "dist", "build", "target", ".next", ".cache",
    ".pytest_cache", ".mypy_cache", "site-packages", ".tox",
}

# Code chunks need to be smaller than prose chunks: identifiers are dense,
# 800-char code windows pack a lot of unrelated content around any one
# semantically-meaningful line. 400 gives MiniLM more discriminative power.
CODE_CHUNK_SIZE = 400
CODE_CHUNK_OVERLAP = 60


@dataclass
class IndexProgress:
    files_total: int = 0
    files_done: int = 0
    files_skipped: int = 0
    chunks_added: int = 0
    current_file: str = ""


def _hash_id(path: str, idx: int) -> str:
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]
    return f"{digest}_{idx}"


def _walk_files(folder: Path, enable_ocr: bool) -> Iterable[Path]:
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                continue
            p = Path(root) / name
            try:
                if p.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    continue
            except OSError:
                continue
            if is_supported(p, enable_ocr):
                yield p


class Indexer:
    def __init__(self, config: Config, store: VectorStore, model: EmbeddingModel) -> None:
        self.config = config
        self.store = store
        self.model = model
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def index_folders(
        self,
        folders: List[str],
        progress_cb: Optional[Callable[[IndexProgress], None]] = None,
    ) -> IndexProgress:
        self._cancel = False
        progress = IndexProgress()

        all_files: List[Path] = []
        for folder in folders:
            fp = Path(folder)
            if not fp.exists() or not fp.is_dir():
                continue
            all_files.extend(_walk_files(fp, self.config.enable_ocr))

        progress.files_total = len(all_files)
        if progress_cb:
            progress_cb(progress)

        indexed = self.store.get_indexed_files()

        for path in all_files:
            if self._cancel:
                break
            spath = str(path)
            progress.current_file = path.name
            try:
                mtime = path.stat().st_mtime
            except OSError:
                self._bump(progress, skipped=True, cb=progress_cb)
                continue

            if indexed.get(spath, 0) >= mtime:
                self._bump(progress, skipped=True, cb=progress_cb)
                continue

            success, n_chunks = self._embed_path(path, mtime)
            if success:
                progress.chunks_added += n_chunks
                self._bump(progress, skipped=False, cb=progress_cb)
            else:
                self._bump(progress, skipped=True, cb=progress_cb)
        return progress

    # ---- single-file ops used by the background watcher ------------------

    def index_file(self, path: "Path | str") -> bool:
        """Re-embed a single file, ignoring the mtime cache.

        Used by the filesystem watcher when a file is created or modified.
        Returns True if the file was actually embedded; False if it's
        unsupported, too large, unreadable, or produced no usable text.
        """
        p = Path(path)
        try:
            stat = p.stat()
        except OSError:
            return False
        if stat.st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return False
        if not is_supported(p, self.config.enable_ocr):
            return False
        success, _ = self._embed_path(p, stat.st_mtime)
        return success

    def remove_file(self, path: "Path | str") -> None:
        """Drop every chunk associated with this path. Used on file deletion."""
        self.store.delete_by_path(str(path))

    # ---- internal --------------------------------------------------------

    def _embed_path(self, path: Path, mtime: float):
        """Parse + chunk + embed + store one file. Returns (success, n_chunks)."""
        spath = str(path)
        # Always replace existing chunks for this path before re-storing.
        self.store.delete_by_path(spath)

        parser = get_parser(path, self.config.enable_ocr)
        if parser is None:
            return False, 0
        try:
            text = parser(path)
        except Exception:
            return False, 0
        if not text or not text.strip():
            return False, 0

        if path.suffix.lower() in CODE_EXTS:
            chunks = chunk_text(text, CODE_CHUNK_SIZE, CODE_CHUNK_OVERLAP)
        else:
            chunks = chunk_text(
                text, self.config.chunk_size, self.config.chunk_overlap
            )
        if not chunks:
            return False, 0

        try:
            embeddings = self.model.encode(chunks)
        except Exception:
            return False, 0

        ids = [_hash_id(spath, i) for i in range(len(chunks))]
        metadatas = [
            {
                "path": spath,
                "name": path.name,
                "ext": path.suffix.lower(),
                "mtime": mtime,
                "chunk_index": i,
                "chunk_count": len(chunks),
            }
            for i in range(len(chunks))
        ]
        try:
            self.store.add(ids, embeddings, chunks, metadatas)
        except Exception:
            return False, 0
        return True, len(chunks)

    @staticmethod
    def _bump(progress: IndexProgress, skipped: bool, cb) -> None:
        progress.files_done += 1
        if skipped:
            progress.files_skipped += 1
        if cb:
            cb(progress)
