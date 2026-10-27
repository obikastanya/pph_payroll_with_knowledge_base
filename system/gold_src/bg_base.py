"""Background updates BG-000 (vocabulary and input convention) and BG-001 (annualised method, UU 36/2008 tariffs).

Both are recorded on 2009-01-01, the start of the modelled range. BG-001 quotes PER-16/PJ/2016 for the annualised
method because its predecessors (PMK 252/PMK.03/2008, PER-31/PJ/2012) are not available; PER-16 restates the same
method. This anachronism only affects the development range (2012-2016) and is noted in the update.
"""
from . import Doc, Update, fact, param, rule, table

IC = Doc("INPUT-CONVENTION")
P16 = Doc("PER-16-PJ-2016")
UU36 = Doc("UU-36-2008")
START = "2009-01-01"
UPPER = "1000000000000"

# ---------------------------------------------------------------------------------------------- vocabulary
# name, type, scope, output, label, label_id
FACTS = [
    ("base_salary", "money", "period", True, "base salary", "gaji pokok"),
    ("fixed_allowance", "money", "period", False, "fixed allowances", "tunjangan tetap"),
    ("other_regular_income", "money", "period", False, "other regular income", "penghasilan teratur lain"),
    ("overtime_pay", "money", "period", True, "overtime pay", "upah lembur"),
    ("thr", "money", "period", True, "religious holiday allowance (THR)", "tunjangan hari raya"),
    ("bonus", "money", "period", True, "bonus", "bonus"),
    ("other_irregular_income", "money", "period", False, "other irregular income", "penghasilan tidak teratur lain"),
    ("company_deductions", "money", "period", False, "deductions by the employer", "potongan perusahaan"),
    ("zakat_withheld", "money", "period", False, "zakat paid through the employer", "zakat melalui pemberi kerja"),
    ("zakat_deductible", "money", "period", False, "zakat deductible in withholding", "zakat pengurang"),
    ("withholding_method", "category", "year", False, "withholding method", "metode pemotongan"),
    ("ptkp_status_input", "category", "year", False, "PTKP status at the start of the year", "status PTKP"),
    ("ptkp_status_effective", "category", "year", False, "PTKP status used", "status PTKP yang dipakai"),
    ("ptkp_amount", "money", "year", True, "non-taxable income (PTKP)", "penghasilan tidak kena pajak"),
    ("bpjs_wage", "money", "period", False, "monthly wage for social security contributions", "upah sebulan iuran"),
    ("jkk_rate", "rate", "period", False, "work accident premium rate", "tarif iuran JKK"),
    ("jkk_premium", "money", "period", True, "work accident premium paid by employer", "iuran jaminan kecelakaan kerja"),
    ("jkm_premium", "money", "period", True, "death benefit premium paid by employer", "iuran jaminan kematian"),
    ("health_wage", "money", "period", False, "wage base for health insurance", "dasar upah iuran jaminan kesehatan"),
    ("health_premium_employer", "money", "period", True, "health premium paid by employer", "iuran jaminan kesehatan pemberi kerja"),
    ("health_employee", "money", "period", False, "health contribution paid by employee", "iuran jaminan kesehatan pegawai"),
    ("jht_employee", "money", "period", True, "old-age savings contribution paid by employee", "iuran jaminan hari tua pegawai"),
    ("jp_wage", "money", "period", False, "wage base for pension contribution", "batas upah jaminan pensiun"),
    ("jp_employee", "money", "period", True, "pension contribution paid by employee", "iuran jaminan pensiun pegawai"),
    ("employer_premiums_taxable", "money", "period", False, "employer premiums that are income", "premi yang dibayar pemberi kerja"),
    ("employee_pension_contributions", "money", "period", False, "employee pension and old-age contributions", "iuran pensiun pegawai"),
    ("benefits_taxable_regular", "money", "period", False, "taxable benefits in kind, regular", "natura teratur"),
    ("benefits_taxable_irregular", "money", "period", False, "taxable benefits in kind, irregular", "natura tidak teratur"),
    ("tax_allowance", "money", "period", True, "tax allowance or tax borne by the employer", "tunjangan pajak"),
    ("regular_gross", "money", "period", False, "regular gross income", "penghasilan bruto teratur"),
    ("irregular_gross", "money", "period", False, "irregular gross income", "penghasilan bruto tidak teratur"),
    ("gross_income", "money", "period", True, "gross income of the period", "penghasilan bruto"),
    ("job_expense_month", "money", "period", False, "job expense of the month (annualised method)", "biaya jabatan sebulan"),
    ("net_regular_month", "money", "period", False, "net regular income of the month", "penghasilan neto sebulan"),
    ("annualization_factor", "int", "year", False, "months used to annualise", "faktor pengali disetahunkan"),
    ("taxable_regular_annualized", "money", "period", False, "annualised taxable regular income", "penghasilan kena pajak disetahunkan"),
    ("pph_regular_annual", "money", "period", False, "annual tax on annualised regular income", "PPh setahun atas penghasilan teratur"),
    ("pph_regular_month", "money", "period", False, "monthly tax on regular income", "PPh sebulan atas penghasilan teratur"),
    ("taxable_with_irregular", "money", "period", False, "annualised taxable income including irregular income", "penghasilan kena pajak termasuk tidak teratur"),
    ("taxable_without_irregular", "money", "period", False, "annualised taxable income without irregular income", "penghasilan kena pajak tanpa tidak teratur"),
    ("pph_irregular_month", "money", "period", False, "tax on irregular income of the month", "PPh atas penghasilan tidak teratur"),
    ("pph21_running", "money", "period", False, "PPh 21 of a period other than the final one", "PPh Pasal 21 masa"),
    ("pph21_due", "money", "period", True, "PPh 21 due for the period", "PPh Pasal 21 terutang"),
    ("pph21_dtp", "money", "period", True, "PPh 21 borne by the government", "PPh Pasal 21 ditanggung pemerintah"),
    ("employee_tax_burden", "money", "period", False, "PPh 21 borne by the employee", "PPh Pasal 21 yang ditanggung pegawai"),
    ("cash_income", "money", "period", False, "cash income of the period", "penghasilan tunai"),
    ("take_home_pay", "money", "period", True, "take-home pay", "gaji bersih"),
    ("annual_gross", "money", "year", True, "gross income of the tax year", "penghasilan bruto setahun"),
    ("job_expense", "money", "year", True, "job expense of the tax year", "biaya jabatan"),
    ("annual_pension_contributions", "money", "year", False, "employee pension contributions of the year", "iuran pensiun setahun"),
    ("annual_zakat_deduction", "money", "year", False, "zakat deducted in the year", "zakat setahun"),
    ("annual_deductions", "money", "year", True, "deductions of the tax year", "pengurang setahun"),
    ("annual_net", "money", "year", True, "net income of the tax year", "penghasilan neto setahun"),
    ("subjective_months", "int", "year", False, "months of subjective tax obligation", "bulan kewajiban subjektif"),
    ("taxable_income", "money", "year", True, "taxable income (PKP)", "penghasilan kena pajak"),
    ("annual_pph21", "money", "year", True, "PPh 21 of the tax year", "PPh Pasal 21 setahun"),
    ("withheld_before_final", "money", "year", False, "PPh 21 withheld before the final period", "PPh Pasal 21 yang telah dipotong"),
    ("final_period_tax", "money", "year", False, "PPh 21 of the final period", "PPh Pasal 21 masa pajak terakhir"),
    ("refund_to_employee", "money", "year", True, "over-withholding refunded to the employee", "kelebihan potong dikembalikan"),
]


def _vocabulary():
    src = IC.q("1", "cara data kasus satu pegawai tetap untuk satu tahun pajak masuk ke basis pengetahuan")
    return [fact(n, t, s, src, output=o, label=lab, label_id=lid) for n, t, s, o, lab, lid in FACTS]


def _input_convention():
    q = IC.q
    out = []
    for fid, produces, expr, quote in [
        ("BASE_SALARY", "base_salary", "income('base_salary')", "Gaji pokok masa itu sebagaimana tercatat pada data kasus menjadi nilai gaji pokok."),
        ("FIXED_ALLOWANCE", "fixed_allowance", "income('fixed_allowance')", "Tunjangan tetap masa itu sebagaimana tercatat pada data kasus menjadi nilai tunjangan tetap."),
        ("OTHER_REGULAR", "other_regular_income", "income('other_regular')", "Penghasilan teratur lain masa itu sebagaimana tercatat pada data kasus"),
        ("OVERTIME", "overtime_pay", "income('overtime_pay')", "Upah lembur masa itu sebagaimana tercatat pada data kasus menjadi nilai upah lembur."),
        ("THR", "thr", "income('thr')", "Tunjangan hari raya yang dibayar pada masa itu sebagaimana tercatat pada data kasus menjadi nilai THR."),
        ("BONUS", "bonus", "income('bonus')", "Bonus yang dibayar pada masa itu sebagaimana tercatat pada data kasus menjadi nilai bonus."),
        ("OTHER_IRREGULAR", "other_irregular_income", "income('other_irregular')", "Penghasilan tidak teratur lain masa itu sebagaimana tercatat pada data kasus"),
        ("DEDUCTIONS", "company_deductions", "income('deductions')", "Potongan oleh pemberi kerja masa itu sebagaimana tercatat pada data kasus menjadi nilai potongan perusahaan."),
        ("ZAKAT", "zakat_withheld", "zakat_paid()", "Zakat atau sumbangan keagamaan yang dibayarkan melalui pemberi kerja pada masa itu"),
    ]:
        out.append(rule(f"REG.INPUT.{fid}", produces, expr, q("1", quote), START, modality="default",
                        label=f"input convention: {produces}"))
    out.append(rule("REG.INPUT.METHOD", "withholding_method", "case('method')",
                    q("2", "Metode pemotongan pada data kasus (gross, gross up, atau ditanggung pemberi kerja) menjadi metode pemotongan"),
                    START, scope="year", modality="default"))
    out.append(rule("REG.INPUT.PTKP_STATUS", "ptkp_status_input", "employee('ptkp_status')",
                    q("2", "Status penghasilan tidak kena pajak pada data kasus adalah status pada awal tahun pajak."),
                    START, scope="year", modality="default"))
    zero = q("3", "Unsur yang belum diatur atau belum dimodelkan pada suatu masa bernilai nol")
    for fid, produces in [("JKK", "jkk_premium"), ("JKM", "jkm_premium"), ("HEALTH_EMPLOYER", "health_premium_employer"),
                          ("HEALTH_EMPLOYEE", "health_employee"), ("JHT", "jht_employee"), ("JP", "jp_employee"),
                          ("BENEFITS_REGULAR", "benefits_taxable_regular"),
                          ("BENEFITS_IRREGULAR", "benefits_taxable_irregular"),
                          ("TAX_ALLOWANCE", "tax_allowance"), ("DTP", "pph21_dtp"), ("ZAKAT_DEDUCTIBLE", "zakat_deductible")]:
        out.append(rule(f"REG.DEFAULT.{fid}", produces, "0", zero, START, modality="default",
                        label=f"default zero: {produces}"))
    billed = q("3", "premi dan iuran yang tercatat pada data kasus dipakai sebagai premi dan iuran masa itu")
    for fid, produces in [("JKK", "jkk_premium"), ("JKM", "jkm_premium"), ("HEALTH_EMPLOYER", "health_premium_employer"),
                          ("HEALTH_EMPLOYEE", "health_employee"), ("JHT", "jht_employee"), ("JP", "jp_employee")]:
        out.append(rule(f"REG.INPUT.BILLED.{fid}", produces, f"income('{produces}')", billed, START,
                        modality="default", cond="employer('premiums_as_billed') == True",
                        overrides=[f"REG.DEFAULT.{fid}"], label=f"premium as billed: {produces}"))
    rnd = q("4", "PPh Pasal 21 masa dibulatkan ke bawah ke rupiah penuh (pecahan rupiah dibuang)")
    out.append(param("PAR.PPH_ROUND_MODE.2009", "pph_round_mode", "truncate", "category", rnd, START,
                     label_id="pembulatan PPh Pasal 21 masa"))
    out.append(param("PAR.BPJS_ROUND_MODE.2009", "bpjs_round_mode", "half_up", "category",
                     q("4", "Premi dan iuran program jaminan sosial dibulatkan ke rupiah penuh terdekat"), START,
                     label_id="pembulatan premi dan iuran"))
    thp = q("5", "Gaji bersih (take home pay) adalah penghasilan tunai masa itu dikurangi iuran yang ditanggung pegawai")
    out.append(rule("REG.THP.CASH", "cash_income",
                    "base_salary + fixed_allowance + other_regular_income + overtime_pay + thr + bonus"
                    " + other_irregular_income + (tax_allowance if withholding_method == 'gross_up' else 0)",
                    thp, START, modality="default"))
    out.append(rule("REG.THP.TAX_BURDEN", "employee_tax_burden",
                    "0 if withholding_method == 'employer_borne' else ((pph21_due - pph21_dtp) if (not is_final_period"
                    " or pph21_due >= 0) else (0 - refund_to_employee))", thp, START, modality="default"))
    out.append(rule("REG.THP", "take_home_pay",
                    "cash_income - jht_employee - jp_employee - health_employee - company_deductions"
                    " - employee_tax_burden", thp, START, modality="default"))
    return out


BG000 = Update("BG-000", IC, "background", add=_vocabulary() + _input_convention(), recorded_on=START,
               note="Vocabulary (F_nilai frozen: facts with output=true) and input convention.")


# ---------------------------------------------------------------------------------------------- method
def _method():
    q16, q36 = P16.q, UU36.q
    out = []
    out.append(table("TAB.PTKP.2009", "ptkp", "lookup",
                     [q36("Pasal 7 ayat (1) huruf a", "Rp15.840.000,00 (lima belas juta delapan ratus"),
                      q36("Pasal 7 ayat (1) huruf b", "b. Rp1.320.000,00 (satu juta tiga ratus dua puluh"),
                      q36("Pasal 7 ayat (1) huruf d", "paling banyak 3 (tiga) orang untuk setiap keluarga")],
                     START, label_id="penghasilan tidak kena pajak",
                     rows=[{"key": k, "value": v} for k, v in [
                         ("TK/0", 15840000), ("TK/1", 17160000), ("TK/2", 18480000), ("TK/3", 19800000),
                         ("K/0", 17160000), ("K/1", 18480000), ("K/2", 19800000), ("K/3", 21120000)]]))
    out.append(table("TAB.PASAL17.2009", "pasal17", "progressive",
                     [q36("Pasal 17 ayat (1) huruf a", "sampai dengan Rp50.000.000,00 5%"),
                      q36("Pasal 17 ayat (1) huruf a", "di atas Rp250.000.000,00 (dua ratus 25%"),
                      q36("Pasal 17 ayat (1) huruf a", "di atas Rp500.000.000,00 (lima ratus 30%")],
                     START, label_id="tarif Pasal 17",
                     rows=[{"lower": 0, "upper": 50000000, "rate": "0.05"},
                           {"lower": 50000000, "upper": 250000000, "rate": "0.15"},
                           {"lower": 250000000, "upper": 500000000, "rate": "0.25"},
                           {"lower": 500000000, "upper": None, "rate": "0.30"}]))
    out.append(rule("REG.PTKP.STATUS", "ptkp_status_effective", "ptkp_status_input",
                    q36("Pasal 7 ayat (2)", "ditentukan oleh keadaan pada awal tahun pajak atau"), START, scope="year"))
    out.append(rule("REG.PTKP.STATUS.MARRIED_WOMAN", "ptkp_status_effective", "'TK/0'",
                    q16("Pasal 11 ayat (3)", "karyawati kawin"), START, scope="year",
                    cond="employee('sex') == 'F' and startswith(ptkp_status_input, 'K/')"
                         " and not employee('husband_no_income_certified')",
                    overrides=["REG.PTKP.STATUS"]))
    out.append(rule("REG.PTKP.AMOUNT", "ptkp_amount", "lookup('ptkp', ptkp_status_effective)",
                    q36("Pasal 7 ayat (1)", "Penghasilan Tidak Kena Pajak per tahun diberikan"), START, scope="year"))
    out.append(param("PAR.JOB_EXPENSE_RATE.2009", "job_expense_rate", "0.05", "rate",
                     q16("Pasal 10 ayat (3) huruf a", "biaya jabatan, sebesar 5% (lima persen) dari penghasilan bruto"),
                     START, label_id="biaya jabatan"))
    out.append(param("PAR.JOB_EXPENSE_MAX_MONTH.2009", "job_expense_max_month", 500000, "money",
                     q16("Pasal 10 ayat (3) huruf a", "Rp 500.000,00 (lima ratus ribu rupiah) sebulan"), START,
                     label_id="biaya jabatan sebulan"))
    out.append(param("PAR.JOB_EXPENSE_MAX_YEAR.2009", "job_expense_max_year", 6000000, "money",
                     q16("Pasal 10 ayat (3) huruf a", "Rp6.000.000,00"), START, label_id="biaya jabatan setahun"))
    # gross income
    reg = q16("Lampiran I angka 15", "berupa gaji atau upah, segala macam tunjangan, dan imbalan dengan nama")
    irr = q16("Lampiran I angka 16", "antara lain berupa bonus, Tunjangan Hari Raya")
    out.append(rule("REG.GROSS.REGULAR", "regular_gross",
                    "base_salary + fixed_allowance + other_regular_income + overtime_pay + employer_premiums_taxable"
                    " + benefits_taxable_regular + tax_allowance",
                    [reg, q16("Lampiran I angka 15", "termasuk uang lembur")], START))
    out.append(rule("REG.GROSS.IRREGULAR", "irregular_gross",
                    "thr + bonus + other_irregular_income + benefits_taxable_irregular", irr, START))
    out.append(rule("REG.GROSS", "gross_income", "regular_gross + irregular_gross",
                    q16("Pasal 10 ayat (1)", "adalah seluruh jumlah"), START))
    out.append(rule("REG.PREMIUMS.TAXABLE", "employer_premiums_taxable",
                    "jkk_premium + jkm_premium + health_premium_employer",
                    q16("Lampiran contoh", "(JKK), premi Jaminan Kematian (JK), dan premi"), START))
    out.append(rule("REG.PENSION.EMPLOYEE", "employee_pension_contributions", "jht_employee + jp_employee",
                    q16("Pasal 10 ayat (3) huruf b", "iuran yang terkait dengan gaji yang dibayar oleh pegawai kepada dana pensiun"),
                    START))
    # annualised method for periods other than the final one
    a14 = q16("Pasal 14 ayat (2) huruf a", "perkiraan atas penghasilan yang bersifat teratur adalah jumlah penghasilan")
    out.append(rule("REG.P16.JOB_EXPENSE_MONTH", "job_expense_month",
                    "min(round(param('job_expense_rate') * regular_gross, 1, 'down'), param('job_expense_max_month'))",
                    q16("Pasal 10 ayat (3) huruf a", "biaya jabatan, sebesar 5% (lima persen) dari penghasilan bruto"),
                    START, cond="not is_final_period"))
    out.append(rule("REG.P16.NET_MONTH", "net_regular_month",
                    "regular_gross - job_expense_month - employee_pension_contributions",
                    q16("Pasal 10 ayat (3)", "Besarnya penghasilan neto bagi Pegawai Tetap yang dipotong PPh Pasal 21 adalah"),
                    START, cond="not is_final_period"))
    out.append(rule("REG.P16.FACTOR", "annualization_factor", "12", a14, START, scope="year"))
    out.append(rule("REG.P16.FACTOR.NEW_EMPLOYEE", "annualization_factor", "12 - first_month + 1",
                    q16("Pasal 14 ayat (4)", "jumlah bulan tersisa dalam tahun"), START, scope="year",
                    cond="first_month > 1 and employee('subjective_start_month') == None",
                    overrides=["REG.P16.FACTOR"]))
    pkp = q16("Pasal 14 ayat (8)", "dibulatkan ke bawah hingga ribuan penuh")
    out.append(rule("REG.P16.TAXABLE_ANNUALIZED", "taxable_regular_annualized",
                    "max(0, round(net_regular_month * annualization_factor - ptkp_amount, 1000, 'down'))",
                    [a14, pkp], START, cond="not is_final_period"))
    out.append(rule("REG.P16.PPH_ANNUAL", "pph_regular_annual",
                    "round(progressive('pasal17', taxable_regular_annualized), 1, 'down')",
                    q16("Pasal 14 ayat (1)", "Tarif berdasarkan Pasal 17 ayat (1) huruf a"), START,
                    cond="not is_final_period"))
    out.append(rule("REG.P16.PPH_MONTH", "pph_regular_month",
                    "round(pph_regular_annual / annualization_factor, 1, param('pph_round_mode'))",
                    q16("Pasal 14 ayat (3) huruf a", "atas penghasilan yang bersifat teratur adalah sebesar Pajak Penghasilan"),
                    START, cond="not is_final_period"))
    b14 = q16("Pasal 14 ayat (3) huruf b", "atas penghasilan yang bersifat tidak teratur adalah sebesar selisih antara Pajak")
    with_irr = ("annualization_factor * regular_gross + irregular_gross")
    out.append(rule("REG.P16.TAXABLE_WITH_IRREGULAR", "taxable_with_irregular",
                    f"max(0, round(({with_irr}) - min(round(param('job_expense_rate') * ({with_irr}), 1, 'down'),"
                    " param('job_expense_max_year')) - annualization_factor * employee_pension_contributions"
                    " - ptkp_amount, 1000, 'down'))",
                    [b14, q16("Pasal 14 ayat (2) huruf b", "ditambah dengan jumlah")], START,
                    cond="not is_final_period and irregular_gross > 0"))
    out.append(rule("REG.P16.TAXABLE_WITHOUT_IRREGULAR", "taxable_without_irregular",
                    "max(0, round(annualization_factor * regular_gross - min(round(param('job_expense_rate')"
                    " * annualization_factor * regular_gross, 1, 'down'), param('job_expense_max_year'))"
                    " - annualization_factor * employee_pension_contributions - ptkp_amount, 1000, 'down'))",
                    b14, START, cond="not is_final_period and irregular_gross > 0"))
    out.append(rule("REG.P16.PPH_IRREGULAR", "pph_irregular_month",
                    "round(progressive('pasal17', taxable_with_irregular), 1, 'down')"
                    " - round(progressive('pasal17', taxable_without_irregular), 1, 'down')",
                    b14, START, cond="not is_final_period and irregular_gross > 0"))
    out.append(rule("REG.P16.PPH_IRREGULAR.NONE", "pph_irregular_month", "0", b14, START,
                    cond="not is_final_period and irregular_gross <= 0"))
    out.append(rule("REG.P16.RUNNING", "pph21_running", "pph_regular_month + pph_irregular_month",
                    q16("Pasal 14 ayat (3)", "dimaksud pada ayat (2) adalah:"), START, cond="not is_final_period"))
    # withholding per period and the final period (both regimes)
    out.append(rule("REG.PPH.DUE.RUNNING", "pph21_due", "pph21_running",
                    q16("Pasal 14 ayat (2)", "harus dipotong setiap Masa Pajak, kecuali"), START, cond="not is_final_period"))
    p5 = q16("Pasal 14 ayat (5)", "selisih antara Pajak Penghasilan yang terutang atas seluruh penghasilan kena")
    out.append(rule("REG.PPH.DUE.FINAL", "pph21_due", "final_period_tax", p5, START, cond="is_final_period"))
    out.append(rule("REG.YEAR.GROSS", "annual_gross", "sum_periods('gross_income')", p5, START, scope="year"))
    out.append(rule("REG.YEAR.JOB_EXPENSE", "job_expense",
                    "min(round(param('job_expense_rate') * annual_gross, 1, 'down'),"
                    " param('job_expense_max_month') * months_employed, param('job_expense_max_year'))",
                    q16("Pasal 10 ayat (3) huruf a", "biaya jabatan, sebesar 5% (lima persen) dari penghasilan bruto"),
                    START, scope="year", label="tafsir K6: aggregate cap of n x 500,000"))
    out.append(rule("REG.YEAR.PENSION", "annual_pension_contributions",
                    "sum_periods('employee_pension_contributions')",
                    q16("Pasal 10 ayat (3) huruf b", "iuran yang terkait dengan gaji yang dibayar oleh pegawai kepada dana pensiun"),
                    START, scope="year"))
    out.append(rule("REG.YEAR.ZAKAT", "annual_zakat_deduction", "sum_periods('zakat_deductible')",
                    IC.q("3", "Unsur yang belum diatur atau belum dimodelkan pada suatu masa bernilai nol"),
                    START, scope="year"))
    out.append(rule("REG.YEAR.DEDUCTIONS", "annual_deductions",
                    "job_expense + annual_pension_contributions + annual_zakat_deduction",
                    q16("Pasal 10 ayat (3)", "jumlah seluruh penghasilan bruto dikurangi dengan:"), START, scope="year"))
    out.append(rule("REG.YEAR.NET", "annual_net", "annual_gross - annual_deductions",
                    q16("Pasal 10 ayat (3)", "Besarnya penghasilan neto bagi Pegawai Tetap yang dipotong PPh Pasal 21 adalah"),
                    START, scope="year"))
    p6 = q16("Pasal 14 ayat (6)", "dihitung berdasarkan Penghasilan Kena Pajak yang disetahunkan,")
    out.append(rule("REG.YEAR.SUBJECTIVE_MONTHS", "subjective_months",
                    "(employee('subjective_end_month') if employee('subjective_end_month') != None else 12)"
                    " - (employee('subjective_start_month') if employee('subjective_start_month') != None else 1) + 1",
                    p6, START, scope="year"))
    out.append(rule("REG.YEAR.TAXABLE", "taxable_income",
                    "max(0, round(annual_net - ptkp_amount, 1000, 'down'))", pkp, START, scope="year"))
    out.append(rule("REG.YEAR.TAXABLE.PART_YEAR", "taxable_income",
                    "max(0, round(annual_net * 12 / subjective_months - ptkp_amount, 1000, 'down'))",
                    [p6, pkp], START, scope="year", cond="subjective_months < 12", overrides=["REG.YEAR.TAXABLE"]))
    out.append(rule("REG.YEAR.PPH", "annual_pph21", "round(progressive('pasal17', taxable_income), 1, 'down')",
                    q16("Pasal 14 ayat (1)", "Tarif berdasarkan Pasal 17 ayat (1) huruf a"), START, scope="year"))
    out.append(rule("REG.YEAR.PPH.PART_YEAR", "annual_pph21",
                    "round(progressive('pasal17', taxable_income) * subjective_months / 12, 1, param('pph_round_mode'))",
                    [p6, q16("Pasal 14 ayat (6)", "sebanding dengan jumlah bulan dalam bagian tahun")], START,
                    scope="year", cond="subjective_months < 12", overrides=["REG.YEAR.PPH"]))
    out.append(rule("REG.YEAR.WITHHELD", "withheld_before_final", "sum_periods_before_final('pph21_due')",
                    q16("Pasal 14 ayat (5)", "yang telah dipotong pada masa"), START, scope="year"))
    out.append(rule("REG.YEAR.FINAL_TAX", "final_period_tax", "annual_pph21 - withheld_before_final", p5, START,
                    scope="year"))
    out.append(rule("REG.YEAR.REFUND", "refund_to_employee", "max(0, 0 - final_period_tax)",
                    q16("Pasal 14 ayat (7)", "lebih besar dari PPh Pasal 21 yang terutang untuk 1 (satu) tahun pajak maka kelebihan"),
                    START, scope="year"))
    # gross-up: tax allowance equal to the tax (least fixed point, tafsir K3)
    gu = q16("Pasal 10 ayat (1)", "adalah seluruh jumlah")
    out.append(rule("REG.GROSSUP.RUNNING", "tax_allowance", "pph21_running", gu, START,
                    cond="withholding_method == 'gross_up' and not is_final_period", fixed_point=("0", UPPER),
                    label="tafsir K3: least fixed point T = PPh(B + T)"))
    out.append(rule("REG.GROSSUP.FINAL", "tax_allowance", "max(0, final_period_tax)", gu, START,
                    cond="withholding_method == 'gross_up' and is_final_period", fixed_point=("0", UPPER),
                    label="tafsir K3 item 2: final period allowance = shortfall of the year, least fixed point"))
    return out


BG001 = Update("BG-001", P16, "background", add=_method(), recorded_on=START,
               note=("Annualised method and UU 36/2008 tariffs, recorded 2009-01-01. The method is quoted from "
                     "PER-16/PJ/2016 because PMK 252/PMK.03/2008 and PER-31/PJ/2012 are not available; PER-16 "
                     "restates the same method. Only the development range is affected by this anachronism."))

UPDATES = [BG000, BG001]
