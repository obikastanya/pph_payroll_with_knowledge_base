"""Segment selection (akuisisi.md 3.1): lexical scores from the domain lexicon, opening and closing always kept,
annexes that have an extracted table shown as a table description instead of their text."""
import csv
import re
from dataclasses import dataclass

from ..text import TEXT_DIR, normalize, segments

FIXED_TERMS = ("pasal 21", "pegawai tetap", "penghasilan bruto", "tarif", "dibulatkan", "iuran", "upah",
               "ditanggung pemerintah", "masa pajak", "penghasilan tidak kena pajak", "biaya jabatan",
               "pemotongan", "tunjangan", "natura", "batas", "berlaku", "dicabut", "tidak berlaku", "pembulatan",
               "klasifikasi lapangan usaha", "insentif")
TOKEN_BUDGET = 14000
ALWAYS_CAP = 3000          # opening and closing segments longer than this are truncated


def tokens(text):
    """Rough token count for Indonesian legal text (about 3.5 characters per token)."""
    return int(len(text) / 3.5) + 1


@dataclass
class Selection:
    document: str
    segments: list          # dicts of segmen.json, in document order, text possibly replaced for annexes
    tables: list            # descriptions of extracted tables of the document
    dropped: list           # ids of segments left out
    tokens: int


def lexicon(view):
    terms = set(FIXED_TERMS)
    for r in view.records:
        lab = getattr(r, "label_id", "") or ""
        lab = normalize(lab)
        if len(lab) >= 5:
            terms.add(lab)
    return sorted(terms)


def extracted_tables(doc_id):
    out = []
    d = TEXT_DIR / doc_id / "tabel"
    for p in sorted(d.glob("*.csv")) if d.exists() else []:
        with open(p, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        out.append({"id": f"{doc_id}/{p.stem}", "columns": list(rows[0]) if rows else [], "rows": len(rows),
                    "sample": rows[:6]})
    return out


def _table_text(t):
    lines = [f"[Extracted table {t['id']}: {t['rows']} rows; columns {', '.join(t['columns'])}. "
             f"Refer to it with rows_ref; do not copy rows. First rows:]"]
    for r in t["sample"]:
        lines.append("  " + "; ".join(f"{k}={v}" for k, v in r.items()))
    return "\n".join(lines)


def select(doc_id, view, budget=TOKEN_BUDGET):
    segs = segments(doc_id)
    if not segs:
        raise ValueError(f"document {doc_id} has no segments (dataset/13_teks/{doc_id}/segmen.json)")
    tables = extracted_tables(doc_id)
    terms = lexicon(view)
    scored = []
    for i, s in enumerate(segs):
        text = s["text"]
        if s["kind"] == "annex" and tables:
            text = "\n".join(_table_text(t) for t in tables)
        nt = normalize(text)
        score = sum(len(re.findall(re.escape(t), nt)) for t in terms)
        scored.append((i, dict(s, text=text), score))
    for i, s, score in scored:
        if s["kind"] in ("opening", "closing") and tokens(s["text"]) > ALWAYS_CAP:
            s["text"] = s["text"][: int(ALWAYS_CAP * 3.5)] + "\n[... truncated]"
    keep = {i for i, s, _ in scored if s["kind"] in ("opening", "closing")}
    keep |= {i for i, s, _ in scored if s["kind"] == "annex" and tables}
    used = sum(tokens(scored[i][1]["text"]) for i in keep)
    # density (matches per square root of length), so that long definition articles do not crowd out short
    # substantive ones; segments without a match come last but are still taken while the budget allows
    order = sorted(scored, key=lambda t: (-(t[2] / tokens(t[1]["text"]) ** 0.5), t[0]))
    for i, s, score in order:
        if i in keep:
            continue
        n = tokens(s["text"])
        if used + n <= budget:
            keep.add(i)
            used += n
    chosen = [s for i, s, _ in scored if i in keep]
    dropped = [s["id"] for i, s, _ in scored if i not in keep]
    return Selection(doc_id, chosen, tables, dropped, used)


def render(selection):
    parts = [f"=== DOCUMENT {selection.document} ==="]
    for s in selection.segments:
        pages = f" (PDF pages {s.get('page_start')}-{s.get('page_end')})" if s.get("page_start") else ""
        parts.append(f"--- {s['id']}{pages} ---\n{s['text'].strip()}")
    if selection.dropped:
        parts.append(f"[segments not shown: {', '.join(selection.dropped)}]")
    return "\n\n".join(parts)
