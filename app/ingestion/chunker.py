from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def chunk_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits extracted PDF pages into overlapping chunks for embedding.

    Args:
        pages: Output from extractor.py — list of page dicts with
               keys: text, page_number, source

    Returns:
        List of chunk dicts:
        [
            {
                "text": "chunk content...",
                "page_number": 3,
                "source": "report.pdf",
                "chunk_index": 0
            },
            ...
        ]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],  # respects paragraph → sentence → word boundaries
        length_function=len,
    )

    all_chunks = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]
        source = page["source"]

        # Split this page's text into chunks
        splits = splitter.split_text(text)

        for split_text in splits:
            # Skip noise — chunks that are too short to be meaningful
            if len(split_text.strip()) < 30:
                logger.debug(f"Skipping short chunk on page {page_number} of {source}")
                continue

            all_chunks.append({
                "text": split_text.strip(),
                "page_number": page_number,
                "source": source,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

    logger.info(
        f"Chunking complete | "
        f"Pages: {len(pages)} | "
        f"Chunks: {len(all_chunks)} | "
        f"Chunk size: {settings.CHUNK_SIZE} | "
        f"Overlap: {settings.CHUNK_OVERLAP}"
    )

    return all_chunks