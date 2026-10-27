"""Uji diferensial: GT3 (dihitung manual dari teks regulasi) terhadap engine prototipe lama (engine/ + kb/).

    env\\Scripts\\python dataset\\11_acuan\\diferensial_gt3_engine_lama.py

Engine lama dibangun sebelum GT3 dan sudah lolos 46 contoh resmi, sehingga menjadi pembanding yang independen dari
penyusun GT3. Selisih TIDAK otomatis berarti GT3 salah: setiap selisih diadjudikasi (lihat diferensial_gt3.md).
Keluaran: diferensial_gt3.csv (satu baris per kasus, bulan, dan fakta yang dibandingkan).
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.kalkulator import hitung  # noqa: E402

HERE = Path(__file__).resolve().parent
GT3 = HERE / "gt3_kasus_bertingkat"

KATEGORI = {
    "gaji": "teratur", "tunjangan_tetap": "teratur", "lembur": "teratur",
    "premi_jkk": "premi_objek", "premi_jkm": "premi_objek", "premi_bpjs_kesehatan_pemberi_kerja": "premi_objek",
    "iuran_jht_pemberi_kerja": None, "iuran_jp_pemberi_kerja": None,   # bukan objek: engine lama tidak menerimanya
    "iuran_jht_pegawai": "iuran_pengurang", "iuran_jp_pegawai": "iuran_pengurang",
    "iuran_bpjs_kesehatan_pegawai": None,                                # tidak diperhitungkan
    "thr": "tidak_teratur", "bonus": "tidak_teratur",
    "natura_rumah_individual": "natura", "kendaraan_dinas": "natura", "bingkisan_non_hari_raya": "natura",
    "kupon_makan_dinas_luar": "natura", "zakat": "zakat",
}
METODE = {"gross": "gross", "gross_up": "gross_up", "ditanggung": "ditanggung_pemberi_kerja"}


def kanonik(d):
    i = d["input"]
    masa = [{"bulan": m["bulan"], "komponen": [{"kode": k, "kategori": KATEGORI[k], "satuan_periode": "bulan", "nominal": v}
                                               for k, v in m["komponen"].items() if v and KATEGORI[k]]} for m in i["masa"]]
    info = i.get("info_dtp") or {}
    # PMK 10/2025 dan 105/2025: kriteria memakai penghasilan tetap dan teratur (gaji + tunjangan tetap) di bulan pertama,
    # bukan lembur. Tanpa nilai ini engine lama menjumlah semua komponen 'teratur', termasuk lembur.
    pertama = i["masa"][0]["komponen"]
    tetap = info.get("penghasilan_tetap_teratur_kontrak_januari", pertama.get("gaji", 0) + pertama.get("tunjangan_tetap", 0))
    perempuan_kawin = i.get("jenis_kelamin") == "P" and i["status_ptkp"].startswith("K/")
    return {
        "id": d["id"], "tahun_pajak": d["tahun_pajak"],
        "cakupan": "satu_masa" if len(masa) == 1 and d["expected"].get("tahunan") is None else "setahun",
        "pegawai": {"status_ptkp": i["status_ptkp"], "jenis_kelamin": i.get("jenis_kelamin", "L"),
                    "punya_npwp": i.get("npwp_nik_valid", True), "subjektif_mulai_bulan": None,
                    "subjektif_akhir_bulan": None, "bulan_masuk": i.get("bulan_masuk"),
                    "bulan_terakhir_bekerja": i.get("bulan_keluar"), "periode_gaji": "bulanan", "hari_kerja_sebulan": None,
                    "suami_tidak_berpenghasilan_terbukti": perempuan_kawin and not i.get("karyawati_kawin_suami_berpenghasilan")},
        "pemberi_kerja": {"klu": (i.get("sektor") or {}).get("klu"), "jenis": "biasa"},
        "metode": METODE[i["metode"]], "kurs": {},
        "dtp": {"penghasilan_tetap_teratur_kontrak_januari": tetap if d["tahun_pajak"] >= 2025 else None},
        "masa": masa,
    }


def main():
    rows, failures = [], 0
    for f in sorted(GT3.glob("GT3-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        try:
            h = hitung(kanonik(d))
        except Exception as e:  # noqa: BLE001 - every engine refusal is recorded, not hidden
            rows.append({"id": d["id"], "bulan": "", "fakta": "ERROR", "gt3": "", "engine_lama": f"{type(e).__name__}: {e}"[:200], "sama": False})
            failures += 1
            continue
        for pm in d["expected"]["per_masa"]:
            got = h["per_masa"].get(pm["bulan"], {})
            for fakta in ("bruto", "pph21", "pph21_dtp"):
                if pm.get(fakta) is None:
                    continue
                g = got.get(fakta, 0 if fakta == "pph21_dtp" else None)
                rows.append({"id": d["id"], "bulan": pm["bulan"], "fakta": fakta, "gt3": pm[fakta], "engine_lama": g,
                             "sama": g == pm[fakta]})
        t = d["expected"].get("tahunan")
        if t:
            for fakta, kunci in (("pkp", "pkp"), ("pph21_setahun", "pph21_setahun"), ("pph21_masa_terakhir", "pph21_masa_terakhir")):
                if t.get(kunci) is None:
                    continue
                g = h["tahunan"].get(fakta)
                rows.append({"id": d["id"], "bulan": "tahunan", "fakta": fakta, "gt3": t[kunci], "engine_lama": g, "sama": g == t[kunci]})
    out = HERE / "diferensial_gt3.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    same = sum(r["sama"] for r in rows)
    cases_diff = sorted({r["id"] for r in rows if not r["sama"]})
    print(f"{len(rows)} perbandingan, {same} sama, {len(rows) - same} beda; kasus dengan selisih: {len(cases_diff)}; engine menolak: {failures}")
    print("kasus berselisih:", ", ".join(cases_diff))


if __name__ == "__main__":
    main()
