r"""Bandingkan hasil kalkulator DJP (hasil.csv) dengan GT3 dan dengan tabel TER (setelah semua kasus tercatat).

    env\Scripts\python dataset\11_acuan\gt2_kalkulator_djp\bandingkan.py
"""
import csv
import json
import re
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TER = list(csv.DictReader(open(ROOT / "dataset/01_regulasi/tables/ter_bulanan.csv", encoding="utf-8")))
KATEGORI = {r["status"]: r["kategori_ter"] for r in csv.DictReader(open(ROOT / "dataset/01_regulasi/tables/ptkp.csv", encoding="utf-8"))}


def ter(kategori, bruto):
    for r in TER:
        if r["kategori"] == kategori and int(r["batas_bawah"]) < bruto and (not r["batas_atas"] or bruto <= int(r["batas_atas"])):
            return Fraction(r["tarif_persen"]) / 100
    return Fraction(0)


def bulat(x):
    """Pembulatan PPh mulai Masa Januari 2025 (rezim kalkulator DJP 2026): rupiah terdekat, 0,50 ke atas
    (PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3); docs/spesifikasi/tafsir_perhitungan.md K1)."""
    return int(x + Fraction(1, 2))


def gross_up(kategori, dasar):
    """Tunjangan pajak T terkecil dengan T = floor(tarif(dasar + T) x (dasar + T)), dari tabel TER (iterasi titik tetap)."""
    t = 0
    for _ in range(100):
        baru = bulat(ter(kategori, dasar + t) * (dasar + t))
        if baru == t:
            return t
        t = baru
    raise ValueError("gross-up tidak konvergen")


# Kasus yang sumber GT3-nya memakai metode 'ditanggung': bruto GT3 sudah termasuk pajak yang di-gross-up, sehingga
# bruto itu tidak boleh diisikan lagi ke mode Gross Up. Data DJP tetap sah sebagai gross-up atas bruto yang diisikan,
# jadi acuannya adalah gross-up independen dari tabel TER atas bruto tersebut (lihat README, bagian Catatan).
DITANGGUNG = {"GT2-07", "GT2-11"}

rows = []
for r in csv.DictReader(open(HERE / "hasil.csv", encoding="utf-8")):
    rencana = {x["gt2_id"]: x for x in csv.DictReader(open(HERE / "rencana_kasus.csv", encoding="utf-8"))}[r["gt2_id"]]
    pph_djp = int(r["pph21"])
    m = re.match(r"(GT3-\d+) bulan (\d+)", rencana["sumber"])
    if r["gt2_id"] in DITANGGUNG:
        acuan, nama = gross_up(KATEGORI[r["ptkp"]], int(r["bruto_diisi"])), "gross-up dari tabel TER atas bruto yang diisikan"
    elif m:
        d = json.loads((ROOT / f"dataset/11_acuan/gt3_kasus_bertingkat/{m.group(1)}.json").read_text(encoding="utf-8"))
        pm = next(p for p in d["expected"]["per_masa"] if p["bulan"] == int(m.group(2)))
        acuan, nama = pm["pph21"], f"GT3 {m.group(1)} bulan {m.group(2)}"
    else:
        bruto = int(r["bruto_diisi"])
        acuan, nama = bulat(ter(KATEGORI[r["ptkp"]], bruto) * bruto), "tabel TER (dataset/01_regulasi/tables)"
    selisih = pph_djp - acuan
    rows.append({"gt2_id": r["gt2_id"], "skema": r["skema"], "ptkp": r["ptkp"], "bruto": r["bruto_diisi"],
                 "pph21_djp": pph_djp, "acuan": nama, "pph21_acuan": acuan, "selisih": selisih, "sama": selisih == 0,
                 "putusan": "" if selisih == 0 else ("pembulatan: kalkulator DJP membuang pecahan, PER-11/PJ/2025 Ps. 129 "
                                                      "mewajibkan rupiah terdekat" if abs(selisih) == 1 else "perlu diselidiki")})
with open(HERE / "perbandingan.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
for x in rows:
    print(f"{x['gt2_id']} {x['skema']:8} {x['ptkp']:5} {x['bruto']:>10} DJP {x['pph21_djp']:>9} acuan {x['pph21_acuan']:>9} {'sama' if x['sama'] else 'BEDA ' + str(x['selisih'])}")
print(f"{sum(x['sama'] for x in rows)}/{len(rows)} sama")
