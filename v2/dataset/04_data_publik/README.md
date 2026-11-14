# 04_data_publik — Data publik Indonesia untuk kalibrasi profil karyawan sintetis

Folder ini dikumpulkan pada 2026-10-01. Isinya data publik untuk membuat profil karyawan sintetis (`dataset/06_kasus_uji_sintetis/`) yang realistis, ditambah sumber kasus uji resmi.

Aturan yang dipegang:
- **Tidak ada angka yang dikarang.** Setiap file berasal dari unduhan langsung, atau dari konversi format yang setia dengan file mentahnya ikut disimpan.
- Tabel yang tidak bisa diunduh hanya dicatat URL dan isinya (`status = hanya_referensi`).

## 1. Manifest

| File | Isi |
|---|---|
| `manifest_resmi.csv` | Sumber resmi (BPS, Kemnaker, Satu Data). 50 baris: 37 `diunduh` dan 13 `hanya_referensi`, lengkap dengan URL halaman, URL unduhan, lisensi, dimensi, dan catatan. |
| `manifest_sekunder_dan_kasus_uji.csv` | Data sekunder (Kaggle, Zenodo), sumber kasus uji resmi (PER-16/PJ/2016, indeks contoh PMK 168/2023), dan referensi jurnal. |

Kolom kedua manifest: `file_name, status, judul, penerbit, periode, source_page_url, download_url, lisensi, lisensi_url, format, dimensi, catatan`.

## 2. Data resmi yang diunduh

### 2.1 BPS (`bps/`)

**Upah/gaji bersih buruh (Sakernas)**, tabel dinamis 2025–2026. Masing-masing disimpan sebagai `*_raw.json` (respons asli), `*.csv` (bentuk panjang), dan `raw_html/` (halaman sumber):

| File | Periode |
|---|---|
| `bps_upah_provinsi_x_lapangan_usaha_17sektor_2025` | Feb & Agu 2025, 1.308 sel |
| `bps_upah_kelompok_umur_x_lapangan_usaha_17sektor_2025` | 2025 |
| `bps_upah_pendidikan_x_lapangan_usaha_17sektor_2025` | 2025 |
| `bps_upah_provinsi_x_jenis_pekerjaan_2026` | Feb 2026 |
| `bps_upah_pendidikan_x_jenis_pekerjaan_2026` | Feb 2026 |
| `bps_upah_kelompok_umur_x_jenis_pekerjaan_2026` | Feb 2026 |
| `bps_upah_rata2_17sektor_nasional_2026` | Feb 2026 |
| `bps_upah_rata2_triwulanan_17sektor_2026` | Feb & Mei 2026 |
| `bps_upah_per_jam_provinsi_2025` | 2025, upah per jam |

**Tabel statis 2023–2024**:
- `bps_upah_provinsi_x_jenis_pekerjaan_2024.xls`
- `bps_upah_pendidikan_x_jenis_pekerjaan_2024.xls`
- `bps_upah_kelompok_umur_x_lapangan_pekerjaan_2024.xls`
- `bps_upah_kelompok_umur_x_jenis_pekerjaan_2024.xls`
- `bps_upah_pendidikan_x_lapangan_pekerjaan_17sektor_2023.xlsx`

**Publikasi PDF**:
- `keadaan_pekerja_indonesia_agustus_2025.pdf` (394 hal.) dan `keadaan_pekerja_indonesia_februari_2026.pdf` (414 hal.). Keduanya memuat tabel distribusi buruh **menurut golongan upah** per jenis kelamin dan provinsi; tabel ini belum diekstrak ke CSV.
- `statistik_kesejahteraan_rakyat_2025.pdf` (584 hal.). Tabel 2.2–2.4 berisi persentase penduduk 10+ menurut status perkawinan (Susenas 2025).

**Status perkawinan dan rumah tangga (Susenas)**:
- `bps_status_perkawinan_penduduk10plus_provinsi_jk_2009_2018.xls`. Serinya berhenti di 2018; untuk data terbaru pakai PDF Statistik Kesra 2025.
- `bps_rumah_tangga_provinsi_jk_krt_banyaknya_art_2009_2025.xls` (banyaknya anggota rumah tangga: 1, 2–3, 4–5, 6+).
- `bps_rumah_tangga_daerah_umur_jk_krt_status_perkawinan_2009_2025.xls`.

**UMR lama**: `bps_ump_upah_minimum_regional_provinsi_2020.*`, hanya sebagai pembanding.

**Lisensi BPS**: Syarat & Ketentuan BPS. Konten boleh dipakai, disalin, diubah, dan dipakai komersial dengan **wajib mencantumkan kredit** (judul, tanggal akses, tautan). Ini **bukan lisensi CC standar**, dan BPS dapat mengubah atau menarik kontennya. Kutipan dan URL lengkap ada di kolom `lisensi_url`.

### 2.2 Kemnaker (`kemnaker/`)

- `kemnaker_ump_2018_2022.xlsx`, `kemnaker_ump_2023.xlsx`, `kemnaker_ump_2024.xlsx`, `kemnaker_ump_2025.xlsx`, `kemnaker_ump_2026.xlsx`: UMP per provinsi dari Satu Data Kemnaker.
- Dasar hukum menurut abstraksi dataset:

| Tahun | Dasar hukum |
|---|---|
| 2023 | Permenaker 18/2022 |
| 2024 | PP 51/2023 |
| 2025 | Permenaker 16/2024 |
| 2026 | PP 49/2025 (terverifikasi oleh agen pengunduh) |

- Lisensi: halaman dataset tidak menyatakan lisensi eksplisit. Panduan Portal Satu Data dikutip di manifest. Perlakukan sebagai data pemerintah terbuka dengan atribusi.

### 2.3 Satu Data daerah (`satudata/`)

- `satudata_sumsel_ump_umk_2024.xlsx`: contoh UMK resmi (1 UMP + 17 kab/kota Sumatera Selatan).
- Kualitas: 9 kab/kota bernilai 0 dan 1 kosong. Jangan dipakai tanpa pembersihan.
- **Tidak ada tabel UMK nasional resmi yang terkonsolidasi.** UMK ditetapkan per Kepgub (lihat baris `hanya_referensi`).

## 3. Data sekunder dan kasus uji (manifest kedua)

| File/folder | Sumber | Lisensi | Kegunaan | Catatan |
|---|---|---|---|---|
| `sekunder_kaggle/linkgish_.../Indonesian Salary by Region (1997-2025).csv` | Kaggle (M Razif Rizqullah) | Apache 2.0 (metadata Kaggle) | Deret UMP panjang (1997–2025) | Kompilasi sekunder; cek silang dengan `kemnaker/` |
| `sekunder_kaggle/adriantowijaya_.../UMP Indonesia 2018 - 2025.xlsx` | Kaggle (Adrianto M. Wijaya), mengaku bersumber Kemnaker | Apache 2.0 | Pembanding UMP 2018–2025 | 38 provinsi; tidak ada 2026 |
| `sekunder_kaggle/wowevan_.../*.csv` | Kaggle (WowEvan), turunan BPS | CC0 | Upah **per jam** 2015–2022, UMP 2002–2022, garis kemiskinan, pengeluaran | Satuannya per jam, bukan per bulan |
| `sekunder_zenodo/zenodo_18162371_glints_jobstreet_ds/*.csv` | Zenodo (Zainuddin, 2026) | CC-BY-4.0 | Rentang gaji iklan lowongan data science (Mar–Apr 2025) | Sekitar 429 baris bergaji. Bidang sempit; nilai iklan, bukan realisasi. Relevansi rendah. |
| `sekunder_zenodo/zenodo_pph21_slide_uwp/*.pps` | Zenodo (Rusdiyanto, Univ. Wijaya Putra, 2022) | CC-BY-4.0 | Contoh hitung PPh 21 rezim 2022 (pra-TER) | Belum diekstrak; kebenaran **tidak diverifikasi** |
| `kasus_uji_resmi/PER_16_PJ_2016_SALINAN.pdf` | DJP, pajak.go.id | Peraturan, bukan objek hak cipta (UU 28/2014 Ps. 42) | Contoh resmi metode pra-TER (relevan untuk tahun pajak 2023) | PDF pindaian 67 hal. tanpa teks. Contohnya memakai tarif pra-HPP, jadi harus disesuaikan ke tarif HPP untuk 2023. |
| `kasus_uji_resmi/pmk168_2023_indeks_contoh.csv` | Diturunkan dari `01_regulasi/PMK_168_2023.pdf` | Peraturan | Indeks 29 contoh resmi: Bagian B (25 contoh, Tuan A–Z) dan Bagian C (4 contoh PNS), dengan halaman PDF | Hanya indeks; angka tidak ditranskripsi di sini |

**Transkripsi contoh resmi** (PER-16/PJ/2016 dan PMK 168/2023) sedang dikerjakan terpisah di **`dataset/07_kasus_uji_resmi/`**, dengan file seperti `PER16_I.1.1.json` dan seterusnya. Folder itu menjadi sumber *ground truth*; folder ini hanya menyimpan sumber mentah dan indeks.

Jurnal studi kasus (Widyatama/BES, JURIMBIK, LPKIA, ResearchGate 383382086) hanya dicatat sebagai referensi. Angkanya **belum diverifikasi** dan tidak boleh dipakai sebagai ground truth.

## 4. Pemetaan ke kalibrasi profil sintetis

| Parameter profil | Sumber utama | Catatan |
|---|---|---|
| Upah per provinsi × sektor | `bps_upah_provinsi_x_lapangan_usaha_17sektor_2025.csv` | Rata-rata **bersih**, bukan distribusi |
| Upah per umur / pendidikan / jenis pekerjaan | tabel `bps_upah_*` 2023–2026 | Rata-rata saja |
| Bentuk distribusi upah | PDF Keadaan Pekerja (tabel golongan upah) | Golongan teratas terbuka ("2 jt ke atas" atau sejenisnya), jadi ekor atas tidak teridentifikasi |
| Batas bawah gaji (lantai legal) | `kemnaker_ump_20xx.xlsx` | UMP adalah nilai bruto, cocok sebagai batas bawah bruto. UMK tidak tersedia secara nasional. |
| Status kawin (TK vs K) | Statistik Kesra 2025 Tab. 2.2–2.4; xls 2009–2018 | Data penduduk 10+, bukan khusus pekerja |
| Jumlah tanggungan (0–3) | `bps_rumah_tangga_*_banyaknya_art_*` | Hanya proksi: ukuran rumah tangga ≠ tanggungan PTKP (maksimum 3) |
| Kasus ekstrem / gaji tinggi | Zenodo Glints/JobStreet (terbatas) | Ekor atas tetap perlu asumsi eksplisit yang didokumentasikan |

## 5. Peringatan penting

1. **Upah Sakernas adalah upah/gaji BERSIH** (jawaban responden, definisi BPS), bukan bruto payroll. Kalkulator PPh 21 bekerja dari bruto. Konversi bersih → bruto adalah asumsi model yang harus dinyatakan. Opsinya: inversi BPJS dan PPh, atau rasio tetap dengan analisis sensitivitas. Konversi ini tidak boleh disajikan sebagai data.
2. Tabel BPS umumnya berupa **rata-rata**. Distribusi hanya tersedia sebagai golongan upah dengan kelas teratas terbuka. Mikrodata Sakernas berbayar (layanan Silastik) dan tidak diunduh.
3. **Tidak ada tabel status perkawinan khusus pekerja** dan tidak ada tabel jumlah anak yang siap pakai. Status PTKP harus disampel dari proksi penduduk atau rumah tangga.
4. Seri historis lengkap tabel dinamis BPS (2023–2024 dalam format dinamis) memerlukan **API key WebAPI BPS** (gratis, perlu registrasi). Kunci itu tidak dipakai, jadi tahun-tahun tersebut diambil dari tabel statis xls.
5. Lisensi BPS dan Satu Data bukan lisensi CC standar. Selalu cantumkan atribusi (judul, tanggal akses 2026-10-01, URL) sesuai manifest.
6. Data Kaggle adalah kompilasi sekunder. Dahulukan `kemnaker/` untuk angka UMP yang dikutip di laporan.
