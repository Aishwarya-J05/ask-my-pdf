import axios from "axios";

const API_BASE_URL = "http://16.171.166.122:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 min — large PDFs take time
});

// ── Health ─────────────────────────────────────────────────────────────────────
export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

// ── Ingest ─────────────────────────────────────────────────────────────────────
export const ingestDocuments = async (files, onProgress) => {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await api.post("/ingest", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });
  return response.data;
};

// ── Query ──────────────────────────────────────────────────────────────────────
export const queryDocuments = async (question, sessionId) => {
  const response = await api.post("/query", {
    question,
    session_id: sessionId,
  });
  return response.data;
};

// ── Clear Session ──────────────────────────────────────────────────────────────
export const clearSession = async (sessionId) => {
  const response = await api.delete(`/session/${sessionId}`);
  return response.data;
};