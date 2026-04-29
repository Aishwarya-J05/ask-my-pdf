import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    # LLM backend toggle: "mistral_api" or "ollama"
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "mistral_api")

    # Mistral API
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    # Ollama (local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")

    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))

    # Retrieval
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", 5))

    # Storage paths (resolved relative to project root)
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    UPLOAD_DIR: Path = PROJECT_ROOT / os.getenv("UPLOAD_DIR", "data/uploads")
    VECTORSTORE_DIR: Path = PROJECT_ROOT / os.getenv("VECTORSTORE_DIR", "data/vectorstore")

    def __post_init__(self):
        # Ensure directories exist at startup
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)


# Single instance imported everywhere
settings = Settings()

# Ensure directories exist on import
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)