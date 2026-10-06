import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.schemas.scheme_schema import SchemeRecord
from app.schemas.retrieval_schema import RetrievalRequest, RetrievalResponse
from app.rag.embeddings.base import DeterministicMultilingualEmbeddingService
from app.rag.vector_store.base import InMemoryVectorStore
from app.rag.bm25.base import BM25Index
from app.rag.fusion.rrf import ReciprocalRankFusion
from app.rag.reranker.base import DeterministicCrossEncoderReranker
from app.rag.retriever.hybrid_retriever import HybridRetriever
from contextlib import asynccontextmanager
from app.rag.ingestion.indexer import SchemeKnowledgeIndexer

# Initialize core RAG singleton components
embedding_service = DeterministicMultilingualEmbeddingService()
vector_store = InMemoryVectorStore()
bm25_index = BM25Index()
reranker = DeterministicCrossEncoderReranker()
retriever = HybridRetriever(
    embedding_service=embedding_service,
    vector_store=vector_store,
    bm25_index=bm25_index,
    reranker=reranker
)

# In-memory scheme repository for fast retrieval
loaded_schemes: dict[str, SchemeRecord] = {}

def load_initial_schemes():
    """Load sample schemes if available."""
    if loaded_schemes:
        return
    base_dir = Path(__file__).resolve().parent.parent.parent
    sample_file = base_dir / "data" / "processed" / "sample_schemes.json"
    if sample_file.exists():
        with open(sample_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            schemes = [SchemeRecord(**item) for item in data]
            for s in schemes:
                loaded_schemes[s.scheme_id] = s
            indexer = SchemeKnowledgeIndexer(embedding_service, vector_store, bm25_index)
            indexer.index_schemes(schemes)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_initial_schemes()
    yield

app = FastAPI(
    title="Agentic Government Scheme Recommendation API",
    description="Multilingual, profile-aware, and eligibility-guided government scheme assistant",
    version="0.1.0",
    lifespan=lifespan
)

# Enable CORS for future frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "indexed_schemes": len(loaded_schemes),
        "total_chunks": len(vector_store.chunks)
    }

@app.get("/api/schemes")
def get_schemes():
    """List loaded scheme summaries."""
    return [
        {
            "scheme_id": s.scheme_id,
            "scheme_name": s.scheme_name,
            "department": s.department,
            "level": s.level,
            "state": s.state,
            "scheme_category": s.scheme_category
        }
        for s in loaded_schemes.values()
    ]

@app.post("/api/retrieve", response_model=RetrievalResponse)
def retrieve_schemes(request: RetrievalRequest):
    """
    Execute Hybrid RAG retrieval pipeline with optional debug observability.
    """
    try:
        response = retriever.retrieve(
            query=request.query,
            profile=request.profile,
            filters=request.filters,
            top_k=request.top_k,
            debug=request.debug
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.schemas.profile_schema import UserProfile
from app.eligibility.engine import EligibilityEngine
from app.eligibility.models import EligibilityEvaluation
from pydantic import BaseModel

class EligibilityRequest(BaseModel):
    profile: UserProfile
    scheme_id: Optional[str] = None

@app.post("/api/eligibility", response_model=list[EligibilityEvaluation])
def check_eligibility(request: EligibilityRequest):
    """
    Deterministic eligibility check evaluating user profile against scheme rules.
    """
    if request.scheme_id:
        scheme = loaded_schemes.get(request.scheme_id)
        if not scheme:
            raise HTTPException(status_code=404, detail=f"Scheme '{request.scheme_id}' not found.")
        return [EligibilityEngine.evaluate(request.profile, scheme)]
    
    # Evaluate across all loaded schemes
    return EligibilityEngine.batch_evaluate(request.profile, list(loaded_schemes.values()))

