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
    """Engine value of an expected observation. A tuple of fact names means "any of them is true" (used for DTP
    eligibility, which the regulation states once but the knowledge base splits by sector)."""
    if isinstance(key[-1], tuple):
        return any(observe(result, key[:-1] + (name,)) for name in key[-1])
    if key[0] == "period":
        return (result.periods.get(key[1]) or {}).get(key[2])
    return result.year.get(key[1])


def compare(kb, case, expected, omega):
    """Differences between engine and reference: list of (key, engine, reference). Intermediate facts named by the
    reference are evaluated as well as the outputs."""
    view = kb.view(omega)
    names = {f.id for f in view.facts.values() if f.output}
    for k in expected:
        names |= set(k[-1]) if isinstance(k[-1], tuple) else {k[-1]}
    r = evaluate_case(view, case, outputs=sorted(n for n in names if n in view.facts))
    diffs = [(k, observe(r, k), v) for k, v in expected.items() if observe(r, k) != v]
    return r, diffs


# ---------------------------------------------------------------------- GT1: official worked examples (development)
GT1_DIR = REPO / "dataset" / "07_kasus_uji_resmi"
GT1_INCOME = {"gaji": "base_salary", "gaji_pokok": "base_salary", "gaji_tunjangan_tetap": "base_salary",
              "tunjangan_istri_anak": "fixed_allowance", "tunjangan_jabatan": "fixed_allowance",
              "tunjangan_kinerja": "fixed_allowance", "tunjangan_pajak": "other_regular", "lembur": "overtime_pay",
              "thr": "thr", "bonus": "bonus", "gaji_ketiga_belas": "other_irregular",
              "rapel_tunjangan_kinerja": "other_irregular"}
GT1_BILLED = {"iuran_pensiun_pegawai": "jp_employee", "iuran_pensiun_pegawai_sebulan": "jp_employee",
              "iuran_jht_pegawai": "jht_employee", "iuran_jht_pegawai_sebulan": "jht_employee",
              "premi_jkk": "jkk_premium", "premi_jkk_sebulan": "jkk_premium",
              "premi_jkm": "jkm_premium", "premi_jkm_sebulan": "jkm_premium"}
GT1_BENEFITS = {"natura_beasiswa": "other_benefit"}
GT1_ZAKAT = {"sumbangan_keagamaan_wajib"}
# Components outside the case model: pay stated per week or day, foreign currency, back pay of earlier months
# (rapel), and benefits in kind before 2023 from an employer taxed on deemed profit.
GT1_UNSUPPORTED = {"gaji_mingguan": "upah mingguan", "gaji_harian": "upah harian", "gaji_valas_usd": "mata uang asing",
                   "rapel_gaji_jan_mei": "rapel masa lalu", "natura_beras": "natura sebelum 2023",
                   "natura_gula": "natura sebelum 2023"}
GT1_PERIOD = {"bruto": "gross_income", "pph21": "pph21_due", "pph21_dtp": "pph21_dtp", "tarif_ter": "ter_rate",
              "biaya_jabatan_bulanan": "job_expense_month", "iuran_pensiun_bulanan": "employee_pension_contributions",
              "iuran_jht_bulanan": "jht_employee", "neto_sebulan": "net_regular_month",
              "pkp_bulanan": "taxable_regular_annualized", "pph21_setahun_bulanan": "pph_regular_annual",
              "pph21_teratur": "pph_regular_month", "pph21_tidak_teratur": "pph_irregular_month",
              "pkp_dengan_tidak_teratur": "taxable_with_irregular", "pkp_tanpa_tidak_teratur": "taxable_without_irregular"}
GT1_YEAR = {"bruto_setahun": "annual_gross", "biaya_jabatan": "job_expense", "neto_setahun": "annual_net",
            "ptkp": "ptkp_amount", "pkp": "taxable_income", "pph21_setahun": "annual_pph21",
            "pph21_masa_terakhir": "final_period_tax", "pph21_dipotong_sebelumnya": "withheld_before_final",
            "iuran_pengurang": "annual_pension_contributions", "zakat": "annual_zakat_deduction",
            "lebih_bayar_dikembalikan": "refund_to_employee", "kategori_ter": "ter_category",
            "berhak_dtp": ("dtp_eligible", "dtp_eligible_tourism")}
GT1_METHOD = {"gross": "gross", "gross_up": "gross_up", "ditanggung_pemberi_kerja": "employer_borne"}


class Unsupported(ValueError):
    """A reference case uses something outside the case model; it is reported, not compared."""


def gt1_split():
    import csv
    with open(GT1_DIR / "pembagian_holdout.csv", encoding="utf-8") as f:
        return {r["berkas"]: r["bagian"] for r in csv.DictReader(f)}


def load_gt1_dev():
    """Development GT1 cases only. Holdout files are never opened here (Tahap 8, GT1 holdout)."""
    return load_gt1("pengembangan")


def load_gt1(wanted):
    """GT1 cases of one split. The holdout split is read only by system/tools/e0_holdout.py, once (E0)."""
    out = []
    by_stem = {p.stem.replace("-", "_"): p for p in (GT1_DIR / "kanonik").glob("*.json")}
    for name, part in sorted(gt1_split().items()):
        if part != wanted:
            continue
        path = by_stem.get(Path(name).stem.replace("-", "_"))
        if path is None:            # not transcribed: outside the case model (kanonik/buat_kanonik.py)
            print(f"GT1 {name}: no canonical transcription (outside the case model)")
            continue
        out.append(json.loads(path.read_text(encoding="utf-8")))
    return out


def _gt1_value(v):
    from fractions import Fraction
    if isinstance(v, str) and "/" in v:
        return Fraction(v)
    return v


def gt1_case(c):
    """Canonical GT1 case -> (case, expected, not_compared). Premiums and employee contributions stated by the example
    are inputs (premiums_as_billed); a single-month example is placed in a full year whose other months repeat its
    regular components, so that the stated month is not the final period unless the example says so."""
    codes = {k["kode"] for m in c["masa"] for k in m["komponen"]}
    bad = sorted({GT1_UNSUPPORTED[k] for k in codes if k in GT1_UNSUPPORTED})
    if bad or c["pemberi_kerja"].get("jenis") not in (None, "biasa"):
        raise Unsupported(", ".join(bad) or f"pemberi kerja {c['pemberi_kerja'].get('jenis')}")
    unknown = sorted(codes - set(GT1_INCOME) - set(GT1_BILLED) - set(GT1_BENEFITS) - GT1_ZAKAT)
    if unknown:
        raise Unsupported(f"komponen belum dipetakan: {unknown}")
    peg = c["pegawai"]
    # an official example that gives a married female employee a K/ status applies the certificate that her husband
    # has no income (tafsir K16; PER-16 I.1.3)
    female = peg.get("jenis_kelamin") == "P"
    stated = {m["bulan"]: m["komponen"] for m in c["masa"]}
    single = c["cakupan"] == "satu_masa"
    if single:
        month = next(iter(stated))
        start, end = peg.get("bulan_masuk") or 1, peg.get("bulan_terakhir_bekerja") or 12
        regular = [k for k in stated[month] if k["kategori"] in ("teratur", "iuran_pengurang", "premi_objek", "zakat")]
        months = {m: (stated[month] if m == month else regular) for m in range(start, end + 1)}
    else:
        months = stated
        start, end = min(stated), max(stated)
    periods = []
    for m, comps in sorted(months.items()):
        income, benefits, zakat = {}, {}, 0
        for k in comps:
            code, v = k["kode"], k["nominal"]
            if code in GT1_INCOME:
                income[GT1_INCOME[code]] = income.get(GT1_INCOME[code], 0) + v
            elif code in GT1_BILLED:
                income[GT1_BILLED[code]] = income.get(GT1_BILLED[code], 0) + v
            elif code in GT1_BENEFITS:
                benefits[GT1_BENEFITS[code]] = benefits.get(GT1_BENEFITS[code], 0) + v
            else:
                zakat += v
        periods.append({"month": m, "income": income, "benefits": benefits, "zakat": zakat})
    case = {"case_id": c["id"], "tax_year": c["tahun_pajak"],
            "employee": {"ptkp_status": peg["status_ptkp"], "sex": "F" if female else "M",
                         "husband_no_income_certified": bool(
                             female and peg["status_ptkp"].startswith("K/")
                             and peg.get("suami_tidak_berpenghasilan_terbukti", True) is not False),
                         "tax_id_valid": bool(peg.get("punya_npwp", True)),
                         "contract_fixed_income": (c.get("dtp") or {}).get("penghasilan_tetap_teratur_kontrak_januari"),
                         "subjective_start_month": peg.get("subjektif_mulai_bulan"),
                         "subjective_end_month": peg.get("subjektif_akhir_bulan")},
            "employer": {"klu": c["pemberi_kerja"].get("klu"), "jkk_risk_group": "very_low",
                         "jkk_relief_eligible": False, "premiums_as_billed": True, "policy": None},
            "method": GT1_METHOD[c["metode"]], "employment": {"start_month": start, "end_month": end},
            "periods": periods}
    expected, skipped = {}, []
    for h in c["harapan"]:
        name, month, value = h["fakta"], h["bulan"], _gt1_value(h["nilai"])
        if name in GT1_PERIOD:
            m = month if month is not None else (next(iter(stated)) if single else None)
            if m is None:
                skipped.append(name)
                continue
            expected[("period", m, GT1_PERIOD[name])] = value
        elif name in GT1_YEAR:
            expected[("year", GT1_YEAR[name])] = value
        else:
            skipped.append(name)
    return case, expected, sorted(set(skipped))


# ---------------------------------------------------------------------- GT5: company policy worked examples
GT5_DIR = REPO / "dataset" / "11_acuan" / "gt5_contoh_kebijakan"
GT5_POLICY = {"WIKA": ("PKB-WIKA-2025", "GOLD-PKB-WIKA"), "CENTEX": ("PKB-CENTEX-2024", "GOLD-PKB-CENTEX"),
              "AVCO": ("PKB-AVCO-2024", "GOLD-PKB-AVCO"), "TKG": ("PKB-TAEKWANG-2024", "GOLD-PKB-TKG"),
              "SANSAN": ("PKB-SANSAN-2021", "GOLD-PKB-SANSAN")}


def _gt5_base(policy, year, ptkp, employer, income, employee=None, months=range(1, 13)):
    return {"policy": policy, "year": year, "ptkp": ptkp, "employer": employer, "income": income,
            "employee": employee or {}, "months": list(months), "hr": {}, "month_income": {}}


_WIKA = dict(employer={"klu": "41011", "jkk_risk_group": "high"}, income={"base_salary": 12000000,
                                                                          "other_regular": 6000000})
_CENTEX = dict(employer={"klu": "13111", "jkk_risk_group": "medium", "jkk_relief_eligible": True},
               income={"base_salary": 5400000, "fixed_allowance": 650000})
_AVCO = dict(employer={"klu": "52230", "jkk_risk_group": "very_high"})
_TKG = dict(employer={"klu": "15201", "jkk_risk_group": "low", "jkk_relief_eligible": True, "transport_per_day": 15000},
            income={"base_salary": 3600000, "fixed_allowance": 100000, "attendance_allowance": 150000})
_SANSAN = dict(employer={"klu": "14111", "jkk_risk_group": "very_low", "meal_allowance_per_day": 15000})

# Conversion of each worked example (GT5 README "Asumsi umum" and the example's asumsi). One entry per employee in the
# example: case attributes, HR data per month, and the expected observations as (observation key, nilai_harapan key).
# ("conflict", month, code) observes whether the engine reports a conflict with that code in that month.
GT5_SPECS = {
    "GT5-WIKA-01": [dict(_WIKA, year=2025, ptkp="TK/0", hr={3: {"thr_holiday": 1, "months_of_service": 6}},
                         expect=[(("period", 3, "thr"), "thr"), (("period", 3, "gross_income"), "bruto_maret"),
                                 (("period", 3, "pph21_due"), "pph21_maret"),
                                 (("period", 3, "take_home_pay"), "take_home")])],
    "GT5-WIKA-02": [dict(_WIKA, year=2025, ptkp="TK/0", month_income={6: {"bonus": 20000000}},
                         expect=[(("period", 6, "pph21_due"), "pph_total"),
                                 (("period", 6, "tax_allowance"), "pph_perusahaan")])],
    "GT5-WIKA-03": [dict(_WIKA, year=2025, ptkp="TK/0", hr={2: {"leave_pay_paid": 1, "service_years": 20},
                                                           3: {"award_paid": 1, "service_years": 20}},
                         expect=[(("period", 2, "gross_income"), "bruto_feb"), (("period", 2, "pph21_due"), "pph21_feb"),
                                 (("period", 2, "jp_employee"), "iuran_jp"),
                                 (("period", 2, "take_home_pay"), "take_home"),
                                 (("period", 3, "wika_service_award"), "satya_karya")])],
    "GT5-WIKA-04": [dict(_WIKA, year=2025, ptkp="TK/0", months=range(1, 11),
                         hr={3: {"thr_holiday": 1, "months_of_service": 80}, 7: {"leave_pay_paid": 1, "service_years": 7},
                             10: {"separation_paid": 1, "separation_reason": "resign", "months_of_service": 88}},
                         expect=[(("period", 10, "wika_separation_pay"), "uang_pisah"),
                                 (("year", "withheld_before_final"), "pph_jan_sep"),
                                 (("year", "taxable_income"), "pkp"), (("year", "annual_pph21"), "pph_setahun"),
                                 (("period", 10, "pph21_due"), "pph_oktober")])],
    "GT5-WIKA-05": [dict(_WIKA, employer={"klu": "13111", "jkk_risk_group": "high"}, year=2025, ptkp="TK/0",
                         income={"base_salary": 6000000, "other_regular": 3000000},
                         expect=[(("period", 1, "gross_income"), "bruto_jan"), (("period", 1, "pph21_due"), "pph_jan"),
                                 (("period", 1, "pph21_dtp"), "dtp_wajib_tunai"),
                                 (("conflict", 1, "C4"), "selisih_konflik")])],
    "GT5-CENTEX-01": [dict(_CENTEX, year=2025, ptkp="K/1",
                           hr={5: {"ot_work_h1": 60, "ot_work_h2plus": 120, "ot_rest_h1_7": 420, "ot_rest_h8": 60,
                                   "ot_rest_h9": 60, "night_shifts_4g3s": 1}},
                           expect=[(("period", 5, "centex_ot_workday"), "lembur_biasa"),
                                   (("period", 5, "centex_ot_restday"), "lembur_libur"),
                                   (("period", 5, "centex_ot_scheduled"), "lembur_malam")])],
    "GT5-CENTEX-02": [dict(_CENTEX, year=2025, ptkp="K/1", hr={3: {"thr_holiday": 1, "months_of_service": 5}},
                           expect=[(("period", 3, "thr"), "thr"), (("period", 3, "gross_income"), "bruto_maret"),
                                   (("period", 3, "pph21_due"), "pph_maret"), (("conflict", 3, "C6"), "pph_jkk_pkb"),
                                   (("period", 3, "pph21_dtp"), "dtp_tunai"),
                                   (("period", 3, "take_home_pay"), "take_home")])],
    "GT5-CENTEX-03": [dict(_CENTEX, year=2026, ptkp="TK/0", hr={1: {"bonus_paid": 1, "months_of_service": 8}},
                           expect=[(("period", 1, "bonus"), "bonus"), (("period", 1, "gross_income"), "bruto_jan"),
                                   (("period", 1, "pph21_due"), "pph_jan"),
                                   (("period", 1, "take_home_pay"), "take_home")])],
    "GT5-CENTEX-04": [dict(_CENTEX, year=2025, ptkp="K/1",
                           employee={"centex_four_group_three_shift": True, "service_years": 2,
                                     "attendance_permille": 990},
                           hr={2: {"days_absent_unpaid": 2}, 12: {"leave_days_paid": 4}},
                           expect=[(("period", 2, "centex_absence_deduction"), "potongan_4g3s"),
                                   (("period", 12, "centex_leave_compensation"), "sisa_cuti"),
                                   (("period", 2, "gross_income"), "bruto_feb"), (("period", 2, "pph21_due"), "pph_feb")]),
                      dict(_CENTEX, year=2025, ptkp="K/1",
                           employee={"centex_four_group_three_shift": False, "service_years": 2,
                                     "attendance_permille": 990},
                           hr={2: {"days_absent_unpaid": 2}},
                           expect=[(("period", 2, "centex_absence_deduction"), "potongan_non")])],
    "GT5-AVCO-01": [dict(_AVCO, year=2025, ptkp="K/2", income={"base_salary": 12238300},
                         employee={"avco_pratama": True, "avco_work_pattern": "5-2"},
                         hr={5: {"ot_work_h1": 60, "ot_work_h2plus": 120, "ot_rest_h1_7": 420, "ot_rest_h8": 60,
                                 "ot_rest_h9": 60, "ot_rest_h10plus": 60, "days_present": 21}},
                         expect=[(("period", 5, "overtime_pay"), "lembur"), (("period", 5, "gross_income"), "bruto_mei"),
                                 (("period", 5, "pph21_due"), "pph_mei"),
                                 (("period", 5, "take_home_pay"), "take_home")])],
    "GT5-AVCO-02": [dict(_AVCO, year=2025, ptkp="K/2", income={"base_salary": 10169300},
                         employee={"avco_pratama": True, "avco_shift_location": "non_mine"},
                         hr={3: {"thr_holiday": 1, "months_of_service": 7, "shift_days": 20, "days_present": 20}},
                         expect=[(("period", 3, "thr"), "thr"), (("period", 3, "gross_income"), "bruto_maret"),
                                 (("period", 3, "pph21_due"), "pph_maret"), (("period", 3, "jp_employee"), "iuran_jp"),
                                 (("period", 3, "take_home_pay"), "take_home")])],
    "GT5-AVCO-03": [dict(_AVCO, year=2025, ptkp="TK/0", income={"base_salary": 13367100},
                         employee={"avco_pratama": True}, hr={6: {"radiation_net": 950000}},
                         expect=[(("period", 6, "avco_radiation_allowance"), "radiasi_gross"),
                                 (("period", 6, "pph21_due"), "pph_juni")])],
    "GT5-AVCO-04": [dict(_AVCO, year=2025, ptkp="TK/0", income={"base_salary": 12238300},
                         employee={"avco_pratama": True, "avco_work_pattern": "5-2"},
                         hr={7: {"days_absent_unpaid": 1, "days_present": 20}},
                         expect=[(("period", 7, "avco_absence_deduction"), "potongan_5_2"),
                                 (("period", 7, "gross_income"), "bruto_juli"),
                                 (("period", 7, "pph21_due"), "pph_juli")]),
                    dict(_AVCO, year=2025, ptkp="TK/0", income={"base_salary": 12238300},
                         employee={"avco_pratama": True, "avco_work_pattern": "6-1"},
                         hr={7: {"days_absent_unpaid": 1, "days_present": 20}},
                         expect=[(("period", 7, "avco_absence_deduction"), "potongan_6_1")])],
    "GT5-TKG-01": [dict(_TKG, year=2025, ptkp="K/0",
                        hr={3: {"thr_holiday": 1, "months_of_service": 50, "service_years": 4, "days_present": 22,
                                "workdays_in_month": 22}},
                        expect=[(("period", 3, "thr"), "thr_A"), (("period", 3, "gross_income"), "bruto_maret"),
                                (("period", 3, "pph21_due"), "pph_maret"),
                                (("period", 3, "take_home_pay"), "take_home")]),
                   dict(_TKG, year=2025, ptkp="K/0",
                        hr={3: {"thr_holiday": 1, "months_of_service": 5, "service_years": 0, "days_present": 22,
                                "workdays_in_month": 22}},
                        expect=[(("period", 3, "thr"), "thr_B")])],
    "GT5-TKG-02": [dict(_TKG, year=2025, ptkp="K/0", employee={"tkg_work_pattern": "5"},
                        hr={5: {"ot_work_h1": 60, "ot_work_h2plus": 180, "ot_rest_h1_7": 420, "ot_rest_h8": 60,
                                "ot_rest_h9": 60, "ot_rest_h10plus": 60}},
                        expect=[(("period", 5, "tkg_ot_workday"), "lembur_hari_kerja"),
                                (("period", 5, "tkg_ot_restday"), "lembur_istirahat")])],
    "GT5-TKG-03": [dict(_TKG, year=2025, ptkp="TK/0", months=range(6, 13),
                        hr={6: {"calendar_days_worked": 21, "calendar_days_in_month": 30, "days_present": 15,
                                "workdays_in_month": 21}},
                        expect=[(("period", 6, "tkg_prorated_wage"), "upah_kalender"),
                                (("period", 6, "gross_income"), "bruto_juni"), (("period", 6, "pph21_due"), "pph_juni")])],
    "GT5-TKG-04": [dict(_TKG, year=2025, ptkp="TK/0",
                        hr={7: {"days_absconded": 1, "days_present": 21, "workdays_in_month": 22}},
                        expect=[(("period", 7, "tkg_attendance_allowance"), "kehadiran_kasus1"),
                                (("period", 7, "tkg_transport"), "transport_kasus1")]),
                   dict(_TKG, year=2025, ptkp="TK/0",
                        hr={7: {"late_count": 2, "days_present": 22, "workdays_in_month": 22}},
                        expect=[(("period", 7, "tkg_attendance_allowance"), "kehadiran_kasus2"),
                                (("period", 7, "tkg_transport"), "transport_kasus2")])],
    "GT5-SANSAN-01": [dict(_SANSAN, year=2024, ptkp="TK/0",
                           income={"base_salary": 3700000, "attendance_premium": 740000},
                           employee={"sansan_division": "garment"},
                           hr={4: {"thr_holiday": 1, "months_of_service": 8, "days_present": 22}},
                           expect=[(("period", 4, "thr"), "thr_A"), (("period", 4, "gross_income"), "bruto_april"),
                                   (("period", 4, "pph21_due"), "pph_april"),
                                   (("period", 4, "take_home_pay"), "take_home")]),
                      dict(_SANSAN, year=2024, ptkp="TK/0", months=range(3, 13), income={"base_salary": 3700000},
                           employee={"sansan_division": "garment"},
                           hr={4: {"thr_holiday": 1, "months_of_service": 1}},
                           expect=[(("period", 4, "thr"), "thr_B_pkb"), (("conflict", 4, "C10"), "thr_B_regulasi")])],
    "GT5-SANSAN-02": [dict(_SANSAN, year=2024, ptkp="TK/0",
                           income={"base_salary": 3700000, "attendance_premium": 1000000},
                           employee={"sansan_division": "garment"},
                           hr={1: {"days_absent": 0}, 2: {"days_absent": 1}, 3: {"days_absent": 2}},
                           expect=[(("period", 1, "sansan_attendance_premium"), "premi_baca_B"),
                                   (("period", 2, "sansan_attendance_premium"), "absen1_B"),
                                   (("period", 3, "sansan_attendance_premium"), "absen2")])],
    "GT5-SANSAN-03": [dict(_SANSAN, year=2024, ptkp="K/1", income={"base_salary": 9500000, "fixed_allowance": 1500000},
                           employee={"sansan_division": "garment"},
                           hr={4: {"thr_holiday": 1, "months_of_service": 24}},
                           expect=[(("year", "withheld_before_final"), "pph_jan_nov"),
                                   (("period", 12, "pph21_due"), "pph_desember_regulasi")])],
    "GT5-SANSAN-04": [dict(_SANSAN, employer=dict(_SANSAN["employer"], regional_minimum_wage=3241929), year=2024,
                           ptkp="TK/0", income={"base_salary": 3700000}, employee={"sansan_division": "garment"},
                           hr={6: {"separation_paid": 1, "separation_reason": "resign", "service_years": 16}},
                           expect=[(("period", 6, "sansan_separation_pay"), "uang_pisah")])],
}


def load_gt5():
    out = []
    for p in sorted(GT5_DIR.glob("PKB_*.json")):
        out += json.loads(p.read_text(encoding="utf-8"))["contoh"]
    return out


def _gt5_value(v):
    from fractions import Fraction
    if isinstance(v, float):
        return Fraction(str(v))
    return v


def gt5_cases(example):
    """GT5 example -> list of (policy doc id, policy update id, case, expected). Expected keys as in compare(); the
    value of a ("conflict", month, code) key is True."""
    out = []
    short = example["id"].split("-")[1]
    doc_id, update_id = GT5_POLICY[short]
    for spec in GT5_SPECS[example["id"]]:
        months = list(spec.get("months", range(1, 13)))
        periods = []
        for m in months:
            income = dict(spec.get("income", {}))
            income.update(spec.get("month_income", {}).get(m, {}))
            periods.append({"month": m, "income": income, "hr": dict(spec.get("hr", {}).get(m, {}))})
        employer = {"jkk_risk_group": "very_low", "jkk_relief_eligible": False, "policy": doc_id}
        employer.update(spec["employer"])
        employee = {"ptkp_status": spec["ptkp"], "sex": "M", "tax_id_valid": True}
        employee.update(spec.get("employee", {}))
        case = {"case_id": example["id"], "tax_year": spec["year"], "employee": employee, "employer": employer,
                "method": "gross", "employment": {"start_month": months[0], "end_month": months[-1]},
                "periods": periods}
        expected = {}
        for key, name in spec["expect"]:
            value = example["nilai_harapan"][name]
            expected[key] = True if key[0] == "conflict" else _gt5_value(value)
        out.append((doc_id, update_id, case, expected))
    return out


def observe_gt5(result, key):
    if key[0] == "conflict":
        return any(c.get("month") == key[1] and c.get("code") == key[2] for c in result.conflicts)
    return observe(result, key)


def compare_gt5(kb, case, expected, omega):
    """Like compare(), with conflict observations."""
    view = kb.view(omega)
    names = {f.id for f in view.facts.values() if f.output} | {k[-1] for k in expected if k[0] != "conflict"}
    r = evaluate_case(view, case, outputs=sorted(n for n in names if n in view.facts))
    diffs = [(k, observe_gt5(r, k), v) for k, v in expected.items() if observe_gt5(r, k) != v]
    return r, diffs
