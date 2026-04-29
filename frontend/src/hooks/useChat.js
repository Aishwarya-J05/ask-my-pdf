import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { queryDocuments, ingestDocuments, checkHealth, clearSession } from "../services/api";

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestProgress, setIngestProgress] = useState(0);
  const [documentsLoaded, setDocumentsLoaded] = useState(false);
  const [loadedFiles, setLoadedFiles] = useState([]);
  const [apiOnline, setApiOnline] = useState(false);
  const [error, setError] = useState(null);
  const sessionId = useRef(uuidv4());

  // ── Health Check ─────────────────────────────────────────────────────────────
  const pingHealth = useCallback(async () => {
    try {
      const health = await checkHealth();
      setApiOnline(true);
      if (health.documents_loaded) {
        setDocumentsLoaded(true);
      }
      return health;
    } catch {
      setApiOnline(false);
      return null;
    }
  }, []);

  // ── Ingest Documents ─────────────────────────────────────────────────────────
  const ingestFiles = useCallback(async (files) => {
    setIsIngesting(true);
    setIngestProgress(0);
    setError(null);

    try {
      const result = await ingestDocuments(files, setIngestProgress);

      if (result.success) {
        setDocumentsLoaded(true);
        setLoadedFiles(result.filenames);
        setMessages([]);
        sessionId.current = uuidv4(); // new session for new documents
        return result;
      } else {
        throw new Error(result.message || "Ingestion failed");
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      return null;
    } finally {
      setIsIngesting(false);
      setIngestProgress(0);
    }
  }, []);

  // ── Send Message ─────────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (question) => {
    if (!question.trim() || isLoading) return;

    // Add user message immediately
    const userMessage = {
      id: uuidv4(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const result = await queryDocuments(question, sessionId.current);

      const assistantMessage = {
        id: uuidv4(),
        role: "assistant",
        content: result.answer,
        citations: result.citations || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);

      // Show error as assistant message
      setMessages((prev) => [
        ...prev,
        {
          id: uuidv4(),
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          citations: [],
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  // ── Clear Conversation ────────────────────────────────────────────────────────
  const clearConversation = useCallback(async () => {
    try {
      await clearSession(sessionId.current);
    } catch {
      // Session may not exist yet — that's fine
    }
    setMessages([]);
    sessionId.current = uuidv4();
  }, []);

  return {
    messages,
    isLoading,
    isIngesting,
    ingestProgress,
    documentsLoaded,
    loadedFiles,
    apiOnline,
    error,
    sessionId: sessionId.current,
    pingHealth,
    ingestFiles,
    sendMessage,
    clearConversation,
  };
};