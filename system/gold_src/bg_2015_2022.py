"""Background updates 2015-2022: social security contributions (PP 44-46/2015, Perpres JKN), PTKP 2016, UU HPP
tariffs, and the JP wage cap known before the test range. None of these documents is a corpus event."""
from . import Doc, Update, param, rule, table

P44, P45, P46 = Doc("PP-44-2015"), Doc("PP-45-2015"), Doc("PP-46-2015")
PMK101 = Doc("PMK-101-PMK010-2016")
JKN82, JKN75 = Doc("PERPRES-82-2018"), Doc("PERPRES-75-2019")
HPP = Doc("UU-7-2021")
JP23 = Doc("BPJSTK-JP-2023")

NOT_BILLED = "employer('premiums_as_billed') != True"
ROUND = "param('bpjs_round_mode')"
BPJS_START = "2015-07-01"


def _pp44():
    q = P44.q
    wage = q("Pasal 19 ayat (2)", "terdiri atas Upah pokok dan tunjangan tetap.")
    return [
        rule("REG.BPJS.WAGE", "bpjs_wage", "base_salary + fixed_allowance",
             [q("Pasal 19 ayat (1)", "Upah yang dijadikan dasar pembayaran Iuran bagi"), wage], BPJS_START),
        table("TAB.JKK_RATES.2015", "jkk_rates", "lookup",
              [q("Pasal 16 ayat (1) huruf a", "tingkat risiko sangat rendah : 0,24%"),
               q("Pasal 16 ayat (1) huruf b", "tingkat risiko rendah : 0,54%"),
               q("Pasal 16 ayat (1) huruf c", "tingkat risiko sedang : 0,89%"),
               q("Pasal 16 ayat (1) huruf d", "tingkat risiko tinggi : 1,27%"),
               q("Pasal 16 ayat (1) huruf e", "tingkat risiko sangat tinggi : 1,74%")],
              BPJS_START, label_id="tarif iuran JKK menurut tingkat risiko",
              rows=[{"key": "very_low", "value": "0.0024"}, {"key": "low", "value": "0.0054"},
                    {"key": "medium", "value": "0.0089"}, {"key": "high", "value": "0.0127"},
                    {"key": "very_high", "value": "0.0174"}]),
        rule("REG.BPJS.JKK_RATE", "jkk_rate", "lookup('jkk_rates', employer('jkk_risk_group'))",
             q("Pasal 16 ayat (1)", "dalam 5 (lima) kelompok tingkat risiko lingkungan"), BPJS_START),
        rule("REG.BPJS.JKK", "jkk_premium", f"round(jkk_rate * bpjs_wage, 1, {ROUND})",
             q("Pasal 16 ayat (1) huruf a", "tingkat risiko sangat rendah : 0,24%"), BPJS_START, cond=NOT_BILLED),
        param("PAR.JKM_RATE.2015", "jkm_rate", "0.003", "rate",
              q("Pasal 18 ayat (1)", "sebesar 0,30% (nol"), BPJS_START, label_id="iuran JKM"),
        rule("REG.BPJS.JKM", "jkm_premium", f"round(param('jkm_rate') * bpjs_wage, 1, {ROUND})",
             q("Pasal 18 ayat (1)", "Iuran JKM bagi Peserta penerima Upah sebagaimana"), BPJS_START, cond=NOT_BILLED),
    ]


def _pp46():
    q = P46.q
    return [
        param("PAR.JHT_EMPLOYEE_RATE.2015", "jht_employee_rate", "0.02", "rate",
              q("Pasal 16 ayat (1) huruf a", "a. 2% (dua persen) ditanggung oleh Pekerja; dan"), BPJS_START,
              label_id="iuran JHT pekerja"),
        rule("REG.BPJS.JHT_EMPLOYEE", "jht_employee", f"round(param('jht_employee_rate') * bpjs_wage, 1, {ROUND})",
             q("Pasal 16 ayat (1)", "sebesar 5,7% (lima koma tujuh persen) dari Upah,"), BPJS_START, cond=NOT_BILLED),
    ]


def _pp45():
    q = P45.q
    return [
        param("PAR.JP_EMPLOYEE_RATE.2015", "jp_employee_rate", "0.01", "rate",
              q("Pasal 28 ayat (3) huruf b", "b. 1% (satu persen) dari upah ditanggung oleh"), BPJS_START,
              label_id="iuran jaminan pensiun pekerja"),
        param("PAR.JP_WAGE_CAP.2015", "jp_wage_cap", 7000000, "money",
              q("Pasal 29 ayat (2)", "tahun 2015 ditetapkan sebesar Rp7.000.000,00"), BPJS_START,
              label_id="batas upah tertinggi jaminan pensiun"),
        rule("REG.BPJS.JP_WAGE", "jp_wage", "min(bpjs_wage, param('jp_wage_cap'))",
             q("Pasal 29 ayat (2)", "Batas paling tinggi Upah yang digunakan sebagai"), BPJS_START),
        rule("REG.BPJS.JP_EMPLOYEE", "jp_employee", f"round(param('jp_employee_rate') * jp_wage, 1, {ROUND})",
             q("Pasal 28 ayat (3)", "oleh Pemberi Kerja selain penyelenggara negara dan"), BPJS_START, cond=NOT_BILLED),
    ]


def _pmk101():
    q = PMK101.q
    return [table("TAB.PTKP.2016", "ptkp", "lookup",
                  [q("Pasal 1 huruf a", "a. Rp54.000.000,00 (lima puluh empat juta rupiah) untuk"),
                   q("Pasal 1 huruf b", "b. Rp4.500.000,00 (empat juta lima ratus ribu rupiah)"),
                   q("Pasal 3", "berlaku pada Tahun Pajak 2016.")],
                  "2016-01-01", label_id="penghasilan tidak kena pajak",
                  rows=[{"key": k, "value": v} for k, v in [
                      ("TK/0", 54000000), ("TK/1", 58500000), ("TK/2", 63000000), ("TK/3", 67500000),
                      ("K/0", 58500000), ("K/1", 63000000), ("K/2", 67500000), ("K/3", 72000000)]])]


def _jkn82():
    q = JKN82.q
    start = "2018-10-01"
    rates = q("Pasal 30 ayat (2)", "a. 4% (empat persen) dibayar oleh Pemberi Kerja;")
    return [
        param("PAR.HEALTH_EMPLOYER_RATE.2018", "health_employer_rate", "0.04", "rate", rates, start,
              label_id="iuran jaminan kesehatan pemberi kerja"),
        param("PAR.HEALTH_EMPLOYEE_RATE.2018", "health_employee_rate", "0.01", "rate",
              q("Pasal 30 ayat (2) huruf b", "b. 1 % (satu persen) dibayar oleh Peserta."), start,
              label_id="iuran jaminan kesehatan pegawai"),
        param("PAR.HEALTH_WAGE_CAP.2018", "health_wage_cap", 8000000, "money",
              q("Pasal 32 ayat (1)", "Rp8.000.000,00 (delapan juta rupiah)."), start,
              label_id="batas upah jaminan kesehatan"),
    ]


def _jkn75():
    q = JKN75.q
    return [param("PAR.HEALTH_WAGE_CAP.2020", "health_wage_cap", 12000000, "money",
                  [q("Pasal 32 ayat (1)", "Rp12.000.000,00 (dua belas juta rupiah)."),
                   q("Pasal 103B ayat (2) huruf b", "bagi Peserta PPU untuk pegawai swasta")],
                  "2020-01-01", label_id="batas upah jaminan kesehatan")]


def _hpp():
    q = HPP.q
    return [table("TAB.PASAL17.2022", "pasal17", "progressive",
                  [q("Pasal I angka 4, Pasal 17 ayat (1) huruf a", "Tarif pajak yang diterapkan atas Penghasilan Kena"),
                   q("Pasal I angka 4, Pasal 17 ayat (1) huruf a", "Rp60.000.000,00 (enam (lima persen)"),
                   q("Pasal I angka 4, Pasal 17 ayat (1) huruf a", "di atas Rp250.000.000,00 25o/o"),
                   q("Pasal I angka 4, Pasal 17 ayat (1) huruf a", "(lima miliar rupiah)"),
                   q("Pasal I angka 4, Pasal 17 ayat (1) huruf b", "yang mulai berlaku pada tahun pajak 2022.")],
                  "2022-01-01", label_id="tarif Pasal 17",
                  rows=[{"lower": 0, "upper": 60000000, "rate": "0.05"},
                        {"lower": 60000000, "upper": 250000000, "rate": "0.15"},
                        {"lower": 250000000, "upper": 500000000, "rate": "0.25"},
                        {"lower": 500000000, "upper": 5000000000, "rate": "0.30"},
                        {"lower": 5000000000, "upper": None, "rate": "0.35"}])]


def _jp2022():
    q = JP23.q
    return [param("PAR.JP_WAGE_CAP.2022", "jp_wage_cap", 9077600, "money",
                  q("angka 4", "= 9.077.600 x ( 1 + 5,31 / 100 )"), "2022-03-01",
                  label_id="batas upah tertinggi jaminan pensiun")]


UPDATES = [
    Update("BG-002", P44, "background", add=_pp44()),
    Update("BG-003", P46, "background", add=_pp46()),
    Update("BG-004", P45, "background", add=_pp45()),
    Update("BG-005", PMK101, "background", add=_pmk101()),
    Update("BG-006", JKN82, "background", add=_jkn82(),
           note="JKN rates and wage cap as restated by Perpres 82/2018 (same values as before). The JKN rules come "
                "from development events D02 (Perpres 111/2013) and D04 (Perpres 19/2016). valid_from set to the "
                "first full month after promulgation."),
    Update("BG-007", JKN75, "background", add=_jkn75()),
    Update("BG-008", HPP, "background", add=_hpp()),
    Update("BG-009", JP23, "background", add=_jp2022(), recorded_on="2022-03-01",
           note=("JP wage cap 2022 (tafsir K11). The 2022 BPJS letter is not available; the value is quoted from the "
                 "2023 letter (E01), which states it as the base of the 2023 adjustment. Recorded 2022-03-01, before "
                 "the test range, so it is known to every test event.")),
]
