"""
FinWhisper ingest — populates ChromaDB from data/clean/ text files.
Run AFTER starting ChromaDB:  chroma run --path ./chroma_db --port 8330
Usage: python ingest.py
"""

import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

COLLECTION = "prospectus_10k"
CHUNK_SIZE = 512
OVERLAP = 50
DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "clean")

COMPANIES = {
    "amazon":    "amazon.txt",
    "berkshire": "berkshire.txt",
    "elililly":  "elililly.txt",
    "tesla":     "tesla.txt",
}

client = chromadb.HttpClient(host="localhost", port=8330)
ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name=COLLECTION,
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"},
)


def chunk(text: str):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + CHUNK_SIZE]))
        i += CHUNK_SIZE - OVERLAP
    return chunks


def ingest(company: str, filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found")
        return
    text = open(path, encoding="utf-8").read()
    chunks = chunk(text)
    collection.upsert(
        documents=chunks,
        ids=[f"{company}_{i}" for i in range(len(chunks))],
        metadatas=[{"company": company} for _ in chunks],
    )
    print(f"  {company}: {len(chunks)} chunks ingested")


if __name__ == "__main__":
    print(f"Target collection: '{COLLECTION}' on localhost:8330")
    for company, fname in COMPANIES.items():
        ingest(company, fname)
    print(f"\nDone. Total chunks: {collection.count()}")
