"""Gold Deltas of the COVID-19 PPh 21 DTP incentives (development events D05-D07, D10, D11) and the empty Deltas of
D08, D12, D13 (relevant = false; tafsir_korpus A6 and peristiwa.csv).

D05 PMK 23/PMK.03/2020: PPh 21 of employees of employers with a KLU in Lampiran huruf A (440 codes) or a KITE
company, with an NPWP and fixed regular gross income annualised <= Rp200.000.000 in the period, is borne by the
government for Masa April-September 2020 (T4). D06 PMK 44/PMK.03/2020 (issued 27 April 2020, retroactive to April)
replaces it: 1.062 KLU codes, bonded-zone companies added, over-withholding from DTP not refunded (T5). D07 PMK
86/PMK.03/2020: 1.189 codes and extension to Masa Desember 2020 (T6, T5). D10 PMK 9/PMK.03/2021 (issued 2 February
2021, retroactive): new facility Masa Januari-Juni 2021, same 1.189 codes (T4). D11 PMK 82/PMK.03/2021: extension to
Masa Desember 2021, from July only for employers whose KLU is in its Lampiran (KITE and bonded-zone companies no
longer qualify, Pasal 18 ayat (5)) (T6).

Interpretations (development only; recorded for the second reader):
- Fixed regular income for the Rp200 juta criterion = base salary + fixed allowances + other regular income + tax
  allowance (Lampiran B: Tuan C's THR excluded, Tuan D's tax allowance included; overtime and employer premiums
  excluded as in tafsir K5).
- The DTP of a non-final period is the PPh 21 on regular income only (Lampiran B, Tuan C: DTP 925.833 = tax on
  salary; the tax on THR is withheld). In the final period the DTP is the PPh 21 of the period when positive (the
  examples do not cover the final period; the PMKs make "PPh Pasal 21" of the period DTP).
- DTP is paid in cash also when the employer gives a tax allowance or bears the tax (Pasal 2 ayat (4)/(5)): no change
  to gross-up, unlike PMK 10/2025.
- Over-withholding at the final period that comes from DTP periods is not refunded to the employee (PMK 44, 86, 9
  Pasal 2 ayat (8), same reading as tafsir K13 for 2025).
- The notification to the tax office (Pasal 3) and its start month are not modelled; employers are taken to have
  notified from the first month of the facility. KITE and bonded-zone status are case attributes
  employer('kite') and employer('bonded_zone').
"""
from . import Doc, Update, fact, param, rule, table

P23, P44, P86 = Doc("PMK-23-PMK-03-2020"), Doc("PMK-44-PMK-03-2020"), Doc("PMK-86-PMK-03-2020")
P110, P9, P82 = Doc("PMK-110-PMK-03-2020"), Doc("PMK-9-PMK-03-2021"), Doc("PMK-82-PMK-03-2021")
P149, P3 = Doc("PMK-149-PMK-03-2021"), Doc("PMK-3-PMK-03-2022")

VF20, VU20A, VU20B = "2020-04-01", "2020-09-30", "2020-12-31"
VF21, VU21A, VU21B = "2021-01-01", "2021-06-30", "2021-12-31"
INCOME = "covid_dtp_fixed_income * 12 <= param('covid_dtp_income_cap') and employee('tax_id_valid') != False"
REFUND = "max(0, 0 - final_period_tax - sum_periods_before_final('pph21_dtp'))"


def _dated(elements, *quotes):
    """Every element with a validity also cites the provision that sets its period (gate G2 grounds dates per
    element)."""
    for e in elements:
        if e.get("valid_from") or e.get("valid_until"):
            e["source"] = list(e["source"]) + [q for q in quotes if q not in e["source"]]
    return elements


def _klu_table(tid, doc, header, vf, vu):
    return table(tid, "covid_dtp_klu", "set", header, vf, vu=vu, label_id="KLU penerima PPh 21 DTP",
                 rows_ref={"extracted_table": f"{doc.id}/LAMPIRAN-A", "columns": {"key": "klu"}})


def _d05():
    q = P23.q
    klu = q("Pasal 2 ayat (1) huruf a angka 1",
            "memiliki kode Klasifikasi Lapangan Usaha sebagaimana tercantum dalam Lampiran huruf A")
    kite = q("Pasal 2 ayat (1) huruf a angka 2", "telah ditetapkan sebagai Perusahaan KITE")
    npwp = q("Pasal 2 ayat (1) huruf b", "b. memiliki NPWP; dan")
    cap = q("Pasal 2 ayat (1) huruf c", "Penghasilan Bruto yang bersifat tetap dan teratur yang disetahunkan tidak"
                                        " lebih dari Rp200.000.000,00 (dua ratus juta rupiah)")
    borne = q("Pasal 2 ayat (2)", "sebagaimana dimaksud pada ayat (1), ditanggung Pemerintah.")
    period = q("Pasal 2 ayat (6)", "diberikan sejak Masa Pajak April 2020 sampai dengan Masa Pajak September 2020.")
    cash = q("Pasal 2 ayat (4)", "dibayarkan secara tunai oleh pemberi kerja pada saat pembayaran penghasilan kepada"
                                 " Pegawai, termasuk dalam hal pemberi kerja memberikan tunjangan PPh Pasal 21")
    ex_c = q("Lampiran huruf B angka III", "Tuan C yang dapat memperoleh insentif PPh Pasal 21 DTP hanya atas"
                                           " penghasilan gaji dan tunjangan bulanan.")
    ex_d = q("Lampiran huruf B angka IV", "Penghasilan bruto Tuan D yang disetahunkan Rp192.000.000,00")
    header = [klu, q("Lampiran huruf A", "A. KODE KLASIFIKASI LAPANGAN USAHA (KLU) WAJIB PAJAK YANG")]
    return _dated([
        fact("covid_dtp_fixed_income", "money", "period", [cap, ex_c, ex_d],
             label="fixed regular income for the COVID DTP criterion", label_id="penghasilan bruto tetap dan teratur"),
        fact("covid_dtp_eligible", "bool", "period", [klu, kite, npwp, cap], label="employee eligible for COVID DTP",
             label_id="pegawai penerima PPh 21 DTP"),
        param("PAR.COVID_DTP_INCOME_CAP.2020", "covid_dtp_income_cap", 200000000, "money", cap, VF20, vu=VU20A,
              label_id="batas penghasilan bruto disetahunkan"),
        _klu_table("TAB.COVID_DTP_KLU.2020", P23, header, VF20, VU20A),
        rule("REG.COVID_DTP.FIXED_INCOME", "covid_dtp_fixed_income",
             "base_salary + fixed_allowance + other_regular_income + tax_allowance", [cap, ex_c, ex_d], VF20, vu=VU20A),
        rule("REG.COVID_DTP.ELIGIBLE", "covid_dtp_eligible",
             f"(in_table('covid_dtp_klu', employer('klu')) or employer('kite') == True) and {INCOME}",
             [klu, kite, npwp, cap, period], VF20, vu=VU20A),
        rule("REG.COVID_DTP.RUNNING", "pph21_dtp", "pph_regular_month if covid_dtp_eligible else 0",
             [borne, period, ex_c, cash], VF20, vu=VU20A, cond="not is_final_period",
             label="DTP covers the PPh 21 on regular income; tax on THR and bonus is withheld"),
        rule("REG.COVID_DTP.THP_CASH", "employee_tax_burden", "0 - pph21_dtp", [cash, period], VF20, vu=VU20A,
             cond="covid_dtp_eligible and withholding_method == 'employer_borne'",
             label="Pasal 2 ayat (4): the DTP is paid in cash also when the employer bears the tax"),
        rule("REG.COVID_DTP.FINAL", "pph21_dtp", "max(0, final_period_tax) if covid_dtp_eligible else 0",
             [borne, period], VF20, vu=VU20A, cond="is_final_period",
             label="interpretation: DTP of the final period is its PPh 21 when positive"),
    ], period)


def _d06(d05):
    q = P44.q
    zone = q("Pasal 2 ayat (3) huruf a angka 3", "telah mendapatkan izin Penyelenggara Kawasan Berikat, izin"
                                                 " Pengusaha Kawasan Berikat, atau izin PDKB")
    klu = q("Pasal 2 ayat (3) huruf a angka 1", "memiliki kode Klasifikasi Lapangan U saha sebagaimana tercantum"
                                                " dalam Lampiran huruf A")
    kite = q("Pasal 2 ayat (3) huruf a angka 2", "telah ditetapkan sebagai Perusahaan KITE")
    cap = q("Pasal 2 ayat (3) huruf c", "Penghasilan Bruto yang bersifat tetap dan teratur yang disetahunkan tidak"
                                        " lebih dari Rp200.000.000,00 (dua ratus juta rupiah)")
    period = q("Pasal 2 ayat (9)", "diberikan sejak Masa Pajak April 2020 sampai dengan Masa Pajak September 2020.")
    refund = q("Pasal 2 ayat (8)", "kelebihan pembayaran yang berasal dari PPh Pasal 21 ditanggung Pemerintah tidak"
                                   " dapat dikembalikan.")
    revoke = q("Pasal 16", "Nomor 277), dicabut dan dinyatakan tidak berlaku.")
    base = {e["id"]: e for e in d05}
    tab = dict(base["TAB.COVID_DTP_KLU.2020"])
    tab.update(rows_ref={"extracted_table": f"{P44.id}/LAMPIRAN-A", "columns": {"key": "klu"}},
               source=[klu, q("Lampiran huruf A", "A. KODE KLASIFIKASI LAPANGAN USAHA (KLU) WAJIB PAJAK YANG"), revoke])
    tab.pop("recorded_on", None)
    elig = dict(base["REG.COVID_DTP.ELIGIBLE"])
    elig.update(expression="(in_table('covid_dtp_klu', employer('klu')) or employer('kite') == True"
                           f" or employer('bonded_zone') == True) and {INCOME}",
                source=[klu, kite, zone, cap, period, revoke])
    elig.pop("recorded_on", None)
    add = [rule("REG.COVID_DTP.REFUND", "refund_to_employee", REFUND, [refund, period], VF20, vu=VU20A, scope="year",
                overrides=["REG.YEAR.REFUND"],
                label="over-withholding that came from DTP periods is not refunded (as tafsir K13)")]
    return add, [tab, elig]


# REG.COVID_DTP.REFUND is a year rule: a year rule applies when its validity meets the employment span, so the
# 2020 version already covers every employee of tax year 2020 and extending it within 2020 (D07) or within 2021
# (D11) has no effect (gate G5 rejects such a change as vacuous). D10 extends it into 2021, which does matter.
EXTEND_2020 = ["TAB.COVID_DTP_KLU.2020", "PAR.COVID_DTP_INCOME_CAP.2020", "REG.COVID_DTP.FIXED_INCOME",
               "REG.COVID_DTP.ELIGIBLE", "REG.COVID_DTP.RUNNING", "REG.COVID_DTP.FINAL", "REG.COVID_DTP.THP_CASH"]


def _extend(latest, ids, vu, extra_source, **updates):
    out = []
    for rid in ids:
        r = dict(latest[rid])
        r["valid_until"] = vu
        r["source"] = list(r["source"]) + extra_source
        r.update(updates.get(rid, {}))
        r.pop("recorded_on", None)
        out.append(r)
    return out


def _d07(latest):
    q = P86.q
    period = q("Pasal 2 ayat (9)", "diberikan sejak Masa Pajak April 2020 sampai dengan Masa Pajak Desember 2020.")
    header = [q("Pasal 2 ayat (3) huruf a angka 1", "memiliki kode Klasifikasi Lapangan U saha sebagaimana tercantum"
                                                    " dalam Lampiran huruf"),
              q("Lampiran huruf A", "A. KODE KLASIFIKASI LAPANGAN USAHA (KLU) WAJIB PAJAK YANG")]
    revoke = q("Pasal 18", "Nomor 411), dicabut dan dinyatakan tidak berlaku.")
    tab_update = {"rows_ref": {"extracted_table": f"{P86.id}/LAMPIRAN-A", "columns": {"key": "klu"}},
                  "source": header + [period, revoke]}
    return _extend(latest, EXTEND_2020, VU20B, [period], **{"TAB.COVID_DTP_KLU.2020": tab_update})


def _d10(latest):
    q = P9.q
    period = q("Pasal 18 ayat (1)", "diberikan untuk Masa Pajak Januari 2021 sampai dengan Masa Pajak Juni 2021.")
    klu = q("Pasal 2 ayat (3) huruf a angka 1", "Yang Mendapatkan Insentif PPh Pasal 21")
    cap = q("Pasal 2 ayat (3) huruf c", "Penghasilan Bruto yang bersifat tetap dan teratur yang disetahunkan tidak"
                                        " lebih dari Rp 200.000.000,00 (dua ratus juta rupiah)")
    refund = q("Pasal 2 ayat (8)", "kelebihan pembayaran yang berasal dari PPh Pasal 21 ditanggung Pemerintah tidak"
                                   " dapat dikembalikan.")
    add = [
        param("PAR.COVID_DTP_INCOME_CAP.2021", "covid_dtp_income_cap", 200000000, "money", [cap, period], VF21,
              vu=VU21A, label_id="batas penghasilan bruto disetahunkan"),
        _klu_table("TAB.COVID_DTP_KLU.2021", P9,
                   [klu, q("Lampiran A", "A. KODE KLASIFIKASI LAPANGAN USAHA (KLU) WAJIB PAJAK YANG"), period],
                   VF21, VU21A),
    ]
    rules = ["REG.COVID_DTP.FIXED_INCOME", "REG.COVID_DTP.ELIGIBLE", "REG.COVID_DTP.RUNNING", "REG.COVID_DTP.FINAL",
             "REG.COVID_DTP.REFUND", "REG.COVID_DTP.THP_CASH"]
    change = _extend(latest, rules, VU21A, [period],
                     **{"REG.COVID_DTP.REFUND": {"source": list(latest["REG.COVID_DTP.REFUND"]["source"])
                                                 + [period, refund]}})
    return add, change


def _d11(latest):
    q = P82.q
    ext = [q("Pasal I angka 1, Pasal 18 ayat (3)", "dimaksud pada ayat (1) diperpanjang sampai dengan Masa Pajak"
                                                    " Desember 2021."),
           q("Pasal I angka 1, Pasal 18 ayat (5)", "Perpanjangan jangka waktu sebagaimana dimaksud pada ayat (3) dan"
                                                   " ayat (4) hanya berlaku untuk Pemberi Kerja")]
    klu = q("Pasal I angka 1, Pasal 18 ayat (5) huruf a angka 1", "1. kode Klasifikasi Lapangan U saha W ajib Pajak"
                                                                  " Yang Mendapatkan Insentif PPh Pasal 21")
    header = q("Lampiran A", "A. KODE KLASIFIKASI LAPANGAN USAHA WAJIB PAJAK YANG MENDAPATKAN INSENTIF PPh PASAL 21")
    vf = "2021-07-01"
    july = q("Pasal I angka 2, Pasal 19B ayat (1)", "dalam Pasal 12 ayat (1) sejak Masa Pajak Juli 2021")
    add = _dated([
        _klu_table("TAB.COVID_DTP_KLU.2021H2", P82, [klu, header] + ext, vf, VU21B),
        rule("REG.COVID_DTP.ELIGIBLE.2021H2", "covid_dtp_eligible",
             f"in_table('covid_dtp_klu', employer('klu')) and {INCOME}", [klu] + ext, vf, vu=VU21B,
             label="from July 2021 only employers with a listed KLU (KITE and bonded zones no longer qualify)"),
    ], july)
    change = _extend(latest, ["PAR.COVID_DTP_INCOME_CAP.2021", "REG.COVID_DTP.FIXED_INCOME", "REG.COVID_DTP.RUNNING",
                              "REG.COVID_DTP.FINAL", "REG.COVID_DTP.THP_CASH"], VU21B, ext)
    return add, change


def _empty(delta_id, doc, event_id, note):
    return Update(delta_id, doc, "event", event_id=event_id, relevant=False, note=note)


_D05 = _d05()
_latest = {e["id"]: e for e in _D05}
_D06_ADD, _D06_CHANGE = _d06(_D05)
_latest.update({e["id"]: e for e in _D06_ADD + _D06_CHANGE})
_D07 = _d07(_latest)
_latest.update({e["id"]: e for e in _D07})
_D10_ADD, _D10_CHANGE = _d10(_latest)
_latest.update({e["id"]: e for e in _D10_ADD + _D10_CHANGE})
_D11_ADD, _D11_CHANGE = _d11(_latest)

UPDATES = [
    Update("GOLD-D05", P23, "event", event_id="D05", add=_D05),
    Update("GOLD-D06", P44, "event", event_id="D06", add=_D06_ADD, change=_D06_CHANGE,
           note="Replaces PMK 23/2020 from Masa April 2020 (retroactive): KLU list 1.062 codes, bonded zones, "
                "DTP over-withholding not refunded."),
    Update("GOLD-D07", P86, "event", event_id="D07", change=_D07,
           note="Replaces PMK 44/2020: KLU list 1.189 codes and facility extended to Masa Desember 2020."),
    _empty("GOLD-D08", P110, "D08", "PMK 110/2020 restates the PPh 21 DTP provisions and KLU list of PMK 86/2020; "
                                    "no PPh 21 calculation changes."),
    Update("GOLD-D10", P9, "event", event_id="D10", add=_D10_ADD, change=_D10_CHANGE,
           note="New facility Masa Januari-Juni 2021 (retroactive, issued 2021-02-02); the rules continue from 2020."),
    Update("GOLD-D11", P82, "event", event_id="D11", add=_D11_ADD, change=_D11_CHANGE,
           note="Extension to Masa Desember 2021 for employers with a KLU in the new Lampiran only (Pasal 18 ayat "
                "(5)); REG.COVID_DTP.ELIGIBLE keeps its end date 2021-06-30. Re-notification (Pasal 19B) not modelled."),
    _empty("GOLD-D12", P149, "D12", "PMK 149/2021 restates Pasal 19B and the KLU list (1.189 codes); changes concern "
                                    "PPh 22 import, PPh 25, VAT and reporting deadlines only (tafsir_korpus A6)."),
    _empty("GOLD-D13", P3, "D13", "PMK 3/2022 revokes PMK 9/2021 after PPh 21 DTP ended in Masa Desember 2021; it "
                                  "grants no PPh 21 DTP for 2022."),
]
