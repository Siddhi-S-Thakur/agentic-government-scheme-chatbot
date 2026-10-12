
from typing import Any, Optional

from app.schemas.profile_schema import UserProfile
from app.schemas.scheme_schema import SchemeRecord, SchemeEligibilityCriteria
from app.eligibility.models import (
    EligibilityStatus,
    ConditionResult,
    EligibilityEvaluation,
)


class EligibilityEngine:
    """
    Deterministic eligibility evaluation.

    This engine evaluates configured, structured criteria only.
    Passing these criteria is not an official eligibility approval.
    """

    @staticmethod
    def _normalise(value: Any) -> str:
        """Normalize values for conservative text comparisons."""
        if value is None:
            return ""
        return " ".join(
            str(value).strip().lower().replace("_", " ").split()
        ).strip(" .,-")

    @classmethod
    def _matches_category(
        cls,
        actual: Any,
        allowed_values: list[str],
    ) -> bool:
        """Match exact labels and a small set of common equivalent labels."""
        actual_value = cls._normalise(actual)
        if not actual_value:
            return False

        alias_groups = [
            {
                "student",
                "college student",
                "undergraduate student",
                "university student",
            },
            {"undergraduate", "undergraduate student", "college student"},
            {"farmer", "agriculturist", "agriculturalist"},
            {"self employed", "self-employed"},
            {
                "post graduate",
                "postgraduate",
                "post graduate student",
                "postgraduate student",
            },
            {"secondary", "secondary school"},
            {
                "higher secondary",
                "senior secondary",
                "12th",
                "class 12",
                "12th pass",
            },
        ]

        for allowed in allowed_values:
            allowed_value = cls._normalise(allowed)

            if actual_value == allowed_value:
                return True

            for group in alias_groups:
                normalized_group = {cls._normalise(item) for item in group}
                if (
                    actual_value in normalized_group
                    and allowed_value in normalized_group
                ):
                    return True

        return False

    @staticmethod
    def _condition(
        name: str,
        description: str,
        status: str,
        expected: Any,
        actual: Any,
        reason: str,
    ) -> ConditionResult:
        """Build a condition result using the existing response model."""
        return ConditionResult(
            condition_name=name,
            description=description,
            status=status,
            expected_value=expected,
            actual_value=actual,
            reason=reason,
        )

    @classmethod
    def evaluate(
        cls,
        profile: UserProfile,
        scheme: SchemeRecord | SchemeEligibilityCriteria,
        scheme_id: Optional[str] = None,
        scheme_name: Optional[str] = None,
        official_url: Optional[str] = None,
    ) -> EligibilityEvaluation:
        """Evaluate the profile against the scheme's configured criteria."""

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

        passed: list[ConditionResult] = []
        unresolved: list[ConditionResult] = []
        hard_failures: list[ConditionResult] = []
        missing_fields: list[str] = []
        evaluated_count = 0

        def check(
            name: str,
            description: str,
            expected: Any,
            actual: Any,
            is_missing: bool,
            is_match: bool,
            pass_reason: str,
            fail_reason: str,
        ) -> None:
            nonlocal evaluated_count
            evaluated_count += 1

            if is_missing:
                missing_fields.append(name)
                unresolved.append(
                    cls._condition(
                        name,
                        description,
                        "missing",
                        expected,
                        None,
                        f"Cannot evaluate {name}: the required information was not provided.",
                    )
                )
            elif is_match:
                passed.append(
                    cls._condition(
                        name,
                        description,
                        "passed",
                        expected,
                        actual,
                        pass_reason,
                    )
                )
            else:
                hard_failures.append(
                    cls._condition(
                        name,
                        description,
                        "failed",
                        expected,
                        actual,
                        fail_reason,
                    )
                )

        # 1. Residence state
        if criteria.residence_state:
            actual = getattr(profile, "state", None)
            expected = criteria.residence_state.strip()
            state_matches = (
                self_value == expected.lower()
                if False
                else cls._normalise(actual) == cls._normalise(expected)
            )
            check(
                "state",
                f"Resident of {expected}",
                expected,
                actual,
                not actual,
                state_matches,
                f"Applicant's state matches {expected}.",
                f"Applicant's state ({actual}) does not match {expected}.",
            )

        # 2. Age
        if criteria.min_age is not None or criteria.max_age is not None:
            age = getattr(profile, "age", None)
            minimum = criteria.min_age
            maximum = criteria.max_age

            valid = (
                age is not None
                and (minimum is None or age >= minimum)
                and (maximum is None or age <= maximum)
            )

            check(
                "age",
                (
                    f"Age: {minimum if minimum is not None else 'no minimum'} "
                    f"to {maximum if maximum is not None else 'no maximum'} years"
                ),
                {"min": minimum, "max": maximum},
                age,
                age is None,
                valid,
                f"Applicant's age ({age}) satisfies the configured age limits.",
                f"Applicant's age ({age}) is outside the configured age limits.",
            )

        # 3. Annual income
        if criteria.min_income is not None or criteria.max_income is not None:
            income = getattr(profile, "annual_income", None)
            minimum = criteria.min_income
            maximum = criteria.max_income

            valid = (
                income is not None
                and (minimum is None or income >= minimum)
                and (maximum is None or income <= maximum)
            )

            fail_reason = (
                f"Applicant income ({income}) exceeds maximum eligible limit of {maximum}."
                if maximum is not None and income is not None and income > maximum
                else f"Applicant income ({income}) is below minimum eligible limit of {minimum}."
                if minimum is not None and income is not None and income < minimum
                else "Reported annual income is outside the configured limits."
            )

            check(
                "annual_income",
                "Annual household income requirement",
                {"min": minimum, "max": maximum},
                income,
                income is None,
                valid,
                "Reported annual income satisfies the configured limits.",
                fail_reason,
            )

        # 4. Occupation
        if criteria.occupations:
            occupation = getattr(profile, "occupation", None)
            valid = bool(occupation) and cls._matches_category(
                occupation,
                criteria.occupations,
            )

            check(
                "occupation",
                f"Eligible occupations: {', '.join(criteria.occupations)}",
                criteria.occupations,
                occupation,
                not occupation,
                valid,
                f"Occupation ({occupation}) matches a configured category.",
                f"Occupation ({occupation}) does not match the configured categories.",
            )

        # 5. Education
        if criteria.education_qualifications:
            education = getattr(profile, "education_level", None)
            valid = bool(education) and cls._matches_category(
                education,
                criteria.education_qualifications,
            )

            check(
                "education_level",
                f"Eligible education: {', '.join(criteria.education_qualifications)}",
                criteria.education_qualifications,
                education,
                not education,
                valid,
                f"Education level ({education}) matches a configured category.",
                f"Education level ({education}) does not match the configured categories.",
            )

        # 6. Caste / social category
        if criteria.caste_categories:
            caste = getattr(profile, "caste_category", None)
            valid = bool(caste) and (
                cls._normalise(caste) == "all"
                or any(
                    cls._normalise(caste) == cls._normalise(item)
                    or cls._normalise(item) == "all"
                    for item in criteria.caste_categories
                )
            )

            check(
                "caste_category",
                f"Eligible categories: {', '.join(criteria.caste_categories)}",
                criteria.caste_categories,
                caste,
                not caste,
                valid,
                f"Social category ({caste}) matches the configured criteria.",
                f"Social category ({caste}) does not match the configured criteria.",
            )

        # 7. Gender
        if criteria.gender and cls._normalise(criteria.gender) != "all":
            gender = getattr(profile, "gender", None)
            valid = bool(gender) and (
                cls._normalise(gender) == cls._normalise(criteria.gender)
            )

            check(
                "gender",
                f"Required gender: {criteria.gender}",
                criteria.gender,
                gender,
                not gender,
                valid,
                "Gender matches the configured criterion.",
                "Gender does not match the configured criterion.",
            )

        # 8. Landholding
        if criteria.landholding_max_acres is not None:
            land = getattr(profile, "landholding_acres", None)
            maximum = criteria.landholding_max_acres

            check(
                "landholding_acres",
                f"Landholding limit: up to {maximum} acres",
                maximum,
                land,
                land is None,
                land is not None and land <= maximum,
                "Reported landholding is within the configured limit.",
                "Reported landholding exceeds the configured limit.",
            )

        # 9. Disability
        if criteria.requires_disability is True:
            disability = getattr(profile, "is_differently_abled", None)

            check(
                "is_differently_abled",
                "Disability status requirement",
                True,
                disability,
                disability is None,
                disability is True,
                "Disability criterion is satisfied.",
                "The configured disability criterion is not satisfied.",
            )

        # 10. Marital status
        if criteria.marital_status:
            marital_status = getattr(profile, "marital_status", None)
            expected = criteria.marital_status
            valid = (
                bool(marital_status)
                and cls._normalise(marital_status) == cls._normalise(expected)
            )

            check(
                "marital_status",
                f"Required marital status: {expected}",
                expected,
                marital_status,
                not marital_status,
                valid,
                "Marital status matches the configured criterion.",
                "Marital status does not match the configured criterion.",
            )

        # Additional free-text rules are informational scheme notes.
        # They do not block deterministic eligibility when all configured criteria are met.
        additional_conditions = criteria.additional_conditions or []

        # Never confirm eligibility when no structured criteria are evaluable.
        if evaluated_count == 0:
            missing_fields.append("eligibility_criteria")
            unresolved.append(
                cls._condition(
                    "eligibility_criteria",
                    "Scheme eligibility criteria",
                    "missing",
                    "At least one meaningful configured criterion",
                    None,
                    "No evaluable eligibility criteria are configured for this scheme.",
                )
            )

        missing_fields = list(dict.fromkeys(missing_fields))

        if hard_failures:
            status = EligibilityStatus.NOT_ELIGIBLE
            summary = (
                f"Applicant does not meet the configured criteria for {sname}: "
                + "; ".join(condition.reason for condition in hard_failures)
            )
        elif unresolved:
            status = EligibilityStatus.INFORMATION_MISSING
            summary = (
                f"Eligibility for {sname} cannot be confirmed yet. "
                "Further information or verification is required: "
                + ", ".join(missing_fields)
                + "."
            )
        else:
            status = EligibilityStatus.ELIGIBLE
            summary = (
                f"Applicant meets all {len(passed)} configured criteria for {sname}. "
                "This is a preliminary assessment, not an official eligibility decision."
            )

        return EligibilityEvaluation(
            scheme_id=sid,
            scheme_name=sname,
            status=status,
            matched_conditions=passed,
            failed_conditions=hard_failures,
            missing_fields=missing_fields,
            summary=summary,
            official_url=surl,
        )

    @classmethod
    def batch_evaluate(
        cls,
        profile: UserProfile,
        schemes: list[SchemeRecord],
    ) -> list[EligibilityEvaluation]:
        """Evaluate a profile against a collection of schemes."""
        return [cls.evaluate(profile, scheme) for scheme in schemes]
