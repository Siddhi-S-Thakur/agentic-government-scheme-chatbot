from typing import Optional
from app.schemas.profile_schema import UserProfile
from app.eligibility.service import SchemeRecommendation
from app.schemas.retrieval_schema import RetrievedEvidence

SYSTEM_PROMPT = """You are the official conversational assistant for the Agentic Government Scheme Recommendation Platform (Government of India / State Welfare).

CRITICAL ANTI-HALLUCINATION GUIDELINES:
1. Ground Truth Eligibility: The eligibility status (ELIGIBLE, NOT_ELIGIBLE, INFORMATION_MISSING) provided to you has been computed by a deterministic rule engine. You MUST NEVER override, alter, or guess eligibility decisions.
2. Fact Strictness: Only discuss benefits, required documents, and procedures present in the retrieved context. Never fabricate financial amounts, eligibility conditions, or deadlines.
3. Official Links: Only provide official portal URLs that are explicitly supplied in the context. Never fabricate or extrapolate web links.
4. Language Alignment: Deliver the final response in the specified language:
   - 'en': Natural, clear English
   - 'hi': Fluent, respectful Hindi (हिंदी)
   - 'mr': Fluent, respectful Marathi (मराठी)
5. Structure:
   - Greet politely and summarize the findings.
   - For each scheme, clearly display its name and eligibility verdict badge: [ELIGIBLE / पात्र / पात्र], [INFORMATION MISSING / अतिरिक्त जानकारी आवश्यक / अधिक माहिती आवश्यक], or [NOT ELIGIBLE / अपात्र / अपात्र].
   - Detail matched conditions and any missing/unmet criteria.
   - Summarize key benefits and documents required.
   - Conclude with the official portal link.
"""

def build_grounded_explanation_prompt(
    user_query: str,
    detected_language: str,
    profile: UserProfile,
    recommendations: list[SchemeRecommendation],
    evidence: list[RetrievedEvidence]
) -> str:
    lang_names = {"en": "English", "hi": "Hindi (हिंदी)", "mr": "Marathi (मराठी)"}
    target_lang = lang_names.get(detected_language, "English")

    profile_items = []
    if profile.age:
        profile_items.append(f"Age: {profile.age}")
    if profile.state:
        profile_items.append(f"State: {profile.state}")
    if profile.occupation:
        profile_items.append(f"Occupation: {profile.occupation}")
    if profile.annual_income:
        profile_items.append(f"Annual Income: ₹{profile.annual_income:,.0f}")
    if profile.education_level:
        profile_items.append(f"Education: {profile.education_level}")
    if profile.caste_category:
        profile_items.append(f"Category: {profile.caste_category}")

    profile_summary = ", ".join(profile_items) if profile_items else "No profile details provided"

    # Format recommendations and rule verdicts
    recs_text_parts = []
    for idx, r in enumerate(recommendations, 1):
        matched_str = "; ".join(f"{c.condition_name}: {c.actual_value} (matched)" for c in r.matched_conditions) or "None"
        failed_str = "; ".join(c.reason for c in r.failed_conditions) or "None"
        missing_str = ", ".join(r.missing_fields) or "None"

        recs_text_parts.append(
            f"Scheme {idx}: {r.scheme_name}\n"
            f"  Scheme ID: {r.scheme_id}\n"
            f"  Deterministic Status: {r.status.value}\n"
            f"  Matched Criteria: {matched_str}\n"
            f"  Unmet Criteria: {failed_str}\n"
            f"  Missing Profile Fields: {missing_str}\n"
            f"  Official Portal URL: {r.official_url or 'N/A'}\n"
            f"  Evidence Summary: {r.top_evidence_snippet or r.summary}\n"
        )
    recommendations_text = "\n".join(recs_text_parts)

    prompt = f"""Target Output Language: {target_lang}
User Query: "{user_query}"
Citizen Profile Context: {profile_summary}

--- DETERMINISTIC ELIGIBILITY RESULTS & RETRIEVED EVIDENCE ---
{recommendations_text}
-------------------------------------------------------------

Instructions:
Generate a transparent, respectful, and explainable response in {target_lang}.
Clearly communicate why each scheme is relevant, explain which eligibility criteria are met or missing, state the benefits and required documents, and cite the official government portal URLs provided.
"""
    return prompt
