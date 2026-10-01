"""E5 — studi ablasi (research_plan.md §12.1). Setiap varian: jumlah tupel salah + contoh tandingan.

Acuan kebenaran per varian:
  A1, A5 : V1 (kasus resmi kanonik, protokol erratum/tafsir)
  A2, A3 : E8 Perusahaan X (sistem penuh sebagai acuan, karena xlsx bukan kebenaran)
  A4     : kasus sintetis gross-up (sistem penuh: titik tetap terkecil + deteksi solusi ganda)
  A9     : transaksi bertanggal (MR14; masa pajak = saat terutang)

    env\\Scripts\\python.exe -m eksperimen.ablasi
"""
import json
from functools import partial

from eksperimen import v1
from eksperimen.e8_perusahaan_x import BERKAS_PX, kasus_kar_a
from eksperimen.v2 import konverter
from engine.kalkulator import fakta, hitung


def _v1(ablasi):
    hasil = v1.jalankan(lambda k, var: hitung(k, var, ablasi=ablasi), fakta)
    c, stj = v1.ringkas(hasil)
    contoh = next((r for r in hasil if r["status"] in ("SELISIH", "TIDAK_DIHASILKAN")), None)
    return {"acuan": "V1 (1213 harapan resmi)", "tupel_salah": stj, "contoh": contoh}


def _beda(a, b):
    n, contoh = 0, None
    for m in a["per_masa"]:
        for f, v in a["per_masa"][m].items():
            if b["per_masa"].get(m, {}).get(f) != v:
                n += 1
                contoh = contoh or {"bulan": m, "fakta": f, "penuh": v, "ablasi": b["per_masa"].get(m, {}).get(f)}
    for f, v in a["tahunan"].items():
        if b["tahunan"].get(f) != v:
            n += 1
            contoh = contoh or {"bulan": None, "fakta": f, "penuh": v, "ablasi": b["tahunan"].get(f)}
    return n, contoh


def _e8(ablasi, tanpa_perusahaan=False):
    penuh = hitung(kasus_kar_a(2023), berkas_perusahaan=BERKAS_PX)
    try:
        abl = hitung(kasus_kar_a(2023), berkas_perusahaan=() if tanpa_perusahaan else BERKAS_PX, ablasi=ablasi)
    except Exception as e:
        return {"acuan": "E8 sistem penuh", "tupel_salah": "galat", "contoh": f"{type(e).__name__}: {e}"[:200]}
    n, contoh = _beda(penuh, abl)
    konflik = sum(p["kode"] == "KONFLIK_WAJIB" for p in abl["peringatan"])
    return {"acuan": "E8 sistem penuh", "tupel_salah": n, "contoh": contoh, "konflik_terdeteksi": konflik}


def _a4():
    kasus = [k for k in konverter().muat() if k["metode"] == "gross_up"]
    salah, ganda_hilang, contoh = 0, 0, None
    for k in kasus:
        penuh, abl = hitung(k), hitung(k, ablasi={"A4_iterasi_naif"})
        g = sum(p["kode"] == "GROSSUP_GANDA" for p in penuh["peringatan"])
        ganda_hilang += g - sum(p["kode"] == "GROSSUP_GANDA" for p in abl["peringatan"])
        n, c = _beda(penuh, abl)
        if n:
            salah += n
            contoh = contoh or {"kasus": k["id"], **c}
    return {"acuan": f"{len(kasus)} kasus gross-up sintetis", "tupel_salah": salah, "contoh": contoh,
            "solusi_ganda_tidak_terdeteksi": ganda_hilang}


def _a9():
    base = kasus_kar_a(2023)
    for m in base["masa"]:
        m["komponen"] = [{"kode": "gaji", "kategori": "teratur", "satuan_periode": "bulan", "nominal": 10_000_000}]
    base.pop("data_hr")
    skenario = {
        "THR dibayar sebelum Lebaran": {"komponen": "thr", "kategori": "tidak_teratur", "nominal": 10_000_000,
                                       "periode_kerja": "2023-04", "tanggal_terutang": "2023-04-15", "tanggal_bayar": "2023-03-28"},
        "gaji Desember dibayar Januari": {"komponen": "gaji_des", "kategori": "teratur", "nominal": 2_000_000,
                                          "periode_kerja": "2023-12", "tanggal_terutang": "2023-12-31", "tanggal_bayar": "2024-01-03"},
        "rapel terutang tahun berikut": {"komponen": "rapel", "kategori": "tidak_teratur", "nominal": 3_000_000,
                                         "periode_kerja": "2023-11", "tanggal_terutang": "2024-01-15", "tanggal_bayar": "2024-01-25"},
    }
    salah, contoh = 0, None
    for nama, t in skenario.items():
        k = json.loads(json.dumps(base))
        k["transaksi"] = [t]
        try:
            penuh = hitung(k)
            abl = hitung(k, ablasi={"A9_tanpa_tiga_tanggal"})
        except Exception as e:
            salah += 1
            contoh = contoh or {"skenario": nama, "galat": str(e)[:120]}
            continue
        n, c = _beda(penuh, abl)
        if n:
            salah += n
            contoh = contoh or {"skenario": nama, **c}
    return {"acuan": "3 skenario transaksi bertanggal", "tupel_salah": salah, "contoh": contoh}


VARIAN = {
    "A1_tanpa_versi_waktu": partial(_v1, {"A1_tanpa_versi_waktu"}),
    "A2_tanpa_lapisan_perusahaan": partial(_e8, set(), True),
    "A3_tanpa_resolusi_konflik": partial(_e8, {"A3_tanpa_resolusi_konflik"}),
    "A4_iterasi_naif": _a4,
    "A5_pembulatan_naif": partial(_v1, {"A5_pembulatan_naif"}),
    "A9_tanpa_tiga_tanggal": _a9,
}


def jalankan():
    return {nama: fn() for nama, fn in VARIAN.items()}


if __name__ == "__main__":
    for nama, r in jalankan().items():
        print(f"{nama}: tupel salah = {r['tupel_salah']} | acuan: {r['acuan']}")
        for k, v in r.items():
            if k not in ("tupel_salah", "acuan"):
                print(f"    {k}: {v}")
