import React from 'react';
import './DocumentList.css';

interface Document {
  id: string;
  filename: string;
  indexed: boolean;
}

interface DocumentListProps {
  documents: Document[];
  onDelete: (filename: string) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onDelete }) => {
  return (
    <div className="card document-list">
      <h2>Indexed Documents</h2>
      {documents.length === 0 ? (
        <p className="empty-state">No documents uploaded yet</p>
      ) : (
        <ul className="document-items">
          {documents.map((doc) => (
            <li key={doc.id} className="document-item">
              <div className="document-info">
                <span className="document-icon">📄</span>
                <span className="document-name" title={doc.filename}>
                  {doc.filename}
                </span>
              </div>
              <button
                className="btn btn-danger"
                onClick={() => {
                  if (window.confirm(`Delete ${doc.filename}?`)) {
                    onDelete(doc.filename);
                  }
                }}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentList;
