#!/bin/bash

# Start Frontend Server Script
echo "Starting PageIndex RAG Frontend..."
echo "=================================="

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    exit 1
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start the development server
echo "Starting React development server on http://localhost:3000"
npm start
