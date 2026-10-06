import pytest
from app.schemas.retrieval_schema import RetrievedEvidence
from app.rag.fusion.rrf import ReciprocalRankFusion

def test_rrf_fusion_logic():
    vector_results = [
        RetrievedEvidence(
            scheme_id="scheme-a",
            scheme_name="Scheme A",
            chunk_id="a-01",
            content="Content A",
            retrieval_source="vector",
            vector_score=0.95
        ),
        RetrievedEvidence(
            scheme_id="scheme-b",
            scheme_name="Scheme B",
            chunk_id="b-01",
            content="Content B",
            retrieval_source="vector",
            vector_score=0.85
        )
    ]

    bm25_results = [
        RetrievedEvidence(
            scheme_id="scheme-b",
            scheme_name="Scheme B",
            chunk_id="b-01",
            content="Content B",
            retrieval_source="bm25",
            bm25_score=12.5
        ),
        RetrievedEvidence(
            scheme_id="scheme-c",
            scheme_name="Scheme C",
            chunk_id="c-01",
            content="Content C",
            retrieval_source="bm25",
            bm25_score=9.2
        )
    ]

    fusion = ReciprocalRankFusion(k=60)
    fused = fusion.fuse(vector_results, bm25_results)

    assert len(fused) == 3
    # Scheme B appears in both lists (rank 2 in vector, rank 1 in bm25)
    # RRF score for B = 1/(60+2) + 1/(60+1) = 1/62 + 1/61 = 0.016129 + 0.016393 = 0.032522
    # RRF score for A = 1/(60+1) = 0.016393
    # RRF score for C = 1/(60+2) = 0.016129
    # Therefore Scheme B should rank first!
    top = fused[0]
    assert top.chunk_id == "b-01"
    assert top.retrieval_source == "hybrid"
    assert top.vector_score == 0.85
    assert top.bm25_score == 12.5
    assert top.fusion_score > fused[1].fusion_score

    # Check origin for single-source items
    a_item = next(item for item in fused if item.chunk_id == "a-01")
    assert a_item.retrieval_source == "vector"

    c_item = next(item for item in fused if item.chunk_id == "c-01")
    assert c_item.retrieval_source == "bm25"
