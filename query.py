import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

def get_index():
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection("prospectus")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )
    return index

def query(question, company=None):
    index = get_index()
    engine = index.as_query_engine(similarity_top_k=5)
    if company:
        question = f"Regarding {company} only: {question}"
    response = engine.query(question)
    sources = []
    for node in response.source_nodes:
        sources.append({
            "company": node.metadata.get("file_name", "Unknown"),
            "score": round(node.score, 3) if node.score else "N/A",
            "snippet": node.text[:150]
        })
    return {
        "answer": str(response),
        "sources": sources
    }

if __name__ == "__main__":
    result = query("What are Tesla's biggest risk factors?", company="Tesla")
    print("ANSWER:", result["answer"])
    print("SOURCES:", result["sources"])