"""Engine: exact arithmetic, rule selection, conflict resolution, fixed points, and monthly runs."""
import copy
from datetime import date
from fractions import Fraction

import pytest

from pph21kbs import config, graph
from pph21kbs.engine import evaluate_case
from pph21kbs.expr import Expression, ExpressionError, PrecisionError, round_value
from pph21kbs.kb import apply_delta, empty_kb


def seed():
    return graph.read_trig(config.SEED_KB, "K")


# --------------------------------------------------------------------------------------------------------------------
# Engine core on a toy knowledge base
# --------------------------------------------------------------------------------------------------------------------
SRC = [{"document": "TOY", "provision": "Pasal 1", "quote": "toy rule for engine tests"}]


def fact(name, t="money", scope="period", output=False):
    return {"kind": "fact", "id": name, "fact_type": t, "fact_scope": scope, "output": output,
            "recorded_on": "2020-01-01", "source": SRC}


def rule(rid, produces, expr, scope="period", cond=None, layer="regulation", modality="mandatory",
         vf="2020-01-01", vu=None, rec="2020-01-01", **extra):
    r = {"kind": "rule", "id": rid, "layer": layer, "modality": modality, "scope": scope, "produces": produces,
         "expression": expr, "valid_from": vf, "recorded_on": rec, "source": SRC}
    if cond:
        r["condition"] = cond
    if vu:
        r["valid_until"] = vu
    r.update(extra)
    return r


def delta(did, add=(), change=(), remove=(), issued="2020-01-01"):
    return {"delta_id": did, "document": {"id": "TOY", "issued": issued}, "relevant": True,
            "add": list(add), "change": list(change), "remove": list(remove)}


def toy_kb():
    d = delta("BASE", add=[
        fact("gross", output=True), fact("tax", output=True), fact("allowance", output=True),
        fact("annual_gross", scope="year", output=True), fact("annual_tax", scope="year", output=True),
        fact("rate", t="rate"), fact("withholding_method", t="category"),
        rule("REG.METHOD", "withholding_method", "case('method')", modality="default"),
        rule("REG.GROSS", "gross", "income('salary') + allowance"),
        rule("REG.ALLOW0", "allowance", "0", modality="default"),
        rule("REG.ALLOW.GU", "allowance", "tax", cond="withholding_method == 'gross_up'",
             fixed_point={"lower": "0", "upper": "income('salary')"}),
        rule("REG.RATE", "rate", "bracket('ter', 'A', gross)"),
        rule("REG.TAX", "tax", "round(rate * gross, 1, param('round_mode'))"),
        rule("REG.AGROSS", "annual_gross", "sum_periods('gross')", scope="year"),
        rule("REG.ATAX", "annual_tax", "round(progressive('p17', annual_gross), 1, 'down')", scope="year"),
        {"kind": "parameter", "id": "PAR.ROUND.1", "name": "round_mode", "value": "truncate",
         "value_type": "category", "valid_from": "2020-01-01", "recorded_on": "2020-01-01", "source": SRC},
        {"kind": "table", "id": "TAB.TER", "name": "ter", "table_kind": "bracket", "valid_from": "2020-01-01",
         "recorded_on": "2020-01-01", "source": SRC,
         "rows": [{"key": "A", "lower": 0, "upper": 5000000, "value": "0"},
                  {"key": "A", "lower": 5000000, "upper": 10000000, "value": "0.015"},
                  {"key": "A", "lower": 10000000, "upper": None, "value": "0.05"}]},
        {"kind": "table", "id": "TAB.P17", "name": "p17", "table_kind": "progressive", "valid_from": "2020-01-01",
         "recorded_on": "2020-01-01", "source": SRC,
         "rows": [{"lower": 0, "upper": 60000000, "rate": "0.05"},
                  {"lower": 60000000, "upper": None, "rate": "0.15"}]},
    ])
    return apply_delta(empty_kb(), d)


def case(salary, months=(1, 2, 3), method="gross", year=2021, policy=None):
    return {"case_id": "T", "tax_year": year, "employee": {"ptkp_status": "TK/0"},
            "employer": {"policy": policy}, "method": method,
            "employment": {"start_month": months[0], "end_month": months[-1]},
            "periods": [{"month": m, "income": {"salary": salary}} for m in months]}


def test_rounding_modes():
    assert round_value(Fraction(5, 2), 1, "half_up") == 3
    assert round_value(Fraction(-5, 2), 1, "half_up") == -3
    assert round_value(Fraction(5, 2), 1, "half_even") == 2
    assert round_value(Fraction(-1, 3), 1, "down") == -1
    assert round_value(Fraction(-1, 3), 1, "truncate") == 0
    assert round_value(4249200, 1000, "down") == 4249000


def test_parser_rejects_floats_and_unknown_functions():
    with pytest.raises(PrecisionError):
        Expression("0.05 * gross")
    with pytest.raises(ExpressionError):
        Expression("eval('1')")
    with pytest.raises(ExpressionError):
        Expression("gross.real")
    e = Expression("min(b, a) + dec('0.05') * 100")
    assert e.canonical() == "(5 + min(a, b))"


def test_basic_month_and_year():
    kb = toy_kb()
    r = evaluate_case(kb, case(8000000), date(2021, 1, 1))
    assert r.errors == []
    assert r.periods[1]["gross"] == 8000000
    assert r.periods[1]["tax"] == 120000          # 1.5% x 8,000,000
    assert r.year["annual_gross"] == 24000000
    assert r.year["annual_tax"] == 1200000


def test_gross_up_least_fixed_point():
    kb = toy_kb()
    r = evaluate_case(kb, case(9900000, method="gross_up"), date(2021, 1, 1))
    assert r.errors == []
    t = r.periods[1]["allowance"]
    assert t == r.periods[1]["tax"]
    # T = rate(9.9m + T) * (9.9m + T); 9.9m + T exceeds 10m, so 5% bracket
    assert t == 521052
    assert t == (9900000 + t) * 5 // 100


def test_parameter_versions_by_knowledge_date():
    kb = toy_kb()
    change = delta("E13", issued="2021-05-22", add=[
        {"kind": "parameter", "id": "PAR.ROUND.2", "name": "round_mode", "value": "half_up", "value_type": "category",
         "valid_from": "2021-01-01", "recorded_on": "2021-05-22", "source": SRC}])
    kb2 = apply_delta(kb, change)
    c = case(6333333)      # 1.5% x 6,333,333 = 94,999.995
    assert evaluate_case(kb2, c, date(2021, 5, 21)).periods[1]["tax"] == 94999
    assert evaluate_case(kb2, c, date(2021, 5, 22)).periods[1]["tax"] == 95000
    assert evaluate_case(kb, c, date(2022, 1, 1)).periods[1]["tax"] == 94999


def test_company_rule_overrides_default_and_conflicts_with_mandatory():
    kb = toy_kb()
    comp = delta("P", issued="2020-06-01", add=[
        rule("PRS.X.ALLOW", "allowance", "100000", layer="company", modality="default", rec="2020-06-01",
             policy="PX"),
        rule("PRS.X.GROSS", "gross", "income('salary')", layer="company", modality="default", rec="2020-06-01",
             conflict_code="C2", policy="PX"),
    ])
    kb2 = apply_delta(kb, comp)
    assert evaluate_case(kb2, case(8000000), date(2021, 1, 1)).periods[1]["allowance"] == 0   # no policy attached
    r = evaluate_case(kb2, case(8000000, policy="PX"), date(2021, 1, 1))
    assert r.periods[1]["allowance"] == 100000                # company beats regulation default
    assert r.periods[1]["gross"] == 8100000                   # mandatory regulation beats company
    assert {c["source"] for c in r.conflicts} == {"PRS.X.GROSS"}
    assert r.conflicts[0]["code"] == "C2"


def test_overrides_lex_specialis_and_unresolved_conflict():
    kb = toy_kb()
    special = delta("S", issued="2020-06-01", add=[
        rule("REG.GROSS.SPECIAL", "gross", "income('salary') * 2", rec="2020-06-01", overrides=["REG.GROSS"],
             cond="income('salary') > 9000000")])
    kb2 = apply_delta(kb, special)
    assert evaluate_case(kb2, case(9500000), date(2021, 1, 1)).periods[1]["gross"] == 19000000
    assert evaluate_case(kb2, case(8000000), date(2021, 1, 1)).periods[1]["gross"] == 8000000
    clash = delta("C", issued="2020-01-01", add=[
        rule("REG.GROSS.CLASH", "gross", "1", rec="2020-01-01", vf="2020-01-01")])
    kb3 = apply_delta(kb, clash)
    r = evaluate_case(kb3, case(8000000), date(2021, 1, 1))
    assert any("UnresolvedConflict" in e for e in r.errors)


def test_change_and_remove_are_bitemporal():
    kb = toy_kb()
    ch = delta("CH", issued="2021-03-01", change=[
        rule("REG.GROSS", "gross", "income('salary') + allowance + 1", rec="2021-03-01", vf="2021-02-01")])
    kb2 = apply_delta(kb, ch)
    c = case(8000000)
    before = evaluate_case(kb2, c, date(2021, 2, 28))
    after = evaluate_case(kb2, c, date(2021, 3, 1))
    assert before.periods[2]["gross"] == 8000000
    assert after.periods[1]["gross"] is None or after.periods[1]["gross"] == "ERROR"
    assert after.periods[2]["gross"] == 8000001


def test_unstated_rounding_is_an_error():
    kb = toy_kb()
    bad = delta("B", issued="2020-02-01", change=[
        rule("REG.TAX", "tax", "rate * gross", rec="2020-02-01")])
    r = evaluate_case(apply_delta(kb, bad), case(6333333), date(2021, 1, 1))
    assert any("TypeViolation" in e for e in r.errors)


# --------------------------------------------------------------------------------------------------------------------
# Conflict resolution (lex superior, lex specialis, lex posterior)
# --------------------------------------------------------------------------------------------------------------------
OMEGA = date(2021, 12, 31)


def base(*rules, adopts=None):
    """Toy KB where fact `x` (output) is produced only by the given rules, read from a case with salary income."""
    d = delta("BASE", add=[fact("x", output=True), fact("y", output=True), *rules])
    if adopts:
        d["adopts"] = adopts
    return apply_delta(empty_kb(), d)


def x_of(kb, policy=None, months=(1,), omega=OMEGA, year=2021):
    r = evaluate_case(kb, case(1000, months=months, policy=policy, year=year), omega)
    return r, r.periods[months[0]]["x"]


# ---------------------------------------------------------------------- lex superior
def test_mandatory_regulation_beats_company_beats_optional_beats_default():
    rules = [rule("REG.D", "x", "1", modality="default"),
             rule("REG.O", "x", "2", modality="optional"),
             rule("PRS.C", "x", "3", layer="company", modality="default", policy="PX"),
             rule("REG.M", "x", "4")]
    r, v = x_of(base(*rules), policy="PX")
    assert v == 4 and r.winners[("x", 1)] == "REG.M"
    r, v = x_of(base(*rules[:3]), policy="PX")
    assert v == 3
    r, v = x_of(base(*rules[:2]))
    assert v == 1, "an optional rule counts only when a policy adopts it"
    kb = base(*rules[:2])
    kb = apply_delta(kb, {**delta("ADOPT"), "document": {"id": "PX", "issued": "2020-01-01"}, "adopts": ["REG.O"]})
    _, v = x_of(kb, policy="PX")
    assert v == 2


def test_company_rule_needs_its_policy_in_the_case():
    kb = base(rule("REG.D", "x", "1", modality="default"),
              rule("PRS.C", "x", "3", layer="company", modality="default", policy="PX"))
    assert x_of(kb)[1] == 1
    assert x_of(kb, policy="PY")[1] == 1
    assert x_of(kb, policy=["PY", "PX"])[1] == 3


def test_company_rule_losing_to_mandatory_rule_is_a_conflict_only_when_values_differ():
    kb = base(rule("REG.M", "x", "4"),
              rule("PRS.SAME", "x", "4", layer="company", modality="default", policy="PX"),
              rule("PRS.DIFF", "y", "5", layer="company", modality="default", policy="PX", conflict_code="C3"),
              rule("REG.MY", "y", "6"))
    r, v = x_of(kb, policy="PX")
    assert v == 4 and r.periods[1]["y"] == 6
    assert [(c["source"], c["code"]) for c in r.conflicts] == [("PRS.DIFF", "C3")]
    assert r.conflict_keys() == {("override", "PRS.DIFF", "y", 1)}


# ---------------------------------------------------------------------- lex specialis
def test_explicit_override_beats_same_rank_rule_even_if_older():
    kb = base(rule("REG.GENERAL", "x", "1", vf="2021-01-01"),
              rule("REG.SPECIAL", "x", "2", vf="2020-01-01", overrides=["REG.GENERAL"]))
    r, v = x_of(kb)
    assert v == 2 and r.winners[("x", 1)] == "REG.SPECIAL"


def test_override_is_transitive_and_inactive_special_rule_leaves_general_rule():
    kb = base(rule("REG.A", "x", "1"),
              rule("REG.B", "x", "2", overrides=["REG.A"], cond="income('salary') > 5000"),
              rule("REG.C", "x", "3", overrides=["REG.B"]))
    assert x_of(kb)[1] == 3
    kb = base(rule("REG.A", "x", "1"), rule("REG.B", "x", "2", overrides=["REG.A"], cond="income('salary') > 5000"))
    assert x_of(kb)[1] == 1


def test_override_does_not_lift_a_lower_rank():
    kb = base(rule("REG.M", "x", "4"), rule("REG.D", "x", "1", modality="default", overrides=["REG.M"]))
    assert x_of(kb)[1] == 4


# ---------------------------------------------------------------------- lex posterior
def test_later_valid_from_wins():
    kb = base(rule("REG.OLD", "x", "1", vf="2020-01-01"), rule("REG.NEW", "x", "2", vf="2021-01-01"))
    assert x_of(kb)[1] == 2
    assert x_of(kb, year=2020)[1] == 1


def test_same_valid_from_later_first_recording_wins():
    kb = base(rule("REG.OLD", "x", "1", vf="2021-01-01"))
    kb = apply_delta(kb, delta("NEW", issued="2021-03-01",
                               add=[rule("REG.NEW", "x", "2", vf="2021-01-01", rec="2021-03-01")]))
    assert x_of(kb)[1] == 2
    assert x_of(kb, omega=date(2021, 2, 28))[1] == 1, "not known before 2021-03-01"


def test_revising_an_old_rule_does_not_make_it_newer():
    kb = base(rule("REG.OLD", "x", "1", vf="2021-01-01"))
    kb = apply_delta(kb, delta("NEW", issued="2021-03-01",
                               add=[rule("REG.NEW", "x", "2", vf="2021-01-01", rec="2021-03-01")]))
    kb = apply_delta(kb, delta("FIX", issued="2021-06-01",
                               change=[rule("REG.OLD", "x", "7", vf="2021-01-01", rec="2021-06-01")]))
    r, v = x_of(kb)
    assert v == 2, "lex posterior uses the first recording date t_c^0, not the revision date"


# ---------------------------------------------------------------------- no unique winner
def test_unresolved_conflict_and_redundant_rules():
    kb = base(rule("REG.A", "x", "1"), rule("REG.B", "x", "2"))
    r, v = x_of(kb)
    assert any("UnresolvedConflict" in e for e in r.errors)
    kb = base(rule("REG.A", "x", "1 + 1"), rule("REG.B", "x", "2"))
    r, v = x_of(kb)
    assert v == 2 and r.errors == [] and any("RedundantRules" in w for w in r.warnings)


# ---------------------------------------------------------------------- validity
def test_period_rules_valid_on_first_day_and_year_rules_on_employment_span():
    kb = base(rule("REG.D", "x", "0", modality="default"),
              rule("REG.MAR", "x", "1", vf="2021-03-01", vu="2021-03-31"),
              fact("z", scope="year", output=True),
              rule("REG.ZD", "z", "0", scope="year", modality="default"),
              rule("REG.Z", "z", "9", scope="year", vf="2021-10-01", vu="2021-12-31"))
    r = evaluate_case(kb, case(1000, months=(2, 3, 4)), OMEGA)
    assert [r.periods[m]["x"] for m in (2, 3, 4)] == [0, 1, 0]
    assert r.year["z"] == 0, "employment Feb-Apr does not meet Oct-Dec"
    r = evaluate_case(kb, case(1000, months=(9, 10)), OMEGA)
    assert r.year["z"] == 9


def test_constraint_violation_names_company_rules():
    kb = base(rule("REG.D", "x", "0", modality="default"),
              rule("PRS.LOW", "x", "-5", layer="company", modality="default", policy="PX"),
              {"kind": "constraint", "id": "CON.NONNEG", "scope": "period", "assertion": "x >= 0",
               "conflict_code": "C8", "valid_from": "2020-01-01", "recorded_on": "2020-01-01", "source": SRC})
    r, v = x_of(kb, policy="PX")
    assert v == -5
    assert r.conflict_keys() == {("constraint", ("PRS.LOW",), 1, "C8")}


# --------------------------------------------------------------------------------------------------------------------
# Monthly runs on the starting knowledge base
# --------------------------------------------------------------------------------------------------------------------
OMEGA = date(2026, 10, 27)


@pytest.fixture(scope="module")
def kb():
    return seed()


def year_case(months=range(1, 13), end=12, method="gross", thr_month=3):
    periods = [{"month": m, "income": {"base_salary": 10_000_000, "fixed_allowance": 1_500_000,
                                       **({"thr": 11_500_000} if m == thr_month else {})}} for m in months]
    return {"case_id": "t", "tax_year": 2025, "method": method, "employee": {"ptkp_status": "K/1", "sex": "M"},
            "employer": {"jkk_risk_group": "low"}, "employment": {"start_month": months[0], "end_month": end},
            "periods": periods}


def test_months_so_far_are_not_final(kb):
    full = evaluate_case(kb, year_case(), OMEGA)
    part = evaluate_case(kb, year_case(months=range(1, 4)), OMEGA)
    assert part.partial and not part.year and part.final_month == 12
    assert all(part.periods[m] == full.periods[m] for m in (1, 2, 3))
    assert not full.partial and full.final_month == 12 and full.year


def test_exit_month_is_final(kb):
    r = evaluate_case(kb, year_case(months=range(1, 9), end=8), OMEGA)
    assert not r.partial and r.final_month == 8 and r.year["annual_pph21"] is not None


def test_recorded_withholding_moves_the_final_month(kb):
    full = evaluate_case(kb, year_case(), OMEGA)
    rec = copy.deepcopy(year_case())
    rec["periods"][1]["recorded"] = {"pph21_due": full.periods[2]["pph21_due"] + 50_000}
    r = evaluate_case(kb, rec, OMEGA, trace=True)
    assert r.periods[2]["pph21_due"] == full.periods[2]["pph21_due"] + 50_000
    assert r.trace[("pph21_due", 2)]["rule"] == "RECORDED"
    assert r.year["annual_pph21"] == full.year["annual_pph21"]
    assert full.periods[12]["pph21_due"] - r.periods[12]["pph21_due"] == 50_000


def test_recorded_unknown_fact_is_refused(kb):
    bad = copy.deepcopy(year_case())
    bad["periods"][0]["recorded"] = {"no_such_fact": 1}
    with pytest.raises(Exception):
        evaluate_case(kb, bad, OMEGA)


def test_missing_inputs_are_reported(kb):
    r = evaluate_case(kb, year_case(), OMEGA)
    assert ("income", "overtime_pay", 1) in r.missing_inputs          # read by the gross rule, absent from the case
    assert ("income", "base_salary", 1) not in r.missing_inputs


# --------------------------------------------------------------------------------------------------------------------
# Worked example (README): the switch to the effective-rate method (TER) of PP 58/2023
# --------------------------------------------------------------------------------------------------------------------
def test_worked_example_employee_a(kb):
    """Salary Rp15,000,000, PTKP K/1, THR Rp15,000,000 in March 2024. Known today, TER applies: 6% in January, 12% in
    March, and the final period settles the annual tax. Asked before PP 58/2023 was recorded (27 Dec 2023), the old
    annualised method applies."""
    from cli import simple_case
    case = simple_case(2024, 15_000_000, "K/1", thr=15_000_000, thr_month=3)
    now = evaluate_case(kb, case, date(2026, 11, 8), trace=True)
    assert now.periods[1]["gross_income"] == 15_561_000
    assert now.periods[1]["pph21_due"] == 933_660 and now.periods[3]["pph21_due"] == 3_667_320
    assert now.periods[12]["pph21_due"] == 186_480 and now.year["annual_pph21"] == 13_190_400
    assert now.trace[("pph21_running", 1)]["rule"] == "REG.TER.RUNNING"
    before = evaluate_case(kb, case, date(2023, 12, 1))
    assert before.periods[1]["pph21_due"] == 912_300
