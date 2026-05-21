"""Run after server is up: python test_query.py"""
import requests

BASE = "http://localhost:8000"

tests = [
    "/ask Amazon What did management say about AWS growth and cloud profitability?",
    "/compare Tesla Berkshire How did each company describe risk factors related to competition?",
    "/ask Tesla What are the top risk factors Tesla disclosed related to competition?",
    "/stats Eli Lilly",
    "/ask Berkshire What did Buffett say about capital allocation or investment strategy?",
]

for q in tests:
    print(f"\nQ: {q}")
    r = requests.post(f"{BASE}/query", json={"message": {"text": q}})
    print(f"A: {r.json().get('reply', r.text)[:300]}")
