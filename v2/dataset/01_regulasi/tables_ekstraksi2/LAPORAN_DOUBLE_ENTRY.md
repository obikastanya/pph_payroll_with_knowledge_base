# Laporan Double-Entry — Ekstraksi Kedua Tabel Parameter PPh 21 / BPJS

Tanggal: 2026-10-01
Folder ekstraksi kedua: `dataset/01_regulasi/tables_ekstraksi2/`
Pembanding (ekstraksi pertama): `dataset/01_regulasi/tables/` (tidak diubah)

## 1. Metode

- **Independen.** Folder `dataset/01_regulasi/tables/` dan `kb/regulasi/tabel_manifest.yaml` tidak dibuka sebelum semua CSV ekstraksi kedua selesai ditulis. Folder `tables/` baru dibuka pada tahap perbandingan.
- **Sumber nilai = gambar halaman, bukan text layer.** Setiap halaman PDF dirender ke PNG dengan pypdfium2, lalu dibaca secara visual:
  - PP 58/2023: hlm. 3–5 dan 11–25, skala 3 (sekitar 1840 x 2830 px per halaman).
  - UU 7/2021 (HPP): hlm. 55–56, skala 3. Hlm. 56 dipotong menjadi dua bagian (atas/bawah) supaya tabel Pasal 17 terbaca jelas.
  - PMK 101/PMK.010/2016: hlm. 1–4, skala 3.
  - PMK 168/2023: hlm. 11–12, skala 2,5.
  - PP 44/2015: hlm. 12, 13, 45. PP 45/2015: hlm. 12–13, 20–21, 24. PP 46/2015: hlm. 11–12, 22. Skala 2,5 (hlm. tanggal berlaku: skala 1,6).
  - Perpres 75/2019: hlm. 2–5, skala 2,5. Perpres 82/2018: hlm. 22–23, skala 2 (hanya untuk dasar upah dan nilai historis).
  - Empat surat batas upah JP (2023, 2024, 2025, 2026): hlm. 1–2, skala 2,5.
  - PP 7/2025: hlm. 3–6. PP 36/2025: hlm. 2–5. Skala 2,2.
- **Pemakaian text layer:** hanya untuk *mencari nomor halaman* (pencarian kata "Pasal 17", "persen", "mulai berlaku", dan sejenisnya). Tidak ada nilai yang diambil dari text layer. Cek silang ketiga via text layer **tidak dilakukan**, karena kedua ekstraksi sudah cocok untuk semua nilai.
- **Pemeriksaan internal sebelum perbandingan:** untuk setiap kategori TER, `batas_atas` naik monoton, tarif naik monoton, `batas_bawah` = `batas_atas` baris sebelumnya, dan hanya baris terakhir yang `batas_atas`-nya kosong. Semua lolos.
- **Batasan:** halaman TER dibaca utuh per halaman (gambar ditampilkan sekitar 1303 x 2000 px) tanpa crop tambahan. Semua digit terbaca jelas. Karena perbandingan tidak menemukan selisih nilai, tidak ada halaman TER yang perlu dibuka ulang dengan zoom.
- **Aturan perbandingan:** nilai dibandingkan secara numerik dengan Decimal. Selisih yang hanya berupa format angka (mis. `0.0` vs `0`, `2.0` vs `2`, `0.12` vs `0.120`) dicatat sebagai *normalisasi*, bukan selisih nilai.

## 2. Ringkasan per tabel

| Tabel | Baris e1 | Baris e2 | Baris dipasangkan | Sel dibandingkan | Selisih nilai | Selisih normalisasi/format | Verdict |
|---|---|---|---|---|---|---|---|
| ter_bulanan | 125 (A 44, B 40, C 41) | 125 (A 44, B 40, C 41) | 125 | 375 (+125 rujukan halaman) | 0 | 3 (`0.0` vs `0`) | **cocok 100%** |
| ter_harian | 3 | 2 | 2 | 6 | 0 | 1 (`0.0` vs `0`) + 1 baris tambahan di e1 | **cocok 100%** (nilai) |
| tarif_pasal17 (rezim UU HPP) | 5 | 5 | 5 | 15 | 0 | 0 | **cocok 100%** |
| ptkp (ptkp_setahun) | 12 | 12 | 12 | 12 | 0 | 0 | **cocok 100%** |
| kategori TER (ptkp.kategori_ter vs kategori_ter.csv) | 12 | 8 | 8 | 8 | 0 | 4 baris K/I hanya di e1 (sengaja "tidak dipetakan") | **cocok 100%** |
| biaya_jabatan (baris PMK 168/2023) | 2 (+2 baris PER-16) | 2 | 2 | 6 | 0 | 0 | **cocok 100%** |
| bpjs | 20 | 19 | 18 | 90 | 0 untuk tarif dan batas upah | 22 normalisasi + 1 tanggal inferensi + 17 format angka; 3 baris hanya di salah satu sisi | **ada koreksi (normalisasi saja, bukan nilai)** |

Total sel yang dibandingkan: 375 + 6 + 15 + 12 + 8 + 6 + 90 = **512 sel**, ditambah 125 rujukan halaman PDF pada TER bulanan (semuanya cocok).
Hasil: **0 selisih nilai numerik** (tarif, batas, PTKP, plafon, batas upah) di seluruh tabel.

## 3. Rincian per tabel

### 3.1 ter_bulanan (PP 58/2023 Lampiran A/B/C, PDF hlm. 11–24)
- 375 sel (batas_bawah, batas_atas, tarif_desimal) cocok 100%.
- Rujukan halaman PDF per baris juga cocok untuk 125 baris. A: hlm. 11–15, B: hlm. 16–20, C: hlm. 20–24.
- Normalisasi: tarif 0% ditulis `0.0` di e1 dan `0` di e2 (3 baris, satu per kategori). Nilainya sama.
- Kolom `status_ptkp` di e1 (A = TK/0; TK/1; K/0, B = TK/2; TK/3; K/1; K/2, C = K/3) konsisten dengan Pasal 2 ayat (4) yang saya baca di gambar hlm. 4.

### 3.2 ter_harian (PP 58/2023 Lampiran D, PDF hlm. 25)
- Gambar hlm. 25 hanya memuat 2 baris: "sampai dengan Rp450.000,00" → 0%, dan "di atas Rp450.000,00 sampai dengan Rp2.500.000,00" → 0,5%. Kedua baris cocok di e1 dan e2. Untuk Lampiran D, kedua ekstraksi menulis `batas_atas` baris terakhir = 2.500.000 karena tabelnya memang berbatas atas.
- Baris ke-3 di e1 (di atas 2.500.000, nilai kosong, berlabel "TIDAK ADA di Lampiran PP 58/2023", merujuk PMK 168/2023) **tidak ada di gambar Lampiran D**. Baris ini bukan kesalahan nilai karena labelnya jujur. Namun baris ini adalah aturan turunan dari PMK 168/2023, bukan isi tabel. Saran: pertahankan bila memang dibutuhkan mesin inferensi, tetapi jangan dihitung sebagai baris Lampiran D.
- Normalisasi: `0.0` vs `0` (1 sel).

### 3.3 tarif_pasal17 (UU HPP, PDF hlm. 56)
- Gambar: s.d. Rp60.000.000 → 5%; >60 jt s.d. 250 jt → 15%; >250 jt s.d. 500 jt → 25%; >500 jt s.d. Rp5.000.000.000 → 30%; >5 M → 35%.
- 15 sel cocok 100%. Baris rezim "UU 36/2008" di e1 di luar cakupan dan tidak dibandingkan.

### 3.4 ptkp (PMK 101/PMK.010/2016 Pasal 1, PDF hlm. 2–3)
- Gambar: a. Rp54.000.000 (diri, hlm. 2); b. Rp4.500.000 (kawin, hlm. 3); c. Rp54.000.000 (istri, penghasilan digabung, hlm. 3); d. Rp4.500.000 per tanggungan, paling banyak 3 orang (hlm. 3).
- 12 nilai ptkp_setahun (TK/0..3 = 54,0/58,5/63,0/67,5 jt; K/0..3 = 58,5/63,0/67,5/72,0 jt; K/I/0..3 = 112,5/117,0/121,5/126,0 jt) cocok 100%.

### 3.5 Kategori TER (PP 58/2023 Pasal 2 ayat (4), PDF hlm. 4)
- 8 status cocok 100%: A = TK/0, TK/1, K/0; B = TK/2, TK/3, K/1, K/2; C = K/3.
- K/I/0..3: gambar Pasal 2 ayat (4) tidak menyebut status K/I. E1 menulis "tidak dipetakan (lihat catatan)". E2 sengaja tidak memasukkan K/I ke `kategori_ter.csv`. Kedua penanganan konsisten; ini perbedaan bentuk, bukan nilai.

### 3.6 biaya_jabatan (PMK 168/2023 Pasal 10 ayat (2) dan Pasal 11 ayat (2), PDF hlm. 12)
- Gambar hlm. 12: biaya jabatan 5%, paling banyak Rp6.000.000 setahun atau Rp500.000 sebulan; biaya pensiun 5%, paling banyak Rp2.400.000 setahun atau Rp200.000 sebulan.
- 6 sel cocok 100%. E1 juga punya 2 baris PER-16/PJ/2016 (tahun 2023) dengan nilai identik. PER-16 tidak termasuk sumber ekstraksi kedua dan tidak saya verifikasi dari gambar.

### 3.7 bpjs
Dipasangkan 18 baris: JKK 5 kelas, JKK keringanan 5 kelas, JKM, JHT, JP 2022/2023/2024/2025/2026, JKN 12 jt. Kolom yang dibandingkan: tarif_pemberi_kerja_persen, tarif_pekerja_persen, batas_upah_bulanan, berlaku_mulai, berlaku_sampai (90 sel).

**Nilai yang terverifikasi di gambar dan cocok di kedua ekstraksi:**
- JKK 0,24 / 0,54 / 0,89 / 1,27 / 1,74 % (PP 44/2015, hlm. 12).
- JKM 0,30 % (PP 44/2015 Pasal 18 ayat (1), hlm. 13).
- JHT 3,7 % pemberi kerja + 2 % pekerja (PP 46/2015 Pasal 16 ayat (1), hlm. 11).
- JP 2 % + 1 % (PP 45/2015 Pasal 28 ayat (3), hlm. 20).
- Batas upah JP: 9.559.600 mulai Maret 2023 (B/77/022023); 10.042.300 mulai iuran Maret 2024 (B/1387/022024); 10.547.400 mulai 1 Maret 2025 (B/726/022025); 11.086.300 mulai Maret 2026 (B/1226/022026).
- JKN 4 % + 1 %, batas Rp12.000.000, berlaku 1 Januari 2020 untuk pegawai swasta (Perpres 75/2019, hlm. 2, 3, 5).
- Keringanan JKK 50 %: 0,120 / 0,270 / 0,445 / 0,635 / 0,870 % (PP 7/2025 Pasal 4 ayat (1), hlm. 4). Periode iuran Februari 2025 s.d. Juli 2025 (Pasal 10, hlm. 6), diperpanjang s.d. iuran Januari 2026 (PP 36/2025 Pasal 10A, hlm. 4). Syarat: ≥50 pekerja aktif (Pasal 3 ayat (3)); enam industri (Pasal 3 ayat (4)); lunas iuran JKK s.d. Januari 2025 (Pasal 6 ayat (2)).

**Selisih dan adjudikasinya (semuanya bukan selisih nilai):**

| # | Baris | Kolom | e1 | e2 | Adjudikasi |
|---|---|---|---|---|---|
| 1–12 | JKK x5, JKK keringanan x5, JKM, JHT | batas_upah_bulanan | `tidak ada` | (kosong) | Normalisasi. Tidak ada plafon upah di PP 44/2015 atau PP 46/2015 (gambar hlm. 12–13; hlm. 11–12). Menurut konvensi tugas, sel harus kosong → **e1 perlu dinormalisasi**. Nilainya sendiri benar. |
| 13–22 | JKK keringanan x5 | berlaku_mulai / berlaku_sampai | `2025-02 (iuran Feb 2025)` / `2026-01 (iuran Jan 2026)` | `2025-02-01` / `2026-01-31` | Normalisasi. Periode sama (iuran Feb 2025 s.d. iuran Jan 2026; PP 7/2025 hlm. 6 dan PP 36/2025 hlm. 4). E1 bukan ISO YYYY-MM-DD → **e1 perlu dinormalisasi**. |
| 23 | JP batas 9.077.600 | berlaku_mulai | `2022-03-01` | (kosong) | Surat B/77/022023 (hlm. 1) hanya menyebut 9.077.600 sebagai "Batas Upah Tertinggi Tahun 2022", tanpa tanggal mulai. Tanggal 2022-03-01 di e1 adalah **inferensi** (pola bulan Maret), bukan isi sumber yang tersedia. Nilai 9.077.600 dan `berlaku_sampai` 2023-02-28 cocok. Saran: tandai tanggal itu sebagai turunan, atau kosongkan. |
| — | 17 sel | tarif | `2.0`, `1.0`, `4.0`, `0.3`, `0.12`, `0.27`, `0.87` | `2`, `1`, `4`, `0.30`, `0.120`, `0.270`, `0.870` | Hanya format angka; nilainya identik. |

**Baris yang hanya ada di salah satu ekstraksi:**
- JKN batas Rp8.000.000 (2018-09-18 s.d. 2019-12-31), hanya di e1. Saya cek gambar Perpres 82/2018 hlm. 22: Pasal 31 berisi 4 % + 1 % dan Pasal 32 ayat (1) berisi Rp8.000.000. **e1 benar.** E2 sengaja tidak memasukkannya karena historis; tanggal mulai 2018-09-18 tidak saya verifikasi.
- JKP (iuran 0 / 0, batas 5.000.000), hanya di e1. Di luar daftar sumber ekstraksi kedua (PP 37/2021, PP 6/2025) sehingga **tidak diverifikasi**.
- JP batas Rp7.000.000 tahun 2015, hanya di e2 (PP 45/2015 Pasal 29 ayat (2), hlm. 21). Ini nilai dasar historis dan bukan selisih terhadap e1.

**Catatan rujukan (bukan nilai):** e1 mengutip tarif JKK sebagai "PP 44/2015 Pasal 16 ayat (2)". Di gambar hlm. 12, daftar huruf a–e (0,24 % … 1,74 %) berada *sebelum* "(2) Besarnya Iuran JKK bagi setiap perusahaan ditetapkan oleh BPJS…". Artinya tarif ada di **Pasal 16 ayat (1)**; ayat (2) mengatur penetapan per perusahaan berdasarkan Lampiran I. Saran: perbaiki rujukan pasal di kolom `sumber` e1.

## 4. Perbedaan normalisasi (bukan perbedaan nilai)

1. Penulisan tarif 0: `0.0` (e1) vs `0` (e2), di ter_bulanan (3) dan ter_harian (1).
2. Format angka persen BPJS: trailing `.0` dan jumlah digit desimal (17 sel).
3. Plafon tidak ada: `tidak ada` (e1) vs kosong (e2), 12 sel di bpjs.
4. Tanggal non-ISO pada baris keringanan JKK di e1 (10 sel).
5. Struktur: e1 menyimpan kategori TER sebagai kolom di `ptkp.csv` dan menambahkan K/I sebagai "tidak dipetakan"; e2 memakai file `kategori_ter.csv` terpisah tanpa K/I.
6. Struktur: e1 menambahkan baris sentinel di ter_harian (di atas 2,5 jt/hari) dan baris PER-16 di biaya_jabatan; e2 hanya memuat isi sumber yang ditugaskan.

## 5. Kesimpulan

- **Tidak ada koreksi nilai** yang diperlukan pada ekstraksi pertama. Semua 512 sel yang dibandingkan cocok secara numerik; 125 rujukan halaman TER juga cocok.
- **Koreksi normalisasi yang disarankan untuk e1 (`tables/bpjs.csv`):**
  (a) ganti `tidak ada` dengan sel kosong di batas_upah_bulanan (12 sel);
  (b) ubah tanggal keringanan JKK ke ISO (`2025-02-01`, `2026-01-31`);
  (c) tandai `berlaku_mulai` 2022-03-01 untuk batas JP 9.077.600 sebagai inferensi;
  (d) perbaiki rujukan "Pasal 16 ayat (2)" menjadi "Pasal 16 ayat (1)" untuk tarif JKK.
- Verdict akhir: ter_bulanan **cocok 100%**; ter_harian **cocok 100%** (nilai; baris sentinel e1 dicatat); tarif_pasal17 **cocok 100%**; ptkp **cocok 100%**; kategori TER **cocok 100%**; biaya_jabatan **cocok 100%**; bpjs **ada koreksi** (normalisasi a–d saja, bukan nilai).
