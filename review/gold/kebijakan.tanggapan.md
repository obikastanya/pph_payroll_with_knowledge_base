# Tanggapan atas pembacaan kedua emas kebijakan

Tinjauan: [kebijakan.review.md](kebijakan.review.md), pengodean buta SP01–SP14 [kebijakan.koding.csv](kebijakan.koding.csv), perbandingan [kebijakan.banding.csv](kebijakan.banding.csv), pemeriksaan PKB [pkb.cek.csv](pkb.cek.csv). Ditanggapi 2026-10-28.

## Kebijakan sintetis

| Temuan | Putusan | Perubahan |
|---|---|---|
| SP08 `DEDUCTIONS` menghilangkan pengurang zakat → C3 palsu bila ada zakat lewat pemberi kerja | **Diterima** | `+ annual_zakat_deduction` |
| SP04 `BENEFITS_NOT_INCOME` menolkan semua natura teratur, padahal Pasal 27 hanya apartemen, makan siang, pakaian kerja | **Diterima.** Aturan perusahaan tidak dapat merujuk nilai yang akan dihasilkan aturan wajib, jadi representasi emas E02 diperhalus | E02 memisahkan fakta `benefit_housing_taxable` (aturan `REG.NATURA.HOUSING`); SP04 kini hanya menolkan fakta itu (C1). Temuan RQ1: granularitas fakta menentukan apakah konflik kebijakan dapat dinyatakan setepat klausulnya |
| Kode C6 pada aturan `jkk_rate` tetap (6 dari 7 beda kode) | Emas dipertahankan: kode adalah anotasi yang dipakai bila aturan perusahaan kalah dengan nilai berbeda | — |
| SP14 C10 pada aturan THR yang tidak pernah kalah | Dipertahankan sebagai anotasi; tidak menghasilkan konflik | — |

## PKB (pemeriksaan tidak buta, 15 masalah)

| No. | Masalah | Putusan |
|---|---|---|
| 1 | WIKA 22(2) PPh Jasa Produksi/IHL ditanggung pegawai tidak diformalkan | **Batas representasi (RQ1).** Aturan wajib *gross-up* penanggungan penuh tidak dapat dikalahkan sebagian oleh aturan perusahaan; dicatat di daftar batas representasi |
| 2 | WIKA `BPJS_WAGE` memicu C8 juga saat dasar perusahaan lebih luas | **Diperbaiki:** aturan aktif hanya bila dasar perusahaan lebih sempit dari dasar wajib |
| 3 | WIKA uang pisah hanya untuk pengunduran diri | Diterima sebagai keterbatasan; uang pisah PPh final (PP 68/2009), tidak memengaruhi $F_\mathit{nilai}$; tidak diperbaiki sekarang |
| 4 | WIKA 26(4) makan sesudah lembur ≥ 4 jam tidak tercatat di catatan "tidak diformalkan" | Diterima; dicatat |
| 5 | CENTEX `BPJS_WAGE` jeda dua bulan | Diterima sebagai keterbatasan (fungsi `value_in` dibatasi bulan pertama kerja tahun berjalan); dicatat |
| 6 | CENTEX berlaku 27 Maret 2024, emas mulai 2024-03-01 | Dipertahankan: masa berlaku dicatat per bulan; penggajian Maret dibayar sesudah 27 Maret |
| 7–8 | Komponen variabel (CENTEX, Taekwang, SP01) masuk `other_regular_income` dan ikut uji DTP Rp10 jt | **Batas representasi:** kosakata tidak membedakan penghasilan teratur tetap dan teratur variabel; dicatat (RQ1), dampak hanya pada uji kelayakan DTP |
| 9 | Taekwang potongan pulang awal per hari | Dicatat sebagai klausul sebagian |
| 10 | AVCO kacamata: batas bingkai+lensa dan lensa saja dijumlah | **Diperbaiki:** alternatif |
| 11 | AVCO santunan kematian tanggungan | Dicatat |
| 12 | AVCO potongan mangkir hari ke-6 pola 6-1 (5 jam) | **Diperbaiki:** masukan `hr('days_absent_unpaid_sixth_day')` × 5 jam |
| 13–14 | SANSAN tunjangan jabatan saat ditahan dan saat sakit lama | Dicatat; perbaikan memerlukan pemisahan faktor bayar per komponen |
| 15 | SANSAN berlaku 23 September 2021, emas 2021-09-01 | Dipertahankan (sama dengan no. 6) |

## Kekhawatiran prosedur

- Pembaca membuka daftar berkas `review/` sebelum bagian A selesai (hanya nama berkas); dicatat.
- **Konteks LLM tidak memuat aturan yang diubah kebijakan** (JKK, JP, JHT ditulis sebagai singkatan): **diperbaiki** di `system/pph21kbs/pipeline/context.py` (pencocokan token id rekaman dengan kata di dokumen; rekaman yang berakhir lebih dari setahun sebelum tanggal dokumen tidak ditampilkan). Sesudah perbaikan SP01/SP05/SP11 memuat `REG.BPJS.JKK_RATE`, `JP_WAGE`, `JP_EMPLOYEE`, `JHT_EMPLOYEE`.
- α per klausul dan arti kolom konflik `jkk_rate`: α kode konflik 0,73 (κ 0,73) dihitung pada unsur yang ada di kedua pengodean; kesepakatan nilai 100%.
