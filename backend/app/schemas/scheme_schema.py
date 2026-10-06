from typing import Optional, Literal, Any
from pydantic import BaseModel, Field

class SchemeEligibilityCriteria(BaseModel):
    """
    Structured rule definitions for deterministic eligibility evaluation.
    Used by the Python rule engine to compare against UserProfile.
    """
    min_age: Optional[int] = Field(default=None, ge=0, description="Minimum age requirement in years")
    max_age: Optional[int] = Field(default=None, ge=0, description="Maximum age requirement in years")
    max_income: Optional[float] = Field(default=None, ge=0.0, description="Maximum annual household income in INR")
    min_income: Optional[float] = Field(default=None, ge=0.0, description="Minimum annual household income in INR")
    occupations: list[str] = Field(default_factory=list, description="Eligible occupations (e.g., ['farmer', 'agricultural_laborer'])")
    education_qualifications: list[str] = Field(default_factory=list, description="Eligible educational qualifications")
    caste_categories: list[str] = Field(default_factory=list, description="Eligible caste/social categories (e.g., ['SC', 'ST', 'OBC'])")
    gender: Optional[Literal["male", "female", "transgender", "all"]] = Field(default="all", description="Eligible gender")
    marital_status: Optional[str] = Field(default=None, description="Eligible marital status (e.g., 'widowed')")
    residence_state: Optional[str] = Field(default=None, description="Required state of residence, or None if central")
    landholding_max_acres: Optional[float] = Field(default=None, description="Maximum agricultural landholding limit")
    requires_disability: Optional[bool] = Field(default=None, description="Whether disability status is required")
    additional_conditions: list[str] = Field(default_factory=list, description="Qualitative or textual conditions")

class SchemeRecord(BaseModel):
    """
    Primary knowledge base record for an official government scheme.
    """
    scheme_id: str = Field(..., description="Unique slug or alphanumeric identifier for the scheme")
    scheme_name: str = Field(..., description="Official scheme name in English")
    scheme_name_hi: Optional[str] = Field(default=None, description="Official scheme name in Hindi")
    scheme_name_mr: Optional[str] = Field(default=None, description="Official scheme name in Marathi")
    description: str = Field(..., description="Comprehensive description of the scheme's purpose")
    department: str = Field(..., description="Nodal government ministry or department")
    level: Literal["central", "state"] = Field(..., description="Classification: central or state government scheme")
    state: Optional[str] = Field(default=None, description="Applicable Indian state if level is 'state'")
    beneficiary_categories: list[str] = Field(default_factory=list, description="Target groups (e.g. ['farmer', 'women', 'student'])")
    scheme_category: str = Field(..., description="Sector category (e.g. 'Agriculture', 'Education', 'Social Welfare')")
    benefits: str = Field(..., description="Direct financial, material, or service benefits provided")
    eligibility_criteria: SchemeEligibilityCriteria = Field(..., description="Structured eligibility criteria")
    documents_required: list[str] = Field(default_factory=list, description="Required verification documents")
    application_procedure: str = Field(..., description="Step-by-step instructions for citizens to apply")
    official_url: str = Field(..., description="Verified official government portal URL")
    source_department: str = Field(..., description="Official source authority verifying this scheme")
    last_updated: Optional[str] = Field(default=None, description="Last update date (YYYY-MM-DD)")
    tags: list[str] = Field(default_factory=list, description="Search and categorization tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")

class SchemeChunk(BaseModel):
    """
    A chunked representation of a scheme for vector and lexical retrieval.
    Chunks are section-based to retain semantic coherence.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g., 'pm-kisan-overview-01'")
    scheme_id: str = Field(..., description="Foreign key to the parent SchemeRecord")
    scheme_name: str = Field(..., description="Parent scheme name for quick reference")
    section: str = Field(..., description="Section name: 'overview', 'eligibility', 'benefits', 'application'")
    content: str = Field(..., description="Cleaned textual content of the chunk")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata tags for filtering and debugging")
