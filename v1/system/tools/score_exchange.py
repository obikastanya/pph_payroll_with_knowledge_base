r"""Development: score every candidate response in a subagent exchange folder (draft, repair, review) separately.

    env\Scripts\python system\tools\score_exchange.py <RUN> <EXCHANGE DIR> [--dev]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.analysis.evaluate import score_update, se_cases, se_expected  # noqa: E402
from pph21kbs.pipeline.convert import ConversionError, to_delta  # noqa: E402
from pph21kbs.pipeline.run import documents_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("exchange")
    ap.add_argument("--dev", action="store_true")
    args = ap.parse_args()
    chain = build_gold.load_graph()
    cases = se_cases(dev=args.dev)
    side = {u.doc.id: u.to_json() for u in build_gold.collect_side() if u.kind == "policy"}
    for resp in sorted(Path(args.exchange).glob(f"{args.run}-*-cand*.resp.json")):
        cid = resp.name[:-len(".resp.json")]
        ev_id = cid[len(args.run) + 1:].split("-cand")[0]
        ev = corpus.event(ev_id)
        base, _ = base_for(ev, chain)
        gp = None
        if ev.layer == "company":
            gp = {e["id"]: e["produces"] for e in side[ev.document]["add"] + side[ev.document]["change"]
                  if e.get("kind") == "rule"}
        try:
            delta = to_delta(json.loads(resp.read_text(encoding="utf-8")), cid, ev.id, documents_of(ev)[0])
            s = score_update(base, delta, ev, se_expected(ev.id, dev=args.dev), cases, gp)
            print(f"{cid:45s} {s.outcome:7s} wrong {s.wrong_tuples}/{s.tuples} values {s.a2 + s.a3t + s.a3w} "
                  f"conflicts {s.a4} errors {s.errors}")
        except (ConversionError, ValueError, KeyError) as e:
            print(f"{cid:45s} invalid {str(e)[:80]}")


if __name__ == "__main__":
    main()
