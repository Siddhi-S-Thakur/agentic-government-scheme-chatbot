from typing import Optional
from app.schemas.retrieval_schema import RetrievedEvidence

class ReciprocalRankFusion:
    """
    Combines dense vector retrieval and sparse BM25 lexical retrieval results
    using Reciprocal Rank Fusion (RRF).
    
    RRF Score formula:
        RRF_Score(d) = sum_{m in models} ( 1 / (k + rank_m(d)) )
    where:
        - k is a smoothing constant (standard default is 60).
        - rank_m(d) is the 1-based rank position in model m's result list.
    """
    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        vector_results: list[RetrievedEvidence],
        bm25_results: list[RetrievedEvidence],
        top_k: Optional[int] = None
    ) -> list[RetrievedEvidence]:
        """
        Merges vector and BM25 candidate lists into a unified ranked list.
        Preserves individual vector and BM25 scores for complete observability.
        """
        # Map: chunk_id -> dict with evidence object and rank tracking
        candidates: dict[str, dict] = {}

        # 1. Process vector rankings
        for rank_zero, item in enumerate(vector_results):
            rank = rank_zero + 1
            chunk_id = item.chunk_id
            if chunk_id not in candidates:
                candidates[chunk_id] = {
                    "item": item.model_copy(),
                    "rrf_score": 0.0,
                    "in_vector": True,
                    "in_bm25": False,
                }
            candidates[chunk_id]["rrf_score"] += 1.0 / (self.k + rank)
            candidates[chunk_id]["item"].vector_score = item.vector_score

        # 2. Process BM25 rankings
        for rank_zero, item in enumerate(bm25_results):
            rank = rank_zero + 1
            chunk_id = item.chunk_id
            if chunk_id not in candidates:
                candidates[chunk_id] = {
                    "item": item.model_copy(),
                    "rrf_score": 0.0,
                    "in_vector": False,
                    "in_bm25": True,
                }
            else:
                candidates[chunk_id]["in_bm25"] = True

            candidates[chunk_id]["rrf_score"] += 1.0 / (self.k + rank)
            candidates[chunk_id]["item"].bm25_score = item.bm25_score

        # 3. Build fused results
        fused_list: list[RetrievedEvidence] = []
        for chunk_id, entry in candidates.items():
            ev: RetrievedEvidence = entry["item"]
            ev.fusion_score = round(entry["rrf_score"], 6)

            if entry["in_vector"] and entry["in_bm25"]:
                ev.retrieval_source = "hybrid"
            elif entry["in_vector"]:
                ev.retrieval_source = "vector"
            else:
                ev.retrieval_source = "bm25"

            fused_list.append(ev)

        # 4. Sort descending by fusion_score
        fused_list.sort(key=lambda x: x.fusion_score or 0.0, reverse=True)

        if top_k is not None:
            return fused_list[:top_k]
        return fused_list
