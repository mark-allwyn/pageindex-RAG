import React, { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';

interface Document {
  id: string;
  filename: string;
  indexed: boolean;
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8000/documents');
      const data = await response.json();
      setDocuments(data.documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSuccess = () => {
    fetchDocuments();
  };

  const handleDeleteDocument = async (filename: string) => {
    try {
      await fetch(`http://localhost:8000/documents/${filename}`, {
        method: 'DELETE'
      });
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PageIndex RAG - Document Q&A</h1>
        <p className="subtitle">Upload documents and ask questions using reasoning-based retrieval</p>
      </header>

      <div className="container">
        <div className="sidebar">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          <DocumentList
            documents={documents}
            onDelete={handleDeleteDocument}
          />
        </div>

        <div className="main-content">
          <ChatInterface documents={documents} />
        </div>
      </div>
    </div>
  );
}

export default App;
