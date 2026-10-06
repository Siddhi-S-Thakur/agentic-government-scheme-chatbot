from typing import TypedDict, Optional, Literal, Any
from app.schemas.profile_schema import UserProfile
from app.schemas.retrieval_schema import RetrievedEvidence
from app.eligibility.service import SchemeRecommendation

class MCQOption(TypedDict):
    id: str
    label_en: str
    label_hi: str
    label_mr: str
    field_name: str
    value: Any

class AgentState(TypedDict):
    """
    Unified state managed by the LangGraph orchestrator.
    Maintains progressive profile, conversation turns, retrieval evidence,
    and eligibility evaluation throughout the lifecycle of user requests.
    """
    # Conversation tracking
    messages: list[dict[str, str]]
    user_query: str
    
    # Active preferences & profile
    profile: UserProfile
    detected_language: Literal["en", "hi", "mr"]
    interaction_mode: Literal["text", "mcq"]
    
    # Intent & Routing
    intent: str
    needs_clarification: bool
    missing_critical_fields: list[str]
    
    # Clarification payload (if information is missing)
    clarification_question: Optional[str]
    mcq_options: Optional[list[dict[str, Any]]]
    
    # Retrieval & Eligibility evidence
    retrieved_evidence: list[RetrievedEvidence]
    eligibility_recommendations: list[SchemeRecommendation]
    
    # Output
    final_response: str
    source_urls: list[str]
