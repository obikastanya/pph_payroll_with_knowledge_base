"""Build the E1 Deltas (one per unseen change U01-U16, plus the convention Delta KONVENSI).

Usage: python deltas.py [U01 U02 ...]   (writes ../delta/<id>.json; no argument = all)

Every element cites the change text itself (document UNSEEN-Uxx); G2 does not apply (no locked text).
"""
import copy
import csv
import json
import re
import sys
from datetime import date
from fractions import Fraction

from common import REPO, OUT, SEALED, base_at

GOLD = REPO / "dataset" / "12_emas"
DOCS = {}          # uid -> (title, issued)


# ---------------------------------------------------------------------- helpers
def S(uid, provision, quote):
    return {"document": f"UNSEEN-{uid}", "provision": provision, "quote": quote}


def fact(fid, ftype, scope, src, label=""):
    return {"kind": "fact", "id": fid, "fact_type": ftype, "fact_scope": scope, "output": False, "label": label,
            "source": src}


def rule(rid, produces, expr, src, scope="period", cond=None, vf="2027-01-01", vu=None, ov=None, fp=None,
         modality="mandatory", layer="regulation", policy=None, label=""):
    e = {"kind": "rule", "id": rid, "layer": layer, "modality": modality, "scope": scope, "produces": produces,
         "expression": expr, "valid_from": vf, "source": src}
    if cond:
        e["condition"] = cond
    if vu:
        e["valid_until"] = vu
    if ov:
        e["overrides"] = list(ov)
    if fp:
        e["fixed_point"] = {"lower": fp[0], "upper": fp[1]}
    if policy:
        e["policy"] = policy
    if label:
        e["label"] = label
    return e


def param(pid, name, value, vtype, src, vf="2027-01-01", vu=None, label=""):
    e = {"kind": "parameter", "id": pid, "name": name, "value": value, "value_type": vtype, "valid_from": vf,
         "source": src}
    if vu:
        e["valid_until"] = vu
    if label:
        e["label"] = label
    return e


def table(tid, name, kind, rows, src, vf="2027-01-01", vu=None, label=""):
    e = {"kind": "table", "id": tid, "name": name, "table_kind": kind, "rows": rows, "valid_from": vf, "source": src}
    if vu:
        e["valid_until"] = vu
    if label:
        e["label"] = label
    return e


def gold_element(eid):
    """Latest add/change of an element in the gold chain (its full JSON), for a change operation."""
    found = None
    with open(GOLD / "rantai.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            d = json.loads((GOLD / row["file"]).read_text(encoding="utf-8"))
            for op in ("add", "change"):
                for e in d[op]:
                    if e["id"] == eid:
                        found = copy.deepcopy(e)
    if found is None:
        raise KeyError(eid)
    found.pop("recorded_on", None)
    return found


def dec_text(v):
    f = Fraction(v)
    if f.denominator == 1:
        return str(f.numerator)
    k = 0
    while (f * 10 ** k).denominator != 1:
        k += 1
        if k > 12:
            raise ValueError(f"not a terminating decimal: {f}")
    n = (f * 10 ** k).numerator
    s = str(abs(n)).rjust(k + 1, "0")
    return ("-" if n < 0 else "") + s[:-k] + "." + s[-k:]


_BASE_VIEW = None


def base_view():
    global _BASE_VIEW
    if _BASE_VIEW is None:
        _BASE_VIEW = base_at("2026-10-28").view(date(2026, 10, 28))
    return _BASE_VIEW


def base_table_rows(name, tid):
    rec = [t for t in base_view().tables[name] if t.id == tid][0]
    out = []
    for r in rec.rows:
        r2 = dict(r)
        if rec.table_kind == "bracket":
            r2["value"] = dec_text(r["value"])
        out.append(r2)
    return out


_MONEY = r"Rp([0-9.]+)"


def parse_ter_annex(text, key):
    """Rows of a TER annex table written as '| n | 0 s.d. RpX | r% |', '| n | di atas RpX s.d. RpY | r% |',
    '| n | di atas RpX | r% |'."""
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\| *\d+ *\| *(.+?) *\| *([0-9,]+)% *\|$", line.strip())
        if not m:
            continue
        band, rate = m.group(1), m.group(2).replace(",", ".")
        nums = [int(x.replace(".", "")) for x in re.findall(_MONEY, band)]
        if band.startswith("0 s.d."):
            lo, hi = 0, nums[0]
        elif "s.d." in band:
            lo, hi = nums
        else:
            lo, hi = nums[0], None
        value = dec_text(Fraction(rate.replace(".", "")) / (10 ** (len(rate.split(".")[1]) if "." in rate else 0)) / 100)
        rows.append({"key": key, "lower": lo, "upper": hi, "value": value})
    for a, b in zip(rows, rows[1:]):
        assert a["upper"] == b["lower"], (a, b)
    return rows


def finish(uid, title, issued, add, change=(), remove=(), note=""):
    doc = f"UNSEEN-{uid}"
    for e in list(add) + list(change):
        e["recorded_on"] = issued
    for e in remove:
        e["recorded_on"] = issued
    d = {"delta_id": f"E1-{uid}", "event_id": uid, "document": {"id": doc, "title": title, "issued": issued},
         "relevant": True, "add": list(add), "change": list(change), "remove": list(remove), "note": note}
    DOCS[uid] = (title, issued)
    return d


def text(uid):
    return (SEALED / uid / "perubahan.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------- convention of the worked examples
def KONVENSI():
    src = [{"document": "UNSEEN-KONVENSI", "provision": "contoh.json konvensi butir 2",
            "quote": "Hasil TER x bruto dibulatkan ke bawah ke rupiah penuh (asumsi implementasi; PP 58/2023 dan "
                     "PMK 168/2023 tidak mengatur), kecuali perubahan menyatakan lain."}]
    src2 = [{"document": "UNSEEN-KONVENSI", "provision": "contoh.json konvensi butir 8 dan langkah premi",
             "quote": "Ekspresi memakai notasi Python: // adalah pembagian bulat ke bawah; 'x * 225 // 10000' berarti "
                      "2,25% x x dibulatkan ke bawah."}]
    add = [param("PAR.PPH_ROUND_MODE.E1_CONVENTION", "pph_round_mode", "down", "category", src, vf="2026-01-01",
                 label="rounding of monthly PPh 21 as assumed by the worked examples"),
           param("PAR.BPJS_ROUND_MODE.E1_CONVENTION", "bpjs_round_mode", "down", "category", src2, vf="2026-01-01",
                 label="rounding of BPJS premiums as computed by the worked examples (upah * 24 // 10000)")]
    d = finish("KONVENSI", "Konvensi contoh hitungan perubahan tak terlihat (bukan perubahan regulasi)", "2026-01-01",
               add, note="Aligns the 2026 baseline with the convention of every contoh.json: TER x bruto rounded "
                         "down (konvensi butir 2) and BPJS premiums computed with floor division (langkah, e.g. "
                         "'u * 24 // 10000'). Premiums are billed amounts in the cases, so the second parameter only "
                         "matters where a Delta recomputes premiums (U15). Applied before every change Delta; not "
                         "part of any change.")
    d["delta_id"] = "E1-KONVENSI"
    d["event_id"] = None
    return d


# ---------------------------------------------------------------------- U01 PTKP
def U01():
    u, iss = "U01", "2027-03-19"
    s1 = [S(u, "Pasal 1 ayat (1)", "Besarnya Penghasilan Tidak Kena Pajak per tahun disesuaikan menjadi sebagai berikut"),
          S(u, "Pasal 5", "berlaku untuk Tahun Pajak 2027 dan Tahun Pajak berikutnya, terhitung sejak 1 Januari 2027")]
    own, add_ = 60_000_000, 5_400_000
    rows = [{"key": f"TK/{n}", "value": own + n * add_} for n in range(4)] + \
           [{"key": f"K/{n}", "value": own + add_ + n * add_} for n in range(4)]
    old = gold_element("TAB.PTKP.2016")
    old["valid_until"] = "2026-12-31"
    old["source"] = old["source"] + [S(u, "Pasal 4", "Peraturan Menteri Keuangan Nomor 101/PMK.010/2016 tentang "
                                                     "Penyesuaian Besarnya Penghasilan Tidak Kena Pajak dicabut")]
    return finish(u, "PMK 27/2027 (fiktif): penyesuaian besarnya PTKP", iss,
                  [table("TAB.PTKP.2027", "ptkp", "lookup", rows, s1, label="PTKP per status from 2027")],
                  change=[old],
                  note="Retroactive to 1 Jan 2027 (valid_from 2027-01-01, recorded 2027-03-19): queries at omega >= "
                       "issue give the recomputed final period (Pasal 3 ayat (2)); TER is unaffected (Pasal 2).")


# ---------------------------------------------------------------------- U02 job expense cap
def U02():
    u, iss = "U02", "2026-11-23"
    s = [S(u, "Pasal I (Pasal 10 ayat (2))", "paling banyak Rp9.000.000,00 (sembilan juta rupiah) setahun atau paling "
                                             "banyak Rp750.000,00 (tujuh ratus lima puluh ribu rupiah) sebulan"),
         S(u, "Pasal II ayat (1)", "mulai Tahun Pajak 2027")]
    s2 = s + [S(u, "Pasal II ayat (2)", "biaya jabatan paling banyak sebesar Rp750.000,00 (tujuh ratus lima puluh "
                                        "ribu rupiah) dikalikan dengan jumlah bulan bekerja")]
    return finish(u, "PMK 104/2026 (fiktif): kenaikan batas biaya jabatan", iss, [
        param("PAR.JOB_EXPENSE_MAX_MONTH.2027", "job_expense_max_month", 750_000, "money", s2),
        param("PAR.JOB_EXPENSE_MAX_YEAR.2027", "job_expense_max_year", 9_000_000, "money", s)])


# ---------------------------------------------------------------------- U03 TER category D
def U03():
    u, iss = "U03", "2026-11-02"
    s4 = [S(u, "Pasal I angka 1 (Pasal 2 ayat (4) huruf d)",
            "kategori D diterapkan atas penghasilan bruto bulanan yang diterima atau diperoleh penerima penghasilan "
            "dengan status Penghasilan Tidak Kena Pajak tidak kawin tanpa tanggungan"),
          S(u, "Pasal I angka 1 (Pasal 2 ayat (4) huruf a)", "kategori A diterapkan atas penghasilan bruto bulanan"),
          S(u, "Pasal II ayat (2)", "mulai berlaku pada tanggal 1 Januari 2027 dan diterapkan sejak Masa Pajak "
                                    "Januari 2027")]
    s5 = [S(u, "Pasal I angka 1 (Pasal 2 ayat (5)) dan Lampiran huruf E",
            "tercantum dalam Lampiran huruf A, huruf B, huruf C, dan huruf E"),
          S(u, "Pasal II ayat (1)", "Lampiran huruf A, huruf B, huruf C, dan huruf D Peraturan Pemerintah Nomor 58 "
                                    "Tahun 2023 tidak berubah")]
    cats = {"TK/0": "D", "TK/1": "A", "K/0": "A", "TK/2": "B", "TK/3": "B", "K/1": "B", "K/2": "B", "K/3": "C"}
    annex = text(u).split("LAMPIRAN HURUF E")[1]
    rows = base_table_rows("ter_monthly", "TAB.TER_MONTHLY.2024") + parse_ter_annex(annex, "D")
    return finish(u, "PP 41/2026 (fiktif): kategori D TER untuk TK/0", iss, [
        table("TAB.TER_CATEGORY.2027", "ter_category", "lookup", [{"key": k, "value": v} for k, v in cats.items()],
              s4, label="TER category per PTKP status from 2027"),
        table("TAB.TER_MONTHLY.2027", "ter_monthly", "bracket", rows, s5,
              label="TER A, B, C (unchanged) and D (Lampiran E)")],
        note="A married woman with PTKP for herself only already has effective status TK/0 "
             "(REG.PTKP.STATUS.MARRIED_WOMAN), so she falls into category D through the lookup.")


# ---------------------------------------------------------------------- U04 Tapera
def U04():
    u, iss = "U04", "2026-12-23"
    s2 = [S(u, "Pasal 2 ayat (1)", "Iuran Tapera yang dibayar oleh pemberi kerja untuk kepentingan Pegawai Tetap tidak "
                                   "termasuk penghasilan yang dipotong Pajak Penghasilan Pasal 21"),
          S(u, "Pasal 2 ayat (2)", "berlaku untuk penghitungan pada setiap Masa Pajak, termasuk Masa Pajak Terakhir")]
    s0 = [S(u, "Ringkasan perubahan", "Menurut aturan 2026, iuran ini tidak dikecualikan secara khusus, sehingga "
                                      "dalam contoh diperlakukan sebagai penghasilan.")]
    s3 = [S(u, "Pasal 3 ayat (1)", "Iuran Tapera yang dibayar oleh Pegawai Tetap melalui pemberi kerja merupakan "
                                   "pengurangan yang diperbolehkan dalam penghitungan penghasilan neto pada Masa "
                                   "Pajak Terakhir"),
          S(u, "Pasal 3 ayat (2)", "paling banyak Rp2.400.000,00 (dua juta empat ratus ribu rupiah) setahun atau "
                                   "Rp200.000,00 (dua ratus ribu rupiah) dikalikan dengan jumlah bulan Iuran Tapera "
                                   "dibayar")]
    prem = gold_element("REG.PREMIUMS.TAXABLE")
    prem["expression"] += " + tapera_employer_taxable"
    prem["source"] = prem["source"] + s2
    ded = gold_element("REG.YEAR.DEDUCTIONS")
    ded["expression"] += " + annual_tapera_deduction"
    ded["source"] = ded["source"] + s3
    add = [
        fact("tapera_employer_taxable", "money", "period", s2, "employer Tapera contribution counted as income"),
        fact("tapera_employee_paid", "money", "period", s3, "Tapera contribution paid by the employee"),
        fact("tapera_paid_month", "int", "period", s3, "1 if the employee paid Tapera this month"),
        fact("annual_tapera_deduction", "money", "year", s3, "deductible employee Tapera contribution"),
        param("PAR.TAPERA_DEDUCTION_MAX_MONTH.2027", "tapera_deduction_max_month", 200_000, "money", s3),
        param("PAR.TAPERA_DEDUCTION_MAX_YEAR.2027", "tapera_deduction_max_year", 2_400_000, "money", s3),
        rule("REG.TAPERA.EMPLOYER.DEFAULT", "tapera_employer_taxable", "income('tapera_employer')", s0,
             vf="2009-01-01", modality="default", label="employer Tapera is income unless exempted"),
        rule("REG.TAPERA.EMPLOYER.EXEMPT", "tapera_employer_taxable", "0", s2),
        rule("REG.TAPERA.EMPLOYEE.PAID", "tapera_employee_paid", "income('tapera_employee')", s3),
        rule("REG.TAPERA.EMPLOYEE.MONTH", "tapera_paid_month", "1 if income('tapera_employee') > 0 else 0", s3),
        rule("REG.TAPERA.DEDUCTION.DEFAULT", "annual_tapera_deduction", "0", s3, scope="year", vf="2009-01-01",
             modality="default"),
        rule("REG.TAPERA.DEDUCTION", "annual_tapera_deduction",
             "min(sum_periods('tapera_employee_paid'), param('tapera_deduction_max_month') * "
             "sum_periods('tapera_paid_month'), param('tapera_deduction_max_year'))", s3, scope="year"),
    ]
    return finish(u, "PMK 115/2026 (fiktif): perlakuan PPh atas iuran Tapera", iss, add, change=[prem, ded],
                  note="Employer Tapera enters gross through employer_premiums_taxable (default: income, as the "
                       "examples treat it under 2026 rules; exempt from 2027). Employee Tapera is a new annual "
                       "deduction; it does not touch the TER base (Pasal 3 ayat (3)).")


# ---------------------------------------------------------------------- U05 internet reimbursement
def U05():
    u, iss = "U05", "2026-12-07"
    s7 = [S(u, "Pasal I angka 1 (Pasal 7 huruf i)", "penggantian biaya komunikasi dan internet bagi Pegawai Tetap "
                                                   "yang bekerja jarak jauh"),
          S(u, "Pasal I angka 2 (Pasal 7A ayat (1) huruf b)", "bekerja jarak jauh paling sedikit 8 (delapan) hari kerja"),
          S(u, "Pasal I angka 2 (Pasal 7A ayat (2))", "paling banyak Rp400.000,00 (empat ratus ribu rupiah) untuk "
                                                      "setiap Masa Pajak"),
          S(u, "Pasal I angka 2 (Pasal 7A ayat (3))", "merupakan penghasilan yang bersifat teratur dan termasuk dalam "
                                                      "penghasilan bruto Pegawai Tetap"),
          S(u, "Pasal I angka 2 (Pasal 7A ayat (4))", "Tunjangan komunikasi atau tunjangan internet yang diberikan "
                                                      "dalam jumlah tetap")]
    s0 = [S(u, "Ringkasan perubahan", "Tunjangan internet tunai dengan jumlah tetap (tanpa bukti tagihan) tetap "
                                      "penghasilan penuh.")]
    gr = gold_element("REG.GROSS.REGULAR")
    gr["expression"] += " + internet_taxable"
    gr["source"] = gr["source"] + s7[3:4]
    add = [
        fact("internet_taxable", "money", "period", s7, "taxable part of internet reimbursement and allowance"),
        param("PAR.INTERNET_REIMBURSEMENT_CAP.2027", "internet_reimbursement_cap", 400_000, "money", s7[2:3]),
        param("PAR.REMOTE_WORK_MIN_DAYS.2027", "remote_work_min_days", 8, "int", s7[1:2]),
        rule("REG.INTERNET.TAXABLE.DEFAULT", "internet_taxable",
             "income('internet_reimbursement') + income('internet_allowance')", s0, vf="2009-01-01",
             modality="default", label="before 2027 reimbursement and allowance are regular income"),
        rule("REG.INTERNET.TAXABLE", "internet_taxable",
             "income('internet_allowance') + (max(0, income('internet_reimbursement') - "
             "param('internet_reimbursement_cap')) if hr('remote_work_days') >= param('remote_work_min_days') "
             "else income('internet_reimbursement'))", s7),
    ]
    return finish(u, "PMK 108/2026 (fiktif): penggantian internet kerja jarak jauh", iss, add, change=[gr],
                  note="Case data: income.internet_reimbursement (bill-based), income.internet_allowance (fixed cash), "
                       "hr.remote_work_days.")


# ---------------------------------------------------------------------- U06 DTP young new employees
def U06():
    u, iss = "U06", "2027-03-01"
    s3 = [S(u, "Pasal 3 huruf a", "mulai bekerja pada pemberi kerja paling cepat tanggal 1 Januari 2027"),
          S(u, "Pasal 3 huruf b", "berusia paling tinggi 30 (tiga puluh) tahun pada tanggal mulai bekerja"),
          S(u, "Pasal 3 huruf c", "Nomor Induk Kependudukan yang telah terintegrasi dengan sistem administrasi "
                                  "Direktorat Jenderal Pajak"),
          S(u, "Pasal 3 huruf d", "tidak lebih dari Rp9.000.000,00 (sembilan juta rupiah) pada Masa Pajak bulan "
                                  "pertama bekerja"),
          S(u, "Pasal 3 huruf e", "tidak menerima insentif Pajak Penghasilan Pasal 21 ditanggung pemerintah lainnya")]
    s5 = [S(u, "Pasal 5 ayat (1)", "berupa gaji dan tunjangan yang bersifat tetap dan teratur setiap bulan"),
          S(u, "Pasal 5 ayat (2)", "hanya diuji pada Masa Pajak bulan pertama bekerja")]
    s4 = [S(u, "Pasal 4 ayat (1)", "jumlah Pegawai Tetap pada akhir bulan Masa Pajak tersebut lebih banyak daripada "
                                   "jumlah Pegawai Tetap pada tanggal 31 Desember 2026")]
    s2 = [S(u, "Pasal 2 ayat (2)", "diberikan untuk Masa Pajak Maret 2027 sampai dengan Masa Pajak Desember 2027"),
          S(u, "Pasal 6 ayat (1)", "PPh 21 DTP untuk setiap Masa Pajak sebesar Pajak Penghasilan Pasal 21 yang "
                                   "terutang pada Masa Pajak tersebut")]
    s6 = [S(u, "Pasal 6 ayat (4)", "dikembalikan kepada Pegawai Baru paling banyak sebesar Pajak Penghasilan Pasal 21 "
                                   "yang benar-benar dipotong dari Pegawai Baru dalam Tahun Pajak 2027"),
          S(u, "Pasal 6 ayat (4)", "Sisa kelebihan yang berasal dari PPh 21 DTP tidak dikembalikan.")]
    vf, vu = "2027-03-01", "2027-12-31"
    age = ("employee('start_year') - employee('birth_year') - (1 if employee('start_month') * 100 + "
           "employee('start_day') < employee('birth_month') * 100 + employee('birth_day') else 0)")
    elig = ("employee('start_date') != None and employee('start_date') >= '2027-01-01' and "
            "employee('birth_year') != None and young_dtp_age <= param('young_dtp_age_max') and "
            "employee('tax_id_integrated') == True and "
            "value_in('young_dtp_fixed_income', first_month) <= param('young_dtp_fixed_income_cap') and "
            "employee('other_dtp_incentive') != True")
    add = [
        fact("young_dtp_age", "int", "year", s3[1:2], "age in full years on the start date"),
        fact("young_dtp_fixed_income", "money", "period", s5, "fixed regular salary and allowances"),
        fact("young_dtp_eligible", "bool", "year", s3, "employee meets the young new employee DTP criteria"),
        fact("young_dtp_facility", "bool", "period", s4, "young new employee DTP applies this month"),
        fact("dtp_excess_not_refunded", "money", "year", s6, "overpayment from DTP that is not refunded"),
        param("PAR.YOUNG_DTP_AGE_MAX.2027", "young_dtp_age_max", 30, "int", s3[1:2], vf=vf, vu=vu),
        param("PAR.YOUNG_DTP_FIXED_INCOME_CAP.2027", "young_dtp_fixed_income_cap", 9_000_000, "money", s3[3:4],
              vf="2027-01-01", vu=vu),
        rule("REG.YOUNG_DTP.AGE", "young_dtp_age", age, s3[1:2], scope="year", vf=vf, vu=vu),
        rule("REG.YOUNG_DTP.FIXED_INCOME", "young_dtp_fixed_income", "base_salary + fixed_allowance", s5,
             vf="2027-01-01", vu=vu),
        rule("REG.YOUNG_DTP.ELIGIBLE", "young_dtp_eligible", elig, s3 + s5[1:], scope="year", vf=vf, vu=vu),
        rule("REG.YOUNG_DTP.FACILITY", "young_dtp_facility",
             "young_dtp_eligible and employer('permanent_headcount_end_2026') != None and "
             "hr('permanent_headcount') > employer('permanent_headcount_end_2026')", s4, vf=vf, vu=vu),
        rule("REG.YOUNG_DTP.RUNNING", "pph21_dtp", "pph21_due if young_dtp_facility else 0", s2,
             cond="not is_final_period", vf=vf, vu=vu),
        rule("REG.YOUNG_DTP.FINAL", "pph21_dtp", "max(0, pph21_due) if young_dtp_facility else 0", s2,
             cond="is_final_period", vf=vf, vu=vu),
        rule("REG.YOUNG_DTP.REFUND", "refund_to_employee",
             "min(max(0, 0 - final_period_tax), max(0, sum_periods_before_final('pph21_due') - "
             "sum_periods_before_final('pph21_dtp')))", s6, scope="year", cond="young_dtp_eligible", vf=vf, vu=vu,
             ov=["REG.YEAR.REFUND"]),
        rule("REG.YOUNG_DTP.EXCESS", "dtp_excess_not_refunded", "max(0, 0 - final_period_tax) - refund_to_employee",
             s6, scope="year", vf=vf, vu=vu),
    ]
    return finish(u, "PMK 19/2027 (fiktif): PPh 21 DTP pegawai baru usia muda", iss, add,
                  note="Case data: employee.start_date/start_year/start_month/start_day, birth_*, tax_id_integrated, "
                       "other_dtp_incentive; employer.permanent_headcount_end_2026; hr.permanent_headcount per month. "
                       "'Never before a permanent employee of the same employer' (Pasal 1 angka 1) has no case "
                       "attribute and is assumed true.")


# ---------------------------------------------------------------------- U07 extension of PMK 105/2025 DTP
def U07():
    u, iss = "U07", "2027-02-09"
    s2 = [S(u, "Pasal I angka 1 (Pasal 2 ayat (4))", "juga diberikan atas penghasilan bruto dalam tahun 2027 untuk "
                                                     "Masa Pajak Januari 2027 sampai dengan Masa Pajak Juni 2027"),
          S(u, "Pasal II", "berlaku surut sejak Masa Pajak Januari 2027")]
    s4a = [S(u, "Pasal I angka 2 (Pasal 4A ayat (1) huruf a)", "kode yang tercantum pada basis data administrasi "
                                                               "perpajakan pada tanggal 1 Januari 2027"),
           S(u, "Pasal I angka 2 (Pasal 4A ayat (1) huruf b)", "diuji pada Masa Pajak Januari 2027 untuk Pegawai Tetap "
                                                               "yang mulai bekerja sebelum Januari 2027, atau pada "
                                                               "Masa Pajak bulan pertama bekerja"),
           S(u, "Pasal I angka 2 (Pasal 4A ayat (1) huruf c)", "kriteria lain sebagaimana dimaksud dalam Pasal 3 dan "
                                                               "Pasal 4 tetap berlaku, termasuk Lampiran huruf A")]
    s5a = [S(u, "Pasal I angka 3 (Pasal 5 ayat (5a))", "kelebihan dikembalikan kepada Pegawai Tetap paling banyak "
                                                       "sebesar Pajak Penghasilan Pasal 21 yang benar-benar dipotong "
                                                       "dari Pegawai Tetap dalam Tahun Pajak 2027")]
    vf, vu = "2027-01-01", "2027-06-30"
    old = {e: gold_element(e) for e in ("REG.DTP.ELIGIBLE", "REG.DTP.INCOME_TEST", "REG.DTP.FIXED_INCOME",
                                        "REG.DTP.FACILITY", "REG.DTP.RUNNING", "REG.DTP.FINAL", "REG.DTP.NO_GROSSUP",
                                        "REG.DTP.THP_CASH")}

    def ext(eid, src, until=vu):
        e = old[eid]
        r = rule(eid + ".2027", e["produces"], e["expression"], src, scope=e["scope"], cond=e.get("condition"),
                 vf=vf, vu=until, ov=[o + ".2027" if o.startswith("REG.DTP.") else o for o in e.get("overrides", [])]
                 or None, label=(e.get("label") or "") + " (2027 extension)")
        return r

    klu = base_table_rows("dtp_klu", "TAB.DTP_KLU.2026")
    add = [
        table("TAB.DTP_KLU.2027", "dtp_klu", "set", klu, s4a, vf=vf, vu=vu, label="KLU of PMK 105/2025 Lampiran A"),
        param("PAR.DTP_FIXED_INCOME_CAP.2027", "dtp_fixed_income_cap", 10_000_000, "money", s4a[1:2], vf=vf, vu=vu),
        ext("REG.DTP.ELIGIBLE", s2 + s4a),
        ext("REG.DTP.INCOME_TEST", s4a[1:2]),
        ext("REG.DTP.FIXED_INCOME", s4a[1:2], until="2027-12-31"),
        ext("REG.DTP.FACILITY", s2),
        ext("REG.DTP.RUNNING", s2),
        ext("REG.DTP.FINAL", s2 + s5a),
        ext("REG.DTP.NO_GROSSUP", s2),
        ext("REG.DTP.THP_CASH", s2),
        rule("REG.DTP.REFUND.2027", "refund_to_employee",
             "min(max(0, 0 - final_period_tax), max(0, sum_periods_before_final('pph21_due') - "
             "sum_periods_before_final('pph21_dtp')))", s5a, scope="year", cond="dtp_eligible", vf=vf,
             vu="2027-12-31", ov=["REG.YEAR.REFUND"]),
    ]
    return finish(u, "PMK 12/2027 (fiktif): perpanjangan PPh 21 DTP PMK 105/2025 sampai Juni 2027", iss, add,
                  note="2027 copies of the PMK 105/2025 DTP rules (same expressions) valid Jan-Jun 2027; KLU table "
                       "copied unchanged; refund for 2027 capped at tax actually withheld (Pasal 5 ayat (5a)).")


# ---------------------------------------------------------------------- U08 married woman dependants
def U08():
    u, iss = "U08", "2026-12-16"
    s = [S(u, "Pasal I (Pasal 9 ayat (2) huruf a)", "sebesar Penghasilan Tidak Kena Pajak untuk dirinya sendiri, "
                                                    "ditambah Penghasilan Tidak Kena Pajak untuk anggota keluarga "
                                                    "sedarah"),
         S(u, "Pasal I (Pasal 9 ayat (2a))", "Surat pernyataan disampaikan kepada pemberi kerja paling lambat pada awal "
                                             "tahun kalender"),
         S(u, "Pasal I (Pasal 9 ayat (2b))", "ditentukan sesuai dengan status tidak kawin dengan jumlah tanggungan "
                                             "yang sama")]
    rows = [{"key": f"K/{n}", "value": f"TK/{n}"} for n in range(4)]
    return finish(u, "PMK 112/2026 (fiktif): PTKP tanggungan karyawati kawin", iss, [
        table("TAB.PTKP_STATUS_MARRIED_WOMAN_DEPENDANTS.2027", "ptkp_status_married_woman_dependants", "lookup",
              rows, s, label="status K/n treated as TK/n"),
        rule("REG.PTKP.STATUS.MARRIED_WOMAN.DEPENDANTS", "ptkp_status_effective",
             "lookup('ptkp_status_married_woman_dependants', ptkp_status_input)", s, scope="year",
             cond="employee('sex') == 'F' and startswith(ptkp_status_input, 'K/') and not "
                  "employee('husband_no_income_certified') and employee('dependants_statement') == True",
             ov=["REG.PTKP.STATUS.MARRIED_WOMAN", "REG.PTKP.STATUS"])],
        note="Case data: employee.dependants_statement. PTKP and TER category both follow the effective status TK/n.")


# ---------------------------------------------------------------------- U09 irregular income method
def U09():
    u, iss = "U09", "2026-12-29"
    pp = [S(u, "Dokumen 1, Pasal I (PP 58/2023 Pasal 2 ayat (2a))",
            "tarif efektif bulanan sebagaimana dimaksud pada ayat (2) huruf a diterapkan atas penghasilan bruto yang "
            "bersifat teratur dalam 1 (satu) Masa Pajak")]
    p2 = [S(u, "Dokumen 2, Pasal 2", "tarif efektif bulanan sesuai kategori Pegawai Tetap dikalikan penghasilan bruto "
                                     "teratur Masa Pajak tersebut")]
    p3 = [S(u, "Dokumen 2, Pasal 3 ayat (1)", "dihitung dari penghasilan bruto teratur Masa Pajak tersebut dikalikan "
                                              "12 (dua belas) ditambah seluruh penghasilan tidak teratur"),
          S(u, "Dokumen 2, Pasal 3 ayat (2)", "mengurangkan biaya jabatan sebesar 5% (lima persen) dari penghasilan "
                                              "bruto yang bersangkutan, paling banyak Rp6.000.000,00"),
          S(u, "Dokumen 2, Pasal 3 ayat (2) huruf d", "membulatkan hasilnya ke bawah hingga ribuan rupiah penuh")]
    c = "not is_final_period and irregular_gross > 0"

    def pkp(gross):
        return (f"max(0, round({gross} - min(round(param('job_expense_rate') * ({gross}), 1, 'down'), "
                f"param('job_expense_max_year')) - 12 * employee_pension_contributions - ptkp_amount, 1000, 'down'))")
    add = [
        rule("REG.TER.RATE.REGULAR_ONLY", "ter_rate", "bracket('ter_monthly', ter_category, regular_gross)", pp + p2,
             cond=c, ov=["REG.TER.RATE"]),
        rule("REG.TER.RUNNING.IRREGULAR", "pph21_running",
             "round(ter_rate * regular_gross, 1, param('pph_round_mode')) + pph_irregular_month", pp + p2, cond=c,
             ov=["REG.TER.RUNNING"]),
        rule("REG.IRREGULAR.TAXABLE_WITH", "taxable_with_irregular", pkp("12 * regular_gross + irregular_gross"),
             p3, cond=c),
        rule("REG.IRREGULAR.TAXABLE_WITHOUT", "taxable_without_irregular", pkp("12 * regular_gross"), p3, cond=c),
        rule("REG.IRREGULAR.PPH", "pph_irregular_month",
             "round(progressive('pasal17', taxable_with_irregular), 1, 'down') - "
             "round(progressive('pasal17', taxable_without_irregular), 1, 'down')", p3, cond=c),
    ]
    return finish(u, "PP 52/2026 dan PMK 118/2026 (fiktif): metode penghasilan tidak teratur", iss, add,
                  note="Two documents (PP sets the principle, PMK the formula); one Delta cites both and is recorded "
                       "on the PMK date, because the computation needs both. Reuses the facts taxable_with_irregular, "
                       "taxable_without_irregular, pph_irregular_month of the PER-16 method.")


# ---------------------------------------------------------------------- U10 zakat
def U10():
    u, iss = "U10", "2026-12-11"
    s = [S(u, "Pasal I angka 1 (Pasal 10 ayat (1) huruf c)", "c. dihapus."),
         S(u, "Pasal II ayat (3)", "berlaku untuk penghitungan Masa Pajak Terakhir Tahun Pajak 2027 dan seterusnya")]
    z = gold_element("REG.ZAKAT.DEDUCTIBLE")
    z["valid_until"] = "2026-12-31"
    z["source"] = z["source"] + s
    return finish(u, "PMK 110/2026 (fiktif): penghapusan zakat sebagai pengurang", iss, [], change=[z],
                  note="Repeal as a change that closes the validity (representasi.md 2); from 2027 the default "
                       "REG.DEFAULT.ZAKAT_DEDUCTIBLE (0) applies.")


# ---------------------------------------------------------------------- U11 rounding of the TER base
def U11():
    u, iss = "U11", "2026-12-24"
    s1 = [S(u, "Pasal I (Pasal 15A ayat (1))", "dibulatkan ke bawah hingga ribuan rupiah penuh. Penentuan lapisan "
                                               "tarif efektif bulanan didasarkan pada penghasilan bruto yang telah "
                                               "dibulatkan")]
    s2 = [S(u, "Pasal I (Pasal 15A ayat (2))", "dengan dasar pengenaan sebagaimana dimaksud pada ayat (1) dibulatkan "
                                               "ke bawah hingga rupiah penuh")]
    c = "not is_final_period"
    return finish(u, "PMK 116/2026 (fiktif): pembulatan dasar TER ke ribuan", iss, [
        fact("ter_base", "money", "period", s1, "monthly TER base rounded down to thousands"),
        rule("REG.TER.BASE", "ter_base", "round(gross_income, 1000, 'down')", s1, cond=c),
        rule("REG.TER.RATE.ROUNDED_BASE", "ter_rate", "bracket('ter_monthly', ter_category, ter_base)", s1, cond=c,
             ov=["REG.TER.RATE"]),
        rule("REG.TER.RUNNING.ROUNDED_BASE", "pph21_running", "round(ter_rate * ter_base, 1, 'down')", s1 + s2,
             cond=c, ov=["REG.TER.RUNNING"])],
        note="Annual gross at the final period keeps the actual amounts (Pasal 15A ayat (3)): only TER rules change.")


# ---------------------------------------------------------------------- U12 partial first month
def U12():
    u, iss = "U12", "2026-12-30"
    s1 = [S(u, "Pasal I (Pasal 15B ayat (1))", "tarif efektif bulanan untuk Masa Pajak bulan pertama bekerja "
                                               "ditentukan berdasarkan penghasilan bruto setara sebulan penuh"),
          S(u, "Pasal II", "berlaku bagi Pegawai Tetap yang mulai bekerja sejak tanggal 1 Januari 2027")]
    s2 = [S(u, "Pasal I (Pasal 15B ayat (2))", "jumlah hari kalender sejak tanggal mulai bekerja sampai dengan akhir "
                                               "bulan, termasuk tanggal mulai bekerja"),
          S(u, "Pasal I (Pasal 15B ayat (2))", "dengan hasil bagi dibulatkan ke bawah hingga rupiah penuh")]
    s3 = [S(u, "Pasal I (Pasal 15B ayat (3))", "dikalikan dengan penghasilan bruto sebenarnya"),
          S(u, "Pasal I (Pasal 15B ayat (4))", "tidak berlaku dalam hal Masa Pajak bulan pertama bekerja juga "
                                               "merupakan Masa Pajak Terakhir")]
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    leap = ("month == 2 and tax_year / 4 == round(tax_year / 4, 1, 'down') and (tax_year / 100 != "
            "round(tax_year / 100, 1, 'down') or tax_year / 400 == round(tax_year / 400, 1, 'down'))")
    return finish(u, "PMK 120/2026 (fiktif): tarif bulan pertama dari bruto setara", iss, [
        fact("days_in_month", "int", "period", s2, "calendar days of the month"),
        fact("partial_first_month", "bool", "period", s1, "first month of an employee who started after day 1"),
        fact("ter_equivalent_gross", "money", "period", s2, "gross equivalent to a full month"),
        table("TAB.DAYS_IN_MONTH", "days_in_month", "lookup",
              [{"key": str(m), "value": d} for m, d in enumerate(days, 1)], s2, label="days per month (non-leap)"),
        rule("REG.CAL.DAYS_IN_MONTH", "days_in_month", f"29 if ({leap}) else lookup('days_in_month', month)", s2),
        rule("REG.TER.PARTIAL_FIRST_MONTH", "partial_first_month",
             "employee('start_date') != None and employee('start_date') >= '2027-01-01' and "
             "employee('start_year') == tax_year and employee('start_month') == month and employee('start_day') > 1",
             s1),
        rule("REG.TER.EQUIVALENT_GROSS", "ter_equivalent_gross",
             "round(regular_gross * days_in_month / (days_in_month - employee('start_day') + 1), 1, 'down') + "
             "irregular_gross", s2, cond="partial_first_month"),
        rule("REG.TER.RATE.PARTIAL_FIRST_MONTH", "ter_rate",
             "bracket('ter_monthly', ter_category, ter_equivalent_gross)", s1 + s3,
             cond="not is_final_period and partial_first_month", ov=["REG.TER.RATE"])],
        note="Case data: employee.start_date and its parts (the expression language has no date arithmetic).")


# ---------------------------------------------------------------------- U13 proportional PTKP
def U13():
    u, iss = "U13", "2026-11-30"
    s = [S(u, "Pasal I (Pasal 15 ayat (2a))", "sebesar Penghasilan Tidak Kena Pajak setahun dikalikan jumlah bulan "
                                              "bekerja pada pemberi kerja tersebut dibagi 12 (dua belas), dibulatkan "
                                              "ke bawah hingga rupiah penuh"),
         S(u, "Pasal II ayat (1)", "tidak berlaku bagi Pegawai Tetap yang kewajiban pajak subjektifnya dimulai setelah "
                                   "bulan Januari atau berakhir sebelum bulan Desember"),
         S(u, "Pasal II ayat (2)", "Bagian bulan bekerja dihitung sebagai 1 (satu) bulan penuh.")]
    return finish(u, "PMK 106/2026 (fiktif): PTKP proporsional di Masa Pajak Terakhir", iss, [
        rule("REG.PTKP.AMOUNT.PART_YEAR_EMPLOYMENT", "ptkp_amount",
             "round(lookup('ptkp', ptkp_status_effective) * months_employed / 12, 1, 'down')", s, scope="year",
             cond="months_employed < 12 and subjective_months >= 12 and employee('subjective_change_mid_year') != True",
             ov=["REG.PTKP.AMOUNT"])],
        note="months_employed counts the employment months of the case (a part month counts as a month).")


# ---------------------------------------------------------------------- U14 company gross-up for grades I-III
def U14():
    u, iss = "U14", "2026-12-14"
    pol = f"UNSEEN-{u}"
    s1 = [S(u, "Pasal 1 ayat (1)", "Pegawai tetap golongan I, golongan II, dan golongan III diberikan tunjangan Pajak "
                                   "Penghasilan Pasal 21 setiap bulan"),
          S(u, "Pasal 1 ayat (2)", "Pegawai tetap golongan IV dan golongan di atasnya tidak diberikan tunjangan Pajak "
                                   "Penghasilan Pasal 21"),
          S(u, "Pasal 5", "berlaku sejak pembayaran gaji Masa Pajak Januari 2027")]
    s4 = [S(u, "Pasal 4 ayat (4)", "kelebihan tersebut menjadi hak perusahaan dan tidak dibayarkan kepada pegawai")]
    return finish(u, "SK Direksi PT Fiktif Maju Bersama 014/SK-DIR/XII/2026: tunjangan PPh 21 golongan I-III", iss, [
        fact("excess_retained_by_company", "money", "year", s4, "final-period overpayment kept by the company"),
        rule("PRS.U14.METHOD", "withholding_method",
             "'gross_up' if employee('grade') in ('I', 'II', 'III') else case('method')", s1, scope="year",
             modality="default", layer="company", policy=pol),
        rule("PRS.U14.TAX_BURDEN.FINAL", "employee_tax_burden", "0", s4,
             cond="withholding_method == 'gross_up' and is_final_period and pph21_due < 0", modality="default",
             layer="company", policy=pol),
        rule("PRS.U14.EXCESS", "excess_retained_by_company",
             "max(0, 0 - final_period_tax) if withholding_method == 'gross_up' else 0", s4, scope="year",
             modality="default", layer="company", policy=pol)],
        note="The gross-up itself (T = TER(B+T) x (B+T), least fixed point from 0; final period max(0, ...)) is the "
             "existing REG.GROSSUP.* of the knowledge base. Grade is taken from the case for the whole year.")


# ---------------------------------------------------------------------- U15 PKB raise with back pay
def U15():
    u, iss = "U15", "2027-04-12"
    pol = f"UNSEEN-{u}"
    s5 = [S(u, "Pasal 5 ayat (1)", "Gaji pokok setiap pegawai tetap dinaikkan sebesar 8% (delapan persen) dari gaji "
                                   "pokok yang berlaku pada tanggal 31 Desember 2026. Gaji pokok baru hasil kenaikan "
                                   "dibulatkan ke atas hingga ribuan rupiah penuh."),
          S(u, "Pasal 5 ayat (2)", "dihitung dari gaji pokok pada saat mulai bekerja dan berlaku sejak bulan mulai "
                                   "bekerja")]
    s6 = [S(u, "Pasal 6 ayat (2)", "dibayarkan sekaligus sebagai rapel bersamaan dengan gaji bulan April 2027"),
          S(u, "Pasal 6 ayat (3)", "Gaji bulan April 2027 dan seterusnya dibayarkan dengan gaji pokok baru."),
          S(u, "Pasal 6 ayat (4)", "dengan memperhatikan batas upah yang berlaku bagi setiap program")]
    s7 = [S(u, "Pasal 7", "Rapel gaji dan rapel iuran bagian perusahaan sebagaimana dimaksud dalam Pasal 6 merupakan "
                          "penghasilan Masa Pajak April 2027")]
    s8 = [S(u, "Pasal 8", "berlaku sejak tanggal 1 Januari 2027 sampai dengan tanggal 31 Desember 2028")]
    vf, vu, apr = "2027-04-01", "2028-12-31", "2027-04-30"
    m = "param('bpjs_round_mode')"

    def r(rid, produces, expr, src, scope="period", cond="employee('old_base_salary') != None", v0=vf, v1=vu):
        return rule(rid, produces, expr, src, scope=scope, cond=cond, vf=v0, vu=v1, modality="default",
                    layer="company", policy=pol)

    def back(rate_expr, new_wage, old_wage):
        return (f"back_pay_months * (round({rate_expr} * {new_wage}, 1, {m}) - "
                f"round({rate_expr} * {old_wage}, 1, {m}))")
    old_w = "old_bpjs_wage"
    add = [
        fact("pkb_new_base_salary", "money", "year", s5, "base salary after the 8% raise"),
        fact("back_pay_months", "int", "year", s6, "months of 2027 before April with the raise"),
        fact("old_bpjs_wage", "money", "period", s6, "wage before the raise"),
        fact("back_pay", "money", "period", s6, "back pay of base salary paid in April 2027"),
        fact("jkk_back_premium", "money", "period", s6, "back JKK premium paid in April 2027"),
        fact("jkm_back_premium", "money", "period", s6, "back JKM premium paid in April 2027"),
        fact("health_back_premium", "money", "period", s6, "back JKN employer premium paid in April 2027"),
        r("PRS.U15.NEW_BASE_SALARY", "pkb_new_base_salary",
          "round(employee('old_base_salary') * 108 / 100, 1000, 'up')", s5, scope="year", v0="2027-01-01"),
        r("PRS.U15.BACK_PAY_MONTHS", "back_pay_months", "max(0, 4 - first_month)", s5 + s6, scope="year",
          v0="2027-01-01"),
        r("PRS.U15.BASE_SALARY", "base_salary", "pkb_new_base_salary", s6 + s8),
        r("PRS.U15.OLD_WAGE", "old_bpjs_wage", "employee('old_base_salary') + fixed_allowance", s6),
        r("PRS.U15.BACK_PAY", "back_pay", "(pkb_new_base_salary - employee('old_base_salary')) * back_pay_months",
          s6, v1=apr),
        r("PRS.U15.BACK_JKK", "jkk_back_premium", back("jkk_rate", "bpjs_wage", old_w), s6, v1=apr),
        r("PRS.U15.BACK_JKM", "jkm_back_premium", back("param('jkm_rate')", "bpjs_wage", old_w), s6, v1=apr),
        r("PRS.U15.BACK_JKN", "health_back_premium",
          back("param('health_employer_rate')", "health_wage", f"min({old_w}, param('health_wage_cap'))"), s6, v1=apr),
        r("PRS.U15.OTHER_IRREGULAR", "other_irregular_income",
          "income('other_irregular') + back_pay + jkk_back_premium + jkm_back_premium + health_back_premium", s7,
          v1=apr),
        r("PRS.U15.JKK", "jkk_premium", f"round(jkk_rate * bpjs_wage, 1, {m})", s6),
        r("PRS.U15.JKM", "jkm_premium", f"round(param('jkm_rate') * bpjs_wage, 1, {m})", s6),
        r("PRS.U15.JKN", "health_premium_employer", f"round(param('health_employer_rate') * health_wage, 1, {m})", s6),
        r("PRS.U15.JHT", "jht_employee",
          f"round(param('jht_employee_rate') * bpjs_wage, 1, {m}) + (" +
          back("param('jht_employee_rate')", "bpjs_wage", old_w) + " if month == 4 and tax_year == 2027 else 0)", s6),
        r("PRS.U15.JP", "jp_employee",
          f"round(param('jp_employee_rate') * jp_wage, 1, {m}) + (" +
          back("param('jp_employee_rate')", "jp_wage", f"min({old_w}, param('jp_wage_cap'))") +
          " if month == 4 and tax_year == 2027 else 0)", s6),
    ]
    return finish(u, "PKB PT Fiktif Maju Bersama 2027-2028: kenaikan gaji 8% berlaku surut dengan rapel", iss, add,
                  note="Company layer (policy UNSEEN-U15). The case keeps the payroll as it was before the PKB "
                       "(old salary, premiums as billed); the policy recomputes base salary and BPJS amounts from "
                       "April 2027 with the regulation's rates and caps, and pays the back amounts in April as "
                       "irregular income. JHT/JP back contributions are deducted in April.")


# ---------------------------------------------------------------------- U16 wider 0% band of TER A/B/C
def U16():
    u, iss = "U16", "2026-12-17"
    s = [S(u, "Pasal I", "Ketentuan Lampiran huruf A, huruf B, dan huruf C Peraturan Pemerintah Nomor 58 Tahun 2023 "
                         "diubah sehingga menjadi sebagaimana tercantum dalam Lampiran"),
         S(u, "Pasal II ayat (2)", "mulai berlaku pada tanggal 1 Januari 2027 dan diterapkan sejak Masa Pajak Januari "
                                   "2027")]
    t = text(u)
    parts = re.split(r"\*\*LAMPIRAN HURUF ([ABC]) ", t)
    rows = []
    for i in range(1, len(parts), 2):
        key, body = parts[i], parts[i + 1].split("Ringkasan perubahan")[0]
        rows += parse_ter_annex(body, key)
    return finish(u, "PP 47/2026 (fiktif): perluasan lapisan 0% TER A/B/C", iss, [
        table("TAB.TER_MONTHLY.2027", "ter_monthly", "bracket", rows, s, label="TER A, B, C from 2027")])


ALL = ["KONVENSI"] + [f"U{i:02d}" for i in range(1, 17)]


def build(uid):
    d = globals()[uid]()
    (OUT / "delta").mkdir(exist_ok=True)
    (OUT / "delta" / f"{uid}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return d


if __name__ == "__main__":
    for uid in sys.argv[1:] or ALL:
        build(uid)
        print("wrote", uid)
