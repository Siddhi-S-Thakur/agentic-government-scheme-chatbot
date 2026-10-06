from typing import Optional, Literal
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    """
    Language-neutral representation of citizen profile data.
    Field values are stored in canonical English strings/numbers internally
    to ensure deterministic rule checking and language-agnostic retrieval.
    """
    age: Optional[int] = Field(default=None, ge=0, le=125, description="Age in years")
    annual_income: Optional[float] = Field(default=None, ge=0.0, description="Annual household income in INR")
    state: Optional[str] = Field(default=None, description="State of residence (e.g., 'Maharashtra')")
    district: Optional[str] = Field(default=None, description="District of residence")
    occupation: Optional[str] = Field(default=None, description="Occupation (e.g., 'farmer', 'student', 'unemployed')")
    education_level: Optional[str] = Field(default=None, description="Education level (e.g., '10th_pass', 'graduate')")
    caste_category: Optional[str] = Field(default=None, description="Category (e.g., 'General', 'SC', 'ST', 'OBC', 'EWS')")
    gender: Optional[Literal["male", "female", "transgender", "other"]] = Field(default=None, description="Gender")
    marital_status: Optional[str] = Field(default=None, description="Marital status (e.g., 'single', 'married', 'widowed', 'divorced')")
    is_differently_abled: Optional[bool] = Field(default=None, description="Disability status")
    landholding_acres: Optional[float] = Field(default=None, ge=0.0, description="Agricultural land holding in acres")
    
    # Preference metadata
    preferred_language: Literal["en", "hi", "mr"] = Field(default="en", description="Preferred interaction language")
    interaction_mode: Literal["text", "mcq"] = Field(default="text", description="Selected interaction mode")

    def to_filter_dict(self) -> dict[str, any]:
        """Convert relevant profile attributes into metadata filters for retrieval."""
        filters = {}
        if self.state:
            filters["state"] = self.state
        if self.occupation:
            filters["beneficiary_categories"] = self.occupation
        return filters
