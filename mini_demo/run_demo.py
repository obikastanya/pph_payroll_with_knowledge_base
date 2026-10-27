"""End-to-end walkthrough of the planned system, from the initial knowledge base to the four research questions.

Run from the repository root:  env\\Scripts\\python mini_demo\\run_demo.py
Each step names the stage of PANDUAN_PENELITIAN.md and the section of paper/draft/skeleton.tex it illustrates.
The same results are drawn by the app:  env\\Scripts\\streamlit run mini_demo\\app\\main.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import acquisition  # noqa: E402
import experiments as ex  # noqa: E402
import kg  # noqa: E402
from mock_llm import MockLLM  # noqa: E402
from reasoner import NOW, compute  # noqa: E402

OUT = HERE / "outputs"


def section(title, where):
    print(f"\n{'=' * 100}\n{title}\n  [{where}]\n{'=' * 100}")


def show_case(case, knowledge_date=NOW):
    return (f"{case['ptkp_status']} salary {case['salary']:,} overtime {case['overtime']:,} "
            f"{case['year']}-{case['month']:02d} dtp_sector={case['dtp_sector']}"
            + ("" if knowledge_date == NOW else f" known as of {knowledge_date}"))


def main():
    OUT.mkdir(exist_ok=True)
    hash_start = ex.engine_hash()
    llm = MockLLM()

    # ------------------------------------------------------------------------------------------------ 1
    section("1. Knowledge representation: initial knowledge base K0 as a knowledge graph",
            "Panduan stage 3 and 5 | skeleton Section IV")
    s = ex.prepare()
    conforms, _ = kg.shacl_check(s.kb0)
    rules = kg.rule_records(s.kb0)
    print(f"triples: {len(s.kb0)} | rules: {len(rules)} "
          f"(regulation {sum(r['layer'] == 'regulation' for r in rules)}, "
          f"company {sum(r['layer'] == 'company' for r in rules)}) | SHACL conforms: {conforms}")
    kg.save(s.kb0, OUT / "initial_kb.ttl")
    print(f"saved {OUT / 'initial_kb.ttl'}")
    case = {"ptkp_status": "TK/0", "salary": 10_000_000, "allowance": 0, "overtime": 0, "dtp_sector": False,
            "year": 2023, "month": 6}
    r = compute(s.kb0, case)
    print(f"\nexample: {show_case(case)}")
    for fact in ("gross_income", "job_expense", "ptkp_annual", "taxable_income_annual", "pph21", "take_home_pay"):
        rule, source = r.trace.get(fact, ("-", "-"))
        print(f"  {fact:24} {r.values.get(fact)!s:>14}   <- {rule:12} {source}")

    # ------------------------------------------------------------------------------------------------ 2
    section("2. Corpus and gold knowledge base", "Panduan stage 6 and 7 | skeleton Section VI, corpus")
    for e in s.events + s.counterfactuals:
        print(f"  {e['id']:5} {e['issued']} effective {e['effective']}  {e['change_type']:32} {e['title']}")
    kg.save(s.kb_gold, OUT / "gold_final_kb.ttl")
    print(f"gold chain K*_0..K*_{len(s.events)} built; final gold KB has {len(s.kb_gold)} triples")

    # ------------------------------------------------------------------------------------------------ 3
    section("3. Test space S^E", "Panduan stage 8 | skeleton Section VI, test space")
    print(f"S^E: {len(s.cases)} (case, knowledge date) tuples. Mini version: TER layer A, Article 17 and DTP boundaries only.")

    # ------------------------------------------------------------------------------------------------ 4
    section("4. E0 instrument validation: references and mutation score",
            "Panduan stage 13 | skeleton Section VI, chain of trust")
    r0 = ex.e0(s)
    for ref in r0["references"]:
        print(f"  {ref['id']:20} {ref['source']}  {'match' if ref['match'] else 'MISMATCH'}  {ref['got']}")
    print(f"discrepancies against references: {sum(not x['match'] for x in r0['references'])}")
    for doc, (killed, total, survivors) in r0["mutation"].items():
        print(f"  Delta-focused mutation score {doc}: {killed}/{total}")
        for sv in survivors:
            print(f"      survived: {sv}  -> S^E needs a case that reaches it")
    print(f"E0 pass criteria met: {r0['passed']} (the demo continues anyway to show the remaining steps)")

    # ------------------------------------------------------------------------------------------------ 5
    section("5. E1 representational adaptability (RQ1)", "Panduan stage 14 | skeleton Section VI, RQ1")
    r1 = ex.e1(s)
    for doc, _, ok in r1["real"]:
        print(f"  {doc}: gold Delta applied as data only, SHACL conforms: {ok}")
    print("  unseen change U1 (written by a collaborator, revealed now):")
    for exm, got in r1["unseen"]:
        print(f"    {show_case(exm['case'])}: expected {exm['expected']} got {got} -> "
              f"{'match' if got == exm['expected'] else 'MISMATCH'}")
    k, n, lower = r1["ra"]
    print(f"RA unseen = {k}/{n}; exact 95% lower bound {lower:.2f} (the study needs about 15 unseen changes for a useful bound)")

    # ------------------------------------------------------------------------------------------------ 6
    section("6. Acquisition pipeline, step by step, for E2 (PMK 10/2025)", "Panduan stage 9 | skeleton Section V")
    res = acquisition.run(s.gold_before["E2"], s.event("E2"), s.texts["E2"], llm)
    print(f"relevance: {res.relevance}")
    keys_e = {acquisition.case_key(c, w) for c, w in s.cases}
    overlap = sum(acquisition.case_key(c, w) in keys_e for c, w in res.gate_cases)
    print(f"S^G generated by the pipeline: {len(res.gate_cases)} tuples; overlap with S^E: {overlap}")
    for c in res.checks:
        print(f"  candidate {c.number}:")
        for gate, verdict in c.gates.items():
            print(f"     {gate:10} {verdict}")
    print(f"status: {res.status} | selected candidate: {res.selected} | {res.reason} | behaviour groups {res.groups}")
    print(f"impact report: company policies affected = {res.impacted}")

    # ------------------------------------------------------------------------------------------------ 7
    section("7. E2 isolated acquisition (RQ2)", "Panduan stage 15 | skeleton Section VI, RQ2")
    r2 = ex.e2(s, llm)
    for row in r2["rows"]:
        print(f"  {row['document']:5} {row['split']:15} {row['status']:8} -> {row['outcome']:16} "
              f"wrong tuples {row['wrong_tuples']:3} | candidates correct before gates {row['c']}/{row['m']} | {row['reason']}")
        if "memorised" in row:
            k, m, orig = row["memorised"]
            print(f"        memorisation rate: {k}/{m} candidates use the original value {orig}")
    print(f"\nSER = {r2['ser']}/{r2['n']} (exact 95% upper bound {r2['ser_upper']:.2f}) | CAR = {r2['car']}/{r2['n']} | "
          f"ABS = {r2['abs']}/{r2['n']}")
    print(f"relevance: false positives on distractors {r2['distractor_fp']}/{r2['n_distractors']}")
    print("\nother conditions (same mock answers):")
    for name in ex.CONDITIONS:
        if name != "Proposed":
            rc = ex.e2(s, llm, name)
            print(f"  {name:28} SER {rc['ser']}/{rc['n']}  CAR {rc['car']}/{rc['n']}  ABS {rc['abs']}/{rc['n']}")

    # ------------------------------------------------------------------------------------------------ 8
    section("8. E3 regulation replay, chained mode (RQ3)", "Panduan stage 16 | skeleton Section VI, RQ3")
    r3 = ex.e3(s, llm, r2["isolated"])
    for row in r3["rows"]:
        iso_ok, n_early = row["knowledge_isolation"]
        print(f"  {row['event']:3} {row['status']:8} inherited {len(row['inherited']):3} new {len(row['new']):3} "
              f"induced {len(row['induced']):3} (mechanical {len(row['induced_mechanical'])}) "
              f"step ok: {row['ok']}  A3_omega holds on {n_early} early tuples: {iso_ok}")
    print(f"OAR = {r3['oar']}/{r3['n']} | final drift D_N = {r3['drift']}/{r3['n_cases']} tuples wrong")
    kg.save(r3["kb_sys"], OUT / "system_final_kb.ttl")
    print(f"invariant A1 (engine code unchanged): {ex.engine_hash() == hash_start} (hash {hash_start})")

    # ------------------------------------------------------------------------------------------------ 9
    section("9. E4 cross-layer impact analysis (RQ4)", "Panduan stage 17 | skeleton Section VI, RQ4")
    r4 = ex.e4(s)
    for p in r4["pairs"]:
        print(f"  ({p['policy']:12}, {p['event']}) label {'impacted' if p['label'] else '-':9} "
              f"detector {'flagged' if p['flagged'] else '-'}")
    print(f"recall {r4['recall']:.2f} (exact 95% lower bound {r4['recall_lower']:.2f}) | precision {r4['precision']:.2f} | "
          f"F2 {r4['f2']:.2f} | flag-all baseline F2 {r4['flag_all_f2']:.2f}")

    # ------------------------------------------------------------------------------------------------ 10
    (OUT / "experiment_log.jsonl").write_text("\n".join(json.dumps(x, default=str) for x in llm.calls) + "\n",
                                              encoding="utf-8")
    section("10. Done", "see mini_demo/README.md and mini_demo/BLUEPRINT.md for what each step needs in the full system")
    print(f"outputs: {OUT}")


if __name__ == "__main__":
    main()
