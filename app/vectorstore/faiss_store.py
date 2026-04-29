import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FAISSVectorStore:
    """
    Manages FAISS index for storing and searching document chunk embeddings.
    Persists both the FAISS index and chunk metadata to disk.
    """

    def __init__(self):
        self.index = None          # FAISS index object
        self.chunks: List[Dict[str, Any]] = []  # parallel list — chunk[i] matches index vector i
        self.dimension: int = 384  # BGE-small-en-v1.5 output dimension

    def build(self, embeddings: np.ndarray, chunks: List[Dict[str, Any]]) -> None:
        """
        Builds FAISS index from embeddings and stores chunk metadata.

        Args:
            embeddings: float32 array of shape (n_chunks, dimension)
            chunks: List of chunk dicts from chunker.py — must be same length as embeddings
        """
        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Embeddings count ({len(embeddings)}) != chunks count ({len(chunks)})"
            )

        self.dimension = embeddings.shape[1]
        self.chunks = chunks

        # IndexFlatIP = exact search using inner product (cosine similarity after L2 norm)
        # Use this over IndexFlatL2 because embeddings are already normalized
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)

        logger.info(
            f"FAISS index built | "
            f"Vectors: {self.index.ntotal} | "
            f"Dimension: {self.dimension}"
        )

    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Searches FAISS index for most similar chunks to query embedding.

        Args:
            query_embedding: float32 array of shape (1, dimension)
            top_k: Number of results to return. Defaults to settings.TOP_K_RESULTS

        Returns:
            List of chunk dicts with added "score" key (cosine similarity 0-1)
        """
        if self.index is None:
            raise RuntimeError("FAISS index is not built. Call build() or load() first.")

        top_k = top_k or settings.TOP_K_RESULTS

        # FAISS returns scores and indices of nearest vectors
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                # FAISS returns -1 for empty slots when fewer results than top_k
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        logger.debug(f"FAISS search returned {len(results)} results for top_k={top_k}")
        return results

    def save(self, name: str = "index") -> None:
        """
        Persists FAISS index and chunk metadata to disk.

        Args:
            name: Base filename for saved files (default: "index")
        """
        if self.index is None:
            raise RuntimeError("No index to save. Build the index first.")

        save_dir = settings.VECTORSTORE_DIR
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save FAISS binary index
        faiss.write_index(self.index, str(save_dir / f"{name}.faiss"))

        # Save chunk metadata separately — FAISS only stores vectors, not metadata
        with open(save_dir / f"{name}.pkl", "wb") as f:
            pickle.dump(self.chunks, f)

        logger.info(f"FAISS index saved to {save_dir} | Name: {name}")

    def load(self, name: str = "index") -> None:
        """
        Loads persisted FAISS index and chunk metadata from disk.

        Args:
            name: Base filename to load (must match what was saved)
        """
        save_dir = settings.VECTORSTORE_DIR
        index_path = save_dir / f"{name}.faiss"
        meta_path = save_dir / f"{name}.pkl"

        if not index_path.exists() or not meta_path.exists():
            raise FileNotFoundError(
                f"Index files not found at {save_dir}. "
                f"Ingest documents first."
            )

        self.index = faiss.read_index(str(index_path))

        with open(meta_path, "rb") as f:
            self.chunks = pickle.load(f)

        self.dimension = self.index.d

        logger.info(
            f"FAISS index loaded | "
            f"Vectors: {self.index.ntotal} | "
            f"Chunks: {len(self.chunks)}"
        )

    def is_built(self) -> bool:
        """Returns True if index is loaded and contains vectors."""
        return self.index is not None and self.index.ntotal > 0


# Single instance shared across the app
vector_store = FAISSVectorStore()