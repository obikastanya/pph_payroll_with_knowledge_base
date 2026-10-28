r"""PPh 21 calculator on the research knowledge base (gold chain dataset/12_emas/kb.trig).

    env\Scripts\python system\tools\calculate.py --year 2025 --salary 12000000 --ptkp K/1
    env\Scripts\python system\tools\calculate.py --year 2025 --salary 9500000 --klu 13921 --trace 3:pph21_due
    env\Scripts\python system\tools\calculate.py --case my_case.json --omega 2025-06-30 --json

A case is either a JSON file in the engine's case format (system/schemas/case.schema.json) or built from the options
below (the same salary every month of employment; THR and bonus in the stated month). --omega is the knowledge date:
the answer as the regulations known on that day give it (default: today). --policy installs a company policy of the
corpus (a side update of the gold, e.g. PKB-WIKA-2025 or SP03) on top of the regulations. --trace month:fact prints the
chain of rules, values and quoted sources behind one value.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

COLUMNS = ("base_salary", "thr", "bonus", "gross_income", "pph21_due", "pph21_dtp", "take_home_pay")


def build_case(a):
    periods = []
    for m in range(a.start_month, a.end_month + 1):
        inc = {"base_salary": a.salary}
        if a.allowance:
            inc["fixed_allowance"] = a.allowance
        if a.thr and m == a.thr_month:
            inc["thr"] = a.thr
        if a.bonus and m == a.bonus_month:
            inc["bonus"] = a.bonus
        ben = {"company_vehicle": a.vehicle} if a.vehicle else {}
        periods.append({"month": m, "income": inc, "benefits": ben, "zakat": 0})
    return {"case_id": "calculator", "tax_year": a.year, "method": a.method,
            "employee": {"ptkp_status": a.ptkp, "sex": a.sex, "tax_id_valid": not a.no_npwp},
            "employer": {"klu": a.klu, "jkk_risk_group": a.jkk_risk, "policy": a.policy},
            "employment": {"start_month": a.start_month, "end_month": a.end_month}, "periods": periods}


def knowledge_base(policy):
    kb = build_gold.load_graph()
    if policy:
        side = {u.doc.id: u for u in build_gold.collect_side() if u.kind == "policy"}
        if policy not in side:
            sys.exit(f"unknown policy {policy}; known: {', '.join(sorted(side))}")
        kb = apply_delta(kb, side[policy].to_json())
    return kb


def rupiah(v):
    return "" if v is None else f"{int(v):>14,}".replace(",", ".")


def print_trace(result, month, fact, depth=0, seen=None):
    seen = set() if seen is None else seen
    t = (result.trace or {}).get((fact, month)) or (result.trace or {}).get((fact, 0))
    if t is None or (fact, month) in seen:
        return
    seen.add((fact, month))
    src = "; ".join(dict.fromkeys(f"{s['document']} {s['provision']}" for s in t.get("source") or []))
    print(f"{'  ' * depth}{fact} = {t['value']}  [{t['rule']}, {t['layer']}/{t['modality']}]  {src}")
    for dep in t.get("reads") or []:              # (fact, month); month 0 = annual
        dep_fact, dep_month = dep if isinstance(dep, (list, tuple)) else (dep, month)
        print_trace(result, dep_month, dep_fact, depth + 1, seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", help="case JSON file (engine format)")
    ap.add_argument("--year", type=int, default=date.today().year)
    ap.add_argument("--salary", type=int, default=0, help="base salary per month")
    ap.add_argument("--allowance", type=int, default=0, help="fixed allowance per month")
    ap.add_argument("--ptkp", default="TK/0")
    ap.add_argument("--sex", default="M", choices=["M", "F"])
    ap.add_argument("--method", default="gross", choices=["gross", "gross_up", "employer_borne"])
    ap.add_argument("--klu", default=None, help="business classification code of the employer")
    ap.add_argument("--jkk-risk", default="very_low",
                    choices=["very_low", "low", "medium", "high", "very_high"])
    ap.add_argument("--thr", type=int, default=0)
    ap.add_argument("--thr-month", type=int, default=4)
    ap.add_argument("--bonus", type=int, default=0)
    ap.add_argument("--bonus-month", type=int, default=12)
    ap.add_argument("--vehicle", type=int, default=0, help="company vehicle benefit per month (in kind)")
    ap.add_argument("--start-month", type=int, default=1)
    ap.add_argument("--end-month", type=int, default=12)
    ap.add_argument("--no-npwp", action="store_true")
    ap.add_argument("--policy", default=None, help="company policy document id of the corpus")
    ap.add_argument("--omega", default=None, help="knowledge date YYYY-MM-DD (default today)")
    ap.add_argument("--trace", default=None, help="month:fact, e.g. 3:pph21_due (month 0 = annual)")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    a = ap.parse_args()
    case = json.loads(Path(a.case).read_text(encoding="utf-8")) if a.case else build_case(a)
    omega = date.fromisoformat(a.omega) if a.omega else date.today()
    kb = knowledge_base(a.policy or case.get("employer", {}).get("policy"))
    r = evaluate_case(kb, case, omega, trace=bool(a.trace))
    if a.json:
        print(json.dumps({"periods": r.periods, "year": r.year, "conflicts": r.conflicts, "errors": r.errors},
                         default=str, indent=1))
        return
    print(f"PPh 21 {case['tax_year']} | PTKP {case['employee']['ptkp_status']} | method {case['method']} | "
          f"knowledge date {omega}")
    print(f"{'month':>5}" + "".join(f"{c:>16}" for c in COLUMNS))
    for m in sorted(r.periods):
        print(f"{m:>5}" + "".join(f"{rupiah(r.periods[m].get(c)):>16}" for c in COLUMNS))
    for k in ("annual_gross", "job_expense", "ptkp_amount", "taxable_income", "annual_pph21", "refund_to_employee"):
        if k in r.year:
            print(f"{k:>20}: {rupiah(r.year[k])}")
    for c in r.conflicts:
        print("conflict:", c)
    for e in r.errors:
        print("error:", e)
    if a.trace:
        month, fact = a.trace.split(":", 1)
        print("\ntrace:")
        print_trace(r, int(month), fact)


if __name__ == "__main__":
    main()
