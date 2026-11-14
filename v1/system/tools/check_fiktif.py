"""Check the gold Deltas of the fictive regulations FR01-FR05 against their worked examples (FRxx.json contoh[]).

    env\\Scripts\\python system\\tools\\check_fiktif.py

For each example the case is built from its input, then evaluated on K_before (the main-chain prefix at the issue date,
plus the side updates the Delta is applied on) and on K_after = K_before (+) Delta*, and compared with
hasil_sebelum_perubahan and hasil_sesudah_perubahan (a null side is a side the example does not show). The value
after the Delta must also be the same at a later knowledge date.

Case conventions (fiktif/README.md "Asumsi"): wage below the JP and JKN caps, JKK very low risk, JKK 0,24%, JKM 0,3%,
JKN 4% (employer) and JHT 2%, JP 1% (employee) of the wage. These premiums are entered as billed (premiums_as_billed),
so the examples test the FR Delta only and not the premium rules of the chain: the main chain has no JP wage caps
between 2016 and February 2022 (the BPJS letters are not available) and keeps Rp7.000.000, which caps JP for wages
above it, while the examples assume the actual cap. The months in the JKK/JKM relief of PP 49/2020 (FR01-4
August-December 2020, FR02-3 January 2021) are billed with 1% of the JKK and JKM rates, as in the examples.
"""
import json
import sys
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_gold  # noqa: E402
from pph21kbs import static  # noqa: E402
from pph21kbs.engine import evaluate_case  # noqa: E402
from pph21kbs.expr import round_value  # noqa: E402
from pph21kbs.kb import apply_delta, shacl  # noqa: E402

FIKTIF = build_gold.ROOT / "dataset" / "09_korpus_peristiwa" / "fiktif"
OUTPUTS = ["pph21_due", "taxable_income", "annual_pph21", "job_expense"]


def _billed(wage, relief=False):
    """Premiums of one month as the examples compute them (rounded half up per program)."""
    r = Fraction(1, 100) if relief else 1

    def p(rate):
        return round_value(Fraction(rate) * wage, 1, "half_up")
    return {"jkk_premium": p(Fraction(24, 10000) * r), "jkm_premium": p(Fraction(3, 1000) * r),
            "health_premium_employer": p(Fraction(4, 100)), "health_employee": p(Fraction(1, 100)),
            "jht_employee": p(Fraction(2, 100)), "jp_employee": p(Fraction(1, 100))}


def case(cid, year, ptkp, wage, months=range(1, 13), extra=None, hr=None, billed_relief=frozenset()):
    """Full-year (or stated months) case; extra: {month: {income key: amount}}; hr: {month: {key: value}};
    billed_relief: months whose JKK and JKM premiums get the 99% relief of PP 49/2020."""
    periods = []
    for m in months:
        income = {"base_salary": wage}
        for k, v in ((extra or {}).get(m) or (extra or {}).get("all") or {}).items():
            income[k] = income.get(k, 0) + v
        income.update(_billed(wage, m in billed_relief))
        p = {"month": m, "income": income}
        h = (hr or {}).get(m) or (hr or {}).get("all")
        if h:
            p["hr"] = dict(h)
        periods.append(p)
    months = list(months)
    return {"case_id": cid, "tax_year": year, "method": "gross",
            "employee": {"ptkp_status": ptkp, "sex": "M", "tax_id_valid": True},
            "employer": {"klu": None, "jkk_risk_group": "very_low", "premiums_as_billed": True,
                         "policy": None},
            "employment": {"start_month": months[0], "end_month": months[-1]}, "periods": periods}


def period(m, fact="pph21_due"):
    return lambda r: r.periods[m][fact]


def year(fact):
    return lambda r: r.year[fact]


def sum_before_final(r):
    months = sorted(r.periods)
    return sum(r.periods[m]["pph21_due"] for m in months[:-1])


COMMISSION = {m: {"other_regular": 4000000} for m in (2, 5, 8, 11)}
COMMISSION_HR = {m: {"variable_sales_commission": 4000000} for m in (2, 5, 8, 11)}
NIGHT = {"all": {"night_shift_days": 15}}

# example id -> (case, {key in the example: observation}, omega override or None)
EXAMPLES = {
    "FR01-1": (case("FR01-1", 2019, "TK/0", 7000000), {"pph21": period(1)}),
    "FR01-2": (case("FR01-2", 2020, "TK/0", 7000000), {"pph21": period(1)}),
    "FR01-3": (case("FR01-3", 2020, "TK/0", 7000000, extra={3: {"bonus": 10000000}}), {"pph21": period(3)}),
    "FR01-4": (case("FR01-4", 2020, "TK/0", 7000000, extra={3: {"bonus": 10000000}}, billed_relief={8, 9, 10, 11, 12}),
               {"pph_setahun": year("annual_pph21"), "pph_jan_nov": sum_before_final, "pph_desember": period(12)}),
    "FR02-1": (case("FR02-1", 2021, "K/1", 7500000), {"pph21": period(2)}),
    "FR02-2": (case("FR02-2", 2021, "TK/0", 6350000), {"pph21": period(2)}),
    "FR02-3": (case("FR02-3", 2021, "K/1", 7500000, billed_relief={1}),
               {"pkp": year("taxable_income"), "pph_setahun": year("annual_pph21"), "pph_desember": period(12)}),
    "FR03-1": (case("FR03-1", 2021, "K/0", 6800000, hr=NIGHT), {"pph21": period(2)}),
    "FR03-2": (case("FR03-2", 2022, "K/0", 6800000, hr=NIGHT), {"pph21": period(1)}),
    "FR03-3": (case("FR03-3", 2022, "K/0", 6800000, hr=NIGHT),
               {"pkp": year("taxable_income"), "pph_setahun": year("annual_pph21"), "pph_desember": period(12)}),
    "FR04-1": (case("FR04-1", 2019, "TK/0", 6000000, extra=COMMISSION, hr=COMMISSION_HR), {"pph21": period(2)}),
    "FR04-2": (case("FR04-2", 2019, "TK/0", 6000000, extra=COMMISSION, hr=COMMISSION_HR), {"pph21": period(3)}),
    "FR04-3": (case("FR04-3", 2019, "TK/0", 6000000, extra=COMMISSION, hr=COMMISSION_HR),
               {"pph_setahun": year("annual_pph21"), "pph_jan_nov": sum_before_final, "pph_desember": period(12)}),
    "FR05-1": (case("FR05-1", 2022, "K/2", 8000000, extra={"all": {"other_regular": 12000000}}),
               {"pph_bulanan": period(1), "biaya_jabatan": year("job_expense"), "pph_setahun": year("annual_pph21")}),
    "FR05-2": (case("FR05-2", 2022, "TK/0", 7000000),
               {"biaya_jabatan": year("job_expense"), "pph_setahun": year("annual_pph21")}),
    "FR05-3": (case("FR05-3", 2022, "TK/0", 8000000, months=range(1, 7), extra={"all": {"other_regular": 6000000}}),
               {"biaya_jabatan": year("job_expense"), "pph_setahun": year("annual_pph21"), "pph_juni": period(6)}),
    # between the two FR05 documents: the cap used is still 6.000.000 (case of FR05-1, annual job expense)
    "FR05-4": (case("FR05-4", 2022, "K/2", 8000000, extra={"all": {"other_regular": 12000000}}),
               {"plafon_biaya_jabatan_dipakai": year("job_expense")}, date(2022, 1, 31)),
}
# delta used for each event; FR05 is checked on GOLD-FR05B (GOLD-FR05A is empty), FR05-4 on both
DELTA = {"FR01": "GOLD-FR01", "FR02": "GOLD-FR02", "FR03": "GOLD-FR03", "FR04": "GOLD-FR04", "FR05": "GOLD-FR05B"}


def bases(kb, update_id):
    u = build_gold.side_update(update_id)
    before = build_gold.prefix_at(kb, u.recorded_on or u.doc.issued)
    for sid in getattr(u, "base_side", ()):
        before = apply_delta(before, build_gold.side_update(sid).to_json())
    return u, before, apply_delta(before, u.to_json())


def evaluate(kb, c, omega):
    r = evaluate_case(kb, c, omega, outputs=OUTPUTS)
    if r.errors:
        raise RuntimeError(f"{c['case_id']}: {r.errors[:2]}")
    return r


def main():
    kb = build_gold.build(check_only=True, side=False)
    ok = total = 0
    for fr, uid in DELTA.items():
        meta = json.loads((FIKTIF / f"{fr}.json").read_text(encoding="utf-8"))
        u, k_before, k_after = bases(kb, uid)
        issued = date.fromisoformat(u.recorded_on or u.doc.issued)
        for ex in meta["contoh"]:
            spec = EXAMPLES[ex["id"]]
            c, obs = spec[0], spec[1]
            omega = spec[2] if len(spec) > 2 else issued
            got_b = {k: f(evaluate(k_before, c, omega)) for k, f in obs.items()}
            got_a = {k: f(evaluate(k_after, c, omega)) for k, f in obs.items()}
            later = {k: f(evaluate(k_after, c, date(2026, 10, 27))) for k, f in obs.items()} if len(spec) == 2 else got_a
            want_b, want_a = ex["hasil_sebelum_perubahan"], ex["hasil_sesudah_perubahan"]
            problems = []
            for k in obs:
                wb = want_b.get(k) if want_b else None
                wa = want_a.get(k) if want_a else None
                if wb is not None and got_b[k] != wb:
                    problems.append(f"{k} before: KB {got_b[k]} example {wb}")
                if wa is not None and got_a[k] != wa:
                    problems.append(f"{k} after: KB {got_a[k]} example {wa}")
                if later[k] != got_a[k]:
                    problems.append(f"{k}: after differs at a later omega: {got_a[k]} vs {later[k]}")
            total += 1
            ok += not problems
            status = "sama" if not problems else "BEDA"
            print(f"{ex['id']:7s} {status}  before {got_b}  after {got_a}  (omega {omega})")
            for p in problems:
                print("        ", p)
    print(f"FR examples: {ok}/{total} equal")
    clean = check_static(kb)
    return ok == total and clean


def check_static(kb):
    """G3 (static.check, no errors) at the issue date and later, and SHACL G1 on every K_after."""
    clean = True
    for u in build_gold.collect_side():
        if u.kind != "event" and u.delta_id != "BG-FR03":
            continue
        _, k_after = build_gold.apply_side(kb, u)
        issued = date.fromisoformat(u.recorded_on or u.doc.issued)
        errors = []
        for omega in (issued, date(issued.year + 1, 12, 31), date(2026, 10, 27)):
            errors += [f"{omega} {f.kind} {f.ids} {f.fact} {f.detail}" for f in static.check(k_after, omega).errors]
        warnings = sorted({f"{f.kind} {f.ids}" for f in static.check(k_after, date(2026, 10, 27)).warnings})
        violations = shacl.validate(k_after)
        clean &= not errors and not violations
        print(f"{u.delta_id:11s} G3 errors {len(errors)}  SHACL {len(violations)}  warnings {warnings}")
        for e in errors[:5] + [str(v) for v in violations[:5]]:
            print("        ", e)
    return clean


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
