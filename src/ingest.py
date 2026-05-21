import gc
import os
import re
import shutil
import uuid
from pathlib import Path

import chromadb
import tiktoken

CLEAN_DIR = Path("/Users/ritunjay/Desktop/Prospectus/data/clean")
VECTORSTORE_DIR = "/Users/ritunjay/Desktop/Prospectus/data/vectorstore"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 32
BATCH_SIZE = 32

_XBRL = re.compile(r"ix:nonFraction|contextRef|unitRef|https?://", re.IGNORECASE)


def filter_xbrl_noise(text):
    kept = []
    for line in text.splitlines():
        if _XBRL.search(line):
            continue
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        numeric = sum(1 for c in stripped if c.isdigit() or c in ".,;:-/")
        if numeric / len(stripped) > 0.60:
            continue
        kept.append(line)
    return "\n".join(kept)


def split_chunks(tokens, enc):
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


if __name__ == "__main__":
    # Wipe stale vectorstore so we get a clean re-ingest
    if os.path.exists(VECTORSTORE_DIR):
        shutil.rmtree(VECTORSTORE_DIR)
    os.makedirs(VECTORSTORE_DIR)

    client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    collection = client.get_or_create_collection(
        name="sec_filings",
        metadata={"hnsw:space": "cosine"},
    )

    enc = tiktoken.get_encoding("cl100k_base")

    for txt_file in sorted(CLEAN_DIR.glob("*.txt")):
        company = txt_file.stem
        print(f"\nIngesting {company}...")

        text = filter_xbrl_noise(txt_file.read_text(encoding="utf-8"))
        tokens = enc.encode(text)
        chunks = split_chunks(tokens, enc)
        print(f"  {len(tokens):,} tokens → {len(chunks)} chunks")

        ids, docs, metas = [], [], []
        batches_sent = 0
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
            ids.append(str(uuid.uuid4()))
            docs.append(chunk)
            metas.append({"company": company})

            if len(ids) == BATCH_SIZE:
                collection.add(ids=ids, documents=docs, metadatas=metas)
                ids, docs, metas = [], [], []
                batches_sent += 1

        if ids:
            collection.add(ids=ids, documents=docs, metadatas=metas)
            batches_sent += 1

        print(f"  Sent {batches_sent} batch(es)")
        del text, tokens, chunks
        gc.collect()

    print(f"\nTotal docs in collection: {collection.count()}")

    # Test query
    print("\n--- Test query: 'What did management say about margins?' (amazon) ---")
    results = collection.query(
        query_texts=["What did management say about margins?"],
        n_results=3,
        where={"company": "amazon"},
        include=["documents", "metadatas", "distances"],
    )
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ), 1):
        print(f"\nResult {i} | company={meta['company']} | score={round(1 - dist, 4)}")
        print(doc[:400])
