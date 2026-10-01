"""Bangkitkan data pegawai sintetis untuk demo kalkulator (format data HR Perusahaan X).

Prinsip: tidak ada angka gaji yang dikarang. Gaji pokok setiap pegawai DIBACA dari berkas data publik di
dataset/04_data_publik (UMP Kemnaker, rata-rata upah/gaji bersih BPS Sakernas) dan sumbernya dicatat per pegawai.
Atribut lain (status PTKP, tanggal masuk/keluar) adalah variasi skenario yang dinyatakan eksplisit sebagai sintetis.

Asumsi yang dicatat di setiap pegawai:
- Gaji pokok = nilai sumber (UMP atau rata-rata upah BPS), dibulatkan KE ATAS ke rupiah bila bersen (upah tidak boleh
  di bawah UMP). Rata-rata upah BPS adalah upah/gaji BERSIH seluruh komponen; di sini dipakai sebagai acuan besaran
  gaji pokok (tanpa tunjangan), bukan klaim tentang struktur gaji sektor tersebut.
- Kehadiran penuh: hari kerja aktual = hari kerja penuh = jumlah hari Senin-Jumat (prorata = 1, sehingga daftar libur
  nasional tidak memengaruhi gaji).
- THR: Idul Fitri menurut SKB 3 Menteri tentang Hari Libur Nasional; dibayar H-7 (Permenaker 6/2016 Ps. 5(4):
  paling lambat 7 hari sebelum hari raya).
- Tanpa kenaikan gaji, tunjangan, lembur, komisi, insentif, kompensasi. BPJS TK & Kes sejak bulan masuk (atau Januari);
  kelas risiko JKK 0,24% (sama dengan Perusahaan X).

    env\\Scripts\\python.exe dataset\\08_pegawai_sintetis\\bangkitkan.py
"""
import calendar
import csv
import json
from datetime import date, timedelta
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
PUBLIK = ROOT / "dataset" / "04_data_publik"
KELUAR = Path(__file__).resolve().parent / "pegawai_sintetis.json"

# SKB 3 Menteri tentang Hari Libur Nasional dan Cuti Bersama (hari pertama Idul Fitri)
IDUL_FITRI = {   # diverifikasi 2026-10-01 lewat pencarian web atas pengumuman resmi/pemberitaan SKB 3 Menteri
    2023: ("2023-04-22", "SKB 3 Menteri Hari Libur Nasional & Cuti Bersama 2023 (Idul Fitri 1444 H: 22-23 April); "
                         "https://kemenag.go.id/read/catat-ini-daftar-hari-libur-nasional-dan-cuti-bersama-2023"),
    2024: ("2024-04-10", "SKB 3 Menteri Hari Libur Nasional & Cuti Bersama 2024 (Idul Fitri 1445 H: 10-11 April); "
                         "https://rri.co.id/daerah/1091606/jadwal-libur-nasional-2024-berdasarkan-skb-tiga-menteri"),
    2025: ("2025-03-31", "SKB 3 Menteri Hari Libur Nasional & Cuti Bersama 2025 (Idul Fitri 1446 H: 31 Maret-1 April); "
                         "https://www.kemenkopmk.go.id/pemerintah-tetapkan-hari-libur-nasional-dan-cuti-bersama-tahun-2025"),
    2026: ("2026-03-21", "SKB Menag/Menaker/MenPANRB No. 1497/2025, 2/2025, 5/2025 (Idul Fitri 1447 H: 21-22 Maret); "
                         "https://setneg.go.id/baca/index/inilah_skb_3_menteri_libur_nasional_dan_cuti_bersama_2026"),
}


def _bulat_atas(x):
    n = int(x)
    return n if n == x else n + 1


def ump(tahun, provinsi):
    berkas = PUBLIK / "kemnaker" / f"kemnaker_ump_{tahun}.xlsx"
    ws = openpyxl.load_workbook(berkas, read_only=True, data_only=True)["data"]
    for i, baris in enumerate(ws.iter_rows(values_only=True), start=1):
        sel = [c for c in baris if c is not None]
        if provinsi in [c.strip() for c in sel if isinstance(c, str)]:
            nilai = next(c for c in sel if isinstance(c, (int, float)) and not isinstance(c, bool) and c > 100_000)
            return _bulat_atas(nilai), {"berkas": berkas.relative_to(ROOT).as_posix(), "sheet": "data", "baris": i,
                                        "provinsi": provinsi, "nilai_sumber": str(nilai),
                                        "keterangan": f"UMP {provinsi} {tahun} (Satu Data Kemnaker)"}
    raise ValueError(f"UMP {provinsi} {tahun} tidak ditemukan")


def upah_bps(berkas, provinsi, sektor, tahun, periode):
    p = PUBLIK / "bps" / berkas
    with open(p, encoding="utf-8-sig", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            if (r["vervar_label"].strip().upper() == provinsi.upper() and r["turvar_label"].strip() == sektor
                    and r["tahun"] == str(tahun) and r["periode"] == periode):
                return int(r["nilai"]), {"berkas": p.relative_to(ROOT).as_posix(), "baris_csv": i, "key": r["key"],
                                         "provinsi": provinsi, "lapangan_usaha": sektor, "periode": f"{periode} {tahun}",
                                         "nilai_sumber": r["nilai"],
                                         "keterangan": "Rata-rata upah/gaji bersih sebulan buruh/karyawan/pegawai (BPS Sakernas)"}
    raise ValueError(f"upah BPS {provinsi}/{sektor}/{tahun}/{periode} tidak ditemukan")


def upah_bps_nasional(tahun, periode):
    p = PUBLIK / "bps" / f"bps_upah_rata2_17sektor_nasional_{tahun}.csv"
    with open(p, encoding="utf-8-sig", newline="") as f:
        for i, r in enumerate(csv.reader(f), start=1):
            if r and r[0] == "Rata-Rata" and periode in r:
                nilai = int(r[-3] if r[-1] != "Rupiah" else r[-2])
                return nilai, {"berkas": p.relative_to(ROOT).as_posix(), "baris_csv": i, "periode": f"{periode} {tahun}",
                               "nilai_sumber": str(nilai), "keterangan": "Rata-rata upah/gaji bersih nasional seluruh sektor (BPS Sakernas)"}
    raise ValueError("rata-rata nasional tidak ditemukan")


def hari_kerja(tahun, bulan):
    return sum(1 for d in range(1, calendar.monthrange(tahun, bulan)[1] + 1) if date(tahun, bulan, d).weekday() < 5)


def pegawai(pid, label, tahun, status, gaji, sumber, masuk, bulan_masuk=None, bulan_keluar=None):
    lebaran, dasar_lebaran = IDUL_FITRI[tahun]
    bayar = (date.fromisoformat(lebaran) - timedelta(days=7)).isoformat()
    bulan = list(range(bulan_masuk or 1, (bulan_keluar or 12) + 1))
    hr = {
        "gaji_pokok": gaji, "kenaikan_tanggal": f"{tahun}-01-01", "kenaikan_nominal": 0,
        "kenaikan_hk_sebelum": 0, "kenaikan_hk_sesudah": 0, "kenaikan_hari_sebelum": 0, "kenaikan_hari_sesudah": 0,
        "tunjangan_tetap_lama": 0, "tunjangan_prorata_lama": 0, "tunjangan_tetap_baru": 0, "tunjangan_prorata_baru": 0,
        "tanggal_masuk": masuk, "tanggal_masuk_awal_bulan": masuk[:8] + "01",
        "tanggal_lebaran": lebaran, "tanggal_thr_bayar": bayar,
        "bpjs_tk_mulai_bulan": bulan[0], "bpjs_kes_mulai_bulan": bulan[0], "kelas_jkk_persen": "0.24",
        "per_masa": {str(b): {"hk_penuh": hari_kerja(tahun, b), "hk_aktual": hari_kerja(tahun, b)} for b in bulan},
    }
    kasus = {
        "id": pid, "tahun_pajak": tahun, "cakupan": "setahun", "metode": "gross", "kurs": {}, "dtp": {},
        "pegawai": {"status_ptkp": status, "jenis_kelamin": "L", "punya_npwp": True, "subjektif_mulai_bulan": None,
                    "subjektif_akhir_bulan": None, "bulan_masuk": bulan_masuk, "bulan_terakhir_bekerja": bulan_keluar,
                    "periode_gaji": "bulanan", "hari_kerja_sebulan": None},
        "pemberi_kerja": {"klu": None, "jenis": "biasa"},
        "masa": [{"bulan": b, "komponen": []} for b in bulan], "data_hr": hr, "harapan": [],
    }
    return {"id": pid, "label": label, "sintetis": True, "sumber_gaji": sumber,
            "sumber_tanggal_lebaran": dasar_lebaran, "kasus": kasus}


def bangkitkan():
    daftar = []
    g, s = ump(2024, "DKI Jakarta")
    daftar.append(pegawai("SINT-01", "Staf UMP DKI Jakarta 2024 (TK/0)", 2024, "TK/0", g, s, "2023-01-02"))
    g, s = ump(2025, "Jawa Tengah")
    daftar.append(pegawai("SINT-02", "Operator UMP Jawa Tengah 2025 (K/1, di bawah PTKP)", 2025, "K/1", g, s, "2022-07-01"))
    g, s = upah_bps("bps_upah_provinsi_x_lapangan_usaha_17sektor_2025.csv", "DKI JAKARTA", "J Informasi dan Komunikasi", 2025, "Agustus")
    daftar.append(pegawai("SINT-03", "Staf TI, rata-rata upah sektor Informasi & Komunikasi DKI 2025 (K/0)", 2025, "K/0", g, s, "2021-03-01"))
    g, s = upah_bps("bps_upah_provinsi_x_lapangan_usaha_17sektor_2025.csv", "DKI JAKARTA", "K Jasa Keuangan dan Asuransi", 2025, "Agustus")
    daftar.append(pegawai("SINT-04", "Analis, rata-rata upah sektor Jasa Keuangan DKI 2025 (K/2)", 2025, "K/2", g, s, "2019-09-02"))
    g, s = upah_bps("bps_upah_provinsi_x_lapangan_usaha_17sektor_2025.csv", "DKI JAKARTA", "B Pertambangan dan Penggalian", 2025, "Februari")
    daftar.append(pegawai("SINT-05", "Insinyur, rata-rata upah sektor Pertambangan DKI 2025 (TK/0, upah tinggi)", 2025, "TK/0", g, s, "2020-01-06"))
    g, s = ump(2026, "DKI Jakarta")
    daftar.append(pegawai("SINT-06", "Pegawai baru Juli 2026, UMP DKI Jakarta 2026 (TK/1, masuk tengah tahun)", 2026, "TK/1", g, s,
                          "2026-07-01", bulan_masuk=7))
    g, s = ump(2023, "DKI Jakarta")
    daftar.append(pegawai("SINT-07", "Staf UMP DKI Jakarta 2023 (K/3, rezim PER-16)", 2023, "K/3", g, s, "2018-04-02"))
    g, s = upah_bps_nasional(2026, "Februari")
    daftar.append(pegawai("SINT-08", "Pegawai resign September 2026, rata-rata upah nasional 2026 (TK/0)", 2026, "TK/0", g, s,
                          "2024-03-01", bulan_keluar=9))
    return daftar


if __name__ == "__main__":
    data = bangkitkan()
    KELUAR.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    for d in data:
        print(d["id"], d["kasus"]["tahun_pajak"], d["kasus"]["pegawai"]["status_ptkp"], d["kasus"]["data_hr"]["gaji_pokok"], "|", d["label"])
