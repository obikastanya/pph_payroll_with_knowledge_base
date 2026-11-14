# 08_pegawai_sintetis — Data HR pegawai sintetis untuk demo kalkulator

`pegawai_sintetis.json` dibangkitkan oleh `bangkitkan.py`, berisi 8 pegawai dalam format data HR Perusahaan X, sama dengan Karyawan A. Data ini dipakai sebagai pilihan default di UI (tab Kalkulator) dan di tes E12 (KB vs tanpa KB).

```bash
env\Scripts\python.exe dataset\08_pegawai_sintetis\bangkitkan.py
```

## Prinsip: tidak ada angka gaji yang dikarang

**Gaji pokok** setiap pegawai **dibaca dari sel** berkas data publik di `dataset/04_data_publik/`. Ada dua sumber:
- **UMP:** Satu Data Kemnaker, `kemnaker_ump_<tahun>.xlsx`.
- **Rata-rata upah/gaji bersih:** BPS Sakernas, `bps_upah_*.csv`.

Berkas, baris, dan nilai sumbernya dicatat di `sumber_gaji` per pegawai.

| ID | Tahun | PTKP | Sumber gaji pokok | Skenario |
|---|---|---|---|---|
| SINT-01 | 2024 | TK/0 | UMP DKI Jakarta 2024 | Pegawai penuh setahun |
| SINT-02 | 2025 | K/1 | UMP Jawa Tengah 2025 | Penghasilan di bawah PTKP |
| SINT-03 | 2025 | K/0 | BPS: DKI, Informasi & Komunikasi, Agustus 2025 | — |
| SINT-04 | 2025 | K/2 | BPS: DKI, Jasa Keuangan & Asuransi, Agustus 2025 | — |
| SINT-05 | 2025 | TK/0 | BPS: DKI, Pertambangan & Penggalian, Februari 2025 | Upah tinggi, lapisan Pasal 17 lebih tinggi |
| SINT-06 | 2026 | TK/1 | UMP DKI Jakarta 2026 | Masuk 1 Juli (tengah tahun, tanpa THR) |
| SINT-07 | 2023 | K/3 | UMP DKI Jakarta 2023 | Rezim PER-16 |
| SINT-08 | 2026 | TK/0 | BPS: rata-rata nasional, Februari 2026 | Resign September |

## Asumsi yang dinyatakan eksplisit (bagian sintetis)

- **Status PTKP, tanggal masuk, dan bulan keluar** adalah variasi skenario. Ketiganya tidak diklaim berasal dari data.
- **Gaji pokok:**
  - Angka UMP yang bersen dibulatkan **ke atas** ke rupiah, karena upah tidak boleh di bawah UMP.
  - Rata-rata upah BPS adalah upah/gaji *bersih* seluruh komponen. Di sini angka itu dipakai sebagai acuan besaran gaji pokok, bukan klaim tentang struktur gaji sektornya.
- **Kehadiran penuh:** hari kerja = hari hadir = jumlah hari Senin–Jumat. Karena prorata bernilai 1, daftar libur nasional tidak memengaruhi gaji.
- **Tanggal Lebaran** mengikuti hari pertama Idul Fitri menurut SKB 3 Menteri. Keempat tanggal (2023–2026) diverifikasi lewat pengumuman resmi; URL-nya ada di `bangkitkan.py`. **THR dibayar H-7**, sesuai Permenaker 6/2016 Ps. 5(4).
- **Komponen yang tidak dipakai:** kenaikan gaji, tunjangan, lembur, komisi, insentif, dan kompensasi.
- **BPJS** aktif sejak bulan masuk. Tarif JKK 0,24%, sama dengan Perusahaan X.
- **KLU pemberi kerja** tidak diisi, karena data Perusahaan X dianonimkan. Akibatnya fasilitas DTP tidak berlaku untuk pegawai sintetis.
