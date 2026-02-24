"""
Persistent vector memory using ChromaDB for semantic search over past tasks.
"""
from __future__ import annotations

import hashlib

import chromadb
from chromadb.utils import embedding_functions

from core.config import get_settings

settings = get_settings()


class VectorMemory:
    _instance: VectorMemory | None = None

    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.vector_db_path)
        self._ef = embedding_functions.DefaultEmbeddingFunction()
        self._collection = self._client.get_or_create_collection(
            name="agent_memory",
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def get(cls) -> VectorMemory:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ──────────────────────────────────────────────────────────────────────────

    def store_task_result(
        self,
        task: str,
        result_summary: str,
        task_db_id: int,
        user_id: int,
        files: list[str] | None = None,
    ):
        doc_id = f"task_{hashlib.md5(task.encode()).hexdigest()[:16]}_{task_db_id}"
        document = f"Task: {task}\nResult: {result_summary[:800]}"
        self._collection.upsert(
            ids=[doc_id],
            documents=[document],
            metadatas=[{
                "task": task[:200],
                "task_db_id": task_db_id,
                "user_id": user_id,
                "files": ",".join(files or []),
            }],
        )

    def search_similar(self, query: str, n_results: int = 5, user_id: int | None = None) -> list[dict]:
        where = {"user_id": user_id} if user_id else None
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, self._collection.count() or 1),
                where=where,
            )
        except Exception:
            return []

        items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            items.append({
                "content": doc,
                "metadata": meta,
                "similarity": 1 - dist,
            })
        return items

    def store_knowledge(self, content: str, source: str, category: str = "general"):
        doc_id = f"know_{hashlib.md5(content.encode()).hexdigest()[:16]}"
        self._collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[{"source": source, "category": category}],
        )
