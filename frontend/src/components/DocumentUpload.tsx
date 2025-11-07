import React, { useState } from 'react';
import './DocumentUpload.css';

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Document uploaded and indexed successfully!' });
        setFile(null);
        onUploadSuccess();
        // Reset file input
        const fileInput = document.getElementById('file-input') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Upload failed' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Upload failed. Please try again.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card document-upload">
      <h2>Upload Document</h2>
      <div className="upload-area">
        <input
          id="file-input"
          type="file"
          accept=".pdf,.md,.markdown"
          onChange={handleFileChange}
          className="file-input"
        />
        <label htmlFor="file-input" className="file-label">
          {file ? file.name : 'Choose a file (PDF or Markdown)'}
        </label>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'Processing...' : 'Upload & Index'}
        </button>
      </div>
      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}
      <div className="upload-info">
        <p>Supported formats: PDF, Markdown (.md)</p>
        <p>Documents will be processed using PageIndex methodology</p>
      </div>
    </div>
  );
};

export default DocumentUpload;
