@echo off
echo FinWhisper — Starting services...
echo.

echo [1/2] Starting ChromaDB on port 8330...
start "ChromaDB" cmd /k "chroma run --path ./chroma_db --port 8330"

timeout /t 4 /nobreak >nul

echo [2/2] Starting FinWhisper API on port 8000...
python server.py
