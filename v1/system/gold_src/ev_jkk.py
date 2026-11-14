"""Gold Deltas of E07 (PP 7/2025) and E09 (PP 36/2025): 50% relief of the JKK contribution for certain
labour-intensive industries, contribution months February-July 2025, extended to January 2026 (change type T1;
tafsir K7, tafsir_korpus B2).

The relief is a separate rate table read by a rule that applies only to employers verified as eligible
(employer('jkk_relief_eligible'), PP 7/2025 Pasal 5 ayat (2)). It wins over the normal rate by lex posterior; employers
that are not eligible keep the normal rule because the relief rule's condition is false. The premium in gross income is
the relief premium of the contribution month (accrual), whatever was paid at first (B2).
"""
from . import Doc, Update, rule, table

PP7, PP36 = Doc("PP-7-2025"), Doc("PP-36-2025")
VF, VU, VU2 = "2025-02-01", "2025-07-31", "2026-01-31"
ELIGIBLE = "employer('jkk_relief_eligible') == True"


def _e07():
    q = PP7.q
    rates = [q("Pasal 4 ayat (1)", "Keringanan Iuran JKK diberikan sebesar 50% (lima puluh"),
             q("Pasal 4 ayat (1) huruf a", "(nol koma satu dua nol persen) dari Upah sebulan;"),
             q("Pasal 4 ayat (1) huruf b", "(nol koma dua tujuh nol persen) dari Upah sebulan;"),
             q("Pasal 4 ayat (1) huruf c", "(nol koma empat empat lima persen) dari Upah sebulan;"),
             q("Pasal 4 ayat (1) huruf d", "(nol koma enam tiga lima persen) dari Upah sebulan; dan"),
             q("Pasal 4 ayat (1) huruf e", "diberikan keringanan sehingga menjadi 0,870% (nol")]
    period = q("Pasal 10", "berlaku untuk Iuran JKK bulan Februari 2O25 sampai dengan Iuran JKK bulan Juli 2O25.")
    who = [q("Pasal 3 ayat (1)", "Perusahaan industri padat karya tertentu."),
           q("Pasal 5 ayat (2)", "pada ayat (1) dilakukan melalui verifikasi terhadap")]
    return [
        table("TAB.JKK_RATES_RELIEF.2025", "jkk_rates_relief", "lookup", rates + [period], VF, vu=VU,
              label_id="tarif iuran JKK setelah keringanan",
              rows=[{"key": "very_low", "value": "0.0012"}, {"key": "low", "value": "0.0027"},
                    {"key": "medium", "value": "0.00445"}, {"key": "high", "value": "0.00635"},
                    {"key": "very_high", "value": "0.0087"}]),
        rule("REG.BPJS.JKK_RATE.RELIEF", "jkk_rate", "lookup('jkk_rates_relief', employer('jkk_risk_group'))",
             rates[:1] + [period] + who, VF, vu=VU, cond=ELIGIBLE,
             label="tafsir K7: the relief rate is the premium of the contribution month"),
    ]


def _e09(e07):
    q = PP36.q
    ext = [q("Pasal I angka 2, Pasal 10A", "dilakukan perpanjangan sampai dengan Iuran JKK"),
           q("Pasal I angka 2, Pasal 10A", "perpanjangan sampai dengan Iuran JKK bulan Januari 2026.")]
    change = []
    for rec in e07:
        r = dict(rec)
        r["valid_until"] = VU2
        r["source"] = list(r["source"]) + ext
        change.append(r)
    return change


_E07 = _e07()
UPDATES = [
    Update("GOLD-E07", PP7, "event", event_id="E07", add=_E07),
    Update("GOLD-E09", PP36, "event", event_id="E09", change=_e09(_E07)),
]
