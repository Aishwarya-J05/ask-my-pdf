import React, { useEffect, useRef } from "react";
import Message from "./Message";
import { Bot } from "lucide-react";

const TypingIndicator = () => (
  <div
    style={{
      display: "flex",
      alignItems: "flex-start",
      gap: "8px",
      marginBottom: "24px",
    }}
  >
    <div
      style={{
        width: "32px",
        height: "32px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      <Bot size={16} color="white" />
    </div>

    <div
      style={{
        background: "#1e1e2e",
        border: "1px solid #2d2d3d",
        borderRadius: "18px 18px 18px 4px",
        padding: "14px 18px",
        display: "flex",
        alignItems: "center",
        gap: "6px",
      }}
    >
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            background: "#6366f1",
            animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
    </div>
  </div>
);

const EmptyState = () => (
  <div
    style={{
      flex: 1,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: "16px",
      color: "#4b5563",
    }}
  >
    <div
      style={{
        width: "64px",
        height: "64px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: 0.5,
      }}
    >
      <Bot size={32} color="white" />
    </div>
    <div style={{ textAlign: "center" }}>
      <p
        style={{
          fontSize: "18px",
          fontWeight: 600,
          color: "#6b7280",
          margin: "0 0 8px 0",
        }}
      >
        Ask My PDF
      </p>
      <p style={{ fontSize: "14px", color: "#4b5563", margin: 0 }}>
        Upload documents in the sidebar and start asking questions.
      </p>
    </div>
  </div>
);

const ChatWindow = ({ messages, isLoading }) => {
  const bottomRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div
      style={{
        flex: 1,
        overflowY: "auto",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        scrollbarWidth: "thin",
        scrollbarColor: "#2d2d3d transparent",
      }}
    >
      {messages.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
};

export default ChatWindow;