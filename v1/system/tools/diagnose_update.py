r"""Development diagnosis of a drafted update against the gold (for pipeline design; never fed to the pipeline).

    env\Scripts\python system\tools\diagnose_update.py <RUN> <EVENT> [--dev] [--n 6] [--cand N]

Prints the selected (or candidate N) Delta and the gold Delta in compact form, and for the first wrong tuples the
observations that differ (expected vs obtained) and conflict-report differences.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from kb_context import base_for  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.analysis.evaluate import _obs, se_cases, se_expected  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

FIELDS = ("valid_from", "valid_until", "layer", "modality", "scope", "produces", "condition", "expression", "overrides",
          "name", "value", "value_type", "table_kind", "assertion", "conflict_code")


def compact(delta):
    out = []
    for part in ("add", "change", "remove"):
        for e in delta.get(part) or []:
            d = {k: e.get(k) for k in FIELDS if e.get(k) not in (None, "")}
            if e.get("rows") is not None:
                d["rows"] = f"{len(e['rows'])} rows: {json.dumps(e['rows'][:3], default=str)[:200]}"
            if e.get("rows_ref"):
                d["rows_ref"] = e["rows_ref"]
            out.append(f"  [{part}] {e.get('kind')} {e.get('id')}: {json.dumps(d, ensure_ascii=False, default=str)}")
    return "\n".join(out)


def gold_delta(ev):
    for u in list(build_gold.collect()) + list(build_gold.collect_side()):
        j = u.to_json()
        if j.get("event_id") == ev.id or (ev.layer == "company" and u.doc.id == ev.document):
            return j
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("event")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--cand", type=int)
    args = ap.parse_args()
    res = json.loads((ROOT / "experiments" / args.run / "results" / f"{args.event}.json").read_text(encoding="utf-8"))
    delta = res.get("delta")
    if args.cand:
        delta = next(c["delta"] for c in res["candidates"] if c["n"] == args.cand)
    ev = corpus.event(args.event)
    base, _ = base_for(ev, build_gold.load_graph())
    print(f"== {args.event} status={res.get('status')} selected={res.get('selected')}")
    rel = (res.get("relevance") or {}).get("output") or {}
    print("relevance effective_from:", rel.get("effective_from"), "| subjects:", rel.get("subjects"))
    print("-- drafted:")
    print(compact(delta or {}))
    g = gold_delta(ev)
    print("-- gold:")
    print(compact(g or {}))
    if delta is None:
        return
    kb = apply_delta(base, delta)
    cases, tuples = se_cases(dev=args.dev), se_expected(ev.id, dev=args.dev)
    keys, shown = Counter(), 0
    for t in tuples:
        case = cases[t["case_id"]]
        obs, conflicts, errors = _obs(kb, case, date.fromisoformat(t["omega"]))
        diff = {k: (w, obs.get(k)) for k, w in t["obs"].items() if obs.get(k) != w}
        cdiff = (t["conflicts"], conflicts) if conflicts != t["conflicts"] else None
        if diff or cdiff or (errors and not t.get("errors")):
            for k in diff:
                keys[k.split(":", 1)[1]] += 1
            if shown < args.n:
                shown += 1
                emp = case["employer"]
                print(f"-- wrong {t['case_id']} omega={t['omega']} year={case['tax_year']} method={case.get('method')} "
                      f"policy={emp.get('policy')} ptkp={case['employee'].get('ptkp_status')}")
                for k, (w, o) in list(diff.items())[:8]:
                    print(f"     {k}: expected {w} got {o}")
                if cdiff:
                    print(f"     conflicts expected {cdiff[0]} got {cdiff[1]}")
                if errors:
                    print(f"     errors {str(errors)[:300]}")
    print("-- wrong facts:", keys.most_common(12))


if __name__ == "__main__":
    main()
