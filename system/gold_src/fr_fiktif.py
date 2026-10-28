"""Gold Deltas of the fictive development regulations FR01-FR05 (dataset/09_korpus_peristiwa/fiktif/). FICTIVE: used
only to tune prompts and gates, never for testing.

Every update here is a side update (SIDE_UPDATES): it is not part of the main chain. build_gold.apply_side applies it
to the main-chain prefix known at its issue date (FR are separate counterfactuals to the real rules of their time,
fiktif/README.md "Cara membaca").

Decisions:
- FR01 (PP FIKTIF 901/2019): effective-rate method for non-final periods from Masa Januari 2020 (Pasal 2-3, Lampiran)
  and Pasal 5 declares the annualised method for non-final periods no longer valid, so the twelve PER-16 rules of the
  annualised method are closed on 2019-12-31 (the same set E04 closes in the real chain). The final period is
  unchanged (Pasal 4 restates the existing rule).
- FR02 (PER FIKTIF-902/PJ/2020): PKP rounded down to hundred thousands and period PPh other than the final period
  rounded down to hundreds from Masa Januari 2021. The rounding unit is a literal in the PER-16 rules, so new rule
  versions valid from 2021-01-01 win by lex posterior; the earlier versions keep their values for earlier periods.
- FR03 (PMK FIKTIF 903/2021) revokes PMK FIKTIF 455/2017, which is not in the real chain. The revoked rule exists only
  in the fictive world, so the gold has two side updates: BG-FR03, a fictive background update that establishes the
  night-shift job expense as summarised in FR03 consideration a (recorded 2017-12-29, valid from 2018-01-01: the
  issue date of PMK FIKTIF 455/2017 is not stated; "Sejak 2018" in FR03.json), and GOLD-FR03 applied on prefix (+)
  BG-FR03. GOLD-FR03 closes the rules and parameters on 2021-12-31 (Pasal 2 ayat (2): still deductible for Tahun
  Pajak 2021, including Desember 2021). A remove (tombstone) would erase the 2021 deduction, so closing is the gold.
- FR04 (PMK FIKTIF 904/2018): variable sales commission becomes irregular income from 2019. Case data contract: the
  payroll records commission as other regular income (input convention, as before FR04) and marks the variable part
  in hr('variable_sales_commission'). New gross rules valid from 2019-01-01 move that part from regular to irregular
  gross; the PER-16 difference method for irregular income (Pasal 3) is already in the chain.
- FR05: FR05A (PMK FIKTIF 905/2021) sets the annual cap Rp7.200.000 but Pasal 2-3 defer application to a PER Dirjen,
  so its Delta is empty (relevant, deferred). FR05B (PER FIKTIF-906/PJ/2022) gives the monthly cap and applies both
  from Masa Januari 2022: two parameter versions recorded 2022-02-14, retroactive to 2022-01-01.
"""
from . import Doc, Update, fact, param, rule, table

FR01, FR02, FR03, FR04 = Doc("FR01"), Doc("FR02"), Doc("FR03"), Doc("FR04")
FR05A, FR05B = Doc("FR05A"), Doc("FR05B")

P16_RULES = ["REG.P16.JOB_EXPENSE_MONTH", "REG.P16.NET_MONTH", "REG.P16.FACTOR", "REG.P16.FACTOR.NEW_EMPLOYEE",
             "REG.P16.FACTOR.KNOWN_END",
             "REG.P16.TAXABLE_ANNUALIZED", "REG.P16.PPH_ANNUAL", "REG.P16.PPH_MONTH",
             "REG.P16.TAXABLE_WITH_IRREGULAR", "REG.P16.TAXABLE_WITHOUT_IRREGULAR", "REG.P16.PPH_IRREGULAR",
             "REG.P16.PPH_IRREGULAR.NONE", "REG.P16.RUNNING"]


def _base_records():
    from .bg_base import BG001
    return {e["id"]: e for e in BG001.add}


def _closed(element, until, extra_source):
    out = dict(element)
    out["valid_until"] = until
    out["source"] = list(out["source"]) + extra_source
    out.pop("recorded_on", None)
    return out


# ---------------------------------------------------------------------------------------------------- FR01
def _fr01():
    q = FR01.q
    vf = "2020-01-01"
    p2 = q("Pasal 2 ayat (1)", "Pajak Penghasilan Pasal 21 bagi Pegawai Tetap untuk setiap Masa Pajak selain Masa Pajak "
                               "Terakhir dihitung dengan mengalikan Tarif Efektif Bulanan dengan penghasilan bruto")
    cat = [q("Pasal 2 ayat (2)", "Kategori I, untuk status Penghasilan Tidak Kena Pajak tidak kawin tanpa tanggungan"),
           q("Lampiran", "Kategori I: status TK/0, TK/1, dan K/0. Kategori II: status selain Kategori I.")]
    lamp = [q("Pasal 2 ayat (3)", "Besarnya Tarif Efektif Bulanan sebagaimana tercantum dalam Lampiran")]
    rows_i = [("sampai dengan Rp4.500.000 | 0%", 0, 4500000, "0"),
              ("di atas Rp4.500.000 sampai dengan Rp6.000.000 | 0,5%", 4500000, 6000000, "0.005"),
              ("di atas Rp6.000.000 sampai dengan Rp8.000.000 | 1%", 6000000, 8000000, "0.01"),
              ("di atas Rp8.000.000 sampai dengan Rp10.000.000 | 1,75%", 8000000, 10000000, "0.0175"),
              ("di atas Rp10.000.000 sampai dengan Rp15.000.000 | 3%", 10000000, 15000000, "0.03"),
              ("di atas Rp15.000.000 sampai dengan Rp25.000.000 | 6%", 15000000, 25000000, "0.06"),
              ("di atas Rp25.000.000 sampai dengan Rp50.000.000 | 12%", 25000000, 50000000, "0.12"),
              ("di atas Rp50.000.000 | 20%", 50000000, None, "0.20")]
    rows_ii = [("sampai dengan Rp5.500.000 | 0%", 0, 5500000, "0"),
               ("di atas Rp5.500.000 sampai dengan Rp7.000.000 | 0,5%", 5500000, 7000000, "0.005"),
               ("di atas Rp7.000.000 sampai dengan Rp9.000.000 | 1%", 7000000, 9000000, "0.01"),
               ("di atas Rp9.000.000 sampai dengan Rp11.000.000 | 1,5%", 9000000, 11000000, "0.015"),
               ("di atas Rp11.000.000 sampai dengan Rp16.000.000 | 2,5%", 11000000, 16000000, "0.025"),
               ("di atas Rp16.000.000 sampai dengan Rp26.000.000 | 5%", 16000000, 26000000, "0.05"),
               ("di atas Rp26.000.000 sampai dengan Rp52.000.000 | 11%", 26000000, 52000000, "0.11"),
               ("di atas Rp52.000.000 | 19%", 52000000, None, "0.19")]
    table_src = lamp + [q("Lampiran Kategori I", t) for t, *_ in rows_i] + [q("Lampiran Kategori II", t)
                                                                            for t, *_ in rows_ii]
    gross = q("Pasal 3", "meliputi seluruh penghasilan teratur dan tidak teratur yang diterima atau diperoleh dalam Masa "
                         "Pajak yang bersangkutan")
    start = q("Pasal 6", "Peraturan Pemerintah ini mulai berlaku pada tanggal 1 Januari 2020.")
    revoke = [q("Pasal 5", "dengan cara menyetahunkan penghasilan teratur dinyatakan tidak berlaku"), start]
    add = [
        fact("effective_rate_category", "category", "year", cat, label="monthly effective rate category",
             label_id="kategori tarif efektif bulanan"),
        fact("effective_rate", "rate", "period", p2, label="monthly effective rate", label_id="tarif efektif bulanan"),
        table("TAB.TEB_CATEGORY.2020", "effective_rate_category", "lookup", cat + [start], vf,
              label_id="kategori tarif efektif bulanan",
              rows=[{"key": k, "value": v} for k, v in [
                  ("TK/0", "I"), ("TK/1", "I"), ("K/0", "I"), ("TK/2", "II"), ("TK/3", "II"), ("K/1", "II"),
                  ("K/2", "II"), ("K/3", "II")]]),
        table("TAB.TEB_MONTHLY.2020", "effective_rate_monthly", "bracket", table_src + [start], vf,
              label_id="tarif efektif bulanan",
              rows=[{"key": "I", "lower": lo, "upper": up, "value": v} for _, lo, up, v in rows_i]
              + [{"key": "II", "lower": lo, "upper": up, "value": v} for _, lo, up, v in rows_ii]),
        rule("REG.TEB.CATEGORY", "effective_rate_category", "lookup('effective_rate_category', ptkp_status_effective)",
             cat + [start], vf, scope="year"),
        rule("REG.TEB.RATE", "effective_rate", "bracket('effective_rate_monthly', effective_rate_category, gross_income)",
             [p2, gross] + lamp + [start], vf, cond="not is_final_period"),
        rule("REG.TEB.RUNNING", "pph21_running", "round(effective_rate * gross_income, 1, param('pph_round_mode'))",
             [p2, gross, start], vf, cond="not is_final_period"),
    ]
    base = _base_records()
    change = [_closed(base[rid], "2019-12-31", revoke) for rid in P16_RULES]
    return add, change


# ---------------------------------------------------------------------------------------------------- FR02
def _fr02():
    q = FR02.q
    vf = "2021-01-01"
    pkp = q("Pasal I angka 1", "Penghasilan Kena Pajak setahun dibulatkan ke bawah hingga ratus ribu rupiah penuh.")
    pph = q("Pasal I angka 2", "Pajak Penghasilan Pasal 21 terutang untuk setiap Masa Pajak selain Masa Pajak terakhir "
                               "dibulatkan ke bawah hingga ratusan rupiah penuh.")
    start = q("Pasal II", "mulai berlaku untuk penghitungan Pajak Penghasilan Pasal 21 Masa Pajak Januari 2021.")
    base = _base_records()
    out = []
    for rid in ["REG.P16.TAXABLE_ANNUALIZED", "REG.P16.TAXABLE_WITH_IRREGULAR", "REG.P16.TAXABLE_WITHOUT_IRREGULAR",
                "REG.YEAR.TAXABLE", "REG.YEAR.TAXABLE.PART_YEAR"]:
        old = base[rid]
        expr = old["expression"]
        assert expr.count(", 1000, 'down')") == 1, rid
        out.append(rule(rid + ".2021", old["produces"], expr.replace(", 1000, 'down')", ", 100000, 'down')"),
                        [pkp, start], vf, scope=old.get("scope", "period"), cond=old.get("condition"),
                        overrides=[o + ".2021" for o in old.get("overrides", [])],
                        label="FR02: PKP rounded down to hundred thousands"))
    out.append(rule("REG.P16.RUNNING.2021", "pph21_running",
                    "round(pph_regular_month + pph_irregular_month, 100, 'down')", [pph, start], vf,
                    cond="not is_final_period", label="FR02: period PPh other than the final period, to hundreds"))
    return out


# ---------------------------------------------------------------------------------------------------- FR03
NIGHT_RULES = ["REG.NIGHT_SHIFT.MONTH", "REG.NIGHT_SHIFT.YEAR", "REG.NIGHT_SHIFT.NET_MONTH",
               "REG.NIGHT_SHIFT.TAXABLE_WITH_IRREGULAR", "REG.NIGHT_SHIFT.TAXABLE_WITHOUT_IRREGULAR",
               "REG.NIGHT_SHIFT.DEDUCTIONS"]
NIGHT_PARAMS = ["PAR.NIGHT_SHIFT_RATE.2018", "PAR.NIGHT_SHIFT_MAX_MONTH.2018", "PAR.NIGHT_SHIFT_MAX_YEAR.2018",
                "PAR.NIGHT_SHIFT_MIN_DAYS.2018"]


def _fr03_base():
    """Fictive PMK 455/PMK.03/2017 as summarised in FR03 consideration a (the only text of it in the corpus)."""
    q = FR03.q
    vf = "2018-01-01"
    a = q("Menimbang huruf a", "menetapkan tambahan biaya jabatan bagi Pegawai Tetap yang bekerja gilir malam")
    days = q("Menimbang huruf a", "paling sedikit 10 (sepuluh) hari dalam sebulan sebesar 2% (dua persen) dari "
                                  "penghasilan bruto")
    caps = q("Menimbang huruf a", "paling banyak Rp100.000,00 (seratus ribu rupiah) sebulan atau Rp1.200.000,00 (satu "
                                  "juta dua ratus ribu rupiah) setahun")
    extra = q("Menimbang huruf a", "di luar biaya jabatan sebagaimana diatur dalam Peraturan Menteri Keuangan Nomor "
                                   "250/PMK.03/2008")
    base = _base_records()
    month = "night_shift_job_expense_month"
    w_old = base["REG.P16.TAXABLE_WITH_IRREGULAR"]["expression"]
    wo_old = base["REG.P16.TAXABLE_WITHOUT_IRREGULAR"]["expression"]
    pens = " - annualization_factor * employee_pension_contributions"
    assert w_old.count(pens) == 1 and wo_old.count(pens) == 1
    add_month = f"{pens} - annualization_factor * {month}"
    return [
        fact(month, "money", "period", [a, days, caps], label="additional job expense for night shift work",
             label_id="tambahan biaya jabatan gilir malam sebulan"),
        fact("night_shift_job_expense", "money", "year", [a, caps], label="additional night-shift job expense of the year",
             label_id="tambahan biaya jabatan gilir malam setahun"),
        param("PAR.NIGHT_SHIFT_RATE.2018", "night_shift_rate", "0.02", "rate", days, vf,
              label_id="tarif tambahan biaya jabatan gilir malam"),
        param("PAR.NIGHT_SHIFT_MAX_MONTH.2018", "night_shift_max_month", 100000, "money", caps, vf,
              label_id="batas sebulan"),
        param("PAR.NIGHT_SHIFT_MAX_YEAR.2018", "night_shift_max_year", 1200000, "money", caps, vf,
              label_id="batas setahun"),
        param("PAR.NIGHT_SHIFT_MIN_DAYS.2018", "night_shift_min_days", 10, "int", days, vf,
              label_id="hari gilir malam paling sedikit"),
        rule("REG.NIGHT_SHIFT.MONTH", month,
             "(min(round(param('night_shift_rate') * regular_gross, 1, 'down'), param('night_shift_max_month'))"
             " if hr('night_shift_days') >= param('night_shift_min_days') else 0)", [a, days, caps], vf),
        rule("REG.NIGHT_SHIFT.YEAR", "night_shift_job_expense",
             f"min(sum_periods('{month}'), param('night_shift_max_year'))", [a, caps], vf, scope="year"),
        rule("REG.NIGHT_SHIFT.NET_MONTH", "net_regular_month",
             f"regular_gross - job_expense_month - employee_pension_contributions - {month}", [a, extra], vf,
             cond="not is_final_period"),
        rule("REG.NIGHT_SHIFT.TAXABLE_WITH_IRREGULAR", "taxable_with_irregular", w_old.replace(pens, add_month),
             [a, extra], vf, cond=base["REG.P16.TAXABLE_WITH_IRREGULAR"]["condition"]),
        rule("REG.NIGHT_SHIFT.TAXABLE_WITHOUT_IRREGULAR", "taxable_without_irregular", wo_old.replace(pens, add_month),
             [a, extra], vf, cond=base["REG.P16.TAXABLE_WITHOUT_IRREGULAR"]["condition"]),
        rule("REG.NIGHT_SHIFT.DEDUCTIONS", "annual_deductions",
             "job_expense + annual_pension_contributions + annual_zakat_deduction + night_shift_job_expense",
             [a, extra], vf, scope="year"),
    ]


def _fr03(base_add):
    q = FR03.q
    revoke = [q("Pasal 1", "Peraturan Menteri Keuangan Nomor 455/PMK.03/2017 tentang Tambahan Biaya Jabatan bagi "
                           "Pegawai Tetap yang Bekerja Gilir Malam dicabut dan dinyatakan tidak berlaku."),
              q("Pasal 2 ayat (1)", "tidak dapat dikurangkan dalam penghitungan Pajak Penghasilan Pasal 21 mulai Masa "
                                    "Pajak Januari 2022."),
              q("Pasal 2 ayat (2)", "masih dapat dikurangkan dalam penghitungan Pajak Penghasilan Pasal 21 untuk Tahun "
                                    "Pajak 2021, termasuk pada Masa Pajak Desember 2021.")]
    by_id = {e["id"]: e for e in base_add}
    return [_closed(by_id[i], "2021-12-31", revoke) for i in NIGHT_RULES + NIGHT_PARAMS]


# ---------------------------------------------------------------------------------------------------- FR04
def _fr04():
    q = FR04.q
    vf = "2019-01-01"
    var = q("Pasal 2 ayat (1)", "Komisi penjualan yang besarnya bergantung pada realisasi penjualan dan tidak dibayarkan "
                                "dalam jumlah tetap setiap bulan merupakan penghasilan yang bersifat tidak teratur.")
    fixed = q("Pasal 2 ayat (2)", "Komisi penjualan yang dibayarkan dalam jumlah tetap setiap bulan merupakan "
                                  "penghasilan yang bersifat teratur.")
    defn = q("Pasal 1", "Komisi penjualan adalah imbalan yang diberikan pemberi kerja kepada Pegawai Tetap berdasarkan "
                        "realisasi penjualan barang atau jasa dalam periode tertentu.")
    start = q("Pasal 4", "Peraturan Menteri ini mulai berlaku pada tanggal 1 Januari 2019.")
    base = _base_records()
    reg_old, irr_old = base["REG.GROSS.REGULAR"]["expression"], base["REG.GROSS.IRREGULAR"]["expression"]
    return [
        fact("variable_sales_commission", "money", "period", [defn, var],
             label="sales commission that depends on sales (part of other regular income in the case data)",
             label_id="komisi penjualan tidak tetap"),
        rule("REG.COMMISSION.VARIABLE", "variable_sales_commission",
             "min(hr('variable_sales_commission'), other_regular_income)", [defn, var, start], vf,
             label="case contract: the payroll marks the variable part of commission paid as other regular income"),
        rule("REG.GROSS.REGULAR.2019", "regular_gross", f"{reg_old} - variable_sales_commission", [var, fixed, start],
             vf, label="FR04 Pasal 2: variable sales commission leaves regular income"),
        rule("REG.GROSS.IRREGULAR.2019", "irregular_gross", f"{irr_old} + variable_sales_commission", [var, start], vf,
             label="FR04 Pasal 2 ayat (1): variable sales commission is irregular income"),
    ]


# ---------------------------------------------------------------------------------------------------- FR05
def _fr05b():
    qa, qb = FR05A.q, FR05B.q
    vf = "2022-01-01"
    year = [qa("Pasal 1", "paling banyak Rp7.200.000,00 (tujuh juta dua ratus ribu rupiah) setahun."),
            qb("Pasal 1 ayat (1)", "paling banyak Rp600.000,00 (enam ratus ribu rupiah) sebulan atau Rp7.200.000,00 "
                                   "(tujuh juta dua ratus ribu rupiah) setahun.")]
    month = [qb("Pasal 1 ayat (1)", "biaya jabatan bagi Pegawai Tetap sebesar 5% (lima persen) dari penghasilan bruto, "
                                    "paling banyak Rp600.000,00 (enam ratus ribu rupiah) sebulan"),
             qb("Pasal 1 ayat (2)", "biaya jabatan paling banyak Rp600.000,00 (enam ratus ribu rupiah) dikalikan jumlah "
                                    "bulan bekerja.")]
    start = qb("Pasal 2 ayat (1)", "diterapkan dalam penghitungan Pajak Penghasilan Pasal 21 mulai Masa Pajak Januari "
                                   "2022.")
    return [
        param("PAR.JOB_EXPENSE_MAX_MONTH.2022", "job_expense_max_month", 600000, "money", month + [start], vf,
              label_id="biaya jabatan sebulan"),
        param("PAR.JOB_EXPENSE_MAX_YEAR.2022", "job_expense_max_year", 7200000, "money", year + [start], vf,
              label_id="biaya jabatan setahun"),
    ]


_BG_FR03 = Update("BG-FR03", FR03, "background", add=_fr03_base(), recorded_on="2017-12-29",
                  note=("FICTIVE background: PMK FIKTIF 455/PMK.03/2017 as summarised in FR03 consideration a; issue "
                        "date not stated (assumed 2017-12-29, valid from 2018-01-01). Base of GOLD-FR03 only."))
_GOLD_FR03 = Update("GOLD-FR03", FR03, "event", event_id="FR03", change=_fr03(_BG_FR03.add),
                    note="Revocation without replacement: closed on 2021-12-31 (Pasal 2 ayat (2)); applied on BG-FR03.")
_GOLD_FR03.base_side = ["BG-FR03"]

_fr01_add, _fr01_change = _fr01()
SIDE_UPDATES = [
    Update("GOLD-FR01", FR01, "event", event_id="FR01", add=_fr01_add, change=_fr01_change,
           note="FICTIVE. Effective-rate method for non-final periods from 2020; annualised method closed (Pasal 5)."),
    Update("GOLD-FR02", FR02, "event", event_id="FR02", add=_fr02(),
           note="FICTIVE. Rounding of PKP (100.000) and period PPh (100) from Masa Januari 2021."),
    _BG_FR03,
    _GOLD_FR03,
    Update("GOLD-FR04", FR04, "event", event_id="FR04", add=_fr04(),
           note="FICTIVE. Variable sales commission is irregular income from 2019 (case marks it in hr)."),
    Update("GOLD-FR05A", FR05A, "event", event_id="FR05",
           note=("FICTIVE. Relevant but deferred: Pasal 2-3 leave the monthly cap and the start to a PER Dirjen and keep "
                 "PMK 250/2008 until then, so nothing changes yet (FR05-4).")),
    Update("GOLD-FR05B", FR05B, "event", event_id="FR05", add=_fr05b(),
           note="FICTIVE. Job expense caps 600.000 a month and 7.200.000 a year from Masa Januari 2022 (retroactive)."),
]
UPDATES = []
