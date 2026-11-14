"""Gold Deltas of the synthetic company policies SP01-SP14 (dataset/10_kebijakan_perusahaan/sintetis).

Each policy is one side update (kind "policy") with company-layer rules (PRS.SPxx.*) valid for the policy's term.
A company rule that produces a fact also produced by a mandatory regulation rule loses (lex superior); the engine
reports an override conflict with the rule's conflict code when the values differ. Minimum entitlements (C10) go
through the regulation constraint CON.THR.MINIMUM (bg_support).

Encoding choices (applied to every policy):
1. A clause is encoded when it states a value or computation for a fact of the vocabulary that can differ from the
   regulation (a fixed rate or cap where the regulation's value is conditional or changes, a method, a tax treatment)
   or a company-specific income item (allowances, THR).
2. A clause that only refers to "ketentuan yang berlaku" or restates a statutory value fixed over the whole test range
   (JHT 2%, JP 1%, JKM 0.30%, JKN 4%/1% with the Rp12 million cap, premiums included in gross) is not encoded: it has
   no content of its own.
3. Procedural clauses (payment dates, withholding slips) are not encoded.
4. "Dipotong dari penghasilan pekerja" is encoded as withholding_method = 'gross'.
5. DTP "not paid to the employee" is encoded as pph21_dtp = 0 (the vocabulary has no separate fact for the cash
   payment of DTP); it conflicts with the mandatory DTP rules where the employee is eligible.
"""
from . import Doc, Update, fact, rule

NOT_BILLED = "employer('premiums_as_billed') != True"
ROUND = "param('bpjs_round_mode')"
TERMS = {
    "SP01": ("2023-04-01", "2025-03-31"), "SP02": ("2023-01-01", "2024-12-31"), "SP03": ("2025-03-01", "2026-12-31"),
    "SP04": ("2023-01-01", "2024-12-31"), "SP05": ("2024-07-01", "2026-06-30"), "SP06": ("2025-01-01", "2026-12-31"),
    "SP07": ("2024-02-01", "2025-12-31"), "SP08": ("2024-02-01", "2025-12-31"), "SP09": ("2023-08-01", "2025-07-31"),
    "SP10": ("2024-04-01", "2026-03-31"), "SP11": ("2025-01-01", "2026-12-31"), "SP12": ("2024-02-01", "2025-12-31"),
    "SP13": ("2023-06-01", "2025-05-31"), "SP14": ("2025-01-01", "2026-12-31"),
}


class Policy:
    def __init__(self, pid):
        self.id = pid
        self.doc = Doc(pid)
        self.vf, self.vu = TERMS[pid]
        self.term = None

    def q(self, provision, quote):
        return self.doc.q(provision, quote)

    def rule(self, name, produces, expression, src, *, scope="period", cond=None, code=None, label="",
             modality="default"):
        src = src if isinstance(src, list) else [src]
        return rule(f"PRS.{self.id}.{name}", produces, expression, src + [self.term], self.vf, vu=self.vu,
                    scope=scope, cond=cond, layer="company", modality=modality, policy=self.id, code=code,
                    label=label)

    def method(self, method, src):
        return self.rule("METHOD", "withholding_method", f"'{method}'", src, scope="year",
                         label=f"withholding method stated by the policy: {method}")

    def jkk_rate(self, rate, src):
        return self.rule("JKK_RATE", "jkk_rate", f"dec('{rate}')", src, code="C6",
                         label="JKK rate written as a fixed number")

    def update(self, add, note=""):
        return Update(f"GOLD-{self.id}", self.doc, "policy", add=add, note=note)


def _sp01():
    p = Policy("SP01")
    p.term = p.q("Pasal 44 ayat (1)", "berlaku sejak tanggal 1 April 2023 sampai dengan tanggal 31 Maret 2025")
    meal = p.q("Pasal 14 ayat (2)", "uang makan sebesar Rp35.000,00 (tiga puluh lima ribu rupiah) dan uang transport sebesar "
               "Rp25.000,00 (dua puluh lima ribu rupiah) untuk setiap hari kehadiran")
    jp = [p.q("Pasal 22 ayat (4)", "1% (satu persen) ditanggung pekerja, dengan batas upah paling tinggi Rp9.559.600,00"),
          p.q("Pasal 22 ayat (5)", "berlaku selama masa berlaku Peraturan Perusahaan ini dan hanya dapat diubah melalui "
              "perubahan Peraturan Perusahaan")]
    return p.update([
        fact("attendance_allowance", "money", "period", meal, label="meal and transport allowance per day present",
             label_id="uang makan dan transport per hari hadir"),
        p.rule("ATTENDANCE_ALLOWANCE", "attendance_allowance", "(35000 + 25000) * hr('days_present')", meal),
        p.rule("OTHER_REGULAR", "other_regular_income", "income('other_regular') + attendance_allowance", meal,
               label="non-fixed allowances paid monthly are regular income"),
        p.jkk_rate("0.0054", p.q("Pasal 22 ayat (2)", "Iuran JKK sebesar 0,54% (nol koma lima puluh empat persen)")),
        p.rule("JP_EMPLOYEE", "jp_employee", f"round(dec('0.01') * min(bpjs_wage, 9559600), 1, {ROUND})", jp,
               cond=NOT_BILLED, code="C6", label="JP wage cap locked at Rp9,559,600 for the policy term"),
        p.method("gross", p.q("Pasal 24 ayat (1)", "menjadi beban pekerja dan dipotong dari penghasilan setiap bulan")),
    ])


def _sp02():
    p = Policy("SP02")
    p.term = p.q("Pasal 52 ayat (1)", "berlaku sejak tanggal 1 Januari 2023 sampai dengan tanggal 31 Desember 2024")
    reg = [p.q("Pasal 31 ayat (2)", "a. penghasilan bruto teratur sebulan dikalikan 12 (dua belas)"),
           p.q("Pasal 31 ayat (2) huruf b", "dikurangi biaya jabatan sebesar 5% (lima persen) paling banyak Rp6.000.000,00 (enam juta rupiah) setahun"),
           p.q("Pasal 31 ayat (2) huruf c", "dibulatkan ke bawah hingga ribuan rupiah penuh"),
           p.q("Pasal 31 ayat (2) huruf e", "e. hasilnya dibagi 12 (dua belas)")]
    irr = p.q("Pasal 31 ayat (3)", "sebesar selisih antara Pajak Penghasilan setahun atas penghasilan teratur yang "
              "disetahunkan ditambah penghasilan tidak teratur")
    lock = p.q("Pasal 31 ayat (5)", "berlaku selama masa berlaku Peraturan Perusahaan ini")
    pens = "12 * employee_pension_contributions"
    base_reg = "12 * regular_gross"
    taxable = ("max(0, round({g} - min(round(dec('0.05') * ({g}), 1, 'down'), 6000000) - " + pens
               + " - ptkp_amount, 1000, 'down'))")
    return p.update([
        fact("annualized_tax_regular", "money", "period", reg, label="annual tax on regular income annualised by 12",
             label_id="PPh setahun atas penghasilan teratur disetahunkan"),
        fact("annualized_tax_irregular", "money", "period", irr, label="tax on irregular income, difference method",
             label_id="PPh atas penghasilan tidak teratur"),
        p.jkk_rate("0.0089", p.q("Pasal 32 ayat (1)", "Iuran JKK sebesar 0,89% (nol koma delapan puluh sembilan persen)")),
        p.rule("TAX_REGULAR_ANNUAL", "annualized_tax_regular",
               f"round(progressive('pasal17', {taxable.format(g=base_reg)}), 1, 'down')", reg,
               cond="not is_final_period"),
        p.rule("TAX_IRREGULAR", "annualized_tax_irregular",
               f"(round(progressive('pasal17', {taxable.format(g=base_reg + ' + irregular_gross')}), 1, 'down')"
               " - annualized_tax_regular) if irregular_gross > 0 else 0", [irr] + reg, cond="not is_final_period"),
        p.rule("RUNNING", "pph21_running", "round(annualized_tax_regular / 12, 1, 'down') + annualized_tax_irregular",
               reg + [irr, lock], cond="not is_final_period", code="C5",
               label="annualised method locked for the policy term"),
        p.method("gross", p.q("Pasal 31 ayat (1)", "dipotong setiap bulan dari penghasilan pekerja")),
    ])


def _sp03():
    p = Policy("SP03")
    p.term = p.q("Pasal 60 ayat (1)", "berlaku sejak tanggal 1 Maret 2025 sampai dengan tanggal 31 Desember 2026")
    held = p.q("Pasal 40 ayat (3)", "diterima dan dikelola oleh Perusahaan untuk mendukung program kesejahteraan pekerja "
               "secara kolektif, dan tidak dibayarkan secara perorangan kepada pekerja")
    return p.update([
        p.rule("DTP_WITHHELD", "pph21_dtp", "0", held, code="C4",
               label="government-borne PPh 21 kept by the company, not paid to the employee"),
        p.method("gross", p.q("Pasal 40 ayat (1)", "menjadi beban pekerja dan dipotong oleh Perusahaan setiap bulan")),
    ])


def _sp04():
    p = Policy("SP04")
    p.term = p.q("Pasal 49 ayat (1)", "berlaku sejak tanggal 1 Januari 2023 sampai dengan tanggal 31 Desember 2024")
    src = [p.q("Pasal 27 ayat (2)", "diberikan fasilitas tempat tinggal berupa satu unit apartemen yang disewa Perusahaan"),
           p.q("Pasal 28", "tidak diperhitungkan sebagai penghasilan pekerja dalam penghitungan Pajak Penghasilan Pasal 21")]
    return p.update([
        p.rule("BENEFITS_NOT_INCOME", "benefit_housing_taxable", "0", src, code="C1",
               label="the apartment of Pasal 27 is treated as no income; other benefits in kind keep their "
                     "treatment (second reader, kebijakan.review.md)"),
        # koreksi emas 2026-10-29 (review/gold/sintetis_adjudikasi.md): "dipotong" alone does not say who bears the
        # tax, so no method rule; the case data's method applies
    ])


def _sp05():
    p = Policy("SP05")
    p.term = p.q("Pasal 67 ayat (1)", "berlaku sejak tanggal 1 Juli 2024 sampai dengan tanggal 30 Juni 2026")
    return p.update([
        p.jkk_rate("0.0054", p.q("Pasal 45 ayat (2)", "Iuran JKK ditetapkan sebesar 0,54% (nol koma lima puluh empat persen)")),
        p.method("gross", p.q("Pasal 47", "dipotong dari upah pekerja setiap bulan")),
    ])


def _sp06():
    p = Policy("SP06")
    p.term = p.q("Pasal 53 ayat (1)", "berlaku sejak tanggal 1 Januari 2025 sampai dengan tanggal 31 Desember 2026")
    return p.update([
        p.method("gross_up", [p.q("Pasal 33 ayat (1)", "sebesar Pajak Penghasilan Pasal 21 terutang atas penghasilan pekerja"),
                              p.q("Pasal 33 ayat (2)", "dihitung dengan metode gross-up")]),
        p.rule("DTP_AS_ALLOWANCE", "pph21_dtp", "0",
               p.q("Pasal 33 ayat (3)", "diperhitungkan sebagai pemenuhan tunjangan sebagaimana dimaksud pada ayat (1) "
                   "untuk Masa Pajak yang bersangkutan, dan Perusahaan tidak melakukan pembayaran tambahan"),
               code="C4", label="DTP counted against the tax allowance; no cash payment to the employee"),
    ])


def _thr(p, multiplier, src, leaver_keeps):
    leaver = "hr('days_terminated_before_holiday') <= 30" if leaver_keeps else "hr('days_terminated_before_holiday') == 0"
    mult = f"{multiplier} * " if multiplier else ""
    return p.rule("THR", "thr",
                  f"(round({mult}(base_salary + fixed_allowance) * min(hr('months_of_service'), 12) / 12, 1, 'down')"
                  f" if hr('months_of_service') >= 1 and {leaver} else 0) if hr('thr_holiday') == 1"
                  " else income('thr')", src, code="C10",
                  label="THR of the policy in the holiday period; other periods keep the THR recorded in the case")


def _sp07():
    p = Policy("SP07")
    p.term = p.q("Pasal 73 ayat (1)", "berlaku sejak tanggal 1 Februari 2024 sampai dengan tanggal 31 Desember 2025")
    src = [p.q("Pasal 52 ayat (2)", "diberikan THR sebesar 1 (satu) bulan upah"),
           p.q("Pasal 52 ayat (3)", "dengan perhitungan masa kerja dibagi 12 (dua belas) dikali 1 (satu) bulan upah"),
           p.q("Pasal 52 ayat (4)", "terdiri atas gaji pokok dan tunjangan tetap"),
           p.q("Pasal 52 ayat (6)", "berakhir sebelum hari raya keagamaan, karena sebab apa pun, tidak berhak atas THR")]
    return p.update([
        _thr(p, None, src, leaver_keeps=False),
        # koreksi emas 2026-10-29 (review/gold/sintetis_adjudikasi.md): "dipotong" alone does not say who bears the
        # tax, so no method rule; the case data's method applies
    ])


def _sp08():
    p = Policy("SP08")
    p.term = p.q("Pasal 39 ayat (1)", "berlaku sejak tanggal 1 Februari 2024 sampai dengan tanggal 31 Desember 2025")
    up = p.q("Pasal 18 ayat (3)", "dibulatkan ke atas hingga ratusan rupiah penuh")
    return p.update([
        p.rule("RUNNING", "pph21_running", "round(ter_rate * gross_income, 100, 'up')",
               [p.q("Pasal 18 ayat (1)", "dihitung dengan tarif efektif bulanan sesuai ketentuan perpajakan"), up],
               cond="not is_final_period", code="C9", label="monthly PPh rounded up to hundreds"),
        p.rule("JOB_EXPENSE", "job_expense", "round(dec('0.05') * annual_gross, 1, 'down')",
               p.q("Pasal 18 ayat (2) huruf b", "mengurangkan biaya jabatan sebesar 5% (lima persen) dari penghasilan bruto setahun"),
               scope="year", code="C3", label="job expense without the cap"),
        p.rule("DEDUCTIONS", "annual_deductions",
               "job_expense + annual_pension_contributions + annual_zakat_deduction + sum_periods('health_employee')",
               p.q("Pasal 18 ayat (2) huruf c", "mengurangkan iuran JHT, iuran JP, dan iuran Jaminan Kesehatan bagian pekerja setahun"),
               scope="year", code="C3", label="employee health contributions deducted"),
        p.rule("TAXABLE", "taxable_income", "max(0, round(annual_net - ptkp_amount, 1000, 'half_up'))",
               p.q("Pasal 18 ayat (2) huruf e", "membulatkan Penghasilan Kena Pajak ke ribuan rupiah terdekat, dengan sisa "
                   "Rp500,00 (lima ratus rupiah) atau lebih dibulatkan ke atas"),
               scope="year", code="C9", label="PKP rounded to the nearest thousand"),
        p.rule("FINAL", "pph21_due", "round(final_period_tax, 100, 'up')",
               [p.q("Pasal 18 ayat (2) huruf g", "mengurangkan Pajak Penghasilan Pasal 21 yang telah dipotong"), up],
               cond="is_final_period", code="C9", label="final-period PPh rounded up to hundreds"),
    ])


def _sp09():
    p = Policy("SP09")
    p.term = p.q("Pasal 46 ayat (1)", "berlaku sejak tanggal 1 Agustus 2023 sampai dengan tanggal 31 Juli 2025")
    return p.update([
        p.rule("PREMIUMS_NOT_GROSS", "employer_premiums_taxable", "0",
               p.q("Pasal 25 ayat (2)", "bukan merupakan penghasilan pekerja, dan tidak dimasukkan dalam penghasilan bruto"),
               code="C2", label="employer JKK, JKM, and JKN premiums left out of gross income"),
        p.jkk_rate("0.0054", p.q("Pasal 25 ayat (1)", "iuran JKK sebesar 0,54% (nol koma lima puluh empat persen)")),
        p.method("gross", p.q("Pasal 26 ayat (1)", "dipotong dari penghasilan pekerja sesuai ketentuan perpajakan")),
    ])


def _sp10():
    p = Policy("SP10")
    p.term = p.q("Pasal 62 ayat (1)", "berlaku sejak tanggal 1 April 2024 sampai dengan tanggal 31 Maret 2026")
    agreed = p.q("Pasal 41 ayat (5)", "merupakan kesepakatan para pihak dalam rangka program efisiensi")
    jkn = p.q("Pasal 41 ayat (3)", "dengan batas upah Rp12.000.000,00 (dua belas juta rupiah) dibayar oleh Perusahaan sebesar "
              "3% (tiga persen) dan oleh pekerja sebesar 2% (dua persen)")
    return p.update([
        p.rule("JHT_EMPLOYEE", "jht_employee", f"round(dec('0.03') * bpjs_wage, 1, {ROUND})",
               [p.q("Pasal 41 ayat (1)", "dan oleh pekerja sebesar 3% (tiga persen)"), agreed], cond=NOT_BILLED,
               code="C7", label="employee JHT share 3%"),
        p.rule("HEALTH_EMPLOYEE", "health_employee", f"round(dec('0.02') * min(bpjs_wage, 12000000), 1, {ROUND})",
               [jkn, agreed], cond=NOT_BILLED, code="C7", label="employee JKN share 2%"),
        p.rule("HEALTH_EMPLOYER", "health_premium_employer",
               f"round(dec('0.03') * min(bpjs_wage, 12000000), 1, {ROUND})", [jkn, agreed], cond=NOT_BILLED,
               code="C7", label="employer JKN share 3%"),
        p.jkk_rate("0.0054", p.q("Pasal 41 ayat (4)", "Iuran JKK sebesar 0,54% (nol koma lima puluh empat persen)")),
    ])


def _sp11():
    p = Policy("SP11")
    p.term = p.q("Pasal 71 ayat (1)", "berlaku sejak tanggal 1 Januari 2025 sampai dengan tanggal 31 Desember 2026")
    jp = [p.q("Pasal 50 ayat (1)", "terdiri atas 2% (dua persen) bagian Perusahaan dan 1% (satu persen) bagian pekerja"),
          p.q("Pasal 50 ayat (1)", "dihitung dari seluruh upah sebulan (gaji pokok dan tunjangan tetap) tanpa batas upah")]
    jkn = [p.q("Pasal 50 ayat (2)", "terdiri atas 4% (empat persen) bagian Perusahaan dan 1% (satu persen) bagian pekerja"),
           p.q("Pasal 50 ayat (2)", "dihitung dari seluruh upah sebulan tanpa batas upah")]
    leave = p.q("Pasal 51 ayat (2)", "dihitung dengan tarif efektif bulanan sebagaimana bulan-bulan sebelumnya, dan "
                "kekurangan atau kelebihan Pajak Penghasilan Pasal 21 diselesaikan sendiri oleh pekerja")
    return p.update([
        p.rule("JP_EMPLOYEE", "jp_employee", f"round(dec('0.01') * bpjs_wage, 1, {ROUND})", jp, cond=NOT_BILLED,
               code="C8", label="JP on the whole wage, no cap"),
        p.rule("HEALTH_EMPLOYEE", "health_employee", f"round(dec('0.01') * bpjs_wage, 1, {ROUND})", jkn,
               cond=NOT_BILLED, code="C8", label="JKN on the whole wage, no cap"),
        p.rule("HEALTH_EMPLOYER", "health_premium_employer", f"round(dec('0.04') * bpjs_wage, 1, {ROUND})", jkn,
               cond=NOT_BILLED, code="C8", label="JKN on the whole wage, no cap"),
        p.jkk_rate("0.0127", p.q("Pasal 50 ayat (3)", "Iuran JKK sebesar 1,27% (satu koma dua puluh tujuh persen)")),
        p.rule("LEAVER_TAX", "pph21_due",
               "round(bracket('ter_monthly', ter_category, gross_income) * gross_income, 1, param('pph_round_mode'))",
               leave, cond="is_final_period and final_month < 12", code="C5",
               label="leaver's last month at the monthly effective rate"),
        p.rule("LEAVER_REFUND", "refund_to_employee", "0", leave, scope="year", cond="final_month < 12", code="C5",
               label="over-withholding of a leaver settled by the employee"),
        # koreksi emas 2026-10-29 (review/gold/sintetis_adjudikasi.md): "dipotong" alone does not say who bears the
        # tax, so no method rule; the case data's method applies
    ])


def _sp12():
    p = Policy("SP12")
    p.term = p.q("Pasal 41 ayat (1)", "berlaku sejak tanggal 1 Februari 2024 sampai dengan tanggal 31 Desember 2025")
    return p.update([p.method("gross_up", [
        p.q("Pasal 20 ayat (1)", "termasuk atas tunjangan pajak itu sendiri"),
        p.q("Pasal 20 ayat (3)", "termasuk penghitungan ulang pada Masa Pajak Terakhir")])])


def _sp13():
    p = Policy("SP13")
    p.term = p.q("Pasal 82 ayat (1)", "berlaku sejak tanggal 1 Juni 2023 sampai dengan tanggal 31 Mei 2025")
    return p.update([
        p.method("employer_borne", p.q("Pasal 61 ayat (1)", "ditanggung sepenuhnya oleh Perusahaan")),
        p.jkk_rate("0.0127", p.q("Pasal 62", "Iuran JKK sebesar 1,27% (satu koma dua puluh tujuh persen)")),
    ], note="Pasal 60 (crew mess) defers to the tax rules ('sepanjang sesuai ketentuan perpajakan') and is not encoded.")


def _sp14():
    p = Policy("SP14")
    p.term = p.q("Pasal 81 ayat (1)", "berlaku sejak tanggal 1 Januari 2025 sampai dengan tanggal 31 Desember 2026")
    src = [p.q("Pasal 60 ayat (2)", "menerima THR sebesar 1,5 (satu koma lima) kali upah sebulan"),
           p.q("Pasal 60 ayat (3)", "sebesar masa kerja dibagi 12 (dua belas) dikali 1,5 (satu koma lima) kali upah sebulan"),
           p.q("Pasal 60 ayat (4)", "Upah sebulan terdiri atas gaji pokok dan tunjangan tetap"),
           p.q("Pasal 60 ayat (5)", "berakhir terhitung sejak 30 (tiga puluh) hari sebelum hari raya keagamaan tetap berhak atas THR")]
    return p.update([
        _thr(p, "dec('1.5')", src, leaver_keeps=True),
        # koreksi emas 2026-10-29 (review/gold/sintetis_adjudikasi.md): "dipotong" alone does not say who bears the
        # tax, so no method rule; the case data's method applies
    ], note="Pasal 61 ayat (3) (DTP paid in cash, not income) restates PMK 10/2025 Pasal 5 and is not encoded.")


UPDATES = []
SIDE_UPDATES = [_sp01(), _sp02(), _sp03(), _sp04(), _sp05(), _sp06(), _sp07(), _sp08(), _sp09(), _sp10(), _sp11(),
                _sp12(), _sp13(), _sp14()]
