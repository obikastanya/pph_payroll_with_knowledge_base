"""Convert reference cases (GT1, GT3, GT5) into the case format and expected observations, and compare.

Expected observations are keyed ("period", month, fact) or ("year", fact). Only observations that the reference states
are compared. Conversion choices are documented per function, because they are part of the instrument (E0).
"""
import json
from datetime import date
from pathlib import Path

from .config import REPO
from .engine import evaluate_case

GT3_DIR = REPO / "dataset" / "11_acuan" / "gt3_kasus_bertingkat"
RISK = {"sangat rendah": "very_low", "rendah": "low", "sedang": "medium", "tinggi": "high", "sangat tinggi": "very_high"}
METHOD = {"gross": "gross", "gross_up": "gross_up", "ditanggung": "employer_borne"}
INCOME = {"gaji": "base_salary", "tunjangan_tetap": "fixed_allowance", "lembur": "overtime_pay", "thr": "thr",
          "bonus": "bonus"}
BENEFITS = {"natura_rumah_individual": "housing_individual", "kendaraan_dinas": "company_vehicle",
            "kupon_makan_dinas_luar": "meal_coupon_field_duty", "bingkisan_non_hari_raya": "gift_other"}
PERIOD_FACTS = {"bruto": "gross_income", "pph21": "pph21_due", "pph21_dtp": "pph21_dtp",
                "tunjangan_pajak": "tax_allowance"}
YEAR_FACTS = {"bruto_setahun": "annual_gross", "biaya_jabatan": "job_expense", "neto_setahun": "annual_net",
              "ptkp": "ptkp_amount", "pkp": "taxable_income", "pph21_setahun": "annual_pph21",
              "kelebihan_dikembalikan_ke_pegawai": "refund_to_employee"}
PREMIUMS = {"premi_jkk": "jkk_premium", "premi_jkm": "jkm_premium",
            "premi_bpjs_kesehatan_pemberi_kerja": "health_premium_employer", "iuran_jht_pegawai": "jht_employee",
            "iuran_jp_pegawai": "jp_employee"}


def gt3_case(d):
    """GT3 case -> (case, expected). Missing months of a monthly-stratum case are filled with the last stated month
    so that the stated months are not the final period; only stated months are compared. GT3 premium amounts are
    compared as observations (they follow the same wage-based rules), not used as inputs."""
    i = d["input"]
    masa = {m["bulan"]: m["komponen"] for m in i["masa"]}
    start = i.get("bulan_masuk") or 1
    end = i.get("bulan_keluar") or 12
    # monthly-stratum cases state only some months: the employment span stays as stated (or the whole year)
    periods, last = [], None
    for m in range(start, end + 1):
        comp = masa.get(m, last)
        if comp is None:
            comp = masa[min(masa)]
        last = comp
        income = {INCOME[k]: v for k, v in comp.items() if k in INCOME and v}
        benefits = {BENEFITS[k]: v for k, v in comp.items() if k in BENEFITS and v}
        unknown = [k for k in comp if k not in INCOME and k not in BENEFITS and k not in PREMIUMS and k != "zakat"
                   and not k.endswith("pemberi_kerja") and k != "iuran_bpjs_kesehatan_pegawai"]
        if unknown:
            raise ValueError(f"{d['id']}: unmapped components {unknown}")
        periods.append({"month": m, "income": income, "benefits": benefits, "zakat": comp.get("zakat", 0) or 0})
    sek = i.get("sektor") or {}
    female = i.get("jenis_kelamin") == "P"
    case = {"case_id": d["id"], "tax_year": d["tahun_pajak"],
            "employee": {"ptkp_status": i["status_ptkp"], "sex": "F" if female else "M",
                         "husband_no_income_certified": bool(female and not i.get("karyawati_kawin_suami_berpenghasilan")),
                         "tax_id_valid": bool(i.get("npwp_nik_valid", True))},
            "employer": {"klu": sek.get("klu"), "jkk_risk_group": RISK.get(sek.get("kelompok_risiko_jkk"), "very_low"),
                         "jkk_relief_eligible": bool(sek.get("padat_karya_pp7_2025")), "policy": None},
            "method": METHOD[i["metode"]], "employment": {"start_month": start, "end_month": end},
            "periods": periods}
    expected = {}
    for m in d["expected"]["per_masa"]:
        for k, f in PERIOD_FACTS.items():
            if k in m and m[k] is not None:
                expected[("period", m["bulan"], f)] = m[k]
    for m in i["masa"]:
        for k, f in PREMIUMS.items():
            if k in m["komponen"]:
                expected[("period", m["bulan"], f)] = m["komponen"][k]
    for k, f in YEAR_FACTS.items():
        t = d["expected"].get("tahunan") or {}
        if k in t and t[k] is not None:
            expected[("year", f)] = t[k]
    return case, expected


def load_gt3():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(GT3_DIR.glob("GT3-*.json"))]


def observe(result, key):
    if key[0] == "period":
        return (result.periods.get(key[1]) or {}).get(key[2])
    return result.year.get(key[1])


def compare(kb, case, expected, omega):
    """Differences between engine and reference: list of (key, engine, reference)."""
    r = evaluate_case(kb, case, omega)
    diffs = [(k, observe(r, k), v) for k, v in expected.items() if observe(r, k) != v]
    return r, diffs
