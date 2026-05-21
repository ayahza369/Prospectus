import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pathlib import Path

COLLECTION = "prospectus_10k"
ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

COMPANY_MAP = {
    "amazon": "amazon",
    "berkshire": "berkshire",
    "elililly": "elililly",
    "tesla": "tesla",
}

def chunk_text(text, chunk_size=512, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def index_company(client, company_key, file_path):
    col = client.get_or_create_collection(COLLECTION, embedding_function=ef)
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    chunks = chunk_text(text)
    ids = [f"{company_key}_{i}" for i in range(len(chunks))]
    metadatas = [{"company": company_key} for _ in chunks]
    col.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"Indexed {len(chunks)} chunks for {company_key}")

if __name__ == "__main__":
    client = chromadb.HttpClient(host="localhost", port=8330)
    index_company(client, "tesla", "data/clean/Tesla.txt")
    index_company(client, "elililly", "data/clean/EliLilly.txt")
    # add these when Person B delivers them:
    index_company(client, "amazon", "data/clean/Amazon.txt")
    index_company(client, "berkshire", "data/clean/Berkshire.txt")
