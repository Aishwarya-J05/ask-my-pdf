import time
import tempfile
from pathlib import Path
from typing import Dict

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ingestion.extractor import extract_from_multiple_pdfs
from app.ingestion.chunker import chunk_pages
from app.embeddings.embedder import embedder
from app.vectorstore.faiss_store import vector_store
from app.retrieval.hybrid import hybrid_retriever
from app.chain.rag_chain import RAGChain
from app.utils.config import settings
from app.utils.logger import get_logger
from api.schemas import QueryRequest, QueryResponse, IngestResponse, HealthResponse

logger = get_logger(__name__)

# ── App Initialization ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Ask My PDF API",
    description="RAG-powered document question answering API",
    version="1.0.0",
)

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ────────────────────────────────────────────────────
# Stores one RAGChain per session_id
# For production scale: replace with Redis
sessions: Dict[str, RAGChain] = {}


def get_or_create_session(session_id: str) -> RAGChain:
    """Returns existing RAGChain for session or creates a new one."""
    if session_id not in sessions:
        if not vector_store.is_built():
            raise HTTPException(
                status_code=400,
                detail="No documents ingested. Call /ingest first."
            )
        sessions[session_id] = RAGChain(use_hybrid=True)
        logger.info(f"New session created | ID: {session_id}")
    return sessions[session_id]


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Returns service status and current state."""
    return HealthResponse(
        status="ok",
        llm_backend=settings.LLM_BACKEND,
        documents_loaded=vector_store.is_built(),
        total_vectors=vector_store.index.ntotal if vector_store.is_built() else 0,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files: list[UploadFile] = File(...)):
    """
    Accepts one or more PDF files, runs full ingestion pipeline,
    builds FAISS + BM25 indexes, persists to disk.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    start_time = time.time()
    temp_paths = []

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save uploaded files to temp directory
            for uploaded_file in files:
                if not uploaded_file.filename.endswith(".pdf"):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{uploaded_file.filename} is not a PDF."
                    )
                temp_path = Path(tmpdir) / uploaded_file.filename
                temp_path.write_bytes(await uploaded_file.read())
                temp_paths.append(temp_path)

            # Stage 1 — Extract
            pages = extract_from_multiple_pdfs(temp_paths)
            if not pages:
                raise HTTPException(
                    status_code=422,
                    detail="No text extracted. PDFs may be scanned images."
                )

            # Stage 2 — Chunk
            chunks = chunk_pages(pages)

            # Stage 3 — Embed
            texts = [chunk["text"] for chunk in chunks]
            embeddings = embedder.embed_texts(texts)

            # Stage 4 — Build and persist FAISS
            vector_store.build(embeddings, chunks)
            vector_store.save()

            # Stage 5 — Build BM25
            hybrid_retriever.build_bm25(chunks)

        # Clear all existing sessions — new docs invalidate old chains
        sessions.clear()

        elapsed = round(time.time() - start_time, 2)
        filenames = [f.filename for f in files]

        logger.info(
            f"Ingestion complete | "
            f"Files: {filenames} | "
            f"Chunks: {len(chunks)} | "
            f"Elapsed: {elapsed}s"
        )

        return IngestResponse(
            success=True,
            message=f"Successfully ingested {len(files)} document(s).",
            filenames=filenames,
            total_chunks=len(chunks),
            elapsed_seconds=elapsed,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """
    Accepts a question and session_id, returns answer with citations.
    Maintains conversation memory per session.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        chain = get_or_create_session(request.session_id)
        result = chain.query(request.question)

        return QueryResponse(
            answer=result["answer"],
            citations=result["citations"],
            session_id=request.session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """Clears conversation memory for a given session."""
    if session_id in sessions:
        sessions[session_id].clear_memory()
        del sessions[session_id]
        logger.info(f"Session cleared | ID: {session_id}")
        return {"message": f"Session {session_id} cleared."}
    raise HTTPException(status_code=404, detail="Session not found.")


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,   # never use reload=True in production
    )