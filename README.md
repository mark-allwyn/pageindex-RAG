# PageIndex RAG - Document Q&A Application

A full-stack RAG (Retrieval Augmented Generation) application that allows users to upload documents and ask questions using the [PageIndex methodology](https://github.com/VectifyAI/PageIndex). Unlike traditional vector-based RAG systems, PageIndex uses reasoning-based retrieval with hierarchical document structures.

## Features

- **Document Upload**: Support for PDF and Markdown files
- **Reasoning-Based Retrieval**: Uses PageIndex's hierarchical tree structure approach
- **Interactive Chat Interface**: Ask questions about your documents in real-time
- **Document Management**: View and delete indexed documents
- **Real-time Processing**: Documents are automatically indexed upon upload

## Architecture

- **Backend**: Python FastAPI server with PageIndex integration
- **Frontend**: React TypeScript application with modern UI
- **Document Processing**: Automatic indexing using OpenAI GPT-4
- **Storage**: File-based storage for documents and indices

## Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mark-allwyn/pageindex-RAG.git
cd pageindex-RAG
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Start the backend server
python main.py
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Upload Documents**
   - Click "Choose a file" in the sidebar
   - Select a PDF or Markdown file
   - Click "Upload & Index" to process the document

2. **Ask Questions**
   - Type your question in the chat input
   - Press "Send" or hit Enter
   - The system will use reasoning-based retrieval to find relevant information
   - Answers will include source documents

3. **Manage Documents**
   - View all indexed documents in the sidebar
   - Delete documents by clicking the "Delete" button

## API Endpoints

### Backend API (`http://localhost:8000`)

- `GET /` - Health check
- `POST /upload` - Upload and index a document
- `GET /documents` - List all indexed documents
- `POST /ask` - Ask a question about the documents
- `DELETE /documents/{filename}` - Delete a document

### Example API Request

```bash
# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

## Project Structure

```
pageindex-RAG/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── pageindex_lib/         # PageIndex library (cloned)
│   └── indices/               # Stored document indices
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── DocumentList.tsx
│   │   ├── App.tsx            # Main app component
│   │   └── App.css            # Global styles
│   ├── package.json
│   └── tsconfig.json
├── uploads/                    # Uploaded documents
└── README.md
```

## How PageIndex Works

PageIndex uses a fundamentally different approach compared to traditional vector-based RAG:

1. **Document Indexing**: Documents are converted into hierarchical tree structures (Table of Contents style)
2. **Reasoning-Based Retrieval**: Instead of vector similarity, the system uses LLM reasoning to navigate the document tree
3. **Relevance over Similarity**: The approach focuses on actual relevance rather than mathematical similarity

This results in more accurate and interpretable retrieval, especially for complex professional documents.

## Technologies Used

- **Backend**: FastAPI, Python, OpenAI API
- **Frontend**: React, TypeScript, CSS
- **Document Processing**: PageIndex, PyMuPDF, PyPDF2
- **AI**: OpenAI GPT-4

## Troubleshooting

### Backend not starting
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your OpenAI API key is set in `.env`

### Frontend not connecting to backend
- Ensure the backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify the API URL in frontend components

### Document processing fails
- Check that your OpenAI API key has sufficient credits
- Verify the document format is supported (PDF or Markdown)
- Check backend logs for detailed error messages

## License

This project uses the PageIndex library from [VectifyAI](https://github.com/VectifyAI/PageIndex).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [PageIndex](https://github.com/VectifyAI/PageIndex) by VectifyAI for the reasoning-based RAG methodology
- OpenAI for GPT-4 API
