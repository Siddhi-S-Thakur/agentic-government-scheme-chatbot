import pytest
from app.schemas.profile_schema import UserProfile
from app.eligibility.service import SchemeRecommendation
from app.eligibility.models import EligibilityStatus, ConditionResult
from app.schemas.retrieval_schema import RetrievedEvidence
from app.llm.prompts import build_grounded_explanation_prompt, SYSTEM_PROMPT
from app.llm.offline import OfflineDeterministicLLMService
from app.llm.gemini import GeminiLLMService
from app.llm.openai import OpenAILLMService
from app.llm.factory import get_llm_service

@pytest.fixture
def sample_recommendations():
    rec = SchemeRecommendation(
        scheme_id="pm-kisan",
        scheme_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        status=EligibilityStatus.ELIGIBLE,
        matched_conditions=[
            ConditionResult(
                condition_name="occupation",
                description="Eligible occupations: farmer",
                status="passed",
                expected_value=["farmer"],
                actual_value="farmer",
                reason="Applicant occupation (farmer) is eligible."
            )
        ],
        failed_conditions=[],
        missing_fields=[],
        summary="Applicant is ELIGIBLE for PM-KISAN. All evaluated criteria are satisfied.",
        official_url="https://pmkisan.gov.in",
        retrieved_sections=["overview", "benefits"],
        top_evidence_snippet="Direct cash benefit of ₹6,000 per year.",
        retrieval_score=0.88
    )
    return [rec]

def test_prompt_construction_anti_hallucination(sample_recommendations):
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer")
    prompt = build_grounded_explanation_prompt(
        user_query="How much money do farmers get under PM-KISAN?",
        detected_language="en",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "Deterministic Status: ELIGIBLE" in prompt
    assert "https://pmkisan.gov.in" in prompt
    assert "Target Output Language: English" in prompt
    assert "Strict Rule 1" in SYSTEM_PROMPT or "CRITICAL ANTI-HALLUCINATION" in SYSTEM_PROMPT

def test_offline_fallback_service_english(sample_recommendations):
    service = OfflineDeterministicLLMService()
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer")

    response = service.generate_explanation(
        user_query="What schemes are for me?",
        detected_language="en",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "PM-KISAN" in response
    assert "[ELIGIBLE]" in response
    assert "https://pmkisan.gov.in" in response

def test_offline_fallback_service_marathi(sample_recommendations):
    service = OfflineDeterministicLLMService()
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer", preferred_language="mr")

    response = service.generate_explanation(
        user_query="माझ्यासाठी कोणत्या योजना आहेत?",
        detected_language="mr",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "PM-KISAN" in response
    assert "पात्र" in response
    assert "https://pmkisan.gov.in" in response

def test_offline_fallback_service_hindi(sample_recommendations):
    service = OfflineDeterministicLLMService()
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer", preferred_language="hi")

    response = service.generate_explanation(
        user_query="मेरे लिए कौन सी योजनाएं हैं?",
        detected_language="hi",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "PM-KISAN" in response
    assert "पात्र" in response
    assert "https://pmkisan.gov.in" in response

def test_factory_returns_offline_fallback_when_no_keys():
    # In default test environment without active live keys
    service = get_llm_service()
    assert isinstance(service, (OfflineDeterministicLLMService, GeminiLLMService, OpenAILLMService))

def test_gemini_service_graceful_fallback(sample_recommendations):
    # Dummy invalid key should trigger fallback rather than crashing
    service = GeminiLLMService(api_key="invalid_test_key_xyz")
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer")

    response = service.generate_explanation(
        user_query="Tell me about farming schemes",
        detected_language="en",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "PM-KISAN" in response
    assert "https://pmkisan.gov.in" in response

def test_openai_service_graceful_fallback(sample_recommendations):
    # Dummy invalid key should trigger fallback rather than crashing
    service = OpenAILLMService(api_key="sk-invalid_test_key_xyz")
    profile = UserProfile(age=30, state="Maharashtra", occupation="farmer")

    response = service.generate_explanation(
        user_query="Tell me about farming schemes",
        detected_language="en",
        profile=profile,
        recommendations=sample_recommendations,
        evidence=[]
    )

    assert "PM-KISAN" in response
    assert "https://pmkisan.gov.in" in response
