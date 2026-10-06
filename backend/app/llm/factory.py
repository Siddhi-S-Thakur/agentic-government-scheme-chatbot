import logging
from app.core.config import settings
from app.llm.base import BaseLLMService
from app.llm.gemini import GeminiLLMService
from app.llm.openai import OpenAILLMService
from app.llm.offline import OfflineDeterministicLLMService

logger = logging.getLogger(__name__)

def get_llm_service() -> BaseLLMService:
    """
    Factory function instantiating the configured LLM provider
    with automatic offline fallback if credentials are absent.
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "gemini" and settings.gemini_api_key:
        logger.info(f"Initialized Gemini LLM provider with model '{settings.llm_model}'")
        return GeminiLLMService(api_key=settings.gemini_api_key, model=settings.llm_model)

    if provider == "openai" and settings.openai_api_key:
        logger.info(f"Initialized OpenAI LLM provider with model '{settings.llm_model}'")
        return OpenAILLMService(api_key=settings.openai_api_key, model=settings.llm_model)

    # Offline deterministic generator fallback
    logger.info("Using OfflineDeterministicLLMService (offline fallback mode)")
    return OfflineDeterministicLLMService()
