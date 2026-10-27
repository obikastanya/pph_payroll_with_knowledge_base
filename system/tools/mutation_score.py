"""Delta-focused mutation score per event on S^E (PANDUAN Tahap 8).

    env\\Scripts\\python system\\tools\\mutation_score.py [--events E01,E02] [--write]

For each test event with a non-empty gold Delta: every single-element mutant of Delta*_n is applied to the chain
before the event and evaluated on the event's S^E tuples (dataset/14_ruang_uji/harapan/<EVENT>.jsonl.gz), stopping at
the first difference. Writes docs/hasil/mutasi.csv (one row per mutant) and prints the score per event and operator.
"""
import argparse
import csv
import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.mutation import killed, mutants_of  # noqa: E402

SE = ROOT / "dataset" / "14_ruang_uji"


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default="")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--set", choices=["test", "dev"], default="test")
    args = ap.parse_args()
    root = SE if args.set == "test" else SE / "pengembangan"
    cases = {c["case_id"]: c for c in load_gz(root / "kasus.jsonl.gz")}
    chain = build_gold.load_graph()
    ids = [u.update_id for u in chain.updates]
    wanted = set(filter(None, args.events.split(",")))
    rows = []
    for u in build_gold.collect():
        if u.kind != "event" or (wanted and u.event_id not in wanted):
            continue
        path = root / "harapan" / f"{u.event_id}.jsonl.gz"
        if not path.exists():
            continue
        d = u.to_json()
        if not (d["add"] or d["change"]):
            continue
        base = chain.until(ids[ids.index(u.delta_id) - 1])
        tuples = load_gz(path)
        t0 = time.time()
        for m in mutants_of(d):
            status, where = killed(base, m, tuples, cases)
            rows.append({"event": u.event_id, "element": m.element, "operator": m.operator, "detail": m.detail,
                         "status": status, "detected_by": where})
        ev_rows = [r for r in rows if r["event"] == u.event_id and r["status"] != "stillborn"]
        k = sum(r["status"] == "killed" for r in ev_rows)
        print(f"{u.event_id}: {k}/{len(ev_rows)} killed ({time.time() - t0:.0f}s)", flush=True)
    by_op = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["status"] == "stillborn":
            continue
        by_op[r["operator"]][1] += 1
        by_op[r["operator"]][0] += r["status"] == "killed"
    total = sum(v[1] for v in by_op.values())
    kills = sum(v[0] for v in by_op.values())
    print(f"overall: {kills}/{total} = {kills / total:.3f}" if total else "no mutants")
    for op, (k, n) in sorted(by_op.items()):
        print(f"  {op:15s} {k}/{n}")
    print("survivors:")
    for r in rows:
        if r["status"] == "survived":
            print(f"  {r['event']} {r['element']} {r['operator']} ({r['detail']})")
    if args.write and rows:
        out = ROOT / "docs" / "hasil" / ("mutasi.csv" if args.set == "test" else "mutasi_pengembangan.csv")
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
