"""Evaluation of the month-by-month use of the engine (payroll during the year), on test cases of the research.

    env\\Scripts\\python system\\tools\\eval_monthly.py [--n 300] [--seed 7]

T1 months so far: a case cut after month M (employment end unchanged) gives, for every month up to M, the same
   period values as the full case; no year values while the final month is missing.
T2 recorded = computed: recording, for every month before the final one, the PPh 21 the engine computes changes nothing.
T3 recorded differs: recording more PPh 21 in one month raises "withheld before the final month" by exactly that
   amount and the final month's tax stays PPh of the year - withheld. With the gross method and no DTP the PPh of the
   year is unchanged and the final month's PPh 21 drops by exactly that amount. With gross-up or tax borne by the
   employer the tax allowance of that month is recorded with it (it equals the tax): it is income of that month, so the
   PPh of the year may change.
T4 missing inputs: an input a rule reads, removed from the case, is reported as missing.
Writes nothing; prints a report and exits 1 when a check fails.
"""
import argparse
import copy
import gzip
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

SE = ROOT / "dataset" / "14_ruang_uji"
OMEGA = date(2026, 10, 27)


def _load(name):
    return [json.loads(line) for line in gzip.open(SE / name, "rt", encoding="utf-8")]


def check_case(kb, case, fails, stats):
    full = evaluate_case(kb, case, OMEGA)
    if full.errors or full.partial:
        stats["skipped"] += 1
        return
    months = sorted(full.periods)
    final = months[-1]
    # T1
    for cut in months[:-1]:
        part = copy.deepcopy(case)
        part["periods"] = [p for p in part["periods"] if int(p["month"]) <= cut]
        r = evaluate_case(kb, part, OMEGA)
        stats["t1"] += 1
        bad = [m for m in months if m <= cut and r.periods.get(m) != full.periods[m]]
        if bad or r.year or not r.partial:
            fails.append(("T1", case["case_id"], cut, bad[:3], bool(r.year)))
    # T2
    rec = copy.deepcopy(case)
    for p in rec["periods"]:
        m = int(p["month"])
        if m < final and full.periods[m].get("pph21_due") is not None:
            p["recorded"] = {"pph21_due": str(full.periods[m]["pph21_due"])}
    r2 = evaluate_case(kb, rec, OMEGA)
    stats["t2"] += 1
    if r2.periods != full.periods or r2.year != full.year:
        fails.append(("T2", case["case_id"]))
    # T3
    if len(months) > 1 and full.year.get("annual_pph21") is not None:
        shift = 100_000
        m0 = months[0]
        f0 = evaluate_case(kb, case, OMEGA, trace=True)
        method = (f0.trace.get(("withholding_method", 0)) or {}).get("value")      # effective (a policy may set it)
        borne = method != "gross" or any(full.periods[m].get("tax_allowance") for m in months)
        rec3 = copy.deepcopy(case)
        for p in rec3["periods"]:
            if int(p["month"]) == m0:
                p["recorded"] = {"pph21_due": str(full.periods[m0]["pph21_due"] + shift)}
                if borne:      # the employer pays the tax: its allowance is income of that month, recorded with it
                    p["recorded"]["tax_allowance"] = str((full.periods[m0].get("tax_allowance") or 0) + shift)
        r3 = evaluate_case(kb, rec3, OMEGA, trace=True)
        stats["t3"] += 1
        y = lambda r, f: (r.trace.get((f, 0)) or {}).get("value")  # noqa: E731
        ok = (y(r3, "withheld_before_final") - y(f0, "withheld_before_final") == shift
              and y(r3, "final_period_tax") == y(r3, "annual_pph21") - y(r3, "withheld_before_final"))
        if not borne and not any(f0.periods[m].get("pph21_dtp") for m in months):
            ok = ok and y(r3, "annual_pph21") == y(f0, "annual_pph21")                 and f0.periods[final]["pph21_due"] - r3.periods[final]["pph21_due"] == shift
        if not ok:
            fails.append(("T3", case["case_id"], method, y(f0, "withheld_before_final"),
                          y(r3, "withheld_before_final"), y(f0, "annual_pph21"), y(r3, "annual_pph21")))
    # T4
    for p in case["periods"]:
        for b in ("hr", "income"):
            for k in list(p.get(b) or {}):
                cut = copy.deepcopy(case)
                for q in cut["periods"]:
                    if int(q["month"]) == int(p["month"]):
                        del q[b][k]
                r4 = evaluate_case(kb, cut, OMEGA)
                stats["t4"] += 1
                if r4.periods != full.periods and (b, k, int(p["month"])) not in r4.missing_inputs:
                    fails.append(("T4", case["case_id"], b, k, int(p["month"])))
                return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    chain = build_gold.load_graph()
    fails, stats = [], {"skipped": 0, "t1": 0, "t2": 0, "t3": 0, "t4": 0}
    cases = rng.sample(_load("kasus.jsonl.gz"), args.n)
    for c in cases:
        check_case(chain, c, fails, stats)
    side = {u.doc.id: u.to_json() for u in build_gold.collect_side() if u.kind == "policy"}
    pol_cases = _load("kasus_kebijakan.jsonl.gz")
    by_policy = {}
    for c in pol_cases:
        by_policy.setdefault((c.get("employer") or {}).get("policy"), []).append(c)
    for pe in corpus.policy_events():
        if pe.document not in side or pe.document not in by_policy:
            continue
        kb = apply_delta(chain, side[pe.document])
        for c in rng.sample(by_policy[pe.document], min(6, len(by_policy[pe.document]))):
            check_case(kb, c, fails, stats)
    print(json.dumps(stats))
    kinds = {}
    for f in fails:
        kinds.setdefault(f[0], []).append(f)
    for k, fs in kinds.items():
        print(f"{k}: {len(fs)} gagal")
        for f in fs[:6]:
            print("   ", f)
    if not fails:
        print("Semua pemeriksaan lolos.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
