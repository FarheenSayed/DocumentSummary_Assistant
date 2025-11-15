import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import "./Upload.css"; // Updated CSS below

const UploadComponent = ({ 
  onUpload, 
  length, 
  setLength, 
  loading, 
  uploadedFile, 
  summary, 
  improvements 
}) => {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fileName, setFileName] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];

      const allowedTypes = ["application/pdf", "image/png", "image/jpeg", "image/jpg"];
      if (!allowedTypes.includes(file.type)) {
        alert("Only PDF, PNG, JPG files are allowed.");
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        alert("File size must be less than 10MB.");
        return;
      }

      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => setPreviewUrl(reader.result);
        reader.readAsDataURL(file);
      } else {
        setPreviewUrl(null);
      }

      setFileName(file.name);
      onUpload(file);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg"],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024,
  });

  return (
    <div className={`upload-container ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
      {/* Theme Toggle */}
      <button 
        className="theme-toggle" 
        onClick={toggleTheme}
        aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
      >
        {isDarkMode ? (
          <>
            ☀️ Light Mode
          </>
        ) : (
          <>
            🌙 Dark Mode
          </>
        )}
      </button>

      {/* Upload Zone */}
      <div {...getRootProps({ className: `dropzone ${isDragActive ? "drag-active" : ""} ${loading ? "loading-state" : ""}` })}>
        <input {...getInputProps()} />
        
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing Document...</p>
          </div>
        ) : (
          <>
            <div className="icon">📁</div>
            <h3>Upload Your Document</h3>
            <p className="subtitle">Drag & drop or click to browse</p>
            <p className="hint">Supports PDF, PNG, JPG (max 10MB)</p>
          </>
        )}

        {!loading && (
          <div className="length-selector">
            <label htmlFor="length">Summary Length: </label>
            <select
              id="length"
              value={length}
              onChange={(e) => setLength(e.target.value)}
            >
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>
        )}
      </div>

      {/* Uploaded File Preview */}
      {uploadedFile && (
        <div className="document-preview animate-fadeIn">
          <h3>📄 Uploaded Document</h3>
          <div className="file-info">
            <span className="filename">{fileName}</span>
            <a 
              href={uploadedFile.file_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="download-btn"
              download
            >
              💾 Download
            </a>
          </div>

          {previewUrl && (
            <div className="preview-image-wrapper">
              <img src={previewUrl} alt="Uploaded preview" className="preview-image" />
            </div>
          )}

          {!previewUrl && fileName.toLowerCase().endsWith('.pdf') && (
            <div className="pdf-preview-box">
              <p>📘 PDF uploaded successfully. Click "Download" to view.</p>
            </div>
          )}
        </div>
      )}

      {/* AI Summary */}
      {summary && (
        <div className="ai-summary animate-fadeIn">
          <h3>✨ AI-Generated Summary</h3>
          <div className="content-box">
            {/* Remove markdown formatting for cleaner display */}
            <div className="summary-text">
              {summary.replace(/\*\*/g, '').replace(/\\n/g, '\n')}
            </div>
          </div>
        </div>
      )}

      {/* Improvements */}
      {improvements && (
        <div className="improvements animate-fadeIn">
          <h3>🔍 Document Analysis & Improvements</h3>
          <div className="content-box">
            <div className="improvements-text">
              {improvements.replace(/\*\*/g, '').replace(/\\n/g, '\n')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadComponent;