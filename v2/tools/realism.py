"""Mechanical realism check of the prospective set: text features of the synthetic documents against real documents of
the same kind, on the text the system reads (extracted from the PDF).

    regulation units (R01-R50)   against the 13 real test regulations and the 20 distractors (full text)
    company units (K01-K30)      against the 6 real PKB texts available locally and the 14 synthetic policies (v1)

Features are densities per 1,000 characters (numbers, rupiah amounts, percentages, article and paragraph references,
table-like lines) and the share of documents carrying the formal parts of their kind. Writes
v2/work/analysis/realism.csv (one row per document) and realism.md (median and interquartile range per group).

    env\\Scripts\\python -m v2.tools.realism
"""
import csv
import re
import statistics

import v2.harness  # noqa: F401
from v2.harness import DATA, WORK

TEXTS = DATA / "13_teks"
UNITS = DATA / "15_set_prospektif" / "units"
OUT = WORK / "analysis"

NUMBER = re.compile(r"\d[\d.,]*")
RUPIAH = re.compile(r"Rp\s?\d")
PERCENT = re.compile(r"\d\s?%|persen")
ARTICLE = re.compile(r"\bPasal\s+\d+")
PARAGRAPH = re.compile(r"\bayat\s*\(\d+\)")
PARTS = {
    "regulation": {"menimbang": r"Menimbang", "mengingat": r"Mengingat", "menetapkan": r"Menetapkan|MEMUTUSKAN",
                   "ditetapkan": r"Ditetapkan di", "berlaku": r"mulai berlaku"},
    "company": {"bab": r"\bBAB\s+[IVXL]+", "pihak": r"(?i)pihak|pengusaha|serikat pekerja|pekerja/buruh",
                "berlaku": r"(?i)berlaku", "upah": r"(?i)\bupah\b"},
}


def features(text, kind):
    n = max(1, len(text)) / 1000
    lines = [x for x in text.splitlines() if x.strip()]
    table = sum(1 for x in lines if len(NUMBER.findall(x)) >= 3)
    row = {"chars": len(text), "numbers": len(NUMBER.findall(text)) / n, "rupiah": len(RUPIAH.findall(text)) / n,
           "percent": len(PERCENT.findall(text)) / n, "articles": len(ARTICLE.findall(text)) / n,
           "paragraphs": len(PARAGRAPH.findall(text)) / n, "table_lines": table / max(1, len(lines))}
    for name, pattern in PARTS[kind].items():
        row["has_" + name] = int(bool(re.search(pattern, text)))
    return row


def documents():
    roles = {r["id"]: r["role"] for r in csv.DictReader(open(TEXTS / "dokumen.csv", encoding="utf-8"))}
    for doc_id, role in roles.items():
        path = TEXTS / doc_id / "teks.txt"
        if not path.exists():
            continue
        if role in ("event", "distractor"):
            yield "regulation", f"nyata ({role})", doc_id, path.read_text(encoding="utf-8")
        elif role == "policy":
            yield "company", "nyata (PKB)", doc_id, path.read_text(encoding="utf-8")
        elif role == "policy_synthetic":
            yield "company", "sintetis v1 (SP)", doc_id, path.read_text(encoding="utf-8")
    for d in sorted(UNITS.iterdir()):
        path = d / "teks.txt"
        if path.exists():
            kind = "regulation" if d.name.startswith("R") else "company"
            yield kind, "prospektif", d.name, path.read_text(encoding="utf-8")


def iqr(values):
    if len(values) < 2:
        return f"{values[0]:.2f}" if values else "-"
    q = statistics.quantiles(values, n=4)
    return f"{statistics.median(values):.2f} [{q[0]:.2f}–{q[2]:.2f}]"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [dict(kind=k, group=g, doc=i, **features(t, k)) for k, g, i, t in documents()]
    keys = sorted({k for r in rows for k in r})
    with open(OUT / "realism.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    md = ["# Realisme mekanis set prospektif", "",
          "Median [kuartil 1–kuartil 3] per 1.000 karakter teks hasil ekstraksi; bagian formal = proporsi dokumen "
          "yang memuatnya.", ""]
    for kind in ("regulation", "company"):
        group_rows = [r for r in rows if r["kind"] == kind]
        groups = sorted({r["group"] for r in group_rows})
        dens = ["numbers", "rupiah", "percent", "articles", "paragraphs", "table_lines", "chars"]
        parts = ["has_" + p for p in PARTS[kind]]
        md += [f"## {'Regulasi' if kind == 'regulation' else 'Kebijakan perusahaan'}", "",
               "| Fitur | " + " | ".join(f"{g} (n={sum(1 for r in group_rows if r['group'] == g)})" for g in groups) + " |",
               "|---|" + "---|" * len(groups)]
        for k in dens:
            md.append(f"| {k} | " + " | ".join(iqr([r[k] for r in group_rows if r["group"] == g]) for g in groups) + " |")
        for k in parts:
            md.append(f"| {k} | " + " | ".join(
                f"{statistics.mean([r[k] for r in group_rows if r['group'] == g]):.2f}" for g in groups) + " |")
        md.append("")
    (OUT / "realism.md").write_text("\n".join(md), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    print(main(), "dokumen →", OUT / "realism.md")
