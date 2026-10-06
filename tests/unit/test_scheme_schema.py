import pytest
from app.schemas.scheme_schema import SchemeRecord, SchemeEligibilityCriteria, SchemeChunk
from app.schemas.profile_schema import UserProfile

def test_scheme_record_validation():
    criteria = SchemeEligibilityCriteria(
        min_age=18,
        max_age=60,
        max_income=300000.0,
        occupations=["farmer"],
        residence_state="Maharashtra"
    )
    scheme = SchemeRecord(
        scheme_id="test-scheme",
        scheme_name="Test Farming Scheme",
        scheme_name_hi="परीक्षण कृषि योजना",
        scheme_name_mr="चाचणी कृषी योजना",
        description="A scheme to support small farmers.",
        department="Department of Agriculture",
        level="state",
        state="Maharashtra",
        beneficiary_categories=["farmer"],
        scheme_category="Agriculture",
        benefits="Direct cash transfer of ₹5,000 per year.",
        eligibility_criteria=criteria,
        documents_required=["Aadhaar", "Land Records"],
        application_procedure="Apply online via test portal.",
        official_url="https://example.gov.in",
        source_department="State Govt"
    )
    assert scheme.scheme_id == "test-scheme"
    assert scheme.eligibility_criteria.min_age == 18
    assert scheme.level == "state"
    assert scheme.state == "Maharashtra"

def test_user_profile_filtering():
    profile = UserProfile(
        age=25,
        annual_income=200000.0,
        state="Maharashtra",
        occupation="farmer",
        preferred_language="hi",
        interaction_mode="text"
    )
    filter_dict = profile.to_filter_dict()
    assert filter_dict["state"] == "Maharashtra"
    assert filter_dict["beneficiary_categories"] == "farmer"

def test_scheme_chunk_structure():
    chunk = SchemeChunk(
        chunk_id="test-chunk-01",
        scheme_id="test-scheme",
        scheme_name="Test Farming Scheme",
        section="eligibility",
        content="Age must be at least 18 years. Income must not exceed 3 lakh.",
        metadata={"state": "Maharashtra", "level": "state"}
    )
    assert chunk.section == "eligibility"
    assert chunk.metadata["state"] == "Maharashtra"
