# Klausul kebijakan perusahaan (lapisan perusahaan)

Ekstraksi klausul PKB yang memengaruhi upah atau PPh 21. Satu berkas CSV per dokumen di `../dokumen/`. Disusun dan ditinjau 2026-10-27 (lembar tinjauan: `review/company_policies/klausul.review.md`).

| Berkas | Perusahaan | Masa berlaku | Bagian | Klausul | Dapat diformalkan (ya / sebagian / tidak) |
|---|---|---|---|---|---|
| PKB_WIKA_2025_2026.csv | PT Wijaya Karya (konstruksi, BUMN) | 2025-03-01 s.d. 2026-12-31 | uji | 43 | 30 / 7 / 6 |
| PKB_Century_Textile_2024_2026.csv | PT Century Textile Industry (tekstil) | 2024-03-27 s.d. 2026-03-26 | uji | 34 | 26 / 7 / 1 |
| PKB_AVCO_2024_2026.csv | PT Airfast Aviation Facilities (jasa penerbangan) | 2024-04-01 s.d. 2026-03-31 | uji | 44 | 37 / 6 / 1 |
| PKB_Taekwang_2024_2026.csv | PT TKG Taekwang Indonesia (alas kaki) | 2024-03 s.d. 2026-03-28 | uji | 34 | 27 / 5 / 2 |
| PKB_Sansan_2021_2024.csv | PT Sansan Saudaratex Jaya (garmen/tekstil) | 2021-09-23 s.d. 2024-09-23 | uji | 24 | 19 / 5 / 0 |
| PKB_TPK_Koja_2012_2014.csv | KSO Terminal Petikemas Koja (pelabuhan) | 2012-12-28 s.d. 2014-12-28 | pengembangan | 22 | 16 / 5 / 1 |

## Kolom

| Kolom | Isi |
|---|---|
| `id` | `<DOK>-<pasal>-<ayat>`; prefiks WIKA, CENTEX, AVCO, TKG, SANSAN, KOJA. `P` = bagian Penjelasan, `L` = Lampiran. Century dan Sansan hanya punya satu LAMPIRAN dengan butir bernomor, jadi `CENTEX-L2` = Lampiran angka 2 (kolom `pasal` = `Lampiran`, `ayat` = `angka n`); WIKA (Lampiran 1-2) dan AVCO (Lampiran I-III, X) punya lampiran terpisah |
| `pasal`, `ayat` | nomor dalam dokumen; `-` bila pasal tanpa ayat |
| `kutipan` | kutipan verbatim pendek. Setiap kutipan dicek otomatis terhadap teks hasil ekstraksi (spasi dinormalkan); 201 dari 201 lolos. Ejaan asli dipertahankan, termasuk salah ketik (mis. "peserat", "melunası") |
| `topik` | komponen_upah, tunjangan_tetap, tunjangan_tidak_tetap, lembur, THR, bonus, prorata, perlakuan_pajak, BPJS, potongan, natura, lainnya |
| `nilai_atau_rumus` | angka atau rumus yang dinyatakan dokumen |
| `dapat_diformalkan` | `ya` / `sebagian` / `tidak` + alasan |
| `relevansi_pph21` | pengaruh ke bruto, pengurang, atau siapa menanggung pajak; rujukan pasal dan halaman PDF regulasi di `dataset/01_regulasi/` |
| `potensi_konflik` | kode C1-C10 (taksonomi Bagian 2) + status (aktif/laten/terpicu) + regulasi pembanding, atau `tidak` (dengan alasan bila klausul tampak berkonflik) |
| `peristiwa_pemicu` | id peristiwa E01-E12 (`dataset/09_korpus_peristiwa/peristiwa.csv`) yang memicu atau mengaktifkan konflik; `-` bila tidak ada konflik |
| `lokasi` | halaman PDF (penomoran berkas, bukan nomor cetak; di WIKA nomor cetak = PDF + 1) atau pasal/butir pada halaman HTML WageIndicator |

## Temuan konflik

| Id | Kode | Status | Regulasi pembanding | Peristiwa |
|---|---|---|---|---|
| WIKA-4-36 (juga WIKA-32-4, WIKA-89-2) | C8 (dasar upah iuran dipersempit); C10 untuk dasar pesangon | laten | PP 44/2015 Ps 19 hlm. 13; PP 46/2015 Ps 17 hlm. 11; PP 45/2015 Ps 29 ayat (1) hlm. 21; UU 13/2003 Ps 157 jo. UU 6/2023 | - |
| WIKA-22-3, WIKA-P22-3 | C4 | laten | PMK 10/2025 Ps 5 ayat (1) hlm. 6; PMK 105/2025 Ps 5 ayat (1) hlm. 6 | - (E06, E10, E11 tidak mencakup konstruksi) |
| WIKA-31-4 | C10 | laten | Permenaker 6/2016 Ps 2 ayat (1), Ps 3 ayat (1) | - |
| WIKA-31-8 | C10 | laten | Permenaker 6/2016 Ps 7 ayat (1); PP 35/2021 Ps 36 | - |
| CENTEX-33-3a | C6 | terpicu perubahan | PP 7/2025 Ps 4 ayat (1) huruf c hlm. 4; PP 36/2025 Ps 10A hlm. 4 | E07, E09 |
| CENTEX-33-4 | C6 | laten | PP 44/2015 Ps 9 ayat (3) hlm. 7; PP 46/2015 Ps 10 ayat (3) hlm. 7; PP 45/2015 Ps 12 hlm. 9 | - |
| TKG-53-3 | C10 | laten | Permenaker 6/2016 Ps 2 ayat (1), Ps 3 ayat (1) | - |
| TKG-76 | C10 | laten | PP 35/2021 Ps 40 ayat (2) | - |
| SANSAN-34-2 | C10 | laten | UU 13/2003 Ps 93 ayat (3) (dirujuk PKB sendiri) | - |
| SANSAN-41-2 | C10 | laten | Permenaker 6/2016 Ps 2 ayat (1), Ps 3 ayat (1) | - |
| SANSAN-92-2 | C10 | laten | UU 13/2003 Ps 157 ayat (1) jo. UU 6/2023; PP 35/2021 Ps 40 | - |

Satu-satunya konflik dengan aturan PPh 21/BPJS yang dipicu peristiwa uji adalah CENTEX-33-3a. WIKA menahan insentif pajak secara eksplisit tetapi sektornya tidak eligible. Regulasi ketenagakerjaan (Permenaker 6/2016, PP 35/2021, PP 36/2021, UU 13/2003 dan perubahannya) tidak disimpan di `dataset/01_regulasi/`; rujukannya tanpa halaman PDF.

Klausul yang tampak berkonflik tetapi diputuskan `tidak`:

- CENTEX-28 (PPh ditanggung) dan TKG-46 (PPh dipotong): metode adalah pilihan perusahaan dan teksnya tidak menahan DTP. Kewajiban membayar DTP secara tunai (PMK 10/2025 dan PMK 105/2025 Ps 5 ayat (1)) adalah aturan tambahan yang dijalankan payroll pada masa DTP.
- AVCO-42-2, AVCO-42-4 (Savings Plan): PKB tidak menetapkan perlakuan pajak; perlakuan bergantung pada status penyelenggara (data masukan). Kecuali penyelenggara terbukti dana pensiun/badan penyelenggara THT, kontribusi pemberi kerja masuk bruto dan kontribusi pegawai bukan pengurang.
- TKG-44-3a (jam lembur ke-4): celah diisi regulasi melalui rujukan Ps 44 ayat 1, bukan pengali yang lebih rendah.
- SANSAN-52-2d (JP "2% x upah sebulan"): rumusan sama dengan PP 45/2015 Ps 28 ayat (3); batas upah berlaku lewat Ps 29.

## Putusan perlakuan pajak yang dipakai di kolom `relevansi_pph21`

| Hal | Putusan | Dasar |
|---|---|---|
| PPh ditanggung perusahaan (2024 dst.) | kenikmatan objek PPh 21, *full gross-up* | PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44; tafsir K3-K4 |
| DTP pada metode ditanggung atau *gross* | PPh DTP tidak menjadi beban perusahaan (tanpa *gross-up*); nilainya dibayar tunai dan bukan penghasilan | PMK 168/2023 Ps 7 huruf h, PDF hlm. 10; PMK 10/2025 dan PMK 105/2025 Ps 5 ayat (1)-(2), PDF hlm. 6 |
| Uang pesangon, UPMK, uang penggantian hak, uang pisah, santunan karena pegawai meninggal | PPh 21 final PP 68/2009, di luar TER dan Pasal 17 | PP 68/2009 Ps 1-2 (di luar dataset); PER-16/PJ/2016 Ps 18, PDF hlm. 15 |
| THR yang dibayar setelah hubungan kerja berakhir | penghasilan Mantan Pegawai, tarif Pasal 17 x bruto | PMK 168/2023 Ps 5 ayat (1) huruf h, Ps 12 ayat (8), Ps 16 ayat (6), PDF hlm. 8, 14, 17 |
| Potongan upah karena mangkir atau sanksi | mengurangi bruto | PMK 168/2023 Ps 8 ayat (2) huruf a, PDF hlm. 10 |
| Upah/lembur bulan M yang dibayar awal bulan M+1 | Masa Pajak M | PMK 168/2023 Ps 19 ayat (1) huruf a, PDF hlm. 20 |
| Penggantian biaya kesehatan (kacamata, gigi) | penghasilan tidak teratur; bukan natura kesehatan yang dikecualikan | PMK 66/2023 Lampiran A angka 4, PDF hlm. 22 |
| Bantuan keluarga selama pegawai ditahan | penghasilan pegawai | PMK 168/2023 Ps 5 ayat (1)-(2), PDF hlm. 8 |
| Premi JKK dengan keringanan PP 7/2025 / PP 36/2025 | premi yang dibayar (tarif keringanan) yang masuk bruto, bila perusahaan lolos syarat dan verifikasi | PP 7/2025 Ps 3-6; PMK 168/2023 Ps 5 ayat (3) huruf d; tafsir K7-K8 |

## Catatan metode

- Teks diekstrak dengan pdfplumber (PDF) dan `html.parser` (HTML, hanya isi perjanjian). Tabel bergambar (WIKA Lampiran 1-2, AVCO Lampiran I-III) dibaca dari render halaman; nilainya ada di `nilai_atau_rumus`, kutipan diambil dari judul tabel. WIKA Lampiran 1 dan AVCO Lampiran I-III dicocokkan ulang dengan render halaman saat tinjauan.
- Tinjauan memeriksa 105 dari 201 klausul terhadap teks sumber (semua klausul berlabel konflik dan sampel dari keenam dokumen), termasuk nomor pasal/ayat setiap klausul secara otomatis. Koreksi: 61 baris (penomoran lampiran Century/Sansan, label konflik, keputusan perlakuan pajak, dan keterbacaan rumus).
- Bagian PHI AVCO hanya diambil Lampiran X (uang pengganti Travel Allowance) karena satu-satunya yang mengatur pembayaran.
- Koja adalah data pengembangan; relevansi dinilai terhadap regulasi 2012-2014, tanpa label konflik.
