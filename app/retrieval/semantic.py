from typing import List, Dict, Any

from app.vectorstore.faiss_store import vector_store
from app.embeddings.embedder import embedder
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def semantic_search(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    """
    Retrieves most semantically relevant chunks for a given query.

    Args:
        query: User's natural language question.
        top_k: Number of chunks to retrieve. Defaults to settings.TOP_K_RESULTS.

    Returns:
        List of chunk dicts with keys: text, page_number, source, score
    """
    top_k = top_k or settings.TOP_K_RESULTS

    if not vector_store.is_built():
        raise RuntimeError("Vector store is empty. Ingest documents first.")

    # Embed the query into the same vector space as the chunks
    query_embedding = embedder.embed_query(query)

    # Search FAISS for nearest chunk vectors
    results = vector_store.search(query_embedding, top_k=top_k)

    logger.info(
        f"Semantic search | "
        f"Query: '{query[:60]}...' | "
        f"Results: {len(results)}"
    )

    return results