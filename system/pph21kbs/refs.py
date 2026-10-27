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
    out = []
    by_stem = {p.stem.replace("-", "_"): p for p in (GT1_DIR / "kanonik").glob("*.json")}
    for name, part in sorted(gt1_split().items()):
        if part != "pengembangan":
            continue
        path = by_stem[Path(name).stem.replace("-", "_")]
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
                         "husband_no_income_certified": bool(female and peg["status_ptkp"].startswith("K/")),
                         "tax_id_valid": bool(peg.get("punya_npwp", True)),
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
