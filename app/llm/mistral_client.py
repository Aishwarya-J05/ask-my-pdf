from langchain_mistralai import ChatMistralAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Optional

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_mistral_llm() -> ChatMistralAI:
    """
    Returns a configured ChatMistralAI instance.
    Called once during chain assembly — not on every query.
    """
    if not settings.MISTRAL_API_KEY:
        raise ValueError(
            "MISTRAL_API_KEY is not set. "
            "Add it to your .env file."
        )

    logger.info(f"Initializing Mistral LLM | Model: {settings.MISTRAL_MODEL}")

    llm = ChatMistralAI(
        api_key=settings.MISTRAL_API_KEY,
        model=settings.MISTRAL_MODEL,
        temperature=0,        # 0 = deterministic — no hallucination drift
        max_tokens=1024,      # enough for detailed answers, not runaway generation
        timeout=30,           # fail fast if API is unresponsive
    )

    return llm


def test_mistral_connection() -> bool:
    """
    Sends a minimal test message to verify API key and connectivity.
    Use during startup or debugging — not in the hot path.

    Returns:
        True if connection succeeds, False otherwise.
    """
    try:
        llm = get_mistral_llm()
        response = llm.invoke([HumanMessage(content="Reply with OK only.")])
        logger.info(f"Mistral connection test passed | Response: {response.content}")
        return True
    except Exception as e:
        logger.error(f"Mistral connection test failed: {e}")
        return False