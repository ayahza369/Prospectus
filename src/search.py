import sys
import os
import re


_NOISE = re.compile(
    r"http[s]?://|ix:|xbrli:|iso4217:|utr:|us-gaap:|contextRef|unitRef|amzn:|fasb\.org",
    re.IGNORECASE,
)


def _is_noisy(paragraph: str) -> bool:
    lines = paragraph.splitlines()
    if not lines:
        return True
    noise_lines = sum(1 for l in lines if _NOISE.search(l))
    if noise_lines / len(lines) > 0.4:
        return True
    words = paragraph.split()
    if not words:
        return True
    numeric = sum(1 for w in words if re.fullmatch(r"[\d,.\-/:$%()]+", w))
    if numeric / len(words) > 0.6:
        return True
    # require at least one sentence-like chunk (capital letter + period)
    if not re.search(r"[A-Z][^.]{20,}\.", paragraph):
        return True
    return False


def load_paragraphs(company: str) -> list[tuple[str, str]]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "clean", f"{company}.txt")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if len(p.strip()) > 80]
    return [(p, company) for p in paragraphs if not _is_noisy(p)]


def score(paragraph: str, query_tokens: list[str]) -> float:
    lower = paragraph.lower()
    return sum(1 for t in query_tokens if t in lower)


def search(query: str, company: str | None = None, top_k: int = 3) -> list[dict]:
    companies = [company] if company else ["amazon", "berkshire", "elililly", "tesla"]
    query_tokens = query.lower().split()

    candidates = []
    for c in companies:
        try:
            for para, comp in load_paragraphs(c):
                s = score(para, query_tokens)
                if s > 0:
                    candidates.append({"score": s, "company": comp, "text": para})
        except FileNotFoundError:
            print(f"Warning: no file for company '{c}'", file=sys.stderr)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py <query> [company]")
        sys.exit(1)

    query = sys.argv[1]
    company = sys.argv[2].lower() if len(sys.argv) > 2 else None

    results = search(query, company)
    if not results:
        print("No results found.")
        sys.exit(0)

    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} | company={r['company']} | score={r['score']} ---")
        print(r["text"][:600])
