"""E6 — peta solusi gross-up TER bulanan: domain real vs domain integer (research_plan.md §6.7, §6.9.7, RQ5).

Persamaan integer (BULAT-TER-01 = bawah): T = floor(r(B+T) * (B+T)). Dengan x = B + T:
    x - floor(r_k x) = B,  x in lapisan k = (bawah_k, atas_k].
Setiap solusi integer dicari eksak per lapisan (kandidat di sekitar B/(1-r_k), diverifikasi integer).
Jenis ambiguitas:
  - lintas_lapisan : solusi di dua lapisan berbeda (pita real (x_k(1-r_{k+1}), x_k(1-r_k)])
  - pembulatan     : dua solusi berurutan T, T+1 di lapisan yang sama, karena floor melompat

    env\\Scripts\\python.exe -m eksperimen.grossup
"""
import json
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path

from engine.interval import tabel_ter
from engine.muat import muat_tabel

ROOT = Path(__file__).resolve().parents[1]


def tabel():
    baris = muat_tabel("ter_bulanan")
    return {k: tabel_ter(baris, k) for k in "ABC"}


def solusi(t, B):
    """Semua x integer (bruto) yang memenuhi x - floor(r x) = B, beserta indeks lapisan."""
    hasil = []
    for i, l in enumerate(t.lapisan):
        r = l.tarif
        pusat = B / (1 - r)
        dasar = pusat.numerator // pusat.denominator
        for x in range(dasar - 2, dasar + 3):
            if x < 0 or not l.memuat(x):
                continue
            T = (r * x).numerator // (r * x).denominator
            if x - T == B:
                hasil.append((x, i))
    return sorted(set(hasil))


def jenis(sol):
    if len(sol) <= 1:
        return "tunggal"
    lapis = {i for _, i in sol}
    return "lintas_lapisan" if len(lapis) > 1 else "pembulatan"


def pita_real(t):
    pita = []
    for i in range(len(t.lapisan) - 1):
        xk, r0, r1 = t.lapisan[i].atas, t.lapisan[i].tarif, t.lapisan[i + 1].tarif
        if r1 > r0:
            pita.append({"batas": xk, "r_bawah": str(r0), "r_atas": str(r1),
                         "B_bawah_eksklusif": xk * (1 - r1), "B_atas_inklusif": xk * (1 - r0)})
    return pita


def jalankan(n_acak=60_000, seed=7):
    rng = random.Random(seed)
    T = tabel()
    laporan = {}
    for k, t in T.items():
        pita = pita_real(t)
        lebar = sum(p["B_atas_inklusif"] - p["B_bawah_eksklusif"] for p in pita)
        # (1) sampel acak B pada rentang gaji realistis 0 - 100 jt
        c = Counter()
        for _ in range(n_acak):
            c[jenis(solusi(t, rng.randint(0, 100_000_000)))] += 1
        # (2) verifikasi integer pada seluruh ujung pita real (titik kritis eksak)
        ujung_cocok = 0
        for p in pita:
            lo = p["B_bawah_eksklusif"]
            lo_i = lo.numerator // lo.denominator
            hi = p["B_atas_inklusif"]
            hi_i = hi.numerator // hi.denominator
            dalam = solusi(t, lo_i + 1)
            if len({i for _, i in dalam}) == 2 and len({i for _, i in solusi(t, hi_i + 1)}) <= 1:
                ujung_cocok += 1
        laporan[k] = {
            "jumlah_pita_lintas_lapisan": len(pita),
            "lebar_total_pita_real_rupiah": int(lebar),
            "ujung_pita_terverifikasi_integer": f"{ujung_cocok}/{len(pita)}",
            "sampel_acak_0_100jt": {j: round(v / n_acak, 4) for j, v in c.items()},
        }
    # contoh proposal & contoh resmi
    contoh = {
        "proposal_B_14.100.000_A": solusi(T["A"], 14_100_000),
        "resmi_PMK168_B_I.4_B_51.827.997_A": solusi(T["A"], 51_827_997),
    }
    return {"per_kategori": laporan, "contoh": {k: [(x, x - b) for x, _ in v] for (k, v), b in
                                                 zip(contoh.items(), (14_100_000, 51_827_997))}}


if __name__ == "__main__":
    hasil = jalankan()
    (ROOT / "eksperimen" / "hasil").mkdir(exist_ok=True)
    (ROOT / "eksperimen" / "hasil" / "grossup.json").write_text(json.dumps(hasil, indent=1, default=str), encoding="utf-8")
    print(json.dumps(hasil, indent=1, default=str))
