from typing import Any
import re

from app.agent.state import AgentState
from app.profile.extractor import ProfileExtractor
from app.agent.prompts.templates import CLARIFICATION_QUESTIONS, format_mcq_options
from app.rag.retriever.hybrid_retriever import HybridRetriever
from app.eligibility.service import EligibilityService
from app.schemas.scheme_schema import SchemeRecord


class AgentNodeHandlers:
    """Node handlers for the LangGraph government-scheme assistant."""

    KNOWN_SCHEMES = (
        "lakhpati didi", "pm kisan", "pm-kisan", "pmkisan", "pmay-g",
        "pmay", "ayushman bharat", "ayushman", "sanjay gandhi",
        "post matric scholarship", "post-matric scholarship", "mahadbt",
        "maha dbt", "sukanya samriddhi", "atal pension", "stand up india",
        "startup india", "mudra loan", "pm mudra", "ujjwala",
        "vishwakarma", "pm vishwakarma", "kisan samman nidhi",
        "kcc crop loan", "solar pump subsidy",
    )

    DETAIL_TERMS = (
        "details", "detail", "explain", "tell me about", "what is",
        "how does", "benefits of", "documents required", "documents needed",
        "how to apply", "application process", "official website",
        "माहिती सांगा", "योजनेची माहिती", "अधिक माहिती",
    )
    DISCOVERY_TERMS = (
        "find schemes", "find more schemes", "recommend schemes",
        "suggest schemes", "show schemes", "government schemes",
        "schemes for me", "schemes for my profile", "योजना", "योजनाएं",
        "योजनाएँ", "शोधा",
    )
    ELIGIBILITY_TERMS = (
        "am i eligible", "check eligibility", "check if i qualify",
        "eligible for", "eligibility check", "पात्रता", "पात्र आहे",
        "पात्र हूं",
    )
    SHORT_PROFILE_ANSWERS = {
        "student", "farmer", "unemployed", "self employed", "self-employed",
        "business owner", "homemaker", "housewife", "worker", "employee",
        "graduate", "undergraduate", "postgraduate", "male", "female",
        "other", "maharashtra", "gujarat", "goa", "rajasthan", "karnataka",
        "madhya pradesh", "uttar pradesh", "delhi", "bihar", "tamil nadu",
        "telangana", "kerala", "west bengal", "punjab", "haryana", "odisha",
        "assam", "jharkhand", "chhattisgarh", "himachal pradesh",
        "uttarakhand", "andhra pradesh", "jammu and kashmir",
    }

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    @classmethod
    def _classify_intent(cls, query: str, profile: Any) -> str:
        q = cls._normalize(query)
        if not q:
            return "discover_schemes"

        # Named scheme requests always go to retrieval; don't gate them on profile completeness.
        if any(name in q for name in cls.KNOWN_SCHEMES):
            return "scheme_details"
        if any(term in q for term in cls.ELIGIBILITY_TERMS):
            return "check_eligibility"
        if any(term in q for term in cls.DETAIL_TERMS):
            return "scheme_details"
        if any(term in q for term in cls.DISCOVERY_TERMS) or any(
            term in q for term in ("find", "recommend", "suggest", "योजना", "शोधा")
        ):
            return "discover_schemes"

        words = len(q.split())
        has_profile = any(
            getattr(profile, field, None)
            for field in ("occupation", "state", "annual_income", "education_level", "age", "caste_category")
        )
        if q in cls.SHORT_PROFILE_ANSWERS or (words <= 5 and (bool(re.search(r"\d", q)) or has_profile)):
            return "clarification_answer"
        return "discover_schemes"

    @classmethod
    def understand_and_extract_node(cls, state: AgentState) -> dict[str, Any]:
        query = state.get("user_query", "").strip()
        existing_profile = state.get("profile")
        updated_profile = ProfileExtractor.extract_from_text(query, existing_profile)

        lang = updated_profile.preferred_language or state.get("detected_language") or "en"
        mode = updated_profile.interaction_mode or state.get("interaction_mode") or "text"
        updated_profile.preferred_language = lang
        updated_profile.interaction_mode = mode
        intent = cls._classify_intent(query, updated_profile)

        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": query})
        return {
            "profile": updated_profile,
            "detected_language": lang,
            "interaction_mode": mode,
            "intent": intent,
            "messages": messages,
            "user_query": query,
        }

    @classmethod
    def check_sufficiency_node(cls, state: AgentState) -> dict[str, Any]:
        intent = state.get("intent", "discover_schemes")
        profile = state.get("profile")
        missing: list[str] = []

        # General recommendations need occupation and state. A short profile answer
        # should ask for the next missing targeting field rather than run unrelated retrieval.
        if intent in ("discover_schemes", "clarification_answer") and profile is not None:
            if not getattr(profile, "occupation", None):
                missing.append("occupation")
            if not getattr(profile, "state", None):
                missing.append("state")

        needs_clarification = bool(missing) and intent in ("discover_schemes", "clarification_answer")
        return {
            "needs_clarification": needs_clarification,
            "missing_critical_fields": missing,
        }

    @classmethod
    def ask_clarification_node(cls, state: AgentState) -> dict[str, Any]:
        missing = state.get("missing_critical_fields", [])
        field = missing[0] if missing else "occupation"
        lang = state.get("detected_language", "en")
        mode = state.get("interaction_mode", "text")
        question_map = CLARIFICATION_QUESTIONS.get(field, CLARIFICATION_QUESTIONS["occupation"])
        question = question_map.get(lang, question_map.get("en", "What is your occupation?"))
        options = format_mcq_options(field, lang) if mode == "mcq" else None
        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": question})
        return {
            "clarification_question": question,
            "mcq_options": options,
            "final_response": question,
            "messages": messages,
        }

    @classmethod
    def make_retrieve_rag_node(cls, retriever: HybridRetriever):
        def retrieve_rag_node(state: AgentState) -> dict[str, Any]:
            response = retriever.retrieve(
                query=state.get("user_query", ""),
                profile=state.get("profile"),
                top_k=5,
                debug=True,
            )
            urls = list(dict.fromkeys(
                item.official_url for item in response.results if item.official_url
            ))
            return {"retrieved_evidence": response.results, "source_urls": urls}
        return retrieve_rag_node

    @classmethod
    def make_evaluate_eligibility_node(cls, schemes_catalog: dict[str, SchemeRecord]):
        def evaluate_eligibility_node(state: AgentState) -> dict[str, Any]:
            recommendations = EligibilityService.evaluate_retrieved_schemes(
                profile=state.get("profile"),
                evidence=state.get("retrieved_evidence", []),
                schemes_catalog=schemes_catalog,
            )
            return {"eligibility_recommendations": recommendations}
        return evaluate_eligibility_node

    @classmethod
    def generate_explanation_node(cls, state: AgentState) -> dict[str, Any]:
        from app.llm.factory import get_llm_service

        final_text = get_llm_service().generate_explanation(
            user_query=state.get("user_query", ""),
            detected_language=state.get("detected_language", "en"),
            profile=state.get("profile"),
            recommendations=state.get("eligibility_recommendations", []),
            evidence=state.get("retrieved_evidence", []),
        )
        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": final_text})
        return {"final_response": final_text, "messages": messages}
