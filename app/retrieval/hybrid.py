from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

from app.vectorstore.faiss_store import vector_store
from app.embeddings.embedder import embedder
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HybridRetriever:
    """
    Combines FAISS semantic search with BM25 keyword search.
    Fusion strategy: Reciprocal Rank Fusion (RRF).

    Why hybrid:
    - Semantic search finds conceptually related chunks (even with different words)
    - BM25 finds exact keyword matches (critical for legal/technical terms)
    - RRF merges both ranked lists without needing score normalization
    """

    def __init__(self):
        self.bm25 = None
        self.bm25_chunks: List[Dict[str, Any]] = []

    def build_bm25(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Builds BM25 index from chunk texts.
        Must be called after FAISS index is built.

        Args:
            chunks: List of chunk dicts from chunker.py
        """
        self.bm25_chunks = chunks

        # BM25 operates on tokenized text — simple whitespace split
        tokenized_corpus = [chunk["text"].lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        logger.info(f"BM25 index built | Chunks: {len(chunks)}")

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Runs hybrid search: FAISS + BM25, fused with Reciprocal Rank Fusion.

        Args:
            query: User's natural language question.
            top_k: Number of final results to return.

        Returns:
            Re-ranked list of chunk dicts with fused RRF score.
        """
        if not vector_store.is_built():
            raise RuntimeError("Vector store is empty. Ingest documents first.")

        if self.bm25 is None:
            raise RuntimeError("BM25 index not built. Call build_bm25() first.")

        top_k = top_k or settings.TOP_K_RESULTS

        # --- Semantic retrieval via FAISS ---
        query_embedding = embedder.embed_query(query)
        semantic_results = vector_store.search(query_embedding, top_k=top_k * 2)

        # --- Keyword retrieval via BM25 ---
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Get top_k*2 BM25 chunk indices sorted by score
        top_bm25_indices = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True
        )[:top_k * 2]

        bm25_results = [self.bm25_chunks[i] for i in top_bm25_indices]

        # --- Reciprocal Rank Fusion ---
        # RRF score = sum of 1 / (rank + k) across both lists
        # k=60 is standard — dampens the impact of very high ranks
        rrf_scores: Dict[int, float] = {}
        chunk_map: Dict[int, Dict[str, Any]] = {}

        for rank, chunk in enumerate(semantic_results):
            idx = chunk["chunk_index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (rank + 60)
            chunk_map[idx] = chunk

        for rank, chunk in enumerate(bm25_results):
            idx = chunk["chunk_index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (rank + 60)
            chunk_map[idx] = chunk

        # Sort by fused RRF score descending
        sorted_indices = sorted(rrf_scores, key=lambda i: rrf_scores[i], reverse=True)

        fused_results = []
        for idx in sorted_indices[:top_k]:
            chunk = chunk_map[idx].copy()
            chunk["score"] = round(rrf_scores[idx], 6)
            fused_results.append(chunk)

        logger.info(
            f"Hybrid search | "
            f"Query: '{query[:60]}' | "
            f"Semantic: {len(semantic_results)} | "
            f"BM25: {len(bm25_results)} | "
            f"Fused: {len(fused_results)}"
        )

        return fused_results


# Single instance
hybrid_retriever = HybridRetriever()