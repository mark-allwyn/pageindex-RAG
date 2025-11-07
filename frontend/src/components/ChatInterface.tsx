import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

interface Document {
  id: string;
  filename: string;
  indexed: boolean;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

interface ChatInterfaceProps {
  documents: Document[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ documents }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          document_ids: null // Query all documents
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.answer,
          sources: data.sources
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const error = await response.json();
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error: ${error.detail || 'Failed to get answer. Please try again.'}`
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error: Failed to connect to the server. Please make sure the backend is running.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card chat-interface">
      <h2>Chat</h2>

      {documents.length === 0 && (
        <div className="chat-empty-state">
          <p>Please upload documents to start asking questions</p>
        </div>
      )}

      {documents.length > 0 && (
        <>
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <h3>Welcome to PageIndex RAG!</h3>
                <p>Ask questions about your documents. The system uses reasoning-based retrieval to find relevant information.</p>
                <div className="example-questions">
                  <p><strong>Example questions:</strong></p>
                  <ul>
                    <li>What is the main topic of the document?</li>
                    <li>Summarize the key findings</li>
                    <li>What does the document say about [specific topic]?</li>
                  </ul>
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  <div className="message-avatar">
                    {message.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.content}</div>
                    {message.sources && message.sources.length > 0 && (
                      <div className="message-sources">
                        <strong>Sources:</strong> {message.sources.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="chat-input"
              disabled={loading}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!input.trim() || loading}
            >
              {loading ? 'Thinking...' : 'Send'}
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default ChatInterface;
