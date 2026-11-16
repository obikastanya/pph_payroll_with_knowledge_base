"""Analysis of the measured runs (preregistration, section 6). Reads only logged results; no model calls.

    env\\Scripts\\python -m v2.harness.analysis isolated   H2, baselines, breakdowns, run-to-run, Sonnet, failures
    env\\Scripts\\python -m v2.harness.analysis code       payslip rows of the code scenario per real chain (cached)
    env\\Scripts\\python -m v2.harness.analysis power      H1 power simulation from the development rates
    env\\Scripts\\python -m v2.harness.analysis chains     H1 and the HR conditions from the chain logs

Writes v2/work/analysis/<name>.json and a short text report to stdout.
"""
import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from datetime import timedelta

from scipy import stats

from . import WORK, chain, corpus, gold, instances, prospective, score, units
from . import testspace as ts
from .measure import MEASURED

OUT = WORK / "analysis"
OUTCOMES = ("correct", "abstain", "silent_error")
ARMS = ("pipeline", "B2", "B3", "B4", "top")
REAL_COMPANIES = ("SANSAN", "CENTEX", "TAEKWANG", "AVCO", "WIKA")


# ------------------------------------------------------------------------------------------------------- statistics
def clopper_pearson(k, n, level=0.95, sided=2):
    """(low, high): exact binomial interval; sided=1 gives the one-sided upper (or lower) bound at `level`."""
    a = 1 - level if sided == 1 else (1 - level) / 2
    lo = 0.0 if k == 0 else stats.beta.ppf(a, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a, k + 1, n - k)
    return float(lo), float(hi)


def wilson(k, n, z=1.959964):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    c = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    d = 1 + z * z / n
    return (p + z * z / (2 * n) - c) / d, (p + z * z / (2 * n) + c) / d


def mcnemar_one_sided(b, c):
    """Exact one-sided p for 'arm 1 has fewer failures': b = failures of arm 2 only, c = failures of arm 1 only."""
    n = b + c
    return 1.0 if n == 0 else float(stats.binom.sf(b - 1, n, 0.5))


def newcombe_paired(a, b, c, d):
    """95% CI of p1 - p2 for paired proportions (Newcombe 1998, method 10). a: both, b: only 1, c: only 2, d: none."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n)
    l2, u2 = wilson(a + c, n)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    phi = 0.0 if den == 0 else (a * d - b * c) / math.sqrt(den)
    delta = p1 - p2
    lo = delta - math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    hi = delta + math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return delta, lo, hi


def kappa(xs, ys):
    n = len(xs)
    if not n:
        return None
    po = sum(x == y for x, y in zip(xs, ys)) / n
    cx, cy = Counter(xs), Counter(ys)
    pe = sum(cx[k] * cy[k] for k in set(cx) | set(cy)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


# ------------------------------------------------------------------------------------------------------- isolated
def scores(stage):
    path = MEASURED / stage / "scores.jsonl"
    if not path.exists():
        return {}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {r["event"]: r for r in rows}


def arm(row, name):
    return row["outcome"] if name == "pipeline" else row[name]


def rates(rows, name="pipeline"):
    n = len(rows)
    c = Counter(arm(r, name) for r in rows)
    out = {"n": n}
    for o in OUTCOMES:
        out[o] = c[o]
        out[f"{o}_rate"] = c[o] / n if n else None
        out[f"{o}_ci95"] = clopper_pearson(c[o], n) if n else None
    return out


def h2(rows):
    """H2 on the prospective set: (a) one-sided 95% upper bound of SER <= 0.15; (b) SER pipeline < SER B3 (exact
    McNemar, one-sided, alpha 0.05) and Newcombe lower bound of CAR(pipeline) - CAR(B3) >= -0.10; (c) abstain <= 0.5."""
    n = len(rows)
    ser = sum(r["outcome"] == "silent_error" for r in rows)
    upper = clopper_pearson(ser, n, sided=1)[1]
    b = sum(r["B3"] == "silent_error" and r["outcome"] != "silent_error" for r in rows)
    c = sum(r["outcome"] == "silent_error" and r["B3"] != "silent_error" for r in rows)
    p = mcnemar_one_sided(b, c)
    pc = [(r["outcome"] == "correct", r["B3"] == "correct") for r in rows]
    tab = (sum(x and y for x, y in pc), sum(x and not y for x, y in pc), sum(y and not x for x, y in pc),
           sum(not x and not y for x, y in pc))
    d, lo, hi = newcombe_paired(*tab)
    abstain = sum(r["outcome"] == "abstain" for r in rows) / n
    out = {"n": n, "ser": ser / n, "ser_upper95_one_sided": upper, "a": upper <= 0.15,
           "mcnemar_b3_only": b, "mcnemar_pipeline_only": c, "mcnemar_p_one_sided": p,
           "car_diff_vs_b3": d, "car_diff_ci95": (lo, hi), "car_table_both_only1_only2_none": tab,
           "b": p < 0.05 and lo >= -0.10, "abstain_rate": abstain, "c": abstain <= 0.50}
    out["supported"] = out["a"] and out["b"] and out["c"]
    return out


def _event_rows():
    with open(corpus.EVENTS_CSV, encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def breakdown(rows, key):
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    return {str(k): {name: dict(Counter(arm(r, name) for r in g)) for name in ARMS} | {"n": len(g)}
            for k, g in sorted(groups.items(), key=lambda t: str(t[0]))}


def isolated_report():
    specs = {s["id"]: s for s in prospective.specs()}
    events = _event_rows()
    pros = list(scores("isolated-prospective").values())
    real1, real2 = scores("isolated-real-1"), scores("isolated-real-2")
    son_r, son_p = scores("sonnet-real"), scores("sonnet-prospective")
    reg = lambda rid: rid in events and events[rid]["bagian"] == "uji"
    dis = lambda rid: rid in events and events[rid]["bagian"] == "pengecoh"
    real_docs = [r for k, r in real1.items() if reg(k) or k.startswith("PKB-")]
    out = {"prospective": {name: rates(pros, name) for name in ARMS}}
    if pros:
        out["H2"] = h2(pros)
        out["prospective_by"] = {
            "layer": breakdown(pros, lambda r: specs[r["event"]]["layer"]),
            "change_type": breakdown(pros, lambda r: specs[r["event"]]["change_type"]),
            "size": breakdown(pros, lambda r: ("1" if specs[r["event"]]["size"] <= 1 else
                                               "2-5" if specs[r["event"]]["size"] <= 5 else "6+")),
            "retroactive": breakdown(pros, lambda r: bool(specs[r["event"]]["retroactive"])),
            "traps": breakdown(pros, lambda r: bool(specs[r["event"]]["traps"])),
        }
    out["real"] = {"documents": {name: rates(real_docs, name) for name in ARMS},
                   "regulations": {name: rates([r for k, r in real1.items() if reg(k)], name) for name in ARMS},
                   "pkb": {name: rates([r for k, r in real1.items() if k.startswith("PKB-")], name) for name in ARMS},
                   "distractors": rates([r for k, r in real1.items() if dis(k)])}
    if real_docs:
        s_p = sum(r["outcome"] == "silent_error" for r in real_docs)
        s_b3 = sum(r["B3"] == "silent_error" for r in real_docs)
        out["real"]["same_direction"] = {"ser_pipeline": s_p, "ser_b3": s_b3, "ok": s_p <= s_b3}
        out["real"]["by_change_type"] = breakdown([r for k, r in real1.items() if reg(k)],
                                                  lambda r: events[r["event"]]["jenis_perubahan"])
        out["real"]["by_retroactive"] = breakdown([r for k, r in real1.items() if reg(k)],
                                                  lambda r: events[r["event"]]["berlaku_surut"])
    both = sorted(k for k in real2 if k in real1)
    if both:
        out["run_to_run"] = {"n": len(both), "same_outcome": sum(real1[k]["outcome"] == real2[k]["outcome"]
                                                                 for k in both),
                             "pairs": {k: (real1[k]["outcome"], real2[k]["outcome"]) for k in both},
                             "run2": rates([real2[k] for k in both])}
    for label, son, ref in (("sonnet_real", son_r, real1), ("sonnet_prospective", son_p,
                                                            scores("isolated-prospective"))):
        common = sorted(k for k in son if k in ref)
        if common:
            xs, ys = [ref[k]["outcome"] for k in common], [son[k]["outcome"] for k in common]
            out[label] = {"n": len(common), "agreement": sum(x == y for x, y in zip(xs, ys)) / len(common),
                          "kappa": kappa(xs, ys), "gpt": dict(Counter(xs)), "sonnet": dict(Counter(ys)),
                          "pairs": {k: (ref[k]["outcome"], son[k]["outcome"]) for k in common}}
    fails = []
    for stage, rows in (("prospective", pros), ("real-1", real1.values()), ("real-2", real2.values())):
        for r in rows:
            if r["outcome"] != "correct":
                fails.append({"stage": stage, "event": r["event"], "outcome": r["outcome"], "status": r["status"],
                              "note": r["note"], "wrong_tuples": r["wrong_tuples"], "tuples": r["tuples"],
                              "drafts": r["drafts"], "top": r["top"], "relevant": r["relevant"]})
    out["failures"] = fails
    out["cost_usd"] = {st: round(sum(r.get("cost_usd") or 0 for r in scores(st).values()), 4)
                       for st in ("isolated-prospective", "isolated-real-1", "isolated-real-2", "sonnet-real",
                                  "sonnet-prospective")}
    return out


def posthoc_policy():
    """Post-hoc sensitivity (not preregistered): a memo amending a policy in force gets its rules' policy renamed from
    the memo's id to the policy in force, then the selected update is scored again. No model calls."""
    import copy
    from . import measure
    from .isolated import set_dictionary
    specs = {s["id"]: s for s in prospective.specs()}
    rows = scores("isolated-prospective")
    pool = {u.event.id: u for u in measure.prospective_units()}
    changed = {}
    for eid, r in rows.items():
        spec = specs[eid]
        if spec["layer"] != "company" or spec["policy"] == eid or r["outcome"] != "silent_error":
            continue
        res = json.loads((MEASURED / "isolated-prospective" / "results" / f"{eid}.json").read_text(encoding="utf-8"))
        d = copy.deepcopy(res.get("delta"))
        for op in ("add", "change"):
            for e in (d or {}).get(op, []):
                if e.get("policy") == eid:
                    e["policy"] = spec["policy"]
        u = pool[eid]
        set_dictionary(u.extra.get("fields"))
        want = score.Behaviour(gold.apply(u.base, u.expected, update_id="GOLD"))
        changed[eid] = score.score_delta(u.base, d, want, u.cases, gold.omegas(u.event)).outcome
    set_dictionary(None)
    after = [dict(r, outcome=changed.get(k, r["outcome"])) for k, r in rows.items()]
    return {"rescored": changed, "rates": rates(after),
            "ser_upper95_one_sided": clopper_pearson(sum(r["outcome"] == "silent_error" for r in after), len(after),
                                                     sided=1)[1]}


# ------------------------------------------------------------------------------------------------------- chains
def real_chains():
    return [c for c in chain.chains() if c.id in REAL_COMPANIES]


def panels_of(c):
    return {i.id: instances.panel(i, fields=units.fields_of(i)) for i in c.members}


def _key(r):
    return f"{r['case_id']}|{r['year']}|{r['month']}"


def code_rows(c, panels=None):
    """Payslip rows of the code scenario (independent of the model), cached per chain."""
    path = OUT / f"code_rows_{c.id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    log = [{"event": s.event.id, "instance": s.instance, "delta": None} for s in chain.stream(c.members, c.start)]
    acc = chain.accuracy(c, chain.replay(c, log, "code"), panels or panels_of(c))
    OUT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(acc), encoding="utf-8")
    return acc


def _steps(c):
    """Steps of a chain with the members each one reaches."""
    out = []
    for s in chain.stream(c.members, c.start):
        targets = [i.id for i in c.members] if s.instance is None else [s.instance]
        out.append((s.event, targets))
    return out


def window_owner(steps, member, payroll):
    """The step whose code-scenario delay covers a payroll date for a member: issued on or before it, known to the
    code scenario only after it (the latest such step with a gold update)."""
    best = None
    for ev, targets in steps:
        if member in targets and ev.gold and ev.issued <= payroll < ev.issued + timedelta(days=chain.HR_DAYS):
            best = ev.id
    return best


def gains_by_step(c, code):
    """Payslips the code scenario gets wrong at payroll, attributed to the step whose delay covers the payroll
    date (the gain of a correct update applied on its issue day)."""
    steps = _steps(c)
    out, other = Counter(), 0
    for member, rows in code.items():
        for r in rows:
            if not r["at_payroll"]:
                owner = window_owner(steps, member, score.payroll_date(r["year"], r["month"]))
                if owner:
                    out[owner] += 1
                else:
                    other += 1
    return out, other


def reach_from_dev():
    """Share of wrong (case, knowledge date) tuples of every development silent error (tags 1-4): how much of a
    company's payroll one wrong update reaches."""
    out = []
    for stage in ("dev-1", "dev-2", "dev-3", "dev-4-company"):
        for r in scores(stage).values():
            if r["outcome"] == "silent_error" and r["tuples"]:
                out.append(r["wrong_tuples"] / r["tuples"])
    return out


def power(sims=1000, boots=1000, seed=20261116):
    """H1 power: per event-chain pair an outcome is drawn from the development rates (Dirichlet with a Jeffreys
    prior on the final development counts, and on tag 3 as a sensitivity); a correct update gains the payslips the
    code scenario gets wrong in its delay window, an abstention changes nothing (HR applies the gold update on the
    code scenario's day), and a silent error loses a share r of the member's payslips from its issue month to the
    end of the window (no later correction: conservative), r drawn from the reach of the development silent
    errors. The test is the preregistered clustered bootstrap of (pipeline - code) over the pairs."""
    rng = random.Random(seed)
    pairs, total = [], 0
    for c in real_chains():
        code = code_rows(c)
        gains, _ = gains_by_step(c, code)
        total += sum(len(rows) for rows in code.values())
        for ev, targets in _steps(c):
            if not ev.gold or ev.part not in ("test", "company"):
                continue
            later = sum(1 for m in targets for r in code[m]
                        if score.payroll_date(r["year"], r["month"]) >= ev.issued)
            pairs.append((c.id, ev.id, gains.get(ev.id, 0), later))
    reach = reach_from_dev() or [0.1]
    rate_sets = {"final development (16 correct, 1 abstain, 0 silent)": (16, 1, 0),
                 "tag 3 (14 correct, 1 abstain, 2 silent)": (14, 1, 2)}
    out = {"pairs": len(pairs), "payslips": total, "reach": reach, "results": {}}
    for label, counts in rate_sets.items():
        hits, diffs = 0, []
        for _ in range(sims):
            g = [rng.gammavariate(x + 0.5, 1) for x in counts]
            p = [x / sum(g) for x in g]
            contrib = []
            for _, _, gain, later in pairs:
                u = rng.random()
                if u < p[0]:
                    contrib.append(gain)
                elif u < p[0] + p[1]:
                    contrib.append(0)
                else:
                    contrib.append(-rng.choice(reach) * later)
            diff = sum(contrib) / total
            diffs.append(diff)
            bs = sorted(sum(rng.choice(contrib) for _ in contrib) / total for _ in range(boots))
            if bs[int(0.025 * boots)] > -0.01:
                hits += 1
        diffs.sort()
        out["results"][label] = {"power": hits / sims, "median_diff": diffs[sims // 2],
                                 "diff_p05": diffs[int(0.05 * sims)], "diff_p95": diffs[int(0.95 * sims)]}
    return out


def in_chain_errors(c, log, panels):
    """Steps whose applied system update differs from the gold update on the chain's own knowledge base (base
    condition), judged on the members' panels for the event's years at both knowledge dates."""
    events = {s.event.id: s.event for s in chain.stream(c.members, c.start)}
    reg = gold.chain().known_on(c.start)
    kbs = {i.id: reg for i in c.members}
    wrong = {}
    for row in log:
        ev = events[row["event"]]
        targets = list(kbs) if row["instance"] is None else [row["instance"]]
        update, how = (row["delta"], "system") if row["delta"] is not None else (None, "none")
        if update is None and ev.gold:
            update, how = chain.shifted(gold.delta(ev.gold), chain.HR_DAYS), "hr"
        if how == "system":
            years = set(ts.event_years(ev)) if ev.layer != "company" else None
            for t in targets:
                cases = [x for x in panels[t] if years is None or x["tax_year"] in years]
                want = chain.lenient(kbs[t], gold.delta(ev.gold), "CHK-GOLD") if ev.gold else kbs[t]
                try:
                    got = chain.lenient(kbs[t], update, "CHK-SYS")
                    s = score.compare(score.Behaviour(got), score.Behaviour(want), cases, gold.omegas(ev))
                    bad = s.outcome != "correct"
                except Exception as e:  # noqa: BLE001 - an update that cannot be applied is an error
                    bad, s = True, score.Score("silent_error", note=str(e)[:200])
                if bad:
                    wrong.setdefault(ev.id, []).append({"member": t, "wrong_tuples": s.wrong_tuples,
                                                        "tuples": s.tuples, "note": s.note})
        if update is not None:
            for t in targets:
                kbs[t] = chain.lenient(kbs[t], update, f"{ev.id}-{how}")
    return wrong


def chains_report(boots=10_000, seed=20261116, out_dir=None, ids=None):
    """out_dir: the chain logs (default the measured ones); ids: only these chains (an exploratory replay)."""
    out_dir = out_dir or MEASURED / "chains"
    rng = random.Random(seed)
    iso = {k: (v["outcome"], scores("isolated-real-2").get(k, {}).get("outcome"))
           for k, v in scores("isolated-real-1").items()}
    report, clusters, total_slips = {"chains": {}}, [], 0
    for c in chain.chains():
        path = out_dir / f"{c.id}.jsonl"
        if not path.exists() or (ids and c.id not in ids):
            continue
        log = chain.load(out_dir, c)
        panels = panels_of(c)
        accs = {cond: chain.accuracy(c, chain.replay(c, log, cond), panels) for cond in ("base", "none", "careful")}
        accs["code"] = code_rows(c, panels) if c.id in REAL_COMPANIES else chain.accuracy(
            c, chain.replay(c, log, "code"), panels)
        wrong = in_chain_errors(c, log, panels)
        rep = {"steps": len(log), "statuses": dict(Counter(r["status"] for r in log)),
               "hr_interventions_base": sum(r["delta"] is None and events_gold(c, r["event"]) for r in log),
               "in_chain_errors": wrong, "cost_usd": round(sum(r.get("cost_usd") or 0 for r in log), 4),
               "accuracy": {}}
        for cond, acc in accs.items():
            rows = [r for rs in acc.values() for r in rs]
            rep["accuracy"][cond] = {"payslips": len(rows),
                                     "at_payroll": sum(r["at_payroll"] for r in rows) / len(rows),
                                     "at_end": sum(r["at_end"] for r in rows) / len(rows)}
        if c.id in REAL_COMPANIES:
            steps = _steps(c)
            code = {m: {_key(r): r for r in rows} for m, rows in accs["code"].items()}
            contrib, unattributed = Counter(), 0
            for m, rows in accs["base"].items():
                for r in rows:
                    a, b = r["at_payroll"], code[m][_key(r)]["at_payroll"]
                    if a == b:
                        continue
                    pay = score.payroll_date(r["year"], r["month"])
                    if a and not b:
                        owner = window_owner(steps, m, pay)
                    else:
                        cands = [ev.id for ev, t in steps if m in t and ev.issued <= pay and ev.id in wrong]
                        owner = cands[-1] if cands else None
                    if owner is None:
                        unattributed += 1 if a else -1
                    else:
                        contrib[owner] += 1 if a else -1
            n = sum(len(rs) for rs in accs["base"].values())
            total_slips += n
            pairs = [ev.id for ev, _ in steps if (ev.gold and ev.part in ("test", "company")) or contrib[ev.id]]
            clusters += [contrib[e] for e in pairs]
            rep["pairs"] = len(pairs)
            rep["unattributed"] = unattributed
            report.setdefault("unattributed", 0)
            report["unattributed"] += unattributed
        report["chains"][c.id] = rep
    if clusters:
        base = sum(clusters) + report["unattributed"]
        bs = sorted((sum(rng.choice(clusters) for _ in clusters) + report["unattributed"]) / total_slips
                    for _ in range(boots))
        report["H1"] = {"pairs": len(clusters), "payslips": total_slips, "diff": base / total_slips,
                        "ci95": (bs[int(0.025 * boots)], bs[int(0.975 * boots) - 1])}
        report["H1"]["a"] = report["H1"]["ci95"][0] > -0.01
        prop = {}
        for cid, rep in report["chains"].items():
            for ev in rep["in_chain_errors"]:
                prop.setdefault(ev, []).append(cid)
        systematic = [ev for ev, cs in prop.items()
                      if len(cs) >= 2 and iso.get(ev, (None, None)) == ("correct", "correct")]
        report["H1"]["systematic_propagation"] = systematic
        report["H1"]["b"] = not systematic
        report["H1"]["supported"] = report["H1"]["a"] and report["H1"]["b"]
    return report


def events_gold(c, event_id):
    for s in chain.stream(c.members, c.start):
        if s.event.id == event_id:
            return bool(s.event.gold)
    return False


# ------------------------------------------------------------------------------------------------------- main
def save(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("isolated", "posthoc", "code", "power", "chains"))
    ap.add_argument("--chain")
    a = ap.parse_args()
    if a.what == "isolated":
        r = isolated_report()
        save("isolated", r)
        print(json.dumps({k: r[k] for k in r if k in ("H2", "real", "run_to_run", "cost_usd")}, indent=1,
                         default=str)[:6000])
    elif a.what == "posthoc":
        r = posthoc_policy()
        save("posthoc_policy", r)
        print(json.dumps(r, indent=1, default=str))
    elif a.what == "code":
        for c in real_chains():
            if a.chain and c.id != a.chain:
                continue
            acc = code_rows(c)
            rows = [r for rs in acc.values() for r in rs]
            print(c.id, len(rows), sum(r["at_payroll"] for r in rows) / len(rows), flush=True)
    elif a.what == "power":
        r = power()
        save("power", r)
        print(json.dumps(r["results"], indent=1), r["pairs"], r["payslips"])
    else:
        r = chains_report()
        save("chains", r)
        print(json.dumps({k: v for k, v in r.items() if k != "chains"}, indent=1, default=str))
        for cid, rep in r["chains"].items():
            print(cid, rep["statuses"], rep["accuracy"], len(rep["in_chain_errors"]))
