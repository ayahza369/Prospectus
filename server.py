"""
FinWhisper FastAPI server — mirrors the RocketRide pipeline for local testing.
Pipeline: HTTP POST /query -> ChromaDB retrieve -> Claude -> JSON reply
"""

import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import anthropic

app = FastAPI(title="FinWhisper")

COLLECTION = "prospectus_10k"
TOP_K = 5

ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma = chromadb.HttpClient(host="localhost", port=8330)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are FinWhisper, a financial research assistant that answers questions strictly using SEC 10-K filing excerpts provided as context.

RULES:
1. Answer ONLY from the context passages provided. Never use outside knowledge.
2. Every answer must cite its source: include the company name and a short phrase from the passage.
3. If the context does not contain the answer, reply exactly: "I don't have that information in the filings I've indexed. Try /stats [COMPANY] for a summary."
4. Format for iMessage — plain text only. No markdown. No asterisks. No # headers. No bold syntax.
5. Use CAPITAL LETTERS for emphasis. Use bullet marks (•) not hyphens. Max 3 sentences per paragraph.
6. Keep responses under 250 words. Be direct.

RESPONSE FORMAT:
[Your answer in plain text]

Source: [Company name] 10-K — "[short quoted phrase from the passage]"

SLASH COMMANDS:
/ask [company] [question] — answer from that company's filings only
/compare [co1] [co2] [topic] — compare both companies on the topic, cite both
/stats [company] — return the pre-built key metrics summary for that company

Indexed companies: Amazon, Berkshire Hathaway, Eli Lilly, Tesla."""

STATS = {
    "amazon":    "Amazon (AMZN) Key Metrics • Revenue: $575B • AWS revenue: $91B (growing 17% YoY) • Operating income: $36.9B • Net income: $30.4B • Free cash flow: $35B",
    "berkshire": "Berkshire Hathaway (BRK) Key Metrics • Total revenues: $364B • Operating earnings: $37.4B • Insurance float: $169B • Cash & equivalents: $167B • Book value per share growing ~18% annually",
    "elililly":  "Eli Lilly (LLY) Key Metrics • Revenue: $34.1B • Net income: $5.8B • Gross margin: ~79% • Mounjaro/Zepbound driving GLP-1 growth • R&D spend: $9B",
    "tesla":     "Tesla (TSLA) Key Metrics • Revenue: $97B • Gross margin: ~18% • Net income: $7.1B • Vehicle deliveries: 1.8M • Energy generation & storage growing 54% YoY",
}

TICKER_MAP = {
    "amazon": "amazon", "amzn": "amazon",
    "berkshire": "berkshire", "brk": "berkshire", "berkshirehathaway": "berkshire",
    "elililly": "elililly", "eli": "elililly", "lilly": "elililly", "lly": "elililly",
    "tesla": "tesla", "tsla": "tesla",
}


class QueryRequest(BaseModel):
    message: dict


def parse_command(text: str):
    text = text.strip()
    if text.startswith("/stats "):
        co = TICKER_MAP.get(text[7:].strip().lower().replace(" ", ""), text[7:].strip().lower())
        return "stats", co, None, None
    if text.startswith("/ask "):
        parts = text[5:].split(" ", 1)
        if len(parts) == 2:
            co = TICKER_MAP.get(parts[0].lower(), parts[0].lower())
            return "ask", co, parts[1], None
    if text.startswith("/compare "):
        parts = text[9:].split(" ", 2)
        if len(parts) == 3:
            c1 = TICKER_MAP.get(parts[0].lower(), parts[0].lower())
            c2 = TICKER_MAP.get(parts[1].lower(), parts[1].lower())
            return "compare", c1, parts[2], c2
    return "ask", None, text, None


def retrieve(query: str, company: str = None, k: int = TOP_K) -> str:
    col = chroma.get_collection(COLLECTION, embedding_function=ef)
    where = {"company": company} if company else None
    results = col.query(query_texts=[query], n_results=k, where=where)
    docs = results["documents"][0] if results["documents"] else []
    return "\n\n---\n\n".join(docs) if docs else ""


def ask_claude(context: str, question: str) -> str:
    resp = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return resp.content[0].text


@app.post("/query")
async def query(req: QueryRequest):
    text = req.message.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="message.text required")

    cmd, company, question, company2 = parse_command(text)

    if cmd == "stats":
        return {"reply": STATS.get(company, f"No stats available for {company}.")}

    if cmd == "compare" and company2:
        ctx = f"[{company.upper()} filings]\n{retrieve(question, company)}\n\n[{company2.upper()} filings]\n{retrieve(question, company2)}"
        return {"reply": ask_claude(ctx, f"Compare {company} and {company2}: {question}")}

    ctx = retrieve(question, company)
    if not ctx:
        return {"reply": "I don't have that information in the filings I've indexed. Try /stats [COMPANY] for a summary."}
    return {"reply": ask_claude(ctx, question)}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
