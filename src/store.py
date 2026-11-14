"""Store and search vectors using ChromaDB persistent local vector store."""
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from pathlib import Path
from typing import Any
from .models import Chunk


class ChromaVectorStore:
    """Persistent local vector store using ChromaDB with cosine similarity and metadata filtering."""

    def __init__(self, persist_directory: str = "./chroma_db", dimensions: int = 384) -> None:
        self.persist_directory = persist_directory
        self.dimensions = dimensions
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=str(persist_directory))
        except ImportError:
            raise ImportError("chromadb is required. Install with: pip install chromadb")

    def _get_collection(self, strategy: str):
        collection_name = f"day06_{strategy.lower()}"
        return self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def create_schema(self) -> None:
        """Initialize collections for strategies A, B, and C."""
        for strategy in ["strategy_A", "strategy_B", "strategy_C"]:
            self._get_collection(strategy)

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Validate lengths and write stable IDs without duplicates (idempotent upsert)."""
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunk count ({len(chunks)}) does not match vector count ({len(vectors)})")
        if not chunks:
            return

        collection = self._get_collection(strategy)

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = []
        for c in chunks:
            meta = {
                "document_id": str(c.document_id),
                "source": str(c.source),
                "page": int(c.page),
            }
            # Add extra filter metadata if present
            for k, v in c.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
            metadatas.append(meta)

        # Chroma upsert updates existing IDs or inserts new ones safely
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=vectors,
            metadatas=metadatas
        )

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Filter metadata in vector store, rank by cosine similarity, and return top-k."""
        collection = self._get_collection(strategy)

        where_clause: dict[str, Any] | None = None
        if filters:
            # Build valid Chroma where clause
            filter_conditions = []
            for k, v in filters.items():
                if v is not None:
                    filter_conditions.append({k: {"$eq": v}})
            if len(filter_conditions) == 1:
                where_clause = filter_conditions[0]
            elif len(filter_conditions) > 1:
                where_clause = {"$and": filter_conditions}

        query_kwargs: dict[str, Any] = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_clause:
            query_kwargs["where"] = where_clause

        results = collection.query(**query_kwargs)

        hits: list[dict[str, Any]] = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0] if results.get("documents") else []
            metas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for i in range(len(ids)):
                dist = distances[i] if i < len(distances) else 1.0
                # Cosine similarity for normalized vectors: sim = 1 - distance
                similarity = max(0.0, min(1.0, 1.0 - dist))
                hits.append({
                    "chunk_id": ids[i],
                    "text": docs[i] if i < len(docs) else "",
                    "score": round(similarity, 4),
                    "distance": round(dist, 4),
                    "metadata": metas[i] if i < len(metas) else {}
                })
        return hits


# Alias VectorStore to ChromaVectorStore for flexibility
VectorStore = ChromaVectorStore
