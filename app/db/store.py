"""ChromaDB persistent vector store.

Each chunk is stored as one record keyed by sha1(path)+chunk_index. The
metadata carries the source file path and mtime so the indexer can skip
unchanged files and so search can dedupe results back to file granularity.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Dict, List


class VectorStore:
    def __init__(self, persist_dir: Path, collection_name: str = "recall") -> None:
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._lock = threading.Lock()

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        with self._lock:
            if self._client is not None:
                return
            import chromadb
            from chromadb.config import Settings

            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    @property
    def collection(self):
        self._ensure_client()
        return self._collection

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if not ids:
            return
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, embedding: List[float], n_results: int = 10) -> List[Dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
        )
        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        dists = (result.get("distances") or [[]])[0]
        out: List[Dict[str, Any]] = []
        for i, _id in enumerate(ids):
            out.append(
                {
                    "id": _id,
                    "document": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else 1.0,
                }
            )
        return out

    def delete_by_path(self, file_path: str) -> None:
        try:
            self.collection.delete(where={"path": file_path})
        except Exception:
            pass

    def get_indexed_files(self) -> Dict[str, float]:
        """Map of file_path -> latest mtime seen for any of its chunks."""
        try:
            result = self.collection.get(include=["metadatas"])
        except Exception:
            return {}
        files: Dict[str, float] = {}
        for meta in result.get("metadatas") or []:
            path = meta.get("path")
            if not path:
                continue
            mtime = float(meta.get("mtime") or 0)
            if mtime > files.get(path, 0):
                files[path] = mtime
        return files

    def count(self) -> int:
        try:
            return int(self.collection.count())
        except Exception:
            return 0

    def reset(self) -> None:
        self._ensure_client()
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
