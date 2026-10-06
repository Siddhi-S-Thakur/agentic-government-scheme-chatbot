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
from app.agent.service import AgentOrchestratorService
from app.eligibility.models import EligibilityStatus

@pytest.fixture
def agent_orchestrator():
    base_dir = Path(__file__).resolve().parent.parent.parent
    sample_file = base_dir / "data" / "processed" / "sample_schemes.json"
    with open(sample_file, "r", encoding="utf-8") as f:
        schemes = [SchemeRecord(**item) for item in json.load(f)]

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

    return AgentOrchestratorService(retriever, schemes_catalog)

def test_orchestrator_asks_clarification_when_info_missing(agent_orchestrator):
    # Query with no profile information for broad discovery
    state = agent_orchestrator.process_turn("Hello, please find schemes for me")

    assert state["needs_clarification"] is True
    assert state["clarification_question"] is not None
    assert len(state["missing_critical_fields"]) > 0
    assert len(state["retrieved_evidence"]) == 0  # Does not trigger RAG yet
    assert state["interaction_mode"] == "text"

def test_orchestrator_mcq_mode_provides_options(agent_orchestrator):
    # Query specifying MCQ mode
    state = agent_orchestrator.process_turn("Find schemes for me in mcq mode")

    assert state["needs_clarification"] is True
    assert state["interaction_mode"] == "mcq"
    assert state["mcq_options"] is not None
    assert len(state["mcq_options"]) > 0
    # Check options structure
    first_opt = state["mcq_options"][0]
    assert "label" in first_opt
    assert "value" in first_opt

def test_orchestrator_sufficient_info_triggers_rag_and_eligibility(agent_orchestrator):
    # Query with state and occupation
    state = agent_orchestrator.process_turn("I am a farmer from Maharashtra. What schemes can I get?")

    assert state["needs_clarification"] is False
    assert len(state["retrieved_evidence"]) > 0
    assert len(state["eligibility_recommendations"]) > 0
    assert "PM-KISAN" in state["final_response"]
    assert len(state["source_urls"]) > 0
    assert "https://pmkisan.gov.in" in state["source_urls"]

def test_multi_turn_progressive_dialogue(agent_orchestrator):
    # Turn 1: Broad discovery request -> Agent asks for missing info
    turn1_state = agent_orchestrator.process_turn("I want to apply for government welfare schemes")
    assert turn1_state["needs_clarification"] is True

    # Turn 2: User answers follow-up providing state and occupation
    turn2_state = agent_orchestrator.process_turn(
        user_input="I am a farmer living in Maharashtra, age 32",
        session_state=turn1_state
    )

    # After Turn 2, profile has accumulated age, state, and occupation
    assert turn2_state["profile"].age == 32
    assert turn2_state["profile"].state == "Maharashtra"
    assert turn2_state["profile"].occupation == "farmer"
    assert turn2_state["needs_clarification"] is False

    # Workflow completed through RAG and Eligibility
    assert len(turn2_state["eligibility_recommendations"]) > 0
    pm_kisan_eval = next(r for r in turn2_state["eligibility_recommendations"] if r.scheme_id == "pm-kisan")
    assert pm_kisan_eval.status == EligibilityStatus.ELIGIBLE
    assert "ELIGIBLE" in turn2_state["final_response"]
