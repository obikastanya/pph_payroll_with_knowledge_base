"""Konversi kasus uji resmi -> format kanonik (input + harapan) untuk B1 dan KB.

Prinsip: konverter ini TIDAK menghitung pajak. Ia hanya (1) memetakan nama komponen ke
kategori pajak, (2) memetakan nama fakta harapan ke nama kanonik, dan (3) menempelkan
anotasi erratum/tafsir yang sudah diverifikasi dari gambar halaman (research_plan §9.1).
Nilai `nilai` = angka TERCETAK. Untuk erratum, `terkoreksi` diisi dengan derivasi pasal
yang ditulis manual di ERRATUM (beserta alasannya).

Jalankan dari root proyek:
    env\\Scripts\\python.exe dataset\\07_kasus_uji_resmi\\kanonik\\buat_kanonik.py
"""
import json
from fractions import Fraction
from pathlib import Path

DIR = Path(__file__).resolve().parent
SUMBER = DIR.parent

KATEGORI = {
    # penghasilan teratur
    "gaji": "teratur", "gaji_tunjangan": "teratur", "gaji_tunjangan_tetap": "teratur",
    "gaji_pokok": "teratur", "tunjangan": "teratur", "tunjangan_kinerja": "teratur",
    "tunjangan_jabatan": "teratur", "tunjangan_istri_anak": "teratur", "lembur": "teratur",
    "gaji_mingguan": "teratur", "gaji_harian": "teratur", "gaji_valas_usd": "teratur",
    "tunjangan_pajak": "teratur",
    # penghasilan tidak teratur
    "bonus": "tidak_teratur", "thr": "tidak_teratur", "gaji_ketiga_belas": "tidak_teratur",
    "rapel_tunjangan_kinerja": "tidak_teratur",
    "rapel_gaji_jan_mei": "rapel",
    # premi yang dibayar pemberi kerja (objek)
    "premi_jkk": "premi_objek", "premi_jkm": "premi_objek", "premi_jkk_jkm": "premi_objek",
    "premi_jkk_sebulan": "premi_objek", "premi_jkm_sebulan": "premi_objek",
    # natura / kenikmatan
    "natura_beras": "natura", "natura_gula": "natura", "natura_beasiswa": "natura",
    # pengurang
    "iuran_pensiun_pegawai": "iuran_pengurang", "iuran_jht_pegawai": "iuran_pengurang",
    "iuran_pensiun_pegawai_sebulan": "iuran_pengurang", "iuran_jht_pegawai_sebulan": "iuran_pengurang",
    "zakat": "zakat", "sumbangan_keagamaan_wajib": "zakat",
}
SATUAN = {"gaji_mingguan": "minggu", "gaji_harian": "hari"}
VALAS = {"gaji_valas_usd": "USD"}

DI_LUAR_MODEL = {
    "PER16-I.5": "pindah tugas antarcabang dengan pemotong berbeda (multi-pemotong)",
}

# Erratum terkonfirmasi (gambar halaman) -> koreksi berbasis pasal. Kunci: (id, fakta, bulan)
ERRATUM = {
    ("PMK168-B-I.6", "pph21", 1): (10_450_000, "19% x 55.000.000 = 10.450.000; dokumen mengalikan 55.500.000 (PMK 168 Ps. 15(1)a)"),
    ("PER16-I.1.2", "iuran_pensiun_bulanan", 7): (100_000, "narasi: iuran pegawai 100.000; jumlah pengurang & neto dokumen konsisten dgn 100.000"),
    ("PER16-I.1.3", "biaya_jabatan_bulanan", 7): (500_000, "plafon Rp500.000 sebulan (PER-16 Ps. 10(3)a); dokumen 525.000"),
    ("PER16-I.1.3", "total_pengurang_bulanan", 7): (550_000, "500.000 + 50.000 (turunan koreksi biaya jabatan)"),
    ("PER16-I.1.3", "neto_sebulan", 7): (9_950_000, "turunan koreksi biaya jabatan"),
    ("PER16-I.1.3", "neto_disetahunkan_bulanan", 7): (119_400_000, "turunan koreksi biaya jabatan"),
    ("PER16-I.1.3", "pkp_bulanan", 7): (60_900_000, "turunan koreksi biaya jabatan"),
    ("PER16-I.1.3", "pph21_setahun_bulanan", 7): (4_135_000, "5% x 50jt + 15% x 10,9jt (tarif pra-HPP)"),
    ("PER16-I.1.3", "pph21", 7): (344_583, "4.135.000 / 12 = 344.583,33"),
    ("PER16-I.2.3", "bruto", None): (6_584_500, "premi JKK/JKM DITAMBAHKAN ke bruto (PER-16 Ps. 1); dokumen mengurangkan"),
    ("PER16-I.2.3", "biaya_jabatan_bulanan", None): (329_225, "5% x 6.584.500"),
    ("PER16-I.2.3", "total_pengurang_bulanan", None): (494_225, "329.225 + 35.000 + 130.000"),
    ("PER16-I.2.3", "neto_sebulan", None): (6_090_275, "6.584.500 - 494.225"),
    ("PER16-I.2.3", "neto_disetahunkan_bulanan", None): (73_083_300, "12 x 6.090.275"),
    ("PER16-I.2.3", "pkp_bulanan", None): (10_083_000, "73.083.300 - 63.000.000 dibulatkan ke bawah ribuan"),
    ("PER16-I.2.3", "pph21_setahun_bulanan", None): (504_150, "5% x 10.083.000"),
    ("PER16-I.2.3", "pph21", None): (42_013, "504.150 / 12 = 42.012,5 -> BULAT-P16-01 default (tafsir; bawah: 42.012)"),
    ("PER16-I.2.3", "pph21_periode", None): (1_616, "42.013 / 26 = 1.615,9 -> 1.616 (bergantung tafsir pembulatan)"),
    ("PER16-I.6.2.2", "pph21_masa_terakhir", None): (858_334, "7.291.666 - 6.433.332 = 858.334; dokumen 858.333"),
    ("PER16-I.8", "total_pengurang_bulanan", 7): (475_000, "325.000 + 150.000; neto dokumen konsisten dgn 475.000"),
}

# Tafsir: (id, fakta, bulan) -> {aturan: varian yang mereproduksi angka tercetak}
TAFSIR = {
    ("PER16-I.1.4", "pph21", 7): {"BULAT-P16-01": "bawah"},
    ("PMK10-B-3", "biaya_jabatan", None): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "neto_setahun", None): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "pkp", None): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "pph21_setahun", None): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "pph21_masa_terakhir", None): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "pph21", 12): {"REG-BJ-02": "b"},
    ("PMK10-B-3", "pph21_dtp", 12): {"REG-BJ-02": "b"},
}

PER_MASA_TER = {"bruto": "bruto", "kategori_ter": "kategori_ter", "tarif_ter": "tarif_ter",
                "pph21": "pph21", "pph21_dtp": "pph21_dtp", "tunjangan_pajak_gross_up": "tunjangan_pajak"}
TAHUNAN = {"bruto_setahun": "bruto_setahun", "biaya_jabatan": "biaya_jabatan", "neto_setahun": "neto_setahun",
           "neto_disetahunkan": "neto_disetahunkan", "ptkp": "ptkp", "pkp": "pkp",
           "pph21_disetahunkan": "pph21_disetahunkan", "pph21_setahun": "pph21_setahun",
           "pph21_dipotong_sebelumnya": "pph21_dipotong_sebelumnya", "pph21_masa_terakhir": "pph21_masa_terakhir",
           "lebih_bayar_dapat_dikembalikan": "lebih_bayar_dikembalikan", "zakat": "zakat",
           "iuran_pensiun": "iuran_pengurang"}
PER_MASA_P16 = {"bruto": "bruto", "bruto_sebulan": "bruto", "biaya_jabatan": "biaya_jabatan_bulanan",
                "total_pengurang": "total_pengurang_bulanan", "neto_sebulan": "neto_sebulan",
                "neto_setahun": "neto_disetahunkan_bulanan", "neto_disetahunkan": "neto_disetahunkan_bulanan",
                "ptkp": "ptkp", "pkp": "pkp_bulanan", "pph21_setahun": "pph21_setahun_bulanan",
                "pph21_disetahunkan": "pph21_setahun_bulanan", "pph21": "pph21", "pph21_sebulan": "pph21",
                "pph21_minggu": "pph21_periode", "pph21_sehari": "pph21_periode",
                "pph21_tanpa_npwp": "pph21_tanpa_npwp", "pph21_tahun_2016": "pph21_bagian_tahun",
                "iuran_pensiun": "iuran_pensiun_bulanan", "iuran_jht": "iuran_jht_bulanan"}


def _nilai(v):
    if isinstance(v, float):
        return str(Fraction(str(v)))  # tarif sebagai string pecahan eksak, mis. "3/200"
    return v


def _cek(harapan, kasus_id, fakta, nilai, bulan=None):
    if nilai is None or isinstance(nilai, (dict, list)) or isinstance(nilai, bool) or isinstance(nilai, str) and fakta != "kategori_ter":
        return
    h = {"fakta": fakta, "bulan": bulan, "nilai": _nilai(nilai)}
    e = ERRATUM.get((kasus_id, fakta, bulan))
    if e:
        h["terkoreksi"], h["erratum"] = e
    t = TAFSIR.get((kasus_id, fakta, bulan))
    if t:
        h["tafsir"] = t
    harapan.append(h)


def _pegawai(inp):
    p = {
        "status_ptkp": inp["status_ptkp"], "jenis_kelamin": inp.get("jenis_kelamin"),
        "punya_npwp": True, "subjektif_mulai_bulan": None, "subjektif_akhir_bulan": None,
        "bulan_masuk": None, "bulan_terakhir_bekerja": None, "periode_gaji": inp.get("periode_gaji", "bulanan"),
        "hari_kerja_sebulan": inp.get("hari_kerja_sebulan"),
    }
    if inp.get("status_kawin"):  # karyawati: status keluarga + bukti suami tidak berpenghasilan
        n = inp.get("jumlah_tanggungan", inp.get("jumlah_tanggungan_keluarga", 0))
        p["status_ptkp"] = f"K/{n}"
        p["suami_tidak_berpenghasilan_terbukti"] = not inp.get("suami_berpenghasilan", True)
    for k_in, k_out in (("awal_kewajiban_subjektif", "subjektif_mulai_bulan"),
                        ("akhir_kewajiban_subjektif", "subjektif_akhir_bulan")):
        if inp.get(k_in):
            p[k_out] = int(inp[k_in][5:7])
    if inp.get("tanggal_masuk"):
        p["bulan_masuk"] = int(inp["tanggal_masuk"][5:7])
    return p


def konversi(d):
    inp = d["input"]
    kid = d["id"]
    masa = []
    for m in inp["masa"]:
        komp = []
        for kode, nominal in (m.get("komponen") or {}).items():
            if kode not in KATEGORI:
                raise SystemExit(f"{kid}: komponen tanpa kategori: {kode}")
            k = {"kode": kode, "kategori": KATEGORI[kode], "satuan_periode": SATUAN.get(kode, "bulan")}
            if kode in VALAS:
                k["valas"] = {"mata_uang": VALAS[kode], "jumlah": nominal}
            else:
                k["nominal"] = nominal
            komp.append(k)
        masa.append({"bulan": m.get("bulan"), "komponen": komp})
    pegawai = _pegawai(inp)
    bulan_ada = [m["bulan"] for m in masa if m["bulan"]]
    if inp.get("tanggal_keluar") and bulan_ada:
        pegawai["bulan_terakhir_bekerja"] = max(bulan_ada)  # asumsi A-04
    if kid == "PER16-II.1.1":
        pegawai["bulan_kerja_diketahui"] = 6  # pensiun 1 Juli sudah pasti sejak awal tahun
    pk = inp.get("pemberi_kerja") or {}
    kanon = {
        "id": kid, "sumber": d["sumber"], "rezim_dokumen": d["rezim"], "skenario": d["skenario"],
        "tahun_pajak": inp["tahun_pajak"],
        "cakupan": "setahun" if len(masa) > 1 or (d["expected"].get("tahunan")) else "satu_masa",
        "pegawai": pegawai,
        "pemberi_kerja": {"klu": pk.get("klu"), "jenis": pk.get("jenis", "biasa")},
        "metode": inp["metode"],
        "kurs": inp.get("kurs_menteri_keuangan") or {},
        "dtp": {"penghasilan_tetap_teratur_kontrak_januari": inp.get("penghasilan_tetap_teratur_menurut_kontrak")},
        "masa": masa,
    }
    if "riwayat" in inp:
        r = inp["riwayat"]
        kanon["riwayat"] = {"rapel": {"bulan": [1, 2, 3, 4, 5], "pph21_dipotong_per_bulan": r["pph21_dipotong_per_bulan_jan_mei"]}}
    harapan = []
    exp = d["expected"]
    ter = d["rezim"] == "TER_2024"
    for m in exp.get("per_masa") or []:
        b = m.get("bulan")
        peta = PER_MASA_TER if ter else PER_MASA_P16
        for k, v in m.items():
            if k in peta:
                if kid.startswith("PMK72") and k == "pph21_dtp" and b == 12 and m.get("pph21", 0) < 0:
                    continue  # kolom gabungan "DTP/pengembalian" -> dicek lewat lebih_bayar_dikembalikan
                _cek(harapan, kid, peta[k], v, b)
    for k, v in (exp.get("tahunan") or {}).items():
        if kid == "PER16-II.1.1" and k in ("pph21_dipotong_sebelumnya", "pph21_masa_terakhir"):
            continue  # dokumen menghitung 6 x 50.000 (termasuk Juni) lalu NIHIL; dicek via pph21 Juni
        if k in TAHUNAN:
            _cek(harapan, kid, TAHUNAN[k], v)
    for k, v in exp.items():
        if k in ("per_masa", "tahunan"):
            continue
        if k == "berhak_dtp":
            harapan.append({"fakta": "berhak_dtp", "bulan": None, "nilai": v})
        elif k in ("pph21_atas_bonus", "c_pph21_atas_bonus"):
            _cek(harapan, kid, "pph21_tidak_teratur", v)
        elif k == "pph21_atas_rapel":
            _cek(harapan, kid, "pph21_rapel", v)
    _harapan_khusus(kid, exp, harapan)
    kanon["harapan"] = harapan
    return kanon


def _harapan_khusus(kid, exp, h):
    """Struktur expected yang tidak seragam (contoh PER-16 multi-bagian)."""
    if kid == "PER16-I.12.1":
        for b in range(1, 7):
            _cek(h, kid, "pph21", exp["bulanan_jan_jun"]["pph21"], b)
        for b in range(7, 12):
            _cek(h, kid, "pph21", exp["bulanan_jul_nov"]["pph21"], b)
    elif kid == "PER16-I.6.2.1":
        for b in range(1, 9):
            _cek(h, kid, "pph21", exp["per_masa_bulanan"]["pph21"], b)
        t = exp["tahunan"]
        _cek(h, kid, "bruto_setahun", t["bruto_jan_sep"])
        _cek(h, kid, "neto_setahun", t["neto_9_bulan"])
    elif kid == "PER16-II.1.1":
        for b in range(1, 7):
            _cek(h, kid, "pph21", exp["bulanan"]["pph21"], b)
        t = exp["tahunan"]
        _cek(h, kid, "bruto_setahun", t["bruto_jan_jun"])
        _cek(h, kid, "neto_setahun", t["neto_6_bulan"])
    elif kid == "PER16-I.6.2.2":
        for b in range(1, 5):
            _cek(h, kid, "pph21_teratur", exp["a_gaji_bulanan"]["pph21"], b)
        dm = exp["d_perhitungan_kembali_mei"]
        for k_in, k_out in (("bruto_jan_mei", "bruto_setahun"), ("biaya_jabatan", "biaya_jabatan"),
                            ("neto_5_bulan", "neto_setahun"), ("neto_disetahunkan", "neto_disetahunkan"),
                            ("pkp", "pkp"), ("pph21_disetahunkan", "pph21_disetahunkan"),
                            ("pph21_terutang_5_bulan", "pph21_setahun"),
                            ("pph21_dipotong_sebelumnya", "pph21_dipotong_sebelumnya"),
                            ("pph21_masa_terakhir", "pph21_masa_terakhir")):
            _cek(h, kid, k_out, dm[k_in])
    elif kid in ("PER16-I.4.1", "PER16-I.4.2"):
        a, b = exp["a_gaji_dan_bonus_setahun"], exp["b_gaji_setahun"]
        _cek(h, kid, "pph21_setahun_dengan_tidak_teratur", a["pph21_setahun"])
        _cek(h, kid, "pph21_setahun_tanpa_tidak_teratur", b["pph21_setahun"])
        _cek(h, kid, "pkp_dengan_tidak_teratur", a["pkp"])
        _cek(h, kid, "pkp_tanpa_tidak_teratur", b["pkp"])
    elif kid == "PER16-I.3":
        r = exp["perhitungan_ulang_bulanan"]
        _cek(h, kid, "pph21", r["pph21_sebulan"], 6)
        _cek(h, kid, "pph21_rapel", exp["pph21_atas_rapel"])


def main():
    keluar = DIR
    indeks = []
    for f in sorted(SUMBER.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or not d.get("dalam_lingkup"):
            continue
        if d["id"] in DI_LUAR_MODEL:
            indeks.append({"id": d["id"], "status": "di_luar_model", "alasan": DI_LUAR_MODEL[d["id"]]})
            continue
        k = konversi(d)
        (keluar / f"{d['id']}.json").write_text(json.dumps(k, indent=1, ensure_ascii=False), encoding="utf-8")
        indeks.append({"id": d["id"], "status": "kanonik", "jumlah_harapan": len(k["harapan"]),
                       "erratum": sum("erratum" in x for x in k["harapan"]),
                       "tafsir": sum("tafsir" in x for x in k["harapan"])})
    (keluar / "indeks.json").write_text(json.dumps(indeks, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{sum(i['status'] == 'kanonik' for i in indeks)} kanonik, "
          f"{sum(i.get('jumlah_harapan', 0) for i in indeks)} harapan, "
          f"{sum(i.get('erratum', 0) for i in indeks)} erratum, {sum(i.get('tafsir', 0) for i in indeks)} tafsir")


if __name__ == "__main__":
    main()
