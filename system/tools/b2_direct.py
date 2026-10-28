r"""E5, comparator B2 (skeleton: motivation): the LLM computes PPh 21 directly from the documents, without a knowledge
base, on operational cases of one tax year.

    env\Scripts\python system\tools\b2_direct.py <RUN> [--year 2025] [--n 100] [--limit USD] [--score-only]

Prefix (cached, the same for every case): the segments that the pipeline's selection gives for every document cited by
a gold record in force in the year (the documents a payroll officer would need that year), plus the extracted TER
tables of PP 58/2023. User message: one case as JSON (case data only; the cell and criterion labels of S^E are left
out). Output: monthly PPh 21 due and the annual PPh 21, as structured JSON. Reference: the gold chain at omega =
2026-10-27 (the knowledge base approach reproduces it by construction; its acquisition errors are measured in E2/E3).
Writes experiments/<RUN>/b2_hasil.csv and b2_ringkasan.json.
"""
import argparse
import csv
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs.analysis import stats  # noqa: E402
from pph21kbs.analysis.evaluate import se_cases  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.pipeline import llm, select  # noqa: E402
from pph21kbs.text import TEXT_DIR, registry  # noqa: E402

OMEGA = date(2026, 10, 27)
SYSTEM = """You are a payroll tax officer in Indonesia. Compute the income tax article 21 (PPh 21) to withhold from a
permanent employee (pegawai tetap) for every month of the tax year in the case, and the annual PPh 21, using only the
regulations given. Monthly amounts and the annual amount are whole rupiah. The case data follows the input convention
document given with the regulations. Return only the JSON object required by the schema."""
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["months", "annual_pph21"],
          "properties": {"months": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["month", "pph21_due"],
              "properties": {"month": {"type": "integer"}, "pph21_due": {"type": "integer"}}}},
              "annual_pph21": {"type": "integer"}}}


def documents_in_force(chain, year):
    view = chain.view(date(year, 12, 31))
    docs = set()
    for r in view.records:
        if r.valid_from and r.valid_from.year <= year and (r.valid_until is None or r.valid_until.year >= year):
            for s in getattr(r, "source", None) or []:
                d = s.get("document") if isinstance(s, dict) else getattr(s, "document", None)
                if d:
                    docs.add(d)
    return sorted(docs), view


def prefix_text(chain, year, budget_per_doc):
    docs, view = documents_in_force(chain, year)
    reg = registry()
    parts = []
    for d in docs:
        if not (TEXT_DIR / d / "teks.txt").exists():
            continue
        if (TEXT_DIR / d / "segmen.json").exists():
            body = select.render(select.select(d, view, budget_per_doc))
        else:                                   # short convention texts without segments go in whole
            body = (TEXT_DIR / d / "teks.txt").read_text(encoding="utf-8")
        parts.append(f"=== DOCUMENT {d}: {reg.get(d, {}).get('title', '')} ===\n{body}")
    for table in sorted((TEXT_DIR / "PP-58-2023" / "tabel").glob("*.csv")):
        parts.append(f"=== TABLE PP-58-2023 {table.stem} (extracted TER rates) ===\n"
                     + table.read_text(encoding="utf-8"))
    return "\n\n".join(parts), docs


def case_text(c):
    return json.dumps({k: v for k, v in c.items() if k not in ("cell", "criterion")}, ensure_ascii=False)


def observed(kb, case):
    r = evaluate_case(kb, case, OMEGA, outputs=["pph21_due", "annual_pph21"])
    return {m: row.get("pph21_due") for m, row in r.periods.items()}, r.year.get("annual_pph21")


def compare(months, annual, want_months, want_annual):
    exact = all(months.get(m) == v for m, v in want_months.items()) and annual == want_annual
    within1 = all(months.get(m) is not None and abs(months[m] - v) <= 1 for m, v in want_months.items()) and \
        annual is not None and want_annual is not None and abs(annual - want_annual) <= 1
    err = sum(abs((months.get(m) or 0) - v) for m, v in want_months.items())
    return exact, within1, err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--limit", type=float, default=15.0)
    ap.add_argument("--budget-per-doc", type=int, default=4000)
    ap.add_argument("--score-only", action="store_true")
    args = ap.parse_args()
    out = ROOT / "experiments" / args.run
    chain = build_gold.load_graph()
    pool = sorted((c for c in se_cases().values() if c["tax_year"] == args.year and c.get("criterion") == "operational"),
                  key=lambda c: c["case_id"])
    cases = random.Random(f"b2-{args.year}").sample(pool, min(args.n, len(pool)))
    answers_path = out / "b2_jawaban.jsonl"
    answers = {}
    if answers_path.exists():
        for line in answers_path.read_text(encoding="utf-8").splitlines():
            a = json.loads(line)
            answers[a["case_id"]] = a
    if not args.score_only:
        ledger = llm.Ledger(args.run, run_limit_usd=args.limit)
        client = llm.AnthropicClient(ledger)
        text, docs = prefix_text(chain, args.year, args.budget_per_doc)
        (out / "b2_dokumen.json").write_text(json.dumps(docs, indent=1) + "\n", encoding="utf-8")
        for c in cases:
            if c["case_id"] in answers:
                continue
            try:
                _, parsed, entry = client.complete(system=SYSTEM, prefix=[text], user="CASE:\n" + case_text(c),
                                                   schema=SCHEMA, schema_name="pph21", effort="high", step="b2",
                                                   document="B2", event=c["case_id"], call_id=f"{args.run}-{c['case_id']}")
            except llm.BudgetExceeded as e:
                print("budget:", e)
                break
            a = {"case_id": c["case_id"], "parsed": parsed, "error": entry["error"], "cost_usd": entry["cost_usd"]}
            answers[c["case_id"]] = a
            with open(answers_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
            print(c["case_id"], "ok" if parsed else entry["error"], entry["cost_usd"], flush=True)
    rows = []
    for c in cases:
        want_m, want_a = observed(chain, c)
        a = answers.get(c["case_id"])
        if a is None:
            continue
        p = a.get("parsed") or {}
        got_m = {x["month"]: x["pph21_due"] for x in p.get("months", [])}
        exact, within1, err = compare(got_m, p.get("annual_pph21"), want_m, want_a)
        rows.append({"case_id": c["case_id"], "answered": bool(p), "exact": exact, "within_1": within1,
                     "abs_error_months": err, "annual_want": want_a, "annual_got": p.get("annual_pph21"),
                     "cost_usd": a.get("cost_usd")})
    if not rows:
        return
    with open(out / "b2_hasil.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    k = sum(r["exact"] for r in rows)
    k1 = sum(r["within_1"] for r in rows)
    summary = {"year": args.year, "cases": n, "exact": k, "exact_rate": k / n, "exact_CI": stats.clopper_pearson(k, n),
               "within_1_rupiah": k1, "within_1_CI": stats.clopper_pearson(k1, n),
               "median_abs_error_months": sorted(r["abs_error_months"] for r in rows)[n // 2],
               "cost_usd": round(sum(r["cost_usd"] or 0 for r in rows), 4)}
    (out / "b2_ringkasan.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
