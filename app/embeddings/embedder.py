from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Embedder:
    """
    Wrapper around SentenceTransformer for generating dense vector embeddings.
    Uses BGE model which is optimized for retrieval tasks.
    """

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded | Dimension: {self.dimension}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embeds a list of texts into dense vectors.

        Args:
            texts: List of strings to embed.

        Returns:
            numpy array of shape (len(texts), embedding_dimension)
            dtype float32 — required by FAISS
        """
        if not texts:
            logger.warning("embed_texts called with empty list")
            return np.array([])

        logger.info(f"Embedding {len(texts)} texts")

        embeddings = self.model.encode(
            texts,
            batch_size=64,           # process in batches to avoid OOM
            show_progress_bar=True,  # visible progress for large PDFs
            normalize_embeddings=True,  # L2 normalize — required for cosine similarity in FAISS
            convert_to_numpy=True,
        )

        # FAISS requires float32 explicitly
        embeddings = embeddings.astype(np.float32)

        logger.info(f"Embedding complete | Shape: {embeddings.shape}")
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string.
        Separate method because BGE models use a query prefix for better retrieval.

        Args:
            query: User's question string.

        Returns:
            numpy array of shape (1, embedding_dimension) — float32
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")

        # BGE models perform better with this prefix on queries (not on documents)
        prefixed_query = f"Represent this sentence for searching relevant passages: {query}"

        embedding = self.model.encode(
            [prefixed_query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        logger.debug(f"Query embedded | Shape: {embedding.shape}")
        return embedding


# Single instance — model loads once, reused across the app
embedder = Embedder()