"""Gold Deltas of E03 (PP 58/2023) and E04 (PMK 168/2023): the effective-rate (TER) method from Masa Januari 2024
(change types T2, T7, T3; tafsir_korpus A5 splits the two documents).

E03 adds the TER categories, the monthly TER table (extracted table of Lampiran A-C), and the rule that periods other
than the final one are withheld at TER x gross; the final period keeps Pasal 17 (already in the chain). E04 closes
the annualised-method rules on 2023-12-31 (PMK 168 Pasal 24 revokes PMK 252/PMK.03/2008) and makes zakat paid through
the employer a deduction (Pasal 10 ayat (1) huruf c).
"""
from . import Doc, Update, fact, rule, table

PP58 = Doc("PP-58-2023")
PMK168 = Doc("PMK-168-2023")
VF = "2024-01-01"


def _e03():
    q = PP58.q
    cat = [q("Pasal 2 ayat (3)", "huruf a dikategorikan berdasarkan besarnya Penghasilan"),
           q("Pasal 2 ayat (4) huruf a", "kategori A diterapkan atas penghasilan bruto bulanan"),
           q("Pasal 2 ayat (4) huruf b", "kategori B diterapkan atas penghasilan bruto bulanan"),
           q("Pasal 2 ayat (4) huruf c", "dengan jumlah tanggungan sebanyak 3 (tiga) orang.")]
    monthly = [q("Penjelasan Pasal 2 ayat (1)", "sampai November 2024 dilakukan dengan menggunakan tarif"),
               q("Penjelasan Pasal 2 ayat (1)", "atau diperoleh Tuan R untuk masa pajak Januari 2024")]
    lampiran = q("Pasal 2 ayat (5)", "tarif dimaksud sebagaimana tercantum dalam Lampiran")
    start = q("Penjelasan Pasal 2 ayat (1)", "atau diperoleh Tuan R untuk masa pajak Januari 2024")
    cat, lampiran = cat + [start], [lampiran, start]
    return [
        fact("ter_category", "category", "year", cat, label="TER category", label_id="kategori tarif efektif bulanan"),
        fact("ter_rate", "rate", "period", lampiran[:1], label="monthly effective rate", label_id="tarif efektif bulanan"),
        table("TAB.TER_CATEGORY.2024", "ter_category", "lookup", cat, VF, label_id="kategori tarif efektif",
              rows=[{"key": k, "value": v} for k, v in [
                  ("TK/0", "A"), ("TK/1", "A"), ("K/0", "A"), ("TK/2", "B"), ("TK/3", "B"), ("K/1", "B"),
                  ("K/2", "B"), ("K/3", "C")]]),
        table("TAB.TER_MONTHLY.2024", "ter_monthly", "bracket", lampiran, VF, label_id="tarif efektif bulanan",
              rows_ref={"extracted_table": "PP-58-2023/LAMPIRAN-ABC",
                        "columns": {"key": "kategori", "lower": "batas_bawah", "upper": "batas_atas",
                                    "value": "tarif_persen"},
                        "value_scale": "percent"}),
        rule("REG.TER.CATEGORY", "ter_category", "lookup('ter_category', ptkp_status_effective)", cat, VF,
             scope="year"),
        rule("REG.TER.RATE", "ter_rate", "bracket('ter_monthly', ter_category, gross_income)", lampiran + monthly,
             VF, cond="not is_final_period"),
        rule("REG.TER.RUNNING", "pph21_running", "round(ter_rate * gross_income, 1, param('pph_round_mode'))",
             monthly + [q("Penjelasan Pasal 2 ayat (1)", "Januari sampai November 2024 adalah sebesar")], VF,
             cond="not is_final_period"),
    ]


P16_RULES = ["REG.P16.JOB_EXPENSE_MONTH", "REG.P16.NET_MONTH", "REG.P16.FACTOR", "REG.P16.FACTOR.NEW_EMPLOYEE",
             "REG.P16.FACTOR.KNOWN_END",
             "REG.P16.TAXABLE_ANNUALIZED", "REG.P16.PPH_ANNUAL", "REG.P16.PPH_MONTH",
             "REG.P16.TAXABLE_WITH_IRREGULAR", "REG.P16.TAXABLE_WITHOUT_IRREGULAR", "REG.P16.PPH_IRREGULAR",
             "REG.P16.PPH_IRREGULAR.NONE", "REG.P16.RUNNING"]


def _e04(chain_records):
    q = PMK168.q
    revoke = [q("Pasal 24 huruf b", "b. Peraturan Menteri Keuangan Nomor 252/PMK.03/2008"),
              q("Pasal 25", "Peraturan Menteri ini mulai berlaku pada tanggal 1 Januari 2024.")]
    changes = []
    for rid in P16_RULES:
        old = dict(chain_records[rid])
        old["valid_until"] = "2023-12-31"
        old["source"] = old["source"] + revoke
        old.pop("recorded_on", None)
        changes.append(old)
    add = [rule("REG.ZAKAT.DEDUCTIBLE", "zakat_deductible", "zakat_withheld",
                [q("Pasal 10 ayat (1) huruf c", "c. zakat atau sumbangan keagamaan yang sifatnya"),
                 q("Pasal 10 ayat (1) huruf c", "yang dibayarkan melalui pemberi kerja kepada badan"),
                 q("Pasal 25", "Peraturan Menteri ini mulai berlaku pada tanggal 1 Januari 2024.")], VF)]
    return add, changes


def _base_records():
    from .bg_base import BG001
    return {e["id"]: e for e in BG001.add}


E03 = Update("GOLD-E03", PP58, "event", event_id="E03", add=_e03())
_add, _change = _e04(_base_records())
E04 = Update("GOLD-E04", PMK168, "event", event_id="E04", add=_add, change=_change,
             note="Closing the annualised-method rules is hygiene: the TER rule from E03 already wins from 2024 by "
                  "lex posterior (later valid_from).")
UPDATES = [E03, E04]
