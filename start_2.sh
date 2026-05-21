#!/bin/bash
echo "FinWhisper — Starting services..."

# Activate the virtual environment
source .venv/bin/activate

echo "[2/2] Starting FinWhisper API on port 8000..."
python server.py