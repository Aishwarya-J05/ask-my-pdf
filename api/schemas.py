from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"


class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
    session_id: str


class IngestResponse(BaseModel):
    success: bool
    message: str
    filenames: List[str]
    total_chunks: int
    elapsed_seconds: float


class HealthResponse(BaseModel):
    status: str
    llm_backend: str
    documents_loaded: bool
    total_vectors: int