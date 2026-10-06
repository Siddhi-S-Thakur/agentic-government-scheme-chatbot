import logging
from typing import Optional
import httpx
from app.llm.base import BaseLLMService
from app.llm.offline import OfflineDeterministicLLMService
from app.llm.prompts import SYSTEM_PROMPT, build_grounded_explanation_prompt
from app.schemas.profile_schema import UserProfile
from app.eligibility.service import SchemeRecommendation
from app.schemas.retrieval_schema import RetrievedEvidence

logger = logging.getLogger(__name__)

class GeminiLLMService(BaseLLMService):
    """
    Google Gemini API provider implementation via HTTP REST.
    Falls back gracefully to OfflineDeterministicLLMService if the API call fails or key is missing.
    """
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        self.fallback = OfflineDeterministicLLMService()

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate_text(prompt, system_prompt)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(self.endpoint_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Gemini API call failed with error: {e}. Falling back to offline generator.")

        return self.fallback.generate_text(prompt, system_prompt)

    def generate_explanation(
        self,
        user_query: str,
        detected_language: str,
        profile: UserProfile,
        recommendations: list[SchemeRecommendation],
        evidence: list[RetrievedEvidence]
    ) -> str:
        if not self.api_key:
            return self.fallback.generate_explanation(
                user_query, detected_language, profile, recommendations, evidence
            )

        prompt = build_grounded_explanation_prompt(
            user_query=user_query,
            detected_language=detected_language,
            profile=profile,
            recommendations=recommendations,
            evidence=evidence
        )

        result = self.generate_text(prompt, system_prompt=SYSTEM_PROMPT)
        if result and not result.startswith("[Offline Fallback Response]"):
            return result

        # Fallback to offline structured explanation
        return self.fallback.generate_explanation(
            user_query, detected_language, profile, recommendations, evidence
        )
