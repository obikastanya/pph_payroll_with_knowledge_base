"""Extract the KLU annex lists of the COVID-19 PPh 21 DTP regulations (development events D05-D07, D10, D11) from the
locked texts into dataset/13_teks/<DOC>/tabel/LAMPIRAN-A.csv (columns klu, uraian, halaman_pdf).

    env\\Scripts\\python system\\tools\\extract_klu_covid.py [--write]

A row is a line whose five-digit KLU code is followed by an upper-case description, after at most two short OCR
tokens (row numbers read as "61 i", "108(')" or "4841"). Expected counts (peristiwa.csv): 440, 1.062, 1.189, 1.189,
1.189. Line ranges are the Lampiran huruf A of each document, from its header to the next lettered annex.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT = ROOT / "dataset" / "13_teks"
SPEC = {  # document: (first line, end line) of Lampiran A, 1-based
    "PMK-23-PMK-03-2020": (567, 1114, 440),
    "PMK-44-PMK-03-2020": (877, 2253, 1062),
    "PMK-86-PMK-03-2020": (923, 2465, 1189),
    "PMK-9-PMK-03-2021": (1312, 2850, 1189),
    "PMK-82-PMK-03-2021": (375, 1870, 1189),
}
ROW = re.compile(r"^\W*(?:\S{1,6}\s+){0,2}(\d{5})\s+([A-Z][A-Z].*)$")
PAGE = re.compile(r"=== PDF hlm\. (\d+) ===")


def extract(doc, first, end):
    lines = (TEXT / doc / "teks.txt").read_text(encoding="utf-8").splitlines()
    page = next(int(m.group(1)) for line in reversed(lines[:first]) if (m := PAGE.match(line)))
    rows, last = [], None
    for line in lines[first - 1:end - 1]:
        m = PAGE.match(line)
        if m:
            page = int(m.group(1))
            continue
        m = ROW.match(line)
        if m:
            last = {"klu": m.group(1), "uraian": m.group(2).strip(), "halaman_pdf": page}
            rows.append(last)
        elif last and line.strip().isupper() and not line.startswith("NO.") and "jdih" not in line:
            last["uraian"] += " " + line.strip()
    return rows


def main(write=False):
    for doc, (first, end, expected) in SPEC.items():
        rows = extract(doc, first, end)
        dup = len(rows) - len({r["klu"] for r in rows})
        print(f"{doc}: {len(rows)} codes (expected {expected}), duplicates {dup}")
        if len(rows) != expected or dup:
            sys.exit(f"{doc}: count mismatch")
        if write:
            (TEXT / doc / "tabel").mkdir(exist_ok=True)
            with open(TEXT / doc / "tabel" / "LAMPIRAN-A.csv", "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, ["klu", "uraian", "halaman_pdf"], lineterminator="\n")
                w.writeheader()
                w.writerows(rows)


if __name__ == "__main__":
    main("--write" in sys.argv)
