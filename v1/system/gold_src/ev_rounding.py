"""Gold Delta of E13, PER-11/PJ/2025: PPh 21 on withholding slips is rounded to the nearest whole rupiah (0.50 up)
from Masa Januari 2025 (change type T2 on a parameter; tafsir K1, tafsir_korpus B5).

Pasal 130 keeps the old slip rules for periods up to Masa Desember 2024, so the new rounding applies from Masa Januari
2025 although the regulation was issued on 22 May 2025: the values of January-April 2025 known before that date were
truncated, and the values they should have are rounded half up (retroactive, B5).
"""
from . import Doc, Update, param

D = Doc("PER-11-PJ-2025")


def _delta():
    q = D.q
    src = [q("Pasal 129 ayat (1)", "diisi dengan pembulatan ke dalam rupiah penuh."),
           q("Pasal 129 ayat (3) huruf b", "b. sama dengan atau lebih dari 0,50 (nol koma lima"),
           q("Pasal 129 ayat (3) huruf b", "nol), maka bilangan tersebut dibulatkan ke atas."),
           q("Pasal 130 huruf a", "dengan Masa Pajak Desember 2024, oleh Pemotong Pajak")]
    return [param("PAR.PPH_ROUND_MODE.2025", "pph_round_mode", "half_up", "category", src, "2025-01-01",
                  label_id="pembulatan PPh Pasal 21 masa")]


UPDATES = [Update("GOLD-E13", D, "event", event_id="E13", add=_delta())]
