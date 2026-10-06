from abc import ABC, abstractmethod
from typing import Optional
import re
from app.schemas.retrieval_schema import RetrievedEvidence

class BaseReranker(ABC):
    """
    Abstract interface for cross-encoder reranking models (e.g., BGE-Reranker).
    Reranks candidates based on deep query-document cross-attention scoring.
    """
    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[RetrievedEvidence],
        top_k: Optional[int] = None
    ) -> list[RetrievedEvidence]:
        """Rerank candidate evidence items against the query."""
        pass


class DeterministicCrossEncoderReranker(BaseReranker):
    """
    A lightweight, deterministic reranker implementation for development, unit testing,
    and fallback operation without requiring heavyweight PyTorch models.
    Scores relevance by calculating cross-token overlap, exact scheme title matching,
    and domain-section alignment.
    """
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name

    def _score_candidate(self, query: str, candidate: RetrievedEvidence) -> float:
        query_words = set(re.findall(r"[\w\u0900-\u097F]+", query.lower(), flags=re.UNICODE))
        if not query_words:
            return 0.0

        content_words = set(re.findall(r"[\w\u0900-\u097F]+", candidate.content.lower(), flags=re.UNICODE))
        title_words = set(re.findall(r"[\w\u0900-\u097F]+", candidate.scheme_name.lower(), flags=re.UNICODE))

        # Title match score (high weight for matching exact scheme name)
        title_overlap = len(query_words.intersection(title_words)) / max(len(query_words), 1)

        # Content match score
        content_overlap = len(query_words.intersection(content_words)) / max(len(query_words), 1)

        # Bonus for chunks directly answering eligibility/benefits if query looks for criteria
        section_bonus = 0.0
        if candidate.section == "eligibility" and any(k in query.lower() for k in ["eligible", "पात्र", "पात्रता", "criteria", "age", "income"]):
            section_bonus = 0.2
        elif candidate.section == "benefits" and any(k in query.lower() for k in ["benefit", "लाभ", "फायदे", "money", "subsidy"]):
            section_bonus = 0.2

        # Blend with prior fusion score if available
        base_fusion = candidate.fusion_score or 0.0

        rerank_score = (0.45 * title_overlap) + (0.35 * content_overlap) + (0.10 * base_fusion) + section_bonus
        return round(rerank_score, 4)

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedEvidence],
        top_k: Optional[int] = None
    ) -> list[RetrievedEvidence]:
        if not candidates:
            return []

        reranked: list[RetrievedEvidence] = []
        for cand in candidates:
            score = self._score_candidate(query, cand)
            copy_cand = cand.model_copy()
            copy_cand.reranker_score = score
            reranked.append(copy_cand)

        # Sort descending by reranker_score, tie-break on fusion_score
        reranked.sort(
            key=lambda x: (x.reranker_score or 0.0, x.fusion_score or 0.0),
            reverse=True
        )

        if top_k is not None:
            return reranked[:top_k]
        return reranked
