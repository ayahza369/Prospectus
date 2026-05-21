import os
import pytest
import chromadb

from src.ingest import filter_xbrl_noise, ingest_to_chromadb, query_collection

BASE = os.path.dirname(os.path.dirname(__file__))
CLEAN_DIR = os.path.join(BASE, "data", "clean")
VS_DIR = os.path.join(BASE, "data", "vectorstore")


# ── Slice 1: XBRL filter ────────────────────────────────────────────────────

def test_filter_removes_xbrl_keywords():
    noisy = "ix:nonFraction contextRef='Q1-2024' unitRef='USD'>1234</ix:nonFraction>"
    assert filter_xbrl_noise(noisy).strip() == ""


def test_filter_removes_numeric_heavy_lines():
    # >60% of chars are digits/punctuation
    noisy = "0001018724 12345 67890 99999 00000 11111"
    assert filter_xbrl_noise(noisy).strip() == ""


def test_filter_removes_raw_urls():
    noisy = "http://fasb.org/us-gaap/2025#PropertyPlantAndEquipment"
    assert filter_xbrl_noise(noisy).strip() == ""


def test_filter_preserves_prose():
    prose = "Net sales increased 9% year-over-year driven by AWS growth."
    assert filter_xbrl_noise(prose).strip() == prose


# ── Slice 2: Ingest into ChromaDB ───────────────────────────────────────────

@pytest.fixture(scope="module")
def collection():
    return ingest_to_chromadb(CLEAN_DIR, VS_DIR)


def test_collection_contains_all_companies(collection):
    companies = {"amazon", "tesla", "elililly", "berkshire"}
    for company in companies:
        results = collection.get(where={"company": company}, limit=1)
        assert len(results["ids"]) > 0, f"No chunks found for {company}"


def test_collection_chunks_have_content(collection):
    results = collection.get(limit=5, include=["documents", "metadatas"])
    for doc in results["documents"]:
        assert len(doc) > 50, f"Chunk too short: {repr(doc[:80])}"


# ── Slice 3: Query with company filter ──────────────────────────────────────

def test_query_returns_amazon_results_only(collection):
    results = query_collection(collection, "margins operating income", "amazon", n=3)
    assert len(results) == 3
    for r in results:
        assert r["company"] == "amazon"
        assert len(r["text"]) > 20
