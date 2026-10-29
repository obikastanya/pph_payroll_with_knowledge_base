"""engine-v2: months so far, recorded values, missing inputs (payroll during the year)."""
import copy
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build_gold  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402

OMEGA = date(2026, 10, 27)


@pytest.fixture(scope="module")
def kb():
    return build_gold.load_graph()


def case(months=range(1, 13), end=12, method="gross", thr_month=3):
    periods = [{"month": m, "income": {"base_salary": 10_000_000, "fixed_allowance": 1_500_000,
                                       **({"thr": 11_500_000} if m == thr_month else {})}} for m in months]
    return {"case_id": "t", "tax_year": 2025, "method": method, "employee": {"ptkp_status": "K/1", "sex": "M"},
            "employer": {"jkk_risk_group": "low"}, "employment": {"start_month": months[0], "end_month": end},
            "periods": periods}


def test_months_so_far_are_not_final(kb):
    full = evaluate_case(kb, case(), OMEGA)
    part = evaluate_case(kb, case(months=range(1, 4)), OMEGA)
    assert part.partial and not part.year and part.final_month == 12
    assert all(part.periods[m] == full.periods[m] for m in (1, 2, 3))
    assert not full.partial and full.final_month == 12 and full.year


def test_exit_month_is_final(kb):
    r = evaluate_case(kb, case(months=range(1, 9), end=8), OMEGA)
    assert not r.partial and r.final_month == 8 and r.year["annual_pph21"] is not None


def test_recorded_withholding_moves_the_final_month(kb):
    full = evaluate_case(kb, case(), OMEGA)
    rec = copy.deepcopy(case())
    rec["periods"][1]["recorded"] = {"pph21_due": full.periods[2]["pph21_due"] + 50_000}
    r = evaluate_case(kb, rec, OMEGA, trace=True)
    assert r.periods[2]["pph21_due"] == full.periods[2]["pph21_due"] + 50_000
    assert r.trace[("pph21_due", 2)]["rule"] == "RECORDED"
    assert r.year["annual_pph21"] == full.year["annual_pph21"]
    assert full.periods[12]["pph21_due"] - r.periods[12]["pph21_due"] == 50_000


def test_recorded_unknown_fact_is_refused(kb):
    bad = copy.deepcopy(case())
    bad["periods"][0]["recorded"] = {"no_such_fact": 1}
    with pytest.raises(Exception):
        evaluate_case(kb, bad, OMEGA)


def test_missing_inputs_are_reported(kb):
    r = evaluate_case(kb, case(), OMEGA)
    assert ("income", "overtime_pay", 1) in r.missing_inputs          # read by the gross rule, absent from the case
    assert ("income", "base_salary", 1) not in r.missing_inputs
