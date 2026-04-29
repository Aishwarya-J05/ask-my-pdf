import React from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import { useChat } from "./hooks/useChat";

const App = () => {
  const {
    messages,
    isLoading,
    isIngesting,
    ingestProgress,
    documentsLoaded,
    loadedFiles,
    apiOnline,
    error,
    pingHealth,
    ingestFiles,
    sendMessage,
    clearConversation,
  } = useChat();

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        background: "#0d0d1a",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Sidebar */}
      <Sidebar
        apiOnline={apiOnline}
        documentsLoaded={documentsLoaded}
        loadedFiles={loadedFiles}
        isIngesting={isIngesting}
        ingestProgress={ingestProgress}
        onUpload={ingestFiles}
        onClearConversation={clearConversation}
        pingHealth={pingHealth}
      />

      {/* Main chat area */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Error banner */}
        {error && (
          <div
            style={{
              padding: "10px 24px",
              background: "rgba(239,68,68,0.1)",
              borderBottom: "1px solid rgba(239,68,68,0.2)",
              color: "#ef4444",
              fontSize: "13px",
            }}
          >
            {error}
          </div>
        )}

        {/* Chat window */}
        <ChatWindow messages={messages} isLoading={isLoading} />

        {/* Input */}
        <ChatInput
          onSend={sendMessage}
          isLoading={isLoading}
          disabled={!documentsLoaded}
        />
      </div>
    </div>
  );
};

export default App;