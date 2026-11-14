"""Engine unit tests on a toy knowledge base, independent of the gold KB (E0: engine tested apart from the KB)."""
from datetime import date
from fractions import Fraction

import pytest

from pph21kbs.expr import Expression, ExpressionError, PrecisionError, round_value
from pph21kbs.kb import apply_delta, empty_kb
from pph21kbs.engine import evaluate_case

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
