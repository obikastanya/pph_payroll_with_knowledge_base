"""Score an acquisition run on S^E (RQ2 metrics; skeleton "Definisi metrik utama").

    env\\Scripts\\python system\\tools\\score_run.py <RUN> [--conditions] [--dev]

Reads experiments/<RUN>/results/<EVENT>.json, scores the selected update of each event in isolated mode (base = gold
chain before the event; policies on the full regulation chain) against the gold expected values of S^E, and writes
experiments/<RUN>/scores.csv and summary.json: outcome per event and condition, SER/CAR/ABS with exact CIs over real
relevant documents (per layer), relevance errors on distractors and relevant documents, pass@1 / pass@m / 1@m and
selection efficiency. --conditions also scores B3, B4, AB3 and AB4 from the same candidates.
"""
import argparse
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
from pph21kbs.analysis.evaluate import score_update, se_cases, se_expected  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--conditions", action="store_true")
    ap.add_argument("--dev", action="store_true")
    args = ap.parse_args()
    run = ROOT / "experiments" / args.run
    chain = build_gold.load_graph()
    cases = se_cases(dev=args.dev)
    rows, by_cond = [], {}
    pass1, passm, onem = [], [], []
    for path in sorted((run / "results").glob("*.json")):
        res = json.loads(path.read_text(encoding="utf-8"))
        ev = corpus.event(res["event"])
        base, _ = base_for(ev, chain)
        tuples = se_expected(ev.id, dev=args.dev)
        if not tuples:
            continue
        conds = {"proposed": res.get("delta") if res.get("status") in ("applied", "empty") else None}
        if args.conditions and res.get("candidates"):
            from pph21kbs.analysis.conditions import conditions
            conds = conditions(res, base, ev, oracle=lambda d: score_update(base, d, ev, tuples, cases).outcome
                               == "benar", policies=(ev.document,) if ev.layer == "company" else ())
        for name, delta in conds.items():
            s = score_update(base, delta, ev, tuples, cases) if delta is not None else None
            outcome = s.outcome if s else "abstain"
            rows.append({"event": ev.id, "part": ev.part, "layer": ev.layer, "relevant": ev.relevant,
                         "condition": name, "status": res.get("status"), "outcome": outcome,
                         "wrong_tuples": s.wrong_tuples if s else "", "tuples": s.tuples if s else "",
                         "a2": s.a2 if s else "", "a3t": s.a3t if s else "", "a3w": s.a3w if s else "",
                         "a4": s.a4 if s else "", "cost_usd": res.get("cost_usd", 0)})
            by_cond.setdefault(name, []).append(rows[-1])
        cands = res.get("candidates") or []
        if cands:
            # pass@k on the initial candidates (before repair; i.i.d.): correct on S^E whatever the gates said
            m = len(cands)
            k = 0
            for c in cands:
                initial = c.get("initial_delta") if c.get("repaired") else c.get("delta")
                if initial is not None and score_update(base, initial, ev, tuples, cases).outcome == "benar":
                    k += 1
            pass1.append(stats.pass_at(m, k, 1))
            passm.append(stats.pass_at(m, k, m))
            onem.append(1.0 if conds["proposed"] is not None and rows[-len(conds)]["outcome"] == "benar" else 0.0)
    summary = {}
    for name, rs in by_cond.items():
        real = [r for r in rs if r["relevant"] and r["part"] in ("uji", "kebijakan_uji")]
        for layer in ("regulation", "company", "all"):
            sub = [r for r in real if layer == "all" or r["layer"] == layer]
            n = len(sub)
            if not n:
                continue
            ser = sum(r["outcome"] == "salah" for r in sub)
            car = sum(r["outcome"] == "benar" for r in sub)
            summary[f"{name}/{layer}"] = {
                "n": n, "SER": ser / n, "SER_CI": stats.clopper_pearson(ser, n),
                "SER_upper": stats.upper_bound(ser, n), "CAR": car / n, "CAR_CI": stats.clopper_pearson(car, n),
                "ABS": 1 - (ser + car) / n}
        dis = [r for r in rs if not r["relevant"]]
        if dis:
            fp = sum(r["status"] not in ("empty", "abstain") for r in dis)
            summary[f"{name}/distractors"] = {"n": len(dis), "false_positive": fp / len(dis),
                                              "wrong_applied": sum(r["outcome"] == "salah" for r in dis)}
    if pass1:
        p1, pm, o = sum(pass1) / len(pass1), sum(passm) / len(passm), sum(onem) / len(onem)
        summary["selection"] = {"pass@1": p1, "pass@m": pm, "1@m": o, "eta": stats.selection_efficiency(o, p1, pm)}
    if rows:
        with open(run / "scores.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    (run / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str) + "\n",
                                      encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
