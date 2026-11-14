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
from kb_context import base_for  # noqa: E402
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


def _load_iso(runs, event_id):
    for r in runs.split(","):
        path = ROOT / "experiments" / r / "results" / f"{event_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def _iso_wrong(base, delta, delta_id, gold_kb, cases, ev, oracle):
    """Wrong tuples of base (+) delta (strict, else lenient; abstain = base) against K*_n."""
    kb = base
    if delta is not None:
        try:
            kb = apply_delta(base, dict(delta, delta_id=delta_id))
        except (UpdateError, ValueError, KeyError):
            try:
                kb = apply_delta(base, dict(delta, delta_id=delta_id + "-l"), lenient=True)
            except (UpdateError, ValueError, KeyError):
                kb = base
    return wrong_set(kb, f"now-{ev.id}", gold_kb, cases, ev.issued, oracle)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--iso", required=True)
    ap.add_argument("--variant", choices=["keep", "perfect"], default="keep")
    ap.add_argument("--regenerate", action="store_true")
    ap.add_argument("--events", default="")
    ap.add_argument("--limit", type=float, default=2.0)
    ap.add_argument("--sample", type=int, default=400, help="cases of S^E per year used in the chain (seeded)")
    ap.add_argument("--iso2", default="", help="second isolated run(s): noise bound of H3b")
    ap.add_argument("--m-reg", type=int, default=3, help="candidates of a regenerated regulation (as in E2)")
    ap.add_argument("--m-dis", type=int, default=1, help="candidates of a regenerated distractor (as in E2)")
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
        iso = _load_iso(args.iso, ev.id)
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
            m = args.m_reg if ev.part == "uji" else args.m_dis
            res = run_document(ev, k_sis, client, ledger, Config(m=m), run_id=args.run,
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
        not_run = iso is None or iso.get("status") in ("budget", "crash")
        if abstained:
            if args.variant == "perfect" and gold is not None:
                k_next = apply_delta(k_sis, dict(gold.to_json(), delta_id=f"{args.run}-{ev.id}-gold"), lenient=True)
                source = "perfect reviewer"
            else:
                k_next = k_sis
                source = "not run (kept)" if not_run else "abstain (kept)"
        wrong = wrong_set(k_next, f"now-{ev.id}", k_star, cases, ev.issued, oracle)
        new = wrong - h_n
        mech = set()
        if iso_delta is not None:
            try:
                k_mech = apply_delta(k_sis, dict(iso_delta, delta_id=f"{args.run}-{ev.id}-m"), lenient=True)
                mech = wrong_set(k_mech, f"now-{ev.id}", k_star, cases, ev.issued, oracle) - h_n
            except (UpdateError, ValueError, KeyError):
                mech = set()
        # H3b: errors of the isolated update on the gold base (same cases and knowledge date), triggered errors
        # I_n = wrong \ (E_iso u H_n), and the noise bound |E_iso1 xor E_iso2| of two independent isolated runs
        gold_base, _ = base_for(ev, chain)
        iso_wrong = _iso_wrong(gold_base, iso_delta, f"{args.run}-{ev.id}-i", k_star, cases, ev, oracle)
        triggered = wrong - (iso_wrong | h_n)
        noise = None
        if args.iso2:
            iso2 = _load_iso(args.iso2, ev.id)
            if iso2 is not None:
                d2 = iso2.get("delta") if iso2.get("status") in ("applied", "empty") else None
                iso2_wrong = _iso_wrong(gold_base, d2, f"{args.run}-{ev.id}-i2", k_star, cases, ev, oracle)
                noise = len(iso_wrong ^ iso2_wrong)
        rows.append({"event": ev.id, "part": ev.part, "source": source, "abstain": abstained, "not_run": not_run,
                     "cases": len(cases),
                     "H_n": len(h_n), "wrong": len(wrong), "new_errors": len(new), "mechanical": len(mech),
                     "iso_wrong": len(iso_wrong), "triggered": len(triggered),
                     "noise_bound": "" if noise is None else noise})
        print(f"{ev.id:4s} {source:22s} H={len(h_n):4d} wrong={len(wrong):4d} new={len(new):4d} "
              f"mech={len(mech):4d}", flush=True)
        k_sis = k_next
    with open(out_dir / "chain.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    run = [r for r in rows if not r["not_run"]]            # events without an isolated result are not counted
    ok = sum(r["new_errors"] == 0 for r in run)
    summary = {"events": len(run), "not_run": len(rows) - len(run), "OAR": ok / len(run),
               "OAR_CI": stats.clopper_pearson(ok, len(run)), "OAR_lower_one_sided": 1 - stats.upper_bound(len(run) - ok, len(run)),
               "regulation_events": sum(r["part"] == "uji" for r in run),
               "OAR_regulation": sum(r["new_errors"] == 0 for r in run if r["part"] == "uji")
               / max(1, sum(r["part"] == "uji" for r in run)),
               "final_wrong_tuples": rows[-1]["wrong"], "variant": args.variant, "iso_run": args.iso,
               "regenerated": args.regenerate,
               "triggered_total": sum(r["triggered"] for r in run), "mechanical_total": sum(r["mechanical"] for r in run)}
    paired = [r for r in run if r["noise_bound"] != ""]
    if paired:
        summary["H3b"] = {"events_with_noise_bound": len(paired),
                          "triggered_total": sum(r["triggered"] for r in paired),
                          "noise_bound_total": sum(r["noise_bound"] for r in paired),
                          "events_triggered_above_noise": [r["event"] for r in paired
                                                           if r["triggered"] > r["noise_bound"]]}
    (out_dir / "chain_summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
