"""Build the test space S^E and its expected values (PANDUAN Tahap 8).

    env\\Scripts\\python system\\tools\\build_se.py [--operational N] [--events E01,E02,...]

Writes dataset/14_ruang_uji/kasus.jsonl.gz (all cases with criterion and cell), laporan.json (coverage per year and
criterion), and harapan/<EVENT>.jsonl.gz: for every regulation event of the corpus (test, distractor, development)
the observations of K*_n on the cases of its years at omega = issue date, plus a 20% sample at issue date - 1 day
(A3 omega). K*_n is the gold chain up to the event's update (for a distractor or an event without update, the chain
known at its issue date). For the test policies (PKB and synthetic), kasus_kebijakan.jsonl.gz holds their cases and
harapan/<POLICY>.jsonl.gz the observations of the full chain with the gold policy at omega = 2026-10-27. Expected values can always be recomputed from the locked gold; the files carry their
SHA-256 in laporan.json.
"""
import argparse
import gzip
import hashlib
import json
import random
import sys
import time
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus, testspace  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

OUT = ROOT / "dataset" / "14_ruang_uji"
POLICY_OMEGA = date(2026, 10, 27)      # knowledge date of the regulation chain policies are scored on


def _v(v):
    return str(v) if isinstance(v, Fraction) else v


def observations(kb, case, omega):
    r = evaluate_case(kb, case, omega)
    obs = {f"{m}:{f}": _v(v) for m, row in r.periods.items() for f, v in row.items()}
    obs.update({f"0:{f}": _v(v) for f, v in r.year.items()})
    return {"case_id": case["case_id"], "omega": omega.isoformat(), "obs": obs,
            "conflicts": sorted(map(str, r.conflict_keys())), "errors": r.errors[:3]}


def gold_for(event, chain):
    gold = next((u for u in build_gold.collect() if u.event_id == event.id), None)
    if gold is not None:
        return chain.until(gold.delta_id)
    return build_gold.prefix_at(chain, event.issued.isoformat())


def policy_expected(chain, by_year, out, per_year):
    """Test policies (PKB and synthetic): cases of testspace.policy_cases (written to kasus_kebijakan.jsonl.gz) and
    the observations of the full regulation chain with the gold policy, at omega = POLICY_OMEGA."""
    side = {u.doc.id: u for u in build_gold.collect_side() if u.kind == "policy"}
    all_cases, hashes = [], {}
    for pe in corpus.policy_events():
        if pe.part not in ("uji", "sintetis") or pe.document not in side:
            continue
        t = time.time()
        pdelta = side[pe.document].to_json()
        cases = testspace.policy_cases(pe, pdelta, by_year, random.Random(f"se-{pe.id}"), per_year)
        kb = apply_delta(chain, pdelta)
        rows = [observations(kb, c, POLICY_OMEGA) for c in cases]
        all_cases += cases
        hashes[pe.id] = {"sha256": write_gz(out / "harapan" / f"{pe.id}.jsonl.gz", rows), "tuples": len(rows),
                         "years": sorted({c["tax_year"] for c in cases}), "omega": POLICY_OMEGA.isoformat()}
        print(f"{pe.id}: {len(rows)} tuples (policy), {time.time() - t:.0f}s", flush=True)
    hashes["kasus_kebijakan"] = {"sha256": write_gz(out / "kasus_kebijakan.jsonl.gz", all_cases),
                                 "cases": len(all_cases)}
    return hashes


def load_cases(out=OUT):
    return [json.loads(line) for line in gzip.open(out / "kasus.jsonl.gz", "rt", encoding="utf-8")]


def write_gz(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows).encode("utf-8")
    with gzip.GzipFile(filename=path.name, fileobj=open(path, "wb"), mode="wb", mtime=0) as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--operational", type=int, default=300)
    ap.add_argument("--events", default="")
    ap.add_argument("--policies-only", action="store_true")
    ap.add_argument("--policy-cases", type=int, default=60, help="cases per policy year")
    ap.add_argument("--set", choices=["test", "dev"], default="test",
                    help="test: tax years 2023-2026 (test events and distractors); dev: development years")
    args = ap.parse_args()
    years = testspace.YEARS if args.set == "test" else testspace.DEV_YEARS
    out = OUT if args.set == "test" else OUT / "pengembangan"
    chain = build_gold.load_graph()
    if args.policies_only:                  # policy tuples only, on the existing S^E cases
        cases = [json.loads(l) for l in gzip.open(out / "kasus.jsonl.gz", "rt", encoding="utf-8")]
        by_year = {}
        for c in cases:
            by_year.setdefault(c["tax_year"], []).append(c)
        rep = json.loads((out / "laporan.json").read_text(encoding="utf-8"))
        rep["events"].update(policy_expected(chain, by_year, out, args.policy_cases))
        (out / "laporan.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return
    t = time.time()
    cases, report = testspace.build(chain, operational_n=args.operational, years=years)
    print(f"S^E: {len(cases)} cases in {time.time() - t:.0f}s", flush=True)
    sha_cases = write_gz(out / "kasus.jsonl.gz", cases)
    by_year = {}
    for c in cases:
        by_year.setdefault(c["tax_year"], []).append(c)
    wanted = set(filter(None, args.events.split(",")))
    hashes = {}
    for ev in corpus.regulation_events():
        if wanted and ev.id not in wanted:
            continue
        if (ev.part == "pengembangan") != (args.set == "dev"):
            continue
        ev_years = testspace.event_years(ev, years)
        if not ev_years:
            continue
        kb = gold_for(ev, chain)
        rng = random.Random(f"{ev.id}-omega")
        rows = []
        t = time.time()
        for y in ev_years:
            for c in by_year.get(y, []):
                rows.append(observations(kb, c, ev.issued))
                if rng.random() < 0.2:
                    rows.append(observations(kb, c, ev.issued - timedelta(days=1)))
        hashes[ev.id] = {"sha256": write_gz(out / "harapan" / f"{ev.id}.jsonl.gz", rows), "tuples": len(rows),
                         "years": ev_years}
        print(f"{ev.id}: {len(rows)} tuples, years {ev_years}, {time.time() - t:.0f}s", flush=True)
    if args.set == "test" and not wanted:
        hashes.update(policy_expected(chain, by_year, out, args.policy_cases))
    rep = {"cases": len(cases), "cases_sha256": sha_cases, "per_year": report,
           "operational_source": str(testspace.BPS_WAGES.relative_to(ROOT)), "events": hashes,
           "gold_fingerprint": chain.fingerprint()}
    old = json.loads((out / "laporan.json").read_text(encoding="utf-8")) if (out / "laporan.json").exists() else {}
    if wanted and old.get("events"):
        old["events"].update(hashes)
        rep["events"] = old["events"]
    (out / "laporan.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
