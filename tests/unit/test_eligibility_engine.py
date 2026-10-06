import pytest
from app.schemas.profile_schema import UserProfile
from app.schemas.scheme_schema import SchemeRecord, SchemeEligibilityCriteria
from app.eligibility.engine import EligibilityEngine
from app.eligibility.models import EligibilityStatus

@pytest.fixture
def sample_schemes():
    sc_scholarship = SchemeRecord(
        scheme_id="mahadbt-post-matric",
        scheme_name="Post-Matric Scholarship for SC Students",
        description="Scholarship for SC students in Maharashtra",
        department="Social Justice Department",
        level="state",
        state="Maharashtra",
        beneficiary_categories=["student", "sc"],
        scheme_category="Education",
        benefits="100% fee waiver and stipend",
        eligibility_criteria=SchemeEligibilityCriteria(
            min_age=16,
            max_age=35,
            max_income=250000.0,
            occupations=["student"],
            education_qualifications=["10th_pass", "12th_pass", "undergraduate"],
            caste_categories=["SC"],
            residence_state="Maharashtra"
        ),
        documents_required=["Caste Certificate", "Income Certificate"],
        application_procedure="Apply online at mahadbt",
        official_url="https://mahadbt.maharashtra.gov.in",
        source_department="Govt of Maharashtra"
    )

    kisan_scheme = SchemeRecord(
        scheme_id="pm-kisan",
        scheme_name="PM-KISAN",
        description="Income support for farmers",
        department="Ministry of Agriculture",
        level="central",
        state=None,
        beneficiary_categories=["farmer"],
        scheme_category="Agriculture",
        benefits="₹6,000 per year",
        eligibility_criteria=SchemeEligibilityCriteria(
            min_age=18,
            max_age=None,
            max_income=None,
            occupations=["farmer"],
            residence_state=None
        ),
        documents_required=["Aadhaar", "Land Record"],
        application_procedure="Apply at pmkisan.gov.in",
        official_url="https://pmkisan.gov.in",
        source_department="Government of India"
    )
    return {"scholarship": sc_scholarship, "kisan": kisan_scheme}

def test_eligible_case(sample_schemes):
    profile = UserProfile(
        age=20,
        annual_income=180000.0,
        state="Maharashtra",
        occupation="student",
        education_level="12th_pass",
        caste_category="SC"
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.ELIGIBLE
    assert len(eval_res.failed_conditions) == 0
    assert len(eval_res.missing_fields) == 0
    assert len(eval_res.matched_conditions) == 6

def test_not_eligible_due_to_income_limit(sample_schemes):
    profile = UserProfile(
        age=20,
        annual_income=300000.0,  # Exceeds ₹2,50,000 limit
        state="Maharashtra",
        occupation="student",
        education_level="12th_pass",
        caste_category="SC"
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.NOT_ELIGIBLE
    failed_names = [c.condition_name for c in eval_res.failed_conditions]
    assert "annual_income" in failed_names
    assert "exceeds" in eval_res.summary.lower()

def test_not_eligible_due_to_state_mismatch(sample_schemes):
    profile = UserProfile(
        age=20,
        annual_income=150000.0,
        state="Gujarat",  # Required: Maharashtra
        occupation="student",
        education_level="12th_pass",
        caste_category="SC"
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.NOT_ELIGIBLE
    failed_names = [c.condition_name for c in eval_res.failed_conditions]
    assert "state" in failed_names

def test_not_eligible_due_to_caste_category(sample_schemes):
    profile = UserProfile(
        age=20,
        annual_income=150000.0,
        state="Maharashtra",
        occupation="student",
        education_level="12th_pass",
        caste_category="General"  # Required: SC
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.NOT_ELIGIBLE
    failed_names = [c.condition_name for c in eval_res.failed_conditions]
    assert "caste_category" in failed_names

def test_information_missing_case(sample_schemes):
    # Only state and occupation provided; missing age, income, caste, education
    profile = UserProfile(
        state="Maharashtra",
        occupation="student"
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.INFORMATION_MISSING
    assert "annual_income" in eval_res.missing_fields
    assert "caste_category" in eval_res.missing_fields
    assert "age" in eval_res.missing_fields
    assert "education_level" in eval_res.missing_fields
    assert len(eval_res.failed_conditions) == 0

def test_boundary_conditions(sample_schemes):
    # Test boundary: exactly max_income (250000.0) -> should be ELIGIBLE
    profile_boundary = UserProfile(
        age=16,  # exact min_age
        annual_income=250000.0,  # exact max_income
        state="Maharashtra",
        occupation="student",
        education_level="10th_pass",
        caste_category="SC"
    )
    eval_res = EligibilityEngine.evaluate(profile_boundary, sample_schemes["scholarship"])
    assert eval_res.status == EligibilityStatus.ELIGIBLE

    # 1 rupee over -> NOT_ELIGIBLE
    profile_over = profile_boundary.model_copy(update={"annual_income": 250001.0})
    eval_res_over = EligibilityEngine.evaluate(profile_over, sample_schemes["scholarship"])
    assert eval_res_over.status == EligibilityStatus.NOT_ELIGIBLE

    # 1 year below min_age -> NOT_ELIGIBLE
    profile_underage = profile_boundary.model_copy(update={"age": 15})
    eval_res_under = EligibilityEngine.evaluate(profile_underage, sample_schemes["scholarship"])
    assert eval_res_under.status == EligibilityStatus.NOT_ELIGIBLE

def test_failure_takes_precedence_over_missing_info(sample_schemes):
    # Occupation is wrong ("engineer"), and income/caste are missing
    profile = UserProfile(
        occupation="engineer",
        state="Maharashtra"
    )
    eval_res = EligibilityEngine.evaluate(profile, sample_schemes["scholarship"])
    # Hard failure must take precedence: the applicant is definitively NOT_ELIGIBLE
    assert eval_res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(eval_res.failed_conditions) > 0
    assert any(c.condition_name == "occupation" for c in eval_res.failed_conditions)
