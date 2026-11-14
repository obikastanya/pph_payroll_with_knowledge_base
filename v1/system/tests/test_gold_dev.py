"""Gold Deltas of the development events D01-D13: hand-computed cases on the gold chain (built from system/gold_src).

Values are computed by hand from the regulation texts; the COVID DTP amounts follow the worked examples of PMK
23/2020 Lampiran B (Tuan A, C, D)."""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build_gold  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402

PREMIUMS = ["health_premium_employer", "health_employee", "jkk_premium", "jkm_premium"]


@pytest.fixture(scope="module")
def kb():
    return build_gold.build(check_only=True, side=False)


def case(year, ptkp="TK/0", base=5000000, fixed=0, months=range(1, 13), employer=None, income=None, method="gross"):
    emp = {"klu": None, "jkk_risk_group": "very_low", "policy": None}
    emp.update(employer or {})
    periods = []
    for m in months:
        inc = {"base_salary": base, "fixed_allowance": fixed}
        inc.update((income or {}).get(m, {}))
        periods.append({"month": m, "income": inc})
    return {"case_id": "DEV", "tax_year": year, "method": method,
            "employee": {"ptkp_status": ptkp, "sex": "M", "tax_id_valid": True}, "employer": emp,
            "employment": {"start_month": min(months), "end_month": max(months)}, "periods": periods}


def run(kb, c, omega, outputs=None):
    r = evaluate_case(kb, c, omega, outputs=outputs)
    assert r.errors == [], r.errors
    return r


# ---------------------------------------------------------------------- D01, D03 PTKP
def test_ptkp_2013_and_2009(kb):
    assert run(kb, case(2012), date(2013, 1, 1)).year["ptkp_amount"] == 15840000
    assert run(kb, case(2013, "K/1"), date(2013, 12, 31)).year["ptkp_amount"] == 24300000 + 2 * 2025000
    assert run(kb, case(2014, "K/3"), date(2014, 12, 31)).year["ptkp_amount"] == 24300000 + 4 * 2025000


def test_ptkp_2015_retroactive(kb):
    before, after = date(2015, 6, 28), date(2015, 6, 29)
    assert run(kb, case(2015), before).year["ptkp_amount"] == 24300000
    assert run(kb, case(2015), after).year["ptkp_amount"] == 36000000
    assert run(kb, case(2015, "K/3"), after).year["ptkp_amount"] == 48000000
    assert run(kb, case(2016), date(2016, 12, 31)).year["ptkp_amount"] == 54000000


# ---------------------------------------------------------------------- D02, D04 JKN
def test_jkn_2014_rates_and_cap(kb):
    r = run(kb, case(2014, base=3000000, fixed=500000), date(2014, 12, 31), PREMIUMS)
    assert r.periods[1]["health_premium_employer"] == 140000        # 4% x 3.500.000
    assert r.periods[1]["health_employee"] == 17500                 # 0,5% x 3.500.000
    r = run(kb, case(2014, base=6000000), date(2014, 12, 31), PREMIUMS)
    assert r.periods[6]["health_premium_employer"] == 189000        # 4% x 2 x 28.350.000 / 12 = 4.725.000
    assert r.periods[6]["health_employee"] == 23625


def test_jkn_2015_cap_follows_retroactive_ptkp(kb):
    c = case(2015, base=8000000)
    r = run(kb, c, date(2015, 6, 28), PREMIUMS)                     # PTKP 2015 not yet known: cap 4.725.000
    assert r.periods[8]["health_employee"] == 47250                 # 1% from July 2015
    r = run(kb, c, date(2015, 12, 31), PREMIUMS)                    # cap 2 x 42.000.000 / 12 = 7.000.000
    assert r.periods[6]["health_employee"] == 35000                 # 0,5% until June 2015
    assert r.periods[8]["health_premium_employer"] == 280000
    assert r.periods[8]["health_employee"] == 70000


def test_jkn_2016_fixed_cap(kb):
    r = run(kb, case(2016, base=9000000), date(2016, 12, 31), PREMIUMS)
    assert r.periods[2]["health_premium_employer"] == 360000        # Feb: cap 2 x 63.000.000 / 12 = 10.500.000
    assert r.periods[4]["health_premium_employer"] == 320000        # from Mar 2016: cap 8.000.000


# ---------------------------------------------------------------------- D09 BPJS TK relief
def test_jkk_jkm_relief_2020(kb):
    emp = {"jkk_risk_group": "low", "bpjs_relief_2020_eligible": True}
    c = case(2020, base=5000000, employer=emp)
    r = run(kb, c, date(2020, 12, 31), PREMIUMS)
    assert (r.periods[7]["jkk_premium"], r.periods[7]["jkm_premium"]) == (27000, 15000)   # 0,54% and 0,30%
    assert (r.periods[8]["jkk_premium"], r.periods[8]["jkm_premium"]) == (270, 150)       # 1% of the contribution
    r = run(kb, case(2021, base=5000000, employer=emp), date(2021, 12, 31), PREMIUMS)
    assert r.periods[1]["jkk_premium"] == 270 and r.periods[2]["jkk_premium"] == 27000
    assert run(kb, c, date(2020, 8, 31), PREMIUMS).periods[8]["jkk_premium"] == 27000    # before issue
    other = case(2020, base=5000000, employer={"jkk_risk_group": "low"})
    assert run(kb, other, date(2020, 12, 31), PREMIUMS).periods[8]["jkk_premium"] == 27000


# ---------------------------------------------------------------------- D05-D07, D10, D11 COVID DTP
def covid(year, ptkp, base, klu, pension=0, extra=None, employer=None, months=range(1, 13)):
    emp = {"klu": klu, "premiums_as_billed": True}
    emp.update(employer or {})
    income = {m: {"jp_employee": pension} for m in months}
    for m, inc in (extra or {}).items():
        income[m].update(inc)
    return case(year, ptkp, base=base, employer=emp, income=income, months=months)


def test_covid_dtp_worked_examples(kb):
    omega = date(2020, 12, 31)
    a = run(kb, covid(2020, "K/1", 16500000, "10791", 330000), omega)          # Tuan A, April 2020
    assert a.periods[4]["pph21_due"] == 1146333 and a.periods[4]["pph21_dtp"] == 1146333
    assert a.periods[3]["pph21_dtp"] == 0                                    # before Masa April 2020
    c = run(kb, covid(2020, "K/1", 15000000, "10791", 300000, {5: {"thr": 10000000}}), omega,
            ["pph_regular_month", "pph_irregular_month", "pph21_due", "pph21_dtp"])  # Tuan C, May 2020
    assert c.periods[5]["pph_regular_month"] == 925833 and c.periods[5]["pph_irregular_month"] == 1500000
    assert c.periods[5]["pph21_dtp"] == 925833                               # tax on THR is withheld
    assert c.periods[5]["pph21_due"] == 925833 + 1500000
    d = run(kb, covid(2020, "K/1", 15000000, "32503", 300000, {m: {"other_regular": 1000000} for m in range(1, 13)}),
            omega)                                                           # Tuan D, July 2020, tax allowance
    assert d.periods[7]["pph21_dtp"] == 1075833


def test_covid_dtp_income_cap_and_klu(kb):
    omega = date(2020, 12, 31)
    b = run(kb, covid(2020, "K/0", 21000000, "10791", 420000), omega)         # Tuan B: 252 juta > 200 juta
    assert b.periods[5]["pph21_dtp"] == 0 and b.periods[5]["pph21_due"] > 0
    bank = run(kb, covid(2020, "TK/0", 8000000, "64190"), omega)              # KLU not listed
    assert all(bank.periods[m]["pph21_dtp"] == 0 for m in range(1, 13))
    kite = run(kb, covid(2020, "TK/0", 8000000, "64190", employer={"kite": True}), omega)
    assert kite.periods[5]["pph21_dtp"] == kite.periods[5]["pph21_due"] > 0


def test_covid_dtp_replacements_and_extensions(kb):
    retail = covid(2020, "TK/0", 8000000, "47111")                           # listed from PMK 44/2020 only
    assert run(kb, retail, date(2020, 4, 26)).periods[4]["pph21_dtp"] == 0
    r = run(kb, retail, date(2020, 4, 27))
    assert r.periods[4]["pph21_dtp"] == r.periods[4]["pph21_due"] > 0       # retroactive to Masa April
    assert r.periods[10]["pph21_dtp"] == 0                                   # PMK 44 ends in September
    out = ["pph21_due", "pph21_dtp", "final_period_tax"]
    r = run(kb, retail, date(2020, 7, 16), out)
    assert r.periods[10]["pph21_dtp"] == r.periods[10]["pph21_due"] > 0     # PMK 86 extends to December
    final = r.year["final_period_tax"]
    assert r.periods[12]["pph21_dtp"] == max(0, final)
    zone = covid(2021, "TK/0", 8000000, "64190", employer={"bonded_zone": True})
    assert run(kb, zone, date(2021, 2, 1)).periods[1]["pph21_dtp"] == 0      # PMK 9/2021 not yet issued
    r = run(kb, zone, date(2021, 12, 31))
    assert r.periods[6]["pph21_dtp"] > 0                                     # Jan-Jun 2021: bonded zones qualify
    assert r.periods[7]["pph21_dtp"] == 0                                    # Jul-Dec 2021: listed KLU only
    listed = run(kb, covid(2021, "TK/0", 8000000, "10791"), date(2021, 12, 31))
    assert listed.periods[11]["pph21_dtp"] > 0
    assert run(kb, covid(2022, "TK/0", 8000000, "10791"), date(2022, 12, 31)).periods[3]["pph21_dtp"] == 0


def test_covid_dtp_over_withholding_not_refunded(kb):
    # paid January-October at 12.000.000 (DTP April-October), leaves in November with a final salary of 1.000.000
    c = covid(2020, "TK/0", 12000000, "10791", months=range(1, 12))
    c["periods"][-1]["income"]["base_salary"] = 1000000
    r = run(kb, c, date(2020, 12, 31), ["pph21_due", "pph21_dtp", "final_period_tax", "refund_to_employee"])
    assert r.year["final_period_tax"] < 0
    dtp_before = sum(r.periods[m]["pph21_dtp"] for m in range(1, 11))
    assert r.year["refund_to_employee"] == max(0, -r.year["final_period_tax"] - dtp_before)


# ---------------------------------------------------------------------- D08, D12, D13 empty
def test_empty_deltas_change_nothing(kb):
    by_id = {u.delta_id: u for u in kb.updates}
    for uid, issued in (("GOLD-D08", date(2020, 8, 14)), ("GOLD-D12", date(2021, 10, 26)),
                        ("GOLD-D13", date(2022, 1, 25))):
        u = by_id[uid]
        assert u.first_seq > u.last_seq, f"{uid} must add no records"
        for c in (covid(issued.year, "K/1", 9000000, "10791"), case(issued.year, base=7000000)):
            before = evaluate_case(kb, c, date.fromordinal(issued.toordinal() - 1))
            after = evaluate_case(kb, c, issued)
            assert (before.periods, before.year, before.conflicts) == (after.periods, after.year, after.conflicts)
