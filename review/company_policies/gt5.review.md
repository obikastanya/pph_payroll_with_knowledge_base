# Tinjauan: contoh hitung kebijakan perusahaan (GT5)

Berkas yang diperiksa: [dataset/11_acuan/gt5_contoh_kebijakan/](../../dataset/11_acuan/gt5_contoh_kebijakan/) (asumsi umum dan putusan tafsir di README berkas itu)
Status: **selesai**

Setiap contoh menghitung nilai yang ditentukan PKB (THR, lembur, bonus, potongan, dan sejenisnya) dan, bila relevan, PPh 21 bulan itu. Nominal upah dipilih untuk ilustrasi karena PKB tidak memuat nominal (kecuali skala upah AVCO).

Untuk setiap contoh: (1) hitung ulang nilai harapan dengan cara Anda atau periksa langkahnya, (2) tulis `ok` atau koreksi di kolom **Setuju? / koreksi**, (3) jawab pertanyaan ambiguitas.

Konvensi saat diajukan: PPh hasil TER dibulatkan ke bawah ke rupiah; PPh yang ditanggung perusahaan tidak di-*gross-up* (metode net); premi JKK, JKM, JKN pemberi kerja masuk bruto; iuran JHT dan JP pegawai hanya menjadi pengurang di Masa Pajak Terakhir.

**Hasil tinjauan.** Semua 21 contoh dihitung ulang dengan program terpisah (TER dari tabel, iterasi titik tetap untuk *gross-up*, tarif Pasal 17). Dua konvensi diubah: PPh yang ditanggung perusahaan di-*gross-up* (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44) dan PPh TER Masa 2025 dst. dibulatkan ke rupiah terdekat (tafsir K1). Tabel langkah di bawah adalah versi setelah koreksi; kolom nilai harapan memuat angka yang diajukan dan koreksinya. Putusan tafsir lengkap: README GT5, bagian **Putusan tafsir**.

## PKB_WIKA_2025_2026

PT Wijaya Karya (konstruksi, BUMN), 2025-03-01 s.d. 2026-12-31

### GT5-WIKA-01: THR prorata pegawai baru dan PPh 21 ditanggung perusahaan (Maret 2025)

**Menguji:** Rumus prorata THR (masa kerja/12 x THP), THR sebagai penghasilan tidak teratur dalam TER, PPh ditanggung perusahaan sebagai kenikmatan (gross-up)  
**Klausul:** WIKA-31-3, WIKA-31-4, WIKA-4-35, WIKA-22-2, WIKA-32-4 · **Tahun pajak:** 2025

**Masukan:** tanggal_masuk = 2024-10-01; hari_raya = 2025-03-31 (Idul Fitri); masa_pajak = 2025-03; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- Pegawai Organik, status PTKP TK/0 (kategori TER A) kecuali disebut lain
- Fixed Pay (FP) Rp12.000.000, Tunjangan Grade (TG) Rp6.000.000, THP Rp18.000.000 (nominal tidak ada di PKB; dipilih untuk ilustrasi)
- Tingkat risiko JKK konstruksi diasumsikan 'tinggi' 1,27% (tingkat risiko ditetapkan per perusahaan; PKB tidak menyebut)
- Dasar iuran BPJS TK dan JKN = Fixed Pay (Ps 32 ayat 4; TG dikecualikan menurut Ps 4 angka 36). Pengecualian ini dipakai sebagai acuan; konflik laten C8 dicatat di WIKA-4-36
- PPh 21 yang ditanggung Perusahaan (Ps 22 ayat 2) adalah kenikmatan objek PPh 21 dan masuk bruto dengan full gross-up (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K3-K4)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Pembagian iuran JHT 2% dan JP 1% oleh pegawai mengikuti regulasi (PKB tidak menyebut)
- Masa kerja dihitung dalam bulan penuh sampai hari raya: 1 Okt 2024 - 31 Mar 2025 = 6 bulan
- THR dibayar sebesar batas bawah (1,0 x THP) pada payroll Maret

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THP bulanan = FP + TG | 18.000.000 | WIKA-4-35, WIKA-19-3 |
| 2 | Premi JKK pemberi kerja 1.27% x 12000000 | 152.400 | PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 3 | Premi JKM pemberi kerja 0,30% x 12000000 | 36.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 4 | Premi JKN pemberi kerja 4% x min(12000000, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 5 | Bruto teratur sebulan tanpa PPh ditanggung = THP + premi JKK + JKM + JKN | 18.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 6 | Masa kerja (bulan penuh sampai hari raya) | 6 | WIKA-31-4; Permenaker 6/2016 Ps 3 ayat (1) huruf b (PDF hlm. 4) |
| 7 | THR = masa kerja / 12 x THP | 9.000.000 | WIKA-31-4 |
| 8 | Bruto Maret sebelum PPh ditanggung (X) = bruto teratur + THR | 27.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 9 | PPh 21 Maret ditanggung Perusahaan: titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 27668400; bruto X + T = 31802759 masuk lapisan TER kategori A di atas 30050000 s.d. 32400000 = 13% | 4.134.359 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 10 | Bruto Maret = X + PPh ditanggung | 31.802.759 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10); PPh ditanggung pemberi kerja = kenikmatan objek PPh 21, full gro… |
| 11 | Iuran JHT pegawai 2% x 12000000 | 240.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 12 | Iuran JP pegawai 1% x min(12000000, batas upah 10547400 untuk iuran 2025-03) | 105.474 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 13 | Iuran JKN pegawai 1% x min(12000000, 12.000.000) | 120.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 14 | Uang diterima = THP + THR - iuran JHT - JP - JKN (PPh ditanggung, tidak dipotong) | 26.534.526 | WIKA-22-2 |

</details>

**Di mana PPh 21 masuk:** Ya: THR dan PPh yang ditanggung (kenikmatan) masuk bruto Maret; TER kategori A atas bruto setelah gross-up

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| THR (Rp) | 9.000.000 | ya |
| bruto Masa Pajak Maret | 27.668.400 | dikoreksi: 31.802.759 |
| PPh 21 Maret, beban perusahaan | 3.043.524 | dikoreksi: 4.134.359 |
| uang diterima pegawai Maret | 26.534.526 | ya |

**Pertanyaan:**

1. Cara menghitung masa kerja: bulan penuh vs pecahan bulan (PKB tidak menjelaskan) - bagaimana praktik Anda?

   Jawaban: Masa kerja dihitung dalam bulan penuh yang telah dilalui sampai hari raya (Permenaker 6/2016 Ps 3 ayat (1) huruf b, PDF hlm. 4: masa kerja/12 x 1 (satu) bulan upah, tanpa aturan pecahan bulan); pecahan bulan tidak dihitung.

2. Apakah PPh yang ditanggung perusahaan harus ditambahkan ke bruto (gross-up) atau tidak (net); contoh memakai net - bagaimana praktik Anda?

   Jawaban: PPh ditanggung perusahaan ditambahkan ke bruto (full gross-up): PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K4. Metode net hanya berlaku untuk Masa Januari-Juni 2023.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: PPh yang ditanggung adalah kenikmatan dan di-gross-up (putusan 1). PPh Maret 3.043.524 -> 4.134.359 (titik tetap pada lapisan 13%), bruto 27.668.400 -> 31.802.759; THR dan uang diterima tetap

### GT5-WIKA-02: Jasa Produksi: PPh dipotong dari pegawai, PPh gaji ditanggung perusahaan (Juni 2025)

**Menguji:** Pengecualian Ps 22 ayat 2: PPh atas Jasa Produksi ditanggung pegawai (metode selisih), PPh atas gaji ditanggung perusahaan (gross-up)  
**Klausul:** WIKA-22-2, WIKA-28 · **Tahun pajak:** 2025

**Masukan:** masa_pajak = 2025-06; jasa_produksi = 20000000; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- Pegawai Organik, status PTKP TK/0 (kategori TER A) kecuali disebut lain
- Fixed Pay (FP) Rp12.000.000, Tunjangan Grade (TG) Rp6.000.000, THP Rp18.000.000 (nominal tidak ada di PKB; dipilih untuk ilustrasi)
- Tingkat risiko JKK konstruksi diasumsikan 'tinggi' 1,27% (tingkat risiko ditetapkan per perusahaan; PKB tidak menyebut)
- Dasar iuran BPJS TK dan JKN = Fixed Pay (Ps 32 ayat 4; TG dikecualikan menurut Ps 4 angka 36). Pengecualian ini dipakai sebagai acuan; konflik laten C8 dicatat di WIKA-4-36
- PPh 21 yang ditanggung Perusahaan (Ps 22 ayat 2) adalah kenikmatan objek PPh 21 dan masuk bruto dengan full gross-up (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K3-K4)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Pembagian iuran JHT 2% dan JP 1% oleh pegawai mengikuti regulasi (PKB tidak menyebut)
- Besaran Jasa Produksi Rp20.000.000 (ditetapkan Direksi; dipilih untuk ilustrasi), dibayar Juni 2025
- Alokasi: metode selisih. Bagian Perusahaan = PPh gross-up atas gaji tanpa Jasa Produksi; bagian pegawai = PPh total bulan itu - bagian Perusahaan

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THP bulanan = FP + TG | 18.000.000 | WIKA-4-35, WIKA-19-3 |
| 2 | Premi JKK pemberi kerja 1.27% x 12000000 | 152.400 | PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 3 | Premi JKM pemberi kerja 0,30% x 12000000 | 36.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 4 | Premi JKN pemberi kerja 4% x min(12000000, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 5 | Bruto teratur sebulan tanpa PPh ditanggung (X) | 18.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 6 | PPh atas gaji tanpa Jasa Produksi, ditanggung Perusahaan: titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 18668400; bruto X + T = 20514725 masuk lapisan TER kategori A di atas 19750000 s.d. 24150000 = 9% | 1.846.325 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 7 | Bruto Juni = X + PPh ditanggung + Jasa Produksi | 40.514.725 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10); PPh ditanggung pemberi kerja = kenikmatan objek PPh 21, full gro… |
| 8 | PPh 21 Juni seluruhnya: TER kategori A untuk bruto 40514725 (di atas 39100000 s.d. 43850000) = 16% | 6.482.356 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -4- (PDF hlm. 14); k… |
| 9 | Bagian PPh dipotong dari Jasa Produksi (selisih) | 4.636.031 | WIKA-22-2; metode selisih: preseden PER-16/PJ/2016 Ps 14 ayat (3) huruf b (PDF hlm. 13, OCR) |
| 10 | Jasa Produksi diterima = 20.000.000 - PPh bagian pegawai | 15.363.969 | WIKA-22-2 |

</details>

**Di mana PPh 21 masuk:** Ya: Jasa Produksi menaikkan lapisan TER dari 9% (gaji setelah gross-up) ke 16% atas seluruh bruto; lompatan itu ditanggung pegawai lewat metode selisih

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| PPh 21 Juni total | 5.800.260 | dikoreksi: 6.482.356 |
| PPh dipotong dari Jasa Produksi (inkremental) | 4.306.788 | dikoreksi: 4.636.031 |
| PPh beban perusahaan | 1.493.472 | dikoreksi: 1.846.325 |
| Jasa Produksi bersih | 15.693.212 | dikoreksi: 15.363.969 |
| pembanding alokasi proporsional | 3.000.000 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |

**Pertanyaan:**

1. Metode alokasi PPh antara komponen ditanggung dan dipotong tidak diatur: inkremental (contoh ini) vs proporsional; selisihnya besar karena lompatan lapisan TER - bagaimana praktik Anda?

   Jawaban: Alokasi: metode selisih (komponen yang dikecualikan menanggung PPh(dengan) - PPh(tanpa)). Dasarnya: Ps 22 ayat 2 menjadikan PPh atas gaji tanggungan Perusahaan sebagaimana bila Jasa Produksi tidak dibayar; kaidah selisih untuk penghasilan tidak teratur dipakai PER-16/PJ/2016 Ps 14 ayat (3) huruf b. Alokasi proporsional ditolak karena membebankan sebagian PPh atas Jasa Produksi kepada Perusahaan.

2. Alokasi pada perhitungan ulang Masa Pajak Desember juga tidak diatur - bagaimana praktik Anda?

   Jawaban: Masa Pajak Desember: kaidah yang sama atas PPh setahun, yaitu Perusahaan menanggung PPh setahun tanpa Jasa Produksi/IHL (dengan gross-up), pegawai menanggung sisanya dikurangi bagian yang telah dipotong dari Jasa Produksi.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: gross-up bagian Perusahaan dan pembulatan 2025. Bagian Perusahaan 1.493.472 -> 1.846.325; PPh total 5.800.260 -> 6.482.356 (lapisan 16%); bagian pegawai 4.306.788 -> 4.636.031; Jasa Produksi bersih 15.693.212 -> 15.363.969; pembanding proporsional dikeluarkan dari nilai harapan

### GT5-WIKA-03: Uang cuti dan ekstra uang cuti masa kerja 20 tahun (Februari 2025)

**Menguji:** Tabel Lampiran 1 (ekstra uang cuti 125% FP), waktu bayar pada bulan tanggal masuk, batas upah JP sebelum Maret  
**Klausul:** WIKA-52-4, WIKA-L1, WIKA-44-1, WIKA-44-2 · **Tahun pajak:** 2025

**Masukan:** tanggal_pengangkatan = 2005-02-01; masa_pajak = 2025-02; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- Pegawai Organik, status PTKP TK/0 (kategori TER A) kecuali disebut lain
- Fixed Pay (FP) Rp12.000.000, Tunjangan Grade (TG) Rp6.000.000, THP Rp18.000.000 (nominal tidak ada di PKB; dipilih untuk ilustrasi)
- Tingkat risiko JKK konstruksi diasumsikan 'tinggi' 1,27% (tingkat risiko ditetapkan per perusahaan; PKB tidak menyebut)
- Dasar iuran BPJS TK dan JKN = Fixed Pay (Ps 32 ayat 4; TG dikecualikan menurut Ps 4 angka 36). Pengecualian ini dipakai sebagai acuan; konflik laten C8 dicatat di WIKA-4-36
- PPh 21 yang ditanggung Perusahaan (Ps 22 ayat 2) adalah kenikmatan objek PPh 21 dan masuk bruto dengan full gross-up (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K3-K4)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Pembagian iuran JHT 2% dan JP 1% oleh pegawai mengikuti regulasi (PKB tidak menyebut)
- Uang cuti dibayar sebesar batas bawah 1 x FP
- Satya Karya 20 tahun dibayar Maret 2025 (HUT perusahaan); hanya nilainya yang dihitung

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THP bulanan = FP + TG | 18.000.000 | WIKA-4-35, WIKA-19-3 |
| 2 | Premi JKK pemberi kerja 1.27% x 12000000 | 152.400 | PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 3 | Premi JKM pemberi kerja 0,30% x 12000000 | 36.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 4 | Premi JKN pemberi kerja 4% x min(12000000, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 5 | Bruto teratur sebulan tanpa PPh ditanggung | 18.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 6 | Uang cuti tahunan = 1 x FP | 12.000.000 | WIKA-52-4 |
| 7 | Ekstra uang cuti masa kerja 20 tahun = 125% x FP | 15.000.000 | WIKA-L1 (Lampiran 1, PDF hlm. 78) |
| 8 | Bruto Februari sebelum PPh ditanggung (X) | 45.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 9 | PPh 21 Februari ditanggung Perusahaan: titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 45668400; bruto X + T = 57085500 masuk lapisan TER kategori A di atas 56300000 s.d. 62200000 = 20% | 11.417.100 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -4- (PDF hlm. 14); k… |
| 10 | Bruto Februari = X + PPh ditanggung | 57.085.500 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10); PPh ditanggung pemberi kerja = kenikmatan objek PPh 21, full gro… |
| 11 | Iuran JHT pegawai 2% x 12000000 | 240.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 12 | Iuran JP pegawai 1% x min(12000000, batas upah 10042300 untuk iuran 2025-02) | 100.423 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 13 | Iuran JKN pegawai 1% x min(12000000, 12.000.000) | 120.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 14 | Uang diterima Februari | 44.539.577 | WIKA-22-2 |
| 15 | Satya Karya 20 tahun (masa kerja s.d. 11 Maret 2025 = 20 tahun) = 1,5 x FP | 18.000.000 | WIKA-44-1, WIKA-44-2 |

</details>

**Di mana PPh 21 masuk:** Ya: uang cuti dan ekstra uang cuti adalah penghasilan tidak teratur Masa Februari; PPh ditanggung ikut masuk bruto

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| ekstra uang cuti | 15.000.000 | ya |
| bruto Februari | 45.668.400 | dikoreksi: 57.085.500 |
| PPh 21 Februari (beban perusahaan) | 7.763.628 | dikoreksi: 11.417.100 |
| iuran JP pegawai (batas upah 2024 masih berlaku untuk iuran Februari) | 100.423 | ya |
| uang diterima | 44.539.577 | ya |
| Satya Karya (Maret) | 18.000.000 | ya |

**Pertanyaan:**

1. Lampiran 1 dibaca dari gambar tabel; ekstra uang cuti hanya pada kelipatan 5 tahun - bagaimana praktik Anda?

   Jawaban: Lampiran 1 dicocokkan ulang dengan render PDF hlm. 78: ekstra uang cuti hanya pada masa kerja 5, 10, ..., 35 tahun (50%-200% x FP).

2. 'minimal 1 kali Fixed Pay': nilai aktual bisa lebih besar - bagaimana praktik Anda?

   Jawaban: 'Minimal 1 kali Fixed Pay': acuan memakai batas bawah; nilai lebih besar hanya bila ditetapkan Perusahaan.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: gross-up. PPh Februari 7.763.628 -> 11.417.100 (lapisan 20%), bruto 45.668.400 -> 57.085.500; nilai PKB (ekstra uang cuti, Satya Karya, iuran JP, uang diterima) tetap

### GT5-WIKA-04: Pegawai mengundurkan diri 31 Oktober 2025: uang pisah dan PPh Masa Pajak Terakhir

**Menguji:** Tabel uang pisah (Ps 90) dan PPh finalnya, Masa Pajak Terakhir pegawai berhenti dengan PPh ditanggung (gross-up), lebih potong  
**Klausul:** WIKA-90-1, WIKA-31-3, WIKA-52-4, WIKA-22-2 · **Tahun pajak:** 2025

**Masukan:** tanggal_pengangkatan = 2018-07-01; tanggal_berhenti = 2025-10-31; alasan = mengundurkan diri sesuai Ps 84 ayat (3); status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- Pegawai Organik, status PTKP TK/0 (kategori TER A) kecuali disebut lain
- Fixed Pay (FP) Rp12.000.000, Tunjangan Grade (TG) Rp6.000.000, THP Rp18.000.000 (nominal tidak ada di PKB; dipilih untuk ilustrasi)
- Tingkat risiko JKK konstruksi diasumsikan 'tinggi' 1,27% (tingkat risiko ditetapkan per perusahaan; PKB tidak menyebut)
- Dasar iuran BPJS TK dan JKN = Fixed Pay (Ps 32 ayat 4; TG dikecualikan menurut Ps 4 angka 36). Pengecualian ini dipakai sebagai acuan; konflik laten C8 dicatat di WIKA-4-36
- PPh 21 yang ditanggung Perusahaan (Ps 22 ayat 2) adalah kenikmatan objek PPh 21 dan masuk bruto dengan full gross-up (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K3-K4)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Pembagian iuran JHT 2% dan JP 1% oleh pegawai mengikuti regulasi (PKB tidak menyebut)
- THR 1 x THP dibayar Maret 2025; uang cuti 1 x FP dibayar Juli (bulan tanggal masuk); tidak ada penghasilan lain
- Pegawai tetap di Indonesia: neto tidak disetahunkan, PTKP penuh (PMK 168/2023 Ps 15 ayat (3) hanya untuk kewajiban subjektif yang mulai/berakhir)
- Biaya jabatan bagian tahun = min(5% x bruto, 10 x Rp500.000) (tafsir K6)
- Uang pisah dikenai PPh 21 final PP 68/2009 (Ps 1 angka 4, Ps 2 ayat (1), PDF hlm. 2-3) dan tidak masuk perhitungan TER/Pasal 17
- Masa Pajak Terakhir (Oktober): PPh ditanggung = titik tetap PPh setahun - PPh Jan-Sep; bila lebih potong, PPh ditanggung Oktober = 0 dan kelebihan dikembalikan (tafsir K3 butir 2)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THP bulanan = FP + TG | 18.000.000 | WIKA-4-35, WIKA-19-3 |
| 2 | Premi JKK pemberi kerja 1.27% x 12000000 | 152.400 | PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 3 | Premi JKM pemberi kerja 0,30% x 12000000 | 36.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 4 | Premi JKN pemberi kerja 4% x min(12000000, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 5 | Bruto teratur sebulan tanpa PPh ditanggung | 18.668.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 6 | Uang pisah masa kerja 7 tahun 4 bulan (pita >6 s.d. 9 tahun) = 3 x FP | 36.000.000 | WIKA-90-1 |
| 7 | PPh 21 final uang pisah: lapisan 0% (s.d. Rp50.000.000) | 0 | PPh 21 final uang pesangon: PP 68/2009 Ps 1 angka 4 dan Ps 2 ayat (1) (PDF hlm. 2-3), lapisan 0% s.d. Rp50.000.000 (Ps 4 huruf a, PDF hlm. 4); dipisa… |
| 8 | PPh 21 bulan tanpa penghasilan tidak teratur (ditanggung): titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 18668400; bruto X + T = 20514725 masuk lapisan TER kategori A di atas 19750000 s.d. 24150000 = 9% | 1.846.325 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 9 | PPh 21 Maret, gaji + THR 18.000.000 (ditanggung): titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 36668400; bruto X + T = 43652857 masuk lapisan TER kategori A di atas 39100000 s.d. 43850000 = 16% | 6.984.457 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -4- (PDF hlm. 14); k… |
| 10 | PPh 21 Juli, gaji + uang cuti 12.000.000 (ditanggung): titik tetap terkecil T = R(TER(X + T) x (X + T)) dengan X = 30668400; bruto X + T = 36080471 masuk lapisan TER kategori A di atas 35400000 s.d. 39100000 = 15% | 5.412.071 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 11 | PPh dipotong (ditanggung) Jan-Sep = 7 bulan biasa + Maret + Juli | 25.320.803 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15) |
| 12 | PPh ditanggung Oktober: titik tetap PPh setahun - PPh Jan-Sep bernilai negatif (lebih potong), sehingga = 0 | 0 | tafsir K3 butir 2; PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16) |
| 13 | Bruto Jan-Okt = 10 bulan gaji + THR + uang cuti + PPh ditanggung Jan-Sep + PPh ditanggung Oktober | 242.004.803 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16); PPh ditanggung pemberi kerja = kenikmatan objek PPh 21… |
| 14 | Biaya jabatan = min(5% x bruto, 10 x 500.000) | 5.000.000 | PMK 168/2023 Ps 10 ayat (1) huruf a dan ayat (2) (PDF hlm. 11-12); plafon bagian tahun n x 500.000 (tafsir K6; PMK 168/2023 Lampiran B contoh, PDF hl… |
| 15 | Iuran JHT 10 x 240.000 + JP 2 x 100.423 (batas 2024) + 8 x 105.474 (batas 2025) | 3.444.638 | PMK 168/2023 Ps 10 ayat (1) huruf b (PDF hlm. 11-12); PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 16 | Neto = bruto - biaya jabatan - iuran | 233.560.165 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16) |
| 17 | PKP = neto - PTKP TK/0 54.000.000, dibulatkan ke bawah ribuan | 179.560.000 | PMK 168/2023 Ps 8 ayat (3)-(4) (PDF hlm. 10); PMK 101/PMK.010/2016 Ps 1 (PDF hlm. 2-3); kategori TER: PP 58/2023 Ps 2 ayat (4) (PDF hlm. 4); tables/p… |
| 18 | PPh Pasal 17: 5% x 60 jt + 15% x sisa | 20.934.000 | UU 7/2021 (HPP) Ps 3 angka 7, Pasal 17 ayat (1) huruf a UU PPh (PDF hlm. 56); tables/tarif_pasal17.csv |
| 19 | PPh Masa Pajak Terakhir (Oktober) = PPh setahun - PPh Jan-Sep (negatif = lebih potong, dikembalikan kepada pegawai) | -4.386.803 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16); pengembalian: PMK 168/2023 Ps 21 ayat (1) dan Ps 22 ay… |

</details>

**Di mana PPh 21 masuk:** Ya: setiap bulan PPh ditanggung di-gross-up dengan TER; Masa Pajak Terakhir dihitung ulang dengan tarif Pasal 17 dan menghasilkan lebih potong. Uang pisah dikenai PPh final terpisah (0%)

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| uang pisah | 36.000.000 | ya |
| PPh 21 Jan-Sep (beban perusahaan) | 19.941.456 | dikoreksi: 25.320.803 |
| PKP | 154.239.000 | dikoreksi: 179.560.000 |
| PPh 21 terutang Jan-Okt | 17.135.850 | dikoreksi: 20.934.000 |
| PPh Oktober (negatif = lebih potong) | -2.805.606 | dikoreksi: -4.386.803 |
| PPh final uang pisah | - | dikoreksi: ditambahkan, 0 |

**Pertanyaan:**

1. Batas biaya jabatan untuk bagian tahun: 10 x 500.000 (contoh) atau 6.000.000 setahun - bagaimana praktik Anda?

   Jawaban: Batas biaya jabatan bagian tahun = min(5% x bruto, n x 500.000): tafsir K6; PMK 168/2023 Lampiran B contoh 'maksimal 8 x Rp500.000' (PDF hlm. 39).

2. Lebih potong pada Masa Pajak Terakhir: karena PPh ditanggung perusahaan, apakah kelebihan menjadi hak pegawai atau dikembalikan ke perusahaan - bagaimana praktik Anda?

   Jawaban: Lebih potong di Masa Pajak Terakhir: PPh ditanggung bulan itu = 0 (tidak ada kenikmatan negatif, tafsir K3 butir 2) dan kelebihan wajib dikembalikan kepada pegawai paling lambat akhir bulan berikutnya (PMK 168/2023 Ps 21 ayat (1), Ps 22 ayat (2), PDF hlm. 21-22); pengecualian hanya untuk PPh DTP (Ps 21 ayat (2)).

3. Perlakuan PPh uang pisah (PPh final pesangon atau PPh 21 tidak teratur) - bagaimana praktik Anda?

   Jawaban: Uang pisah = uang pesangon dalam arti PP 68/2009 Ps 1 angka 4, PDF hlm. 2 ('dengan nama dan dalam bentuk apapun, sehubungan dengan berakhirnya masa kerja'): PPh 21 final, 0% untuk Rp36.000.000 (Ps 4 huruf a, PDF hlm. 4).

4. Sisa cuti: Ps 52 ayat 7 hanya untuk PHK huruf d-j; untuk pengunduran diri Ps 52 ayat 8 mengompensasikan dengan manfaat dana pensiun (tidak dihitung) - bagaimana praktik Anda?

   Jawaban: Sisa cuti pada pengunduran diri: Ps 52 ayat 7 hanya untuk PHK Ps 84 ayat (1) huruf d-j; ayat 8 mengompensasikan dengan manfaat dana pensiun. Tidak ada uang penggantian sisa cuti yang dihitung di contoh ini.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: gross-up bulanan dan Masa Pajak Terakhir (putusan 1 dan 4), PPh final uang pisah ditambahkan (putusan 7). PPh Jan-Sep 19.941.456 -> 25.320.803; PKP 154.239.000 -> 179.560.000; PPh setahun 17.135.850 -> 20.934.000; PPh Oktober -2.805.606 -> -4.386.803 (dikembalikan kepada pegawai); PPh final uang pisah 0

### GT5-WIKA-05: Kontrafaktual: WIKA dianggap eligible PPh 21 DTP 2025 (Januari 2025)

**Menguji:** Konflik C4 WIKA-22-3 vs PMK 10/2025 Ps 5 ayat (1): nilai DTP yang wajib dibayar tunai tetapi ditahan PKB  
**Klausul:** WIKA-22-3, WIKA-P22-3, WIKA-22-2 · **Tahun pajak:** 2025

**Masukan:** golongan = Pegawai Terampil; fixed_pay = 6000000; tunjangan_grade = 3000000; masa_pajak = 2025-01; status_ptkp = TK/0; kontrafaktual = KLU WIKA dianggap tercantum di Lampiran A PMK 10/2025 (aslinya tidak)

**Asumsi (setelah koreksi):**

- JKK 1,27%; dasar iuran = FP; PPh di luar DTP ditanggung perusahaan
- Kelayakan DTP: gaji dan tunjangan tetap-teratur Januari = FP + TG = 9.000.000 <= 10.000.000 (TG dibayar setiap bulan menurut jabatan; premi BPJS tidak dihitung, tafsir K5)
- Pada masa DTP PPh 21 ditanggung pemerintah, jadi tidak ada PPh yang ditanggung Perusahaan untuk di-gross-up (PMK 168/2023 Ps 7 huruf h)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THP = FP + TG | 9.000.000 | WIKA-4-35 |
| 2 | Premi JKK pemberi kerja 1.27% x 6000000 | 76.200 | PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 3 | Premi JKM pemberi kerja 0,30% x 6000000 | 18.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 4 | Premi JKN pemberi kerja 4% x min(6000000, 12.000.000) | 240.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 5 | Bruto Januari | 9.334.200 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 6 | PPh 21 Januari: TER kategori A untuk bruto 9334200 (di atas 8550000 s.d. 9650000) = 1.75% | 163.349 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -2- (PDF hlm. 12); k… |
| 7 | PPh 21 DTP yang menurut regulasi wajib dibayar tunai ke pegawai | 163.349 | PMK 10/2025 Ps 2-4 (PDF hlm. 4-5), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10) |
| 8 | Nilai yang diberikan menurut WIKA Ps 22 ayat 3 | 0 | WIKA-22-3 |
| 9 | Nilai konflik per bulan | 163.349 | C4 |

</details>

**Di mana PPh 21 masuk:** Ya: PPh 21 dihitung dengan TER; seluruhnya DTP dalam skenario kontrafaktual

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| bruto Januari | 9.334.200 | ya |
| PPh 21 Januari | 163.348 | dikoreksi: 163.349 |
| DTP wajib tunai (regulasi) | 163.348 | dikoreksi: 163.349 |
| nilai konflik per bulan | 163.348 | dikoreksi: 163.349 |

**Pertanyaan:**

1. Penjelasan Ps 22 ayat 3 mendefinisikan insentif pajak sebagai pengurang beban pajak perusahaan (contoh pajak badan); apakah PPh 21 DTP termasuk - bagaimana praktik Anda?

   Jawaban: Ps 22 ayat 3 mencakup PPh 21 DTP: Penjelasan mendefinisikan insentif sebagai pengurang 'beban pajak Perusahaan', dan PPh 21 pegawai adalah beban Perusahaan (ayat 2); daftar contoh pajak badan bersifat terbuka.

2. Apakah Tunjangan Grade ('tidak bersifat tetap') termasuk bruto tetap dan teratur untuk syarat Rp10 juta - bagaimana praktik Anda?

   Jawaban: Tunjangan Grade dibayar setiap bulan menurut jabatan sehingga termasuk 'tunjangan yang sifatnya tetap dan teratur setiap bulan' untuk kriteria DTP (PMK 10/2025 Ps 4 ayat (3), PDF hlm. 5; tafsir K5); di contoh ini kelayakan sama saja dengan atau tanpa TG.

3. Contoh ini kontrafaktual: dalam data asli WIKA tidak eligible sehingga konflik laten - bagaimana praktik Anda?

   Jawaban: Contoh kontrafaktual tetap dipakai sebagai acuan nilai konflik; pada data asli konflik WIKA-22-3 laten karena KLU konstruksi tidak tercantum di Lampiran A PMK 10/2025, PMK 72/2025, maupun PMK 105/2025.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: pembulatan Masa 2025 ke rupiah terdekat (tafsir K1): PPh/DTP/nilai konflik 163.348 -> 163.349

## PKB_Century_Textile_2024_2026

PT Century Textile Industry (tekstil), 2024-03-27 s.d. 2026-03-26

### GT5-CENTEX-01: Upah lembur hari biasa, hari libur group, dan lembur terjadwal giliran malam

**Menguji:** Dasar UP = (B..G)/173 dan pengali Lampiran 1; jam pecahan pada lembur terjadwal  
**Klausul:** CENTEX-L1, CENTEX-L1C, CENTEX-22-2, CENTEX-13-1d · **Tahun pajak:** 2025

**Masukan:** lembur_hari_biasa_jam = 3; lembur_libur_group_jam = 9; lembur_terjadwal_malam_jam = 1.25

**Asumsi (setelah koreksi):**

- Komponen upah (nominal tidak ada di PKB, dipilih untuk ilustrasi): B upah pokok 5.400.000; C uang makan 300.000; D tunjangan giliran 200.000; E jabatan 0; F keluarga 150.000; G perumahan 0; jumlah 6.050.000
- 'Satu bulan upah' untuk THR dan bonus = B+...+G (Ps 2 angka 14: upah termasuk tunjangan; komponen sama dengan definisi upah di Lampiran angka 1 huruf C)
- Dasar iuran BPJS = 6.050.000
- Perusahaan lolos keringanan JKK PP 7/2025 (tekstil, >= 50 peserta aktif, verifikasi BPJS, iuran s.d. Januari 2025 lunas): JKK 0,445% untuk iuran Feb 2025-Jan 2026
- PPh ditanggung perusahaan (Ps 28). KLU tekstil eligible DTP 2025 (PMK 10/2025) dan 2026 (PMK 105/2025); pegawai di contoh layak DTP sehingga PPh 21 ditanggung pemerintah, dibayar tunai, dan tidak di-gross-up
- PPh TER Masa 2025-2026 dibulatkan ke rupiah terdekat (tafsir K1)
- Jam lembur pecahan dibayar pro rata dengan pengali jam bersangkutan (0,25 jam pada pengali jam ke-2)
- Upah lembur dibulatkan ke rupiah terdekat

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | UP = (B+C+D+E+F+G)/173 | 34.971,10 | CENTEX-L1C |
| 2 | Hari biasa 3 jam: (1,5 + 2 + 2) x UP | 192.341 | CENTEX-L1 |
| 3 | Libur group 9 jam: (7 x 2 + 3 + 4) x UP | 734.393 | CENTEX-L1 |
| 4 | Lembur terjadwal 1,25 jam per giliran malam: (1,5 + 0,25 x 2) x UP | 69.942 | CENTEX-13-1d, CENTEX-L1 |

</details>

**Di mana PPh 21 masuk:** Ya, tidak langsung: upah lembur adalah penghasilan teratur yang masuk bruto bulan dibayar (PMK 168/2023 Ps 5 ayat (3) huruf a)

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| upah per jam (UP) | 34.971,10 | ya |
| lembur 3 jam hari biasa | 192.341 | ya |
| lembur 9 jam libur group | 734.393 | ya |
| lembur terjadwal per malam | 69.942 | ya |

**Pertanyaan:**

1. Perlakuan 0,25 jam lembur terjadwal tidak diatur - bagaimana praktik Anda?

   Jawaban: 0,25 jam lembur terjadwal giliran malam dibayar pro rata dengan pengali jam tempat pecahan itu jatuh (jam ke-2 = 2 x UP); Lampiran angka 1 tidak membedakan jam pecahan.

2. Pembulatan upah lembur tidak diatur - bagaimana praktik Anda?

   Jawaban: Upah lembur dibulatkan ke rupiah terdekat, sejalan dengan kaidah pembulatan rupiah penuh PER-11/PJ/2025 Ps 129 ayat (3) yang dipakai untuk PPh.

Setuju? / koreksi (keseluruhan contoh): ya

### GT5-CENTEX-02: THR 120% tanpa prorata, keringanan JKK, dan PPh 21 DTP pada PPh ditanggung (Maret 2025)

**Menguji:** Pembacaan literal Ps 24 (THR 120% tanpa prorata), konflik C6 (JKK 0,89% di PKB vs 0,445% regulasi) yang menggeser lapisan TER, DTP wajib tunai pada metode ditanggung  
**Klausul:** CENTEX-24, CENTEX-28, CENTEX-33-3a, CENTEX-34 · **Tahun pajak:** 2025

**Masukan:** tanggal_masuk = 2024-11-01; hari_raya = 2025-03-31; masa_pajak = 2025-03; status_ptkp = K/1

**Asumsi (setelah koreksi):**

- Komponen upah (nominal tidak ada di PKB, dipilih untuk ilustrasi): B upah pokok 5.400.000; C uang makan 300.000; D tunjangan giliran 200.000; E jabatan 0; F keluarga 150.000; G perumahan 0; jumlah 6.050.000
- 'Satu bulan upah' untuk THR dan bonus = B+...+G (Ps 2 angka 14: upah termasuk tunjangan; komponen sama dengan definisi upah di Lampiran angka 1 huruf C)
- Dasar iuran BPJS = 6.050.000
- Perusahaan lolos keringanan JKK PP 7/2025 (tekstil, >= 50 peserta aktif, verifikasi BPJS, iuran s.d. Januari 2025 lunas): JKK 0,445% untuk iuran Feb 2025-Jan 2026
- PPh ditanggung perusahaan (Ps 28). KLU tekstil eligible DTP 2025 (PMK 10/2025) dan 2026 (PMK 105/2025); pegawai di contoh layak DTP sehingga PPh 21 ditanggung pemerintah, dibayar tunai, dan tidak di-gross-up
- PPh TER Masa 2025-2026 dibulatkan ke rupiah terdekat (tafsir K1)
- THR dibayar penuh 120% walau masa kerja 5 bulan (PKB tidak mengatur prorata; lebih tinggi dari minimum)
- Pegawai mulai bekerja sebelum Januari 2025; gaji dan tunjangan tetap-teratur Januari 2025 = 6.050.000 <= 10 juta (layak DTP, tafsir K5)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THR = 120% x satu bulan upah | 7.260.000 | CENTEX-24 |
| 2 | Pembanding (ditolak): 5/12 x 120% x upah | 3.025.000 | pembanding |
| 3 | Premi JKK pemberi kerja 0.445% x 6050000 | 26.922,50 | PP 7/2025 Ps 4 ayat (1) (PDF hlm. 4), masa iuran Feb-Jul 2025 (Ps 10, PDF hlm. 6); diperpanjang s.d. iuran Jan 2026 oleh PP 36/2025 Ps 10A (PDF hlm. … |
| 4 | Premi JKM pemberi kerja 0,30% x 6050000 | 18.150 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 5 | Premi JKN pemberi kerja 4% x min(6050000, 12.000.000) | 242.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 6 | Bruto Maret = upah + THR + premi (JKK 0,445%) | 13.597.072,50 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 7 | PPh 21 Maret: TER kategori B untuk bruto 13597072.5 (di atas 12600000 s.d. 13600000) = 4% | 543.883 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -7- (PDF hlm. 17); k… |
| 8 | Nilai konflik C6: bruto bila JKK 0,89% sesuai angka PKB | 13.623.995 | CENTEX-33-3a |
| 9 | Nilai konflik C6: PPh bila JKK 0,89%: TER kategori B untuk bruto 13623995 (di atas 13600000 s.d. 14950000) = 5% | 681.200 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -7- (PDF hlm. 17); k… |
| 10 | PPh 21 DTP dibayar tunai ke pegawai (walau PPh ditanggung perusahaan) | 543.883 | PMK 10/2025 Ps 2-4 (PDF hlm. 4-5), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10); KLU tekstil: tables/klu_dtp.csv (PMK 10/2… |
| 11 | Iuran JHT pegawai 2% x 6050000 | 121.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 12 | Iuran JP pegawai 1% x min(6050000, batas upah 10547400 untuk iuran 2025-03) | 60.500 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 13 | Iuran JKN pegawai 1% x min(6050000, 12.000.000) | 60.500 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 14 | Uang diterima = upah + THR + DTP tunai - iuran JHT - JP - JKN | 13.611.883 | CENTEX-28; PMK 10/2025 Ps 2-4 (PDF hlm. 4-5), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10) |
| 15 | Pembanding pelaksanaan keliru: DTP tidak dibayarkan tunai | 13.068.000 | CENTEX-28 |

</details>

**Di mana PPh 21 masuk:** Ya: TER kategori B; seluruh PPh adalah DTP dan dibayar tunai; JKK lama 0,89% menggeser bruto ke lapisan 5%

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| THR | 7.260.000 | ya |
| bruto Maret (JKK 0,445%) | 13.597.072,50 | ya |
| PPh 21 Maret = DTP | 543.882 | dikoreksi: 543.883 |
| PPh bila JKK 0,89% (C6) | 681.199 | dikoreksi: 681.200 |
| DTP dibayar tunai | 543.882 | dikoreksi: 543.883 |
| uang diterima | 13.611.882 | dikoreksi: 13.611.883 |
| uang diterima bila DTP ditahan (C4) | 13.068.000 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |

**Pertanyaan:**

1. Ps 24 tidak memuat prorata dan merujuk 'Kesepakatan Bersama 26 Januari 2000' yang tidak tersedia; pembanding prorata 3.025.000 - bagaimana praktik Anda?

   Jawaban: Ps 24 dibaca harfiah: 120% x satu bulan upah bagi masa kerja >= 1 bulan, tanpa prorata. Lebih tinggi dari minimum Permenaker 6/2016 (Ps 3 ayat (1), PDF hlm. 4; Ps 4, PDF hlm. 5), jadi bukan konflik; isi Kesepakatan Bersama 26 Januari 2000 tidak tersedia dan tidak dipakai.

2. Komponen 'satu bulan upah' untuk THR tidak dirinci - bagaimana praktik Anda?

   Jawaban: 'Satu bulan upah' = B+C+D+E+F+G (Ps 2 angka 14 dan definisi upah di Lampiran angka 1 huruf C).

3. Apakah perusahaan benar-benar menerima keringanan JKK (syarat >= 50 pekerja aktif, iuran Januari lunas) - bagaimana praktik Anda?

   Jawaban: Keringanan JKK tidak otomatis: syaratnya >= 50 peserta aktif (PP 7/2025 Ps 3 ayat (3)), sektor tekstil (Ps 3 ayat (4)), verifikasi BPJS (Ps 5 ayat (1)-(2)), iuran s.d. Januari 2025 lunas (Ps 6 ayat (2)). Century memenuhinya sebagai asumsi; premi yang masuk bruto adalah premi yang dibayar (PMK 168/2023 Ps 5 ayat (3) huruf d; tafsir K7-K8).

Putusan tambahan: Tidak membayarkan DTP secara tunai adalah kesalahan pelaksanaan, bukan konflik teks Ps 28.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: pembulatan 2025 (PPh/DTP 543.882 -> 543.883; nilai konflik C6 681.199 -> 681.200; uang diterima 13.611.882 -> 13.611.883); pembanding DTP ditahan bukan konflik C4 melainkan kesalahan pelaksanaan dan dikeluarkan dari nilai harapan

### GT5-CENTEX-03: Bonus tahunan pita masa kerja dan DTP 2026 (Januari 2026)

**Menguji:** Pita masa kerja per 20 Desember (Ps 25 ayat 1-3), bonus dibayar 20 Januari, keringanan JKK Januari 2026, DTP PMK 105/2025  
**Klausul:** CENTEX-25, CENTEX-25-1, CENTEX-25-2, CENTEX-28, CENTEX-33-3a · **Tahun pajak:** 2026

**Masukan:** tanggal_masuk = 2025-04-01; tanggal_acuan_masa_kerja = 2025-12-20; masa_pajak = 2026-01; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- Komponen upah (nominal tidak ada di PKB, dipilih untuk ilustrasi): B upah pokok 5.400.000; C uang makan 300.000; D tunjangan giliran 200.000; E jabatan 0; F keluarga 150.000; G perumahan 0; jumlah 6.050.000
- 'Satu bulan upah' untuk THR dan bonus = B+...+G (Ps 2 angka 14: upah termasuk tunjangan; komponen sama dengan definisi upah di Lampiran angka 1 huruf C)
- Dasar iuran BPJS = 6.050.000
- Perusahaan lolos keringanan JKK PP 7/2025 (tekstil, >= 50 peserta aktif, verifikasi BPJS, iuran s.d. Januari 2025 lunas): JKK 0,445% untuk iuran Feb 2025-Jan 2026
- PPh ditanggung perusahaan (Ps 28). KLU tekstil eligible DTP 2025 (PMK 10/2025) dan 2026 (PMK 105/2025); pegawai di contoh layak DTP sehingga PPh 21 ditanggung pemerintah, dibayar tunai, dan tidak di-gross-up
- PPh TER Masa 2025-2026 dibulatkan ke rupiah terdekat (tafsir K1)
- alfa = 0 (tidak didefinisikan; nilai pasti minimal)
- Upah bulan Desember = upah periode 21 November-20 Desember 2025, sebelum kenaikan yang berlaku 21 Desember = 6.050.000
- Gaji dan tunjangan tetap-teratur Januari 2026 = 6.050.000 <= 10 juta (layak DTP 2026, tafsir K5)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Masa kerja 1 Apr 2025 - 20 Des 2025 = 8 bulan 19 hari -> pita 6 s.d. <9 bulan | 8 | CENTEX-25-1, CENTEX-25-2 |
| 2 | Bonus = 50% x (1 bulan upah Desember + alfa) | 3.025.000 | CENTEX-25-1 |
| 3 | Premi JKK pemberi kerja 0.445% x 6050000 | 26.922,50 | PP 7/2025 Ps 4 ayat (1) (PDF hlm. 4), masa iuran Feb-Jul 2025 (Ps 10, PDF hlm. 6); diperpanjang s.d. iuran Jan 2026 oleh PP 36/2025 Ps 10A (PDF hlm. … |
| 4 | Premi JKM pemberi kerja 0,30% x 6050000 | 18.150 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 5 | Premi JKN pemberi kerja 4% x min(6050000, 12.000.000) | 242.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 6 | Bruto Januari 2026 | 9.362.072,50 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 7 | PPh 21 Januari 2026: TER kategori A untuk bruto 9362072.5 (di atas 8550000 s.d. 9650000) = 1.75% | 163.836 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -2- (PDF hlm. 12); k… |
| 8 | PPh 21 DTP 2026 dibayar tunai | 163.836 | PMK 105/2025 Ps 2-4 (PDF hlm. 4-6), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10); KLU tekstil: tables/klu_dtp.csv (PMK 105… |
| 9 | Iuran JHT pegawai 2% x 6050000 | 121.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 10 | Iuran JP pegawai 1% x min(6050000, batas upah 10547400 untuk iuran 2026-01) | 60.500 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 11 | Iuran JKN pegawai 1% x min(6050000, 12.000.000) | 60.500 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 12 | Uang diterima Januari 2026 | 8.996.836 | CENTEX-28; PMK 105/2025 Ps 2-4 (PDF hlm. 4-6), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10) |

</details>

**Di mana PPh 21 masuk:** Ya: bonus masuk bruto Januari tahun berikutnya; TER kategori A; DTP 2026

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| bonus | 3.025.000 | ya |
| bruto Januari 2026 | 9.362.072,50 | ya |
| PPh 21 Januari 2026 = DTP | 163.836 | ya |
| uang diterima | 8.996.836 | ya |

**Pertanyaan:**

1. Nilai alfa tidak didefinisikan - bagaimana praktik Anda?

   Jawaban: Alfa tidak didefinisikan; acuan memakai alfa = 0 sebagai nilai pasti minimal.

2. Upah Desember: kenaikan upah berlaku 21 Desember (Ps 20 ayat 2e) sehingga 'upah bulan Desember' bisa sudah naik - bagaimana praktik Anda?

   Jawaban: Century memakai periode upah 21-20 (kenaikan berlaku 21 Desember, penilaian 21 November-20 November, Lampiran angka 6), jadi 'upah bulan Desember' = upah periode 21 November-20 Desember, sebelum kenaikan.

Setuju? / koreksi (keseluruhan contoh): ya (asumsi upah Desember dipertegas: periode 21 November-20 Desember sebelum kenaikan)

### GT5-CENTEX-04: Potongan absen Pekerja Bulanan II dan penggantian sisa cuti

**Menguji:** Rumus Lampiran 3 (faktor 1,125 untuk 4 group 3 shift) dan Lampiran 2 (1,5 x upah harian /30)  
**Klausul:** CENTEX-L3, CENTEX-L2, CENTEX-15-1, CENTEX-44-1 · **Tahun pajak:** 2025

**Masukan:** hari_alpha = 2; hari_sisa_cuti = 4; kehadiran_setahun = 99%; masa_pajak = 2025-02; status_ptkp = K/1

**Asumsi (setelah koreksi):**

- Komponen upah (nominal tidak ada di PKB, dipilih untuk ilustrasi): B upah pokok 5.400.000; C uang makan 300.000; D tunjangan giliran 200.000; E jabatan 0; F keluarga 150.000; G perumahan 0; jumlah 6.050.000
- 'Satu bulan upah' untuk THR dan bonus = B+...+G (Ps 2 angka 14: upah termasuk tunjangan; komponen sama dengan definisi upah di Lampiran angka 1 huruf C)
- Dasar iuran BPJS = 6.050.000
- Perusahaan lolos keringanan JKK PP 7/2025 (tekstil, >= 50 peserta aktif, verifikasi BPJS, iuran s.d. Januari 2025 lunas): JKK 0,445% untuk iuran Feb 2025-Jan 2026
- PPh ditanggung perusahaan (Ps 28). KLU tekstil eligible DTP 2025 (PMK 10/2025) dan 2026 (PMK 105/2025); pegawai di contoh layak DTP sehingga PPh 21 ditanggung pemerintah, dibayar tunai, dan tidak di-gross-up
- PPh TER Masa 2025-2026 dibulatkan ke rupiah terdekat (tafsir K1)
- Potongan mengurangi bruto; dasar iuran BPJS tidak ikut turun

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Potongan 4 group 3 shift = 2/30 x gaji pokok x 1,125 | 405.000 | CENTEX-L3 (Lampiran angka 3) |
| 2 | Potongan non 4 group 3 shift = 2/30 x gaji pokok | 360.000 | CENTEX-L3 (Lampiran angka 3) |
| 3 | Penggantian sisa cuti = 1,5 x (B+...+G)/30 x 4 | 1.210.000 | CENTEX-L2 (Lampiran angka 2), CENTEX-15-1 |
| 4 | Premi JKK pemberi kerja 0.445% x 6050000 | 26.922,50 | PP 7/2025 Ps 4 ayat (1) (PDF hlm. 4), masa iuran Feb-Jul 2025 (Ps 10, PDF hlm. 6); diperpanjang s.d. iuran Jan 2026 oleh PP 36/2025 Ps 10A (PDF hlm. … |
| 5 | Premi JKM pemberi kerja 0,30% x 6050000 | 18.150 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(6050000, 12.000.000) | 242.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Februari (4 group 3 shift, dengan potongan) | 5.932.072,50 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 8 | PPh 21 Februari: TER kategori B untuk bruto 5932072.5 (di atas 0 s.d. 6200000) = 0% | 0 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -6- (PDF hlm. 16); k… |

</details>

**Di mana PPh 21 masuk:** Ya: bruto Februari di bawah batas TER B 0% (6.200.000) sehingga PPh 0

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| potongan 2 hari alpha (4 group 3 shift) | 405.000 | ya |
| potongan 2 hari alpha (non 4G3S) | 360.000 | ya |
| penggantian 4 hari sisa cuti | 1.210.000 | ya |
| bruto Februari | 5.932.072,50 | ya |
| PPh 21 Februari | 0 | ya |

**Pertanyaan:**

1. Apakah potongan absen mengurangi bruto PPh atau diperlakukan sebagai potongan setelah pajak - bagaimana praktik Anda?

   Jawaban: Potongan absen mengurangi bruto karena bagian upah itu tidak diterima pegawai (PMK 168/2023 Ps 8 ayat (2) huruf a, PDF hlm. 10).

2. Dasar faktor 1,125 tidak dijelaskan - bagaimana praktik Anda?

   Jawaban: Faktor 1,125 tertulis eksplisit di Lampiran angka 3 huruf a untuk pola 4 group 3 shift dan dipakai apa adanya; PKB tidak menjelaskan asalnya dan nilai itu tidak bertentangan dengan aturan wajib (potongan atas hari tidak bekerja).

Setuju? / koreksi (keseluruhan contoh): ya

## PKB_AVCO_2024_2026

PT Airfast Aviation Facilities / AVCO (jasa penerbangan), 2024-04-01 s.d. 2026-03-31

### GT5-AVCO-01: Upah lembur pola 5-2 dan PPh 21 bulan berjalan (Mei 2025)

**Menguji:** Upah/173, pengali hari kerja dan hari istirahat (Lampiran III: 2/3/4 untuk jam 1-7/8/9+), skala upah 1 April 2025  
**Klausul:** AVCO-22-3a, AVCO-22-3b1, AVCO-22-3b3, AVCO-L2, AVCO-23-5, AVCO-41-2 · **Tahun pajak:** 2025

**Masukan:** golongan = B3; upah_pokok = 12238300; lembur_hari_kerja_jam = 3; lembur_hari_istirahat_jam = 10; hari_hadir = 21; masa_pajak = 2025-05; status_ptkp = K/2

**Asumsi (setelah koreksi):**

- 'Upah bulanan' untuk lembur = upah (Lampiran III angka 3); golongan Pratama tidak punya tunjangan tetap di PKB sehingga = upah pokok
- Dasar iuran BPJS = upah pokok; JKK 1,74% sesuai Ps 41
- PPh 21 dipotong dari pegawai (Ps 20 ayat 10); AVCO bukan KLU DTP
- Makan siang natura Rp47.000/hari bagi seluruh pekerja tidak masuk bruto (PMK 66/2023 Ps 4 huruf a)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Transport Rp28.000/hari hadir (dataran rendah)
- Upah lembur dibayar pada bulan yang sama

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Upah lembur per jam = 12.238.300 / 173 | 70.741,62 | AVCO-22-3a; AVCO-L2 (Lampiran II, PDF hlm. 64) |
| 2 | Lembur: hari kerja (1,5 + 2 + 2) + hari istirahat 10 jam (7 x 2 + 3 + 2 x 4) = 30,5 jam-pengali | 2.157.619 | AVCO-22-3b1, AVCO-22-3b3 (Lampiran III angka 1, PDF hlm. 65) |
| 3 | Transport 21 x 28.000 | 588.000 | AVCO-23-5 |
| 4 | Premi JKK pemberi kerja 1.74% x 12238300 | 212.946,42 | AVCO-41-2; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 5 | Premi JKM pemberi kerja 0,30% x 12238300 | 36.714,90 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(12238300, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Mei | 15.713.580,32 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 8 | PPh 21 Mei (dipotong): TER kategori B untuk bruto 15713580.32 (di atas 14950000 s.d. 16400000) = 6% | 942.815 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -7- (PDF hlm. 17); k… |
| 9 | Iuran JHT pegawai 2% x 12238300 | 244.766 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 10 | Iuran JP pegawai 1% x min(12238300, batas upah 10547400 untuk iuran 2025-05) | 105.474 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 11 | Iuran JKN pegawai 1% x min(12238300, 12.000.000) | 120.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 12 | Uang diterima | 13.570.864 | AVCO-20-10 |

</details>

**Di mana PPh 21 masuk:** Ya: upah lembur penghasilan teratur; TER kategori B

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| upah lembur per jam | 70.741,62 | ya |
| upah lembur sebulan | 2.157.619 | ya |
| bruto Mei | 15.713.580,32 | ya |
| PPh 21 Mei | 942.814 | dikoreksi: 942.815 |
| uang diterima | 13.570.865 | dikoreksi: 13.570.864 |

**Pertanyaan:**

1. 'Upah bulanan' (Ps 22 ayat 3a) tidak didefinisikan - bagaimana praktik Anda?

   Jawaban: 'Upah bulanan' = upah (Lampiran III angka 3; Ps 1 angka 83), dengan dasar lembur upah pokok + tunjangan tetap (PP 35/2021 Ps 32 ayat (1)-(3), PDF hlm. 20; dasar 75% dari keseluruhan upah menurut ayat (4) hanya bila upah pokok + tunjangan tetap < 75% upah, tidak terjadi pada contoh ini); bagi Pratama = upah pokok.

2. Pola 5-2 di Lampiran III memakai pengali 2/3/4 untuk jam 1-7/8/9+ (lebih tinggi dari pola 5 hari umum); contoh mengikuti PKB - bagaimana praktik Anda?

   Jawaban: Pengali pola 5-2 di Lampiran III (2/3/4 untuk jam 1-7/8/9+) lebih tinggi dari minimum dan dipakai apa adanya.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: pembulatan 2025: PPh Mei 942.814 -> 942.815; uang diterima 13.570.865 -> 13.570.864

### GT5-AVCO-02: THR 2 bulan upah pokok prorata 7 bulan dan PPh 21 (Maret 2025)

**Menguji:** THR 2 x upah pokok, prorata masa kerja/12, skala upah 2024 masih berlaku sebelum 1 April 2025, batas upah JP 2025  
**Klausul:** AVCO-23-1, AVCO-23-1a, AVCO-23-3, AVCO-23-5, AVCO-41-2, AVCO-41-4 · **Tahun pajak:** 2025

**Masukan:** golongan = C2; upah_pokok = 10169300; tanggal_masuk = 2024-09-01; hari_raya = 2025-03-31; hari_gilir = 20; hari_hadir = 20; masa_pajak = 2025-03; status_ptkp = K/2

**Asumsi (setelah koreksi):**

- 'Upah bulanan' untuk lembur = upah (Lampiran III angka 3); golongan Pratama tidak punya tunjangan tetap di PKB sehingga = upah pokok
- Dasar iuran BPJS = upah pokok; JKK 1,74% sesuai Ps 41
- PPh 21 dipotong dari pegawai (Ps 20 ayat 10); AVCO bukan KLU DTP
- Makan siang natura Rp47.000/hari bagi seluruh pekerja tidak masuk bruto (PMK 66/2023 Ps 4 huruf a)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Prorata = masa kerja (bulan penuh) / 12 x THR penuh; THR dibulatkan ke rupiah terdekat
- Kerja gilir bukan di tambang: Rp30.000/hari

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THR = 7/12 x 2 x 10.169.300 (dibulatkan ke rupiah) | 11.864.183 | AVCO-23-1, AVCO-23-1a; AVCO-L2 (Lampiran I, PDF hlm. 63) |
| 2 | Tunjangan gilir 20 x 30.000 | 600.000 | AVCO-23-3 |
| 3 | Transport 20 x 28.000 | 560.000 | AVCO-23-5 |
| 4 | Premi JKK pemberi kerja 1.74% x 10169300 | 176.945,82 | AVCO-41-2; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 5 | Premi JKM pemberi kerja 0,30% x 10169300 | 30.507,90 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(10169300, 12.000.000) | 406.772 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Maret | 23.807.708,72 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 8 | PPh 21 Maret (dipotong): TER kategori B untuk bruto 23807708.72 (di atas 21850000 s.d. 26000000) = 9% | 2.142.694 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -7- (PDF hlm. 17); k… |
| 9 | Iuran JHT pegawai 2% x 10169300 | 203.386 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 10 | Iuran JP pegawai 1% x min(10169300, batas upah 10547400 untuk iuran 2025-03) | 101.693 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 11 | Iuran JKN pegawai 1% x min(10169300, 12.000.000) | 101.693 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 12 | Uang diterima | 20.644.017 | AVCO-20-10 |

</details>

**Di mana PPh 21 masuk:** Ya: THR masuk bruto Maret; TER kategori B

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| THR prorata | 11.864.183 | ya |
| bruto Maret | 23.807.708,72 | ya |
| PPh 21 Maret | 2.142.693 | dikoreksi: 2.142.694 |
| iuran JP (batas 2025 berlaku iuran Maret) | 101.693 | ya |
| uang diterima | 20.644.018 | dikoreksi: 20.644.017 |

**Pertanyaan:**

1. Rumus prorata THR tidak ditulis di PKB - bagaimana praktik Anda?

   Jawaban: 'Proporsional' = masa kerja (bulan penuh sampai hari raya)/12 x THR penuh (Permenaker 6/2016 Ps 3 ayat (1) huruf b, PDF hlm. 4).

2. Pembulatan THR - bagaimana praktik Anda?

   Jawaban: THR dibulatkan ke rupiah terdekat.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: pembulatan 2025: PPh Maret 2.142.693 -> 2.142.694; uang diterima 20.644.018 -> 20.644.017

### GT5-AVCO-03: Tunjangan Radiasi Rp950.000 'net': gross-up dalam TER (Juni 2025)

**Menguji:** Pengecualian parsial metode gross (Ps 23 ayat 8a): perusahaan menanggung PPh atas tunjangan radiasi; efek lompatan lapisan TER  
**Klausul:** AVCO-23-8, AVCO-20-10, AVCO-41-2 · **Tahun pajak:** 2025

**Masukan:** golongan = A1; upah_pokok = 13367100; tunjangan_radiasi_net = 950000; masa_pajak = 2025-06; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- 'Upah bulanan' untuk lembur = upah (Lampiran III angka 3); golongan Pratama tidak punya tunjangan tetap di PKB sehingga = upah pokok
- Dasar iuran BPJS = upah pokok; JKK 1,74% sesuai Ps 41
- PPh 21 dipotong dari pegawai (Ps 20 ayat 10); AVCO bukan KLU DTP
- Makan siang natura Rp47.000/hari bagi seluruh pekerja tidak masuk bruto (PMK 66/2023 Ps 4 huruf a)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Tunjangan radiasi diberikan penuh Rp950.000 bersih dan tidak masuk dasar iuran BPJS (besarnya 'maksimal' dan terkait penugasan sebagai RSO, sehingga tunjangan tidak tetap menurut Ps 1 angka 81)
- PPh tambahan akibat tunjangan ditanggung Perusahaan (metode selisih) dan merupakan kenikmatan; tunjangan bruto G = 950.000 + T, T = titik tetap terkecil dari T = R(TER(B0 + 950.000 + T) x (B0 + 950.000 + T)) - PPh(B0)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Premi JKK pemberi kerja 1.74% x 13367100 | 232.587,54 | AVCO-41-2; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 2 | Premi JKM pemberi kerja 0,30% x 13367100 | 40.101,30 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 3 | Premi JKN pemberi kerja 4% x min(13367100, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 4 | Bruto tanpa tunjangan radiasi (B0) | 14.119.788,84 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 5 | PPh tanpa tunjangan radiasi: TER kategori A untuk bruto 14119788.84 (di atas 13750000 s.d. 15100000) = 6% | 847.187 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -2- (PDF hlm. 12); k… |
| 6 | PPh tambahan karena tunjangan radiasi, ditanggung Perusahaan: titik tetap terkecil T = R(TER(X + T) x (X + T)) - 847187 dengan X = 15069788.84; bruto X + T = 15293119.84 masuk lapisan TER kategori A di atas 15100000 s.d. 16950000 = 7% | 223.331 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 7 | Tunjangan radiasi bruto = 950.000 + PPh tambahan | 1.173.331 | AVCO-23-8; PPh ditanggung pemberi kerja = kenikmatan objek PPh 21, full gross-up: PMK 168/2023 Lampiran B Bagian Kedua I.4 (PDF hlm. 44); titik tetap… |
| 8 | Bruto Juni = B0 + tunjangan bruto | 15.293.119,84 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 9 | PPh 21 Juni total: TER kategori A untuk bruto 15293119.84 (di atas 15100000 s.d. 16950000) = 7% | 1.070.518 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -3- (PDF hlm. 13); k… |
| 10 | Cek: tunjangan bersih = tunjangan bruto - PPh tambahan | 950.000 | AVCO-23-8 |
| 11 | PPh yang tetap dipotong dari pegawai (bagian upah biasa) | 847.187 | AVCO-20-10 |
| 12 | Pembanding (ditolak): gross-up dengan tarif lapisan baru saja = 950.000 / (1 - 7%) | 1.021.505 | pembanding |

</details>

**Di mana PPh 21 masuk:** Ya: PPh dihitung TER kategori A atas bruto termasuk tunjangan bruto; PPh tambahan (termasuk lompatan 6% ke 7%) ditanggung perusahaan

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| bruto tanpa radiasi | 14.119.788,84 | ya |
| tunjangan radiasi gross | 1.173.331 | ya |
| PPh 21 Juni total | 1.070.518 | ya |
| PPh ditanggung perusahaan | 223.331 | ya |
| tunjangan bersih (>= 950.000) | 950.000 | ya |
| pembanding gross-up marginal | 1.021.505 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| PPh dipotong dari pegawai | - | dikoreksi: ditambahkan, 847.187 |

**Pertanyaan:**

1. Arti 'net' dan metode gross-up tidak diatur; karena TER berlaku atas seluruh bruto, tunjangan menaikkan tarif seluruh bruto (6% ke 7%) sehingga PPh tambahan jauh di atas 7% x tunjangan - bagaimana praktik Anda?

   Jawaban: 'Net' berarti PPh atas tunjangan ditanggung Perusahaan. Karena PPh yang ditanggung adalah kenikmatan (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44), tunjangan bruto = 950.000 + PPh tambahan, dihitung sebagai titik tetap terkecil (tafsir K3) dengan metode selisih; lompatan lapisan TER atas seluruh bruto ikut ditanggung Perusahaan. Gross-up dengan tarif marginal ditolak karena tidak menghasilkan 950.000 bersih.

2. Apakah tunjangan radiasi adalah tunjangan tetap (masuk dasar iuran BPJS) - bagaimana praktik Anda?

   Jawaban: Tunjangan radiasi tidak masuk dasar iuran BPJS: besarnya 'maksimal' dan melekat pada penugasan RSO, sehingga tunjangan tidak tetap menurut definisi PKB sendiri (Ps 1 angka 80-81).

3. Perlakuan di Masa Pajak Desember (perhitungan ulang setahun) tidak diatur - bagaimana praktik Anda?

   Jawaban: Masa Pajak Desember: kaidah selisih yang sama atas PPh setahun (Perusahaan menanggung PPh setahun dengan tunjangan dikurangi PPh setahun tanpa tunjangan).

Setuju? / koreksi (keseluruhan contoh): ya untuk nilai (223.331 dan 1.173.331 adalah titik tetap terkecil); dasar diganti dari 'G terkecil' menjadi kenikmatan titik tetap (putusan 3); pembanding marginal dikeluarkan dari nilai harapan; PPh dipotong pegawai 847.187 ditambahkan ke nilai harapan

### GT5-AVCO-04: Potongan mangkir satu hari (Juli 2025)

**Menguji:** Rumus potongan upah pokok/173 x jam kerja reguler, beda pola 5-2 (8 jam) dan 6-1 (7 jam); transport hilang hari itu  
**Klausul:** AVCO-24-3, AVCO-23-5, AVCO-1-80 · **Tahun pajak:** 2025

**Masukan:** golongan = B3; upah_pokok = 12238300; hari_mangkir = 1; hari_hadir = 20; masa_pajak = 2025-07; status_ptkp = TK/0

**Asumsi (setelah koreksi):**

- 'Upah bulanan' untuk lembur = upah (Lampiran III angka 3); golongan Pratama tidak punya tunjangan tetap di PKB sehingga = upah pokok
- Dasar iuran BPJS = upah pokok; JKK 1,74% sesuai Ps 41
- PPh 21 dipotong dari pegawai (Ps 20 ayat 10); AVCO bukan KLU DTP
- Makan siang natura Rp47.000/hari bagi seluruh pekerja tidak masuk bruto (PMK 66/2023 Ps 4 huruf a)
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Potongan mengurangi bruto; dasar iuran BPJS tidak berubah

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Pola 5-2 (8 jam reguler): 12.238.300 / 173 x 8 | 565.933 | AVCO-24-3; Lampiran III angka 1 huruf a |
| 2 | Pola 6-1 (7 jam reguler): 12.238.300 / 173 x 7 | 495.191 | AVCO-24-3; Lampiran III angka 2 huruf a |
| 3 | Transport hanya 20 hari hadir | 560.000 | AVCO-23-5 |
| 4 | Premi JKK pemberi kerja 1.74% x 12238300 | 212.946,42 | AVCO-41-2; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 5 | Premi JKM pemberi kerja 0,30% x 12238300 | 36.714,90 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(12238300, 12.000.000) | 480.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Juli (pola 5-2) | 12.962.028,32 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10); PMK 168/2023 Ps 8 ayat (2) huruf a |
| 8 | PPh 21 Juli: TER kategori A untuk bruto 12962028.32 (di atas 12500000 s.d. 13750000) = 5% | 648.101 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -2- (PDF hlm. 12); k… |

</details>

**Di mana PPh 21 masuk:** Ya: bruto turun; dalam contoh ini lapisan TER tetap 5%

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| potongan mangkir pola 5-2 | 565.933 | ya |
| potongan mangkir pola 6-1 | 495.191 | ya |
| bruto Juli | 12.962.028,32 | ya |
| PPh 21 Juli | 648.101 | ya |

**Pertanyaan:**

1. Apakah potongan hukuman mengurangi bruto PPh - bagaimana praktik Anda?

   Jawaban: Potongan hukuman mengurangi bruto karena upah itu tidak diterima pegawai (PMK 168/2023 Ps 8 ayat (2) huruf a, PDF hlm. 10).

2. Jam kerja reguler 7 atau 8 jam bergantung jadwal (Ps 1 angka 26) - bagaimana praktik Anda?

   Jawaban: Jam kerja reguler mengikuti pola jadwal: 8 jam untuk pola 5-2, 7 jam untuk pola 6-1 (Lampiran III angka 1-2 huruf a).

Setuju? / koreksi (keseluruhan contoh): ya

## PKB_Taekwang_2024_2026

PT TKG Taekwang Indonesia (alas kaki), 2024-03 s.d. 2026-03-28

### GT5-TKG-01: THR dengan tambahan masa kerja, THR prorata, dan PPh 21 DTP (Maret 2025)

**Menguji:** Tambahan THR 20% untuk masa kerja 4 tahun, prorata pegawai baru, DTP pada metode gross (PPh tidak mengurangi upah)  
**Klausul:** TKG-53-1, TKG-53-2, TKG-53-3, TKG-53-4, TKG-46, TKG-50-2 · **Tahun pajak:** 2025

**Masukan:** pegawai_A = masa_kerja: 4 tahun 2 bulan, status_ptkp: K/0; pegawai_B = tanggal_masuk: 2024-11-01, masa_kerja: 5 bulan; hari_raya = 2025-03-31; hari_masuk = 22; masa_pajak = 2025-03

**Asumsi (setelah koreksi):**

- Nominal (tidak ada di PKB, dipilih untuk ilustrasi): gaji pokok 3.600.000; tunjangan senioritas 100.000 (tunjangan tetap); upah = 3.700.000; tunjangan kehadiran 150.000/bulan; transport 15.000/hari masuk
- Tingkat risiko JKK alas kaki diasumsikan 'rendah' 0,54%; perusahaan lolos keringanan PP 7/2025 (alas kaki, >= 50 peserta aktif, verifikasi BPJS) sehingga 0,27% untuk iuran Feb 2025-Jan 2026
- Dasar iuran BPJS = gaji pokok + tunjangan tetap
- PPh 21 metode gross (Ps 46); KLU alas kaki eligible DTP 2025 dan 2026
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- PPh dihitung untuk pegawai A; gaji dan tunjangan tetap-teratur Januari 2025 = 3.700.000 <= 10 juta (layak DTP, tafsir K5)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THR pegawai A = (1 + 20%) x upah | 4.440.000 | TKG-53-1, TKG-53-2, TKG-53-4 |
| 2 | THR pegawai B = 5/12 x upah (dibulatkan) | 1.541.667 | TKG-53-3 |
| 3 | Transport 22 x 15.000 | 330.000 | TKG-42-4 |
| 4 | Premi JKK pemberi kerja 0.27% x 3700000 | 9.990 | PP 7/2025 Ps 4 ayat (1) (PDF hlm. 4), masa iuran Feb-Jul 2025 (Ps 10, PDF hlm. 6); diperpanjang s.d. iuran Jan 2026 oleh PP 36/2025 Ps 10A (PDF hlm. … |
| 5 | Premi JKM pemberi kerja 0,30% x 3700000 | 11.100 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(3700000, 12.000.000) | 148.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Maret pegawai A | 8.789.090 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 8 | PPh 21 Maret pegawai A: TER kategori A untuk bruto 8789090 (di atas 8550000 s.d. 9650000) = 1.75% | 153.809 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -2- (PDF hlm. 12); k… |
| 9 | PPh yang mengurangi upah (DTP: dipotong lalu dibayar kembali tunai, atau tidak dipotong) | 0 | PMK 10/2025 Ps 2-4 (PDF hlm. 4-5), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10); KLU alas kaki: tables/klu_dtp.csv (PMK 10… |
| 10 | Iuran JHT pegawai 2% x 3700000 | 74.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 11 | Iuran JP pegawai 1% x min(3700000, batas upah 10547400 untuk iuran 2025-03) | 37.000 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (tafsir K11) |
| 12 | Iuran JKN pegawai 1% x min(3700000, 12.000.000) | 37.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 13 | Uang diterima pegawai A | 8.472.000 | TKG-46; PMK 10/2025 Ps 2-4 (PDF hlm. 4-5), Ps 5 ayat (1)-(2) (PDF hlm. 6); PMK 168/2023 Ps 7 huruf h (PDF hlm. 10) |
| 14 | Pembanding pelaksanaan keliru: PPh dipotong dan DTP tidak dibayarkan | 8.318.191 | TKG-46 |

</details>

**Di mana PPh 21 masuk:** Ya: TER kategori A; seluruh PPh DTP

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| THR pegawai A | 4.440.000 | ya |
| THR pegawai B (prorata) | 1.541.667 | ya |
| bruto Maret pegawai A | 8.789.090 | ya |
| PPh 21 Maret = DTP | 153.809 | ya |
| uang diterima pegawai A | 8.472.000 | ya |
| uang diterima bila PPh dipotong (C4) | 8.318.191 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |

**Pertanyaan:**

1. Masa kerja tepat 1 bulan tidak tercakup ('lebih dari 1 bulan') - C10 laten - bagaimana praktik Anda?

   Jawaban: Syarat 'lebih dari 1 bulan' (Ps 53 ayat 3) di bawah Permenaker 6/2016 Ps 2 ayat (1) (PDF hlm. 3) untuk masa kerja tepat 1 bulan: C10 laten; pegawai B (5 bulan) tidak terdampak.

2. Tingkat risiko JKK dan status keringanan perusahaan - bagaimana praktik Anda?

   Jawaban: Tingkat risiko JKK ditetapkan per perusahaan (PP 44/2015 Ps 16); 0,54% dipakai sebagai asumsi. Keringanan berlaku bila syarat PP 7/2025 Ps 3 ayat (3)-(4), Ps 5, Ps 6 ayat (2) terpenuhi.

Putusan tambahan: Pada metode gross, PPh DTP tidak boleh mengurangi upah; tidak membayarkannya adalah kesalahan pelaksanaan, bukan konflik teks Ps 46.

Setuju? / koreksi (keseluruhan contoh): ya untuk nilai; pembanding 'PPh dipotong' bukan konflik C4 melainkan kesalahan pelaksanaan dan dikeluarkan dari nilai harapan

### GT5-TKG-02: Upah lembur hari kerja 4 jam dan hari istirahat pola 5 hari

**Menguji:** Dasar 1/173 x (gaji pokok + tunjangan tetap); jam lembur ke-4 hari kerja mengikuti regulasi yang dirujuk Ps 44 ayat 1  
**Klausul:** TKG-44-2, TKG-44-3a, TKG-44-3b, TKG-27-5, TKG-44-3e · **Tahun pajak:** 2025

**Masukan:** lembur_hari_kerja_jam = 4; lembur_hari_istirahat_5hari_jam = 10

**Asumsi (setelah koreksi):**

- Nominal (tidak ada di PKB, dipilih untuk ilustrasi): gaji pokok 3.600.000; tunjangan senioritas 100.000 (tunjangan tetap); upah = 3.700.000; tunjangan kehadiran 150.000/bulan; transport 15.000/hari masuk
- Tingkat risiko JKK alas kaki diasumsikan 'rendah' 0,54%; perusahaan lolos keringanan PP 7/2025 (alas kaki, >= 50 peserta aktif, verifikasi BPJS) sehingga 0,27% untuk iuran Feb 2025-Jan 2026
- Dasar iuran BPJS = gaji pokok + tunjangan tetap
- PPh 21 metode gross (Ps 46); KLU alas kaki eligible DTP 2025 dan 2026
- PPh TER Masa 2025 dibulatkan ke rupiah terdekat (tafsir K1)
- Jam ke-4 hari kerja dibayar 2x: Ps 44 ayat 1 merujuk peraturan perundang-undangan (PP 35/2021 Ps 31 ayat (1) huruf b, PDF hlm. 19)
- Dibulatkan ke rupiah terdekat

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Upah lembur per jam = 3.700.000 / 173 | 21.387,28 | TKG-44-2 |
| 2 | Hari kerja 4 jam: (1,5 + 2 + 2 + 2) x upah per jam | 160.405 | TKG-44-3a; jam ke-4 melalui Ps 44 ayat 1: PP 35/2021 Ps 31 ayat (1) huruf b (PDF hlm. 19) |
| 3 | Pembanding: bagian yang tertulis di Ps 44 ayat 3 huruf a (jam 1-3): 5,5 x upah per jam | 117.630 | TKG-44-3a |
| 4 | Hari istirahat pola 5 hari, 10 jam: (8 x 2 + 3 + 4) x upah per jam | 491.908 | TKG-44-3b |

</details>

**Di mana PPh 21 masuk:** Ya, tidak langsung: lembur bulan M dibayar bersama upah bulan M (tanggal 10 bulan M+1) dan masuk bruto Masa Pajak M (PMK 168/2023 Ps 19 ayat (1) huruf a, PDF hlm. 20)

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| upah lembur per jam | 21.387,28 | ya |
| lembur 4 jam hari kerja | 160.405 | ya |
| bagian jam 1-3 menurut PKB | 117.630 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| lembur 10 jam hari istirahat | 491.908 | ya |

**Pertanyaan:**

1. Pengali jam lembur ke-4 pada hari kerja tidak diatur - bagaimana praktik Anda?

   Jawaban: Jam lembur ke-4 hari kerja = 2x upah per jam lewat rujukan Ps 44 ayat 1 ke regulasi; ini celah yang diisi regulasi, bukan konflik.

Setuju? / koreksi (keseluruhan contoh): ya untuk nilai; jam ke-4 bukan konflik C10 (diisi regulasi lewat Ps 44 ayat 1); pembanding literal dikeluarkan dari nilai harapan

### GT5-TKG-03: Upah prorata pegawai baru mulai 10 Juni 2025

**Menguji:** Prorata upah bulan pertama (Ps 37 ayat 3) dengan dua kemungkinan pembagi; syarat DTP pegawai baru diuji pada bulan pertama  
**Klausul:** TKG-37-3, TKG-41-4, TKG-42-4, TKG-46 · **Tahun pajak:** 2025

**Masukan:** tanggal_masuk = 2025-06-10; masa_pajak = 2025-06; status_ptkp = TK/0; hari_kerja_dijalani = 15

**Asumsi (setelah koreksi):**

- Nominal (tidak ada di PKB, dipilih untuk ilustrasi): gaji pokok 3.600.000; tunjangan senioritas 100.000 (tunjangan tetap); upah = 3.700.000; tunjangan kehadiran 150.000/bulan; transport 15.000/hari masuk
- Tingkat risiko JKK alas kaki diasumsikan 'rendah' 0,54%; dengan keringanan PP 7/2025 menjadi 0,27% (iuran Feb 2025-Jan 2026), perusahaan dianggap memenuhi syarat
- Dasar iuran BPJS = gaji pokok + tunjangan tetap
- PPh 21 metode gross (Ps 46); KLU alas kaki eligible DTP 2025 dan 2026
- Tunjangan kehadiran tidak dibayar karena tidak bekerja satu bulan penuh; transport 15 hari
- Iuran BPJS bulan pertama dari upah sebulan penuh
- Pembagi prorata = hari kalender (10-30 Juni = 21 dari 30 hari) karena periode upah tanggal 1 s.d. akhir bulan (Ps 37 ayat 4); pembanding hari kerja hanya dicatat

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Upah prorata hari kalender = 21/30 x 3.700.000 | 2.590.000 | TKG-37-3 |
| 2 | Pembanding: hari kerja = 15/21 x 3.700.000 (dibulatkan) | 2.642.857 | TKG-37-3 |
| 3 | Transport 15 x 15.000 | 225.000 | TKG-42-4 |
| 4 | Premi JKK pemberi kerja 0.27% x 3700000 | 9.990 | PP 7/2025 Ps 4 ayat (1) (PDF hlm. 4), masa iuran Feb-Jul 2025 (Ps 10, PDF hlm. 6); diperpanjang s.d. iuran Jan 2026 oleh PP 36/2025 Ps 10A (PDF hlm. … |
| 5 | Premi JKM pemberi kerja 0,30% x 3700000 | 11.100 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 6 | Premi JKN pemberi kerja 4% x min(3700000, 12.000.000) | 148.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 7 | Bruto Juni | 2.984.090 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 8 | PPh 21 Juni: TER kategori A untuk bruto 2984090 (di atas 0 s.d. 5400000) = 0% | 0 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -1- (PDF hlm. 11); k… |

</details>

**Di mana PPh 21 masuk:** Ya: bruto di bawah batas TER A 0% sehingga PPh 0; tetap tercatat sebagai pegawai eligible DTP

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| upah Juni (hari kalender) | 2.590.000 | ya |
| upah Juni (hari kerja, pembanding) | 2.642.857 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| bruto Juni | 2.984.090 | ya |
| PPh 21 Juni | 0 | ya |

**Pertanyaan:**

1. Pembagi prorata (hari kalender, hari kerja, 25/30 tetap) tidak disebut - bagaimana praktik Anda?

   Jawaban: Pembagi = hari kalender: Ps 37 ayat 4 menetapkan periode upah tanggal 1 s.d. tanggal terakhir bulan.

2. Apakah tunjangan kehadiran dibayar sebagian untuk bulan pertama - bagaimana praktik Anda?

   Jawaban: Tunjangan kehadiran tidak dibayar untuk bulan pertama yang tidak penuh (Ps 41 ayat 3: dibayar penuh bila masuk satu bulan kerja berturut-turut).

3. Dasar iuran BPJS bulan pertama: penuh atau prorata - bagaimana praktik Anda?

   Jawaban: Iuran BPJS bulan pertama dari upah sebulan penuh: dasar iuran adalah upah sebulan (PP 44/2015 Ps 19, PDF hlm. 13; PP 46/2015 Ps 17, PDF hlm. 11), bukan upah yang diprorata.

4. Syarat DTP pegawai baru: bruto tetap dan teratur bulan pertama = upah prorata 2.590.000 - bagaimana praktik Anda?

   Jawaban: Kelayakan DTP pegawai baru diuji pada bulan pertama bekerja dengan gaji dan tunjangan tetap-teratur yang ditetapkan (3.700.000) <= 10 juta (PMK 10/2025 Ps 4 ayat (2) huruf b angka 2; tafsir K5).

Setuju? / koreksi (keseluruhan contoh): ya; pembanding hari kerja dikeluarkan dari nilai harapan (pembagi hari kalender diputuskan)

### GT5-TKG-04: Gugurnya tunjangan kehadiran dan transport karena mangkir (Juli 2025)

**Menguji:** Aturan gugur 100% sebulan (Ps 41 ayat 4a, Ps 42 ayat 4a) dan hilang per hari karena terlambat  
**Klausul:** TKG-41-4, TKG-42-4, TKG-46 · **Tahun pajak:** 2025

**Masukan:** kasus_1 = mangkir 1 hari, masuk 21 hari; kasus_2 = terlambat tanpa izin 2 kali, masuk 22 hari; hari_kerja_bulan = 22

**Asumsi (setelah koreksi):**

- Nominal (tidak ada di PKB, dipilih untuk ilustrasi): gaji pokok 3.600.000; tunjangan senioritas 100.000 (tunjangan tetap); upah = 3.700.000; tunjangan kehadiran 150.000/bulan; transport 15.000/hari masuk
- Tingkat risiko JKK alas kaki diasumsikan 'rendah' 0,54%; dengan keringanan PP 7/2025 menjadi 0,27% (iuran Feb 2025-Jan 2026), perusahaan dianggap memenuhi syarat
- Dasar iuran BPJS = gaji pokok + tunjangan tetap
- PPh 21 dipotong (Ps 46); KLU alas kaki eligible DTP 2025 dan 2026
- Nilai harian tunjangan kehadiran = 150.000 / 22 hari kerja (PKB tidak menyebut pembagi)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Kasus 1: tunjangan kehadiran gugur 100% | 0 | TKG-41-4 |
| 2 | Kasus 1: transport hangus 100% untuk bulan itu | 0 | TKG-42-4 |
| 3 | Kasus 2: tunjangan kehadiran hilang 2 hari = 150.000 x 20/22 (dibulatkan) | 136.364 | TKG-41-4 |
| 4 | Kasus 2: transport 22 hari (terlambat tidak menghilangkan transport) | 330.000 | TKG-42-4 |

</details>

**Di mana PPh 21 masuk:** Ya, tidak langsung: tunjangan tidak tetap yang gugur tidak masuk bruto

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| tunjangan kehadiran kasus 1 | 0 | ya |
| transport kasus 1 | 0 | ya |
| tunjangan kehadiran kasus 2 | 136.364 | ya |
| transport kasus 2 | 330.000 | ya |

**Pertanyaan:**

1. Besar potongan upah untuk hari mangkir (Ps 46 angka 1) tidak diatur sehingga tidak dihitung - bagaimana praktik Anda?

   Jawaban: Potongan upah untuk hari mangkir tidak dihitung karena Ps 46 angka 1 tidak menetapkan besarnya; prinsip no work no pay berlaku tetapi nilainya di luar PKB.

2. Nilai harian tunjangan kehadiran (pembagi) tidak diatur - bagaimana praktik Anda?

   Jawaban: Nilai harian tunjangan kehadiran = tunjangan bulanan / jumlah hari kerja bulan itu (22), karena tunjangan hilang 'pada hari yang ditinggalkan' (Ps 41 ayat 4 huruf b dan d).

Setuju? / koreksi (keseluruhan contoh): ya

## PKB_Sansan_2021_2024

PT Sansan Saudaratex Jaya (garmen/tekstil), 2021-09-23 s.d. 2024-09-23

### GT5-SANSAN-01: THR prorata 8 bulan dan kasus tepat 1 bulan (April 2024)

**Menguji:** Rumus (masa kerja/12) x 1 bulan upah, batas 'lebih dari 1 bulan' (C10 laten), PPh 21 bulan THR  
**Klausul:** SANSAN-41-1, SANSAN-41-2, SANSAN-31-3, SANSAN-37-2, SANSAN-36-1, SANSAN-52-2a · **Tahun pajak:** 2024

**Masukan:** pegawai_A = tanggal_masuk: 2023-08-10, masa_kerja: 8 bulan, status_ptkp: TK/0; pegawai_B = tanggal_masuk: 2024-03-10, masa_kerja: tepat 1 bulan; hari_raya = 2024-04-10; masa_pajak = 2024-04

**Asumsi (setelah koreksi):**

- Operator: gaji pokok 3.700.000, tanpa tunjangan jabatan; upah = 3.700.000 (nominal dipilih untuk ilustrasi)
- Divisi garmen: JKK 0,24%; JKN 4% (PKB tidak menyebut tarif JKN; mengikuti Perpres)
- Tahun pajak 2024 (rezim TER); tidak ada PPh 21 DTP padat karya pada 2024
- PPh 21 dipotong dari pegawai (Ps 31 ayat 8)
- Pegawai A: premi hadir yang ditetapkan perusahaan 740.000 (hadir penuh; di bawah batas 25% x upah pokok = 925.000); uang makan 15.000 x 22 hari
- PPh TER Masa 2024: desimal dibuang (tafsir K1)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | THR pegawai A = 8/12 x 3.700.000 (dibulatkan) | 2.466.667 | SANSAN-41-2 |
| 2 | THR pegawai B menurut PKB (masa kerja tidak 'lebih dari 1 bulan') | 0 | SANSAN-41-2 |
| 3 | THR pegawai B menurut Permenaker 6/2016 = 1/12 x upah (dibulatkan) | 308.333 | Permenaker 6/2016 Ps 2 ayat (1) dan Ps 3 ayat (1) huruf b (PDF hlm. 3-4) |
| 4 | Premi hadir A (nilai yang ditetapkan, di bawah batas Ps 37 ayat 2) | 740.000 | SANSAN-37-2 |
| 5 | Uang makan 22 x 15.000 | 330.000 | SANSAN-36-1 |
| 6 | Premi JKK pemberi kerja 0.24% x 3700000 | 8.880 | SANSAN-52-2a; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 1… |
| 7 | Premi JKM pemberi kerja 0,30% x 3700000 | 11.100 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 8 | Premi JKN pemberi kerja 4% x min(3700000, 12.000.000) | 148.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 9 | Bruto April pegawai A | 7.404.647 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 10 | PPh 21 April pegawai A (dipotong): TER kategori A untuk bruto 7404647 (di atas 6750000 s.d. 7500000) = 1.25% | 92.558 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf A (Tarif Efektif Bulanan Kategori A), hlm. lampiran -1- (PDF hlm. 11); k… |
| 11 | Iuran JHT pegawai 2% x 3700000 | 74.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 12 | Iuran JP pegawai 1% x min(3700000, batas upah 10042300 untuk iuran 2024-04) | 37.000 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv |
| 13 | Iuran JKN pegawai 1% x min(3700000, 12.000.000) | 37.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 14 | Uang diterima pegawai A | 6.996.109 | SANSAN-31-8 |

</details>

**Di mana PPh 21 masuk:** Ya: THR masuk bruto April; TER kategori A

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| THR pegawai A | 2.466.667 | ya |
| THR pegawai B menurut PKB | 0 | ya |
| THR pegawai B menurut regulasi (C10) | 308.333 | ya |
| bruto April A | 7.404.647 | ya |
| PPh 21 April A | 92.558 | ya |
| uang diterima A | 6.996.109 | ya |

**Pertanyaan:**

1. 'lebih dari 1 bulan' vs 'sekurang-kurangnya 1 bulan' (C10 laten) - bagaimana praktik Anda?

   Jawaban: Syarat 'lebih dari 1 bulan' tidak mencakup masa kerja tepat 1 bulan, sedangkan Permenaker 6/2016 Ps 2 ayat (1) (PDF hlm. 3) memberi hak sejak masa kerja 1 bulan: C10 laten; nilai yang wajib dibayar 308.333.

2. Masa kerja dihitung sampai hari raya atau sampai tanggal pembayaran - bagaimana praktik Anda?

   Jawaban: Masa kerja dihitung sampai hari raya: THR adalah pendapatan yang dibayarkan menjelang hari raya (Permenaker 6/2016 Ps 1 angka 1, PDF hlm. 2) dan besarnya ditentukan masa kerja (Ps 2 ayat (1) dan Ps 3 ayat (1), PDF hlm. 3-4); karena pasal tidak menyebut tanggal hitung, hari raya dipakai sebagai titik hitung.

Setuju? / koreksi (keseluruhan contoh): ya (premi hadir 740.000 dicatat sebagai nilai yang ditetapkan, di bawah batas 925.000)

### GT5-SANSAN-02: Dua pembacaan batas premi hadir

**Menguji:** Batas premi hadir Ps 37 ayat 2a ('20% dari upah pokok dan premi hadir') dan gugur 50%/100% karena absen  
**Klausul:** SANSAN-37-2 · **Tahun pajak:** 2024

**Masukan:** upah_pokok = 3700000; absen_hari = [0, 1, 2]

**Asumsi (setelah koreksi):**

- Operator: gaji pokok 3.700.000, tanpa tunjangan jabatan; upah = 3.700.000 (nominal dipilih untuk ilustrasi)
- Divisi garmen: JKK 0,24%; JKN 4% (PKB tidak menyebut tarif JKN; mengikuti Perpres)
- Tahun pajak 2024 (rezim TER); tidak ada PPh 21 DTP padat karya pada 2024
- PPh 21 dipotong dari pegawai (Ps 31 ayat 8)
- Premi dihitung pada batas maksimum menurut pembacaan harfiah

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Pembanding (ditolak): premi = 20% x upah pokok | 740.000 | SANSAN-37-2 |
| 2 | Batas premi = 20% x (upah pokok + premi) -> premi = 0,2/0,8 x upah pokok = 25% x upah pokok | 925.000 | SANSAN-37-2 |
| 3 | Pembanding (ditolak): absen 1 hari, pembacaan 20% x upah pokok | 370.000 | SANSAN-37-2 |
| 4 | Absen 1 hari: premi hilang 50% | 462.500 | SANSAN-37-2 |
| 5 | Absen 2 hari: premi hilang seluruhnya | 0 | SANSAN-37-2 |

</details>

**Di mana PPh 21 masuk:** Ya, tidak langsung: premi hadir masuk bruto teratur

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| premi maksimum (pembacaan A) | 740.000 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| premi maksimum (pembacaan B) | 925.000 | ya |
| absen 1 hari (A) | 370.000 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| absen 1 hari (B) | 462.500 | ya |
| absen 2 hari | 0 | ya |

**Pertanyaan:**

1. Pembacaan mana yang dimaksud; contoh tidak memilih, keduanya dicatat sebagai nilai acuan bersyarat - bagaimana praktik Anda?

   Jawaban: Dibaca harfiah: '20% dari upah pokok dan premi hadir' = 20% dari jumlah keduanya (pola rumusan '75% dari jumlah upah pokok dan tunjangan tetap', UU 13/2003 Ps 94, PDF hlm. 38), sehingga premi <= 25% x upah pokok = 925.000.

Setuju? / koreksi (keseluruhan contoh): dikoreksi: pembacaan harfiah dipilih (batas 20% x (upah pokok + premi) = 925.000; absen 1 hari 462.500); pembacaan 20% x upah pokok dikeluarkan dari nilai harapan

### GT5-SANSAN-03: Iuran JP tanpa batas upah (C8) dan PPh 21 Desember 2024

**Menguji:** Iuran JP dengan batas upah (E01, E05) dan pengaruhnya ke Masa Pajak Desember; pembacaan tanpa batas dicatat sebagai pembanding  
**Klausul:** SANSAN-52-2d, SANSAN-41-1, SANSAN-31-3, SANSAN-31-8 · **Tahun pajak:** 2024

**Masukan:** gaji_pokok = 9500000; tunjangan_jabatan = 1500000; status_ptkp = K/1; thr_bulan = 2024-04

**Asumsi (setelah koreksi):**

- Divisi garmen: JKK 0,24%; JKN 4% (PKB tidak menyebut tarif JKN; mengikuti Perpres)
- Tahun pajak 2024 (rezim TER); tidak ada PPh 21 DTP padat karya pada 2024
- PPh 21 dipotong dari pegawai (Ps 31 ayat 8)
- Pegawai berjabatan: upah = 9.500.000 + 1.500.000 = 11.000.000 tetap sepanjang 2024; tidak ada premi hadir/lembur
- THR 1 x upah dibayar April; tidak ada penghasilan lain

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Premi JKK pemberi kerja 0.24% x 11000000 | 26.400 | SANSAN-52-2a; PP 44/2015 Ps 16 ayat (1) (PDF hlm. 12); masuk bruto: PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 1… |
| 2 | Premi JKM pemberi kerja 0,30% x 11000000 | 33.000 | PP 44/2015 Ps 18 ayat (1) (PDF hlm. 13) |
| 3 | Premi JKN pemberi kerja 4% x min(11000000, 12.000.000) | 440.000 | Perpres 75/2019 Pasal I angka 2-3 (Ps 30 ayat (2), Ps 32 ayat (1)) (PDF hlm. 2-3); batas upah Rp12.000.000 |
| 4 | Bruto teratur sebulan | 11.499.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 5 | PPh 21 bulan biasa: TER kategori B untuk bruto 11499400 (di atas 11250000 s.d. 11600000) = 2.5% | 287.485 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -6- (PDF hlm. 16); k… |
| 6 | Bruto April = bruto teratur + THR | 22.499.400 | PMK 168/2023 Ps 5 ayat (3) huruf a-b, d-e (PDF hlm. 9); Ps 8 ayat (2) (PDF hlm. 10) |
| 7 | PPh 21 April: TER kategori B untuk bruto 22499400 (di atas 21850000 s.d. 26000000) = 9% | 2.024.946 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15); PP 58/2023 Lampiran huruf B (Tarif Efektif Bulanan Kategori B), hlm. lampiran -7- (PDF hlm. 17); k… |
| 8 | PPh dipotong Jan-Nov = 10 bulan biasa + April | 4.899.796 | PMK 168/2023 Ps 15 ayat (1) huruf a (PDF hlm. 15) |
| 9 | Bruto setahun | 148.992.800 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16) |
| 10 | Biaya jabatan = min(5% x bruto, 6.000.000) | 6.000.000 | PMK 168/2023 Ps 10 ayat (1) huruf a dan ayat (2) (PDF hlm. 11-12) |
| 11 | Iuran JP setahun menurut batas upah: 2 x 1% x 9.559.600 + 10 x 1% x 10.042.300 | 1.195.422 | PP 45/2015 Ps 28-29 (PDF hlm. 20-21); batas upah dari tables/bpjs.csv (E01, E05) |
| 12 | Pembanding (ditolak, pembacaan tanpa batas upah): Iuran JP setahun menurut PKB: 12 x 1% x 11.000.000 | 1.320.000 | SANSAN-52-2d (dibaca tanpa batas; ditolak) |
| 13 | Iuran JHT setahun 12 x 2% x 11.000.000 | 2.640.000 | PP 46/2015 Ps 16 ayat (1)-(2) (PDF hlm. 11) |
| 14 | Neto (regulasi) | 139.157.378 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16); PMK 168/2023 Ps 10 ayat (1) huruf b (PDF hlm. 11-12) |
| 15 | PKP (regulasi) = neto - PTKP K/1 63.000.000, dibulatkan ke bawah ribuan | 76.157.000 | PMK 168/2023 Ps 8 ayat (3)-(4) (PDF hlm. 10); PMK 101/PMK.010/2016 Ps 1 (PDF hlm. 2-3); kategori TER: PP 58/2023 Ps 2 ayat (4) (PDF hlm. 4); tables/p… |
| 16 | PPh setahun (regulasi) | 5.423.550 | UU 7/2021 (HPP) Ps 3 angka 7, Pasal 17 ayat (1) huruf a UU PPh (PDF hlm. 56); tables/tarif_pasal17.csv |
| 17 | PPh Desember (regulasi) = PPh setahun - PPh Jan-Nov | 523.754 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16) |
| 18 | Pembanding (ditolak, pembacaan tanpa batas upah): Neto (pkb) | 139.032.800 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16); PMK 168/2023 Ps 10 ayat (1) huruf b (PDF hlm. 11-12) |
| 19 | Pembanding (ditolak, pembacaan tanpa batas upah): PKP (pkb) = neto - PTKP K/1 63.000.000, dibulatkan ke bawah ribuan | 76.032.000 | PMK 168/2023 Ps 8 ayat (3)-(4) (PDF hlm. 10); PMK 101/PMK.010/2016 Ps 1 (PDF hlm. 2-3); kategori TER: PP 58/2023 Ps 2 ayat (4) (PDF hlm. 4); tables/p… |
| 20 | Pembanding (ditolak, pembacaan tanpa batas upah): PPh setahun (pkb) | 5.404.800 | UU 7/2021 (HPP) Ps 3 angka 7, Pasal 17 ayat (1) huruf a UU PPh (PDF hlm. 56); tables/tarif_pasal17.csv |
| 21 | Pembanding (ditolak, pembacaan tanpa batas upah): PPh Desember (pkb) = PPh setahun - PPh Jan-Nov | 505.004 | PMK 168/2023 Ps 1 angka 18 (PDF hlm. 4); Ps 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16) |
| 22 | Pembanding: Kelebihan potongan JP pegawai menurut PKB | 124.578 | pembanding pembacaan tanpa batas |
| 23 | Pembanding: Selisih PPh setahun (regulasi - PKB) | 18.750 | pembanding pembacaan tanpa batas |

</details>

**Di mana PPh 21 masuk:** Ya: Masa Pajak Desember dihitung ulang; iuran JP adalah pengurang sehingga kelebihan iuran menurunkan PPh

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| PPh dipotong Jan-Nov | 4.899.796 | ya |
| iuran JP pegawai setahun (regulasi) | 1.195.422 | ya |
| iuran JP pegawai setahun (PKB) | 1.320.000 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| PPh Desember (regulasi) | 523.754 | ya |
| PPh Desember (PKB literal) | 505.004 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| kelebihan potongan JP | 124.578 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |
| selisih PPh setahun | 18.750 | dikoreksi: dikeluarkan dari nilai harapan (pembanding) |

**Pertanyaan:**

1. Apakah 'upah sebulan' untuk iuran JP di PKB memang dimaksudkan tanpa batas atau hanya penulisan ringkas - bagaimana praktik Anda?

   Jawaban: '2% x upah sebulan' adalah penulisan ringkas yang sama dengan PP 45/2015 Ps 28 ayat (3); batas upah (Ps 29 ayat (2)-(3)) tetap berlaku. Bukan konflik C8.

2. JKN: PKB tidak menyebut tarif; batas Rp12 juta tidak terlampaui di contoh ini - bagaimana praktik Anda?

   Jawaban: JKN: PKB tidak menyebut tarif; mengikuti Perpres 82/2018 jo. 75/2019 (4% + 1%, batas Rp12 juta, tidak terlampaui di contoh ini).

Setuju? / koreksi (keseluruhan contoh): dikoreksi: klausul JP bukan konflik C8; nilai harapan = perhitungan dengan batas upah (PPh Desember 523.754); nilai pembacaan tanpa batas menjadi pembanding

### GT5-SANSAN-04: Uang pisah operator masa kerja 16 tahun (Lampiran 2)

**Menguji:** Rumus UMK x faktor (Lampiran angka 2); salah ketik angka ilustrasi baris faktor 1,6; PPh final uang pisah  
**Klausul:** SANSAN-L2 · **Tahun pajak:** 2024

**Masukan:** masa_kerja = 16 tahun; faktor = 1.6; umk_ilustrasi = UMK Kota Cimahi 2021 tanpa sen, Rp3.241.929 (direkonstruksi dari tujuh baris ilustrasi Lampiran angka 2)

**Asumsi (setelah koreksi):**

- UMK berjalan tidak ada di dataset; contoh memakai UMK ilustrasi Rp3.241.929 yang mereproduksi tujuh baris lain dengan pembulatan ke rupiah terdekat
- Uang pisah dikenai PPh 21 final PP 68/2009 (uang pesangon dalam arti luas, Ps 1 angka 4, PDF hlm. 2)

<details><summary>Langkah hitung (setelah koreksi)</summary>

| No | Uraian | Hasil | Sumber |
|---|---|---|---|
| 1 | Cek baris faktor 0,6 (tercetak 1.945.157) | 1.945.157 | SANSAN-L2 |
| 2 | Cek baris faktor 1,8 (tercetak 5.835.472) | 5.835.472 | SANSAN-L2 |
| 3 | Cek baris faktor 2,3 (tercetak 7.456.437) | 7.456.437 | SANSAN-L2 |
| 4 | Uang pisah = 1,6 x UMK (dibulatkan ke rupiah) | 5.187.086 | SANSAN-L2 |
| 5 | Angka tercetak di ilustrasi untuk faktor 1,6 | 5.192.086 | SANSAN-L2 |
| 6 | Selisih angka tercetak - rumus (salah ketik) | 5.000 | SANSAN-L2 |
| 7 | PPh 21 final uang pisah: lapisan 0% (s.d. Rp50.000.000) | 0 | PPh 21 final uang pesangon: PP 68/2009 Ps 1 angka 4 dan Ps 2 ayat (1) (PDF hlm. 2-3), lapisan 0% s.d. Rp50.000.000 (Ps 4 huruf a, PDF hlm. 4); dipisa… |

</details>

**Di mana PPh 21 masuk:** Tidak masuk TER/Pasal 17: uang pisah dikenai PPh 21 final PP 68/2009 (0% untuk nilai ini, Ps 4 huruf a)

| Nilai harapan | Rp | Setuju? / koreksi |
|---|---|---|
| uang pisah (rumus) | 5.187.085 | dikoreksi: 5.187.086 |
| angka ilustrasi PKB | 5.192.086 | ya |
| selisih ilustrasi vs rumus | 5.001 | dikoreksi: 5.000 |
| PPh final uang pisah | - | dikoreksi: ditambahkan, 0 |

**Pertanyaan:**

1. Angka ilustrasi baris 1,6 (5.192.086) tidak sesuai rumus (sekitar 5.187.086); baris lain cocok dengan selisih <= 2 rupiah. Acuan memakai rumus - bagaimana praktik Anda?

   Jawaban: Acuan memakai rumus: angka 5.192.086 adalah salah ketik dari 5.187.086 (selisih tepat 5.000); UMK ilustrasi Rp3.241.929 mereproduksi ketujuh baris lain.

2. UMK tahun berjalan dan kota unit produksi harus ditetapkan saat dipakai - bagaimana praktik Anda?

   Jawaban: Saat dipakai, UMK yang berlaku adalah UMK tahun berjalan kota unit produksi (catatan Lampiran angka 2).

Putusan tambahan: Uang pisah = uang pesangon dalam arti PP 68/2009 Ps 1 angka 4 (PDF hlm. 2): PPh 21 final, 0% s.d. Rp50 juta (Ps 4 huruf a, PDF hlm. 4).

Setuju? / koreksi (keseluruhan contoh): dikoreksi: UMK ilustrasi Rp3.241.929 (bukan 1.945.157/0,6): uang pisah 5.187.085 -> 5.187.086, selisih ilustrasi 5.001 -> 5.000 (salah ketik); PPh final 0 ditambahkan

## Pertanyaan umum

1. **PPh ditanggung perusahaan.** Di kantor Anda, apakah PPh 21 yang ditanggung perusahaan (bukan tunjangan pajak) ditambahkan ke bruto pegawai? Contoh WIKA dan Century memakai metode net.

   Jawaban: Ya, sejak Masa Juli 2023. PPh yang ditanggung pemberi kerja adalah kenikmatan objek PPh 21 dan dihitung *full gross-up* (PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; PMK 66/2023 Ps 23 ayat (4); tafsir K3-K4). Angkanya sama dengan metode tunjangan pajak tetapi tidak dipotong dari gaji. WIKA-01 s.d. 04 sudah dikoreksi. Century tidak berubah karena pegawainya layak DTP: PPh ditanggung pemerintah, jadi tidak ada PPh yang ditanggung perusahaan untuk di-*gross-up*.

2. **DTP.** Untuk metode *gross* (Taekwang), apakah benar DTP berarti PPh tidak dipotong sehingga gaji bersih naik sebesar PPh itu; dan untuk metode ditanggung (Century), apakah nilai DTP dibayar tunai di atas gaji?

   Jawaban: Ya untuk keduanya. PMK 10/2025 dan PMK 105/2025 Ps 5 ayat (1) (PDF hlm. 6): DTP wajib dibayar tunai saat pembayaran penghasilan, termasuk bila pemberi kerja memberi tunjangan PPh atau menanggung PPh; ayat (2): pembayaran itu bukan penghasilan. Pada metode *gross* PPh dipotong lalu dibayarkan kembali (atau tidak dipotong), hasil bersihnya sama. Pada metode ditanggung nilai DTP dibayar di atas gaji. Kegagalan membayarkan DTP adalah kesalahan pelaksanaan, bukan konflik teks PKB.

3. **Potongan hukuman/absen.** Apakah potongan upah karena mangkir atau sanksi mengurangi bruto PPh 21?

   Jawaban: Ya. Bruto adalah penghasilan yang diterima atau diperoleh (PMK 168/2023 Ps 8 ayat (2) huruf a, PDF hlm. 10); upah yang dipotong tidak diterima pegawai.

4. **Pesangon dan uang pisah.** Apakah uang pisah dikenai PPh 21 final pesangon (PP 68/2009) atau PPh 21 biasa sebagai penghasilan tidak teratur?

   Jawaban: PPh 21 final PP 68/2009 (Ps 2 ayat (1), PDF hlm. 3). Uang pesangon didefinisikan sebagai penghasilan 'dengan nama dan dalam bentuk apapun, sehubungan dengan berakhirnya masa kerja atau terjadi pemutusan hubungan kerja, termasuk uang penghargaan masa kerja dan uang penggantian hak' (Ps 1 angka 4, PDF hlm. 2), sehingga uang pisah tercakup. Tarif (Ps 4, PDF hlm. 4) 0% s.d. Rp50 juta, 5% di atas Rp50-100 juta, 15% di atas Rp100-500 juta, 25% di atasnya. Penghasilan ini dipisahkan dari TER dan Pasal 17 (PER-16/PJ/2016 Ps 18, PDF hlm. 15). Contoh WIKA-04 dan SANSAN-04 kini memuat PPh final 0.

## Hasil

- [ ] Disetujui
- [x] Disetujui dengan perubahan (tulis di atas)
- [ ] Perlu revisi

Status: selesai
