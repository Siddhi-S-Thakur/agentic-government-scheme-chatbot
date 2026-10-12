from typing import Any, Optional

from app.schemas.profile_schema import UserProfile
from app.schemas.retrieval_schema import RetrievalDebugInfo, RetrievalResponse
from app.rag.embeddings.base import BaseEmbeddingService
from app.rag.vector_store.base import BaseVectorStore
from app.rag.bm25.base import BM25Index
from app.rag.fusion.rrf import ReciprocalRankFusion
from app.rag.reranker.base import BaseReranker
from app.rag.retriever.query_preprocessor import QueryPreprocessor


class HybridRetriever:
    """Hybrid dense + BM25 retrieval with fusion, reranking, and debug metadata."""

    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
        bm25_index: BM25Index,
        reranker: BaseReranker,
        fusion_k: int = 60,
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
        debug: bool = False,
    ) -> RetrievalResponse:
        """Retrieve evidence for the actual query; profile attributes inform ranking,
        while only caller-supplied filters restrict the candidate set.

        Avoid automatically filtering by occupation: a profile value such as 'student'
        is not necessarily identical to the scheme catalogue's beneficiary metadata and
        can accidentally hide relevant central schemes.
        """
        if not query or not query.strip():
            return RetrievalResponse(query="", results=[], total_candidates_found=0)

        normalized_query = QueryPreprocessor.normalize_query(query)
        detected_lang = QueryPreprocessor.detect_script_language(normalized_query)
        if isinstance(profile, UserProfile):
            profile_dict = profile.model_dump(exclude_none=True)
        else:
            profile_dict = dict(profile or {})

        active_filters = dict(filters or {})
        query_vector = self.embedding_service.embed_text(normalized_query)
        vector_results = self.vector_store.search(
            query_vector=query_vector,
            filters=active_filters,
            top_k=max(top_k, candidate_pool_size),
        )
        bm25_results = self.bm25_index.search(
            query=normalized_query,
            filters=active_filters,
            top_k=max(top_k, candidate_pool_size),
        )
        fused_results = self.fusion.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=max(top_k, candidate_pool_size),
        )
        reranked_results = self.reranker.rerank(
            query=normalized_query,
            candidates=fused_results,
            top_k=top_k,
        )
        source_urls = list(dict.fromkeys(
            item.official_url for item in reranked_results if item.official_url
        ))

        debug_info = None
        if debug:
            debug_info = RetrievalDebugInfo(
                original_query=query,
                normalized_query=normalized_query,
                detected_language=detected_lang,
                profile_context=profile_dict or None,
                metadata_filters=active_filters or None,
                vector_results=vector_results,
                bm25_results=bm25_results,
                fusion_results=fused_results,
                reranker_results=reranked_results,
                final_top_k=reranked_results,
                source_urls=source_urls,
            )

        return RetrievalResponse(
            query=normalized_query,
            results=reranked_results,
            total_candidates_found=len(fused_results),
            debug_info=debug_info,
        )
