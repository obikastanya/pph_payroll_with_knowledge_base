"""Descriptive analyses for the paper (preregistration, section 6), from logged results only; no model calls.

    env\\Scripts\\python -m v2.harness.extra late        late upload: 5 retroactive events x 3 lags
    env\\Scripts\\python -m v2.harness.extra workload    automated steps and HR interventions per chain
    env\\Scripts\\python -m v2.harness.extra discord     isolated outcome vs in-chain outcome per regulation event
"""
import argparse
import json
from collections import Counter
from datetime import timedelta

from pph21kbs import engine, recalc  # noqa: E402

from . import WORK, chain, gold, units
from .analysis import REAL_COMPANIES, scores
from .late import LAGS, RETROACTIVE, add_months, scenario
from .measure import MEASURED
from .score import delta_of

OUT = WORK / "analysis"


def _same(a, b):
    return a.periods == b.periods and a.year == b.year


def late():
    pool = {u.event.id: u for u in units.regulation_units()}
    rows = []
    for eid in RETROACTIVE:
        u = pool[eid]
        ev = u.event
        res = json.loads((MEASURED / "isolated-real-1" / "results" / f"{eid}.json").read_text(encoding="utf-8"))
        system = delta_of(res, ev)
        base = gold.base_before(ev)
        for lag in LAGS:
            upload = add_months(ev.issued, lag)
            days = (upload - ev.issued).days
            before = upload - timedelta(days=1)
            paid = upload.month - 1 if upload.year == ev.issued.year else 12
            expected = gold.apply(base, chain.shifted(gold.delta(ev.gold), days), update_id="LATE-GOLD")
            year_cases = [c for c in u.cases if c["tax_year"] in (ev.issued.year, upload.year)]
            rep = recalc.report(expected, year_cases, before, upload, paid_through=paid)
            months = sum(len({r["month"] for r in x["differences"] if r["month"]}) for x in rep)
            # the results as known before the upload stay those of the base (bitemporal invariant)
            invariant = all(_same(engine.evaluate_case(expected, c, omega=before),
                                  engine.evaluate_case(base, c, omega=before)) for c in year_cases)
            row = {"event": eid, "lag": lag, "upload": upload.isoformat(), "paid_through": paid,
                   "cases": len(year_cases), "cases_recalculated": len(rep), "months_recalculated": months,
                   "old_results_reproducible": invariant, "isolated_outcome": scores("isolated-real-1")[eid]["outcome"]}
            if system is None:
                row["system"] = "abstain"
            else:
                s = scenario(ev, system, u.cases, lag)
                row["system"] = s["outcome"]
                row["system_wrong_cases"] = len(s["wrong_cases"])
            rows.append(row)
            print(row, flush=True)
    summary = {"scenarios": len(rows), "system": dict(Counter(r["system"] for r in rows)),
               "old_results_reproducible": sum(r["old_results_reproducible"] for r in rows),
               "cases_recalculated": sum(r["cases_recalculated"] for r in rows),
               "months_recalculated": sum(r["months_recalculated"] for r in rows)}
    return {"rows": rows, "summary": summary}


def _logs(out_dir):
    return {c.id: chain.load(out_dir, c) for c in chain.chains() if (out_dir / f"{c.id}.jsonl").exists()}


def workload():
    out = {}
    for label, d in (("measured", MEASURED / "chains"), ("g7", WORK / "posthoc_g7" / "chains")):
        rows = {}
        for cid, log in _logs(d).items():
            events = {s.event.id: s.event for c in chain.chains() if c.id == cid
                      for s in chain.stream(c.members, c.start)}
            st = Counter(r["status"] for r in log)
            hr = sum(1 for r in log if r["delta"] is None and events[r["event"]].gold)
            rows[cid] = {"steps": len(log), "proposed": st["proposed"], "not_relevant": st["empty"],
                         "abstain": st["abstain"], "abstain_needing_hr_update": hr,
                         "automated_share": (st["proposed"] + st["empty"]) / len(log)}
        real = [v for k, v in rows.items() if k in REAL_COMPANIES]
        tot = {k: sum(v[k] for v in real) for k in ("steps", "proposed", "not_relevant", "abstain",
                                                    "abstain_needing_hr_update")}
        tot["automated_share"] = (tot["proposed"] + tot["not_relevant"]) / tot["steps"] if tot["steps"] else None
        out[label] = {"chains": rows, "real_total": tot}
    return out


def discord():
    rep = json.loads((OUT / "chains.json").read_text(encoding="utf-8"))
    r1, r2 = scores("isolated-real-1"), scores("isolated-real-2")
    logs = _logs(MEASURED / "chains")
    events = sorted({e for c in REAL_COMPANIES for e in (r["event"] for r in logs.get(c, []))
                     if e.startswith("E")})
    rows = []
    for e in events:
        row = {"event": e, "isolated_1": r1.get(e, {}).get("outcome"), "isolated_2": r2.get(e, {}).get("outcome"),
               "chains": {}}
        for c in REAL_COMPANIES:
            step = next((r for r in logs.get(c, []) if r["event"] == e), None)
            if step is None:
                continue
            if e in rep["chains"][c]["in_chain_errors"]:
                row["chains"][c] = "silent_error"
            elif step["delta"] is None:
                row["chains"][c] = "abstain"
            else:
                row["chains"][c] = "correct"
        rows.append(row)
    agree = sum(1 for r in rows for o in r["chains"].values() if o == r["isolated_1"])
    total = sum(len(r["chains"]) for r in rows)
    return {"rows": rows, "pairs": total, "same_as_isolated_run1": agree}


def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("late", "workload", "discord"))
    a = ap.parse_args()
    r = {"late": late, "workload": workload, "discord": discord}[a.what]()
    save(f"extra_{a.what}", r)
    print(json.dumps(r.get("summary") or r.get("real_total") or {k: v for k, v in r.items() if k != "rows"},
                     indent=1, default=str))
