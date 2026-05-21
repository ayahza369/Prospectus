#!/bin/bash
echo "FinWhisper — Starting services..."

# Activate the virtual environment
source .venv/bin/activate

echo "[1/2] Starting ChromaDB on port 8330..."
chroma run --path ./chroma_db --port 8330 &
CHROMA_PID=$!

# Cleanup when script is killed
trap "kill $CHROMA_PID" EXIT
