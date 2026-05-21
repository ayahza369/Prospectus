import os
import pytest
from src.extractor import extract_html_to_text, extract_mhtml_to_text

BASE = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE, "data", "clean")
HTML_DIR = BASE  # HTML files live at project root (Desktop/Prospectus/)

CASES = [
    ("Amazon.html", "amazon.txt"),
    ("Tesla.html", "tesla.txt"),
    ("Berkshire.html", "berkshire.txt"),
]


@pytest.mark.parametrize("html_file,txt_file", CASES)
def test_extraction_produces_readable_text(html_file, txt_file):
    html_path = os.path.join(HTML_DIR, html_file)
    out_path = os.path.join(RAW_DIR, txt_file)

    extract_html_to_text(html_path, out_path)

    assert os.path.exists(out_path), f"{txt_file} was not created"
    content = open(out_path).read()
    assert len(content) > 0, f"{txt_file} is empty"
    # first non-whitespace character should be alphanumeric (no raw HTML tags)
    stripped = content.strip()
    assert stripped[0].isalnum() or stripped[0] in ('"', "'", "("), (
        f"{txt_file} starts with suspicious char: {repr(stripped[:20])}"
    )


@pytest.mark.parametrize("html_file,txt_file", [
    ("Amazon.html", "amazon.txt"),
    ("Tesla.html", "tesla.txt"),
    ("Berkshire.html", "berkshire.txt"),
])
def test_large_files_exceed_50kb(html_file, txt_file):
    out_path = os.path.join(RAW_DIR, txt_file)
    size_kb = os.path.getsize(out_path) / 1024
    assert size_kb > 50, f"{txt_file} is only {size_kb:.1f}KB — expected >50KB"


def test_mhtml_extraction_produces_readable_text():
    mhtml_path = os.path.join(HTML_DIR, "eli.mhtml")
    out_path = os.path.join(RAW_DIR, "elililly.txt")

    extract_mhtml_to_text(mhtml_path, out_path)

    assert os.path.exists(out_path), "elililly.txt was not created"
    content = open(out_path).read()
    stripped = content.strip()
    assert len(stripped) > 0, "elililly.txt is empty"
    assert stripped[0].isalnum() or stripped[0] in ('"', "'", "("), (
        f"elililly.txt starts with suspicious char: {repr(stripped[:20])}"
    )


def test_mhtml_elililly_exceeds_50kb():
    out_path = os.path.join(RAW_DIR, "elililly.txt")
    size_kb = os.path.getsize(out_path) / 1024
    assert size_kb > 50, f"elililly.txt is only {size_kb:.1f}KB — expected >50KB"
