from langchain_community.llms import Ollama
from typing import Optional

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_ollama_llm() -> Ollama:
    """
    Returns a configured Ollama LLM instance for local offline inference.
    Requires Ollama to be running locally with the target model pulled.

    Setup (run once before using):
        1. Download Ollama: https://ollama.ai
        2. Pull model: ollama pull mistral
        3. Ollama runs as a background service on port 11434
    """
    logger.info(
        f"Initializing Ollama LLM | "
        f"Model: {settings.OLLAMA_MODEL} | "
        f"URL: {settings.OLLAMA_BASE_URL}"
    )

    llm = Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0,        # deterministic — same reasoning as Mistral client
        num_predict=1024,     # max tokens to generate
        timeout=120,          # local models are slower — give more time than API
    )

    return llm


def test_ollama_connection() -> bool:
    """
    Verifies Ollama service is running and model is available.
    Use during startup or debugging.

    Returns:
        True if Ollama responds, False otherwise.
    """
    try:
        llm = get_ollama_llm()
        response = llm.invoke("Reply with OK only.")
        logger.info(f"Ollama connection test passed | Response: {response[:50]}")
        return True
    except Exception as e:
        logger.error(
            f"Ollama connection test failed: {e} | "
            f"Make sure Ollama is running: 'ollama serve'"
        )
        return False