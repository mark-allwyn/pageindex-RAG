#!/bin/bash

# Start Backend Server Script
echo "Starting PageIndex RAG Backend..."
echo "=================================="

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "ERROR: backend/.env file not found!"
    echo "Please create backend/.env with your OPENAI_API_KEY"
    echo "Example: echo 'OPENAI_API_KEY=your_key_here' > backend/.env"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if dependencies are installed
echo "Checking Python dependencies..."
cd backend
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
python3 main.py
