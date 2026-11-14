"""Locked document texts and quote matching (akuisisi.md 3.1 and gate G2).

Texts live in dataset/13_teks/<DOC>/teks.txt with page markers "=== PDF hlm. N ===". The same normalisation is used
when the gold is written and when G2 checks a candidate, so a quote that passes for the gold passes for the LLM too.
"""
import csv
import json
import re
from functools import lru_cache

from .config import REPO

TEXT_DIR = REPO / "dataset" / "13_teks"
PAGE_MARK = re.compile(r"^=== PDF hlm\. (\d+) ===$", re.M)

_QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "–": "-",
                         "—": "-", "−": "-", " ": " ", "­": ""})


def normalize(text):
    """Lower case, joined hyphenation, collapsed whitespace, unified quotes and dashes, numbers without inner
    spaces ("9. 559.600" -> "9.559.600"), "Rp 1" -> "rp1"."""
    t = text.translate(_QUOTES)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    t = t.lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(\d)\s*([.,])\s*(?=\d)", r"\1\2", t)
    t = re.sub(r"rp\.?\s+(?=\d)", "rp", t)
    t = re.sub(r"\s*%", "%", t)
    return t.strip()


@lru_cache(maxsize=None)
def registry():
    """Document registry: id -> row of dataset/13_teks/dokumen.csv."""
    path = TEXT_DIR / "dokumen.csv"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


@lru_cache(maxsize=None)
def pages(doc_id):
    """List of (page number, raw text) of a locked document."""
    path = TEXT_DIR / doc_id / "teks.txt"
    if not path.exists():
        raise FileNotFoundError(f"no locked text for document {doc_id}: {path}")
    raw = path.read_text(encoding="utf-8")
    parts = PAGE_MARK.split(raw)
    out = []
    if parts[0].strip():
        out.append((1, parts[0]))
    for i in range(1, len(parts), 2):
        out.append((int(parts[i]), parts[i + 1]))
    return out


@lru_cache(maxsize=None)
def normalized(doc_id):
    """Normalised full text and, for each page, the offset where it starts in that text."""
    chunks, starts, pos = [], [], 0
    for n, t in pages(doc_id):
        nt = normalize(t)
        starts.append((pos, n))
        chunks.append(nt)
        pos += len(nt) + 1
    return " ".join(chunks), starts


def find_quote(doc_id, quote):
    """Page number where the normalised quote occurs in the document, or None."""
    full, starts = normalized(doc_id)
    q = normalize(quote)
    if not q:
        return None
    i = full.find(q)
    if i < 0:
        return None
    page = starts[0][1]
    for s, n in starts:
        if s <= i:
            page = n
        else:
            break
    return page


@lru_cache(maxsize=None)
def segments(doc_id):
    path = TEXT_DIR / doc_id / "segmen.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
