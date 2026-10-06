from abc import ABC, abstractmethod
import math
import hashlib

class BaseEmbeddingService(ABC):
    """
    Abstract interface for multilingual text embedding generation.
    Supports English, Hindi, and Marathi representations.
    """
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate a dense vector for a single text string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate dense vectors for a batch of text strings."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""
        pass


class DeterministicMultilingualEmbeddingService(BaseEmbeddingService):
    """
    A lightweight, deterministic embedding generator for local development,
    testing, and CI environments without requiring multi-gigabyte PyTorch/Transformers models.
    Produces repeatable normalized vectors using a SHA-256 hash-projection approach.
    """
    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self._dim

        # Generate a deterministic pseudo-embedding based on character n-grams and hashing
        words = text.lower().split()
        vector = [0.0] * self._dim

        for word in words:
            # Hash each token into buckets
            h = hashlib.sha256(word.encode("utf-8")).digest()
            for i in range(min(len(h), self._dim)):
                bucket = (h[i] + i * 31) % self._dim
                weight = ((h[i] % 100) / 100.0) - 0.5
                vector[bucket] += weight

        # Normalize to unit length (L2 norm) for cosine similarity
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 1e-9:
            vector = [x / norm for x in vector]
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]
