from typing import Any
from app.agent.state import AgentState
from app.profile.extractor import ProfileExtractor
from app.agent.prompts.templates import CLARIFICATION_QUESTIONS, format_mcq_options
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.eligibility.service import EligibilityService, SchemeRecommendation
from app.eligibility.models import EligibilityStatus
from app.schemas.scheme_schema import SchemeRecord

class AgentNodeHandlers:
    """
    Implements individual node functions for the LangGraph orchestrator.
    """

    @classmethod
    def understand_and_extract_node(cls, state: AgentState) -> dict[str, Any]:
        """
        Extracts progressive profile attributes from the user's latest message,
        tracks conversation history, and classifies user intent.
        """
        query = state.get("user_query", "").strip()
        existing_profile = state.get("profile")

        # Incrementally update profile using multilingual extractor
        updated_profile = ProfileExtractor.extract_from_text(query, existing_profile)

        # Detect active language and interaction mode from profile or state
        lang = updated_profile.preferred_language or state.get("detected_language") or "en"
        mode = updated_profile.interaction_mode or state.get("interaction_mode") or "text"
        updated_profile.preferred_language = lang
        updated_profile.interaction_mode = mode

        # Classify intent
        q_lower = query.lower()
        if any(term in q_lower for term in ["pm-kisan", "pmkisan", "sanjay gandhi", "mahadbt", "ayushman"]):
            intent = "scheme_details"
        elif any(term in q_lower for term in ["eligible", "eligibility", "पात्र", "पात्रता", "लायक"]):
            intent = "check_eligibility"
        elif any(term in q_lower for term in ["scheme", "schemes", "योजना", "योजनाएं", "find", "शोध", "शोधा", "मदत", "help"]):
            intent = "discover_schemes"
        elif len(query.split()) <= 4 and (updated_profile.occupation or updated_profile.state or updated_profile.annual_income):
            intent = "clarification_answer"
        else:
            intent = "discover_schemes"

        # Update messages list
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": query})

        return {
            "profile": updated_profile,
            "detected_language": lang,
            "interaction_mode": mode,
            "intent": intent,
            "messages": messages,
            "user_query": query
        }

    @classmethod
    def check_sufficiency_node(cls, state: AgentState) -> dict[str, Any]:
        """
        Determines whether sufficient profile information is available or if
        follow-up clarification is needed before retrieval.
        """
        intent = state.get("intent", "discover_schemes")
        profile = state.get("profile")
        missing_critical: list[str] = []

        # If user is asking for general discovery and we don't have basic targeting
        # (e.g., occupation or state is missing)
        if intent == "discover_schemes":
            if not profile.occupation:
                missing_critical.append("occupation")
            if not profile.state:
                missing_critical.append("state")

        # Specific scheme inquiries or targeted checks proceed directly to retrieval
        needs_clarification = len(missing_critical) > 0 and intent == "discover_schemes"

        return {
            "needs_clarification": needs_clarification,
            "missing_critical_fields": missing_critical
        }

    @classmethod
    def ask_clarification_node(cls, state: AgentState) -> dict[str, Any]:
        """
        Generates a targeted follow-up question (either text or optional MCQ)
        to gather missing profile attributes.
        """
        missing_fields = state.get("missing_critical_fields", [])
        field_to_ask = missing_fields[0] if missing_fields else "occupation"
        lang = state.get("detected_language", "en")
        mode = state.get("interaction_mode", "text")

        # Retrieve localized question
        questions_dict = CLARIFICATION_QUESTIONS.get(field_to_ask, CLARIFICATION_QUESTIONS["occupation"])
        question_text = questions_dict.get(lang, questions_dict["en"])

        mcq_opts = None
        if mode == "mcq":
            mcq_opts = format_mcq_options(field_to_ask, lang)

        # Append assistant question to message history
        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": question_text})

        return {
            "clarification_question": question_text,
            "mcq_options": mcq_opts,
            "final_response": question_text,
            "messages": messages
        }

    @classmethod
    def make_retrieve_rag_node(cls, retriever: HybridRetriever):
        """Creates retrieve_rag node bound to the retriever instance."""
        def retrieve_rag_node(state: AgentState) -> dict[str, Any]:
            query = state.get("user_query", "")
            profile = state.get("profile")

            retrieval_response = retriever.retrieve(
                query=query,
                profile=profile,
                top_k=5,
                debug=True
            )

            source_urls = list({
                e.official_url for e in retrieval_response.results if e.official_url
            })

            return {
                "retrieved_evidence": retrieval_response.results,
                "source_urls": source_urls
            }
        return retrieve_rag_node

    @classmethod
    def make_evaluate_eligibility_node(cls, schemes_catalog: dict[str, SchemeRecord]):
        """Creates evaluate_eligibility node bound to the scheme knowledge catalog."""
        def evaluate_eligibility_node(state: AgentState) -> dict[str, Any]:
            profile = state.get("profile")
            evidence = state.get("retrieved_evidence", [])

            recommendations = EligibilityService.evaluate_retrieved_schemes(
                profile=profile,
                evidence=evidence,
                schemes_catalog=schemes_catalog
            )

            return {
                "eligibility_recommendations": recommendations
            }
        return evaluate_eligibility_node

    @classmethod
    def generate_explanation_node(cls, state: AgentState) -> dict[str, Any]:
        """
        Synthesizes an explainable, source-grounded response in the user's active language
        based on retrieved evidence and deterministic eligibility evaluations using the configured LLM service.
        """
        from app.llm.factory import get_llm_service

        user_query = state.get("user_query", "")
        lang = state.get("detected_language", "en")
        profile = state.get("profile")
        recommendations = state.get("eligibility_recommendations", [])
        evidence = state.get("retrieved_evidence", [])

        llm = get_llm_service()
        final_text = llm.generate_explanation(
            user_query=user_query,
            detected_language=lang,
            profile=profile,
            recommendations=recommendations,
            evidence=evidence
        )

        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": final_text})

        return {
            "final_response": final_text,
            "messages": messages
        }
