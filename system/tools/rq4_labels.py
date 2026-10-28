"""RQ4 (cross-layer impact): execution labels of every (policy, event) pair and the detectors' predictions.

    env\\Scripts\\python system\\tools\\rq4_labels.py [--per-year N]

Pairs: the test policies (5 PKB, 14 synthetic) x the test events E01-E13 whose legal start falls within the policy's
term (labelling rule of dataset/10_kebijakan_perusahaan/sintetis/README.md). For each pair, on cases with the policy
(testspace.policy_cases) evaluated at omega = the event's issue date, K*_{n-1} (+) P is compared with K*_n (+) P:
  (a) a fact produced by the policy's rules changes value in a period from the event's start on;
  (b) the winning rule of a fact the policy's rules produce or read changes (same periods);
  (c) a new conflict entry involves the policy.
Predictions: the static detector on Delta*_n (pph21kbs.impact.detect), B5(i) flag every policy touching F_Delta
downstream, B5(ii) flat text scan of the Delta's produced facts in the policy's expressions. Writes
docs/hasil/rq4_label.csv and rq4_ringkasan.json (recall, precision, F2 with event-cluster bootstrap; Cohen's kappa of
label (c) against the manual labels of the synthetic policies).
"""
import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus, impact, testspace  # noqa: E402
from pph21kbs.analysis import stats  # noqa: E402
from pph21kbs.analysis.agreement import cohen_kappa  # noqa: E402
from pph21kbs.analysis.evaluate import se_cases  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

OUT = ROOT / "docs" / "hasil"


def _run(kb, case, omega, facts):
    view = kb.view(omega)
    outs = sorted({f.id for f in view.facts.values() if f.output} | {f for f in facts if f in view.facts})
    return evaluate_case(kb, case, omega, outputs=outs)


def exec_labels(k_prev, k_new, policy_rules, cases, event):
    produced = {r.produces for r in policy_rules}
    read = set()
    for r in policy_rules:
        for e in (r.expression, r.condition):
            if e is not None:
                read |= e.dependencies()
    ids = {r.id for r in policy_rules}
    start = event.effective_from or event.issued
    a = b = c = False
    for case in cases:
        r0 = _run(k_prev, case, event.issued, produced)
        r1 = _run(k_new, case, event.issued, produced)
        final = max(r1.periods) if r1.periods else 12
        late = {m for m in r1.periods if date(case["tax_year"], m, 1) >= date(start.year, start.month, 1)}
        if not a:
            for m in late:
                if any((r0.periods.get(m) or {}).get(f) != (r1.periods.get(m) or {}).get(f) for f in produced
                       if f in r1.periods.get(m, {})):
                    a = True
                    break
            if not a and date(case["tax_year"], final, 1) >= date(start.year, start.month, 1):
                a = any(r0.year.get(f) != r1.year.get(f) for f in produced if f in r1.year)
        if not b:
            for (fact, month), rid in r1.winners.items():
                if fact in produced | read and (month == 0 or month in late) and r0.winners.get((fact, month)) != rid:
                    b = True
                    break
        if not c:
            old = r0.conflict_keys()
            c = any((x.get("source") in ids or set(x.get("company_rules") or ()) & ids) and _key(x) not in old
                    for x in r1.conflicts)
        if a and b and c:
            break
    return a, b, c


def _key(x):
    from pph21kbs.engine import conflict_key
    return conflict_key(x)


def flat_scan(kb_new, update_id, policy_rules):
    produced = {r.produces for r in kb_new.records if r.update_id == update_id and hasattr(r, "produces")}
    names = {getattr(r, "name", None) for r in kb_new.records if r.update_id == update_id} - {None}
    for r in policy_rules:
        text = " ".join(e.text for e in (r.expression, r.condition) if e is not None)
        if any(f in text for f in produced | names) or r.produces in produced:
            return True
    return False


def manual_labels():
    out = {}
    for path in (ROOT / "dataset/10_kebijakan_perusahaan/sintetis").glob("SP*.json"):
        d = json.loads(path.read_text(encoding="utf-8"))
        for lab in d.get("label_dampak", []):
            ev = lab.get("peristiwa") or lab.get("event")
            out[(d["id"], ev)] = (lab.get("terdampak") == "ya", "".join(lab.get("tipe") or []))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-year", type=int, default=40)
    args = ap.parse_args()
    chain = build_gold.load_graph()
    ids = [u.update_id for u in chain.updates]
    gold_of = {u.event_id: u.delta_id for u in build_gold.collect() if u.event_id}
    cases_by_year = defaultdict(list)
    for c in se_cases().values():
        cases_by_year[c["tax_year"]].append(c)
    events = [e for e in corpus.regulation_events() if e.part == "uji" and e.id in gold_of]
    side = {u.doc.id: u for u in build_gold.collect_side() if u.kind == "policy"}
    manual = manual_labels()
    rows = []
    for pe in corpus.policy_events():
        if pe.part not in ("uji", "sintetis") or pe.document not in side:
            continue
        pdelta = side[pe.document].to_json()
        rng = random.Random(f"rq4-{pe.id}")
        cases = testspace.policy_cases(pe, pdelta, cases_by_year, rng, args.per_year)
        p_start = pe.effective_from or pe.issued
        p_end = pe.effective_until or date(2026, 12, 31)
        for ev in events:
            start = ev.effective_from or ev.issued
            if not (p_start <= start <= p_end):
                continue
            n = ids.index(gold_of[ev.id])
            k_prev = apply_delta(chain.until(ids[n - 1]), pdelta)
            k_new = apply_delta(chain.until(ids[n]), pdelta)
            rules = [r for r in k_new.view(ev.issued).rules.values() if r.policy == pe.document]
            ev_cases = [c for c in cases if start.year - 1 <= c["tax_year"] <= (ev.effective_until or
                                                                                  date(2026, 12, 31)).year]
            a, b, c = exec_labels(k_prev, k_new, rules, ev_cases, ev)
            det = impact.detect(k_new, gold_of[ev.id], [pe.document], ev.issued, remote=True)[pe.document]["kinds"]
            det2 = impact.detect(k_new, gold_of[ev.id], [pe.document], ev.issued, remote=True,
                                 query="impact_policy_v2")[pe.document]["kinds"]
            b5i = impact.flag_all(k_new, gold_of[ev.id], [pe.document], ev.issued, remote=True)[pe.document]
            b5ii = flat_scan(k_new, gold_of[ev.id], rules)
            man = manual.get((pe.id, ev.id))
            rows.append({"policy": pe.id, "part": pe.part, "event": ev.id, "cases": len(ev_cases),
                         "a": a, "b": b, "c": c, "positive": a or b or c,
                         "detector": bool(det), "detector_kinds": "".join(sorted(det)), "b5_flag_all": b5i,
                         "detector_v2": bool(det2), "detector_v2_kinds": "".join(sorted(det2)),
                         "b5_flat_scan": b5ii, "manual": "" if man is None else man[0],
                         "manual_type": "" if man is None else man[1]})
            print(f"{pe.id} {ev.id}: exec a={a} b={b} c={c} | detector {''.join(sorted(det)) or '-'} | "
                  f"B5i {b5i} B5ii {b5ii} | manual {man}", flush=True)
    with open(OUT / "rq4_label.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summary = {"pairs": len(rows), "positives": sum(r["positive"] for r in rows)}
    clusters = defaultdict(list)
    for r in rows:
        clusters[r["event"]].append(r)
    for name in ("detector", "detector_v2", "b5_flag_all", "b5_flat_scan"):
        def f2(rs, name=name):
            tp = sum(r[name] and r["positive"] for r in rs)
            fp = sum(r[name] and not r["positive"] for r in rs)
            fn = sum((not r[name]) and r["positive"] for r in rs)
            p = tp / (tp + fp) if tp + fp else None
            rec = tp / (tp + fn) if tp + fn else None
            return p, rec, stats.f_beta(p, rec) if p is not None and rec is not None else None
        p, rec, f = f2(rows)
        summary[name] = {"precision": p, "recall": rec, "F2": f,
                         "F2_CI": stats.cluster_bootstrap(clusters, lambda rs: f2(rs)[2], b=1000),
                         "recall_CI": stats.cluster_bootstrap(clusters, lambda rs: f2(rs)[1], b=1000)}
    def f2_of(rs, name):
        tp = sum(r[name] and r["positive"] for r in rs)
        fp = sum(r[name] and not r["positive"] for r in rs)
        fn = sum((not r[name]) and r["positive"] for r in rs)
        p = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        return stats.f_beta(p, rec) if p and rec else 0.0
    for det_name in ("detector", "detector_v2"):          # H4b: paired differences with event-cluster bootstrap
        for other in ("b5_flag_all", "b5_flat_scan"):
            summary[f"F2_diff_{det_name}_minus_{other}"] = {
                "diff": f2_of(rows, det_name) - f2_of(rows, other),
                "CI": stats.cluster_bootstrap(clusters, lambda rs, a=det_name, b=other: f2_of(rs, a) - f2_of(rs, b),
                                              b=2000)}
    prev = summary["positives"] / summary["pairs"] if summary["pairs"] else 0
    summary["prevalence"] = prev
    summary["F2_flag_everything"] = stats.f2_flag_all(prev) if prev else None
    paired = [(r["manual"], r["c"]) for r in rows if r["manual"] != ""]
    summary["kappa_c_vs_manual_any"] = cohen_kappa([(m, x) for m, x in paired])
    summary["kappa_positive_vs_manual"] = cohen_kappa([(r["manual"], r["positive"]) for r in rows
                                                       if r["manual"] != ""])
    (OUT / "rq4_ringkasan.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
