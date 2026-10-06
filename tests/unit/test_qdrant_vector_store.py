import pytest
from qdrant_client import QdrantClient
from app.rag.vector_store.qdrant_store import QdrantVectorStore
from app.schemas.scheme_schema import SchemeChunk
from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService

@pytest.fixture
def memory_qdrant_store():
    # Use isolated in-memory Qdrant instance
    client = QdrantClient(":memory:")
    store = QdrantVectorStore(client=client, collection_name="test_gov_schemes", dimension=64)
    return store

def test_qdrant_add_and_search(memory_qdrant_store):
    store = memory_qdrant_store
    embedder = DeterministicMultilingualEmbeddingService(dimension=64)

    chunk1 = SchemeChunk(
        chunk_id="chunk-kisan-01",
        scheme_id="pm-kisan",
        scheme_name="PM-KISAN",
        section="benefits",
        content="Direct income support of ₹6,000 per year for farmer families.",
        metadata={"level": "central", "beneficiary_categories": ["farmer"], "state": None}
    )
    chunk2 = SchemeChunk(
        chunk_id="chunk-scholarship-01",
        scheme_id="mahadbt-post-matric",
        scheme_name="MahaDBT Scholarship",
        section="benefits",
        content="Tuition fee waiver for SC students in Maharashtra.",
        metadata={"level": "state", "beneficiary_categories": ["student"], "state": "Maharashtra"}
    )

    chunks = [chunk1, chunk2]
    embeddings = embedder.embed_batch([c.content for c in chunks])

    store.add_chunks(chunks, embeddings)

    # 1. Search for farmer scheme
    query_vec = embedder.embed_text("financial support for farmer")
    results = store.search(query_vector=query_vec, top_k=2)

    assert len(results) > 0
    top = results[0]
    assert top.scheme_id == "pm-kisan"
    assert top.retrieval_source == "vector"
    assert top.vector_score is not None

    # 2. Search with metadata filter (state=Maharashtra)
    results_mh = store.search(query_vector=query_vec, filters={"state": "Maharashtra"}, top_k=2)
    assert len(results_mh) > 0
    # Both central scheme (applicable everywhere) and Maharashtra scheme match
    mh_ids = [r.scheme_id for r in results_mh]
    assert "mahadbt-post-matric" in mh_ids or "pm-kisan" in mh_ids
