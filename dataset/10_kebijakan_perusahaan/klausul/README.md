# Klausul kebijakan perusahaan (lapisan perusahaan)

Ekstraksi klausul PKB yang memengaruhi upah atau PPh 21. Satu berkas CSV per dokumen di `../dokumen/`. Disusun 2026-10-27, belum ditinjau pakar (lembar tinjauan: `review/company_policies/klausul.review.md`).

| Berkas | Perusahaan | Masa berlaku | Bagian | Klausul | Dapat diformalkan (ya / sebagian / tidak) |
|---|---|---|---|---|---|
| PKB_WIKA_2025_2026.csv | PT Wijaya Karya (konstruksi, BUMN) | 2025-03-01 s.d. 2026-12-31 | uji | 43 | 28 / 9 / 6 |
| PKB_Century_Textile_2024_2026.csv | PT Century Textile Industry (tekstil) | 2024-03-27 s.d. 2026-03-26 | uji | 34 | 25 / 8 / 1 |
| PKB_AVCO_2024_2026.csv | PT Airfast Aviation Facilities (jasa penerbangan) | 2024-04-01 s.d. 2026-03-31 | uji | 44 | 34 / 9 / 1 |
| PKB_Taekwang_2024_2026.csv | PT TKG Taekwang Indonesia (alas kaki) | 2024-03 s.d. 2026-03-28 | uji | 34 | 23 / 9 / 2 |
| PKB_Sansan_2021_2024.csv | PT Sansan Saudaratex Jaya (garmen/tekstil) | 2021-09-23 s.d. 2024-09-23 | uji | 24 | 18 / 6 / 0 |
| PKB_TPK_Koja_2012_2014.csv | KSO Terminal Petikemas Koja (pelabuhan) | 2012-12-28 s.d. 2014-12-28 | pengembangan | 22 | 16 / 5 / 1 |

## Kolom

| Kolom | Isi |
|---|---|
| `id` | `<DOK>-<pasal>-<ayat>`; prefiks WIKA, CENTEX, AVCO, TKG, SANSAN, KOJA. `P` = bagian Penjelasan, `L` = Lampiran |
| `pasal`, `ayat` | nomor dalam dokumen; `-` bila pasal tanpa ayat |
| `kutipan` | kutipan verbatim pendek. Setiap kutipan dicek otomatis terhadap teks hasil ekstraksi (spasi dinormalkan); semua lolos. Ejaan asli dipertahankan, termasuk salah ketik (mis. "peserat", "melunası") |
| `topik` | komponen_upah, tunjangan_tetap, tunjangan_tidak_tetap, lembur, THR, bonus, prorata, perlakuan_pajak, BPJS, potongan, natura, lainnya |
| `nilai_atau_rumus` | angka atau rumus yang dinyatakan dokumen |
| `dapat_diformalkan` | `ya` / `sebagian` / `tidak` + alasan |
| `relevansi_pph21` | pengaruh ke bruto, pengurang, atau siapa menanggung pajak; rujukan pasal dan halaman PDF regulasi di `dataset/01_regulasi/` |
| `potensi_konflik` | kode C1-C10 (taksonomi Bagian 2) + status (aktif/laten/terpicu) + regulasi pembanding, atau `tidak` |
| `peristiwa_pemicu` | id peristiwa E01-E12 (`dataset/09_korpus_peristiwa/peristiwa.csv`) yang dapat memicu/mengaktifkan konflik; `-` bila tidak ada konflik |
| `lokasi` | halaman PDF (penomoran berkas, bukan nomor cetak; di WIKA nomor cetak = PDF + 1) atau pasal pada halaman HTML WageIndicator |

## Temuan konflik

| Id | Kode | Status | Regulasi pembanding | Peristiwa |
|---|---|---|---|---|
| WIKA-22-3, WIKA-P22-3 | C4 | laten | PMK 10/2025 Ps 5(1) hlm. 6; PMK 105/2025 Ps 5(1) hlm. 6 | E06, E11 (pola pemicu E10) |
| WIKA-4-36 | C8 (terdekat) | laten | dasar iuran BPJS = upah pokok + tunjangan tetap | - |
| WIKA-31-4, WIKA-31-8 | C10 | laten | Permenaker 6/2016 Ps 2(1), Ps 7(1) (tidak di dataset) | - |
| CENTEX-28 | C4 | laten (pelaksanaan) | PMK 10/2025 Ps 5(1); PMK 105/2025 Ps 5(1) | E06, E11 |
| CENTEX-33-3a | C6 | terpicu perubahan | PP 7/2025 Ps 4(1)c hlm. 4; PP 36/2025 Ps 10A hlm. 4 | E07, E09 |
| CENTEX-33-4 | C6 (terdekat) | laten | dasar iuran = upah berjalan | - |
| AVCO-42-2, AVCO-42-4 | C2/C3 | laten | PMK 168/2023 Ps 7 huruf c, Ps 10(1)b hlm. 10-12 | E04 |
| TKG-46 | C4 | laten (pelaksanaan) | PMK 10/2025 Ps 5(1); PMK 105/2025 Ps 5(1) | E06, E11 |
| TKG-44-3a, TKG-53-3 | C10 | laten | PP 35/2021 Ps 31; Permenaker 6/2016 (tidak di dataset) | - |
| SANSAN-52-2d | C8 | laten | PP 45/2015 Ps 28-29 hlm. 20-21; batas upah JP | E01, E05 |
| SANSAN-41-2 | C10 | laten | Permenaker 6/2016 Ps 2(1) (tidak di dataset) | - |

Hanya WIKA yang menahan insentif secara eksplisit. Pada Century (PPh ditanggung) dan Taekwang (PPh dipotong) sektornya eligible DTP dan teksnya tidak melarang penerusan DTP; konflik hanya muncul bila payroll menjalankan klausul pajak apa adanya selama masa DTP.

## Catatan metode

- Teks diekstrak dengan pdfplumber (PDF) dan `html.parser` (HTML, hanya isi perjanjian). Tabel bergambar (WIKA Lampiran 1-2, AVCO Lampiran I-III) dibaca dari render halaman; nilainya ada di `nilai_atau_rumus`, kutipan diambil dari judul tabel.
- Bagian PHI AVCO hanya diambil Lampiran X (uang pengganti Travel Allowance) karena satu-satunya yang mengatur pembayaran.
- Koja adalah data pengembangan; relevansi dinilai terhadap regulasi 2012-2014, tanpa label konflik.
- Rujukan Permenaker 6/2016 dan PP 35/2021 berasal dari pengetahuan umum dan tidak ada di `dataset/01_regulasi/`; perlu verifikasi pakar.
