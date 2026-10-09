import json
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
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
    # Initialize database tables (creates users, profiles, conversations tables)
    init_db()
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

from app.agent.service import AgentOrchestratorService

agent_service = AgentOrchestratorService(retriever, loaded_schemes)
from app.models.repositories import UserRepository, ConversationRepository, ProfileRepository

class ChatRequest(BaseModel):
    message: str
    session_state: Optional[dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    detected_language: str
    interaction_mode: str
    needs_clarification: bool
    mcq_options: Optional[list[dict[str, Any]]] = None
    profile: dict[str, Any]
    recommendations: list[dict[str, Any]]
    source_urls: list[str]
    session_state: dict[str, Any]

ChatRequest.model_rebuild()
ChatResponse.model_rebuild()

@app.post("/api/chat", response_model=ChatResponse)
def chat_turn(request: ChatRequest):
    """
    Execute a conversational turn through the LangGraph AI orchestrator agent.
    Automatically persists messages and extracted profile context to the database if a registered session_id is provided.
    Guest users (no session_id or guest-prefixed session_id) can chat freely without persistence.
    """
    try:
        session_id = request.session_id
        session_state = dict(request.session_state) if request.session_state else {}

        # Determine if this is a registered user session (not a guest)
        is_registered_session = session_id and not session_id.startswith("guest-")

        # If registered session, recover stored profile from DB if not fully provided in incoming state
        if is_registered_session:
            stored_profile = ProfileRepository.get_profile(session_id)
            if stored_profile:
                incoming_profile = session_state.get("profile")
                if not incoming_profile:
                    session_state["profile"] = stored_profile.model_dump()
                elif isinstance(incoming_profile, dict):
                    # Merge stored profile with non-empty incoming profile attributes
                    merged = stored_profile.model_dump()
                    for k, v in incoming_profile.items():
                        if v is not None and v != "":
                            merged[k] = v
                    session_state["profile"] = merged

            # Persist user query to database
            ConversationRepository.save_message(
                session_id=session_id,
                role="user",
                content=request.message
            )

        updated_state = agent_service.process_turn(
            user_input=request.message,
            session_state=session_state
        )

        # Serialize recommendations and profile
        profile_dict = updated_state["profile"].model_dump()
        recs_list = [r.model_dump() for r in updated_state.get("eligibility_recommendations", [])]
        final_response_text = updated_state.get("final_response", "")

        # Persist assistant reply and updated profile to database if registered session
        if is_registered_session:
            ConversationRepository.save_message(
                session_id=session_id,
                role="assistant",
                content=final_response_text
            )
            ProfileRepository.upsert_profile(
                session_id=session_id,
                profile=updated_state["profile"]
            )

        # Prepare state for next turn
        serializable_state = {
            "messages": updated_state.get("messages", []),
            "profile": profile_dict,
            "detected_language": updated_state.get("detected_language", "en"),
            "interaction_mode": updated_state.get("interaction_mode", "text")
        }

        return ChatResponse(
            response=final_response_text,
            detected_language=updated_state.get("detected_language", "en"),
            interaction_mode=updated_state.get("interaction_mode", "text"),
            needs_clarification=updated_state.get("needs_clarification", False),
            mcq_options=updated_state.get("mcq_options"),
            profile=profile_dict,
            recommendations=recs_list,
            source_urls=updated_state.get("source_urls", []),
            session_state=serializable_state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# AUTH ENDPOINTS — Registration, Login, Session Validation
# ═══════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    full_name: str
    password: str
    email: Optional[str] = None
    # Optional citizen profile fields provided during registration
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    annual_income: Optional[float] = None
    caste_category: Optional[str] = None
    landholding_acres: Optional[float] = None
    preferred_language: Optional[str] = "en"

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class AuthResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    session_id: str
    profile: Optional[dict[str, Any]] = None

@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(request: RegisterRequest):
    """Register a new citizen account and store initial eligibility profile."""
    try:
        user = UserRepository.create_user(
            username=request.username,
            full_name=request.full_name,
            password=request.password,
            email=request.email
        )

        # Store profile in database associated with this citizen's session_id
        initial_profile = UserProfile(
            age=request.age,
            gender=request.gender,
            occupation=request.occupation,
            state=request.state,
            district=request.district,
            annual_income=request.annual_income,
            caste_category=request.caste_category,
            landholding_acres=request.landholding_acres,
            preferred_language=request.preferred_language or "en"
        )
        saved_profile = ProfileRepository.upsert_profile(
            session_id=user.session_id,
            profile=initial_profile
        )

        return AuthResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            session_id=user.session_id,
            profile=saved_profile.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(request: LoginRequest):
    """Authenticate a citizen and return user and saved profile details."""
    user = UserRepository.authenticate(
        username_or_email=request.username_or_email,
        password=request.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")

    profile = ProfileRepository.get_profile(user.session_id)
    profile_dict = profile.model_dump() if profile else {}

    return AuthResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        session_id=user.session_id,
        profile=profile_dict
    )

@app.get("/api/auth/me", response_model=AuthResponse)
def get_current_user(session_id: str):
    """Validate a session and return citizen info and saved profile."""
    user = UserRepository.get_by_session_id(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    profile = ProfileRepository.get_profile(session_id)
    profile_dict = profile.model_dump() if profile else {}

    return AuthResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        session_id=user.session_id,
        profile=profile_dict
    )


# ═══════════════════════════════════════════════════════════════
# CITIZEN PROFILE CRUD ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/profile/{session_id}", response_model=dict[str, Any])
def get_user_profile(session_id: str):
    """Retrieve the saved citizen profile for a session."""
    if session_id.startswith("guest-"):
        return {}
    user = UserRepository.get_by_session_id(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    profile = ProfileRepository.get_profile(session_id)
    return profile.model_dump() if profile else {}

@app.put("/api/profile/{session_id}", response_model=dict[str, Any])
def update_user_profile(session_id: str, profile_data: dict[str, Any]):
    """Update or save citizen eligibility profile attributes for a session."""
    user = UserRepository.get_by_session_id(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    profile_obj = UserProfile(**profile_data)
    updated = ProfileRepository.upsert_profile(session_id=session_id, profile=profile_obj)
    return updated.model_dump()


# ═══════════════════════════════════════════════════════════════
# CONVERSATION HISTORY & SYNC ENDPOINTS
# ═══════════════════════════════════════════════════════════════

class SyncMessageItem(BaseModel):
    role: str
    content: str
    metadata: Optional[dict[str, Any]] = None

class SyncMessagesRequest(BaseModel):
    session_id: str
    messages: list[SyncMessageItem]

@app.get("/api/conversations/{session_id}")
def get_conversation_history(session_id: str, limit: int = 50):
    """Retrieve past conversation messages for a session."""
    if session_id.startswith("guest-"):
        return []
    user = UserRepository.get_by_session_id(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session.")
    return ConversationRepository.get_history(session_id=session_id, limit=limit)

@app.delete("/api/conversations/{session_id}")
def clear_conversation_history(session_id: str):
    """Clear past conversation messages for a session."""
    if session_id.startswith("guest-"):
        return {"status": "cleared", "session_id": session_id}
    user = UserRepository.get_by_session_id(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session.")
    ConversationRepository.clear_history(session_id=session_id)
    return {"status": "cleared", "session_id": session_id}

@app.post("/api/conversations/sync")
def sync_messages(request: SyncMessagesRequest):
    """
    Sync in-flight conversation messages (e.g. from guest mode) to a registered user account.
    """
    user = UserRepository.get_by_session_id(request.session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session.")

    saved_count = 0
    for item in request.messages:
        if item.role in ("user", "assistant") and item.content.strip():
            ConversationRepository.save_message(
                session_id=request.session_id,
                role=item.role,
                content=item.content,
                metadata=item.metadata
            )
            saved_count += 1
    return {"status": "synced", "count": saved_count}
