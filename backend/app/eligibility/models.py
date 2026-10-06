from enum import Enum
from typing import Optional, Any, Literal
from pydantic import BaseModel, Field

class EligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    INFORMATION_MISSING = "INFORMATION_MISSING"

class ConditionResult(BaseModel):
    """
    Evaluation result for an individual eligibility rule condition.
    """
    condition_name: str = Field(..., description="Field or criteria name, e.g. 'age', 'income', 'residence_state'")
    description: str = Field(..., description="Human-readable description of the condition")
    status: Literal["passed", "failed", "missing"] = Field(..., description="Outcome of condition check")
    expected_value: Any = Field(..., description="Criterion requirement from the scheme")
    actual_value: Any = Field(default=None, description="Citizen's actual value from profile")
    reason: str = Field(..., description="Deterministic explanation for the pass/fail/missing decision")

class EligibilityEvaluation(BaseModel):
    """
    Structured outcome of deterministic eligibility checking for a specific scheme.
    Ground truth for explainable recommendations. LLMs must NOT override this decision.
    """
    scheme_id: str = Field(..., description="Unique scheme identifier")
    scheme_name: str = Field(..., description="Official scheme name")
    status: EligibilityStatus = Field(..., description="Determined status: ELIGIBLE, NOT_ELIGIBLE, or INFORMATION_MISSING")
    matched_conditions: list[ConditionResult] = Field(default_factory=list, description="Conditions the citizen meets")
    failed_conditions: list[ConditionResult] = Field(default_factory=list, description="Conditions the citizen fails to meet")
    missing_fields: list[str] = Field(default_factory=list, description="Specific profile fields required to determine eligibility")
    summary: str = Field(..., description="Deterministic natural summary of eligibility result")
    official_url: Optional[str] = Field(default=None, description="Verified portal link for the scheme")
