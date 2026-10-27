# GT5: contoh hitung kebijakan perusahaan

Sumber *ground truth* kelima: nilai yang ditentukan oleh kebijakan perusahaan (PKB), dihitung manual langkah demi langkah dan, bila PPh 21 terlibat, dihitung dari tabel regulasi di `dataset/01_regulasi/tables/`. Dasar klausul: `dataset/10_kebijakan_perusahaan/klausul/`. Status: draf 2026-10-27, menunggu tinjauan pakar (`review/company_policies/gt5.review.md`).

## Isi

| Berkas | Contoh | Tahun pajak |
|---|---|---|
| PKB_WIKA_2025_2026.json | 5 | 2025 |
| PKB_Century_Textile_2024_2026.json | 4 | 2025, 2026 |
| PKB_AVCO_2024_2026.json | 4 | 2025 |
| PKB_Taekwang_2024_2026.json | 4 | 2025 |
| PKB_Sansan_2021_2024.json | 4 | 2024 |

Koja (data pengembangan) tidak punya contoh GT5.

## Struktur per contoh

`id`, `judul`, `menguji` (apa yang diuji), `tahun_pajak`, `klausul` (id di tabel klausul), `masukan`, `asumsi`, `langkah` (setiap langkah: `uraian`, `ekspresi` berisi angka literal, `hasil`, `sumber` berupa id klausul atau pasal dan halaman PDF regulasi; langkah TER juga memuat `ter` = kategori, bruto, tarif), `nilai_harapan` (nilai acuan yang dibandingkan dengan keluaran sistem), `nilai_harapan_keterangan`, `pph21_masuk`, `ambiguitas`.

## Apa yang diuji

| Id | Inti uji |
|---|---|
| GT5-WIKA-01 | THR prorata masa kerja/12 x THP; PPh ditanggung perusahaan (net) |
| GT5-WIKA-02 | Jasa Produksi yang PPh-nya ditanggung pegawai di tengah PPh gaji yang ditanggung perusahaan; alokasi inkremental vs proporsional |
| GT5-WIKA-03 | Ekstra uang cuti 125% (Lampiran 1) pada bulan tanggal masuk; batas upah JP lama untuk iuran Februari |
| GT5-WIKA-04 | Pegawai berhenti Oktober: uang pisah 3 x FP, Masa Pajak Terakhir, lebih potong pada PPh yang ditanggung |
| GT5-WIKA-05 | Kontrafaktual konflik C4: nilai DTP yang ditahan Ps 22 ayat 3 bila WIKA eligible |
| GT5-CENTEX-01 | Upah lembur (B..G)/173 dengan pengali Lampiran 1, jam pecahan lembur terjadwal |
| GT5-CENTEX-02 | THR 120% tanpa prorata; C6 (JKK 0,89% vs 0,445%) menggeser lapisan TER B dari 4% ke 5%; DTP wajib tunai walau PPh ditanggung (C4) |
| GT5-CENTEX-03 | Bonus pita masa kerja per 20 Desember, dibayar Januari 2026; JKK diskon Januari 2026; DTP 2026 |
| GT5-CENTEX-04 | Potongan Bulanan II (faktor 1,125) dan penggantian sisa cuti |
| GT5-AVCO-01 | Lembur upah/173 pola 5-2 dan PPh bulan berjalan |
| GT5-AVCO-02 | THR 2 x upah pokok prorata 7/12 dengan skala upah 2024 (sebelum 1 April 2025) |
| GT5-AVCO-03 | Gross-up tunjangan radiasi "net" dalam TER: lompatan lapisan membuat PPh tambahan 223.331 atas tunjangan bersih 950.000 |
| GT5-AVCO-04 | Potongan mangkir upah pokok/173 x jam reguler (8 vs 7 jam) |
| GT5-TKG-01 | THR + tambahan masa kerja 20%, THR prorata; DTP pada metode *gross* (PPh tidak dipotong) dan pembanding bila Ps 46 dijalankan apa adanya |
| GT5-TKG-02 | Lembur 1/173 x (GP + TT); jam lembur ke-4 tanpa pengali di PKB (C10) |
| GT5-TKG-03 | Upah prorata pegawai baru (hari kalender vs hari kerja); syarat DTP bulan pertama |
| GT5-TKG-04 | Gugurnya tunjangan kehadiran dan transport |
| GT5-SANSAN-01 | THR prorata; masa kerja tepat 1 bulan (C10) |
| GT5-SANSAN-02 | Dua pembacaan batas premi hadir (740.000 vs 925.000) |
| GT5-SANSAN-03 | C8: iuran JP tanpa batas upah vs batas E01/E05; dampak ke PPh Desember (selisih 18.750) |
| GT5-SANSAN-04 | Uang pisah UMK x 1,6; angka ilustrasi PKB tidak cocok dengan rumus (selisih 5.001) |

## Asumsi umum

- Nominal upah tidak ada di PKB (kecuali AVCO yang punya skala upah); nilai dipilih untuk ilustrasi dan dicatat di `asumsi` setiap contoh.
- Bruto bulanan = penghasilan tunai + premi JKK, JKM, JKN yang dibayar pemberi kerja (PMK 168/2023 Ps 5 ayat (3) huruf d-e, PDF hlm. 9). Iuran JHT dan JP pegawai hanya mengurangi neto di Masa Pajak Terakhir.
- TER: lapisan "di atas batas bawah s.d. batas atas" (PP 58/2023 Lampiran). PPh hasil TER dibulatkan ke bawah ke rupiah (pembulatan tidak diatur). PKP dibulatkan ke bawah ribuan.
- PPh ditanggung perusahaan dihitung dengan metode net (tidak di-*gross-up*), kecuali komponen yang tegas "net" (AVCO tunjangan radiasi).
- DTP hanya untuk sektor yang eligible (tekstil, alas kaki; tables/klu_dtp.csv). Pada metode *gross*, DTP berarti PPh tidak dipotong; pada metode ditanggung, nilai DTP dibayar tunai di atas upah (PMK 10/2025 dan PMK 105/2025 Ps 5 ayat (1)).
- Keringanan JKK 50% (PP 7/2025, PP 36/2025) diterapkan pada Century dan Taekwang dengan anggapan syaratnya terpenuhi.
- Pesangon/uang pisah tidak dihitung PPh-nya (PP 68/2009 tidak ada di dataset).

## Ambiguitas utama

1. Alokasi PPh satu masa antara komponen yang PPh-nya ditanggung perusahaan dan yang ditanggung pegawai (WIKA Ps 22 ayat 2).
2. Arti "net" dan metode *gross-up* dalam rezim TER (AVCO Ps 23 ayat 8).
3. Lebih potong di Masa Pajak Terakhir saat PPh ditanggung perusahaan: milik pegawai atau perusahaan.
4. Century: THR tanpa rumus prorata, rujukan kesepakatan tahun 2000 tidak tersedia, alfa pada bonus tidak didefinisikan.
5. Pembagi prorata upah harian (Taekwang Ps 37, Sansan Ps 29) dan nilai harian tunjangan kehadiran.
6. Batas biaya jabatan untuk bagian tahun (10 x 500.000 vs 6.000.000).
7. Premi hadir Sansan dapat dibaca dua cara.

## Cek aritmetika

`check_gt5.py` mengevaluasi ulang setiap `ekspresi` dengan aritmetika Decimal, mencari ulang setiap tarif TER dari `tables/ter_bulanan.csv`, dan mencocokkan `nilai_harapan` dengan hasil langkah.

```
python dataset/11_acuan/gt5_contoh_kebijakan/check_gt5.py . dataset/11_acuan/gt5_contoh_kebijakan
21 contoh, 227 langkah dicek, 0 selisih
```
