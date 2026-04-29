import React, { useState, useRef, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";

const ChatInput = ({ onSend, isLoading, disabled }) => {
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);

  const handleSend = useCallback(() => {
    if (!input.trim() || isLoading || disabled) return;
    onSend(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, isLoading, disabled, onSend]);

  const handleKeyDown = (e) => {
    // Send on Enter, new line on Shift+Enter
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e) => {
    setInput(e.target.value);
    // Auto-resize textarea
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
    }
  };

  return (
    <div
      style={{
        padding: "16px 24px 24px 24px",
        background: "#0d0d1a",
        borderTop: "1px solid #1e1e2e",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: "12px",
          background: "#1e1e2e",
          border: "1px solid #2d2d3d",
          borderRadius: "16px",
          padding: "12px 16px",
          transition: "border-color 0.2s",
        }}
        onFocus={() => {}}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={
            disabled
              ? "Upload and process documents first..."
              : "Ask a question about your documents..."
          }
          disabled={disabled || isLoading}
          rows={1}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            outline: "none",
            color: disabled ? "#4b5563" : "#e2e8f0",
            fontSize: "15px",
            lineHeight: "1.6",
            resize: "none",
            fontFamily: "inherit",
            cursor: disabled ? "not-allowed" : "text",
          }}
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading || disabled}
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            border: "none",
            background:
              !input.trim() || isLoading || disabled
                ? "#2d2d3d"
                : "linear-gradient(135deg, #6366f1, #8b5cf6)",
            cursor:
              !input.trim() || isLoading || disabled
                ? "not-allowed"
                : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            transition: "background 0.2s",
          }}
        >
          {isLoading ? (
            <Loader2
              size={18}
              color="#6b7280"
              style={{ animation: "spin 1s linear infinite" }}
            />
          ) : (
            <Send
              size={18}
              color={!input.trim() || disabled ? "#6b7280" : "white"}
            />
          )}
        </button>
      </div>

      <p
        style={{
          textAlign: "center",
          fontSize: "12px",
          color: "#4b5563",
          marginTop: "8px",
          marginBottom: 0,
        }}
      >
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
};

export default ChatInput;