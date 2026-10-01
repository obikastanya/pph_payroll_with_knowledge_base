"""E8 — studi kasus Perusahaan X: KB (regulasi + lapisan perusahaan) vs xlsx v8 (B0, referensi).

    env\\Scripts\\python.exe -m eksperimen.e8_perusahaan_x            # tahun 2023 (rezim PER-16)
    env\\Scripts\\python.exe -m eksperimen.e8_perusahaan_x --tahun 2024   # pegawai & kebijakan sama, rezim TER
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from engine.kalkulator import hitung

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "dataset" / "02_studi_kasus"
BERKAS_PX = [ROOT / "kb" / "perusahaan" / "perusahaan_x.yaml"]

# fakta KB -> baris output xlsx (output_xlsx_karyawan_A_2023.csv)
PETA = {
    "px_gaji": "gaji_prorata", "px_tunjangan": "tunjangan", "px_premi_jkm": "premi_jkm_perusahaan",
    "px_premi_jkk": "premi_jkk_perusahaan", "px_premi_kes": "premi_bpjs_kes_perusahaan",
    "px_premi_jht_pk": "premi_jht_perusahaan_non_objek", "px_premi_jp_pk": "premi_jp_perusahaan_non_objek",
    "px_iuran_jp_pg": "iuran_jp_pegawai", "px_iuran_jht_pg": "iuran_jht_pegawai", "px_iuran_kes_pg": "iuran_bpjs_kes_pegawai",
    "px_thr": "thr", "px_kompensasi": "kompensasi", "px_ota": "insentif_ota", "px_lembur": "lembur", "px_komisi": "komisi",
    "bruto": "bruto_teratur_sebulan", "biaya_jabatan_bulanan": "biaya_jabatan", "neto_sebulan": "neto_sebulan",
    "pph21": "pph21_dipotong",
}


def _rp(v):
    """Nilai dari xlsx (kadang float bernilai bulat) -> int; tolak bila tidak bulat."""
    if isinstance(v, float):
        if v != int(v):
            raise ValueError(f"nilai rupiah tidak bulat dari xlsx: {v}")
        return int(v)
    return v


def data_hr(inp, tahun):
    k, n = inp["karyawan"], inp["kenaikan_gaji"]
    tl = {t["nama"]: t for t in inp["tunjangan_sebelum_kenaikan"]}
    tb = {t["nama"]: t for t in inp["tunjangan_sesudah_kenaikan"]}
    jumlah = lambda d, tipe: sum(_rp(t["nilai"]) for t in d.values() if t["tipe"] == tipe)
    geser = lambda s: f"{tahun}{s[4:]}" if s and s[:4] == "2023" else s
    per = {}
    for h in inp["hari_kerja_per_bulan"]:
        per[str(h["bulan"])] = {"hk_penuh": _rp(h["hari_kerja_penuh"]), "hk_aktual": _rp(h["hari_kerja_aktual"])}
    for x in inp["kompensasi"]:
        per[str(int(x["tanggal"][5:7]))]["kompensasi_persen"] = repr(x["persen_gaji"])  # 0.1 -> "0.1" (string desimal)
    for kunci, sumber in (("ota", "insentif_ota"), ("lembur", "lembur"), ("komisi", "komisi")):
        for x in inp[sumber]:
            b = int((x.get("tanggal") or x.get("periode"))[5:7])
            per[str(b)][kunci] = per[str(b)].get(kunci, 0) + _rp(x["nominal"])
    return {
        "gaji_pokok": _rp(k["gaji_pokok"]), "kenaikan_tanggal": geser(n["tanggal"]), "kenaikan_nominal": _rp(n["nominal"]),
        "kenaikan_hk_sebelum": _rp(n["hari_kerja_aktual_sebelum"]), "kenaikan_hk_sesudah": _rp(n["hari_kerja_aktual_sesudah"]),
        "kenaikan_hari_sebelum": 15, "kenaikan_hari_sesudah": 7,  # xlsx sheet Allowance G2/H2 (hari kerja total)
        "tunjangan_tetap_lama": jumlah(tl, "fixed"), "tunjangan_prorata_lama": jumlah(tl, "prorate"),
        "tunjangan_tetap_baru": jumlah(tb, "fixed"), "tunjangan_prorata_baru": jumlah(tb, "prorate"),
        "tanggal_masuk": k["tanggal_masuk"], "tanggal_masuk_awal_bulan": k["tanggal_masuk"][:8] + "01",
        "tanggal_lebaran": geser(inp["thr"]["tanggal_lebaran"]), "tanggal_thr_bayar": geser(inp["thr"]["tanggal_transfer"]),
        "bpjs_tk_mulai_bulan": int(k["tanggal_daftar_bpjs_tk"][5:7]), "bpjs_kes_mulai_bulan": int(k["tanggal_daftar_bpjs_kes"][5:7]),
        "kelas_jkk_persen": "0.24", "per_masa": per,
    }


def kasus_kar_a(tahun=2023, thr_di_bulan_lebaran=False):
    inp = json.loads((DIR / "input_karyawan_A_2023.json").read_text(encoding="utf-8"))
    hr = data_hr(inp, tahun)
    if thr_di_bulan_lebaran:
        hr["tanggal_thr_bayar"] = hr["tanggal_lebaran"]
    return {
        "id": f"PX-KAR-A-{tahun}", "tahun_pajak": tahun, "cakupan": "setahun", "metode": "gross", "kurs": {}, "dtp": {},
        "pegawai": {"status_ptkp": inp["karyawan"]["status_ptkp"], "jenis_kelamin": "L", "punya_npwp": True,
                    "subjektif_mulai_bulan": None, "subjektif_akhir_bulan": None, "bulan_masuk": None,
                    "bulan_terakhir_bekerja": None, "periode_gaji": "bulanan", "hari_kerja_sebulan": None},
        "pemberi_kerja": {"klu": None, "jenis": "biasa"},
        "masa": [{"bulan": b, "komponen": []} for b in range(1, 13)], "data_hr": hr, "harapan": [],
    }


def keluaran_xlsx():
    hasil = {}
    with open(DIR / "output_xlsx_karyawan_A_2023.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hasil[r["variabel"]] = {b: int(r[f"bulan_{b:02d}"]) for b in range(1, 13)}
            hasil[r["variabel"]]["setahun"] = int(r["setahun"]) if r["setahun"] else None
    return hasil


def bandingkan(h, xl):
    baris = []
    for f, v in PETA.items():
        for b in range(1, 13):
            a = h["per_masa"][b].get(f, 0) or 0
            x = xl[v][b]
            baris.append({"fakta": f, "xlsx": v, "bulan": b, "kb": a, "b0": x, "sama": a == x})
    return baris


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tahun", type=int, default=2023)
    ap.add_argument("--thr-lebaran", action="store_true", help="anggap THR dibayar di bulan Lebaran (seperti xlsx)")
    a = ap.parse_args()
    h = hitung(kasus_kar_a(a.tahun, a.thr_lebaran), berkas_perusahaan=BERKAS_PX)
    print("peringatan:", [(p["kode"], p.get("fakta"), p.get("kategori_perusahaan"), p.get("kategori_wajib")) for p in h["peringatan"]])
    t = h["tahunan"]
    print({k: t.get(k) for k in ("bruto_setahun", "biaya_jabatan", "iuran_pengurang", "neto_setahun", "ptkp", "pkp",
                                 "pph21_setahun", "pph21_dipotong_sebelumnya", "pph21_masa_terakhir")})
    if a.tahun == 2023:
        xl = keluaran_xlsx()
        baris = bandingkan(h, xl)
        c = Counter((r["fakta"], r["sama"]) for r in baris)
        for f in PETA:
            beda = [r for r in baris if r["fakta"] == f and not r["sama"]]
            print(f"  {f:24} sama {c[(f, True)]:2}/12" + (" | beda: " + "; ".join(f"b{r['bulan']} kb={r['kb']} xlsx={r['b0']}" for r in beda[:4]) if beda else ""))
        print("PPh setahun KB:", t["pph21_setahun"], "| xlsx Q31:", xl["pph21_setahun"]["setahun"],
              "| total dipotong xlsx:", sum(xl["pph21_dipotong"][b] for b in range(1, 13)))
    else:
        print("PPh per masa:", {b: h["per_masa"][b]["pph21"] for b in range(1, 13)})
