from typing import List, Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import BaseMessage

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Prompt Template ────────────────────────────────────────────────────────────
# This is your anti-hallucination guardrail.
# The LLM is explicitly told to answer ONLY from provided context.
SYSTEM_PROMPT = """You are a precise document assistant. Your job is to answer questions strictly based on the provided context excerpts from uploaded documents.

Rules you must follow:
1. Answer ONLY from the provided context. Do not use outside knowledge.
2. If the answer is not in the context, say exactly: "I could not find this information in the uploaded documents."
3. Always cite your source at the end of your answer in this format: [Source: <filename>, Page <number>]
4. If multiple chunks support the answer, cite all of them.
5. Be concise and factual. Do not speculate or infer beyond what is written.

Context:
{context}
"""

HUMAN_PROMPT = "{question}"


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved chunks into a single context string for the prompt.
    Each chunk is labeled with its source and page number.

    Args:
        chunks: List of chunk dicts from retrieval layer.

    Returns:
        Formatted context string injected into the system prompt.
    """
    formatted = []
    for i, chunk in enumerate(chunks, 1):
        formatted.append(
            f"[Excerpt {i} | Source: {chunk['source']} | Page {chunk['page_number']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n---\n\n".join(formatted)


def format_citations(chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Extracts unique citations from retrieved chunks.

    Returns:
        Deduplicated list of citation strings.
    """
    seen = set()
    citations = []
    for chunk in chunks:
        citation = f"{chunk['source']} — Page {chunk['page_number']}"
        if citation not in seen:
            seen.add(citation)
            citations.append(citation)
    return citations


class RAGChain:
    """
    Orchestrates the full RAG pipeline:
    retrieval → context formatting → LLM generation → memory update
    """

    def __init__(self, use_hybrid: bool = True):
        """
        Args:
            use_hybrid: If True, uses BM25+FAISS hybrid retrieval.
                       If False, uses semantic-only retrieval.
        """
        self.use_hybrid = use_hybrid
        self.llm = self._load_llm()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,   # returns Message objects, not raw strings
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", HUMAN_PROMPT),
        ])

        logger.info(
            f"RAGChain initialized | "
            f"Backend: {settings.LLM_BACKEND} | "
            f"Retrieval: {'hybrid' if use_hybrid else 'semantic'}"
        )

    def _load_llm(self):
        """Loads the correct LLM based on LLM_BACKEND config."""
        if settings.LLM_BACKEND == "mistral_api":
            from app.llm.mistral_client import get_mistral_llm
            return get_mistral_llm()
        elif settings.LLM_BACKEND == "ollama":
            from app.llm.ollama_client import get_ollama_llm
            return get_ollama_llm()
        else:
            raise ValueError(
                f"Unknown LLM_BACKEND: '{settings.LLM_BACKEND}'. "
                f"Must be 'mistral_api' or 'ollama'."
            )

    def _retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Runs retrieval based on configured strategy."""
        if self.use_hybrid:
            from app.retrieval.hybrid import hybrid_retriever
            return hybrid_retriever.search(query)
        else:
            from app.retrieval.semantic import semantic_search
            return semantic_search(query)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Full RAG query pipeline: retrieve → format → generate → return.

        Args:
            question: User's natural language question.

        Returns:
            Dict with keys:
                - answer: LLM generated answer string
                - citations: List of source citation strings
                - chunks: Raw retrieved chunks (for debugging/display)
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info(f"RAG query received: '{question[:80]}'")

        # Step 1 — Retrieve relevant chunks
        chunks = self._retrieve(question)

        if not chunks:
            logger.warning("No chunks retrieved for query.")
            return {
                "answer": "I could not find relevant information in the uploaded documents.",
                "citations": [],
                "chunks": [],
            }

        # Step 2 — Format chunks into context string
        context = format_context(chunks)

        # Step 3 — Get conversation history from memory
        chat_history: List[BaseMessage] = self.memory.chat_memory.messages

        # Step 4 — Build and invoke the prompt chain
        chain = self.prompt | self.llm

        response = chain.invoke({
            "context": context,
            "chat_history": chat_history,
            "question": question,
        })

        # Extract answer text from response object
        answer = response.content if hasattr(response, "content") else str(response)

        # Step 5 — Save this turn to memory
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(answer)

        # Step 6 — Extract citations
        citations = format_citations(chunks)

        logger.info(f"RAG query complete | Citations: {citations}")

        return {
            "answer": answer,
            "citations": citations,
            "chunks": chunks,
        }

    def clear_memory(self) -> None:
        """Resets conversation history. Call when user starts a new session."""
        self.memory.clear()
        logger.info("Conversation memory cleared.")

    def get_history(self) -> List[BaseMessage]:
        """Returns current conversation history as list of Message objects."""
        return self.memory.chat_memory.messages