import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extracts text from each page of a PDF file.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        List of dicts, one per page:
        [
            {
                "text": "page content...",
                "page_number": 1,
                "source": "report.pdf"
            },
            ...
        ]
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        logger.error(f"File is not a PDF: {pdf_path}")
        raise ValueError(f"File is not a PDF: {pdf_path}")

    pages = []

    try:
        doc = fitz.open(str(pdf_path))
        logger.info(f"Opened PDF: {pdf_path.name} | Pages: {len(doc)}")

        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text").strip()

            # Skip empty pages (scanned images, blank pages)
            if not text:
                logger.debug(f"Skipping empty page {page_index + 1} in {pdf_path.name}")
                continue

            pages.append({
                "text": text,
                "page_number": page_index + 1,  # 1-indexed for citations
                "source": pdf_path.name,
            })

        doc.close()
        logger.info(f"Extracted {len(pages)} non-empty pages from {pdf_path.name}")

    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
        raise

    return pages


def extract_from_multiple_pdfs(pdf_paths: List[str | Path]) -> List[Dict[str, Any]]:
    """
    Extracts text from multiple PDFs and combines results.

    Args:
        pdf_paths: List of paths to PDF files.

    Returns:
        Combined list of page dicts from all PDFs.
    """
    all_pages = []

    for path in pdf_paths:
        try:
            pages = extract_text_from_pdf(path)
            all_pages.extend(pages)
        except Exception as e:
            # Log and continue — don't let one bad PDF kill the whole batch
            logger.error(f"Skipping {path} due to error: {e}")
            continue

    logger.info(f"Total pages extracted from {len(pdf_paths)} PDFs: {len(all_pages)}")
    return all_pages