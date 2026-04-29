import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { User, Bot, ChevronDown, ChevronUp, FileText, AlertCircle } from "lucide-react";
import Citations from "./Citations";

const Message = ({ message }) => {
  const isUser = message.role === "user";
  const isError = message.isError;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: isUser ? "flex-end" : "flex-start",
        marginBottom: "24px",
        gap: "8px",
      }}
    >
      {/* Role label + icon */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          flexDirection: isUser ? "row-reverse" : "row",
        }}
      >
        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            background: isUser
              ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
              : isError
              ? "linear-gradient(135deg, #ef4444, #dc2626)"
              : "linear-gradient(135deg, #0ea5e9, #6366f1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {isUser ? (
            <User size={16} color="white" />
          ) : isError ? (
            <AlertCircle size={16} color="white" />
          ) : (
            <Bot size={16} color="white" />
          )}
        </div>
        <span
          style={{
            fontSize: "12px",
            color: "#6b7280",
            fontWeight: 500,
          }}
        >
          {isUser ? "You" : "Assistant"}
        </span>
      </div>

      {/* Message bubble */}
      <div
        style={{
          maxWidth: "75%",
          background: isUser
            ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
            : "#1e1e2e",
          color: isUser ? "white" : "#e2e8f0",
          borderRadius: isUser
            ? "18px 18px 4px 18px"
            : "18px 18px 18px 4px",
          padding: "12px 16px",
          fontSize: "15px",
          lineHeight: "1.6",
          border: isUser ? "none" : "1px solid #2d2d3d",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
        }}
      >
        {isUser ? (
          <p style={{ margin: 0 }}>{message.content}</p>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => (
                <p style={{ margin: "0 0 8px 0" }}>{children}</p>
              ),
              code: ({ children }) => (
                <code
                  style={{
                    background: "#0d0d1a",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    fontSize: "13px",
                    color: "#a5f3fc",
                  }}
                >
                  {children}
                </code>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>

      {/* Citations */}
      {!isUser && message.citations && message.citations.length > 0 && (
        <Citations citations={message.citations} />
      )}
    </div>
  );
};

export default Message;