"""Choose a real embedding provider (API or local) and implement this contract."""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class SentenceTransformerEmbedder:
    """Real local embedding model using Sentence Transformers.

    Model: sentence-transformers/all-MiniLM-L6-v2
    Dimensions: 384
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.dimensions = 384
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name, local_files_only=True)
            # Verify dimensions
            sample = self._model.encode(["test"], normalize_embeddings=True)
            self.dimensions = len(sample[0])
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model '{model_name}': {e}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return dense embeddings normalized for cosine similarity."""
        if not texts:
            return []
        vectors = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with stored document vectors."""
        if not question:
            return [0.0] * self.dimensions
        vector = self._model.encode(
            question,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return vector.tolist()


# Alias MyEmbedder to SentenceTransformerEmbedder
MyEmbedder = SentenceTransformerEmbedder
