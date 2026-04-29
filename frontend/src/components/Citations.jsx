import React, { useState } from "react";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

const Citations = ({ citations }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        maxWidth: "75%",
        background: "#12121f",
        border: "1px solid #2d2d3d",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      {/* Toggle header */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 12px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          color: "#6366f1",
          fontSize: "13px",
          fontWeight: 500,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <FileText size={14} />
          <span>
            {citations.length} source{citations.length > 1 ? "s" : ""}
          </span>
        </div>
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {/* Citations list */}
      {expanded && (
        <div
          style={{
            padding: "0 12px 10px 12px",
            display: "flex",
            flexDirection: "column",
            gap: "6px",
          }}
        >
          {citations.map((citation, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 10px",
                background: "#1e1e2e",
                borderRadius: "8px",
                fontSize: "13px",
                color: "#94a3b8",
              }}
            >
              <FileText size={12} color="#6366f1" />
              <span>{citation}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Citations;