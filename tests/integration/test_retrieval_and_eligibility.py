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
from app.eligibility.service import EligibilityService
from app.eligibility.models import EligibilityStatus

@pytest.fixture
def integrated_system():
    base_dir = Path(__file__).resolve().parent.parent.parent
    sample_file = base_dir / "data" / "processed" / "sample_schemes.json"
    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        schemes = [SchemeRecord(**item) for item in data]

    schemes_catalog = {s.scheme_id: s for s in schemes}

    embedding_service = DeterministicMultilingualEmbeddingService()
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    reranker = DeterministicCrossEncoderReranker()

    indexer = SchemeKnowledgeIndexer(embedding_service, vector_store, bm25_index)
    indexer.index_schemes(schemes)

    retriever = HybridRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        bm25_index=bm25_index,
        reranker=reranker
    )

    return retriever, schemes_catalog

def test_retrieval_to_eligibility_pipeline_eligible(integrated_system):
    retriever, catalog = integrated_system

    # Citizen: 30-year-old farmer in Maharashtra
    profile = UserProfile(
        age=30,
        state="Maharashtra",
        occupation="farmer"
    )

    # 1. Retrieve evidence
    retrieval_res = retriever.retrieve(
        query="PM-KISAN financial assistance for farmers",
        profile=profile,
        top_k=5,
        debug=True
    )
    assert len(retrieval_res.results) > 0

    # 2. Evaluate eligibility over retrieved candidates
    recommendations = EligibilityService.evaluate_retrieved_schemes(
        profile=profile,
        evidence=retrieval_res.results,
        schemes_catalog=catalog
    )
    assert len(recommendations) > 0

    # PM-KISAN should be evaluated as ELIGIBLE
    pm_kisan_rec = next(r for r in recommendations if r.scheme_id == "pm-kisan")
    assert pm_kisan_rec.status == EligibilityStatus.ELIGIBLE
    assert pm_kisan_rec.official_url == "https://pmkisan.gov.in"
    assert pm_kisan_rec.top_evidence_snippet is not None
    assert len(pm_kisan_rec.matched_conditions) >= 2

def test_retrieval_to_eligibility_pipeline_missing_info(integrated_system):
    retriever, catalog = integrated_system

    # Citizen: Student looking for scholarship in Maharashtra, but hasn't entered income or caste
    profile = UserProfile(
        state="Maharashtra",
        occupation="student"
    )

    retrieval_res = retriever.retrieve(
        query="Post matric scholarship for students in Maharashtra",
        profile=profile,
        top_k=5
    )
    assert len(retrieval_res.results) > 0

    recommendations = EligibilityService.evaluate_retrieved_schemes(
        profile=profile,
        evidence=retrieval_res.results,
        schemes_catalog=catalog
    )
    scholarship_rec = next((r for r in recommendations if r.scheme_id == "mahadbt-post-matric"), None)
    assert scholarship_rec is not None
    assert scholarship_rec.status == EligibilityStatus.INFORMATION_MISSING
    assert "annual_income" in scholarship_rec.missing_fields
    assert "caste_category" in scholarship_rec.missing_fields
