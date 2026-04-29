import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, Loader2 } from "lucide-react";

const FileUpload = ({ onUpload, isIngesting, ingestProgress }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    setSelectedFiles((prev) => {
      // Avoid duplicates by filename
      const existing = new Set(prev.map((f) => f.name));
      const newFiles = acceptedFiles.filter((f) => !existing.has(f.name));
      return [...prev, ...newFiles];
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    disabled: isIngesting,
  });

  const removeFile = (filename) => {
    setSelectedFiles((prev) => prev.filter((f) => f.name !== filename));
  };

  const handleUpload = () => {
    if (selectedFiles.length === 0 || isIngesting) return;
    onUpload(selectedFiles);
    setSelectedFiles([]);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {/* Dropzone */}
      <div
        {...getRootProps()}
        style={{
          border: `2px dashed ${isDragActive ? "#6366f1" : "#2d2d3d"}`,
          borderRadius: "12px",
          padding: "20px",
          textAlign: "center",
          cursor: isIngesting ? "not-allowed" : "pointer",
          background: isDragActive ? "rgba(99,102,241,0.08)" : "transparent",
          transition: "all 0.2s",
        }}
      >
        <input {...getInputProps()} />
        <Upload
          size={24}
          color={isDragActive ? "#6366f1" : "#4b5563"}
          style={{ margin: "0 auto 8px auto", display: "block" }}
        />
        <p
          style={{
            fontSize: "13px",
            color: isDragActive ? "#6366f1" : "#6b7280",
            margin: 0,
          }}
        >
          {isDragActive
            ? "Drop PDFs here"
            : "Drag & drop PDFs or click to browse"}
        </p>
      </div>

      {/* Selected files list */}
      {selectedFiles.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {selectedFiles.map((file) => (
            <div
              key={file.name}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "8px 10px",
                background: "#1e1e2e",
                borderRadius: "8px",
                border: "1px solid #2d2d3d",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  overflow: "hidden",
                }}
              >
                <FileText size={14} color="#6366f1" flexShrink={0} />
                <span
                  style={{
                    fontSize: "13px",
                    color: "#94a3b8",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {file.name}
                </span>
              </div>
              <button
                onClick={() => removeFile(file.name)}
                style={{
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  color: "#6b7280",
                  padding: "2px",
                  flexShrink: 0,
                }}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Progress bar */}
      {isIngesting && (
        <div>
          <div
            style={{
              height: "4px",
              background: "#2d2d3d",
              borderRadius: "2px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${ingestProgress}%`,
                background: "linear-gradient(90deg, #6366f1, #8b5cf6)",
                borderRadius: "2px",
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <p
            style={{
              fontSize: "12px",
              color: "#6b7280",
              marginTop: "6px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Loader2
              size={12}
              style={{ animation: "spin 1s linear infinite" }}
            />
            Processing documents...
          </p>
        </div>
      )}

      {/* Upload button */}
      {selectedFiles.length > 0 && !isIngesting && (
        <button
          onClick={handleUpload}
          style={{
            width: "100%",
            padding: "10px",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            border: "none",
            borderRadius: "10px",
            color: "white",
            fontSize: "14px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Process {selectedFiles.length} file
          {selectedFiles.length > 1 ? "s" : ""}
        </button>
      )}
    </div>
  );
};

export default FileUpload;