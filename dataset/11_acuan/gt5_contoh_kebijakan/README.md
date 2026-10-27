# GT5: contoh hitung kebijakan perusahaan

Sumber *ground truth* kelima: nilai yang ditentukan oleh kebijakan perusahaan (PKB), dihitung manual langkah demi langkah dan, bila PPh 21 terlibat, dihitung dari tabel regulasi di `dataset/01_regulasi/tables/`. Dasar klausul: `dataset/10_kebijakan_perusahaan/klausul/`. Disusun dan ditinjau 2026-10-27 (lembar tinjauan: `review/company_policies/gt5.review.md`). Aturan tafsir umum mengikuti `docs/spesifikasi/tafsir_perhitungan.md` (K1-K16); putusan khusus kebijakan perusahaan ada di bagian **Putusan tafsir** di bawah.

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

`id`, `judul`, `menguji` (apa yang diuji), `tahun_pajak`, `klausul` (id di tabel klausul), `masukan`, `asumsi`, `langkah` (setiap langkah: `uraian`, `ekspresi` berisi angka literal, `hasil`, `sumber` berupa id klausul atau pasal dan halaman PDF regulasi; langkah TER juga memuat `ter` = kategori, bruto, tarif), `nilai_harapan` (nilai acuan yang dibandingkan dengan keluaran sistem), `nilai_harapan_keterangan`, `pph21_masuk`, `ambiguitas` (pertanyaan yang muncul saat penyusunan) dan `putusan` (jawaban yang dipakai, dengan rujukan). Langkah berlabel "Pembanding" mencatat pembacaan yang ditolak atau kesalahan pelaksanaan; nilainya tidak masuk `nilai_harapan`, kecuali nilai konflik yang diberi keterangan "nilai konflik".

## Apa yang diuji

| Id | Inti uji |
|---|---|
| GT5-WIKA-01 | THR prorata masa kerja/12 x THP; PPh ditanggung perusahaan di-*gross-up* (kenikmatan) |
| GT5-WIKA-02 | Jasa Produksi yang PPh-nya ditanggung pegawai di tengah PPh gaji yang ditanggung perusahaan; metode selisih |
| GT5-WIKA-03 | Ekstra uang cuti 125% (Lampiran 1) pada bulan tanggal masuk; batas upah JP lama untuk iuran Februari; *gross-up* |
| GT5-WIKA-04 | Pegawai berhenti Oktober: uang pisah 3 x FP dengan PPh final 0%, Masa Pajak Terakhir dengan *gross-up*, lebih potong dikembalikan |
| GT5-WIKA-05 | Kontrafaktual konflik C4: nilai DTP yang ditahan Ps 22 ayat 3 bila WIKA eligible |
| GT5-CENTEX-01 | Upah lembur (B..G)/173 dengan pengali Lampiran angka 1, jam pecahan lembur terjadwal |
| GT5-CENTEX-02 | THR 120% tanpa prorata; C6 (JKK 0,89% vs 0,445%) menggeser lapisan TER B dari 4% ke 5%; DTP wajib tunai walau PPh ditanggung |
| GT5-CENTEX-03 | Bonus pita masa kerja per 20 Desember, dibayar Januari 2026; JKK diskon Januari 2026; DTP 2026 |
| GT5-CENTEX-04 | Potongan Bulanan II (faktor 1,125) dan penggantian sisa cuti |
| GT5-AVCO-01 | Lembur upah/173 pola 5-2 dan PPh bulan berjalan |
| GT5-AVCO-02 | THR 2 x upah pokok prorata 7/12 dengan skala upah 2024 (sebelum 1 April 2025) |
| GT5-AVCO-03 | Tunjangan radiasi "net": PPh tambahan ditanggung perusahaan, titik tetap 223.331 atas tunjangan bersih 950.000 |
| GT5-AVCO-04 | Potongan mangkir upah pokok/173 x jam reguler (8 vs 7 jam) |
| GT5-TKG-01 | THR + tambahan masa kerja 20%, THR prorata; DTP pada metode *gross* |
| GT5-TKG-02 | Lembur 1/173 x (GP + TT); jam lembur ke-4 diisi regulasi lewat Ps 44 ayat 1 |
| GT5-TKG-03 | Upah prorata pegawai baru dengan hari kalender; syarat DTP bulan pertama |
| GT5-TKG-04 | Gugurnya tunjangan kehadiran dan transport |
| GT5-SANSAN-01 | THR prorata; masa kerja tepat 1 bulan (C10 laten) |
| GT5-SANSAN-02 | Batas premi hadir 20% dari (upah pokok + premi) = 925.000 |
| GT5-SANSAN-03 | Iuran JP dengan batas upah E01/E05 dan PPh Desember |
| GT5-SANSAN-04 | Uang pisah UMK x 1,6; salah ketik angka ilustrasi PKB (selisih 5.000); PPh final 0% |

## Asumsi umum

- Nominal upah tidak ada di PKB (kecuali AVCO yang punya skala upah); nilai dipilih untuk ilustrasi dan dicatat di `asumsi` setiap contoh.
- Bruto bulanan = penghasilan tunai + premi JKK, JKM, JKN yang dibayar pemberi kerja (PMK 168/2023 Ps 5 ayat (3) huruf d-e, PDF hlm. 9) + PPh yang ditanggung pemberi kerja. Iuran JHT dan JP pegawai hanya mengurangi neto di Masa Pajak Terakhir.
- TER: lapisan "di atas batas bawah s.d. batas atas" (PP 58/2023 Lampiran). Pembulatan PPh TER mengikuti tafsir K1: Masa 2024 desimal dibuang (Sansan), Masa 2025 dst. ke rupiah terdekat (WIKA, Century, AVCO, Taekwang). PKP dibulatkan ke bawah ribuan (PMK 168/2023 Ps 8 ayat (4)).
- DTP hanya untuk sektor yang eligible (tekstil, alas kaki; `tables/klu_dtp.csv`) dan pegawai yang memenuhi kriteria Rp10 juta (tafsir K5).
- Keringanan JKK 50% (PP 7/2025, PP 36/2025) diterapkan pada Century dan Taekwang dengan anggapan syaratnya terpenuhi; premi yang masuk bruto adalah premi yang dibayar (tafsir K7-K8).

## Putusan tafsir

| No | Pertanyaan | Putusan | Dasar | Contoh yang berubah |
|---|---|---|---|---|
| 1 | PPh 21 ditanggung perusahaan: net atau *gross-up*? | Kenikmatan objek PPh 21, ditambahkan ke bruto dengan *full gross-up*: T = titik tetap terkecil dari T = R(TER(X + T) x (X + T)), iterasi dari 0. Metode net hanya untuk Masa Januari-Juni 2023 | PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44 ("merupakan penggantian dalam bentuk kenikmatan ... objek pemotongan"); tafsir K3-K4; PMK 66/2023 Ps 23 ayat (4) | WIKA-01 s.d. 04 |
| 2 | WIKA Ps 22 ayat 2: alokasi PPh satu masa antara gaji (ditanggung) dan Jasa Produksi/IHL (ditanggung pegawai) | Metode selisih: bagian Perusahaan = PPh *gross-up* atas penghasilan tanpa Jasa Produksi/IHL; bagian pegawai = PPh total masa itu - bagian Perusahaan. Kaidah yang sama di Masa Pajak Terakhir atas PPh setahun. Alokasi proporsional ditolak | Teks ayat 2 (Perusahaan menanggung PPh atas penerimaan selain Jasa Produksi/IHL); kaidah selisih PER-16/PJ/2016 Ps 14 ayat (3) huruf b, PDF hlm. 13 | WIKA-02 (bagian pegawai 4.636.031) |
| 3 | AVCO Ps 23 ayat 8: tunjangan radiasi "net" dalam TER | PPh tambahan akibat tunjangan ditanggung Perusahaan (metode selisih) dan merupakan kenikmatan, sehingga tunjangan bruto = 950.000 + T dengan T titik tetap terkecil; lompatan lapisan TER atas seluruh bruto ikut ditanggung Perusahaan. Gross-up dengan tarif marginal ditolak | Putusan 1 dan 2; tafsir K3 | AVCO-03 (nilai tetap; pembanding marginal dikeluarkan dari nilai harapan) |
| 4 | Lebih potong di Masa Pajak Terakhir saat PPh ditanggung perusahaan | PPh ditanggung bulan itu = 0 (tidak ada kenikmatan negatif); kelebihan PPh yang telah dipotong wajib dikembalikan kepada pegawai paling lambat akhir bulan berikutnya. Pengecualian hanya untuk PPh DTP | Tafsir K3 butir 2; PMK 168/2023 Ps 21 ayat (1)-(2) dan Ps 22 ayat (2), PDF hlm. 21-22 | WIKA-04 (lebih potong 4.386.803) |
| 5 | DTP pada metode ditanggung (Century) dan *gross* (Taekwang) | PPh DTP ditanggung pemerintah, sehingga tidak ada PPh yang ditanggung perusahaan untuk di-*gross-up*; nilai DTP dibayar tunai (metode ditanggung: di atas upah; metode *gross*: potongan dibayarkan kembali) dan bukan penghasilan. Tidak membayarkan DTP adalah kesalahan pelaksanaan, bukan konflik teks PKB | PMK 168/2023 Ps 7 huruf h, PDF hlm. 10; PMK 10/2025 dan PMK 105/2025 Ps 5 ayat (1)-(2), PDF hlm. 6 | CENTEX-02, TKG-01 (pembanding dikeluarkan dari nilai harapan) |
| 6 | WIKA Ps 22 ayat 3: apakah "insentif pajak" mencakup PPh 21 DTP | Ya. Penjelasan mendefinisikan insentif sebagai pengurang "beban pajak Perusahaan" dan PPh 21 pegawai adalah beban Perusahaan (ayat 2); daftar contoh pajak badan terbuka. Konflik C4 laten karena KLU konstruksi tidak eligible | PKB WIKA Penjelasan Ps 22 ayat (3), PDF hlm. 96; PMK 10/2025 Ps 5 ayat (1) | WIKA-05 |
| 7 | Uang pisah, pesangon, UPMK, UPH, santunan karena pegawai meninggal | PPh 21 final PP 68/2009 ("uang pesangon" = penghasilan dengan nama dan dalam bentuk apa pun sehubungan dengan berakhirnya masa kerja), lapisan 0% s.d. Rp50 juta; tidak masuk TER maupun Pasal 17 | PP 68/2009 Ps 1-2 (di luar dataset); PER-16/PJ/2016 Ps 18, PDF hlm. 15 | WIKA-04 dan SANSAN-04 (PPh final 0 ditambahkan) |
| 8 | Plafon biaya jabatan bagian tahun | min(5% x bruto, n x Rp500.000) | Tafsir K6; PMK 168/2023 Lampiran B, PDF hlm. 39 | tidak ada |
| 9 | Sansan Lampiran angka 2: angka ilustrasi faktor 1,6 | Ilustrasi memakai UMK Kota Cimahi 2021 tanpa sen (Rp3.241.929); tujuh baris lain cocok dengan pembulatan ke rupiah terdekat. 5.192.086 adalah salah ketik dari 5.187.086 (selisih tepat 5.000). Acuan memakai rumus dengan UMK tahun berjalan | Teks dan catatan Lampiran angka 2 | SANSAN-04 (uang pisah 5.187.086, selisih 5.000) |
| 10 | Sansan Ps 37 ayat 2a: "20% dari upah pokok dan premi hadir" | Dibaca harfiah: premi <= 20% x (upah pokok + premi), setara 25% x upah pokok | Rumusan "dari jumlah X dan Y" seperti UU 13/2003 Ps 94 | SANSAN-02 (batas 925.000) |
| 11 | Sansan Ps 52 ayat 2: JP "2% x upah sebulan" tanpa menyebut batas | Penulisan ringkas yang sama dengan PP 45/2015 Ps 28 ayat (3); batas upah Ps 29 tetap berlaku; bukan konflik | PP 45/2015 Ps 28-29, PDF hlm. 20-21 | SANSAN-03 (nilai harapan = perhitungan dengan batas) |
| 12 | Definisi yang tidak ada di PKB | AVCO "upah bulanan" = upah (Lampiran III angka 3), bagi Pratama = upah pokok; Century "satu bulan upah" = B+C+D+E+F+G; Century "upah bulan Desember" = periode 21 November-20 Desember (sebelum kenaikan 21 Desember); alfa = 0; WIKA masa kerja THR = bulan penuh sampai hari raya; AVCO prorata THR = masa kerja/12 x THR penuh | PKB masing-masing; Permenaker 6/2016 Ps 3 ayat (1) huruf b; PP 35/2021 Ps 32 | CENTEX-03 (asumsi dipertegas) |
| 13 | Pembagi prorata upah (Taekwang Ps 37) dan nilai harian tunjangan kehadiran | Hari kalender, karena periode upah tanggal 1 s.d. akhir bulan (Ps 37 ayat 4); nilai harian tunjangan kehadiran = tunjangan bulanan / hari kerja bulan itu | PKB Taekwang Ps 37 ayat 4, Ps 41 ayat 4 | TKG-03 (pembanding hari kerja dikeluarkan dari nilai harapan) |
| 14 | Potongan absen, mangkir, dan sanksi | Mengurangi bruto | PMK 168/2023 Ps 8 ayat (2) huruf a, PDF hlm. 10 | tidak ada |
| 15 | Taekwang jam lembur ke-4 | 2x upah per jam lewat rujukan Ps 44 ayat 1 ke regulasi; bukan konflik | PP 35/2021 Ps 31 (di luar dataset) | TKG-02 (pembanding literal dikeluarkan dari nilai harapan) |
| 16 | Pembulatan PPh TER | Masa 2024 desimal dibuang; Masa 2025 dst. ke rupiah terdekat | Tafsir K1 | WIKA-05 (163.348 -> 163.349), CENTEX-02 (543.882 -> 543.883; 681.199 -> 681.200), AVCO-01 (942.814 -> 942.815), AVCO-02 (2.142.693 -> 2.142.694) |

## Cek aritmetika

`check_gt5.py` mengevaluasi ulang setiap `ekspresi` dengan aritmetika Decimal, mencari ulang setiap tarif TER dari `tables/ter_bulanan.csv`, dan mencocokkan `nilai_harapan` dengan hasil langkah. Nilai *gross-up* dan Masa Pajak Terakhir juga dihitung ulang dengan program terpisah (iterasi titik tetap dan tarif Pasal 17) dan cocok.

```
python dataset/11_acuan/gt5_contoh_kebijakan/check_gt5.py . dataset/11_acuan/gt5_contoh_kebijakan
21 contoh, 229 langkah dicek, 0 selisih
```
