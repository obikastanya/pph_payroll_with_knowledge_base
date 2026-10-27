"""Gold Deltas of development events D01-D04 and D09 (before the test range; used to tune prompts and gates).

D01 PMK 162/PMK.011/2012 and D03 PMK 122/PMK.010/2015: PTKP tables 2013 and 2015 (T1; D03 retroactive to
Tahun Pajak 2015, issued 29 June 2015). D02 Perpres 111/2013: JKN contribution of employees from January 2014,
4,5% (4% employer, 0,5% employee) until June 2015 and 5% (4%/1%) from July 2015, on base salary and fixed allowances
up to 2 x PTKP K/1. D04 Perpres 19/2016: wage cap Rp8.000.000 from 1 March 2016 (Pasal 16D replaced). D09 PP 49/2020:
JKK and JKM contributions reduced to 1% of the normal contribution for contribution months August 2020 - January 2021
(retroactive, issued 1 September 2020) for employers that paid their contributions up to July 2020.

Interpretations:
- D02 Pasal 16D "2 (dua) kali PTKP dengan status kawin dengan 1 (satu) orang anak" is a monthly cap equal to
  2 x the annual PTKP K/1 / 12 (Rp4.725.000 with the 2013 PTKP, Rp7.000.000 with the 2015 PTKP). The cap follows the
  PTKP table valid on the contribution month, so D03 also changes the cap of 2015 retroactively.
- D02 wage base before July 2015 is base salary + fixed allowances read directly (Pasal 16E ayat (3)); the shared
  BPJS wage fact (PP 44/2015) starts in July 2015.
- D09 eligibility (Pasal 13: contributions up to July 2020 paid) is a case attribute employer('bpjs_relief_2020_eligible');
  the two-month wait of employers registering after July 2020 (Pasal 13 ayat (2)) is not modelled. The deferral of
  99% of the employer JP share (Pasal 17) does not change PPh 21: the employee JP contribution of 1% is still
  withheld, and the employer JP share is not gross income.
"""
from . import Doc, Update, param, rule, table

PMK162, PMK122 = Doc("PMK-162-PMK-011-2012"), Doc("PMK-122-PMK-010-2015")
JKN111, JKN19 = Doc("PERPRES-111-2013"), Doc("PERPRES-19-2016")
PP49 = Doc("PP-49-2020")
NOT_BILLED = "employer('premiums_as_billed') != True"
ROUND = "param('bpjs_round_mode')"


def _dated(elements, *quotes):
    """Every element with a validity also cites the provision that sets its period (gate G2 grounds dates per
    element)."""
    for e in elements:
        if e.get("valid_from") or e.get("valid_until"):
            e["source"] = list(e["source"]) + [q for q in quotes if q not in e["source"]]
    return elements


def _ptkp_rows(own, extra):
    return [{"key": k, "value": v} for k, v in [
        ("TK/0", own), ("TK/1", own + extra), ("TK/2", own + 2 * extra), ("TK/3", own + 3 * extra),
        ("K/0", own + extra), ("K/1", own + 2 * extra), ("K/2", own + 3 * extra), ("K/3", own + 4 * extra)]]


def _d01():
    q = PMK162.q
    return [table("TAB.PTKP.2013", "ptkp", "lookup",
                  [q("Pasal 1 huruf a", "a. Rp24.300.000,00 (dua puluh empat juta tiga ratus ribu rupiah) untuk diri"),
                   q("Pasal 1 huruf b", "b. Rp2.025.000,00 (dua juta dua puluh lima ribu rupiah) tambahan untuk Wajib"),
                   q("Pasal 1 huruf d", "paling banyak 3 (tiga) orang untuk setiap keluarga."),
                   q("Pasal 3", "mulai berlaku pada tanggal 1 Januari 2013.")],
                  "2013-01-01", label_id="penghasilan tidak kena pajak", rows=_ptkp_rows(24300000, 2025000))]


def _d03(d01):
    q = PMK122.q
    add = [table("TAB.PTKP.2015", "ptkp", "lookup",
                 [q("Pasal 1 huruf a", "a. Rp36.000.000,00 (tiga puluh enam juta rupiah) untuk diri Wajib"),
                  q("Pasal 1 huruf b", "b. Rp3.000.000,00 (tiga juta rupiah) tambahan untuk Wajib Pajak"),
                  q("Pasal 1 huruf d", "paling banyak 3 (tiga) orang untuk setiap keluarga."),
                  q("Pasal 3", "berlaku pada Tahun Pajak 2015.")],
                 "2015-01-01", label_id="penghasilan tidak kena pajak", rows=_ptkp_rows(36000000, 3000000))]
    closed = dict(d01[0])
    closed["valid_until"] = "2014-12-31"
    closed["source"] = list(closed["source"]) + [
        q("Pasal 4", "Penghasilan Tidak Kena Pajak, dicabut dan dinyatakan tidak berlaku."),
        q("Pasal 3", "berlaku pada Tahun Pajak 2015.")]
    closed.pop("recorded_on", None)
    return add, [closed]


def _d02():
    q = JKN111.q
    vf = "2014-01-01"
    rate1 = [q("Pasal 16C ayat (1)", "dibayarkan mulai tanggal 1 Januari 2014 sampai dengan 30 Juni 2015 sebesar 4,5%"),
             q("Pasal 16C ayat (1) huruf a", "a. 4% (empat persen) dibayar oleh Pemberi Kerja;")]
    emp1 = q("Pasal 16C ayat (1) huruf b", "b. 0,5% (nol koma lima persen) dibayar oleh Peserta.")
    rate2 = [q("Pasal 16C ayat (2)", "dibayarkan mulai tanggal 1 Juli 2015 sebesar 5%"),
             q("Pasal 16C ayat (2) huruf b", "b. 1% (satu persen) dibayar oleh Peserta.")]
    cap = [q("Pasal 16D", "Batas paling tinggi Gaji atau Upah per bulan yang digunakan sebagai dasar perhitungan"),
           q("Pasal 16D", "kali Penghasilan Tidak Kena Pajak (PTKP) dengan status kawin dengan 1 (satu) orang anak.")]
    wage = q("Pasal 16E ayat (3)", "Jaminan Kesehatan sebagaimana dimaksud dalam Pasal 16C terdiri atas Gaji atau Upah"
                                   " pokok dan tunjangan tetap.")
    return _dated([
        param("PAR.HEALTH_EMPLOYER_RATE.2014", "health_employer_rate", "0.04", "rate", rate1, vf,
              label_id="iuran jaminan kesehatan pemberi kerja"),
        param("PAR.HEALTH_EMPLOYEE_RATE.2014", "health_employee_rate", "0.005", "rate", [rate1[0], emp1], vf,
              vu="2015-06-30", label_id="iuran jaminan kesehatan pegawai"),
        param("PAR.HEALTH_EMPLOYEE_RATE.2015", "health_employee_rate", "0.01", "rate", rate2, "2015-07-01",
              label_id="iuran jaminan kesehatan pegawai"),
        rule("REG.JKN.WAGE.2014", "health_wage",
             "min(base_salary + fixed_allowance, round(2 * lookup('ptkp', 'K/1') / 12, 1, 'down'))", cap + [wage], vf,
             label="Pasal 16D: monthly cap 2 x PTKP K/1 / 12 of the PTKP table valid in the month"),
        rule("REG.JKN.EMPLOYER", "health_premium_employer",
             f"round(param('health_employer_rate') * health_wage, 1, {ROUND})", rate1, vf, cond=NOT_BILLED),
        rule("REG.JKN.EMPLOYEE", "health_employee",
             f"round(param('health_employee_rate') * health_wage, 1, {ROUND})", [emp1] + rate2[1:], vf,
             cond=NOT_BILLED),
    ], rate1[0])


def _d04(d02):
    q = JKN19.q
    vf = "2016-03-01"
    cap = [q("Pasal I angka 9, Pasal 16D", "Ketentuan Pasal 16D diubah sehingga berbunyi sebagai"),
           q("Pasal I angka 9, Pasal 16D", "dalam Pasal 16B ayat (1) sebesar Rp 8.000.000,00 (delapan juta rupiah)."),
           q("Pasal II", "Peraturan Presiden ini mulai berlaku pada tanggal diundangkan.")]
    add = [
        param("PAR.HEALTH_WAGE_CAP.2016", "health_wage_cap", 8000000, "money", cap, vf,
              label_id="batas upah jaminan kesehatan"),
        rule("REG.JKN.WAGE", "health_wage", "min(bpjs_wage, param('health_wage_cap'))", cap, vf),
    ]
    old = next(dict(e) for e in d02 if e["id"] == "REG.JKN.WAGE.2014")
    old["valid_until"] = "2016-02-29"
    old["source"] = list(old["source"]) + cap[:1]
    old.pop("recorded_on", None)
    return add, [old]


def _d09():
    q = PP49.q
    vf, vu = "2020-08-01", "2021-01-31"
    period = q("Pasal 26", "berlaku dimulai sejak Iuran Program Jaminan Sosial Ketenagakerjaan bulan Agustus 2O2O")
    who = q("Pasal 13 ayat (1)", "setelah melunasi Iuran JKK dan Iuran JKM sampai dengan bulan Juli 2O2O.")
    jkk = [q("Pasal 5", "Keringanan Iuran JKK diberikan sebesar 99% (sembilan puluh sembilan persen), sehingga Iuran JKK"),
           q("Pasal 6 huruf a", "tingkat risiko sangat rendah, yaitu sebesar lo/o (satu persen) dikali O,24oh")]
    jkm = q("Pasal 10", "Penerima Upah yaitu sebesar 1% (satu persen) dikali 0,30% (nol koma tiga puluh persen)")
    end = q("Pasal 26", "sampai dengan Iuran Program Jaminan Sosial Ketenagakerjaan bulan Januari 202t.")
    eligible = "employer('bpjs_relief_2020_eligible') == True"
    return _dated([
        rule("REG.BPJS.JKK_RATE.RELIEF2020", "jkk_rate",
             "lookup('jkk_rates', employer('jkk_risk_group')) * dec('0.01')", jkk + [period, who], vf, vu=vu,
             cond=eligible, label="Pasal 5-6: JKK contribution reduced to 1% of the PP 44/2015 contribution"),
        rule("REG.BPJS.JKM.RELIEF2020", "jkm_premium",
             f"round(param('jkm_rate') * dec('0.01') * bpjs_wage, 1, {ROUND})", [jkm, period, who], vf, vu=vu,
             cond=f"{NOT_BILLED} and {eligible}", label="Pasal 9-10: JKM contribution reduced to 1%"),
    ], period, end)


_D01 = _d01()
_D03_ADD, _D03_CHANGE = _d03(_D01)
_D02 = _d02()
_D04_ADD, _D04_CHANGE = _d04(_D02)

UPDATES = [
    Update("GOLD-D01", PMK162, "event", event_id="D01", add=_D01),
    Update("GOLD-D02", JKN111, "event", event_id="D02", add=_D02),
    Update("GOLD-D03", PMK122, "event", event_id="D03", add=_D03_ADD, change=_D03_CHANGE,
           note="Retroactive to Tahun Pajak 2015 (issued 2015-06-29). Closing the 2013 table is hygiene: the 2015 "
                "table already wins from 2015 by lex posterior."),
    Update("GOLD-D04", JKN19, "event", event_id="D04", add=_D04_ADD, change=_D04_CHANGE),
    Update("GOLD-D09", PP49, "event", event_id="D09", add=_d09(),
           note="Retroactive to contribution month August 2020 (issued 2020-09-01). JP deferral (Pasal 17) has no "
                "PPh 21 effect; the Delta has none for it."),
]
