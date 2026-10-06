from abc import ABC, abstractmethod
from typing import Optional, Any
from app.schemas.profile_schema import UserProfile
from app.eligibility.service import SchemeRecommendation
from app.schemas.retrieval_schema import RetrievedEvidence

class BaseLLMService(ABC):
    """
    Abstract interface for LLM provider implementations (Gemini, OpenAI, Offline Fallback).
    """

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response text for a given prompt and system instructions."""
        pass

    @abstractmethod
    def generate_explanation(
        self,
        user_query: str,
        detected_language: str,
        profile: UserProfile,
        recommendations: list[SchemeRecommendation],
        evidence: list[RetrievedEvidence]
    ) -> str:
        """
        Generate a conversational, grounded explanation of scheme recommendations
        and deterministic eligibility verdicts in the specified language.
        """
        pass
