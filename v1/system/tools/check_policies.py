"""Check the gold Deltas of the synthetic company policies SP01-SP14 against their worked examples and impact labels.

    env\\Scripts\\python system\\tools\\check_policies.py [--isolated] [--labels] [--write]

For each example (dataset/10_kebijakan_perusahaan/sintetis/SPxx.json, contoh[]) the case is built from CASES below,
the policy is installed on the final gold chain (K* (+) P) and evaluated at omega = 2026-10-27. Reported per
observation: the engine value (mandatory rules win, so it is compared with hasil_menurut_aturan_wajib; for a conflict
through a constraint the policy's value stays, so it is compared with hasil_menurut_kebijakan) and the value in the
"policy world" (policy rules promoted over their regulation rivals), compared with hasil_menurut_kebijakan. The example
field `sama` (policy and mandatory agree) is compared with the presence of a conflict in the observed periods.

--labels computes the RQ4 labels of akuisisi.md Definition 9 by execution for each event E01-E12 between
K*_{n-1} (+) P and K*_n (+) P at omega = t_terbit of E_n, on the policy's example profiles moved to the event's year:
(a) a fact produced by a P rule changes for an observation t >= t_berlaku; (b) the winning rule of a fact produced or
read by P's rules changes; (c) a new conflict entry involving P. Only events whose effective date lies in the policy's
term count (the labelling rule of the manual labels). Agreement with label_dampak is printed; nothing is tuned to it.

--isolated builds the chain without the COVID development module, the fictive regulations, and the PKB policies
(for use while those are being written).
"""
import copy
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "system" / "tools"))

import build_gold  # noqa: E402
from pph21kbs.engine import YEAR, evaluate_case  # noqa: E402
from pph21kbs.engine.evaluator import Evaluator  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

SP_DIR = ROOT / "dataset" / "10_kebijakan_perusahaan" / "sintetis"
EVENTS = ROOT / "dataset" / "09_korpus_peristiwa" / "peristiwa.csv"
OMEGA = date(2026, 10, 27)

# employer profile per policy: KLU (INDEX.csv), JKK risk group (from the policy or its examples), JKK relief eligible
EMPLOYER = {
    "SP01": ("52101", "low", False), "SP02": ("29300", "medium", False), "SP03": ("55110", "very_low", False),
    "SP04": ("09100", "very_low", False), "SP05": ("13112", "low", True), "SP06": ("46411", "very_low", False),
    "SP07": ("47111", "low", False), "SP08": ("62019", "very_low", False), "SP09": ("21012", "low", False),
    "SP10": ("22220", "low", False), "SP11": ("41012", "high", False), "SP12": ("63122", "very_low", False),
    "SP13": ("50131", "high", False), "SP14": ("14111", "low", True),
}
P, Y = "period", "year"

# example id -> case profile and observations {example key: (scope, month or None, fact)}
CASES = {
    "SP01-1": dict(year=2023, ptkp="K/0", wage=12000000, obs={"iuran_jp_pekerja": (P, 4, "jp_employee")}),
    "SP01-2": dict(year=2024, ptkp="TK/0", wage=12000000, obs={"iuran_jp_pekerja": (P, 4, "jp_employee")}),
    "SP01-3": dict(year=2024, ptkp="TK/0", wage=12000000,
                   obs={"neto": (Y, None, "annual_net"), "pkp": (Y, None, "taxable_income"),
                        "pph_setahun": (Y, None, "annual_pph21"), "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP02-1": dict(year=2023, ptkp="K/1", wage=15000000, obs={"pph21": (P, 1, "pph21_due")}),
    "SP02-2": dict(year=2024, ptkp="K/1", wage=15000000, obs={"pph21": (P, 1, "pph21_due")}),
    "SP02-3": dict(year=2024, ptkp="K/1", wage=15000000, income={3: {"bonus": 30000000}},
                   obs={"pph21": (P, 3, "pph21_due")}),
    "SP03-1": dict(year=2025, ptkp="TK/0", wage=6800000,
                   obs={"pph21": (P, 8, "pph21_due"), "dtp_tunai_ke_pekerja": (P, 8, "pph21_dtp"),
                        "penerimaan_bersih": (P, 8, "take_home_pay")}),
    "SP03-2": dict(year=2025, ptkp="TK/0", wage=6800000,
                   obs={"pph21": (P, 10, "pph21_due"), "dtp_tunai_ke_pekerja": (P, 10, "pph21_dtp"),
                        "penerimaan_bersih": (P, 10, "take_home_pay")}),
    "SP03-3": dict(year=2026, ptkp="TK/0", wage=7200000,
                   obs={"pph21": (P, 2, "pph21_due"), "dtp_tunai_ke_pekerja": (P, 2, "pph21_dtp"),
                        "penerimaan_bersih": (P, 2, "take_home_pay")}),
    "SP04-1": dict(year=2023, ptkp="K/2", wage=25000000, benefits={"housing_individual": 6000000},
                   obs={"bruto_pemotongan": (P, 5, "gross_income"), "pph21": (P, 5, "pph21_due")}),
    "SP04-2": dict(year=2023, ptkp="K/2", wage=25000000, benefits={"housing_individual": 6000000},
                   obs={"bruto_pemotongan": (P, 8, "gross_income"), "pph21": (P, 8, "pph21_due")}),
    "SP04-3": dict(year=2024, ptkp="K/2", wage=25000000, benefits={"housing_individual": 6000000},
                   obs={"bruto_pemotongan": (P, 2, "gross_income"), "pph21": (P, 2, "pph21_due")}),
    "SP05-1": dict(year=2025, ptkp="TK/0", wage=5500000,
                   obs={"premi_jkk": (P, 1, "jkk_premium"), "bruto": (P, 1, "gross_income"),
                        "pph21_terutang_dtp": (P, 1, "pph21_due")}),
    "SP05-2": dict(year=2025, ptkp="TK/0", wage=5500000,
                   obs={"premi_jkk": (P, 3, "jkk_premium"), "bruto": (P, 3, "gross_income"),
                        "pph21_terutang_dtp": (P, 3, "pph21_due")}),
    "SP05-3": dict(year=2025, ptkp="TK/0", wage=5500000,
                   obs={"bruto": (Y, None, "annual_gross"), "pkp": (Y, None, "taxable_income"),
                        "pph_setahun": (Y, None, "annual_pph21"), "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP06-1": dict(year=2025, ptkp="K/1", wage=8000000,
                   obs={"bruto": (P, 3, "gross_income"), "tunjangan_pph": (P, 3, "tax_allowance"),
                        "dtp_tunai_ke_pekerja": (P, 3, "pph21_dtp"), "penerimaan_bersih": (P, 3, "take_home_pay")}),
    "SP06-2": dict(year=2026, ptkp="K/1", wage=8000000, klu="14111",
                   obs={"bruto": (P, 2, "gross_income"), "pph21_dtp": (P, 2, "pph21_dtp"),
                        "dtp_tunai_ke_pekerja": (P, 2, "pph21_dtp"), "penerimaan_bersih": (P, 2, "take_home_pay")}),
    "SP07-1": dict(year=2025, ptkp="TK/0", wage=5200000,
                   hr={3: {"thr_holiday": 1, "months_of_service": 8}},
                   obs={"thr": (P, 3, "thr"), "bruto_maret": (P, 3, "gross_income"), "pph21_maret": (P, 3, "pph21_due")}),
    "SP07-2": dict(year=2025, ptkp="K/0", wage=6000000, end=11,
                   hr={11: {"thr_holiday": 1, "months_of_service": 48, "days_terminated_before_holiday": 25}},
                   obs={"thr": (P, 11, "thr"), "bruto_setahun": (Y, None, "annual_gross"),
                        "pph_masa_terakhir": (P, 11, "pph21_due")}),
    "SP07-3": dict(year=2025, ptkp="K/0", wage=6000000, end=11,
                   hr={11: {"thr_holiday": 1, "months_of_service": 48, "days_terminated_before_holiday": 45}},
                   obs={"thr": (P, 11, "thr")}),
    "SP08-1": dict(year=2024, ptkp="K/1", wage=25000000,
                   obs={"pph21_bulanan": (P, 2, "pph21_due"), "biaya_jabatan": (Y, None, "job_expense"),
                        "neto": (Y, None, "annual_net"), "pkp": (Y, None, "taxable_income"),
                        "pph_setahun": (Y, None, "annual_pph21"), "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP08-2": dict(year=2024, ptkp="TK/0", wage=9000000,
                   obs={"pph21_bulanan": (P, 2, "pph21_due"), "biaya_jabatan": (Y, None, "job_expense"),
                        "neto": (Y, None, "annual_net"), "pkp": (Y, None, "taxable_income"),
                        "pph_setahun": (Y, None, "annual_pph21"), "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP08-3": dict(year=2024, ptkp="TK/0", wage=9000000, obs={"pph21": (P, 2, "pph21_due")}),
    "SP09-1": dict(year=2023, ptkp="K/0", wage=9000000,
                   obs={"bruto": (P, 8, "gross_income"), "pph21": (P, 8, "pph21_due")}),
    "SP09-2": dict(year=2024, ptkp="K/0", wage=9000000,
                   obs={"bruto": (P, 3, "gross_income"), "pph21": (P, 3, "pph21_due")}),
    "SP09-3": dict(year=2024, ptkp="K/0", wage=9000000,
                   obs={"bruto": (Y, None, "annual_gross"), "pkp": (Y, None, "taxable_income"),
                        "pph_setahun": (Y, None, "annual_pph21"), "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP10-1": dict(year=2025, ptkp="K/2", wage=7500000,
                   obs={"iuran_jht_pekerja": (P, 3, "jht_employee"), "iuran_jkn_pekerja": (P, 3, "health_employee"),
                        "jkn_pemberi_kerja": (P, 3, "health_premium_employer"), "bruto": (P, 3, "gross_income"),
                        "pph21": (P, 3, "pph21_due"), "penerimaan_bersih": (P, 3, "take_home_pay")}),
    "SP10-2": dict(year=2025, ptkp="K/2", wage=7500000,
                   obs={"bruto": (Y, None, "annual_gross"), "neto": (Y, None, "annual_net"),
                        "pkp": (Y, None, "taxable_income"), "pph_setahun": (Y, None, "annual_pph21"),
                        "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP11-1": dict(year=2025, ptkp="K/2", wage=18000000,
                   obs={"iuran_jp_pekerja": (P, 4, "jp_employee"), "iuran_jkn_pekerja": (P, 4, "health_employee"),
                        "jkn_pemberi_kerja": (P, 4, "health_premium_employer"), "bruto": (P, 4, "gross_income"),
                        "pph21": (P, 4, "pph21_due")}),
    "SP11-2": dict(year=2025, ptkp="K/2", wage=18000000,
                   obs={"bruto": (Y, None, "annual_gross"), "neto": (Y, None, "annual_net"),
                        "pkp": (Y, None, "taxable_income"), "pph_setahun": (Y, None, "annual_pph21"),
                        "pph_masa_terakhir": (P, 12, "pph21_due")}),
    "SP11-3": dict(year=2025, ptkp="TK/0", wage=9500000, end=6,
                   obs={"pph21_juni": (P, 6, "pph21_due"), "pph_setahun": (Y, None, "annual_pph21"),
                        "pengembalian_ke_pegawai": (Y, None, "refund_to_employee")}),
    "SP12-1": dict(year=2024, ptkp="TK/0", wage=20000000,
                   obs={"tunjangan_pph": (P, 2, "tax_allowance"), "bruto": (P, 2, "gross_income"),
                        "pph21": (P, 2, "pph21_due")}),
    "SP12-2": dict(year=2024, ptkp="TK/0", wage=20000000,
                   obs={"tunjangan_desember": (P, 12, "tax_allowance"), "pph_setahun": (Y, None, "annual_pph21")}),
    "SP13-1": dict(year=2024, ptkp="K/3", wage=22000000,
                   obs={"pph_ditanggung": (P, 2, "tax_allowance"), "bruto": (P, 2, "gross_income")}),
    "SP13-2": dict(year=2024, ptkp="K/3", wage=22000000,
                   obs={"pph_ditanggung_desember": (P, 12, "tax_allowance"), "pph_setahun": (Y, None, "annual_pph21")}),
    "SP14-1": dict(year=2025, ptkp="TK/1", wage=5400000,
                   hr={3: {"thr_holiday": 1, "months_of_service": 36}},
                   obs={"thr": (P, 3, "thr"), "thr_dibayar": (P, 3, "thr"), "thr_minimum": (P, 3, "thr_minimum"),
                        "bruto": (P, 3, "gross_income"), "pph21_dtp": (P, 3, "pph21_dtp"),
                        "dtp_tunai_ke_pekerja": (P, 3, "pph21_dtp")}),
    "SP14-2": dict(year=2025, ptkp="TK/1", wage=5400000,
                   hr={3: {"thr_holiday": 1, "months_of_service": 6}},
                   obs={"thr": (P, 3, "thr"), "thr_dibayar": (P, 3, "thr"), "thr_minimum": (P, 3, "thr_minimum"),
                        "bruto": (P, 3, "gross_income"), "pph21_dtp": (P, 3, "pph21_dtp")}),
    "SP14-3": dict(year=2025, ptkp="TK/1", wage=5400000,
                   hr={12: {"thr_holiday": 1, "months_of_service": 24, "days_terminated_before_holiday": 15}},
                   obs={"thr": (P, 12, "thr"), "thr_dibayar": (P, 12, "thr"), "thr_minimum": (P, 12, "thr_minimum")}),
}


def chain(isolated=False):
    if isolated:
        build_gold.MODULES = [m for m in build_gold.MODULES if not m.startswith(("dev_covid", "fr_", "pol_pkb"))]
    return build_gold.build(check_only=True, side=False)


def policy_update(pid):
    return build_gold.side_update(f"GOLD-{pid}")


def install(kb, pid):
    return apply_delta(kb, policy_update(pid).to_json())


def make_case(pid, spec, year=None):
    klu, risk, relief = EMPLOYER[pid]
    year = year or spec["year"]
    start, end = spec.get("start", 1), spec.get("end", 12)
    periods = []
    for m in range(start, end + 1):
        income = {"base_salary": spec["wage"]}
        income.update((spec.get("income") or {}).get(m, {}))
        p = {"month": m, "income": income, "benefits": dict(spec.get("benefits") or {})}
        hr = (spec.get("hr") or {}).get(m)
        if hr:
            p["hr"] = dict(hr)
        periods.append(p)
    return {"case_id": spec.get("id", pid), "tax_year": year, "method": "gross",
            "employee": {"ptkp_status": spec["ptkp"], "sex": "M", "tax_id_valid": True},
            "employer": {"klu": spec.get("klu", klu), "jkk_risk_group": risk, "jkk_relief_eligible": relief,
                         "premiums_as_billed": False, "policy": pid},
            "employment": {"start_month": start, "end_month": end}, "periods": periods}


def _ctx(scope, month):
    return YEAR if scope == Y else month


def evaluate(kb, case, omega, facts):
    view = kb.view(omega)
    names = sorted({f.id for f in view.facts.values() if f.output} | set(facts))
    ev = Evaluator(view, case)
    res = ev.run([n for n in names if n in view.facts])
    return ev, res


def policy_world(kb, pid, omega=OMEGA):
    """K* with the policy's rules promoted to mandatory regulation rules that override every regulation rule producing
    the same fact: the payroll the policy describes, used to compare with hasil_menurut_kebijakan. Not a gold KB."""
    d = copy.deepcopy(policy_update(pid).to_json())
    view = kb.view(omega)
    for e in d["add"]:
        if e["kind"] != "rule":
            continue
        rivals = sorted(r.id for r in view.rules.values() if r.produces == e["produces"] and r.layer == "regulation")
        e.update(layer="regulation", modality="mandatory", overrides=rivals)
        e.pop("policy", None)
    return apply_delta(kb, d, validate=False)


def observe(res, scope, month, fact):
    return res.year.get(fact) if scope == Y else (res.periods.get(month) or {}).get(fact)


def check_examples(kb, verbose=True):
    rows = []
    for pid in EMPLOYER:
        kp = install(kb, pid)
        kw = policy_world(kb, pid)
        doc = json.loads((SP_DIR / f"{pid}.json").read_text(encoding="utf-8"))
        for ex in doc["contoh"]:
            spec = CASES[ex["id"]]
            case = make_case(pid, dict(spec, id=ex["id"]))
            facts = {f for _, _, f in spec["obs"].values()}
            ev, res = evaluate(kp, case, OMEGA, facts)
            _, res_p = evaluate(kw, case, OMEGA, facts)
            months = {m for s, m, _ in spec["obs"].values() if s == P}
            year_obs = any(s == Y for s, _, _ in spec["obs"].values())
            conflicts = sorted({(c["code"], c["source"], c.get("fact") or "", c["month"]) for c in res.conflicts
                                if c["month"] in months or (year_obs and c["month"] in (YEAR, case["periods"][-1]["month"]))
                                or (c["kind"] == "constraint" and c["month"] in months)})
            mand, pol = ex["hasil_menurut_aturan_wajib"], ex["hasil_menurut_kebijakan"]
            # a conflict through a constraint (C10) leaves the policy's value in the engine: compare with the policy
            constraint_only = bool(conflicts) and all(c[1].startswith("CON.") for c in conflicts)
            line_ok = True
            details = []
            for key, (scope, month, fact) in spec["obs"].items():
                got = observe(res, scope, month, fact)
                pval = observe(res_p, scope, month, fact)
                want_m, want_p = mand.get(key), pol.get(key)
                if constraint_only and want_p is not None:
                    want_m = want_p
                m_ok = want_m is None or got == want_m
                p_ok = None if want_p is None else pval == want_p
                line_ok &= m_ok
                rows.append({"policy": pid, "example": ex["id"], "observation": key, "fact": fact,
                             "engine": got, "mandatory_expected": want_m, "policy_world": pval,
                             "policy_expected": want_p, "engine_eq_mandatory": m_ok,
                             "world_eq_policy": "" if p_ok is None else p_ok})
                details.append(f"{key}: engine {got} / wajib {want_m}" + ("" if m_ok else " **")
                               + (f"; kebijakan {pval} / {want_p}" + ("" if p_ok else " **") if p_ok is not None else ""))
            conflict_expected = not ex.get("sama", True)
            conflict_seen = bool(conflicts)
            rows.append({"policy": pid, "example": ex["id"], "observation": "conflict", "fact": "",
                         "engine": ";".join(f"{c[0]}:{c[1]}:{c[2]}@{c[3]}" for c in conflicts), "mandatory_expected": "",
                         "policy_world": "", "policy_expected": "expected" if conflict_expected else "none",
                         "engine_eq_mandatory": conflict_seen == conflict_expected, "world_eq_policy": ""})
            if verbose:
                flag = "ok" if line_ok and conflict_seen == conflict_expected else "DIFF"
                print(f"{ex['id']} [{flag}] conflict expected={conflict_expected} seen={[c[:3] for c in conflicts]}"
                      + (f" errors={res.errors[:2]}" if res.errors else ""))
                for d in details:
                    print("    " + d)
    return rows


# ---------------------------------------------------------------------- RQ4 labels by execution
def _events():
    with open(EVENTS, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f) if r["bagian"] == "uji"}


def _run_labels(kb_before, kb_after, pid, case, omega, t_from, t_to):
    pol_rules = {r.id: r for r in kb_after.view(omega).rules.values() if r.layer == "company" and r.policy == pid}
    produced = {r.produces for r in pol_rules.values()}
    read = set()
    for r in pol_rules.values():
        for e in (r.expression, r.condition):
            if e is not None:
                read |= e.dependencies()
    facts = produced | read
    out = []
    for kb in (kb_before, kb_after):
        ev, res = evaluate(kb, case, omega, facts)
        vals = {k: (v if isinstance(v, (int, str, bool, type(None))) or hasattr(v, "denominator") else repr(v))
                for k, v in ev.memo.items() if k[0] in produced}
        out.append((vals, dict(res.winners), res.conflict_keys()))
    (v0, w0, c0), (v1, w1, c1) = out
    year = case["tax_year"]

    def in_window(m):
        d = date(year, 12, 31) if m == YEAR else date(year, m, 1)
        return t_from <= d <= t_to

    a = any(v0.get(k) != v1.get(k) for k in set(v0) | set(v1) if in_window(k[1]))
    b = any(w0.get(k) != w1.get(k) for k in set(w0) | set(w1) if k[0] in facts)
    c = any(_involves(k, pid) for k in c1 - c0)
    return a, b, c


def _involves(key, pid):
    if key[0] == "override":
        return key[1].startswith(f"PRS.{pid}.")
    return any(r.startswith(f"PRS.{pid}.") for r in key[1])


def labels(kb, verbose=True):
    events = _events()
    ids = [u.update_id for u in kb.updates]
    table = []
    for pid in EMPLOYER:
        doc = json.loads((SP_DIR / f"{pid}.json").read_text(encoding="utf-8"))
        term = (date.fromisoformat(doc["berlaku_mulai"]), date.fromisoformat(doc["berlaku_sampai"]))
        manual = {l["peristiwa"]: (l["terdampak"] == "ya", set(l.get("tipe") or [])) for l in doc["label_dampak"]}
        # scenario profiles (an employer attribute changed, e.g. SP06-2) are not the policy's company
        profiles = [CASES[ex["id"]] for ex in doc["contoh"] if "klu" not in CASES[ex["id"]]]
        for eid in sorted(manual):
            uid = f"GOLD-{eid}"
            ev_row = events[eid]
            t_eff = date.fromisoformat(ev_row["berlaku_mulai"])
            omega = date.fromisoformat(ev_row["tanggal_terbit"])
            got = set()
            if term[0] <= t_eff <= term[1] and uid in ids:
                i = ids.index(uid)
                before = install(kb.until(ids[i - 1]), pid)
                after = install(kb.until(uid), pid)
                for spec in profiles:
                    for year in sorted({t_eff.year, min(t_eff.year + 1, term[1].year)}):
                        case = make_case(pid, dict(spec, id=f"{pid}-{eid}-{year}"), year=year)
                        a, b, c = _run_labels(before, after, pid, case, omega, t_eff, term[1])
                        got |= {k for k, v in (("a", a), ("b", b), ("c", c)) if v}
            want_yes, want_types = manual[eid]
            table.append({"policy": pid, "event": eid, "manual": ",".join(sorted(want_types)) if want_yes else "-",
                          "execution": ",".join(sorted(got)) or "-"})
    if verbose:
        agree = sum((r["manual"] != "-") == (r["execution"] != "-") for r in table)
        print(f"impact (any type): {agree}/{len(table)} pairs agree")
        for t in "abc":
            tp = sum(t in r["manual"] and t in r["execution"] for r in table)
            fn = sum(t in r["manual"] and t not in r["execution"] for r in table)
            fp = sum(t not in r["manual"] and t in r["execution"] for r in table)
            tn = len(table) - tp - fn - fp
            print(f"   type {t}: both {tp}, manual only {fn}, execution only {fp}, neither {tn}")
        yy = sum(r["manual"] != "-" and r["execution"] != "-" for r in table)
        yn = sum(r["manual"] != "-" and r["execution"] == "-" for r in table)
        ny = sum(r["manual"] == "-" and r["execution"] != "-" for r in table)
        print(f"   any: both {yy}, manual only {yn}, execution only {ny}, neither {len(table) - yy - yn - ny}")
        for r in table:
            if r["manual"] != r["execution"]:
                print(f"   {r['policy']} {r['event']}: manual {r['manual']} execution {r['execution']}")
    return table


def main():
    kb = chain("--isolated" in sys.argv)
    rows = check_examples(kb)
    ex = {(r["example"]) for r in rows}
    bad = {r["example"] for r in rows if r["engine_eq_mandatory"] is False}
    print(f"examples: {len(ex) - len(bad)}/{len(ex)} with engine = mandatory result and conflict as expected")
    table = labels(kb) if "--labels" in sys.argv else []
    if "--write" in sys.argv:
        out = ROOT / "docs" / "hasil"
        out.mkdir(parents=True, exist_ok=True)
        for name, data in (("kebijakan_sintetis_contoh.csv", rows), ("kebijakan_sintetis_label.csv", table)):
            if data:
                with open(out / name, "w", encoding="utf-8", newline="") as f:
                    w = csv.DictWriter(f, list(data[0]), lineterminator="\n")
                    w.writeheader()
                    w.writerows(data)


if __name__ == "__main__":
    main()
