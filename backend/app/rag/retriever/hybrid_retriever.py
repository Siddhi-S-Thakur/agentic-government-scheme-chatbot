from typing import Optional, Any
from app.schemas.profile_schema import UserProfile
from app.schemas.retrieval_schema import (
    RetrievedEvidence,
    RetrievalDebugInfo,
    RetrievalResponse,
)
from app.rag.embeddings.base import BaseEmbeddingService
from app.rag.vector_store.base import BaseVectorStore
from app.rag.bm25.base import BM25Index
from app.rag.fusion.rrf import ReciprocalRankFusion
from app.rag.reranker.base import BaseReranker
from app.rag.retriever.query_preprocessor import QueryPreprocessor

class HybridRetriever:
    """
    Core Hybrid RAG Retrieval Engine.
    Orchestrates:
      1. Query Preprocessing & Language Normalization
      2. Metadata Pre-filtering (State, Beneficiary, Category)
      3. Vector Search (Dense Semantic Retrieval)
      4. BM25 Search (Sparse Lexical Keyword Retrieval)
      5. Reciprocal Rank Fusion (RRF)
      6. Cross-Encoder Reranking
      7. Top-K Evidence Construction with Full Observability
    """
    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
        bm25_index: BM25Index,
        reranker: BaseReranker,
        fusion_k: int = 60
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.reranker = reranker
        self.fusion = ReciprocalRankFusion(k=fusion_k)

    def retrieve(
        self,
        query: str,
        profile: Optional[UserProfile | dict[str, Any]] = None,
        filters: Optional[dict[str, Any]] = None,
        top_k: int = 5,
        candidate_pool_size: int = 20,
        debug: bool = False
    ) -> RetrievalResponse:
        """
        Execute the end-to-end Hybrid RAG retrieval pipeline.
        """
        # Step A: Query preprocessing
        normalized_query = QueryPreprocessor.normalize_query(query)
        detected_lang = QueryPreprocessor.detect_script_language(normalized_query)

        # Profile context handling
        profile_dict = profile.model_dump() if isinstance(profile, UserProfile) else (profile or {})

        # Step B: Combine metadata filters from explicit filters & profile
        active_filters = dict(filters) if filters else {}
        if profile_dict:
            if "state" not in active_filters and profile_dict.get("state"):
                active_filters["state"] = profile_dict["state"]
            if "beneficiary_categories" not in active_filters and profile_dict.get("occupation"):
                active_filters["beneficiary_categories"] = profile_dict["occupation"]

        # Step C: Dense Vector Search
        query_vector = self.embedding_service.embed_text(normalized_query)
        vector_results = self.vector_store.search(
            query_vector=query_vector,
            filters=active_filters,
            top_k=candidate_pool_size
        )

        # Step D: Sparse BM25 Keyword Search
        bm25_results = self.bm25_index.search(
            query=normalized_query,
            filters=active_filters,
            top_k=candidate_pool_size
        )

        # Step E: Hybrid Fusion via RRF
        fused_results = self.fusion.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=candidate_pool_size
        )

        # Step F: Reranking
        reranked_results = self.reranker.rerank(
            query=normalized_query,
            candidates=fused_results,
            top_k=top_k
        )

        # Step G: Collect unique official source URLs
        source_urls = list({
            item.official_url for item in reranked_results if item.official_url
        })

        debug_info = None
        if debug:
            debug_info = RetrievalDebugInfo(
                original_query=query,
                normalized_query=normalized_query,
                detected_language=detected_lang,
                profile_context=profile_dict if profile_dict else None,
                metadata_filters=active_filters if active_filters else None,
                vector_results=vector_results,
                bm25_results=bm25_results,
                fusion_results=fused_results,
                reranker_results=reranked_results,
                final_top_k=reranked_results,
                source_urls=source_urls
            )

        return RetrievalResponse(
            query=normalized_query,
            results=reranked_results,
            total_candidates_found=len(fused_results),
            debug_info=debug_info
        )
