"""E7 — ekspresivitas katalog kebijakan (research_plan.md §11.3, RQ1).

Setiap kebijakan KP-xx dinilai: native (hanya KB, dieksekusi & diverifikasi angkanya), input (cukup data
kasus/metode), atau tidak_bisa (butuh perubahan engine / bertentangan dengan sifat aturan wajib) + alasan.

    env\\Scripts\\python.exe -m eksperimen.ekspresivitas
"""
import json
from pathlib import Path

from engine.kalkulator import hitung

ROOT = Path(__file__).resolve().parents[1]
KAT = ROOT / "kb" / "perusahaan" / "katalog"


def _kasus(tahun, hr, per_masa=None, bulan=range(1, 13)):
    hr = dict(hr, per_masa={str(b): v for b, v in (per_masa or {}).items()})
    return {"id": "KP", "tahun_pajak": tahun, "cakupan": "setahun", "metode": "gross", "kurs": {}, "dtp": {},
            "pegawai": {"status_ptkp": "TK/0", "jenis_kelamin": "L", "punya_npwp": True, "subjektif_mulai_bulan": None,
                        "subjektif_akhir_bulan": None, "bulan_masuk": None, "bulan_terakhir_bekerja": None,
                        "periode_gaji": "bulanan", "hari_kerja_sebulan": None},
            "pemberi_kerja": {"klu": None, "jenis": "biasa"}, "masa": [{"bulan": b, "komponen": []} for b in bulan],
            "data_hr": hr, "harapan": []}


def _uji(berkas, kasus, cek):
    h = hitung(kasus, berkas_perusahaan=[KAT / berkas])
    hasil = {nama: (fn(h), harap) for nama, (fn, harap) in cek.items()}
    return all(a == b for a, b in hasil.values()), {k: {"aktual": a, "harapan": b} for k, (a, b) in hasil.items()}, h


def jalankan():
    tabel = []

    def catat(kp, nama, status, bukti):
        tabel.append({"kebijakan": kp, "nama": nama, "status": status, "bukti": bukti})

    ok, b, _ = _uji("kp06_thr_permenaker.yaml",
                    _kasus(2024, {"gaji_pokok": 10_000_000, "tunjangan_tetap": 2_000_000, "tanggal_masuk": "2023-10-01",
                                  "tanggal_lebaran": "2024-04-10"}),
                    {"THR April = 12 jt x 6/12": (lambda h: h["per_masa"][4]["kp_thr"], 6_000_000)})
    catat("KP-06", "THR prorata per bulan (Permenaker 6/2016)", "native" if ok else "GAGAL", b)
    ok, b, _ = _uji("kp09_lembur_jam.yaml",
                    _kasus(2024, {"gaji_pokok": 17_300_000}, {3: {"jam_pertama": 4, "jam_berikutnya": 6}}),
                    {"lembur Maret = 100.000 x (1,5x4 + 2x6)": (lambda h: h["per_masa"][3]["kp_lembur"], 1_800_000),
                     "bruto Maret": (lambda h: h["per_masa"][3]["bruto"], 19_100_000)})
    catat("KP-09", "lembur per jam 1/173 bertingkat", "native" if ok else "GAGAL", b)
    ok, b, _ = _uji("kp11_dasar_bpjs.yaml", _kasus(2024, {"gaji_pokok": 10_000_000, "tunjangan_tetap": 2_500_000}),
                    {"premi Kes = 4% x min(12,5 jt; 12 jt)": (lambda h: h["per_masa"][1]["kp_premi_kes"], 480_000),
                     "iuran JP Jan 2024 (batas 9.559.600)": (lambda h: h["per_masa"][1]["kp_iuran_jp"], 95_596),
                     "iuran JP Mar 2024 (batas 10.042.300)": (lambda h: h["per_masa"][3]["kp_iuran_jp"], 100_423)})
    catat("KP-11", "dasar upah BPJS = gaji + tunjangan tetap", "native" if ok else "GAGAL", b)
    ok, b, _ = _uji("kp12_prorata_kalender.yaml", _kasus(2024, {"gaji_pokok": 9_000_000}, {1: {"hari_kalender": 20}}),
                    {"gaji Jan = 9 jt x 20/30": (lambda h: h["per_masa"][1]["kp_gaji"], 6_000_000)})
    catat("KP-12", "prorata hari kalender /30", "native" if ok else "GAGAL", b)
    ok, b, h = _uji("kp14_natura_makan.yaml", _kasus(2024, {"gaji_pokok": 10_000_000, "nilai_makan": 600_000}),
                    {"bruto tidak memuat natura makan": (lambda h: h["per_masa"][1]["bruto"], 10_000_000)})
    catat("KP-14", "natura makan bersama seluruh pegawai (dikecualikan PMK 66/2023)", "native" if ok else "GAGAL", b)
    ok, b, _ = _uji("kp16_17_zakat_dplk.yaml", _kasus(2024, {"gaji_pokok": 10_000_000, "iuran_dplk": 300_000}),
                    {"zakat setahun": (lambda h: h["tahunan"]["zakat"], 3_000_000),
                     "iuran pengurang setahun": (lambda h: h["tahunan"]["iuran_pengurang"], 3_600_000)})
    catat("KP-16/17", "zakat via pemberi kerja & iuran DPLK pegawai", "native" if ok else "GAGAL", b)

    for kp, nama, bukti in [
        ("KP-07", "THR prorata per hari", "kb/perusahaan/perusahaan_x.yaml PX-THR-01 (E8 identik xlsx)"),
        ("KP-10", "lembur diklasifikasi perusahaan sebagai tidak teratur", "dinyatakan; DITOLAK lex superior + KONFLIK_WAJIB (E8, E4b)"),
        ("KP-13", "kenaikan gaji tengah bulan per hari kerja", "PX-GAJI-03 / PX-TUNJ-03 (E8 identik xlsx)"),
    ]:
        catat(kp, nama, "native", bukti)
    for kp, nama, bukti in [
        ("KP-01", "metode gross", "kasus.metode = gross"),
        ("KP-02", "metode gross-up", "kasus.metode = gross_up (titik tetap R24-05a/b)"),
        ("KP-05", "nett / THP tetap", "setara gross-up (REG-DITANGGUNG-02)"),
        ("KP-08", "bonus tahunan", "komponen kategori tidak_teratur"),
        ("KP-18", "keluar tengah tahun", "pegawai.bulan_terakhir_bekerja (REG-MT-01)"),
        ("KP-19", "rapel retroaktif", "transaksi bertanggal (REG-WAKTU-01) / R16-07 (rezim 2023)"),
        ("KP-20", "PPh 21 DTP", "pemberi_kerja.klu (aturan_dtp.yaml)"),
    ]:
        catat(kp, nama, "input", bukti)
    catat("KP-03", "gross-up hanya untuk gaji, bonus gross", "tidak_bisa",
          "regulasi tidak mendefinisikan PPh 'atas gaji saja' di bawah TER (tarif atas bruto masa total); "
          "butuh definisi atribusi pajak per komponen -> perlu aturan regulasi/tafsir baru, bukan sekadar KB perusahaan")
    catat("KP-04", "gross-up dengan plafon tunjangan pajak", "tidak_bisa",
          "R24-05a/b bersifat WAJIB; lapisan perusahaan tidak boleh menimpa titik tetap (lex superior). "
          "Bisa didukung bila tunjangan pajak dimodelkan sebagai komponen perusahaan 'default' -> keputusan desain")
    catat("KP-15", "fasilitas kendaraan/rumah dinas (penilaian PMK 66/2023)", "input",
          "aturan penilaian natura PMK 66 belum dikodifikasi; nilai natura dimasukkan HR sebagai komponen natura (objek)")
    return tabel


if __name__ == "__main__":
    t = jalankan()
    (ROOT / "eksperimen" / "hasil").mkdir(exist_ok=True)
    (ROOT / "eksperimen" / "hasil" / "ekspresivitas.json").write_text(json.dumps(t, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    from collections import Counter
    print(dict(Counter(r["status"] for r in t)), "dari", len(t))
    for r in t:
        print(f"  {r['kebijakan']:8} {r['status']:10} {r['nama']}" + ("" if r["status"] != "GAGAL" else f" | {r['bukti']}"))
