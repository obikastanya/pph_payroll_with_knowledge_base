# Kasus Uji Resmi PPh Pasal 21 (gold standard V1)

Folder ini memuat **transkripsi contoh perhitungan resmi** (contoh perhitungan di dalam regulasi) yang menjadi oracle tertinggi (V1) dalam piramida validasi `research_plan.md` §9.1. Tidak ada SME dan kalkulator eksisting tidak dipercaya, sehingga **satu-satunya acuan adalah angka yang tercetak di dokumen**. Semua angka di kunci `expected` disalin apa adanya, termasuk angka yang diduga salah (ralat contoh resmi). Hasil hitung ulang diletakkan terpisah di `cek_aritmetika`, `cek_tabel_rinci`, dan (untuk PER-16) `relevansi_tarif_2023`.

Ringkasan isi:
- **46 kasus dalam lingkup** (pegawai tetap), masing-masing satu berkas JSON.
- **4 kasus di luar lingkup yang tetap ditranskripsi lengkap** (multi pemberi kerja, tanpa NPWP, pensiunan) - berkas JSON dengan `dalam_lingkup: false`.
- **38 contoh di luar lingkup ditranskripsi ringkas** (pegawai tidak tetap, bukan pegawai, pensiunan, komisaris, peserta kegiatan, mantan pegawai, PPh 26, DTP pegawai tidak tetap) di `di_luar_lingkup.json`.
- `index.csv` = manifest yang sama dengan tabel di bawah (satu baris per kasus, termasuk entri ringkas).

## Sumber dan jumlah contoh yang ditemukan

| Sumber | Lokasi contoh | Contoh ditemukan | Dalam lingkup (ditranskripsi penuh) |
|---|---|---|---|
| PMK 168/2023 | Lampiran B Bagian Kedua (hlm. 33-57) dan Lampiran C Bagian Kedua (hlm. 60-69) | 31 contoh: B.I pegawai tetap 10 (I.2.2.2 memuat 2 varian), B.II-VII lainnya 17, C (PNS/pensiunan PNS) 4 | 13 berkas (B: 10; C: 3 bagian PNS) + 3 berkas lengkap di luar lingkup (B-I.2.2.2b, C-I.1.3b, C-I.1.4b) |
| PER-16/PJ/2016 | Lampiran Bagian Kedua (PDF hlm. 27-67; hasil pindai) | 41 contoh: I (pegawai tetap) 22 bernomor + I.12.2 (hanya merujuk I.6.2), II pensiun 3 (II.1.1 = pegawai tetap s.d. pensiun), III harian/lepas 6, IV 3, V 5, VI 1, VII 1 | 22 berkas (I.1.1-I.12.1 kecuali I.11, ditambah II.1.1) + 1 berkas lengkap di luar lingkup (I.11 NPWP) |
| PP 58/2023 | Penjelasan Pasal 2 ayat (1) (PDF hlm. 8-9) | 1 | 1 |
| PMK 10/2025 | Lampiran B (hlm. 17-23) | 5 (Tuan A-E) | 4 (Tuan E = pegawai tidak tetap) |
| PMK 72/2025 | Lampiran B (hlm. 37-49) + Lampiran C (format kertas kerja) | 8 (no. 1-5 identik secara numerik dengan PMK 10/2025; no. 6-8 baru) | 3 baru (no. 6-8); no. 1-4 dicatat sebagai `duplikat_identik_di` pada berkas PMK10 |
| PMK 105/2025 | Lampiran B (hlm. 38-43), TA 2026 | 4 (Tuan A, B, C, E) | 3 |
| FAQ PMK 72/2025 (DJP) | seluruh dokumen | 0 contoh hitung (hanya tanya-jawab kelayakan DTP) | 0 |

Catatan: duplikasi PMK 72/2025 no. 1-4 dicek dengan membandingkan seluruh deret angka teks PDF kedua dokumen (474 angka, identik).

## Struktur berkas JSON

```
id, sumber{regulasi, bagian, halaman_pdf[, halaman_dokumen, duplikat_identik_di]}, rezim (TER_2024 | PER16_2023),
dalam_lingkup, catatan_lingkup, skenario[], uraian,
input{tahun_pajak, status_ptkp, jenis_kelamin (L/P/tidak_disebutkan), metode, tanggal_masuk/keluar, masa[{bulan, komponen{...}}], info_tambahan},
expected{per_masa[...], tahunan{...}, ...}   <- HANYA angka yang tercetak di dokumen
langkah_resmi[]           <- kutipan (hampir) verbatim baris perhitungan dokumen
catatan_transkripsi       <- keraguan, artefak OCR yang diselesaikan via citra halaman, dugaan erratum
cek_aritmetika[]          <- hitung ulang setiap baris (dokumen vs hitung_ulang)
cek_tabel, cek_tabel_rinci[]  <- pencocokan dengan tables/ter_bulanan.csv, tarif_pasal17.csv, ptkp.csv
ringkasan_cek, dugaan_erratum, catatan_minor, verifikasi_pass2
relevansi_tarif_2023      <- (PER-16 saja) PPh atas PKP dokumen dihitung dgn tarif UU 36/2008 dan UU HPP
```

Konvensi: nilai negatif pada `pph21` masa terakhir = "lebih dipotong" (dokumen menulis dalam kurung). Komponen pengurang (`iuran_pensiun_pegawai`, `iuran_jht_pegawai`, `zakat`, `sumbangan_keagamaan_wajib`) dicantumkan di `komponen` tetapi bukan bagian bruto. `metode` memakai `gross`, `gross_up`, dan satu perluasan `ditanggung_pemberi_kerja` (PER16-I.8). Kunci `input` yang tidak disebut dokumen tidak diisi (mis. jenis kelamin di PER-16 bila tidak ada kata "karyawati"/"Tuan").

**Peringatan rezim PER-16.** Semua contoh PER-16 bertahun 2016 dan memakai lapisan tarif Pasal 17 **UU 36/2008** (5% s.d. Rp50 juta). Untuk tahun pajak 2023 berlaku lapisan **UU HPP** (5% s.d. Rp60 juta). Kunci `rezim: PER16_2023` menandai *metode* (disetahunkan, PPh sebulan = PPh setahun/12), bukan tahun contoh. Hanya contoh dengan PKP <= Rp50 juta yang hasilnya identik di kedua tarif (lihat `relevansi_tarif_2023.rincian[].hasil_sama_di_kedua_tarif`). PER16-I.1.3, I.1.5, I.6.1.2, I.6.2.2 dan I.7 **tidak** identik.

## Manifest - kasus dalam lingkup

| id | sumber (hlm. PDF) | rezim | skenario | dalam_lingkup | cek aritmetika | cek tabel | dugaan erratum | verifikasi pass 2 |
|---|---|---|---|---|---|---|---|---|
| [PER16-I.1.1](PER16_I.1.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.1.1 (gaji bulanan), Retto (hlm. 27 28) | PER16_2023 | metode_PER16_bulanan, iuran_pensiun | ya | 7/7 cocok | cocok | tidak | cocok |
| [PER16-I.1.2](PER16_I.1.2.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.1.2, Bambang Eko (hlm. 28 29) | PER16_2023 | metode_PER16_bulanan, premi_JKK_JKM, iuran_JHT, iuran_pensiun | ya | 11/12 cocok | cocok | ya | cocok |
| [PER16-I.1.3](PER16_I.1.3.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.1.3, Tanti Agustin (karyawati, suami tanpa penghasilan) (hlm. 29) | PER16_2023 | metode_PER16_bulanan, pegawai_wanita_kawin, lembur, iuran_pensiun | ya | 5/6 cocok | cocok | ya | cocok |
| [PER16-I.1.4](PER16_I.1.4.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.1.4, Ikha Hapsari (karyawati, suami PNS) (hlm. 30) | PER16_2023 | metode_PER16_bulanan, pegawai_wanita_kawin, lembur, premi_JKK_JKM, iuran_JHT, iuran_pensiun | ya | 10/10 cocok | cocok | tidak | cocok |
| [PER16-I.1.5](PER16_I.1.5.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.1.5, dr. Aulia Rais (pegawai tetap rumah sakit) (hlm. 30 31) | PER16_2023 | metode_PER16_bulanan, plafon_biaya_jabatan, iuran_pensiun | ya | 6/6 cocok | cocok | tidak | cocok |
| [PER16-I.10](PER16_I.10.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.10 (natura dari pemberi kerja PPh final/deemed profit), Maydina Aprilianto (hlm. 47 48) | PER16_2023 | metode_PER16_bulanan, natura_kenikmatan | ya | 9/9 cocok | cocok | tidak | cocok |
| [PER16-I.12.1](PER16_I.12.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.12.1.b (Masa Pajak Terakhir Desember, penghasilan tetap berubah), Sisusa (hlm. 50 51 52) | PER16_2023 | metode_PER16_bulanan, masa_terakhir_desember, kenaikan_gaji, iuran_pensiun | ya | 18/18 cocok | cocok | tidak | cocok |
| [PER16-I.2.1](PER16_I.2.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.2.1 (gaji mingguan), Oka Sagala (hlm. 31 32) | PER16_2023 | metode_PER16_bulanan, gaji_mingguan | ya | 6/7 cocok | cocok | ya | cocok |
| [PER16-I.2.2](PER16_I.2.2.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.2.2 (gaji mingguan), Muhammad Shodiq (hlm. 32) | PER16_2023 | metode_PER16_bulanan, gaji_mingguan, premi_JKK_JKM, iuran_JHT, iuran_pensiun, pembulatan_PKP | ya | 11/11 cocok | cocok | tidak | cocok |
| [PER16-I.2.3](PER16_I.2.3.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.2.3 (gaji harian pegawai tetap), Indradi (hlm. 33) | PER16_2023 | metode_PER16_bulanan, gaji_harian, premi_JKK_JKM, iuran_JHT, iuran_pensiun, pembulatan_PKP | ya | 10/13 cocok | cocok | ya | cocok; dikonfirmasi dua kesalahan cetak (bruto & jumlah peng |
| [PER16-I.3](PER16_I.3.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.3 (uang rapel), Retto (hlm. 33 34) | PER16_2023 | metode_PER16_bulanan, rapel, iuran_pensiun | ya | 10/10 cocok | cocok | tidak | cocok |
| [PER16-I.4.1](PER16_I.4.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.4.1 (bonus), Sudiro (hlm. 34 35) | PER16_2023 | metode_PER16_bulanan, bonus, metode_selisih_tidak_teratur, iuran_pensiun | ya | 7/7 cocok | cocok | tidak | cocok |
| [PER16-I.4.2](PER16_I.4.2.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.4.2 (bonus), Shanaya Aqeela (karyawati) (hlm. 35 36) | PER16_2023 | metode_PER16_bulanan, bonus, metode_selisih_tidak_teratur, premi_JKK_JKM, iuran_JHT, iuran_pensiun, pegawai_wanita | ya | 9/9 cocok | cocok | tidak | cocok |
| [PER16-I.5](PER16_I.5.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.5 (pegawai dipindahtugaskan dalam tahun berjalan), Didin Qomarudin (hlm. 36 37 38 39 40) | PER16_2023 | metode_PER16_bulanan, pindah_tugas_cabang, masa_terakhir_desember, iuran_pensiun | ya | 17/18 cocok | cocok | ya | cocok setelah perbaikan |
| [PER16-I.6.1.1](PER16_I.6.1.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.6.1.1 (mulai bekerja pertengahan tahun, subjektif sejak awal tahun), Suwondo (hlm. 40 41) | PER16_2023 | metode_PER16_bulanan, masuk_tengah_tahun, plafon_biaya_jabatan, iuran_pensiun | ya | 6/6 cocok | cocok | tidak | cocok |
| [PER16-I.6.1.2](PER16_I.6.1.2.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.6.1.2 (kewajiban subjektif dimulai setelah awal tahun), David Raisita (hlm. 41 42) | PER16_2023 | metode_PER16_bulanan, masuk_tengah_tahun, subjektif_parsial_disetahunkan, plafon_biaya_jabatan | ya | 6/6 cocok | cocok | tidak | cocok |
| [PER16-I.6.2.1](PER16_I.6.2.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.6.2.1 (berhenti bekerja, subjektif tetap), Sulistiyo Wibowo (hlm. 42 43) | PER16_2023 | metode_PER16_bulanan, keluar_tengah_tahun, masa_terakhir_bulan_keluar, iuran_pensiun, lebih_potong | ya | 12/12 cocok | cocok | tidak | cocok |
| [PER16-I.6.2.2](PER16_I.6.2.2.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.6.2.2 (berhenti dan kehilangan kewajiban subjektif), Lewis Oshea (hlm. 43 44 45) | PER16_2023 | metode_PER16_bulanan, keluar_tengah_tahun, subjektif_parsial_disetahunkan, bonus, metode_selisih_tidak_teratur, plafon_biaya_jabatan | ya | 11/12 cocok | cocok | ya | cocok setelah perbaikan |
| [PER16-I.7](PER16_I.7.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.7 (mata uang asing), Neill Mc Leary (hlm. 45) | PER16_2023 | metode_PER16_bulanan, mata_uang_asing, plafon_biaya_jabatan | ya | 7/7 cocok | cocok | tidak | cocok |
| [PER16-I.8](PER16_I.8.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.8 (PPh ditanggung pemberi kerja), Adi Putro (hlm. 46) | PER16_2023 | metode_PER16_bulanan, pph_ditanggung_pemberi_kerja, iuran_pensiun | ya | 5/6 cocok | cocok | ya | cocok |
| [PER16-I.9](PER16_I.9.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.9 (tunjangan pajak), Edward Simatupang (hlm. 47) | PER16_2023 | metode_PER16_bulanan, tunjangan_pajak, iuran_pensiun | ya | 7/7 cocok | cocok | tidak | cocok |
| [PER16-II.1.1](PER16_II.1.1.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, II.1.1 (PPh 21 di tempat pemberi kerja sebelum pensiun), Hari Irawan (hlm. 52 53 54) | PER16_2023 | metode_PER16_bulanan, keluar_tengah_tahun, masa_terakhir_bulan_keluar, plafon_biaya_jabatan, iuran_pensiun | ya | 8/8 cocok | cocok | tidak | cocok |
| [PMK105-B-1](PMK105_B_1.json) | PMK 105/2025 - Lampiran huruf B nomor 1, Tuan A (Tahun Anggaran 2026) (hlm. 38 39) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP | ya | 31/31 cocok | cocok | tidak | cocok |
| [PMK105-B-2](PMK105_B_2.json) | PMK 105/2025 - Lampiran huruf B nomor 2, Tuan B (Tahun Anggaran 2026) (hlm. 39 40 41) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, bonus, kategori_B, kenaikan_gaji | ya | 44/44 cocok | cocok | tidak | cocok setelah perbaikan |
| [PMK105-B-3](PMK105_B_3.json) | PMK 105/2025 - Lampiran huruf B nomor 3, Tuan C (Tahun Anggaran 2026) (hlm. 41 42 43) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, bonus, masuk_tengah_tahun, lebih_potong | ya | 37/39 cocok | cocok | ya | cocok setelah perbaikan |
| [PMK10-B-1](PMK10_B_1.json) | PMK 10/2025 - Lampiran huruf B nomor 1, Tuan A (hlm. 17 18) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP | ya | 31/31 cocok | cocok | tidak | cocok |
| [PMK10-B-2](PMK10_B_2.json) | PMK 10/2025 - Lampiran huruf B nomor 2, Tuan B (hlm. 18 19 20) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, bonus, kategori_B, kenaikan_gaji | ya | 44/44 cocok | cocok | tidak | cocok |
| [PMK10-B-3](PMK10_B_3.json) | PMK 10/2025 - Lampiran huruf B nomor 3, Tuan C (hlm. 20 21 22) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, bonus, masuk_tengah_tahun, lebih_potong | ya | 38/39 cocok | cocok | ya | cocok setelah perbaikan |
| [PMK10-B-4](PMK10_B_4.json) | PMK 10/2025 - Lampiran huruf B nomor 4, Tuan D (hlm. 22) | TER_2024 | DTP, kelayakan_DTP_tidak_berhak | ya | 1/1 cocok | n/a | tidak | cocok |
| [PMK168-B-I.1](PMK168_B_I.1.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.1 (Pegawai Tetap yang menerima penghasilan dalam satu Tahun Pajak), Tuan A (hlm. 33 34 35) | TER_2024 | TER_bulanan, masa_terakhir_desember, THR, bonus, lembur, premi_JKK_JKM, iuran_pensiun, zakat | ya | 31/31 cocok | cocok | tidak | cocok |
| [PMK168-B-I.2.1.1](PMK168_B_I.2.1.1.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.1.1 (mulai bekerja pertengahan tahun, kewajiban subjektif sudah ada sejak awal tahun), Tuan B (hlm. 35 36) | TER_2024 | TER_bulanan, masa_terakhir_desember, masuk_tengah_tahun, iuran_pensiun, lebih_potong | ya | 7/7 cocok | cocok | tidak | cocok |
| [PMK168-B-I.2.1.2](PMK168_B_I.2.1.2.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.1.2 (kewajiban subjektif dimulai setelah awal tahun dan mulai bekerja pada tahun berjalan), Tuan C (hlm. 37 38) | TER_2024 | TER_bulanan, masa_terakhir_desember, masuk_tengah_tahun, subjektif_parsial_disetahunkan, zakat_sumbangan_keagamaan | ya | 10/10 cocok | cocok | tidak | cocok |
| [PMK168-B-I.2.2.1](PMK168_B_I.2.2.1.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.2.1 (berhenti bekerja, masih memiliki kewajiban pajak subjektif), Tuan D di PT W (hlm. 38 39) | TER_2024 | TER_bulanan, masa_terakhir_bulan_keluar, keluar_tengah_tahun, iuran_pensiun, lebih_potong | ya | 11/11 cocok | cocok | tidak | cocok |
| [PMK168-B-I.2.2.2a](PMK168_B_I.2.2.2a.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.2.2 (berhenti di satu pemberi kerja dan mulai bekerja di pemberi kerja lain), varian 'Tuan D tidak menyerahkan bukti pemotongan dari PT W ke PT AB' (hlm. 40 41) | TER_2024 | TER_bulanan, masa_terakhir_desember, masuk_tengah_tahun, iuran_pensiun, lebih_potong | ya | 8/8 cocok | cocok | tidak | cocok |
| [PMK168-B-I.2.2.3](PMK168_B_I.2.2.3.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.2.3 (berhenti bekerja dan sekaligus kehilangan kewajiban pajak subjektif), Tuan E (hlm. 42 43) | TER_2024 | TER_bulanan, masa_terakhir_bulan_keluar, keluar_tengah_tahun, subjektif_parsial_disetahunkan | ya | 12/12 cocok | cocok | tidak | cocok |
| [PMK168-B-I.3](PMK168_B_I.3.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.3 (penghasilan dalam mata uang asing), Tuan F (hlm. 44) | TER_2024 | TER_bulanan, mata_uang_asing, kategori_C | ya | 2/2 cocok | cocok | tidak | cocok |
| [PMK168-B-I.4](PMK168_B_I.4.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.4 (PPh 21 ditanggung pemberi kerja, full gross up), Tuan G (hlm. 44) | TER_2024 | TER_bulanan, gross_up | ya | 3/3 cocok | cocok | tidak | cocok |
| [PMK168-B-I.5](PMK168_B_I.5.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.5 (tunjangan pajak), Tuan H (hlm. 45) | TER_2024 | TER_bulanan, tunjangan_pajak, kategori_B, iuran_pensiun_tidak_mengurangi_bruto_masa | ya | 2/2 cocok | cocok | tidak | cocok; catatan 'tunjangan pajak jumlah tetap' kini ditandai  |
| [PMK168-B-I.6](PMK168_B_I.6.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.6 (natura dan/atau kenikmatan), Tuan I (hlm. 45 46) | TER_2024 | TER_bulanan, natura_kenikmatan, kategori_B | ya | 2/3 cocok | cocok | ya | cocok |
| [PMK168-C-I.1.1](PMK168_C_I.1.1.json) | PMK 168/2023 - Lampiran huruf C, Bagian Kedua, I.1.1 (Pejabat Negara/PNS/TNI/POLRI dengan penghasilan tetap dan teratur), Tuan A PNS III/c (hlm. 60 61 62) | TER_2024 | TER_bulanan, masa_terakhir_desember, kategori_B, penghasilan_tidak_teratur_gaji13_rapel, PNS, DTP_pemerintah_APBN | ya | 30/30 cocok | cocok | tidak | cocok |
| [PMK168-C-I.1.3a](PMK168_C_I.1.3a.json) | PMK 168/2023 - Lampiran huruf C, Bagian Kedua, I.3, bagian '1. Penghasilan yang diterima dan/atau diperoleh dari KPP A', Tuan C PNS (hlm. 64 65) | TER_2024 | TER_bulanan, masa_terakhir_desember, kategori_B, penghasilan_tidak_teratur_gaji13_rapel, PNS, pembulatan_PKP, DTP_pemerintah_APBN | ya | 30/30 cocok | cocok | tidak | cocok setelah perbaikan |
| [PMK168-C-I.1.4a](PMK168_C_I.1.4a.json) | PMK 168/2023 - Lampiran huruf C, Bagian Kedua, I.4 (Pensiunan yang menerima uang pensiun dalam tahun berjalan), bagian penghasilan sebagai PNS Januari-Mei (hlm. 67 68) | TER_2024 | TER_bulanan, masa_terakhir_bulan_keluar, keluar_tengah_tahun, kategori_B, PNS, lebih_potong, DTP_pemerintah_APBN | ya | 14/14 cocok | cocok | tidak | cocok |
| [PMK72-B-6](PMK72_B_6.json) | PMK 72/2025 - Lampiran huruf B nomor 6, Tuan F (hlm. 42 43 44 45) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, DTP_parsial_okt_des, THR | ya | 35/35 cocok | cocok | tidak | cocok |
| [PMK72-B-7](PMK72_B_7.json) | PMK 72/2025 - Lampiran huruf B nomor 7, Tuan G (hlm. 45 46 47) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, DTP_parsial_okt_des, bonus, lebih_potong, lebih_bayar_vs_DTP | ya | 33/33 cocok | cocok | tidak | cocok setelah perbaikan |
| [PMK72-B-8](PMK72_B_8.json) | PMK 72/2025 - Lampiran huruf B nomor 8, Tuan H (nilai BP21 tambahan dari Lampiran huruf C angka III, hlm. 55-57) (hlm. 47 48 49 55 56 57) | TER_2024 | TER_bulanan, masa_terakhir_desember, DTP, DTP_parsial_okt_des, bonus, kategori_C, lebih_potong, lebih_bayar_vs_DTP | ya | 33/33 cocok | cocok | tidak | cocok setelah perbaikan |
| [PP58-Penj-Ps2-1](PP58_Penj_Ps2_1.json) | PP 58/2023 - Penjelasan Pasal 2 ayat (1), Contoh Tuan R (hlm. 8 9) | TER_2024 | TER_bulanan, masa_terakhir_desember, iuran_pensiun | ya | 15/15 cocok | cocok | tidak | cocok |

## Manifest - di luar lingkup, ditranskripsi lengkap

| id | sumber (hlm. PDF) | rezim | skenario | dalam_lingkup | cek aritmetika | cek tabel | dugaan erratum | verifikasi pass 2 |
|---|---|---|---|---|---|---|---|---|
| [PER16-I.11](PER16_I.11.json) | PER-16/PJ/2016 - Lampiran, Bagian Kedua, I.11 (pegawai tetap baru memiliki NPWP pada tahun berjalan), Adi Putra Tarigan (hlm. 48 49 50) | PER16_2023 | metode_PER16_bulanan, tanpa_NPWP_120persen, masa_terakhir_desember | tidak | 13/15 cocok | cocok | ya | cocok |
| [PMK168-B-I.2.2.2b](PMK168_B_I.2.2.2b.json) | PMK 168/2023 - Lampiran huruf B, Bagian Kedua, I.2.2.2, varian 'Tuan D menyerahkan bukti pemotongan dari PT W kepada PT AB' (tabel masa Sept-Nov di hlm. 40) (hlm. 40 41 42) | TER_2024 | TER_bulanan, masa_terakhir_desember, masuk_tengah_tahun, multi_pemberi_kerja | tidak | 4/4 cocok | cocok | tidak | cocok setelah perbaikan |
| [PMK168-C-I.1.3b](PMK168_C_I.1.3b.json) | PMK 168/2023 - Lampiran huruf C, Bagian Kedua, I.3, bagian '2. Penghasilan yang diterima dan/atau diperoleh dari KIP B' (penggabungan dua pemberi kerja) (hlm. 65 66) | TER_2024 | TER_bulanan, masa_terakhir_desember, multi_pemberi_kerja, PNS, pembulatan_PKP | tidak | 16/16 cocok | cocok | tidak | cocok setelah perbaikan |
| [PMK168-C-I.1.4b](PMK168_C_I.1.4b.json) | PMK 168/2023 - Lampiran huruf C, Bagian Kedua, I.4, bagian uang pensiun Juni-Desember (pembayar uang pensiun berkala memperhitungkan neto PNS Jan-Mei) (hlm. 67 68 69) | TER_2024 | pensiunan, multi_pemberi_kerja, masa_terakhir_desember | tidak | 4/5 cocok | cocok | ya | cocok setelah perbaikan |

## Manifest - di luar lingkup, ringkas (`di_luar_lingkup.json`)

| id | sumber (hlm. PDF) | subjek | cek aritmetika | dugaan ralat |
|---|---|---|---|---|
| PMK168-B-II | PMK 168/2023 - Lampiran B, Bagian Kedua, II (uang pensiun berkala), Tuan J (hlm. 46 47) | pensiunan | 6/6 cocok | tidak |
| PMK168-B-III | PMK 168/2023 - Lampiran B, Bagian Kedua, III (dewan komisaris tidak teratur), Tuan P (hlm. 47 48) | anggota dewan komisaris | 2/2 cocok | tidak |
| PMK168-B-IV.1.1 | PMK 168/2023 - Lampiran B, Bagian Kedua, IV.1.1 (PTT upah harian <= 2,5 juta), Tuan K (hlm. 48 49) | pegawai tidak tetap | 1/1 cocok | tidak |
| PMK168-B-IV.1.2 | PMK 168/2023 - Lampiran B, Bagian Kedua, IV.1.2 (PTT upah borongan <= 2,5 juta/hari), Tuan L (hlm. 49) | pegawai tidak tetap | 1/1 cocok | tidak |
| PMK168-B-IV.1.3 | PMK 168/2023 - Lampiran B, Bagian Kedua, IV.1.3 (PTT upah satuan > 2,5 juta/hari), Tuan M (hlm. 49 50) | pegawai tidak tetap | 1/1 cocok | tidak |
| PMK168-B-IV.1.4 | PMK 168/2023 - Lampiran B, Bagian Kedua, IV.1.4 (PTT upah borongan > 2,5 juta/hari), Tuan Z (hlm. 50) | pegawai tidak tetap | 3/3 cocok | tidak |
| PMK168-B-IV.2 | PMK 168/2023 - Lampiran B, Bagian Kedua, IV.2 (PTT dibayar bulanan), Tuan N (hlm. 50 51 52) | pegawai tidak tetap | 14/14 cocok | tidak |
| PMK168-B-V.1 | PMK 168/2023 - Lampiran B, Bagian Kedua, V.1 (bukan pegawai, pekerjaan bebas), Tuan U (hlm. 52) | bukan pegawai | 1/1 cocok | tidak |
| PMK168-B-V.2 | PMK 168/2023 - Lampiran B, Bagian Kedua, V.2 (jasa dokter di rumah sakit), Tuan R (hlm. 52 53) | bukan pegawai | 2/2 cocok | tidak |
| PMK168-B-V.3 | PMK 168/2023 - Lampiran B, Bagian Kedua, V.3 (imbalan jasa), Tuan T (hlm. 53 54) | bukan pegawai | 1/1 cocok | tidak |
| PMK168-B-V.4 | PMK 168/2023 - Lampiran B, Bagian Kedua, V.4 (bukan pegawai mempekerjakan orang/menyerahkan material), Tuan V (hlm. 54 55) | bukan pegawai | 2/2 cocok | tidak |
| PMK168-B-VI.1 | PMK 168/2023 - Lampiran B, Bagian Kedua, VI.1 (peserta kegiatan), Tuan W (hlm. 55) | peserta kegiatan | 1/1 cocok | tidak |
| PMK168-B-VI.2 | PMK 168/2023 - Lampiran B, Bagian Kedua, VI.2 (penarikan manfaat pensiun oleh pegawai), Tuan Q (hlm. 56) | peserta program pensiun (masih pegawai) | 2/2 cocok | tidak |
| PMK168-B-VI.3 | PMK 168/2023 - Lampiran B, Bagian Kedua, VI.3 (mantan pegawai), Tuan O (hlm. 56 57) | mantan pegawai | 1/1 cocok | tidak |
| PMK168-B-VII.1 | PMK 168/2023 - Lampiran B, Bagian Kedua, VII.1 (PPh 26, gaji rupiah), Tuan X (hlm. 57) | WPLN (PPh 26) | 1/1 cocok | tidak |
| PMK168-B-VII.2 | PMK 168/2023 - Lampiran B, Bagian Kedua, VII.2 (PPh 26, valas), Tuan Y (hlm. 57) | WPLN (PPh 26) | 1/1 cocok | tidak |
| PMK168-C-I.1.2 | PMK 168/2023 - Lampiran C, Bagian Kedua, I.2 (pensiunan PNS), Tuan B (hlm. 62 63) | pensiunan PNS | 2/2 cocok | tidak |
| PMK10-B-5 | PMK 10/2025 - Lampiran B, Tuan E (pegawai tidak tetap, DTP) (hlm. 22 23) | pegawai tidak tetap (DTP) | 1/1 cocok | tidak |
| PMK72-B-5 | PMK 72/2025 - Lampiran B, Tuan E (pegawai tidak tetap, DTP) (hlm. 42) | pegawai tidak tetap (DTP) | 1/1 cocok | tidak |
| PMK105-B-4 | PMK 105/2025 - Lampiran B, Tuan E (pegawai tidak tetap, DTP) (hlm. 43) | pegawai tidak tetap (DTP) | 1/1 cocok | tidak |
| PER16-II.1.2 | PER-16/PJ/2016 - Bagian Kedua, II.1.2 (Dana Pensiun, tahun pertama pensiun), Hari Irawan (hlm. 54 55) | pensiunan | 3/3 cocok | ya |
| PER16-II.2 | PER-16/PJ/2016 - Bagian Kedua, II.2 (uang pensiun tahun kedua), Hari Irawan (hlm. 55 56) | pensiunan | 2/2 cocok | tidak |
| PER16-III.1.1 | PER-16/PJ/2016 - Bagian Kedua, III.1.1 (upah harian), Nurcahyo (hlm. 56 57) | pegawai tidak tetap / harian | 2/2 cocok | tidak |
| PER16-III.1.2 | PER-16/PJ/2016 - Bagian Kedua, III.1.2 (upah harian), Nanang Hermawan (hlm. 57) | pegawai tidak tetap / harian | 1/1 cocok | tidak |
| PER16-III.2 | PER-16/PJ/2016 - Bagian Kedua, III.2 (upah satuan), Rizal Fahmi (hlm. 58) | pegawai tidak tetap | 1/1 cocok | tidak |
| PER16-III.3 | PER-16/PJ/2016 - Bagian Kedua, III.3 (upah borongan), Mawan (hlm. 58) | pegawai tidak tetap | 1/1 cocok | tidak |
| PER16-III.4 | PER-16/PJ/2016 - Bagian Kedua, III.4 (harian dibayar bulanan), Bagus Hermanto (hlm. 58 59) | pegawai tidak tetap | 2/2 cocok | tidak |
| PER16-III.5 | PER-16/PJ/2016 - Bagian Kedua, III.5 (bonus tenaga harian lepas), Bagus Hermanto (hlm. 59) | pegawai tidak tetap | 3/3 cocok | tidak |
| PER16-IV.1 | PER-16/PJ/2016 - Bagian Kedua, IV.1 (mantan pegawai), Victoria Endah (hlm. 60) | mantan pegawai | 1/1 cocok | tidak |
| PER16-IV.2 | PER-16/PJ/2016 - Bagian Kedua, IV.2 (komisaris bukan pegawai tetap), Aulia Rais (hlm. 60) | komisaris | 1/1 cocok | tidak |
| PER16-IV.3 | PER-16/PJ/2016 - Bagian Kedua, IV.3 (penarikan dana pensiun oleh pegawai), Nicholas Sinulingga (hlm. 60 61) | peserta program pensiun (masih pegawai) | 1/1 cocok | tidak |
| PER16-V.1.a | PER-16/PJ/2016 - Bagian Kedua, V.1.a (dokter praktik di RS), dr. Samudera Putra (hlm. 61 62) | bukan pegawai berkesinambungan | 2/2 cocok | tidak |
| PER16-V.1.b | PER-16/PJ/2016 - Bagian Kedua, V.1.b (agen asuransi bukan pegawai), Ety Rahmawati (hlm. 62 63 64) | bukan pegawai berkesinambungan | 1/4 cocok | ya |
| PER16-V.2.a | PER-16/PJ/2016 - Bagian Kedua, V.2.a (bukan pegawai tidak berkesinambungan), Nashrun Berlianto (hlm. 65) | bukan pegawai | 1/1 cocok | tidak |
| PER16-V.2.b | PER-16/PJ/2016 - Bagian Kedua, V.2.b (pengacara), Toga Marolop Simanjuntak (hlm. 65) | bukan pegawai | 1/1 cocok | tidak |
| PER16-V.3 | PER-16/PJ/2016 - Bagian Kedua, V.3 (bukan pegawai mempekerjakan orang/material), Dedy Efriliansyah (hlm. 65 66) | bukan pegawai | 2/2 cocok | tidak |
| PER16-VI | PER-16/PJ/2016 - Bagian Kedua, VI (peserta kegiatan), Sony Gemilang (hlm. 66) | peserta kegiatan | 1/1 cocok | tidak |
| PER16-VII | PER-16/PJ/2016 - Bagian Kedua, VII (PPh 26 pegawai WPLN, valas), Done Preksi (hlm. 67) | WPLN (PPh 26) | 2/2 cocok | tidak |

## Cakupan per jenis skenario (hanya kasus dalam lingkup)

| Jenis skenario | Rezim TER 2024+ | Rezim PER-16 (contoh 2016) | Kasus TER | Kasus PER-16 |
|---|---|---|---|---|
| TER bulanan (masa selain terakhir) | 23 | 0 | PMK105-B-1, PMK105-B-2, PMK105-B-3, PMK10-B-1, PMK10-B-2, PMK10-B-3, PMK168-B-I.1, PMK168-B-I.2.1.1, PMK168-B-I.2.1.2, PMK168-B-I.2.2.1, PMK168-B-I.2.2.2a, PMK168-B-I.2.2.3, PMK168-B-I.3, PMK168-B-I.4, PMK168-B-I.5, PMK168-B-I.6, PMK168-C-I.1.1, PMK168-C-I.1.3a, PMK168-C-I.1.4a, PMK72-B-6, PMK72-B-7, PMK72-B-8, PP58-Penj-Ps2-1 | - |
| Masa pajak terakhir - Desember (TER + Pasal 17) | 16 | 0 | PMK105-B-1, PMK105-B-2, PMK105-B-3, PMK10-B-1, PMK10-B-2, PMK10-B-3, PMK168-B-I.1, PMK168-B-I.2.1.1, PMK168-B-I.2.1.2, PMK168-B-I.2.2.2a, PMK168-C-I.1.1, PMK168-C-I.1.3a, PMK72-B-6, PMK72-B-7, PMK72-B-8, PP58-Penj-Ps2-1 | - |
| Masa pajak terakhir - bulan keluar (TER + Pasal 17) | 3 | 0 | PMK168-B-I.2.2.1, PMK168-B-I.2.2.3, PMK168-C-I.1.4a | - |
| THR | 2 | 0 | PMK168-B-I.1, PMK72-B-6 | - |
| Bonus / penghasilan tidak teratur lain (gaji-13, rapel) | 9 | 4 | PMK105-B-2, PMK105-B-3, PMK10-B-2, PMK10-B-3, PMK168-B-I.1, PMK168-C-I.1.1, PMK168-C-I.1.3a, PMK72-B-7, PMK72-B-8 | PER16-I.3, PER16-I.4.1, PER16-I.4.2, PER16-I.6.2.2 |
| Lembur | 1 | 2 | PMK168-B-I.1 | PER16-I.1.3, PER16-I.1.4 |
| Gross-up (full gross up) | 1 | 0 | PMK168-B-I.4 | - |
| Tunjangan pajak (jumlah tetap) | 1 | 1 | PMK168-B-I.5 | PER16-I.9 |
| PPh ditanggung pemberi kerja (non gross-up, PER-16) | 0 | 1 | - | PER16-I.8 |
| Masuk tengah tahun | 5 | 2 | PMK105-B-3, PMK10-B-3, PMK168-B-I.2.1.1, PMK168-B-I.2.1.2, PMK168-B-I.2.2.2a | PER16-I.6.1.1, PER16-I.6.1.2 |
| Keluar tengah tahun | 3 | 3 | PMK168-B-I.2.2.1, PMK168-B-I.2.2.3, PMK168-C-I.1.4a | PER16-I.6.2.1, PER16-I.6.2.2, PER16-II.1.1 |
| Kewajiban subjektif parsial (disetahunkan + proporsional) | 2 | 2 | PMK168-B-I.2.1.2, PMK168-B-I.2.2.3 | PER16-I.6.1.2, PER16-I.6.2.2 |
| Pegawai wanita (jenis_kelamin P) | 0 | 3 | - | PER16-I.1.3, PER16-I.1.4, PER16-I.4.2 |
| Pegawai wanita kawin (penentuan PTKP) | 0 | 2 | - | PER16-I.1.3, PER16-I.1.4 |
| Natura / kenikmatan | 1 | 1 | PMK168-B-I.6 | PER16-I.10 |
| Zakat / sumbangan keagamaan wajib | 2 | 0 | PMK168-B-I.1, PMK168-B-I.2.1.2 | - |
| Iuran pensiun pegawai | 5 | 17 | PMK168-B-I.1, PMK168-B-I.2.1.1, PMK168-B-I.2.2.1, PMK168-B-I.2.2.2a, PP58-Penj-Ps2-1 | PER16-I.1.1, PER16-I.1.2, PER16-I.1.3, PER16-I.1.4, PER16-I.1.5, PER16-I.12.1, PER16-I.2.2, PER16-I.2.3, PER16-I.3, PER16-I.4.1, PER16-I.4.2, PER16-I.5, PER16-I.6.1.1, PER16-I.6.2.1, PER16-I.8, PER16-I.9, PER16-II.1.1 |
| Iuran JHT pegawai | 0 | 5 | - | PER16-I.1.2, PER16-I.1.4, PER16-I.2.2, PER16-I.2.3, PER16-I.4.2 |
| Premi JKK/JKM dibayar pemberi kerja | 1 | 5 | PMK168-B-I.1 | PER16-I.1.2, PER16-I.1.4, PER16-I.2.2, PER16-I.2.3, PER16-I.4.2 |
| Premi BPJS Kesehatan dibayar pemberi kerja | 0 | 0 | - | - |
| Iuran JP (Jaminan Pensiun) pegawai | 0 | 0 | - | - |
| PPh 21 DTP (insentif) | 10 | 0 | PMK105-B-1, PMK105-B-2, PMK105-B-3, PMK10-B-1, PMK10-B-2, PMK10-B-3, PMK10-B-4, PMK72-B-6, PMK72-B-7, PMK72-B-8 | - |
| Mata uang asing | 1 | 1 | PMK168-B-I.3 | PER16-I.7 |
| TER kategori B | 7 | 0 | PMK105-B-2, PMK10-B-2, PMK168-B-I.5, PMK168-B-I.6, PMK168-C-I.1.1, PMK168-C-I.1.3a, PMK168-C-I.1.4a | - |
| TER kategori C | 2 | 0 | PMK168-B-I.3, PMK72-B-8 | - |
| PNS (Lampiran C PMK 168) | 3 | 0 | PMK168-C-I.1.1, PMK168-C-I.1.3a, PMK168-C-I.1.4a | - |
| Gaji mingguan/harian pegawai tetap | 0 | 3 | - | PER16-I.2.1, PER16-I.2.2, PER16-I.2.3 |
| Pindah tugas antar cabang | 0 | 1 | - | PER16-I.5 |

Catatan cakupan: kasus PNS (PMK168-C-*) dihitung dalam lingkup dengan tanda `PNS` karena mekanismenya identik (TER + Pasal 17 pada masa terakhir); keluarkan bila KB hanya untuk pemberi kerja swasta. Kasus DTP (PMK 10/72/105) juga memuat perhitungan PPh 21 normal (TER + Desember) sehingga sekaligus menjadi contoh TER tahun 2025/2026.

## Celah: skenario tanpa contoh resmi

Tidak ditemukan contoh resmi (di sumber yang diperiksa) untuk:
1. **Tahun pajak 2023 dengan tarif UU HPP.** PER-16 hanya memuat contoh 2016 (tarif UU 36/2008). Rezim 2023 hanya teruji resmi untuk kasus dengan PKP <= Rp50 juta.
2. **Premi BPJS Kesehatan** yang dibayar pemberi kerja sebagai komponen bruto (PER16-I.1.4 menyebut kepesertaan BPJS Kesehatan tetapi tidak menghitung preminya).
3. **Iuran JP (Jaminan Pensiun)** dan batas upah JP; **iuran JHT pegawai** hanya ada di contoh PER-16 2016 (PMK 168 memakai "iuran pensiun" generik).
4. **Pegawai wanita di rezim TER** - seluruh contoh PMK 168/PP 58/PMK DTP memakai "Tuan"; kasus karyawati (kawin, suami berpenghasilan / tidak) hanya ada di PER-16.
5. **Gross-up setahun penuh dengan penghitungan ulang Desember**, maupun campuran gross/gross-up per komponen - satu-satunya contoh gross-up (PMK168-B-I.4) hanya satu masa.
6. **Natura menurut PMK 66/2023** (penilaian, batas pengecualian) - PMK168-B-I.6 hanya beasiswa (kenikmatan) satu masa; PER16-I.10 memakai aturan natura 2016 (hanya objek bila pemberi kerja final/deemed profit).
7. **Status PTKP TK/1, TK/2, TK/3**: tidak ada contoh; K/2 hanya satu masa (PMK168-B-I.5); kategori C setahun penuh hanya PMK72-B-8 (DTP).
8. **Keluar tengah tahun disertai THR/bonus di rezim TER** (PMK168-B-I.2.2.1 dan I.2.2.3 hanya gaji); **keluar tengah tahun + DTP** tidak ada.
9. **Zakat di rezim PER-16** (zakat hanya di PMK168-B-I.1 dan sumbangan keagamaan di PMK168-B-I.2.1.2).
10. **Tahun pajak 2025/2026 tanpa DTP** - contoh 2025/2026 hanya berupa contoh DTP (perhitungan PPh-nya tetap ada).
11. **Pembulatan rupiah PPh per masa** - semua hasil TER contoh berupa bilangan bulat kecuali gross-up (PMK168-B-I.4: 13.777.062,39 -> 13.777.062, aturan pembulatan tidak dinyatakan).

Sumber lain yang ada di `01_regulasi` dan mungkin memuat contoh tetapi **tidak** diperiksa dalam tugas ini: PMK 66/2023 (natura), PER-2/PJ/2024 Lampiran (pengisian bukti potong), PMK 81/2024, PMK 6/2026 (DTP pemagangan), PP 20/2026.

## Dugaan erratum dalam contoh resmi (temuan penelitian)

Semua butir di bawah diverifikasi pada **citra halaman** (bukan artefak OCR). Nilai `expected` TIDAK diubah; KB yang benar seharusnya *tidak* mereproduksi angka-angka ini, dan selisihnya dicatat sebagai "ralat contoh resmi" (research_plan §9.1).

| Kasus | Dugaan erratum | Dampak pada angka akhir |
|---|---|---|
| PMK168-B-I.6 (hlm. 46) | Bruto Rp55.000.000 tetapi baris hitung `19% x Rp55.500.000 = Rp10.545.000` | PPh masa seharusnya 10.450.000 |
| PMK10-B-3 = PMK 72/2025 no. 3 (hlm. 21 / 41) | Biaya jabatan `9 x 450.000 + 1 x 500.000 = 4.550.000` (plafon per bulan) vs metode semua contoh PMK 168 & PMK 105/2025 (`5% x bruto, maks n x 500.000` = 4.750.000). Teks Pasal 10 ayat (2) PMK 168 ("Rp6 juta setahun atau Rp500 ribu sebulan") ambigu | PKP, PPh setahun dan lebih potong berbeda (1.822.500/277.500 vs 1.812.500/287.500) |
| PMK105-B-3 (hlm. 42) | Baris Total tabel: PPh & DTP 1.822.500, jumlah baris = 1.812.500 | Hanya total tabel |
| PMK168-C-I.1.4b (hlm. 67-68, di luar lingkup) | Narasi uang pensiun 2.500.000/bulan, tabel 3.000.000/bulan | - |
| PER16-I.1.2 (hlm. -9-) | Baris iuran pensiun tercetak 200.000; jumlah memakai 100.000 (iuran pegawai) | Tidak ada (jumlah benar) |
| PER16-I.1.3 (hlm. -10-) | Biaya jabatan 525.000 tanpa plafon Rp500.000/bulan | PPh Juli seharusnya 344.583 (bukan 340.833) |
| PER16-I.2.1 (hlm. -13-) | `1.860.000 : 4 = 38.750` (langkah :12 hilang) | Tidak ada (hasil benar) |
| PER16-I.2.3 (hlm. -14-) | Bruto 6.415.500 = gaji **dikurangi** premi (seharusnya 6.584.500); jumlah pengurang 487.775 (seharusnya 485.775) | Seluruh rantai setelah bruto |
| PER16-I.5 (hlm. -20-) | `5% X Rp5.000.000 = 750.000` (seharusnya 15.000.000) | Tidak ada |
| PER16-I.6.2.2 (hlm. -26-) | 7.291.666 - 6.433.332 ditulis 858.333 (seharusnya 858.334) | Rp1 |
| PER16-I.8 (hlm. -27-) | Jumlah pengurang 425.000 (seharusnya 475.000) | Tidak ada (neto benar) |
| PER16-I.11 (hlm. -31-, di luar lingkup) | 88.500 x 11 = 973.750 (seharusnya 973.500); Desember (88.500) vs (88.750) | Rp250 |
| PER16-V.1.b (hlm. -45-, di luar lingkup, ringkas) | Tabel tanpa NPWP: DPP Agustus 32 jt (seharusnya 31 jt); total PPh 59.430.000 ≠ jumlah baris 64.650.000; Nov/Des tampak tanpa faktor 120% | - |

Inkonsistensi minor (label/pembulatan, angka benar): label "PPh Pasal 21 bulan Januari" untuk contoh Juli/Agustus (PER16-I.1.2, I.1.3, I.1.4, I.1.5, I.2.1), "bulan Juli" untuk September (PER16-I.9), "Biaya jabatan sebulan" untuk 4 bulan (PMK168-B-I.2.2.2b), nama dana pensiun berganti (PER16-II.1.2). **Pembulatan PPh bulanan PER-16 tidak konsisten**: 126.287,5 -> 126.288 (I.1.2, normal) tetapi 103.087,5 -> 103.087 (I.1.4, ke bawah); 7.291.666,67 -> 7.291.666 (I.6.2.2, ke bawah). Kasus lain berpecahan < 0,5 sehingga kedua aturan memberi hasil sama.

## Verifikasi

1. **Pass 1 (transkripsi).** Teks diekstrak dengan pdfplumber; setiap halaman contoh dalam lingkup dirender (pypdfium2) dan dibaca dari citra, terutama untuk PDF hasil pindai (PER-16, PP 58, dan lapisan OCR PMK 168). Artefak OCR yang diselesaikan dicatat di `catatan_transkripsi`.
2. **Cek aritmetika & tabel.** Setiap baris dihitung ulang (`cek_aritmetika`); tarif TER dicocokkan dengan `tables/ter_bulanan.csv` (batas bawah eksklusif, batas atas inklusif), kategori TER & PTKP dengan `tables/ptkp.csv`, Pasal 17 dengan `tables/tarif_pasal17.csv` (UU HPP untuk 2024+, UU 36/2008 untuk contoh PER-16 2016). Semua pencarian tabel cocok; semua ketidakcocokan aritmetika adalah dugaan erratum di atas atau cek pembanding yang sengaja ditulis (mis. "bruto menurut narasi").
3. **Pass 2 (independen).** Tiga agen terpisah membaca ulang citra halaman lebih dahulu, lalu membandingkannya dengan JSON (tanpa mengubah berkas). Hasil per kasus ada di kunci `verifikasi_pass2` dan kolom manifest.

Hasil pass 2: **50/50 berkas JSON cocok dengan citra halaman pada setiap angka `expected` dan `input`** (PMK 168 + PP 58: 17 berkas; PER-16: 23 berkas; PMK 10/72/105: 10 berkas). Tidak ada angka yang harus diubah. Perbaikan yang dilakukan setelah pass 2 hanya metadata/teks: salah ketik pemisah desimal pada `langkah_resmi` (PMK10-B-3, PMK105-B-3), redaksi kutipan (PMK105-B-2), rujukan halaman (PMK168-B-I.2.2.2b, PMK72-B-8), penambahan `kredit_pajak_spt` & `metode` (PMK168-C-I.1.4b), dan penandaan simpulan/penafsiran transkriptor (PMK168-B-I.5, PER16-I.6.2.2, `jenis_kelamin`). Duplikasi PMK 72/2025 no. 1-4 = PMK 10/2025 no. 1-4 juga dikonfirmasi visual.

Nilai yang merupakan **simpulan transkriptor**, bukan angka dokumen: `jenis_kelamin: "L"` (dari sapaan "Tuan"), `metode: "gross"` (dokumen tidak menyebut), `akhir_kewajiban_subjektif`/`awal_kewajiban_subjektif` (dari narasi tanggal), dan pemecahan komponen yang hanya tersirat (mis. `tunjangan_pajak_gross_up` di PMK168-B-I.4).


## Ketidakpastian OCR yang tersisa

Tidak ada ketidakpastian OCR yang tersisa pada kasus dalam lingkup: setiap angka dibaca dari citra halaman (dan diulang oleh pass 2). Artefak OCR yang ditemukan dan diselesaikan via citra antara lain: PMK 168 "1.0.000.000" (hlm. 34), baris PTKP rusak (hlm. 39), "Rpl 1.115.000" (hlm. 66, seharusnya 17.115.000); PP 58 angka PTKP hilang (hlm. 9, 58.500.000); PER-16 "4.8235.000" (3.825.000), "1.0560.000" (1.050.000), dan beberapa PKP/neto/bruto yang tidak terbaca (I.2.2, I.6.1.2, I.10, I.12.1, II.1.1). Dugaan erratum di atas sudah dipastikan tercetak di dokumen, bukan hasil OCR.

Batasan: entri ringkas di `di_luar_lingkup.json` tidak melalui pass 2. Angka PER-16 hlm. 61 dan 66 (di luar lingkup) hanya dibaca dari teks OCR plus cek aritmetika, tidak dilihat sebagai citra; halaman lain entri ringkas dilihat sebagai citra pada pass 1.


## Reproduksi

Berkas dibangkitkan oleh skrip di luar repositori (scratchpad sesi) dari nilai yang diketik tangan per contoh; cek dihitung dengan `Decimal`. Untuk memeriksa ulang, buka PDF pada `sumber.halaman_pdf` dan bandingkan dengan `expected` dan `langkah_resmi`.
