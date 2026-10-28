r"""Sample of elements for labelling quote accuracy (PANDUAN Tahap 15: "beri label ketepatan kutipan pada sampel unsur").

    env\Scripts\python system\tools\quote_sample.py [--n 50] [--runs e2-regulasi,...]

From the selected updates of the given runs (regulation documents only, so that no collective agreement text is copied
into the review folder), every added or changed element with its quotes is listed, and a seeded sample of N elements is
written to review/kutipan/sampel.csv for an independent labeller: does each quote support the element (the right
provision, the stated value or condition, the validity dates)? Labels go to review/kutipan/label.csv
(mendukung | sebagian | tidak_mendukung) with a reason; system/tools/quote_sample.py --summary tallies them into
docs/hasil/ketepatan_kutipan.json.
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

from pph21kbs.analysis import stats  # noqa: E402

OUT = ROOT / "review" / "kutipan"


def elements(runs):
    for run in runs:
        for p in sorted((ROOT / "experiments" / run / "results").glob("*.json")):
            r = json.loads(p.read_text(encoding="utf-8"))
            d = r.get("delta")
            if r.get("status") != "applied" or not d or str(r["event"]).startswith("PKB"):
                continue
            for e in d.get("add", []) + d.get("change", []):
                content = e.get("expression") or e.get("value") or e.get("assertion") or e.get("rows_ref") or ""
                if e.get("kind") == "table" and e.get("rows"):
                    content = f"{len(e['rows'])} rows, first: {json.dumps(e['rows'][0], ensure_ascii=False)}"
                yield {"run": run, "event": r["event"], "element": e["id"], "kind": e["kind"],
                       "content": str(content)[:300], "condition": e.get("condition") or "",
                       "valid_from": e.get("valid_from") or "", "valid_until": e.get("valid_until") or "",
                       "quotes": " || ".join(f"[{q.get('document')} {q.get('provision')} hlm. {q.get('page')}] "
                                             f"{q.get('quote')}" for q in e.get("source") or [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--runs", default="e2-regulasi")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.summary:
        rows = list(csv.DictReader(open(OUT / "label.csv", encoding="utf-8")))
        c = Counter(r["label"] for r in rows)
        n = len(rows)
        out = {"n": n, "labels": dict(c), "supported_rate": c["mendukung"] / n,
               "supported_CI": stats.clopper_pearson(c["mendukung"], n)}
        (ROOT / "docs" / "hasil" / "ketepatan_kutipan.json").write_text(json.dumps(out, indent=1) + "\n",
                                                                       encoding="utf-8")
        print(json.dumps(out, indent=1))
        return
    pool = list(elements(args.runs.split(",")))
    sample = random.Random(20261028).sample(pool, min(args.n, len(pool)))
    with open(OUT / "sampel.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(sample[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sample)
    print(f"{len(sample)} of {len(pool)} elements written to {(OUT / 'sampel.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
