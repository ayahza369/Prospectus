import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from search import search

STATS = {
    "amazon": (
        "Amazon Q1 2026: Net sales $181.5B (+17% YoY), operating income $23.9B, net income $30.3B.\n"
        "AWS grew 28% YoY to $37.6B, driving margin expansion across the business.\n"
        "Key risk: tariff policy changes and geopolitical events affecting global supply chains and cross-border operations."
    ),
    "tesla": (
        "Tesla 2025 annual revenue approximately $97B; Q1 2026 results pending full filing.\n"
        "Net income under pressure from pricing cuts and rising competition in the EV market.\n"
        "Key risk: intensifying global EV competition and Elon Musk's divided attention across multiple ventures."
    ),
    "berkshire": (
        "Berkshire Hathaway Q1 2026: Total assets ~$1.18T; net earnings decreased $69M vs Q1 2025.\n"
        "Insurance underwriting and railroad (BNSF) remain core earnings drivers alongside a $288B equity portfolio.\n"
        "Key risk: catastrophe losses from insurance subsidiaries and volatility in equity investment valuations."
    ),
    "elililly": (
        "Eli Lilly Q1 2026: Revenue $19.8B (+56% YoY), net income $7.4B, driven by Mounjaro and Zepbound volume growth.\n"
        "Zepbound U.S. revenue grew 79%; Mounjaro added to China NRDL, expanding international reach.\n"
        "Key risk: continued pricing pressure from government drug pricing actions and IRA implementation."
    ),
}

HELP = (
    "Available commands:\n"
    "  /ask [COMPANY] [question]          search a company's filings\n"
    "  /compare [COMPANY1] [COMPANY2] [question]  compare two companies on a query\n"
    "  /stats [COMPANY]                   show key financial summary\n"
    "\n"
    "Supported companies: amazon, tesla, berkshire, elililly\n"
    "Example: /ask amazon What did management say about AWS growth?"
)


def cmd_ask(parts: list[str]) -> str:
    if len(parts) < 3:
        return "Usage: /ask [COMPANY] [question]"
    company = parts[1].lower()
    query = " ".join(parts[2:])
    results = search(query, company)
    if not results:
        return f"No results found for '{query}' in {company}."
    lines = [f"Top results for '{query}' in {company}:\n"]
    for i, r in enumerate(results, 1):
        excerpt = r["text"][:400].replace("\n", " ").strip()
        lines.append(f"[{i}] (score {r['score']}) {excerpt}")
    return "\n".join(lines)


def cmd_compare(parts: list[str]) -> str:
    if len(parts) < 4:
        return "Usage: /compare [COMPANY1] [COMPANY2] [question]"
    c1, c2 = parts[1].lower(), parts[2].lower()
    query = " ".join(parts[3:])
    lines = [f"Comparing '{query}': {c1} vs {c2}\n"]
    for company in (c1, c2):
        results = search(query, company)
        lines.append(f"-- {company.upper()} --")
        if not results:
            lines.append("  No results found.")
        else:
            excerpt = results[0]["text"][:350].replace("\n", " ").strip()
            lines.append(f"  {excerpt}")
        lines.append("")
    return "\n".join(lines).rstrip()


def cmd_stats(parts: list[str]) -> str:
    if len(parts) < 2:
        return "Usage: /stats [COMPANY]"
    company = parts[1].lower()
    if company not in STATS:
        known = ", ".join(STATS.keys())
        return f"Unknown company '{company}'. Known: {known}"
    return STATS[company]


def route(line: str) -> str:
    line = line.strip()
    if not line.startswith("/"):
        return HELP
    parts = line.split()
    cmd = parts[0].lower()
    if cmd == "/ask":
        return cmd_ask(parts)
    if cmd == "/compare":
        return cmd_compare(parts)
    if cmd == "/stats":
        return cmd_stats(parts)
    return f"Unknown command '{cmd}'.\n\n" + HELP


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(route(" ".join(sys.argv[1:])))
    else:
        print("Interactive mode. Type a command or 'quit' to exit.")
        for line in sys.stdin:
            line = line.strip()
            if line.lower() in ("quit", "exit"):
                break
            print(route(line))
            print()
