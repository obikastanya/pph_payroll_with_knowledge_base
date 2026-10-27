"""Classify the mutants that survive S^E, and add targeted cases for the killable ones (PANDUAN Tahap 8 / prareg 5).

    env\\Scripts\\python system\\tools\\mutation_equivalence.py [--events E04,E06]

For every mutant with status survived in docs/hasil/mutasi.csv, gold K_{n-1} (+) Delta*_n and the mutant are compared
on S^G generated for the gold Delta and for the mutant Delta (the generator of the gates: attribute values of the
rules, thresholds, table keys, the month each element starts), at both knowledge dates of S^G. A mutant that differs
on some case is killable: S^E missed it, and the first distinguishing case is added to S^E as a targeted case
(dataset/14_ruang_uji/kasus_terarah.jsonl.gz, criterion targeted_mutation) with its expected values appended to
harapan/<EVENT>.jsonl.gz. A mutant that behaves like the gold on all of them is classified likely equivalent (the
generator explores every literal the changed element reads, so a behavioural difference would have to come from a
value outside those). Writes docs/hasil/mutasi_kesetaraan.csv. Targeted cases come from the gold only, never from LLM
output, and are added before any test event is run.
"""
import argparse
import csv
import gzip
import json
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
import build_se  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402
from pph21kbs.mutation import mutants_of, observations  # noqa: E402
from pph21kbs.pipeline import gates, sg  # noqa: E402

SE = ROOT / "dataset" / "14_ruang_uji"
TARGETED = SE / "kasus_terarah.jsonl.gz"


def _load(path):
    if not path.exists():
        return []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sg(base, delta, issued):
    try:
        kb2 = apply_delta(base, delta)
    except Exception:  # noqa: BLE001 - a stillborn mutant has no S^G
        return None, []
    starts, s_d = gates.effect_start(base, delta)
    return kb2, sg.generate(base, kb2, delta, s_d, issued, starts=starts).cases


def distinguishing(base, gold, mutant, issued):
    kb_g, cases_g = _sg(base, gold, issued)
    kb_m, cases_m = _sg(base, mutant, issued)
    if kb_m is None:
        return None
    for case in cases_g + cases_m:
        for omega in (issued - timedelta(days=1), issued):
            try:
                a = observations(kb_g, case, omega)
            except Exception:  # noqa: BLE001 - the gold fails on this generated case: not usable
                continue
            try:
                b = observations(kb_m, case, omega)
            except Exception:  # noqa: BLE001 - an engine failure on the mutant only is a difference
                return case, omega
            if a != b:
                return case, omega
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default="")
    args = ap.parse_args()
    wanted = set(filter(None, args.events.split(",")))
    rows = list(csv.DictReader(open(ROOT / "docs/hasil/mutasi.csv", encoding="utf-8")))
    surv = [r for r in rows if r["status"] == "survived" and (not wanted or r["event"] in wanted)]
    chain = build_gold.load_graph()
    ids = [u.update_id for u in chain.updates]
    gold = {u.event_id: u for u in build_gold.collect() if u.kind == "event"}
    targeted = {c["case_id"]: c for c in _load(TARGETED)}
    out, new_rows = [], {}
    for ev_id in sorted({r["event"] for r in surv}):
        u = gold[ev_id]
        d = u.to_json()
        base = chain.until(ids[ids.index(u.delta_id) - 1])
        ev = corpus.event(ev_id)
        muts = {(m.element, m.operator, m.detail): m for m in mutants_of(d)}
        kb_star = chain.until(u.delta_id)
        for r in [r for r in surv if r["event"] == ev_id]:
            m = muts.get((r["element"], r["operator"], r["detail"]))
            if m is None:
                continue
            res = distinguishing(base, d, m.delta, ev.issued)
            status = "likely_equivalent" if res is False else ("stillborn" if res is None else "killable")
            row = {"event": ev_id, "element": r["element"], "operator": r["operator"], "detail": r["detail"],
                   "classification": status, "targeted_case": ""}
            if status == "killable":
                case, omega = res
                case = json.loads(json.dumps(case))
                case["case_id"] = f"T-{ev_id}-{len([c for c in targeted if c.startswith(f'T-{ev_id}-')]):03d}"
                case["criterion"] = "targeted_mutation"
                targeted[case["case_id"]] = case
                row["targeted_case"] = case["case_id"]
                exp = [build_se.observations(kb_star, case, ev.issued),
                       build_se.observations(kb_star, case, ev.issued - timedelta(days=1))]
                new_rows.setdefault(ev_id, []).extend(exp)
            out.append(row)
            print(f"{ev_id} {r['element']} {r['operator']} ({r['detail']}): {status} {row['targeted_case']}",
                  flush=True)
    build_se.write_gz(TARGETED, list(targeted.values()))
    rep_path = SE / "laporan.json"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    for ev_id, extra in new_rows.items():
        path = SE / "harapan" / f"{ev_id}.jsonl.gz"
        tuples = _load(path) + extra
        rep["events"][ev_id].update(sha256=build_se.write_gz(path, tuples), tuples=len(tuples))
    rep["events"]["kasus_terarah"] = {"cases": len(targeted)}
    rep_path.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    path = ROOT / "docs/hasil/mutasi_kesetaraan.csv"
    old = [r for r in csv.DictReader(open(path, encoding="utf-8"))] if path.exists() and wanted else []
    done = {(r["event"], r["element"], r["operator"], r["detail"]) for r in out}
    old = [r for r in old if (r["event"], r["element"], r["operator"], r["detail"]) not in done]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(old + out)
    n = {k: sum(r["classification"] == k for r in out) for k in ("killable", "likely_equivalent", "stillborn")}
    print(json.dumps(n))


if __name__ == "__main__":
    main()
