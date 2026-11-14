r"""Exploratory (8-9 November 2026; no LLM call): recompute the behavioural consensus of an existing run with conflict
keys aligned by the fact a rule produces instead of the rule id, and score the newly selected update.

    env\Scripts\python system\tools\reconsensus.py <RUN> [--dev] [--events E1,E2]

The candidates and their gate results are taken from experiments/<RUN>/results/<EVENT>.json as recorded; only the
grouping step changes. Prints, per event, the recorded status and outcome and the status and outcome with aligned
conflict keys, and writes experiments/<RUN>/reconsensus.json.
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.analysis.evaluate import score_update, se_cases, se_expected  # noqa: E402
from pph21kbs.pipeline import consensus  # noqa: E402
from pph21kbs.pipeline.run import Config, check  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--events")
    args = ap.parse_args()
    run = ROOT / "experiments" / args.run
    chain = build_gold.load_graph()
    cases = se_cases(dev=args.dev)
    side = {u.doc.id: u.to_json() for u in build_gold.collect_side() if u.kind == "policy"}
    out = {}
    for path in sorted((run / "results").glob("*.json")):
        res = json.loads(path.read_text(encoding="utf-8"))
        if args.events and res["event"] not in args.events.split(","):
            continue
        cands = [c for c in res.get("candidates") or [] if c.get("passed") and c.get("delta")]
        if not cands:
            continue
        ev = corpus.event(res["event"])
        base, _ = base_for(ev, chain)
        rel = (res.get("relevance") or {}).get("output") or {}
        policies = (ev.document,) if ev.layer == "company" else ()
        cfg = Config()
        passing = {}
        for c in cands:
            ok, _, kb2, sgs = check(base, c["delta"], ev, ev.issued, rel, cfg, policies)
            if ok:
                passing[c["n"]] = (kb2, sgs.cases, sgs.omegas)
        order = sorted(passing, key=lambda n: next(c["order"] for c in cands if c["n"] == n))
        sel, groups, status = consensus.choose(passing, order, align=True)
        gp = None
        if ev.layer == "company":
            gp = {e["id"]: e["produces"] for e in side[ev.document]["add"] + side[ev.document]["change"]
                  if e.get("kind") == "rule"}
        tuples = se_expected(ev.id, dev=args.dev)

        def outcome(delta):
            return score_update(base, delta, ev, tuples, cases, gp).outcome if delta is not None else "abstain"
        old = outcome(res.get("delta") if res.get("status") in ("applied", "empty") else None)
        new_delta = next(c["delta"] for c in cands if c["n"] == sel) if sel is not None else None
        new = outcome(new_delta)
        out[ev.id] = {"recorded": [res.get("status"), res.get("groups"), old], "aligned": [status, groups, new]}
        print(f"{ev.id:18s} recorded {res.get('status'):8s} {str(res.get('groups')):22s} {old:8s} | aligned "
              f"{status:8s} {str(groups):22s} {new}", flush=True)
    (run / "reconsensus.json").write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
