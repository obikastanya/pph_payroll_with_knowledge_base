"""Convert a sealed worked example (contoh.json) into the engine's case format and expected observations.

Conventions (documented in RINGKASAN.md):
- Premiums and contributions are stated in the example input, so employer.premiums_as_billed = True and they enter
  as income components (the knowledge base already reads them that way: REG.INPUT.BILLED.*).
- Months: the case holds the stated months. If the last stated month is neither December nor masa_terakhir, the
  example has no final period; months up to December are filled with the last stated month (as refs.gt3_case does)
  and only stated months are compared.
- Dates are passed as text and also split into integer parts (year, month, day), because the expression language has
  no date arithmetic (representasi.md 10.6: the case must hold the attribute).
- Unknown components keep an English name (open case model: income/hr accept new names).
"""
import json

from common import SEALED

INCOME = {"gaji_pokok": "base_salary", "tunjangan_tetap": "fixed_allowance", "bonus": "bonus", "thr": "thr",
          "lembur": "overtime_pay", "premi_jkk": "jkk_premium", "premi_jkm": "jkm_premium",
          "premi_jkn": "health_premium_employer", "iuran_jht_pegawai": "jht_employee",
          "iuran_jp_pegawai": "jp_employee", "iuran_tapera_pegawai": "tapera_employee",
          "iuran_tapera_pemberi_kerja": "tapera_employer", "penggantian_internet": "internet_reimbursement",
          "tunjangan_internet": "internet_allowance"}
PERIOD_HR = {"hari_kerja_jarak_jauh": "remote_work_days", "jumlah_pegawai_tetap_akhir_bulan": "permanent_headcount"}
PERIOD = {"bruto": "gross_income", "pph21": "pph21_due", "pph21_dipotong": "employee_tax_burden",
          "pph21_dtp": "pph21_dtp", "tunjangan_pph21": "tax_allowance"}
YEAR = {"bruto_setahun": "annual_gross", "biaya_jabatan": "job_expense", "neto": "annual_net", "ptkp": "ptkp_amount",
        "pkp": "taxable_income", "pph21_setahun": "annual_pph21"}
SECTOR = {"lainnya": "other", "padat_karya": "labour_intensive", "pariwisata": "tourism"}


def load(uid):
    return json.loads((SEALED / uid / "contoh.json").read_text(encoding="utf-8"))


def _date_parts(prefix, text, out):
    y, m, d = (int(x) for x in text.split("-"))
    out[f"{prefix}_date"] = text
    out[f"{prefix}_year"], out[f"{prefix}_month"], out[f"{prefix}_day"] = y, m, d


def to_case(ex, policy=None, method=None, extra_employee=None, extra_employer=None):
    i = ex["input"]
    masa = sorted(i["masa"], key=lambda m: m["bulan"])
    stated = [m["bulan"] for m in masa]
    final_stated = stated[-1] == 12 or i.get("masa_terakhir") == stated[-1]
    emp = {"ptkp_status": i["status_ptkp"], "sex": "F" if i.get("jenis_kelamin") == "P" else "M",
           "husband_no_income_certified": bool(i.get("keterangan_suami_tidak_berpenghasilan", False)),
           "tax_id_valid": bool(i.get("nik_npwp_terintegrasi", True)),
           "tax_id_integrated": bool(i.get("nik_npwp_terintegrasi", True))}
    if "menerima_dtp_lain" in i:
        emp["other_dtp_incentive"] = bool(i["menerima_dtp_lain"])
    if "surat_pernyataan_tanggungan" in i:
        emp["dependants_statement"] = bool(i["surat_pernyataan_tanggungan"])
    if "golongan" in i:
        emp["grade"] = i["golongan"]
    if "kewajiban_subjektif_tengah_tahun" in i:
        emp["subjective_change_mid_year"] = bool(i["kewajiban_subjektif_tengah_tahun"])
    for key, prefix in (("tanggal_mulai_bekerja", "start"), ("tanggal_lahir", "birth"), ("tanggal_berhenti", "end")):
        if i.get(key):
            _date_parts(prefix, i[key], emp)
    dp = i.get("data_pegawai") or {}
    names = {"gaji_pokok_lama": "old_base_salary", "tunjangan_tetap": "contract_fixed_allowance"}
    for k, v in dp.items():
        if k in ("tanggal_berhenti", "tanggal_mulai_bekerja"):
            _date_parts("end" if k == "tanggal_berhenti" else "start", v, emp)
        else:
            emp[names.get(k, k)] = v
    emp.update(extra_employee or {})
    er = {"klu": i.get("klu"), "jkk_risk_group": "very_low", "jkk_relief_eligible": False, "policy": policy,
          "premiums_as_billed": True}
    if "sektor" in i:
        er["sector"] = SECTOR[i["sektor"]]
    for k, v in (i.get("pemberi_kerja") or {}).items():
        er["permanent_headcount_end_2026" if k == "jumlah_pegawai_tetap_31_desember_2026" else k] = v
    er.update(extra_employer or {})
    periods = []
    last = None
    months = stated if final_stated else list(range(stated[0], 13))
    by_month = {m["bulan"]: m for m in masa}
    for mo in months:
        m = by_month.get(mo, last)
        last = m
        comp = m["komponen"]
        unknown = [k for k in comp if k not in INCOME and k != "zakat"]
        if unknown:
            raise ValueError(f"{ex['id']}: unmapped components {unknown}")
        periods.append({"month": mo, "income": {INCOME[k]: v for k, v in comp.items() if k in INCOME and v},
                        "benefits": {}, "zakat": comp.get("zakat", 0) or 0,
                        "hr": {PERIOD_HR[k]: v for k, v in m.items() if k in PERIOD_HR}})
        extra = [k for k in m if k not in ("bulan", "komponen") and k not in PERIOD_HR]
        if extra:
            raise ValueError(f"{ex['id']}: unmapped period fields {extra}")
    meth = method or i["metode"]
    case = {"case_id": ex["id"], "tax_year": i["tahun_pajak"], "employee": emp, "employer": er, "method": meth,
            "employment": {"start_month": months[0], "end_month": months[-1]}, "periods": periods}
    return case, set(stated)


def expected(block, period_extra=None, year_extra=None):
    """Observations stated in keluaran_diharapkan (or keluaran_menurut_aturan_2026). Keys:
    ("period", month, fact), ("year", fact), or ("unmapped", month|0, name) for values with no fact."""
    out = {}
    for m in block.get("per_masa", []):
        for k, v in m.items():
            if k == "bulan":
                continue
            f = PERIOD.get(k) or (period_extra or {}).get(k)
            if isinstance(f, dict):            # nested dict of components -> facts
                for kk, vv in v.items():
                    ff = f.get(kk)
                    out[("period", m["bulan"], ff) if ff else ("unmapped", m["bulan"], f"{k}.{kk}")] = vv
                continue
            out[("period", m["bulan"], f) if f else ("unmapped", m["bulan"], k)] = v
    year = dict(block.get("setahun") or {})
    if "pph21_setahun" in block:
        year["pph21_setahun"] = block["pph21_setahun"]
    for k, v in year.items():
        f = YEAR.get(k) or (year_extra or {}).get(k)
        out[("year", f) if f else ("unmapped", 0, k)] = v
    for k, v in block.items():
        if k not in ("per_masa", "setahun", "pph21_setahun"):
            out[("unmapped", 0, k)] = v
    return out
