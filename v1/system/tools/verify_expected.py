"""Recompute every locked expectation of the test space with the current engine and compare it row by row.

    env\\Scripts\\python system\\tools\\verify_expected.py [--workers 8] [--only E06,SP14]

dataset/14_ruang_uji/harapan/<EVENT or POLICY>.jsonl.gz holds the observations of the locked gold on the test cases
(build_se.py). A change of the engine after the freeze (engine-v1) must leave all of them identical; this tool shows
whether it does, and where not. Nothing is written except the report printed at the end.
"""
import argparse
import gzip
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

OUT = ROOT / "dataset" / "14_ruang_uji"
_CHAIN = None
_CASES = None


def _init():
    global _CHAIN, _CASES
    import build_gold
    _CHAIN = build_gold.load_graph()
    _CASES = {}
    for name in ("kasus.jsonl.gz", "kasus_kebijakan.jsonl.gz", "kasus_terarah.jsonl.gz"):
        for line in gzip.open(OUT / name, "rt", encoding="utf-8"):
            c = json.loads(line)
            _CASES[c["case_id"]] = c


def _check(group):
    import build_gold
    import build_se
    from pph21kbs import corpus
    from pph21kbs.kb import apply_delta
    t = time.time()
    ev = next((e for e in corpus.regulation_events() if e.id == group), None)
    if ev is not None:
        kb, cases = build_se.gold_for(ev, _CHAIN), _CASES
    elif group.startswith("CF"):        # counterfactual: its gold Delta on the base of its source event
        from kb_context import base_for
        cf = corpus.event(group)
        delta = json.loads((ROOT / "dataset" / "12_emas" / "kontrafaktual" / f"GOLD-{group}.json").read_text(encoding="utf-8"))
        kb, cases = apply_delta(base_for(cf, _CHAIN)[0], delta), _CASES
    else:
        pe = next(e for e in corpus.policy_events() if e.id == group)
        side = {u.doc.id: u for u in build_gold.collect_side() if u.kind == "policy"}
        kb, cases = apply_delta(_CHAIN, side[pe.document].to_json()), _CASES
    rows = [json.loads(line) for line in gzip.open(OUT / "harapan" / f"{group}.jsonl.gz", "rt", encoding="utf-8")]
    diffs = []
    for row in rows:
        now = build_se.observations(kb, cases[row["case_id"]], date.fromisoformat(row["omega"]))
        if now != row:
            changed = sorted(k for k in set(now["obs"]) | set(row["obs"]) if now["obs"].get(k) != row["obs"].get(k))
            diffs.append({"case_id": row["case_id"], "omega": row["omega"], "obs": changed[:6],
                          "conflicts": now["conflicts"] != row["conflicts"], "errors": now["errors"] != row["errors"]})
    return group, len(rows), diffs, time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    groups = sorted(p.name.split(".")[0] for p in (OUT / "harapan").glob("*.jsonl.gz"))
    if args.only:
        groups = [g for g in groups if g in set(args.only.split(","))]
    total = bad = 0
    with ProcessPoolExecutor(args.workers, initializer=_init) as ex:
        for group, n, diffs, secs in ex.map(_check, groups):
            total += n
            bad += len(diffs)
            print(f"{group:16} {n:6} baris  {'SAMA' if not diffs else str(len(diffs)) + ' BERBEDA'}  ({secs:.0f} s)",
                  flush=True)
            for dd in diffs[:3]:
                print("    ", json.dumps(dd, ensure_ascii=False))
    print(f"\nTotal {total} baris, {bad} berbeda.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
