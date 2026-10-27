"""Gold Deltas of the yearly JP wage-cap letters (E01, E05, E08, E12; change type T1).

Each letter sets the highest wage for the pension contribution from the March contribution month. The new value is a
new parameter element; the selection rule (latest valid_from) makes the previous year's value stop applying, so no
closing change is needed (representasi.md section 3).
"""
from . import Doc, Update, param

E01, E05, E08, E12 = (Doc("BPJSTK-JP-2023"), Doc("BPJSTK-JP-2024"), Doc("BPJSTK-JP-2025"), Doc("BPJSTK-JP-2026"))


def cap(doc, year, value, quotes):
    return param(f"PAR.JP_WAGE_CAP.{year}", "jp_wage_cap", value, "money", [doc.q(p, t) for p, t in quotes],
                 f"{year}-03-01", label_id="batas upah tertinggi jaminan pensiun")


UPDATES = [
    Update("GOLD-E01", E01, "event", event_id="E01", add=[cap(E01, 2023, 9559600, [
        ("angka 4", "Batas paling tinggi Upah sebagai dasar perhitungan iuran Jaminan Pensiun mulai bulan"),
        ("angka 4", "Maret 2023, dengan perhitungan:"),
        ("angka 4", "Dibulatkan menjadi 9.559.600")])]),
    Update("GOLD-E05", E05, "event", event_id="E05", add=[cap(E05, 2024, 10042300, [
        ("isi surat", "Jaminan Pensiun dari Rp 9.559.600 menjadi Rp. 10.042.300 di tahun 2024."),
        ("isi surat", "pembayaran iuran bulan Maret 2024.")])]),
    Update("GOLD-E08", E08, "event", event_id="E08", add=[cap(E08, 2025, 10547400, [
        ("angka 4", "dasar perhitungan iuran jaminan pensiun sebesar Rp 10.547.400,-"),
        ("angka 6", "berlaku per 1 Maret 2025.")])]),
    Update("GOLD-E12", E12, "event", event_id="E12", add=[cap(E12, 2026, 11086300, [
        ("angka 5", "Batas upah paling tinggi sebagai dasar perhitungan iuran Jaminan Pensiun mulai Maret"),
        ("angka 5", "Dibulatkan menjadi Rp11.086.300,00")])]),
]
