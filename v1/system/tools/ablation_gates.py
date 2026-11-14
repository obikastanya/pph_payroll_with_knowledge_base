"""Gate ablation per component (feedback 3 November 2026): consensus with G2 or G3 removed, and with only G1 kept.

    env\\Scripts\\python system\\tools\\ablation_gates.py e2-regulasi e2-pkb

Completes AB3 (score_run --conditions removes G4, G5 and the repair round) for the gates it did not remove. Uses the
stored candidates and gate logs of each run, with no LLM call, exactly as analysis/conditions.py does: gates that did
not run for a candidate are run here without stopping, and the consensus is computed on S^G, never on S^E. The
condition "full" recomputes the proposed selection as a check. Writes docs/hasil/ablasi_gerbang.json and .csv.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.analysis import stats  # noqa: E402
from pph21kbs.analysis.conditions import ORDER, _choose, all_gates  # noqa: E402
from pph21kbs.analysis.evaluate import score_update, se_cases, se_expected  # noqa: E402

VARIANTS = {
    "full": ORDER,
    "AB3_noG2": ("G1", "G3", "G4", "G5"),
    "AB3_noG3": ("G1", "G2", "G4", "G5"),
    "AB3_onlyG1": ("G1",),
}


def main(runs):
    chain = build_gold.load_graph()
    cases = se_cases()
    side = {u.doc.id: u.to_json() for u in build_gold.collect_side() if u.kind == "policy"}
    produces_of = {doc: {e["id"]: e["produces"] for e in d["add"] + d["change"] if e.get("kind") == "rule"}
                   for doc, d in side.items()}
    rows = []
    for run in runs:
        for path in sorted((ROOT / "experiments" / run / "results").glob("*.json")):
            res = json.loads(path.read_text(encoding="utf-8"))
            ev = corpus.event(res["event"])
            if not (ev.relevant and ev.part in ("uji", "kebijakan_uji")):
                continue
            base, _ = base_for(ev, chain)
            tuples = se_expected(ev.id)
            gp = produces_of.get(ev.document) if ev.layer == "company" else None
            rel = (res.get("relevance") or {}).get("output") or None
            policies = (ev.document,) if ev.layer == "company" else ()
            cands = res.get("candidates") or []
            order = [c["n"] for c in sorted(cands, key=lambda c: c["order"])]
            final = {c["n"]: (c["delta"],) + all_gates(base, c["delta"], ev, ev.issued, rel, policies)
                     for c in cands if c.get("delta") is not None}
            for name, need in VARIANTS.items():
                pool = {n: final[n][2] for n in order
                        if n in final and final[n][2] and all(final[n][1].get(g) for g in need)}
                sel, _ = _choose(pool, order)
                delta = final[sel][0] if sel is not None else None
                s = score_update(base, delta, ev, tuples, cases, gp) if delta is not None else None
                rows.append({"run": run, "event": ev.id, "layer": ev.layer, "condition": name,
                             "outcome": s.outcome if s else "abstain",
                             "wrong_tuples": s.wrong_tuples if s else ""})
                print(run, ev.id, name, rows[-1]["outcome"], flush=True)
    summary = {}
    for name in VARIANTS:
        sub = [r for r in rows if r["condition"] == name]
        n = len(sub)
        ser = sum(r["outcome"] == "salah" for r in sub)
        car = sum(r["outcome"] == "benar" for r in sub)
        summary[name] = {"n": n, "SER": f"{ser}/{n}", "SER_upper_one_sided": round(stats.upper_bound(ser, n), 3),
                         "CAR": f"{car}/{n}", "ABS": f"{n - ser - car}/{n}",
                         "wrong": sorted(r["event"] for r in sub if r["outcome"] == "salah"),
                         "correct": sorted(r["event"] for r in sub if r["outcome"] == "benar")}
    out = ROOT / "docs" / "hasil"
    with open(out / "ablasi_gerbang.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (out / "ablasi_gerbang.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n",
                                             encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or ["e2-regulasi", "e2-pkb"])
