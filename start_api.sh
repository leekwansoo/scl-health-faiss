#!/bin/bash

# Start SCL Health FAISS API Server
# Usage: ./start_api.sh [port]

PORT=${1:-8000}

echo "Starting SCL Health FAISS API Server..."
echo "Port: $PORT"
echo "Make sure your .env file is configured with API_TOKENS and OPENAI_API_KEY"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "Copy .env.example to .env and configure your API tokens and OpenAI key."
    echo ""
fi

# Ensure required directories exist
mkdir -p uploaded query qa_pair faiss_db

# Start the server
python api_server.py --port $PORT