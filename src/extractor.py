import email
import quopri
import re
from pathlib import Path
from bs4 import BeautifulSoup


def extract_html_to_text(html_path: str, output_path: str) -> str:
    html = Path(html_path).read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "meta", "link", "head"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # collapse runs of blank lines and strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

    Path(output_path).write_text(cleaned, encoding="utf-8")
    return cleaned


def extract_mhtml_to_text(mhtml_path: str, output_path: str) -> str:
    raw = Path(mhtml_path).read_bytes()
    msg = email.message_from_bytes(raw)

    html_parts = []
    for part in msg.walk():
        if part.get_content_type() != "text/html":
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            # decode=False returns a string — try quoted-printable manually
            raw_str = part.get_payload(decode=False)
            encoding = part.get("Content-Transfer-Encoding", "").lower()
            if encoding == "quoted-printable":
                payload = quopri.decodestring(raw_str.encode()).decode("utf-8", errors="replace")
            else:
                payload = raw_str
        else:
            charset = part.get_content_charset() or "utf-8"
            payload = payload.decode(charset, errors="replace")
        html_parts.append(payload)

    combined_html = "\n".join(html_parts)
    soup = BeautifulSoup(combined_html, "lxml")

    for tag in soup(["script", "style", "meta", "link", "head"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

    Path(output_path).write_text(cleaned, encoding="utf-8")
    return cleaned
