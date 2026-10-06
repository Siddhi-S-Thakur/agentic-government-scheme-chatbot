from typing import Optional, Any
from app.agent.state import AgentState
from app.agent.graph import create_orchestrator_graph
from app.schemas.profile_schema import UserProfile
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.schemas.scheme_schema import SchemeRecord

class AgentOrchestratorService:
    """
    High-level conversational orchestrator service managing user sessions,
    graph execution, and state persistence across conversation turns.
    """
    def __init__(self, retriever: HybridRetriever, schemes_catalog: dict[str, SchemeRecord]):
        self.retriever = retriever
        self.schemes_catalog = schemes_catalog
        self.graph = create_orchestrator_graph(retriever, schemes_catalog)

    def process_turn(
        self,
        user_input: str,
        session_state: Optional[dict[str, Any]] = None
    ) -> AgentState:
        """
        Executes a single user interaction turn through the LangGraph agent.
        """
        # Initialize or recover existing state
        state_dict = dict(session_state) if session_state else {}
        existing_profile = state_dict.get("profile")
        if isinstance(existing_profile, dict):
            profile_obj = UserProfile(**existing_profile)
        elif isinstance(existing_profile, UserProfile):
            profile_obj = existing_profile
        else:
            profile_obj = UserProfile()

        input_state: AgentState = {
            "messages": state_dict.get("messages", []),
            "user_query": user_input,
            "profile": profile_obj,
            "detected_language": state_dict.get("detected_language", profile_obj.preferred_language),
            "interaction_mode": state_dict.get("interaction_mode", profile_obj.interaction_mode),
            "intent": "",
            "needs_clarification": False,
            "missing_critical_fields": [],
            "clarification_question": None,
            "mcq_options": None,
            "retrieved_evidence": [],
            "eligibility_recommendations": [],
            "final_response": "",
            "source_urls": []
        }

        # Execute through LangGraph
        result_state = self.graph.invoke(input_state)
        return result_state
