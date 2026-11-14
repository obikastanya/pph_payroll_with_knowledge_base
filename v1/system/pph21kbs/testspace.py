"""Test space S^E (PANDUAN Tahap 8; skeleton "Ruang uji"): cases with expected values from the gold chain.

Three criteria per tax year 2023-2026:
  combinatorial  pairwise (2-way) covering array over the dimensions of the tax space with their constraints; 3-way
                 coverage is reported
  boundary       every TER bracket bound b at b - 1, b, b + 1 of the monthly gross (one representative PTKP status
                 per category, a non-final month), and every Pasal 17 bound at PKP b - 1000, b, b + 1000 (generated
                 in reverse from PKP to salary with the engine; PKP is rounded down to thousands)
  operational    seeded random employee-years: monthly wage drawn from the BPS average wages per province and
                 sector (Sakernas 2025, dataset/04_data_publik/bps), PTKP status uniform (assumption), full year 80%
S^E never uses the S^G marker income.other_regular (akuisisi.md 5 item 7). Cases are plain case dicts
(format_data.md 3) with "criterion" and "cell" metadata.
"""
import csv
import itertools
import json
import random
from datetime import date
from fractions import Fraction

from .config import REPO
from .engine import evaluate_case

YEARS = (2023, 2024, 2025, 2026)
DEV_YEARS = (2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021, 2022)     # years of the development events
PTKP = ("TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3")
CATEGORY_STATUS = {"A": "TK/0", "B": "K/1", "C": "K/3"}
SALARIES = (4_500_000, 9_000_000, 15_000_000, 30_000_000, 70_000_000)
PATTERNS = {"full": (1, 12), "join": (7, 12), "leave": (1, 6)}
SECTORS = {"other": ("62019", False), "labour_intensive": ("14111", True), "tourism": ("55110", False)}
BENEFITS = ("none", "housing", "gift", "vehicle")
INCOMES = ("regular", "thr", "bonus")
BPS_WAGES = REPO / "dataset" / "04_data_publik" / "bps" / "bps_upah_provinsi_x_lapangan_usaha_17sektor_2025.csv"
SECTION_KLU = {"C": "14111", "I": "55110"}      # representative code of a BPS section (assumption, documented)


def make_case(case_id, year, salary, ptkp="TK/0", method="gross", pattern="full", income="regular",
              sector="other", jkk="very_low", benefit="none", zakat=False, tax_id_valid=True):
    start, end = PATTERNS[pattern]
    klu, relief = SECTORS[sector]
    periods = []
    for m in range(start, end + 1):
        inc = {"base_salary": salary, "fixed_allowance": salary // 10}
        ben = {}
        if income == "thr" and m == min(max(start, 4), end):
            inc["thr"] = salary + salary // 10
        if income == "bonus" and m == end:
            inc["bonus"] = 2 * salary
        if benefit == "housing":
            ben["housing_individual"] = 3_000_000
        elif benefit == "gift" and m == min(max(start, 8), end):
            ben["gift_other"] = 4_000_000
        elif benefit == "vehicle":
            ben["company_vehicle"] = 5_000_000
        periods.append({"month": m, "income": inc, "benefits": ben,
                        "zakat": (salary * 25 // 1000) if zakat else 0})
    return {"case_id": case_id, "tax_year": year, "method": method,
            "employee": {"ptkp_status": ptkp, "sex": "M", "tax_id_valid": tax_id_valid},
            "employer": {"klu": klu, "jkk_risk_group": jkk, "jkk_relief_eligible": relief, "policy": None},
            "employment": {"start_month": start, "end_month": end}, "periods": periods}


DIMENSIONS = {"ptkp": PTKP, "method": ("gross", "gross_up", "employer_borne"), "pattern": tuple(PATTERNS),
              "income": INCOMES, "salary": SALARIES, "sector": tuple(SECTORS),
              "jkk": ("very_low", "medium", "very_high"), "benefit": BENEFITS, "zakat": (False, True),
              "tax_id_valid": (True, False)}


def covering(dims, t, rng, limit=2000):
    names = list(dims)
    uncovered = set()
    for idx in itertools.combinations(range(len(names)), t):
        for vals in itertools.product(*(range(len(dims[names[i]])) for i in idx)):
            uncovered.add(tuple(zip(idx, vals)))
    rows = []
    while uncovered and len(rows) < limit:
        target = next(iter(uncovered))
        best, best_cov = None, -1
        for _ in range(40):
            cand = [rng.randrange(len(dims[n])) for n in names]
            for i, v in target:
                cand[i] = v
            cov = sum(1 for c in uncovered if all(cand[i] == v for i, v in c))
            if cov > best_cov:
                best, best_cov = cand, cov
        uncovered = {c for c in uncovered if not all(best[i] == v for i, v in c)}
        rows.append({n: dims[n][i] for n, i in zip(names, best)})
    return rows


def coverage(rows, dims, t):
    """Share of t-way value combinations present in rows."""
    names = list(dims)
    total = got = 0
    for idx in itertools.combinations(range(len(names)), t):
        combos = set(itertools.product(*(dims[names[i]] for i in idx)))
        seen = {tuple(r[names[i]] for i in idx) for r in rows}
        total += len(combos)
        got += len(combos & seen)
    return got / total if total else 1.0


def combinatorial(year, rng):
    rows = covering(DIMENSIONS, 2, rng)
    cases = []
    for i, r in enumerate(rows):
        c = make_case(f"SE-{year}-C{i:03d}", year, r["salary"], r["ptkp"], r["method"], r["pattern"], r["income"],
                      r["sector"], r["jkk"], r["benefit"], r["zakat"], r["tax_id_valid"])
        c["criterion"], c["cell"] = "combinatorial", r
        cases.append(c)
    return cases, rows


def _bisect(kb, omega, make, fact, month, target, lo=0, hi=400_000_000):
    """Smallest salary with fact(month) >= target (monotone in salary); (salary, value)."""
    def value(s):
        r = evaluate_case(kb, make(s), omega, outputs=[fact])
        v = (r.year.get(fact) if month == 0 else (r.periods.get(month) or {}).get(fact))
        return v
    if value(hi) is None or value(hi) < target:
        return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = value(mid)
        if v is not None and v >= target:
            hi = mid
        else:
            lo = mid
    return hi, value(hi)


def ter_bounds(kb, omega):
    view = kb.view(omega)
    out = []
    for t in view.tables.get("ter_monthly", ()):
        for row in t.rows:
            if row.get("upper") is not None:
                out.append((row["key"], row["upper"]))
    return sorted(set(out))


def boundary_ter(kb, year, omega):
    cases = []
    for cat, b in ter_bounds(kb, omega):
        status = CATEGORY_STATUS[cat]
        make = (lambda s, st=status: make_case("probe", year, s, st, "gross", "full"))
        found = _bisect(kb, omega, make, "gross_income", 6, b)
        if not found:
            continue
        s_at, _ = found
        for k, s in (("b-1", s_at - 1), ("b", s_at), ("b+1", s_at + 1)):
            c = make_case(f"SE-{year}-T{cat}{b}{k}", year, s, status, "gross", "full")
            r = evaluate_case(kb, c, omega, outputs=["gross_income"])
            c["criterion"] = "boundary_ter"
            c["cell"] = {"category": cat, "bound": b, "side": k, "gross_m6": r.periods[6]["gross_income"]}
            cases.append(c)
    return cases


def boundary_p17(kb, year, omega):
    view = kb.view(omega)
    bounds = sorted({r["upper"] for t in view.tables.get("pasal17", ()) if t.valid_on(date(year, 6, 1))
                     for r in t.rows if r.get("upper")})
    cases = []
    make = (lambda s: make_case("probe", year, s, "TK/0", "gross", "full"))
    for b in bounds:
        for k, target in (("b-1000", b - 1000), ("b", b), ("b+1000", b + 1000)):
            found = _bisect(kb, omega, make, "taxable_income", 0, target, hi=2_000_000_000)
            if not found:
                continue
            s, v = found
            c = make_case(f"SE-{year}-P{b}{k}", year, s, "TK/0", "gross", "full")
            c["criterion"] = "boundary_p17"
            c["cell"] = {"bound": b, "side": k, "pkp": v}
            cases.append(c)
    return cases


def bps_wages():
    out = []
    with open(BPS_WAGES, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                out.append((r["vervar_label"], r["turvar_label"], int(float(r["nilai"]))))
            except (ValueError, KeyError):
                continue
    return [w for w in out if w[2] > 0]


def operational(year, rng, n):
    wages = bps_wages()
    cases = []
    for i in range(n):
        prov, sector, wage = rng.choice(wages)
        section = sector.split()[0]
        pattern = "full" if rng.random() < 0.8 else rng.choice(["join", "leave"])
        c = make_case(f"SE-{year}-O{i:04d}", year, wage, rng.choice(PTKP), "gross", pattern, "thr")
        klu = SECTION_KLU.get(section, "62019")
        c["employer"]["klu"] = klu
        c["employer"]["jkk_relief_eligible"] = klu == "14111"
        c["criterion"] = "operational"
        c["cell"] = {"province": prov, "sector": sector, "wage": wage}
        cases.append(c)
    return cases


def build(kb, omega=date(2026, 10, 27), seed=20261027, operational_n=300, years=YEARS):
    """The global S^E: all criteria for every year, evaluated against the gold chain only to place boundaries."""
    rng = random.Random(seed)
    cases, report = [], {}
    for y in years:
        comb, rows = combinatorial(y, rng)
        ter = boundary_ter(kb, y, omega) if y >= 2024 else []
        p17 = boundary_p17(kb, y, omega)
        ops = operational(y, rng, operational_n)
        cases += comb + ter + p17 + ops
        report[y] = {"combinatorial": len(comb), "coverage_2way": round(coverage(rows, DIMENSIONS, 2), 4),
                     "coverage_3way": round(coverage(rows, DIMENSIONS, 3), 4), "boundary_ter": len(ter),
                     "boundary_p17": len(p17), "operational": len(ops)}
    for c in cases:
        assert all("other_regular" not in p["income"] for p in c["periods"]), "S^E must not use the S^G marker"
    return cases, report


def event_years(event, years=YEARS):
    """Tax years an event is evaluated on: the year before its legal start (earlier periods, A3t) through the year
    its validity ends (or the year after the start when open-ended), within the given years."""
    start = event.effective_from or event.issued
    end = event.effective_until or date(min(start.year + 1, years[-1]), 12, 31)
    return [y for y in years if start.year - 1 <= y <= end.year]


# ---------------------------------------------------------------------- cases with a company policy (RQ4, E2 policy)
JKK_GROUPS = {Fraction(24, 10000): "very_low", Fraction(54, 10000): "low", Fraction(89, 10000): "medium",
              Fraction(127, 10000): "high", Fraction(174, 10000): "very_high"}
PKB_PROFILE = {"PKB-WIKA-2025": ("41011", "high"), "PKB-CENTEX-2024": ("13111", "medium"),
               "PKB-AVCO-2024": ("52230", "very_high"), "PKB-TAEKWANG-2024": ("15201", "low"),
               "PKB-SANSAN-2021": ("14111", "very_low"), "PKB-KOJA-2012": ("52221", "medium")}


def policy_profile(event, delta):
    """(KLU, JKK risk group) of the company of a policy: the KLU from the policy table (or the GT5 profile of a PKB);
    the risk group whose statutory rate equals a rate the policy fixes, else very_low."""
    import ast as _ast
    from .expr.numbers import decimal_value
    klu, risk = PKB_PROFILE.get(event.document, (event.extra.get("klu") or None, None))
    if risk is None:
        risk = "very_low"
        for e in delta["add"]:
            if e.get("kind") == "rule" and e.get("produces") == "jkk_rate":
                for n in _ast.walk(_ast.parse(e["expression"], mode="eval")):
                    if (isinstance(n, _ast.Call) and getattr(n.func, "id", "") == "dec" and n.args
                            and isinstance(n.args[0], _ast.Constant)):
                        risk = JKK_GROUPS.get(Fraction(decimal_value(n.args[0].value)), risk)
    return klu, risk


def _hr_items(delta):
    import ast as _ast
    out = set()
    for e in delta["add"] + delta["change"]:
        for k in ("expression", "condition", "assertion"):
            if e.get(k):
                for n in _ast.walk(_ast.parse(e[k], mode="eval")):
                    if (isinstance(n, _ast.Call) and getattr(n.func, "id", "") == "hr" and n.args
                            and isinstance(n.args[0], _ast.Constant)):
                        out.add(n.args[0].value)
    return sorted(out)


HR_VALUES = (0, 2, 8, 20)


def policy_cases(event, delta, cases_by_year, rng, per_year=60):
    """Cases of the policy's validity years with employer.policy set, the company's KLU and risk group, and the HR
    items its rules read varied over 0, 2, 8, 20 (round robin). Taken from the combinatorial and operational cases."""
    klu, risk = policy_profile(event, delta)
    items = _hr_items(delta)
    start = event.effective_from or event.issued
    end = event.effective_until or date(YEARS[-1], 12, 31)
    out = []
    for y in YEARS:
        if not (start.year <= y <= end.year):
            continue
        pool = [c for c in cases_by_year.get(y, []) if c.get("criterion") in ("combinatorial", "operational")]
        for i, c in enumerate(rng.sample(pool, min(per_year, len(pool)))):
            c = json.loads(json.dumps(c))
            c["case_id"] = f"{c['case_id']}-{event.id}"
            c["employer"].update(policy=event.document, jkk_risk_group=risk)
            if klu:
                c["employer"]["klu"] = klu
            hr = {name: HR_VALUES[(i + j) % len(HR_VALUES)] for j, name in enumerate(items)}
            for p in c["periods"]:
                p["hr"] = dict(hr)
            c["criterion"] = "policy"
            out.append(c)
    return out
