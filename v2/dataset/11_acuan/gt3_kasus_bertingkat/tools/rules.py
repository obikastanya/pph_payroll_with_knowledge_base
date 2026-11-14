"""GT3 rule helpers: parameters, citations, and exact arithmetic.

Independent of engine/, kb/, system/ and other project code. Values come only from
dataset/01_regulasi/tables/*.csv and the regulation PDFs cited in SRC.
All money arithmetic uses fractions.Fraction (exact).
"""
import csv
import math
import os
from fractions import Fraction as F

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
TABLES = os.path.join(ROOT, "dataset", "01_regulasi", "tables")

# ---------------------------------------------------------------- citations
SRC = {
    # PP 58/2023 (TER)
    "ter_kat": "PP 58/2023 Pasal 2 ayat (3)-(4), PDF hlm. 4",
    # PMK 168/2023
    "ter_masa": "PMK 168/2023 Pasal 15 ayat (1) huruf a, PDF hlm. 15; Lampiran B Bagian Pertama I.1 angka 1-2, PDF hlm. 28",
    "bruto_pt": "PMK 168/2023 Pasal 5 ayat (3) huruf a-b dan Pasal 8 ayat (2) huruf a, PDF hlm. 9-10",
    "jkk_jkm_obj": "PMK 168/2023 Pasal 5 ayat (3) huruf d, PDF hlm. 9",
    "jkn_obj": "PMK 168/2023 Pasal 5 ayat (3) huruf e, PDF hlm. 9",
    "iuran_pk_bukan": "PMK 168/2023 Pasal 7 huruf c, PDF hlm. 10",
    "bj": "PMK 168/2023 Pasal 10 ayat (1) huruf a dan ayat (2), PDF hlm. 11-12; bagian tahun: plafon n x Rp500.000 (contoh resmi PMK 168/2023 Lampiran B I.2.1.1, PDF hlm. 35-36; PMK 105/2025 Lampiran B nomor 3, PDF hlm. 41-43; tafsir K6)",
    "iuran_peng": "PMK 168/2023 Pasal 10 ayat (1) huruf b, PDF hlm. 11-12",
    "zakat": "PMK 168/2023 Pasal 10 ayat (1) huruf c, PDF hlm. 12; Lampiran B Bagian Pertama I.2 angka 5 huruf a, PDF hlm. 29",
    "neto": "PMK 168/2023 Pasal 8 ayat (5), PDF hlm. 11; Lampiran B Bagian Pertama I.2 angka 4-5, PDF hlm. 29",
    "ptkp": "UU 7/2021 (HPP) Pasal 3 angka 3 (Pasal 7 ayat (1) UU PPh), PDF hlm. 48; PMK 101/PMK.010/2016 Pasal 1, PDF hlm. 2-3",
    "ptkp_awal": "PMK 168/2023 Pasal 9 ayat (4), PDF hlm. 11; PP 58/2023 Pasal 2 ayat (3), PDF hlm. 4",
    "karyawati": "PMK 168/2023 Pasal 9 ayat (2) huruf a, PDF hlm. 11",
    "pkp": "PMK 168/2023 Pasal 8 ayat (3)-(4), PDF hlm. 10; Lampiran B Bagian Pertama I.2 angka 3, PDF hlm. 29",
    "tarif17": "UU 7/2021 (HPP) Pasal 3 angka 7 (Pasal 17 ayat (1) huruf a UU PPh), PDF hlm. 56; PMK 168/2023 Pasal 15 ayat (2), PDF hlm. 16",
    "masa_akhir": "PMK 168/2023 Pasal 15 ayat (1) huruf b, PDF hlm. 15; Lampiran B Bagian Pertama I.2 angka 1, PDF hlm. 28-29",
    "masa_akhir_def": "PMK 168/2023 Pasal 1 angka 18, PDF hlm. 4",
    "bagian_tahun": "PMK 168/2023 Lampiran B Bagian Pertama I.2 angka 6 huruf a, PDF hlm. 29",
    "lebih_potong": "PMK 168/2023 Lampiran B Bagian Pertama I.2 angka 7, PDF hlm. 30",
    "kenikmatan_pph": "PMK 168/2023 Lampiran B Bagian Kedua I.4 (PPh 21 ditanggung pemberi kerja = kenikmatan, objek, full gross up), PDF hlm. 44",
    "tunj_pajak": "PMK 168/2023 Pasal 5 ayat (3) huruf a (segala jenis tunjangan), PDF hlm. 9; Lampiran B Bagian Kedua I.5, PDF hlm. 45",
    "natura_obj_168": "PMK 168/2023 Pasal 5 ayat (2), PDF hlm. 8",
    # PMK 66/2023 (natura)
    "natura_obj": "PMK 66/2023 Pasal 3 ayat (1), PDF hlm. 5",
    "natura_rumah": "PMK 66/2023 Pasal 4 huruf e dan Pasal 7 ayat (4), PDF hlm. 6 dan 8; Lampiran huruf A angka 7 (maks. Rp2.000.000/bulan), PDF hlm. 22",
    "natura_kupon": "PMK 66/2023 Pasal 5 ayat (1) huruf b, ayat (4) huruf a dan ayat (5), PDF hlm. 6-7",
    "natura_bingkisan": "PMK 66/2023 Lampiran huruf A angka 2 (maks. Rp3.000.000/tahun), PDF hlm. 21; Pasal 7 ayat (4), PDF hlm. 8",
    "natura_kendaraan": "PMK 66/2023 Lampiran huruf A angka 8, PDF hlm. 22",
    "natura_nilai": "PMK 66/2023 Pasal 22 ayat (1) dan (3), PDF hlm. 16-17",
    "natura_saat": "PMK 66/2023 Pasal 23 ayat (1)-(2), PDF hlm. 17",
    "natura_h1": "PMK 66/2023 Pasal 23 ayat (4) dan Pasal 24, PDF hlm. 18",
    "natura_mulai": "PMK 66/2023 Pasal 27, PDF hlm. 19",
    # PER-16/PJ/2016 (2023)
    "p16_bruto": "PER-16/PJ/2016 Lampiran Bagian Pertama I.1.a.1 angka 1 huruf a-b (gaji, tunjangan, lembur, premi JKK/JKM/JPK), PDF hlm. 20-21",
    "p16_bj": "PER-16/PJ/2016 Pasal 10 ayat (3) huruf a, PDF hlm. 10",
    "p16_iuran": "PER-16/PJ/2016 Pasal 10 ayat (3) huruf b, PDF hlm. 10; Lampiran I.1.a.1 angka 1 huruf c (iuran pensiun/JHT ke BPJS Ketenagakerjaan), PDF hlm. 21; tafsir K9",
    "p16_iuran_pk": "PER-16/PJ/2016 Pasal 8 ayat (1) huruf c, PDF hlm. 9",
    "p16_setahun": "PER-16/PJ/2016 Pasal 14 ayat (2) huruf a, PDF hlm. 13; Lampiran I.1.a.1 angka 2 huruf a, PDF hlm. 21",
    "p16_bulan": "PER-16/PJ/2016 Pasal 14 ayat (3) huruf a, PDF hlm. 13; Lampiran I.1.a.1 angka 2 huruf d, PDF hlm. 21",
    "p16_joiner": "PER-16/PJ/2016 Pasal 14 ayat (4), PDF hlm. 13; Lampiran I.1.a.1 angka 2 huruf b dan huruf d angka 2), PDF hlm. 21",
    "p16_irr": "PER-16/PJ/2016 Pasal 14 ayat (2) huruf b dan ayat (3) huruf b, PDF hlm. 13; Lampiran I.1.b angka 1, PDF hlm. 23",
    "p16_akhir": "PER-16/PJ/2016 Pasal 14 ayat (5), PDF hlm. 13; Lampiran I.2 angka 1, PDF hlm. 24",
    "p16_leaver": "PER-16/PJ/2016 Lampiran I.2 angka 1 huruf c dan angka 2 huruf a, PDF hlm. 24; Pasal 14 ayat (7), PDF hlm. 13-14",
    "p16_pkp": "PER-16/PJ/2016 Pasal 10 ayat (2) huruf a, PDF hlm. 10; Pasal 14 ayat (8), PDF hlm. 14",
    "p16_ptkp": "PER-16/PJ/2016 Pasal 11 ayat (1) dan (5), PDF hlm. 11",
    "p16_karyawati": "PER-16/PJ/2016 Pasal 11 ayat (3) huruf a, PDF hlm. 11",
    "p16_ditanggung": "PER-16/PJ/2016 Pasal 8 ayat (1) huruf b dan ayat (2), PDF hlm. 9; contoh resmi PER-16 Lampiran I.8, PDF hlm. 46; PMK 66/2023 Pasal 23 ayat (4) dan Pasal 24 (kenikmatan Januari-Juni 2023 dikecualikan dari pemotongan), PDF hlm. 18; tafsir K4",
    "p16_zakat": "PER-16/PJ/2016 Pasal 10 ayat (3), PDF hlm. 10 (zakat tidak termasuk pengurang pemotongan); tafsir K10",
    "p16_tunj": "PER-16/PJ/2016 Lampiran Bagian Pertama I.1.a.1 angka 1 huruf a (segala jenis tunjangan), PDF hlm. 20",
    # BPJS
    "jkk": "PP 44/2015 Pasal 16 ayat (1), PDF hlm. 12; dasar upah sebulan Pasal 19 ayat (1)-(2), PDF hlm. 13; seluruh tarif nominal masuk bruto walaupun sebagian direkomposisi untuk JKP (tafsir K8)",
    "jkm": "PP 44/2015 Pasal 18 ayat (1), PDF hlm. 13; dasar upah sebulan Pasal 19 ayat (1)-(2), PDF hlm. 13",
    "jkk_relief": "PP 7/2025 Pasal 3 ayat (3)-(4) dan Pasal 4 ayat (1), PDF hlm. 3-4; Pasal 10 (iuran Februari-Juli 2025), PDF hlm. 6",
    "jkk_relief_ext": "PP 36/2025 Pasal I angka 2 (Pasal 10A: diperpanjang s.d. iuran Januari 2026) dan Pasal II (kelebihan bayar iuran Agustus 2025 dst. diperhitungkan ke bulan berikutnya), PDF hlm. 4; tafsir K7",
    "jht": "PP 46/2015 Pasal 16 ayat (1)-(2), PDF hlm. 11",
    "jp": "PP 45/2015 Pasal 28 ayat (2)-(3), PDF hlm. 20; batas upah Pasal 29, PDF hlm. 21 (nilai: tables/bpjs.csv, surat BPJS TK; berlaku mulai iuran Maret, sebelumnya batas tahun lalu, tafsir K11)",
    "jkn": "Perpres 82/2018 Pasal 31 (4% pemberi kerja, 1% peserta), PDF hlm. 22; batas Rp12.000.000: Perpres 75/2019 Pasal I angka 3 (Pasal 32 ayat (1)), PDF hlm. 3",
    "jkn_bukan_peng": "PMK 168/2023 Pasal 10 ayat (1), PDF hlm. 11-12; PER-16/PJ/2016 Pasal 10 ayat (3), PDF hlm. 10 (iuran JKN pegawai bukan pengurang)",
    # DTP
    "dtp25_sektor": "PMK 10/2025 Pasal 3 ayat (1)-(2), PDF hlm. 4",
    "dtp25_peg": "PMK 10/2025 Pasal 4 ayat (2)-(3), PDF hlm. 5; tafsir K5",
    "dtp25_masa": "PMK 10/2025 Pasal 2 ayat (2)-(3), PDF hlm. 4",
    "dtp25_tunai": "PMK 10/2025 Pasal 5 ayat (1)-(2), PDF hlm. 6",
    "dtp25_lebih": "PMK 10/2025 Pasal 5 ayat (5), PDF hlm. 6; PMK 168/2023 Lampiran B Bagian Pertama I.2 angka 8, PDF hlm. 30",
    "dtp25_pariwisata": "PMK 72/2025 Pasal I angka 4 (Pasal 4A huruf b: pariwisata Masa Oktober-Desember 2025), PDF hlm. 4",
    "dtp26_sektor": "PMK 105/2025 Pasal 3 ayat (1)-(2), PDF hlm. 4",
    "dtp26_peg": "PMK 105/2025 Pasal 4 ayat (2) dan (4), PDF hlm. 5; tafsir K5",
    "dtp26_masa": "PMK 105/2025 Pasal 2 ayat (2)-(3), PDF hlm. 4",
    "dtp26_tunai": "PMK 105/2025 Pasal 5 ayat (1)-(2), PDF hlm. 6",
    "dtp26_lebih": "PMK 105/2025 Pasal 5 ayat (5)-(6), PDF hlm. 6; PMK 168/2023 Lampiran B Bagian Pertama I.2 angka 8 (berlaku untuk setiap Masa Pajak Terakhir, termasuk bulan berhenti bekerja), PDF hlm. 30; tafsir K13",
    "dtp_bukan_penghasilan": "PMK 168/2023 Pasal 7 huruf h, PDF hlm. 10",
    # Interpretation decisions (docs/spesifikasi/tafsir_perhitungan.md)
    "bulat_ter_2024": "Tafsir K1: Masa Pajak s.d. Desember 2024 -> pecahan rupiah dibuang (dibulatkan ke bawah): PER-2/PJ/2024 Lampiran I huruf B Petunjuk Umum angka 7 ('harus tanpa nilai desimal ... 125 (bukan 125,50)'), PDF Lampiran hlm. 5",
    "bulat_ter_2025": "Tafsir K1: Masa Pajak Januari 2025 dst. -> dibulatkan ke rupiah penuh terdekat (< 0,50 ke bawah, >= 0,50 ke atas): PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3), PDF hlm. 106; masa s.d. Desember 2024 tetap PER-2/PJ/2024 (Pasal 130 huruf a, PDF hlm. 107)",
    "bulat_p16": "Tafsir K2: PPh sebulan metode lama dibulatkan ke bawah ke rupiah penuh, mengikuti contoh resmi PER-16/PJ/2016 Lampiran I.6.2.2 (5/12 x 17.500.000 = 7.291.666), PDF hlm. 43-45",
    "gross_up": "Tafsir K3: tunjangan pajak/PPh ditanggung = titik tetap terkecil T = PPh21(bruto tanpa T + T) dengan aturan pembulatan masa itu (perilaku kalkulator PPh 21 DJP, GT2-06); cara iterasi tidak diatur regulasi",
}


def round_pph(x, year):
    """PPh masa to whole rupiah (tafsir K1/K2): truncate up to 2024, half-up from Masa Januari 2025."""
    x = F(x)
    if year <= 2024:
        return math.floor(x)
    return math.floor(x + F(1, 2))


def round_formula(expr, year):
    return f"floor({expr})" if year <= 2024 else f"floor({expr} + 0.5)"


def round_src(year):
    return SRC["bulat_ter_2024"] if year <= 2024 else SRC["bulat_ter_2025"]


# ---------------------------------------------------------------- tables
def _read(name):
    with open(os.path.join(TABLES, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


TER_ROWS = _read("ter_bulanan.csv")
PTKP_ROWS = {r["status"]: r for r in _read("ptkp.csv")}
PASAL17 = [r for r in _read("tarif_pasal17.csv") if r["rezim"] == "UU HPP"]
KLU_ROWS = _read("klu_dtp.csv")


def ter_page(row):
    s = row["sumber"]
    i = s.index("PDF hlm. ")
    return int(s[i + 9:].split(")")[0].split(";")[0])


def ter_lookup(cat, bruto):
    """Return (rate Fraction, row). batas_bawah exclusive, batas_atas inclusive."""
    for r in TER_ROWS:
        if r["kategori"] != cat:
            continue
        lo = int(r["batas_bawah"])
        hi = int(r["batas_atas"]) if r["batas_atas"] else None
        if (bruto > lo or (lo == 0 and bruto >= 0)) and (hi is None or bruto <= hi):
            return F(r["tarif_persen"]) / 100, r
    raise ValueError((cat, bruto))


def ter_category(status):
    return PTKP_ROWS[status]["kategori_ter"]


def ptkp(status):
    return int(PTKP_ROWS[status]["ptkp_setahun"])


def pasal17_layers(pkp):
    """Return list of (rate Fraction, base int, lower, upper) and total tax."""
    out = []
    for r in PASAL17:
        lo = int(r["pkp_batas_bawah"])
        hi = int(r["pkp_batas_atas"]) if r["pkp_batas_atas"] else None
        if pkp <= lo:
            break
        top = pkp if hi is None else min(pkp, hi)
        out.append((F(r["tarif_persen"]) / 100, top - lo, lo, hi))
    total = sum(rate * base for rate, base, _, _ in out)
    return out, total


def jp_cap(year, month):
    if (year, month) < (2023, 3):
        return 9077600
    if (year, month) < (2024, 3):
        return 9559600
    if (year, month) < (2025, 3):
        return 10042300
    if (year, month) < (2026, 3):
        return 10547400
    return 11086300


JKK_NORMAL = {"sangat rendah": F("0.24"), "rendah": F("0.54"), "sedang": F("0.89"),
              "tinggi": F("1.27"), "sangat tinggi": F("1.74")}


def jkk_relief_active(year, month):
    """PP 7/2025 (Feb-Jul 2025) jo. PP 36/2025 (extended to January 2026 premium)."""
    return (2025, 2) <= (year, month) <= (2026, 1)


def klu_info(klu, year, month):
    """Return (sector, regulation, pdf page) when the KLU is listed for the given masa."""
    ym = f"{year}-{month:02d}"
    for r in KLU_ROWS:
        if r["klu"] == klu and r["masa_mulai"] <= ym <= r["masa_akhir"]:
            return r["sektor"], r["regulasi"], int(r["halaman_pdf"])
    return None


def floor_thousand(x):
    return math.floor(F(x) / 1000) * 1000


def dec(x):
    """Exact decimal string for a Fraction with a terminating expansion."""
    x = F(x)
    if x.denominator == 1:
        return str(x.numerator)
    for k in range(1, 13):
        scaled = x * 10 ** k
        if scaled.denominator == 1:
            n = abs(scaled.numerator)
            sign = "-" if x < 0 else ""
            ip, fp = divmod(n, 10 ** k)
            s = f"{sign}{ip}.{fp:0{k}d}".rstrip("0")
            assert F(s) == x, x
            return s
    raise ValueError(f"tidak berhingga: {x}")


def rp(x):
    x = F(x)
    neg = x < 0
    x = abs(x)
    if x.denominator == 1:
        s = f"{x.numerator:,}".replace(",", ".")
    else:
        s = dec(x).replace(".", ",")
        ip, fp = s.split(",")
        s = f"{int(ip):,}".replace(",", ".") + "," + fp
    return ("-" if neg else "") + "Rp" + s


def pct(rate):
    return dec(F(rate) * 100).replace(".", ",") + "%"
