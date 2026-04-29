import React, { useEffect } from "react";
import { FileText, Trash2, Wifi, WifiOff, Settings, ChevronRight } from "lucide-react";
import FileUpload from "./FileUpload";

const Sidebar = ({
  apiOnline,
  documentsLoaded,
  loadedFiles,
  isIngesting,
  ingestProgress,
  onUpload,
  onClearConversation,
  pingHealth,
}) => {
  // Ping health every 30 seconds
  useEffect(() => {
    pingHealth();
    const interval = setInterval(pingHealth, 30000);
    return () => clearInterval(interval);
  }, [pingHealth]);

  return (
    <div
      style={{
        width: "280px",
        flexShrink: 0,
        background: "#12121f",
        borderRight: "1px solid #1e1e2e",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "24px 20px 16px 20px",
          borderBottom: "1px solid #1e1e2e",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginBottom: "16px",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <FileText size={18} color="white" />
          </div>
          <div>
            <h1
              style={{
                fontSize: "16px",
                fontWeight: 700,
                color: "#e2e8f0",
                margin: 0,
              }}
            >
              Ask My PDF
            </h1>
            <p style={{ fontSize: "11px", color: "#6b7280", margin: 0 }}>
              RAG Document Assistant
            </p>
          </div>
        </div>

        {/* API status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "6px 10px",
            background: apiOnline
              ? "rgba(34,197,94,0.1)"
              : "rgba(239,68,68,0.1)",
            borderRadius: "8px",
            border: `1px solid ${apiOnline ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"}`,
          }}
        >
          {apiOnline ? (
            <Wifi size={13} color="#22c55e" />
          ) : (
            <WifiOff size={13} color="#ef4444" />
          )}
          <span
            style={{
              fontSize: "12px",
              color: apiOnline ? "#22c55e" : "#ef4444",
              fontWeight: 500,
            }}
          >
            {apiOnline ? "API Online" : "API Offline"}
          </span>
        </div>
      </div>

      {/* Scrollable content */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px 20px",
          display: "flex",
          flexDirection: "column",
          gap: "24px",
          scrollbarWidth: "thin",
          scrollbarColor: "#2d2d3d transparent",
        }}
      >
        {/* Upload section */}
        <div>
          <p
            style={{
              fontSize: "11px",
              fontWeight: 600,
              color: "#6b7280",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: "10px",
            }}
          >
            Documents
          </p>
          <FileUpload
            onUpload={onUpload}
            isIngesting={isIngesting}
            ingestProgress={ingestProgress}
          />
        </div>

        {/* Loaded files */}
        {documentsLoaded && loadedFiles.length > 0 && (
          <div>
            <p
              style={{
                fontSize: "11px",
                fontWeight: 600,
                color: "#6b7280",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                marginBottom: "10px",
              }}
            >
              Loaded
            </p>
            <div
              style={{ display: "flex", flexDirection: "column", gap: "6px" }}
            >
              {loadedFiles.map((filename) => (
                <div
                  key={filename}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 10px",
                    background: "rgba(99,102,241,0.08)",
                    borderRadius: "8px",
                    border: "1px solid rgba(99,102,241,0.2)",
                  }}
                >
                  <FileText size={13} color="#6366f1" flexShrink={0} />
                  <span
                    style={{
                      fontSize: "13px",
                      color: "#94a3b8",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {filename}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer actions */}
      <div
        style={{
          padding: "16px 20px",
          borderTop: "1px solid #1e1e2e",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        <button
          onClick={onClearConversation}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "9px 12px",
            background: "transparent",
            border: "1px solid #2d2d3d",
            borderRadius: "8px",
            color: "#6b7280",
            fontSize: "13px",
            cursor: "pointer",
            width: "100%",
            transition: "all 0.2s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "#ef4444";
            e.currentTarget.style.color = "#ef4444";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "#2d2d3d";
            e.currentTarget.style.color = "#6b7280";
          }}
        >
          <Trash2 size={14} />
          Clear Conversation
        </button>
      </div>
    </div>
  );
};

export default Sidebar;