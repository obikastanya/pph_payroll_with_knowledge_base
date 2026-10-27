"""Gold Deltas of the PPh 21 DTP incentives: E06 (PMK 10/2025, labour-intensive industry, Masa Januari-Desember 2025,
retroactive), E10 (PMK 72/2025, adds tourism for Masa Oktober-Desember 2025, retroactive), E11 (PMK 105/2025,
both sectors for 2026). Tafsir K5 (fixed regular income), K13, tafsir_korpus B1 and B3.

One refund rule covers Pasal 5 ayat (5) and (5a): the over-withholding refunded to the employee is the part that the
government did not bear, max(0, over-withholding - DTP of the earlier periods). For labour-intensive employees every
period is DTP, so nothing is refunded (ayat (5)); for tourism employees DTP covers only October-November (ayat (5a)).
"""
from . import Doc, Update, fact, param, rule, table

P10, P72, P105 = Doc("PMK-10-2025"), Doc("PMK-72-2025"), Doc("PMK-105-2025")
VF, VU = "2025-01-01", "2025-12-31"
GROSSUP_RULES = ["REG.GROSSUP.RUNNING", "REG.GROSSUP.FINAL", "REG.BORNE.GROSSUP.RUNNING", "REG.BORNE.GROSSUP.FINAL"]


def _e06():
    q = P10.q
    period = q("Pasal 2 ayat (3)", "Pasal 21 ditanggung pemerintah sebagaimana dimaksud")
    period2 = q("Pasal 2 ayat (3)", "pada ayat (2) diberikan untuk Masa Pajak Januari 2025")
    klu = [q("Pasal 3 ayat (1) huruf b", "b. memiliki kode klasifikasi lapangan usaha"),
           q("Pasal 3 ayat (1) huruf a", "melakukan kegiatan usaha pada bidang industri:")]
    crit = [q("Pasal 4 ayat (2) huruf b", "bersifat tetap dan teratur tidak lebih dari"),
            q("Pasal 4 ayat (2) huruf b", "Rp10.000.000,00 (sepuluh juta rupiah) pada:"),
            q("Pasal 4 ayat (2) huruf b angka 1", "1. Masa Pajak Januari 2025, untuk Pegawai tertentu"),
            q("Pasal 4 ayat (2) huruf b angka 2", "2. Masa Pajak bulan pertama bekerja, untuk")]
    fixed = [q("Pasal 4 ayat (3) huruf a", "a. gaji dan tunjangan yang sifatnya tetap dan teratur"),
             q("Pasal 4 ayat (3) huruf b", "b. imbalan sejenis yang bersifat tetap dan teratur,")]
    npwp = q("Pasal 4 ayat (2) huruf a", "a. memiliki Nomor Pokok Wajib Pajak dan/atau Nomor")
    dtp = [q("Pasal 2 ayat (2)", "Pemberi Kerja dengan kriteria tertentu diberikan insentif"),
           q("Pasal 5 ayat (1)", "insentif yang harus dibayarkan secara tunai oleh Pemberi")]
    refund = q("Pasal 5 ayat (5)", "pemerintah tidak dikembalikan kepada Pegawai Tetap")
    no_gu = [q("Pasal 5 ayat (1)", "tunjangan Pajak Penghasilan Pasal 21 atau menanggung"),
             q("Pasal 5 ayat (2)", "dikenakan pajak.")]
    return [
        fact("dtp_fixed_income", "money", "period", fixed, label="fixed regular income for the DTP criterion",
             label_id="penghasilan bruto tetap dan teratur"),
        fact("dtp_income_test", "money", "year", crit, label="fixed regular income in January or the first month",
             label_id="penghasilan tetap bulan pertama"),
        fact("dtp_eligible", "bool", "year", klu + crit, label="employee eligible for DTP",
             label_id="pegawai tetap tertentu penerima insentif"),
        fact("dtp_facility", "bool", "period", [period, period2], label="DTP facility applies in this period",
             label_id="masa pajak insentif"),
        param("PAR.DTP_FIXED_INCOME_CAP.2025", "dtp_fixed_income_cap", 10000000, "money", crit[1], VF, vu=VU,
              label_id="batas penghasilan tetap dan teratur"),
        table("TAB.DTP_KLU.2025", "dtp_klu", "set", klu, VF, vu=VU, label_id="kode klasifikasi lapangan usaha",
              rows_ref={"extracted_table": "PMK-10-2025/LAMPIRAN-A", "columns": {"key": "klu", "sector": "sektor"}}),
        rule("REG.DTP.FIXED_INCOME", "dtp_fixed_income", "base_salary + fixed_allowance + other_regular_income",
             fixed, VF, vu=VU, label="tafsir K5: without employer premiums, incidental overtime, THR, bonus"),
        rule("REG.DTP.INCOME_TEST", "dtp_income_test", "value_in('dtp_fixed_income', first_month)", crit, VF,
             vu=VU, scope="year"),
        rule("REG.DTP.ELIGIBLE", "dtp_eligible",
             "in_table('dtp_klu', employer('klu')) and dtp_income_test <= param('dtp_fixed_income_cap')"
             " and employee('tax_id_valid') != False", klu + crit + [npwp], VF, vu=VU, scope="year"),
        rule("REG.DTP.FACILITY", "dtp_facility", "dtp_eligible", [period, period2], VF, vu=VU),
        rule("REG.DTP.RUNNING", "pph21_dtp", "pph21_due if dtp_facility else 0", dtp, VF, vu=VU,
             cond="not is_final_period"),
        rule("REG.DTP.FINAL", "pph21_dtp",
             "((final_period_tax if final_period_tax >= 0 else final_period_tax + refund_to_employee)"
             " if dtp_facility else 0)", dtp + [refund], VF, vu=VU, cond="is_final_period"),
        rule("REG.DTP.REFUND", "refund_to_employee",
             "max(0, 0 - final_period_tax - sum_periods_before_final('pph21_dtp'))", refund, VF, vu=VU,
             scope="year", cond="dtp_eligible", overrides=["REG.YEAR.REFUND"],
             label="tafsir K13: over-withholding that came from DTP is not refunded"),
        rule("REG.DTP.NO_GROSSUP", "tax_allowance", "0", no_gu, VF, vu=VU,
             cond="dtp_facility and withholding_method in ('gross_up', 'employer_borne')",
             overrides=GROSSUP_RULES,
             label="DTP is paid in cash and is not income; the employer bears no tax to gross up"),
    ]


def _e10():
    q = P72.q
    tour_period = [q("Pasal I angka 4, Pasal 4A huruf b", "b. Masa Pajak Oktober 2025 sampai dengan Masa Pajak"),
                   q("Pasal I angka 4, Pasal 4A huruf b", "Desember 2025, bagi Pegawai tertentu dari Pemberi")]
    klu = [q("Pasal I angka 2, Pasal 3 ayat (1) huruf a angka 5", "5. pariwisata; dan"),
           q("Pasal I angka 2, Pasal 3 ayat (1) huruf b", "b. memiliki kode klasifikasi lapangan usaha")]
    refund = [q("Pasal I angka 5, Pasal 5 ayat (5a)", "(5a) Dikecualikan dari ketentuan ayat (5), untuk Pegawai"),
              q("Pasal I angka 5, Pasal 5 ayat (5a)", "kelebihan pemotongan pajak yang tidak")]
    vf = "2025-10-01"
    return [
        fact("dtp_eligible_tourism", "bool", "year", klu + tour_period, label="employee eligible for tourism DTP",
             label_id="pegawai tertentu sektor pariwisata"),
        table("TAB.DTP_KLU_TOURISM.2025", "dtp_klu_tourism", "set", klu, vf, vu=VU,
              label_id="kode klasifikasi lapangan usaha pariwisata",
              rows_ref={"extracted_table": "PMK-72-2025/LAMPIRAN-A", "columns": {"key": "klu", "sector": "sektor"},
                        "filter": {"sektor": "pariwisata"}}),
        rule("REG.DTP.ELIGIBLE.TOURISM", "dtp_eligible_tourism",
             "in_table('dtp_klu_tourism', employer('klu')) and dtp_income_test <= param('dtp_fixed_income_cap')"
             " and employee('tax_id_valid') != False", klu + tour_period, vf, vu=VU, scope="year"),
        rule("REG.DTP.FACILITY.TOURISM", "dtp_facility", "dtp_eligible or dtp_eligible_tourism", tour_period, vf,
             vu=VU, overrides=["REG.DTP.FACILITY"]),
    ], [
        rule("REG.DTP.REFUND", "refund_to_employee",
             "max(0, 0 - final_period_tax - sum_periods_before_final('pph21_dtp'))",
             [P10.q("Pasal 5 ayat (5)", "pemerintah tidak dikembalikan kepada Pegawai Tetap")] + refund, VF, vu=VU,
             scope="year", cond="dtp_eligible or value_or('dtp_eligible_tourism', False)",
             overrides=["REG.YEAR.REFUND"],
             label="Pasal 5 ayat (5) and (5a): only the part not borne by the government is refunded"),
    ]


def _e11(e06_rules):
    q = P105.q
    vf, vu = "2026-01-01", "2026-12-31"
    period = [q("Pasal 2 ayat (3)", "pada ayat (2) diberikan untuk Masa Pajak Januari 2026"),
              q("Pasal 2 ayat (3)", "sampai dengan Masa Pajak Desember 2026.")]
    klu = [q("Pasal 3 ayat (1) huruf a angka 5", "5. pariwisata; dan"),
           q("Pasal 3 ayat (1) huruf b", "b. memiliki kode klasifikasi lapangan usaha")]
    crit = [q("Pasal 4 ayat (2) huruf b", "Rp10.000.000,00 (sepuluh juta rupiah) pada:"),
            q("Pasal 4 ayat (2) huruf b angka 1", "1. Masa Pajak Januari 2026, untuk Pegawai tertentu")]
    add = [
        param("PAR.DTP_FIXED_INCOME_CAP.2026", "dtp_fixed_income_cap", 10000000, "money", crit, vf, vu=vu,
              label_id="batas penghasilan tetap dan teratur"),
        table("TAB.DTP_KLU.2026", "dtp_klu", "set", klu, vf, vu=vu, label_id="kode klasifikasi lapangan usaha",
              rows_ref={"extracted_table": "PMK-105-2025/LAMPIRAN-A", "columns": {"key": "klu", "sector": "sektor"}}),
    ]
    change = []
    for rid in ["REG.DTP.FIXED_INCOME", "REG.DTP.INCOME_TEST", "REG.DTP.ELIGIBLE", "REG.DTP.FACILITY",
                "REG.DTP.RUNNING", "REG.DTP.FINAL", "REG.DTP.REFUND", "REG.DTP.NO_GROSSUP"]:
        r = dict(e06_rules[rid])
        r["valid_until"] = vu
        r["source"] = list(r["source"]) + period
        r.pop("recorded_on", None)
        change.append(r)
    return add, change


_E06 = _e06()
_E10_ADD, _E10_CHANGE = _e10()
_rules = {e["id"]: e for e in _E06}
_rules.update({e["id"]: e for e in _E10_CHANGE})
_E11_ADD, _E11_CHANGE = _e11(_rules)

UPDATES = [
    Update("GOLD-E06", P10, "event", event_id="E06", add=_E06),
    Update("GOLD-E10", P72, "event", event_id="E10", add=_E10_ADD, change=_E10_CHANGE),
    Update("GOLD-E11", P105, "event", event_id="E11", add=_E11_ADD, change=_E11_CHANGE),
]
