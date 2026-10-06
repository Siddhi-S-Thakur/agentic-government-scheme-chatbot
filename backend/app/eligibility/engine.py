from typing import Optional, Any
from app.schemas.profile_schema import UserProfile
from app.schemas.scheme_schema import SchemeRecord, SchemeEligibilityCriteria
from app.eligibility.models import (
    EligibilityStatus,
    ConditionResult,
    EligibilityEvaluation,
)

class EligibilityEngine:
    """
    Deterministic rule engine that checks citizen profiles against scheme criteria.
    Never relies on LLMs for the eligibility verdict.
    """

    @classmethod
    def evaluate(
        cls,
        profile: UserProfile,
        scheme: SchemeRecord | SchemeEligibilityCriteria,
        scheme_id: Optional[str] = None,
        scheme_name: Optional[str] = None,
        official_url: Optional[str] = None
    ) -> EligibilityEvaluation:
        # Extract criteria and metadata
        if isinstance(scheme, SchemeRecord):
            criteria = scheme.eligibility_criteria
            sid = scheme.scheme_id
            sname = scheme.scheme_name
            surl = scheme.official_url
        else:
            criteria = scheme
            sid = scheme_id or "unknown-scheme"
            sname = scheme_name or "Unknown Scheme"
            surl = official_url

        matched_conditions: list[ConditionResult] = []
        failed_conditions: list[ConditionResult] = []
        missing_fields: list[str] = []

        # 1. State / Residence Check
        if criteria.residence_state:
            req_state = criteria.residence_state.strip()
            if not profile.state:
                missing_fields.append("state")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="state",
                        description=f"Resident of {req_state}",
                        status="missing",
                        expected_value=req_state,
                        actual_value=None,
                        reason=f"State of residence is required (must be {req_state}) but was not provided."
                    )
                )
            elif profile.state.strip().lower() == req_state.lower():
                matched_conditions.append(
                    ConditionResult(
                        condition_name="state",
                        description=f"Resident of {req_state}",
                        status="passed",
                        expected_value=req_state,
                        actual_value=profile.state,
                        reason=f"Resident of {profile.state} matches the required state {req_state}."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="state",
                        description=f"Resident of {req_state}",
                        status="failed",
                        expected_value=req_state,
                        actual_value=profile.state,
                        reason=f"Applicant resides in {profile.state}, but scheme is restricted to {req_state}."
                    )
                )

        # 2. Age Criteria Check
        if criteria.min_age is not None or criteria.max_age is not None:
            min_a = criteria.min_age or 0
            max_a = criteria.max_age
            desc = f"Age between {min_a} and {max_a or 'no upper limit'} years"
            expected = f"[{min_a}, {max_a if max_a is not None else '∞'})"

            if profile.age is None:
                missing_fields.append("age")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="age",
                        description=desc,
                        status="missing",
                        expected_value=expected,
                        actual_value=None,
                        reason="Applicant age is required to determine eligibility."
                    )
                )
            else:
                if profile.age < min_a:
                    failed_conditions.append(
                        ConditionResult(
                            condition_name="age",
                            description=desc,
                            status="failed",
                            expected_value=expected,
                            actual_value=profile.age,
                            reason=f"Applicant age ({profile.age}) is below minimum requirement of {min_a} years."
                        )
                    )
                elif max_a is not None and profile.age > max_a:
                    failed_conditions.append(
                        ConditionResult(
                            condition_name="age",
                            description=desc,
                            status="failed",
                            expected_value=expected,
                            actual_value=profile.age,
                            reason=f"Applicant age ({profile.age}) exceeds maximum allowed limit of {max_a} years."
                        )
                    )
                else:
                    matched_conditions.append(
                        ConditionResult(
                            condition_name="age",
                            description=desc,
                            status="passed",
                            expected_value=expected,
                            actual_value=profile.age,
                            reason=f"Applicant age ({profile.age}) is within the eligible range."
                        )
                    )

        # 3. Income Criteria Check
        if criteria.max_income is not None or criteria.min_income is not None:
            max_inc = criteria.max_income
            min_inc = criteria.min_income or 0.0
            desc = f"Annual income limit: up to ₹{max_inc:,.0f}" if max_inc else f"Annual income at least ₹{min_inc:,.0f}"
            expected = f"<= ₹{max_inc:,.0f}" if max_inc else f">= ₹{min_inc:,.0f}"

            if profile.annual_income is None:
                missing_fields.append("annual_income")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="annual_income",
                        description=desc,
                        status="missing",
                        expected_value=expected,
                        actual_value=None,
                        reason="Annual household income is required to determine eligibility."
                    )
                )
            else:
                if max_inc is not None and profile.annual_income > max_inc:
                    failed_conditions.append(
                        ConditionResult(
                            condition_name="annual_income",
                            description=desc,
                            status="failed",
                            expected_value=expected,
                            actual_value=profile.annual_income,
                            reason=f"Applicant income (₹{profile.annual_income:,.0f}) exceeds the maximum threshold of ₹{max_inc:,.0f}."
                        )
                    )
                elif min_inc > 0.0 and profile.annual_income < min_inc:
                    failed_conditions.append(
                        ConditionResult(
                            condition_name="annual_income",
                            description=desc,
                            status="failed",
                            expected_value=expected,
                            actual_value=profile.annual_income,
                            reason=f"Applicant income (₹{profile.annual_income:,.0f}) is below minimum requirement of ₹{min_inc:,.0f}."
                        )
                    )
                else:
                    matched_conditions.append(
                        ConditionResult(
                            condition_name="annual_income",
                            description=desc,
                            status="passed",
                            expected_value=expected,
                            actual_value=profile.annual_income,
                            reason=f"Applicant income (₹{profile.annual_income:,.0f}) satisfies the income criteria."
                        )
                    )

        # 4. Occupation Criteria Check
        if criteria.occupations:
            allowed_occupations = [o.lower() for o in criteria.occupations]
            desc = f"Eligible occupations: {', '.join(criteria.occupations)}"

            if not profile.occupation:
                missing_fields.append("occupation")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="occupation",
                        description=desc,
                        status="missing",
                        expected_value=criteria.occupations,
                        actual_value=None,
                        reason="Applicant occupation is required for this scheme."
                    )
                )
            elif profile.occupation.lower() in allowed_occupations:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="occupation",
                        description=desc,
                        status="passed",
                        expected_value=criteria.occupations,
                        actual_value=profile.occupation,
                        reason=f"Applicant occupation ({profile.occupation}) is eligible."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="occupation",
                        description=desc,
                        status="failed",
                        expected_value=criteria.occupations,
                        actual_value=profile.occupation,
                        reason=f"Applicant occupation ({profile.occupation}) does not match required categories: {', '.join(criteria.occupations)}."
                    )
                )

        # 5. Education Criteria Check
        if criteria.education_qualifications:
            allowed_edu = [e.lower() for e in criteria.education_qualifications]
            desc = f"Eligible education levels: {', '.join(criteria.education_qualifications)}"

            if not profile.education_level:
                missing_fields.append("education_level")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="education_level",
                        description=desc,
                        status="missing",
                        expected_value=criteria.education_qualifications,
                        actual_value=None,
                        reason="Education qualification is required for this scholarship/educational scheme."
                    )
                )
            elif profile.education_level.lower() in allowed_edu:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="education_level",
                        description=desc,
                        status="passed",
                        expected_value=criteria.education_qualifications,
                        actual_value=profile.education_level,
                        reason=f"Applicant education level ({profile.education_level}) matches eligible qualifications."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="education_level",
                        description=desc,
                        status="failed",
                        expected_value=criteria.education_qualifications,
                        actual_value=profile.education_level,
                        reason=f"Applicant education ({profile.education_level}) is not in eligible qualifications: {', '.join(criteria.education_qualifications)}."
                    )
                )

        # 6. Caste / Category Criteria Check
        if criteria.caste_categories:
            allowed_castes = [c.upper() for c in criteria.caste_categories]
            desc = f"Eligible categories: {', '.join(criteria.caste_categories)}"

            if not profile.caste_category:
                missing_fields.append("caste_category")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="caste_category",
                        description=desc,
                        status="missing",
                        expected_value=criteria.caste_categories,
                        actual_value=None,
                        reason="Social category (caste) is required to evaluate eligibility for this affirmative action scheme."
                    )
                )
            elif profile.caste_category.upper() in allowed_castes or "ALL" in allowed_castes:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="caste_category",
                        description=desc,
                        status="passed",
                        expected_value=criteria.caste_categories,
                        actual_value=profile.caste_category,
                        reason=f"Applicant category ({profile.caste_category}) is eligible."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="caste_category",
                        description=desc,
                        status="failed",
                        expected_value=criteria.caste_categories,
                        actual_value=profile.caste_category,
                        reason=f"Applicant category ({profile.caste_category}) is not among eligible categories: {', '.join(criteria.caste_categories)}."
                    )
                )

        # 7. Gender Check
        if criteria.gender and criteria.gender.lower() != "all":
            req_gender = criteria.gender.lower()
            desc = f"Restricted to gender: {req_gender.capitalize()}"

            if not profile.gender:
                missing_fields.append("gender")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="gender",
                        description=desc,
                        status="missing",
                        expected_value=req_gender,
                        actual_value=None,
                        reason="Gender information is required for this gender-specific scheme."
                    )
                )
            elif profile.gender.lower() == req_gender:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="gender",
                        description=desc,
                        status="passed",
                        expected_value=req_gender,
                        actual_value=profile.gender,
                        reason=f"Applicant gender ({profile.gender}) matches scheme criteria."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="gender",
                        description=desc,
                        status="failed",
                        expected_value=req_gender,
                        actual_value=profile.gender,
                        reason=f"Applicant gender ({profile.gender}) does not match required gender ({req_gender})."
                    )
                )

        # 8. Landholding Check
        if criteria.landholding_max_acres is not None:
            max_land = criteria.landholding_max_acres
            desc = f"Landholding limit: up to {max_land} acres"

            if profile.landholding_acres is None:
                missing_fields.append("landholding_acres")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="landholding_acres",
                        description=desc,
                        status="missing",
                        expected_value=max_land,
                        actual_value=None,
                        reason="Agricultural landholding size is required."
                    )
                )
            elif profile.landholding_acres <= max_land:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="landholding_acres",
                        description=desc,
                        status="passed",
                        expected_value=max_land,
                        actual_value=profile.landholding_acres,
                        reason=f"Applicant landholding ({profile.landholding_acres} acres) is within the {max_land} acre limit."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="landholding_acres",
                        description=desc,
                        status="failed",
                        expected_value=max_land,
                        actual_value=profile.landholding_acres,
                        reason=f"Applicant landholding ({profile.landholding_acres} acres) exceeds the maximum limit of {max_land} acres."
                    )
                )

        # 9. Disability Check
        if criteria.requires_disability is True:
            desc = "Applicant must be a person with benchmark disability"
            if profile.is_differently_abled is None:
                missing_fields.append("is_differently_abled")
                failed_conditions.append(
                    ConditionResult(
                        condition_name="is_differently_abled",
                        description=desc,
                        status="missing",
                        expected_value=True,
                        actual_value=None,
                        reason="Disability status is required for this disability assistance scheme."
                    )
                )
            elif profile.is_differently_abled is True:
                matched_conditions.append(
                    ConditionResult(
                        condition_name="is_differently_abled",
                        description=desc,
                        status="passed",
                        expected_value=True,
                        actual_value=True,
                        reason="Applicant meets disability criteria."
                    )
                )
            else:
                failed_conditions.append(
                    ConditionResult(
                        condition_name="is_differently_abled",
                        description=desc,
                        status="failed",
                        expected_value=True,
                        actual_value=False,
                        reason="Scheme is specifically for differently-abled individuals."
                    )
                )

        # Deduplicate missing fields
        unique_missing_fields = list(dict.fromkeys(missing_fields))

        # Separate failed from missing in failed_conditions
        hard_failures = [c for c in failed_conditions if c.status == "failed"]
        missing_conds = [c for c in failed_conditions if c.status == "missing"]

        # Deterministic verdict logic:
        # 1. Hard failure takes absolute precedence -> NOT_ELIGIBLE
        # 2. If no hard failure, but information is missing -> INFORMATION_MISSING
        # 3. Otherwise -> ELIGIBLE
        if hard_failures:
            status = EligibilityStatus.NOT_ELIGIBLE
            summary = (
                f"Applicant is NOT ELIGIBLE for {sname} due to {len(hard_failures)} unmet condition(s): "
                + "; ".join(c.reason for c in hard_failures)
            )
        elif missing_conds:
            status = EligibilityStatus.INFORMATION_MISSING
            summary = (
                f"Eligibility for {sname} CANNOT BE DETERMINED YET because {len(unique_missing_fields)} field(s) "
                f"are missing: {', '.join(unique_missing_fields)}."
            )
        else:
            status = EligibilityStatus.ELIGIBLE
            summary = (
                f"Applicant is ELIGIBLE for {sname}. All {len(matched_conditions)} evaluated criteria are satisfied."
            )

        return EligibilityEvaluation(
            scheme_id=sid,
            scheme_name=sname,
            status=status,
            matched_conditions=matched_conditions,
            failed_conditions=hard_failures,
            missing_fields=unique_missing_fields,
            summary=summary,
            official_url=surl
        )

    @classmethod
    def batch_evaluate(
        cls,
        profile: UserProfile,
        schemes: list[SchemeRecord]
    ) -> list[EligibilityEvaluation]:
        """
        Evaluate user profile across a collection of schemes deterministically.
        """
        return [cls.evaluate(profile, s) for s in schemes]
