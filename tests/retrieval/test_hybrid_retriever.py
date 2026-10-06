import json
from pathlib import Path
import pytest
from app.schemas.scheme_schema import SchemeRecord
from app.schemas.profile_schema import UserProfile
from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService
from app.rag.vector_store.base import InMemoryVectorStore
from app.rag.bm25.base import BM25Index
from app.rag.reranker.base import DeterministicCrossEncoderReranker
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.rag.ingestion.indexer import SchemeKnowledgeIndexer

@pytest.fixture
def setup_hybrid_retriever():
    base_dir = Path(__file__).resolve().parent.parent.parent
    sample_file = base_dir / "data" / "processed" / "sample_schemes.json"
    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        schemes = [SchemeRecord(**item) for item in data]

    embedding_service = DeterministicMultilingualEmbeddingService()
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    reranker = DeterministicCrossEncoderReranker()

    indexer = SchemeKnowledgeIndexer(embedding_service, vector_store, bm25_index)
    chunks = indexer.index_schemes(schemes)

    retriever = HybridRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        bm25_index=bm25_index,
        reranker=reranker
    )

    return retriever, schemes, chunks

def test_retriever_initialization_and_chunk_count(setup_hybrid_retriever):
    retriever, schemes, chunks = setup_hybrid_retriever
    assert len(schemes) == 4
    # Each scheme is broken into 4 sections (overview, benefits, eligibility, application)
    assert len(chunks) == 16
    assert len(retriever.vector_store.chunks) == 16

def test_english_query_retrieval_and_observability(setup_hybrid_retriever):
    retriever, _, _ = setup_hybrid_retriever
    query = "PM-KISAN scheme benefits for farmers"
    response = retriever.retrieve(query=query, top_k=3, debug=True)

    assert len(response.results) > 0
    top_result = response.results[0]
    assert top_result.scheme_id == "pm-kisan"
    assert top_result.official_url == "https://pmkisan.gov.in"
    assert top_result.reranker_score is not None

    # Check Debug Observability
    debug = response.debug_info
    assert debug is not None
    assert debug.original_query == query
    assert len(debug.vector_results) > 0
    assert len(debug.bm25_results) > 0
    assert len(debug.fusion_results) > 0
    assert len(debug.source_urls) > 0
    assert "https://pmkisan.gov.in" in debug.source_urls

def test_marathi_query_retrieval(setup_hybrid_retriever):
    retriever, _, _ = setup_hybrid_retriever
    query = "संजय गांधी निराधार अनुदान योजना"
    response = retriever.retrieve(query=query, top_k=3, debug=False)

    assert len(response.results) > 0
    top_scheme_ids = [r.scheme_id for r in response.results]
    assert "sanjay-gandhi-niradhar" in top_scheme_ids

def test_metadata_filtering_by_state(setup_hybrid_retriever):
    retriever, _, _ = setup_hybrid_retriever
    # Query with profile specifying Maharashtra
    profile = UserProfile(state="Maharashtra", occupation="student")
    response = retriever.retrieve(
        query="Post matric scholarship",
        profile=profile,
        top_k=3,
        debug=True
    )

    assert len(response.results) > 0
    top_result = response.results[0]
    assert top_result.scheme_id == "mahadbt-post-matric"
    assert response.debug_info.metadata_filters["state"] == "Maharashtra"
