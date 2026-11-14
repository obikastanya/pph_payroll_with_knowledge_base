"""Konversi profil sintetis (bangkitkan_kasus.py) -> kasus kanonik untuk V2 (research_plan.md §9.2).

Premi/iuran BPJS dihitung di sini sebagai INPUT (sama untuk semua sistem yang dibandingkan), seperti
contoh resmi yang menyajikan premi sebagai angka. Pembulatan premi memakai registri (BULAT-BPJS-01,
default). Prorata gaji (S7) dibulatkan setengah-menjauhi-nol (kebijakan perusahaan) karena kontrak input = int.
Strata S8 (sumbu waktu) tidak dikonversi: diuji terpisah (E11).
"""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from engine.muat import muat_registri_pembulatan
from engine.pembulatan import bulatkan

DIR = Path(__file__).resolve().parent
REG = muat_registri_pembulatan()
KLU_DTP = {2025: ["13111", "55110", "15202"], 2026: ["14111", "79121"]}
JP_BATAS = [((2023, 1), 9_077_600), ((2023, 3), 9_559_600), ((2024, 3), 10_042_300),
            ((2025, 3), 10_547_400), ((2026, 3), 11_086_300)]


def _jp_batas(tahun, bulan):
    nilai = None
    for (t, b), v in JP_BATAS:
        if (tahun, bulan) >= (t, b):
            nilai = v
    return nilai


def _nominal(x):
    """Prorata dibulatkan oleh kebijakan perusahaan sebelum masuk payroll (kontrak input: int)."""
    return bulatkan(Fraction(x), "setengah_menjauhi_nol")


def _pilih(id_, pilihan):
    h = int(hashlib.sha256(id_.encode()).hexdigest(), 16)
    return pilihan[h % len(pilihan)], h


def konversi(p):
    if p["strata"].startswith("S8"):
        return None
    if p["tahun_pajak"] <= 2023 and p["metode_pajak"] == "gross_up":
        return None  # gross-up rezim PER-16 di luar model v1 (KODIFIKASI.md bagian E)
    tahun = p["tahun_pajak"]
    masuk, keluar = p["bulan_masuk"], p["bulan_keluar"]
    gaji = p["gaji_pokok"]
    naik = p.get("kenaikan_gaji")
    prorata = {x["bulan"]: x for x in p.get("prorata") or []}
    masa = []
    for b in range(masuk, keluar + 1):
        gaji_b = gaji + (naik["nominal"] if naik and b > naik["bulan"] else 0)
        if naik and b == naik["bulan"]:
            nilai_gaji = Fraction(gaji * naik["hk_sebelum"] + (gaji + naik["nominal"]) * naik["hk_sesudah"], naik["hk_penuh"])
        elif b in prorata:
            nilai_gaji = Fraction(gaji_b * prorata[b]["hari_kerja_aktual"], prorata[b]["hari_kerja_penuh"])
        else:
            nilai_gaji = Fraction(gaji_b)
        komp = [{"kode": "gaji_pokok", "kategori": "teratur", "satuan_periode": "bulan", "nominal": _nominal(nilai_gaji)}]
        if p["tunjangan_tetap"]:
            komp.append({"kode": "tunjangan_tetap", "kategori": "teratur", "satuan_periode": "bulan", "nominal": p["tunjangan_tetap"]})
        tt = p["tunjangan_tidak_tetap"][b - 1]
        if tt:
            komp.append({"kode": "tunjangan_tidak_tetap", "kategori": "teratur", "satuan_periode": "bulan", "nominal": tt})
        for kunci in ("thr", "bonus"):
            if p[kunci]["bulan"] == b and p[kunci]["nominal"]:
                komp.append({"kode": kunci, "kategori": "tidak_teratur", "satuan_periode": "bulan", "nominal": p[kunci]["nominal"]})
        if p.get("bpjs_terdaftar"):
            upah = gaji_b + p["tunjangan_tetap"]
            premi = lambda tarif, dasar: bulatkan(Fraction(tarif) * dasar, REG.entri("BULAT-BPJS-01").mode)
            komp += [
                {"kode": "premi_jkk", "kategori": "premi_objek", "satuan_periode": "bulan", "nominal": premi(p["kelas_risiko_jkk"], upah)},
                {"kode": "premi_jkm", "kategori": "premi_objek", "satuan_periode": "bulan", "nominal": premi("0.003", upah)},
                {"kode": "premi_bpjs_kes", "kategori": "premi_objek", "satuan_periode": "bulan", "nominal": premi("0.04", min(upah, 12_000_000))},
                {"kode": "iuran_jht_pegawai", "kategori": "iuran_pengurang", "satuan_periode": "bulan", "nominal": premi("0.02", upah)},
                {"kode": "iuran_pensiun_pegawai", "kategori": "iuran_pengurang", "satuan_periode": "bulan",
                 "nominal": premi(p["iuran_pensiun_pegawai_persen"], min(upah, _jp_batas(tahun, b)))},
            ]
        if p.get("zakat_bulanan"):
            komp.append({"kode": "zakat", "kategori": "zakat", "satuan_periode": "bulan", "nominal": p["zakat_bulanan"]})
        masa.append({"bulan": b, "komponen": komp})
    klu = None
    if tahun in KLU_DTP:
        pilihan, h = _pilih(p["id"], KLU_DTP[tahun])
        klu = pilihan if h % 3 == 0 else None
    return {
        "id": p["id"], "strata": p["strata"], "tahun_pajak": tahun, "cakupan": "setahun",
        "pegawai": {"status_ptkp": p["status_ptkp"], "jenis_kelamin": "L", "punya_npwp": p["punya_npwp"],
                    "subjektif_mulai_bulan": None, "subjektif_akhir_bulan": None,
                    "bulan_masuk": masuk if masuk > 1 else None,
                    "bulan_terakhir_bekerja": keluar if keluar < 12 else None, "periode_gaji": "bulanan",
                    "hari_kerja_sebulan": None},
        "pemberi_kerja": {"klu": klu, "jenis": "biasa"}, "metode": p["metode_pajak"], "kurs": {}, "dtp": {},
        "masa": masa, "harapan": [],
    }


def muat(path=DIR / "kasus_sintetis.jsonl"):
    for baris in open(path, encoding="utf-8"):
        k = konversi(json.loads(baris))
        if k:
            yield k
