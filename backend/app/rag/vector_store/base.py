from abc import ABC, abstractmethod
from typing import Optional, Any
import math
from app.schemas.scheme_schema import SchemeChunk
from app.schemas.retrieval_schema import RetrievedEvidence

class BaseVectorStore(ABC):
    """
    Abstract interface for dense vector storage and retrieval.
    """
    @abstractmethod
    def add_chunks(self, chunks: list[SchemeChunk], embeddings: list[list[float]]) -> None:
        """Store chunks and their associated dense vectors."""
        pass

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        filters: Optional[dict[str, Any]] = None,
        top_k: int = 10
    ) -> list[RetrievedEvidence]:
        """Perform similarity search with optional metadata pre-filtering."""
        pass


class InMemoryVectorStore(BaseVectorStore):
    """
    In-memory vector store for unit tests, offline development, and evaluation.
    Computes exact cosine similarity and applies metadata filters.
    """
    def __init__(self):
        self.chunks: list[SchemeChunk] = []
        self.vectors: list[list[float]] = []

    def add_chunks(self, chunks: list[SchemeChunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks count ({len(chunks)}) does not match embeddings count ({len(embeddings)})")
        self.chunks.extend(chunks)
        self.vectors.extend(embeddings)

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        return dot / (norm_a * norm_b)

    def _matches_filters(self, chunk: SchemeChunk, filters: Optional[dict[str, Any]]) -> bool:
        if not filters:
            return True
        for key, val in filters.items():
            if val is None:
                continue
            meta = chunk.metadata
            if key == "state":
                chunk_state = meta.get("state")
                level = meta.get("level", "central")
                # Central schemes are applicable across all states
                if level == "central":
                    continue
                if chunk_state and chunk_state.lower() != str(val).lower():
                    return False
            elif key == "beneficiary_categories":
                categories = [c.lower() for c in meta.get("beneficiary_categories", [])]
                if isinstance(val, list):
                    if not any(v.lower() in categories for v in val):
                        return False
                elif isinstance(val, str):
                    if val.lower() not in categories and categories:
                        return False
            elif key in meta and meta[key] != val:
                return False
        return True

    def search(
        self,
        query_vector: list[float],
        filters: Optional[dict[str, Any]] = None,
        top_k: int = 10
    ) -> list[RetrievedEvidence]:
        scored_candidates: list[tuple[float, SchemeChunk]] = []

        for chunk, vector in zip(self.chunks, self.vectors):
            if not self._matches_filters(chunk, filters):
                continue
            score = self._cosine_similarity(query_vector, vector)
            scored_candidates.append((score, chunk))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_candidates[:top_k]

        evidence_list: list[RetrievedEvidence] = []
        for score, chunk in top_candidates:
            evidence_list.append(
                RetrievedEvidence(
                    scheme_id=chunk.scheme_id,
                    scheme_name=chunk.scheme_name,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    section=chunk.section,
                    retrieval_source="vector",
                    vector_score=round(score, 4),
                    metadata=chunk.metadata,
                    official_url=chunk.metadata.get("official_url")
                )
            )
        return evidence_list
