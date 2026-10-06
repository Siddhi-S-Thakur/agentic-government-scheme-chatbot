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

        # Detect active language from profile
        lang = updated_profile.preferred_language
        mode = updated_profile.interaction_mode

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
        based on retrieved evidence and deterministic eligibility evaluations.
        """
        lang = state.get("detected_language", "en")
        recommendations = state.get("eligibility_recommendations", [])
        urls = state.get("source_urls", [])

        if not recommendations:
            if lang == "hi":
                resp = "मुझे आपके मानदंडों से मेल खाने वाली कोई सरकारी योजना नहीं मिली। कृपया अधिक विवरण प्रदान करें।"
            elif lang == "mr":
                resp = "मला तुमच्या निकषांशी जुळणारी कोणतीही सरकारी योजना सापडली नाही. कृपया अधिक माहिती द्या."
            else:
                resp = "I could not find any government schemes matching your criteria. Please provide more details."
            return {"final_response": resp}

        # Build explainable response
        response_lines = []
        if lang == "hi":
            response_lines.append(f"### आपके लिए अनुशंसित सरकारी योजनाएं ({len(recommendations)}):\n")
        elif lang == "mr":
            response_lines.append(f"### तुमच्यासाठी शिफारस केलेल्या सरकारी योजना ({len(recommendations)}):\n")
        else:
            response_lines.append(f"### Recommended Government Schemes for You ({len(recommendations)}):\n")

        for idx, rec in enumerate(recommendations, 1):
            status_badge = f"**[{rec.status.value}]**"
            response_lines.append(f"#### {idx}. {rec.scheme_name} {status_badge}")
            response_lines.append(f"- **Summary**: {rec.summary}")

            # Explain matched criteria
            if rec.matched_conditions:
                matched_str = ", ".join(f"{c.condition_name} ({c.actual_value})" for c in rec.matched_conditions)
                response_lines.append(f"- **Matched Criteria**: {matched_str}")

            # Explain unmet criteria
            if rec.failed_conditions:
                failed_str = "; ".join(c.reason for c in rec.failed_conditions)
                response_lines.append(f"- **Unmet Criteria**: {failed_str}")

            # Explain missing info
            if rec.missing_fields:
                missing_str = ", ".join(rec.missing_fields)
                if lang == "hi":
                    response_lines.append(f"- **अतिरिक्त जानकारी आवश्यक**: {missing_str}")
                elif lang == "mr":
                    response_lines.append(f"- **अधिक माहिती आवश्यक**: {missing_str}")
                else:
                    response_lines.append(f"- **Information Needed to Confirm**: {missing_str}")

            # Add source link
            if rec.official_url:
                response_lines.append(f"- **Official Portal**: [{rec.official_url}]({rec.official_url})")

            response_lines.append("")

        final_text = "\n".join(response_lines).strip()

        messages = list(state.get("messages", []))
        messages.append({"role": "assistant", "content": final_text})

        return {
            "final_response": final_text,
            "messages": messages
        }
