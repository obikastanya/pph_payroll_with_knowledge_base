"""Command line for the PPh 21 knowledge-based system.

    python cli.py calculate --year 2024 --salary 15000000 --ptkp K/1 --thr 15000000 --thr-month 3
    python cli.py calculate --year 2024 --salary 15000000 --ptkp K/1 --trace 1:pph21_due --omega 2023-12-01
    python cli.py acquire examples/documents/SP09.txt --title "Sample company regulation" --issued 2023-08-01 --company
    python cli.py check
    python cli.py graphdb

calculate  PPh 21 of one employee for one tax year, from the starting knowledge base (data/kb/seed.trig), optionally
           with a sample company policy (data/policies). --omega is the knowledge date: the answer as the rules known
           on that day give it. --trace month:fact prints the rules, values, and quoted provisions behind one value.
acquire    Read a new document with the language model and propose an update (needs an Anthropic API key). Nothing
           is applied: the result is written to workspace/calls/cli/results/ for review.
check      Packages, API keys (presence only), the starting knowledge base and its SHACL validation, GraphDB.
graphdb    Load the ontology and the starting knowledge base into a running GraphDB repository (optional).
"""
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

from pph21kbs import config, documents, graph
from pph21kbs.engine import evaluate_case
from pph21kbs.kb import apply_delta

COLUMNS = ("base_salary", "thr", "bonus", "gross_income", "pph21_due", "pph21_dtp", "take_home_pay")
YEAR_VALUES = ("annual_gross", "job_expense", "ptkp_amount", "taxable_income", "annual_pph21", "refund_to_employee")


# --------------------------------------------------------------------------------------------------------- knowledge
def seed():
    return graph.read_trig(config.SEED_KB, "K")


def sample_policies():
    return sorted(p.stem for p in config.POLICIES.glob("*.json"))


def with_policy(kb, policy):
    if not policy:
        return kb
    path = config.POLICIES / f"{policy}.json"
    if not path.exists():
        sys.exit(f"unknown policy {policy}; sample policies: {', '.join(sample_policies())}")
    return apply_delta(kb, json.loads(path.read_text(encoding="utf-8")))


# --------------------------------------------------------------------------------------------------------- calculate
def simple_case(year, salary, ptkp="TK/0", allowance=0, thr=0, thr_month=4, bonus=0, bonus_month=12, vehicle=0,
                start_month=1, end_month=12, method="gross", sex="M", klu=None, jkk_risk="very_low",
                tax_id_valid=True, policy=None):
    """A case in the engine format (spec/schemas/case.schema.json): the same pay every month of employment, THR and
    bonus in their month."""
    periods = []
    for m in range(start_month, end_month + 1):
        income = {"base_salary": salary}
        if allowance:
            income["fixed_allowance"] = allowance
        if thr and m == thr_month:
            income["thr"] = thr
        if bonus and m == bonus_month:
            income["bonus"] = bonus
        periods.append({"month": m, "income": income, "benefits": {"company_vehicle": vehicle} if vehicle else {},
                        "zakat": 0})
    return {"case_id": "cli", "tax_year": year, "method": method,
            "employee": {"ptkp_status": ptkp, "sex": sex, "tax_id_valid": tax_id_valid},
            "employer": {"klu": klu, "jkk_risk_group": jkk_risk, "policy": policy},
            "employment": {"start_month": start_month, "end_month": end_month}, "periods": periods}


def rupiah(v):
    return "" if v is None else f"{int(v):,}"


def print_trace(result, month, fact, depth=0, seen=None):
    seen = set() if seen is None else seen
    t = (result.trace or {}).get((fact, month)) or (result.trace or {}).get((fact, 0))
    if t is None or (fact, month) in seen:
        return
    seen.add((fact, month))
    src = "; ".join(dict.fromkeys(f"{s['document']} {s['provision']}" for s in t.get("source") or []))
    print(f"{'  ' * depth}{fact} = {t['value']}  [{t['rule']}, {t['layer']}/{t['modality']}]  {src}")
    for dep in t.get("reads") or []:              # (fact, month); month 0 = the tax year
        dep_fact, dep_month = dep if isinstance(dep, (list, tuple)) else (dep, month)
        print_trace(result, dep_month, dep_fact, depth + 1, seen)


def cmd_calculate(a):
    case = json.loads(Path(a.case).read_text(encoding="utf-8")) if a.case else simple_case(
        a.year, a.salary, a.ptkp, a.allowance, a.thr, a.thr_month, a.bonus, a.bonus_month, a.vehicle, a.start_month,
        a.end_month, a.method, a.sex, a.klu, a.jkk_risk, not a.no_tax_id, a.policy)
    omega = date.fromisoformat(a.omega) if a.omega else date.today()
    kb = with_policy(seed(), a.policy or case.get("employer", {}).get("policy"))
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
    for k in YEAR_VALUES:
        if k in r.year:
            print(f"{k:>20}: {rupiah(r.year[k]):>14}")
    for c in r.conflicts:
        print("conflict:", c)
    for e in r.errors:
        print("error:", e)
    if a.trace:
        month, fact = a.trace.split(":", 1)
        print("\ntrace:")
        print_trace(r, int(month), fact)


# --------------------------------------------------------------------------------------------------------- acquire
def cmd_acquire(a):
    from pph21kbs import draft, pipeline
    src = Path(a.file)
    doc_id = a.id or re.sub(r"[^A-Za-z0-9]+", "-", src.stem).strip("-").upper()
    issued = date.fromisoformat(a.issued)
    if src.suffix.lower() == ".pdf":
        documents.add_document(doc_id, a.title, issued, pdf=src, company=a.company)
    else:
        documents.add_document(doc_id, a.title, issued, text=src.read_text(encoding="utf-8"), company=a.company)
    event = pipeline.Event(doc_id, (doc_id,), issued, "company" if a.company else "regulation", a.title)
    ledger = draft.Ledger("cli")
    client = draft.AnthropicClient(ledger)
    run_id = datetime.now().strftime("cli-%Y%m%d-%H%M%S")      # call ids of this run only, so its cost is its own
    res = pipeline.run_document(event, seed(), client, ledger, pipeline.Config(m=a.m), run_id=run_id,
                                policies=(doc_id,) if a.company else ())
    meaning = {"proposed": "proposed update (drafts agree; review it before applying)",
               "empty": "not relevant: the document does not change the calculation",
               "abstain": "the AI is not sure (drafts disagree or none passed the checks): formalise it by hand",
               "budget": "stopped by the spending limit"}
    print(f"result: {meaning.get(res['status'], res['status'])}")
    print(f"groups of drafts that behave the same: {res['groups']}   cost: USD {res['cost_usd']:.3f}")
    for d in res["drafts"]:
        failed = {g: v for g, v in d["gate_log"].items() if isinstance(v, str) and v.startswith("fail")}
        print(f"  draft {d['n']}: {'passed' if d['passed'] else 'failed'}"
              f"{' after repair' if d['repaired'] and d['passed'] else ''} {failed or ''}")
    if res.get("delta"):
        for part in ("add", "change", "remove"):
            for e in res["delta"][part]:
                print(f"  [{part}] {e.get('kind', '')} {e['id']}")
    print(f"record: {ledger.dir / 'results' / (doc_id + '.json')}")


# --------------------------------------------------------------------------------------------------------- check
def cmd_check(_a):
    ok = True
    for pkg in ("rdflib", "pyshacl", "jsonschema", "anthropic", "openai", "streamlit", "pandas", "plotly"):
        try:
            __import__(pkg)
            print(f"[ok]   package {pkg}")
        except ImportError:
            ok = False
            print(f"[fail] package {pkg} is not installed (pip install -r requirements.txt)")
    try:
        __import__("docling")
        print("[ok]   package docling (PDF upload), OCR engine:", documents.ocr_engine())
    except ImportError:
        print("[info] docling is not installed: PDF upload is unavailable, text files still work")
    for name, key in (("Anthropic (drafting updates)", config.anthropic_key()),
                      ("OpenAI (app assistant, optional)", config.openai_key())):
        print(f"[{'ok' if key else 'info'}]{'   ' if key else ' '}API key {name}: {'present' if key else 'absent'}")
    kb = seed()
    violations = graph.validate(kb)
    ok = ok and not violations
    print(f"[{'ok' if not violations else 'fail'}]{'   ' if not violations else ' '}starting knowledge base: "
          f"{len(kb.updates)} updates, {len(kb.records)} records, SHACL violations: {len(violations)}")
    print(f"[{'ok' if graph.graphdb_available() else 'info'}]{'   ' if graph.graphdb_available() else ' '}GraphDB at "
          f"{config.GRAPHDB_URL}: {'reachable' if graph.graphdb_available() else 'not running (optional)'}")
    sys.exit(0 if ok else 1)


# --------------------------------------------------------------------------------------------------------- graphdb
def cmd_graphdb(_a):
    if not graph.graphdb_available():
        sys.exit(f"GraphDB is not reachable at {config.GRAPHDB_URL}/repositories/{config.GRAPHDB_REPOSITORY}")
    size = graph.graphdb_load(seed())
    print(f"GraphDB repository {config.GRAPHDB_REPOSITORY}: {size} statements (ontology and starting knowledge base)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("calculate", help="PPh 21 of one employee for one tax year")
    c.add_argument("--case", help="case JSON file (engine format)")
    c.add_argument("--year", type=int, default=date.today().year)
    c.add_argument("--salary", type=int, default=0, help="base salary per month")
    c.add_argument("--allowance", type=int, default=0, help="fixed allowance per month")
    c.add_argument("--ptkp", default="TK/0", help="PTKP status on 1 January, e.g. TK/0, K/1")
    c.add_argument("--sex", default="M", choices=["M", "F"])
    c.add_argument("--method", default="gross", choices=["gross", "gross_up", "employer_borne"])
    c.add_argument("--klu", default=None, help="business classification code (KLU) of the employer")
    c.add_argument("--jkk-risk", default="very_low", choices=["very_low", "low", "medium", "high", "very_high"])
    c.add_argument("--thr", type=int, default=0, help="religious holiday allowance (THR)")
    c.add_argument("--thr-month", type=int, default=4)
    c.add_argument("--bonus", type=int, default=0)
    c.add_argument("--bonus-month", type=int, default=12)
    c.add_argument("--vehicle", type=int, default=0, help="company vehicle benefit per month (in kind)")
    c.add_argument("--start-month", type=int, default=1)
    c.add_argument("--end-month", type=int, default=12)
    c.add_argument("--no-tax-id", action="store_true", help="the employee has no valid NPWP/NIK")
    c.add_argument("--policy", default=None, help=f"sample company policy: {', '.join(sample_policies())}")
    c.add_argument("--omega", default=None, help="knowledge date YYYY-MM-DD (default today)")
    c.add_argument("--trace", default=None, help="month:fact, e.g. 3:pph21_due (month 0 = the tax year)")
    c.add_argument("--json", action="store_true", help="print the full result as JSON")
    c.set_defaults(run=cmd_calculate)
    q = sub.add_parser("acquire", help="propose an update from a new document (language model)")
    q.add_argument("file", help="PDF or text file")
    q.add_argument("--title", required=True)
    q.add_argument("--issued", required=True, help="issue date YYYY-MM-DD")
    q.add_argument("--id", default=None, help="document id (default: from the file name)")
    q.add_argument("--company", action="store_true", help="the document is a company policy")
    q.add_argument("--m", type=int, default=3, help="independent drafts")
    q.set_defaults(run=cmd_acquire)
    sub.add_parser("check", help="check the installation").set_defaults(run=cmd_check)
    sub.add_parser("graphdb", help="load the knowledge base into GraphDB (optional)").set_defaults(run=cmd_graphdb)
    a = ap.parse_args()
    a.run(a)


if __name__ == "__main__":
    main()
