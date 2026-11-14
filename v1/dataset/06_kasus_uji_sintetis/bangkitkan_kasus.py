"""Pembangkit kasus uji sintetis PPh 21 (research_plan.md §8.1 A12, §8.2, §6.9).

Hanya membangkitkan INPUT (profil pegawai 12 bulan + kebijakan perusahaan).
Nilai yang diharapkan (oracle) dihitung terpisah: lihat research_plan.md §9.2.

Kontrak presisi (§6.9.1): semua nilai uang adalah int rupiah; tarif dibaca dari CSV
sebagai Fraction (tidak pernah float); persentase input ditulis sebagai string desimal.

Strata:
  S1 acak-realistis      : gaji log-normal sekitar upah rata-rata
  S2 batas-lapisan-TER   : BRUTO tepat di batas lapisan TER (b-1, b, b+1); BPJS dimatikan
                           agar bruto = gaji persis
  S3 pita-gross-up       : B (bruto sebelum tunjangan pajak) di pita yang berpotensi punya
                           solusi gross-up ganda; BPJS dimatikan agar B = gaji persis
  S4 masuk/keluar-tengah : bulan masuk/keluar acak
  S5 tidak-teratur       : THR/bonus besar yang mendorong lintas lapisan
  S6 lintas-rezim        : profil identik untuk 2023-2026 (uji perubahan KB)
  S7 bruto-pecahan       : prorata hari kerja, kenaikan gaji tengah bulan, gaji tidak bulat,
                           kelas risiko JKK beragam -> setiap titik pembulatan menerima pecahan
  S8 sumbu-waktu         : tanggal bayar != periode kerja (gaji Desember dibayar Januari,
                           THR dibayar sebelum bulan Lebaran, rapel lintas tahun)

Jalankan dari root proyek:
    env\\Scripts\\python.exe dataset\\06_kasus_uji_sintetis\\bangkitkan_kasus.py --n 2000 --seed 42
"""
import argparse
import csv
import json
import math
import random
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "dataset" / "01_regulasi" / "tables"
OUT = Path(__file__).resolve().parent

PTKP_STATUS = ["TK/0", "TK/1", "TK/2", "TK/3", "K/0", "K/1", "K/2", "K/3"]
# distribusi kasar; ganti dengan proporsi BPS bila tersedia (dataset/04_data_publik)
PTKP_BOBOT = [0.35, 0.03, 0.02, 0.01, 0.12, 0.17, 0.18, 0.12]
KATEGORI_TER = {"TK/0": "A", "TK/1": "A", "K/0": "A",
                "TK/2": "B", "TK/3": "B", "K/1": "B", "K/2": "B",
                "K/3": "C"}
TAHUN = [2023, 2024, 2025, 2026]
METODE = ["gross", "gross_up"]
KELAS_JKK = ["0.0024", "0.0054", "0.0089", "0.0127", "0.0174"]  # PP 44/2015 (string desimal)


def baca_ter():
    """Lapisan TER sebagai (batas_bawah:int, batas_atas:int|None, tarif:Fraction), interval (bawah, atas]."""
    path = TABLES / "ter_bulanan.csv"
    if not path.exists():
        raise SystemExit(f"Tabel TER belum ada: {path}")
    batas = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            atas = r["batas_atas"].strip()
            batas.setdefault(r["kategori"].strip(), []).append(
                (int(r["batas_bawah"]), int(atas) if atas else None, Fraction(r["tarif_desimal"])))
    for k in batas:
        batas[k].sort(key=lambda x: x[0])
    return batas


def gaji_realistis(rng):
    # log-normal: median ±Rp7 juta, ekor kanan panjang; dibulatkan ke ribuan (int)
    return int(round(math.exp(rng.gauss(math.log(7_000_000), 0.7)) / 1000)) * 1000


def profil_dasar(rng, idx, strata):
    status = rng.choices(PTKP_STATUS, PTKP_BOBOT)[0]
    tahun = rng.choice(TAHUN)
    return {
        "id": f"SIN-{idx:06d}",
        "strata": strata,
        "tahun_pajak": tahun,
        "status_ptkp": status,
        "kategori_ter_harapan": KATEGORI_TER[status],
        "punya_npwp": True,
        "metode_pajak": rng.choice(METODE),
        "bulan_masuk": 1,
        "bulan_keluar": 12,
        "gaji_pokok": gaji_realistis(rng),
        "tunjangan_tetap": 0,
        "tunjangan_tidak_tetap": [0] * 12,
        "thr": {"bulan": None, "nominal": 0},
        "bonus": {"bulan": None, "nominal": 0},
        "bpjs_terdaftar": True,
        "kelas_risiko_jkk": "0.0024",
        "iuran_pensiun_pegawai_persen": "0.01",
        "zakat_bulanan": 0,
        "prorata": [],                 # [{bulan, hari_kerja_aktual, hari_kerja_penuh}]
        "kenaikan_gaji": None,         # {bulan, nominal, hk_sebelum, hk_sesudah, hk_penuh}
        "transaksi_bertanggal": [],    # [{komponen, nominal, periode_kerja, tanggal_terutang, tanggal_bayar}]
    }


def s2_batas_ter(rng, idx, ter):
    p = profil_dasar(rng, idx, "S2_batas_TER")
    p["tahun_pajak"] = rng.choice([2024, 2025, 2026])
    p["metode_pajak"] = "gross"
    p["bpjs_terdaftar"] = False  # bruto = gaji persis; premi BPJS diuji di S1/S7
    b = rng.choice(ter[p["kategori_ter_harapan"]][1:])[0]
    delta = rng.choice([-1, 0, 1])
    p["gaji_pokok"] = b + delta
    p["catatan"] = f"bruto = batas lapisan {b} {delta:+d} (interval (a, b])"
    return p


def s3_pita_gross_up(rng, idx, ter):
    # Dengan interval lapisan (a, b]: solusi bawah x = B/(1-r_bawah) <= x_k  <=>  B <= x_k(1-r_bawah);
    # solusi atas x = B/(1-r_atas) > x_k  <=>  B > x_k(1-r_atas).
    # Jadi pita dua solusi (domain real) = (x_k(1-r_atas), x_k(1-r_bawah)].
    p = profil_dasar(rng, idx, "S3_pita_gross_up")
    p["tahun_pajak"] = rng.choice([2024, 2025, 2026])
    p["metode_pajak"] = "gross_up"
    p["bpjs_terdaftar"] = False  # B = gaji persis
    lapisan = ter[p["kategori_ter_harapan"]]
    i = rng.randrange(1, len(lapisan))
    xk = lapisan[i][0]
    r_bawah, r_atas = lapisan[i - 1][2], lapisan[i][2]
    lo = math.floor(xk * (1 - r_atas)) + 1   # ujung bawah terbuka
    hi = math.floor(xk * (1 - r_bawah))      # ujung atas tertutup
    if hi < lo:  # tarif sama di kedua sisi: tidak ada pita
        return profil_dasar(rng, idx, "S3_pita_gross_up")
    p["gaji_pokok"] = rng.randint(lo, hi)
    p["catatan"] = f"pita gross-up di batas {xk}: B in [{lo}, {hi}] (domain real; verifikasi integer di engine)"
    return p


def s4_masuk_keluar(rng, idx, ter):
    p = profil_dasar(rng, idx, "S4_masuk_keluar")
    p["bulan_masuk"] = rng.randint(1, 12)
    p["bulan_keluar"] = rng.randint(p["bulan_masuk"], 12)
    return p


def s5_tidak_teratur(rng, idx, ter):
    p = profil_dasar(rng, idx, "S5_tidak_teratur")
    p["thr"] = {"bulan": rng.randint(3, 5), "nominal": p["gaji_pokok"]}
    p["bonus"] = {"bulan": rng.choice([3, 6, 12]), "nominal": p["gaji_pokok"] * rng.choice([1, 2, 3])}
    p["tunjangan_tidak_tetap"] = [rng.choice([0, 0, 500_000, 1_500_000]) for _ in range(12)]
    return p


def s6_lintas_rezim(rng, idx, ter):
    # profil identik untuk setiap tahun -> mengukur dampak perubahan KB terhadap output
    p = profil_dasar(rng, idx, "S6_lintas_rezim")
    return [dict(p, id=f"{p['id']}-{t}", tahun_pajak=t) for t in TAHUN]


def s7_bruto_pecahan(rng, idx, ter):
    p = profil_dasar(rng, idx, "S7_bruto_pecahan")
    p["gaji_pokok"] = rng.randint(3_000_000, 60_000_000)          # tidak bulat ribuan
    p["tunjangan_tetap"] = rng.choice([0, 333_333, 150_001, 427_777])
    p["kelas_risiko_jkk"] = rng.choice(KELAS_JKK)
    p["bulan_masuk"] = rng.randint(1, 12)
    hk_penuh = rng.choice([19, 20, 21, 22, 23])
    p["prorata"] = [{"bulan": p["bulan_masuk"], "hari_kerja_aktual": rng.randint(1, hk_penuh - 1),
                     "hari_kerja_penuh": hk_penuh}]
    if p["bulan_masuk"] < 12:
        bln = rng.randint(p["bulan_masuk"] + 1, 12)
        sebelum = rng.randint(1, hk_penuh - 1)
        p["kenaikan_gaji"] = {"bulan": bln, "nominal": rng.randint(100_000, 2_000_000),
                              "hk_sebelum": sebelum, "hk_sesudah": hk_penuh - sebelum, "hk_penuh": hk_penuh}
    p["catatan"] = "prorata/kenaikan/premi menghasilkan pecahan: uji registri pembulatan"
    return p


def s8_sumbu_waktu(rng, idx, ter):
    p = profil_dasar(rng, idx, "S8_sumbu_waktu")
    t = p["tahun_pajak"]
    jenis = rng.choice(["gaji_des_dibayar_jan", "thr_sebelum_lebaran", "rapel_lintas_tahun"])
    if jenis == "gaji_des_dibayar_jan":
        p["transaksi_bertanggal"].append({
            "komponen": "gaji_pokok", "nominal": p["gaji_pokok"],
            "periode_kerja": f"{t}-12", "tanggal_terutang": f"{t}-12-31",
            "tanggal_bayar": f"{t + 1}-01-0{rng.randint(2, 5)}"})
    elif jenis == "thr_sebelum_lebaran":
        bln_lebaran = rng.randint(3, 5)
        p["transaksi_bertanggal"].append({
            "komponen": "thr", "nominal": p["gaji_pokok"],
            "periode_kerja": f"{t}-{bln_lebaran:02d}", "tanggal_terutang": f"{t}-{bln_lebaran:02d}-01",
            "tanggal_bayar": f"{t}-{bln_lebaran - 1:02d}-2{rng.randint(0, 8)}"})
    else:
        p["transaksi_bertanggal"].append({
            "komponen": "rapel_kenaikan_gaji", "nominal": rng.randint(1, 3) * 500_000,
            "periode_kerja": f"{t}-{rng.randint(10, 12):02d}", "tanggal_terutang": f"{t + 1}-01-15",
            "tanggal_bayar": f"{t + 1}-01-25"})
    p["catatan"] = f"uji sumbu waktu: {jenis} (REG-WAKTU-01)"
    return p


STRATA = {  # proporsi
    "S1": (0.20, lambda r, i, t: profil_dasar(r, i, "S1_acak")),
    "S2": (0.15, s2_batas_ter),
    "S3": (0.15, s3_pita_gross_up),
    "S4": (0.10, s4_masuk_keluar),
    "S5": (0.10, s5_tidak_teratur),
    "S6": (0.10, s6_lintas_rezim),
    "S7": (0.12, s7_bruto_pecahan),
    "S8": (0.08, s8_sumbu_waktu),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(OUT / "kasus_sintetis.jsonl"))
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ter = baca_ter()
    idx, kasus = 0, []
    for nama, (prop, fn) in STRATA.items():
        for _ in range(round(a.n * prop)):
            idx += 1
            hasil = fn(rng, idx, ter)
            kasus.extend(hasil if isinstance(hasil, list) else [hasil])
    with open(a.out, "w", encoding="utf-8") as f:
        for k in kasus:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    hitung = {}
    for k in kasus:
        hitung[k["strata"]] = hitung.get(k["strata"], 0) + 1
    print(f"{len(kasus)} kasus -> {a.out}")
    print(json.dumps(hitung, indent=2))


if __name__ == "__main__":
    main()
