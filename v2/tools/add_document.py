"""Add one document to the locked text store v2/dataset/13_teks with the extractor and segmenter used for every other
document (v1/system/tools/build_texts.py), so its text, segments, and manifest have the same format.

    env\\Scripts\\python v2\\tools\\add_document.py PKB-CENTEX-2021 2021-01-08 policy \\
        "PKB PT Century Textile Industry 2021-2023" 10_kebijakan_perusahaan/dokumen/PKB_Century_Textile_2021_2023.html
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "v2" / "dataset"
OUT = DATA / "13_teks"

spec = importlib.util.spec_from_file_location("build_texts", ROOT / "v1" / "system" / "tools" / "build_texts.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
bt.DATA = DATA


def add(doc_id, issued, role, title, files, event=""):
    row = {"id": doc_id, "files": files}
    text, _ = bt.extract(row, engine="pdfplumber")
    folder = OUT / doc_id
    folder.mkdir(exist_ok=True)
    (folder / "teks.txt").write_text(text, encoding="utf-8")
    (folder / "segmen.json").write_text(
        json.dumps(bt.segment(text, doc_id.startswith("PKB-")), ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"{bt.sha(DATA / f)}  sumber:{f}" for f in files.split(";") if f]
    lines.append(f"{bt.sha(folder / 'teks.txt')}  teks.txt")
    (folder / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    registry = OUT / "dokumen.csv"
    rows = list(csv.DictReader(open(registry, encoding="utf-8")))
    rows = [r for r in rows if r["id"] != doc_id] + [
        {"id": doc_id, "event": event, "role": role, "issued": issued, "title": title, "files": files}]
    with open(registry, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "event", "role", "issued", "title", "files"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(doc_id, len(text), "chars,", len(json.loads((folder / "segmen.json").read_text(encoding="utf-8"))), "segments")


if __name__ == "__main__":
    add(*sys.argv[1:6])
