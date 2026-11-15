"""Import the locked texts of v2/dataset/13_teks into the workspace of system_final, through the system's own
ingestion (documents.add_document), so every experiment reads documents exactly as the system would after an upload.

    env\\Scripts\\python -m v2.harness.workspace            # import all documents and check the gold quotes
"""
import csv
import json
import shutil

from . import DATA, WORK

from pph21kbs import documents  # noqa: E402

TEXTS = DATA / "13_teks"
SHORT = DATA / "13_teks_pengecoh_ringkas"
GOLD = DATA / "12_emas"
FULL_SUFFIX = "-UTUH"         # the full text of a distractor; the plain id holds its short version (the main measure)
COMPANY_ROLES = {"policy", "policy_dev", "policy_synthetic"}


def registry():
    return list(csv.DictReader(open(TEXTS / "dokumen.csv", encoding="utf-8")))


def import_one(row):
    src = TEXTS / row["id"]
    company = row["role"] in COMPANY_ROLES or row["id"].startswith(("PKB-", "SP"))
    full = (src / "teks.txt").read_text(encoding="utf-8").replace("=== PDF hlm. ", "=== page ")
    if row["role"] == "distractor":
        documents.add_document(row["id"] + FULL_SUFFIX, row["title"], row["issued"], text=full)
        full = (SHORT / row["id"] / "teks.txt").read_text(encoding="utf-8").replace("=== PDF hlm. ", "=== page ")
    raw = full
    d = documents.add_document(row["id"], row["title"], row["issued"], text=raw, company=company)
    if (src / "tabel").exists():
        (d / "tables").mkdir(exist_ok=True)
        for t in (src / "tabel").glob("*.csv"):
            shutil.copyfile(t, d / "tables" / t.name)
    return len(raw), len((d / "text.txt").read_text(encoding="utf-8"))


def import_prospective(unit_id):
    """A prospective unit's extracted text (render.py) into the workspace, through the same ingestion."""
    from .prospective import UNITS
    folder = UNITS / unit_id
    spec = json.loads((folder / "spec.json").read_text(encoding="utf-8"))
    raw = (folder / "teks.txt").read_text(encoding="utf-8").replace("=== PDF hlm. ", "=== page ")
    documents.add_document(unit_id, spec["title"], spec["issued"], text=raw, company=spec["layer"] == "company")


def quotes(delta):
    for op in ("add", "change"):
        for rec in delta.get(op, []):
            for s in rec.get("source", []) or []:
                if s.get("quote"):
                    yield s["document"], s["quote"]


def check_gold_quotes():
    """Every quote of every gold update must still be found in the cleaned text."""
    known = {r["id"] for r in registry()}
    missing, total = [], 0
    for f in sorted((GOLD / "delta").glob("*.json")):
        for doc, q in quotes(json.loads(f.read_text(encoding="utf-8"))):
            if doc not in known:
                continue
            total += 1
            if documents.find_quote(doc, q) is None:
                missing.append((f.stem, doc, q[:80]))
    return total, missing


def main():
    WORK.mkdir(exist_ok=True)
    before = after = 0
    rows = registry()
    for row in rows:
        b, a = import_one(row)
        before, after = before + b, after + a
    documents.clear_caches()
    print(f"{len(rows)} documents: {before:,} -> {after:,} characters ({1 - after / before:.1%} removed)")
    total, missing = check_gold_quotes()
    print(f"gold quotes found: {total - len(missing)}/{total}")
    for m in missing:
        print("  MISSING", m)


if __name__ == "__main__":
    main()
