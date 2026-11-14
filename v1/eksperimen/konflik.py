"""E4b — deteksi konflik kebijakan perusahaan vs klasifikasi wajib (research_plan.md §11.4, RQ4).

Himpunan berlabel: pemetaan (jenis -> kategori) yang mungkin dibuat HR. Label 'konflik' ditetapkan dari
pasal (bukan dari sistem). Deteksi = engine mengeluarkan KONFLIK_WAJIB untuk fakta tersebut.

    env\\Scripts\\python.exe -m eksperimen.konflik
"""
import json
import tempfile
from pathlib import Path

from engine.kalkulator import hitung
from engine.kb import muat_kb

# (jenis, kategori perusahaan, konflik?, dasar label)
BERLABEL = [
    ("lembur", "tidak_teratur", True, "PMK 168 Ps. 5(3)a; PER-16 Ps. 1 angka 15"),
    ("premi_jkk", "bukan_objek", True, "PMK 168 Ps. 5(3)d"),
    ("premi_jkn", "tidak_diperhitungkan", True, "PMK 168 Ps. 5(3)e"),
    ("iuran_jht_pemberi_kerja", "premi_objek", True, "PMK 168 Ps. 7c"),
    ("iuran_jp_pemberi_kerja", "iuran_pengurang", True, "PMK 168 Ps. 7c, 10(1)b (hanya iuran pegawai)"),
    ("iuran_jkn_pegawai", "iuran_pengurang", True, "PMK 168 Ps. 10(1): BPJS Kes pegawai bukan pengurang (bug pajakin)"),
    ("thr", "teratur", True, "PMK 168 Ps. 5(3)b"),
    ("bonus", "teratur", True, "PMK 168 Ps. 5(3)b"),
    ("gaji", "tidak_teratur", True, "PMK 168 Ps. 5(3)a"),
    ("tunjangan", "tidak_diperhitungkan", True, "PMK 168 Ps. 5(3)a"),
    ("lembur", "teratur", False, "PMK 168 Ps. 5(3)a"),
    ("premi_jkk", "premi_objek", False, "PMK 168 Ps. 5(3)d"),
    ("premi_jkn", "premi_objek", False, "PMK 168 Ps. 5(3)e"),
    ("iuran_jht_pegawai", "iuran_pengurang", False, "PMK 168 Ps. 10(1)b"),
    ("iuran_jkn_pegawai", "tidak_diperhitungkan", False, "PMK 168 Ps. 10(1)"),
    ("iuran_jht_pemberi_kerja", "bukan_objek", False, "PMK 168 Ps. 7c"),
    ("thr", "tidak_teratur", False, "PMK 168 Ps. 5(3)b"),
    ("bonus", "tidak_teratur", False, "PMK 168 Ps. 5(3)b"),
    ("komisi", "tidak_teratur", False, "tidak diatur tegas (tafsir K-03) -> bukan konflik"),
    ("komisi", "teratur", False, "tidak diatur tegas (tafsir K-03) -> bukan konflik"),
    ("insentif_kinerja", "tidak_teratur", False, "tidak diatur tegas -> bukan konflik"),
]


def _kasus(tahun):
    return {"id": "KONFLIK", "tahun_pajak": tahun, "cakupan": "setahun", "metode": "gross", "kurs": {}, "dtp": {},
            "pegawai": {"status_ptkp": "TK/0", "jenis_kelamin": "L", "punya_npwp": True, "subjektif_mulai_bulan": None,
                        "subjektif_akhir_bulan": None, "bulan_masuk": None, "bulan_terakhir_bekerja": None,
                        "periode_gaji": "bulanan", "hari_kerja_sebulan": None},
            "pemberi_kerja": {"klu": None, "jenis": "biasa"},
            "masa": [{"bulan": b, "komponen": [{"kode": "gaji", "kategori": "teratur", "satuan_periode": "bulan",
                                                 "nominal": 10_000_000}]} for b in range(1, 13)], "harapan": []}


def jalankan(tahun=(2023, 2024)):
    tmp = Path(tempfile.mkdtemp(prefix="konflik_"))
    hasil = []
    for i, (jenis, kategori, label, dasar) in enumerate(BERLABEL):
        p = tmp / f"px_{i}.yaml"
        p.write_text(f'''lapisan: perusahaan
komponen:
  - {{fakta: px_uji, jenis: {jenis}, kategori: {kategori}}}
aturan:
  - id: PX-UJI-{i}
    sifat: opsional
    berlaku: {{mulai: 2016-01-01}}
    lingkup: masa
    menghasilkan: px_uji
    maka: "250000"
    tipe_hasil: rupiah
    sumber: "uji deteksi konflik"
''', encoding="utf-8")
        kb = muat_kb(berkas_tambahan=[p])
        for t in tahun:
            h = hitung(_kasus(t), kb=kb)
            terdeteksi = any(w["kode"] == "KONFLIK_WAJIB" and w["fakta"] == "px_uji" for w in h["peringatan"])
            hasil.append({"jenis": jenis, "kategori": kategori, "tahun": t, "label": label, "terdeteksi": terdeteksi, "dasar": dasar})
    tp = sum(r["label"] and r["terdeteksi"] for r in hasil)
    fp = sum(not r["label"] and r["terdeteksi"] for r in hasil)
    fn = sum(r["label"] and not r["terdeteksi"] for r in hasil)
    presisi = tp / (tp + fp) if tp + fp else 1
    recall = tp / (tp + fn) if tp + fn else 1
    f1 = 2 * presisi * recall / (presisi + recall) if presisi + recall else 0
    return {"n": len(hasil), "tp": tp, "fp": fp, "fn": fn, "presisi": presisi, "recall": recall, "f1": f1}, hasil


if __name__ == "__main__":
    ringkas, hasil = jalankan()
    print(json.dumps(ringkas, indent=1))
    for r in hasil:
        if r["label"] != r["terdeteksi"]:
            print("  SALAH:", r)
