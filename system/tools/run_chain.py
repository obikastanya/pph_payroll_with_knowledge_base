"""E3 regulation replay in chain mode (akuisisi.md Definition 8, mode berantai; skeleton OAR and triggered errors).

    env\\Scripts\\python system\\tools\\run_chain.py <RUN> --iso <ISO_RUN> [--variant keep|perfect] [--regenerate]
                                                     [--events E01,...] [--limit USD]

The regulation sequence (test events and distractors in chain order) is replayed on the system's own knowledge base
K^sis, starting from K*_0 (records known by 2022-12-31). For event n:
  H_n      tuples of S^E_{<=n} already wrong in K^sis_{n-1} at omega = issue date - 1 day;
  Delta-hat_n  the isolated result of <ISO_RUN> when it applies strictly to K^sis_{n-1} and K^sis_{n-1} behaves like
           K*_{n-1} (H_n empty); otherwise, with --regenerate, the pipeline is run again with K^sis_{n-1} as base
           (an LLM call), else the isolated result is transplanted with lenient application;
  abstain  variant keep: K^sis unchanged; variant perfect: the gold Delta*_n is inserted (lenient application);
  errors   wrong tuples of K^sis_n on S^E_{<=n} at omega = issue date; new = wrong minus H_n; OAR = events without
           new errors; mechanical component = errors of K^sis_{n-1} (+)_lenient Delta-hat^iso_n minus H_n.
Writes experiments/<RUN>/chain.csv and chain_summary.json. Expected values on S^E_{<=n} at omega_n come from K*_n.
"""
import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus, testspace  # noqa: E402
from pph21kbs.analysis import stats  # noqa: E402
from pph21kbs.analysis.evaluate import _obs, se_cases  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402
from pph21kbs.kb.delta import UpdateError  # noqa: E402


class Oracle:
    """Expected observations hasil(K*, case, omega), cached."""

    def __init__(self):
        self.memo = {}

    def get(self, label, kb, case, omega):
        key = (label, case["case_id"], omega)
        if key not in self.memo:
            obs, conflicts, errors = _obs(kb, case, omega)
            self.memo[key] = (obs, conflicts)
        return self.memo[key]


def wrong_set(kb, gold_label, gold_kb, cases, omega, oracle):
    out = set()
    for c in cases:
        want = oracle.get(gold_label, gold_kb, c, omega)
        got = _obs(kb, c, omega)
        if (got[0], got[1]) != want:
            out.add(c["case_id"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--iso", required=True)
    ap.add_argument("--variant", choices=["keep", "perfect"], default="keep")
    ap.add_argument("--regenerate", action="store_true")
    ap.add_argument("--events", default="")
    ap.add_argument("--limit", type=float, default=2.0)
    ap.add_argument("--sample", type=int, default=400, help="cases of S^E per year used in the chain (seeded)")
    args = ap.parse_args()
    out_dir = ROOT / "experiments" / args.run
    out_dir.mkdir(parents=True, exist_ok=True)
    chain = build_gold.load_graph()
    ids = [u.update_id for u in chain.updates]
    gold_of = {u.event_id: u for u in build_gold.collect() if u.event_id}
    k0_id = [u.update_id for u in chain.updates if u.recorded_on and u.recorded_on <= date(2022, 12, 31)][-1]
    k_sis = chain.until(k0_id)
    import random
    rng = random.Random(20261027)
    by_year = {}
    for c in se_cases().values():
        by_year.setdefault(c["tax_year"], []).append(c)
    for y in by_year:
        by_year[y] = sorted(by_year[y], key=lambda c: c["case_id"])
        if len(by_year[y]) > args.sample:
            by_year[y] = rng.sample(by_year[y], args.sample)
    wanted = set(filter(None, args.events.split(",")))
    seq = corpus.chain_order([e for e in corpus.regulation_events() if e.part in ("uji", "pengecoh")])
    oracle = Oracle()
    rows, seen_years = [], set()
    ledger = client = None
    for ev in seq:
        if wanted and ev.id not in wanted:
            continue
        seen_years |= set(testspace.event_years(ev))
        cases = [c for y in sorted(seen_years) for c in by_year.get(y, [])]
        gold = gold_of.get(ev.id)
        k_star_prev = build_gold.prefix_at(chain, (ev.issued - timedelta(days=1)).isoformat())
        k_star = chain.until(gold.delta_id) if gold else build_gold.prefix_at(chain, ev.issued.isoformat())
        h_n = wrong_set(k_sis, f"prev-{ev.id}", k_star_prev, cases, ev.issued - timedelta(days=1), oracle)
        iso_path = ROOT / "experiments" / args.iso / "results" / f"{ev.id}.json"
        iso = json.loads(iso_path.read_text(encoding="utf-8")) if iso_path.exists() else None
        iso_delta = iso.get("delta") if iso and iso.get("status") in ("applied", "empty") else None
        source = "isolated"
        delta = iso_delta
        k_next = None
        if delta is not None:
            try:
                k_next = apply_delta(k_sis, dict(delta, delta_id=f"{args.run}-{ev.id}"))
            except (UpdateError, ValueError, KeyError):
                k_next = None
        if (k_next is None or h_n) and args.regenerate and iso is not None:
            from pph21kbs.pipeline import llm
            from pph21kbs.pipeline.run import Config, run_document
            if ledger is None:
                ledger = llm.Ledger(args.run, run_limit_usd=args.limit)
                client = llm.AnthropicClient(ledger)
            res = run_document(ev, k_sis, client, ledger, Config(), run_id=args.run,
                               out_dir=out_dir / "results_chain")
            delta = res.get("delta") if res.get("status") in ("applied", "empty") else None
            source = "regenerated"
            k_next = None
            if delta is not None:
                try:
                    k_next = apply_delta(k_sis, dict(delta, delta_id=f"{args.run}-{ev.id}-r"))
                except (UpdateError, ValueError, KeyError):
                    k_next = None
        if k_next is None and delta is not None:
            try:
                k_next = apply_delta(k_sis, dict(delta, delta_id=f"{args.run}-{ev.id}-l"), lenient=True)
                source += "+lenient"
            except (UpdateError, ValueError, KeyError):
                k_next = None
        abstained = k_next is None
        if abstained:
            if args.variant == "perfect" and gold is not None:
                k_next = apply_delta(k_sis, dict(gold.to_json(), delta_id=f"{args.run}-{ev.id}-gold"), lenient=True)
                source = "perfect reviewer"
            else:
                k_next = k_sis
                source = "abstain (kept)"
        wrong = wrong_set(k_next, f"now-{ev.id}", k_star, cases, ev.issued, oracle)
        new = wrong - h_n
        mech = set()
        if iso_delta is not None:
            try:
                k_mech = apply_delta(k_sis, dict(iso_delta, delta_id=f"{args.run}-{ev.id}-m"), lenient=True)
                mech = wrong_set(k_mech, f"now-{ev.id}", k_star, cases, ev.issued, oracle) - h_n
            except (UpdateError, ValueError, KeyError):
                mech = set()
        rows.append({"event": ev.id, "part": ev.part, "source": source, "abstain": abstained, "cases": len(cases),
                     "H_n": len(h_n), "wrong": len(wrong), "new_errors": len(new), "mechanical": len(mech)})
        print(f"{ev.id:4s} {source:22s} H={len(h_n):4d} wrong={len(wrong):4d} new={len(new):4d} "
              f"mech={len(mech):4d}", flush=True)
        k_sis = k_next
    with open(out_dir / "chain.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    ok = sum(r["new_errors"] == 0 for r in rows)
    summary = {"events": len(rows), "OAR": ok / len(rows), "OAR_CI": stats.clopper_pearson(ok, len(rows)),
               "final_wrong_tuples": rows[-1]["wrong"], "variant": args.variant, "iso_run": args.iso}
    (out_dir / "chain_summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
