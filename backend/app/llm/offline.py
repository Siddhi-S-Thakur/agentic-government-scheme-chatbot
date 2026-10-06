from typing import Optional
from app.llm.base import BaseLLMService
from app.schemas.profile_schema import UserProfile
from app.eligibility.service import SchemeRecommendation
from app.schemas.retrieval_schema import RetrievedEvidence
from app.eligibility.models import EligibilityStatus

class OfflineDeterministicLLMService(BaseLLMService):
    """
    Deterministic offline explanation generator.
    Serves as an offline fallback when API keys are not supplied or external network calls fail.
    Renders structured, grounded explanations in English, Hindi, or Marathi strictly
    from retrieved evidence and deterministic eligibility verdicts.
    """

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[Offline Fallback Response]: Processed prompt of {len(prompt)} characters."

    def generate_explanation(
        self,
        user_query: str,
        detected_language: str,
        profile: UserProfile,
        recommendations: list[SchemeRecommendation],
        evidence: list[RetrievedEvidence]
    ) -> str:
        if not recommendations:
            if detected_language == "hi":
                return "मुझे आपके मानदंडों से मेल खाने वाली कोई सरकारी योजना नहीं मिली। कृपया अपने राज्य या व्यवसाय का विवरण दें।"
            elif detected_language == "mr":
                return "मला तुमच्या निकषांशी जुळणारी कोणतीही सरकारी योजना सापडली नाही. कृपया तुमचे राज्य किंवा व्यवसाय स्पष्ट करा."
            else:
                return "I could not find any government schemes matching your profile criteria. Please provide additional details like your state or occupation."

        lines = []
        if detected_language == "hi":
            lines.append(f"### आपके लिए सरकारी योजनाएं ({len(recommendations)}):\n")
        elif detected_language == "mr":
            lines.append(f"### तुमच्यासाठी सरकारी योजना ({len(recommendations)}):\n")
        else:
            lines.append(f"### Government Schemes for You ({len(recommendations)}):\n")

        for idx, rec in enumerate(recommendations, 1):
            # Badge localization
            if rec.status == EligibilityStatus.ELIGIBLE:
                badge = "[ELIGIBLE / पात्र]" if detected_language in ("hi", "mr") else "[ELIGIBLE]"
            elif rec.status == EligibilityStatus.INFORMATION_MISSING:
                badge = "[INFORMATION MISSING / माहिती आवश्यक]" if detected_language in ("hi", "mr") else "[INFORMATION MISSING]"
            else:
                badge = "[NOT ELIGIBLE / अपात्र]" if detected_language in ("hi", "mr") else "[NOT ELIGIBLE]"

            lines.append(f"#### {idx}. {rec.scheme_name} **{badge}**")
            lines.append(f"- **Summary**: {rec.summary}")

            # Matched criteria
            if rec.matched_conditions:
                matched_str = ", ".join(f"{c.condition_name} ({c.actual_value})" for c in rec.matched_conditions)
                prefix = "- **पूर्ण झालेले निकष**" if detected_language == "mr" else ("- **सत्यापित मानदंड**" if detected_language == "hi" else "- **Matched Criteria**")
                lines.append(f"{prefix}: {matched_str}")

            # Failed criteria
            if rec.failed_conditions:
                failed_str = "; ".join(c.reason for c in rec.failed_conditions)
                prefix = "- **अपूर्ण निकष**" if detected_language == "mr" else ("- **अपात्रता का कारण**" if detected_language == "hi" else "- **Unmet Criteria**")
                lines.append(f"{prefix}: {failed_str}")

            # Missing fields
            if rec.missing_fields:
                missing_str = ", ".join(rec.missing_fields)
                prefix = "- **पात्रता निश्चित करण्यासाठी आवश्यक माहिती**" if detected_language == "mr" else ("- **पात्रता जांचने के लिए आवश्यक जानकारी**" if detected_language == "hi" else "- **Information Needed to Confirm Eligibility**")
                lines.append(f"{prefix}: {missing_str}")

            # Official Link
            if rec.official_url:
                prefix = "- **अधिकृत संकेतस्थळ (Official Portal)**" if detected_language in ("hi", "mr") else "- **Official Portal**"
                lines.append(f"{prefix}: [{rec.official_url}]({rec.official_url})")

            lines.append("")

        return "\n".join(lines).strip()
