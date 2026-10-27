# Tinjauan: regulasi fiktif data pengembangan FR01–FR05

Berkas yang diperiksa: [dataset/09_korpus_peristiwa/fiktif/](../../dataset/09_korpus_peristiwa/fiktif/) (`FRxx.md` teks, `FRxx.json` metadata dan contoh; ringkasan di `README.md`).
Pemeriksa: pakar *payroll* · Status: **menunggu**

Semua dokumen **fiktif** dan hanya dipakai untuk data pengembangan (menyetel *prompt* dan gerbang), tidak untuk pengujian. Yang dinilai: apakah perubahan itu **masuk akal** sebagai regulasi Indonesia pada tahunnya, apakah tanggal dan sifatnya konsisten, dan apakah contoh hitungnya benar menurut aturan nyata saat itu ditambah perubahan fiktif. Setiap FR adalah kontrafaktual terpisah terhadap aturan nyata (FR tidak saling membangun).

## FR01 — PMK FIKTIF 901/PMK.03/2019

Tata Cara Pemotongan Pajak Penghasilan Pasal 21 bagi Pegawai Tetap dengan Tarif Efektif Bulanan. Teks: [FR01.md](../../dataset/09_korpus_peristiwa/fiktif/FR01.md)

Ringkasan: Mulai Masa Pajak Januari 2020, PPh 21 pegawai tetap untuk Januari sampai November tidak lagi dihitung dengan menyetahunkan gaji, tetapi cukup dengan mengalikan penghasilan bruto sebulan dengan tarif efektif bulanan dari tabel lampiran (dua kategori menurut status PTKP). Bonus dan penghasilan tidak teratur lain cukup ditambahkan ke bruto bulan itu. Pada Desember (atau bulan terakhir bekerja) pajak setahun dihitung ulang dengan tarif Pasal 17 dan dikurangi pajak yang sudah dipotong; kelebihan dikembalikan ke pegawai.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | |
| 2 | Apakah jenis perubahan **T7** dan sifat **S6** tepat? | Sesuai taksonomi bagian 1 | |
| 3 | Apakah tanggal konsisten (ditetapkan 2019-10-14, diundangkan 2019-10-16, berlaku 2020-01-01)? | Ya | |
| 4 | Apakah Δ KB yang diharapkan tepat? | sekumpulan aturan baru (pemotongan masa Jan-Nov = TEB x bruto, pemilihan kategori, tabel TEB berversi) dan pencabutan aturan disetahunkan untuk masa Jan-Nov sejak 2020-01-01; aturan Masa Pajak Terakhir tetap | |
| 5 | Contoh **FR01-1** — Januari 2019: metode disetahunkan (aturan nyata). Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; masa 2019-01. Apakah hasilnya benar? | Sebelum: pph21 Rp112.091. Sesudah: – | |
| 6 | Contoh **FR01-2** — Januari 2020: tarif efektif bulanan fiktif. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; masa 2020-01. Apakah hasilnya benar? | Sebelum: pph21 Rp112.091. Sesudah: pph21 Rp73.178 | |
| 7 | Contoh **FR01-3** — Maret 2020: bonus Rp10.000.000. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; bonus Rp10.000.000; masa 2020-03. Apakah hasilnya benar? | Sebelum: pph21 Rp587.091. Sesudah: pph21 Rp1.039.068 | |
| 8 | Contoh **FR01-4** — Desember 2020: Masa Pajak Terakhir menurut FR01. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; bonus maret Rp10.000.000; tahun 2020. Apakah hasilnya benar? | Sebelum: –. Sesudah: pph setahun Rp1.820.100; pph jan nov Rp1.770.848; pph desember Rp49.252 | |

## FR02 — PER FIKTIF-902/PJ/2020

Perubahan atas PER-16/PJ/2016 mengenai Pembulatan dalam Penghitungan PPh Pasal 21. Teks: [FR02.md](../../dataset/09_korpus_peristiwa/fiktif/FR02.md)

Ringkasan: Mulai Masa Pajak Januari 2021 ada dua aturan pembulatan baru. Pertama, penghasilan kena pajak setahun dibulatkan ke bawah sampai ratus ribu rupiah penuh, bukan lagi sampai ribuan. Kedua, PPh 21 setiap bulan (selain bulan terakhir) dibulatkan ke bawah sampai ratusan rupiah. Tarif, PTKP, dan pengurang tidak berubah.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | |
| 2 | Apakah jenis perubahan **T9** dan sifat **S5** tepat? | Sesuai taksonomi bagian 1 | |
| 3 | Apakah tanggal konsisten (ditetapkan 2020-11-23, diundangkan –, berlaku 2021-01-01)? | Ya | |
| 4 | Apakah Δ KB yang diharapkan tepat? | dua entri registri pembulatan baru (PKP: 100.000 ke bawah; PPh masa: 100 ke bawah) berlaku sejak 2021-01-01, menggantikan pembulatan PKP ribuan | |
| 5 | Contoh **FR02-1** — Januari 2021: pembulatan PKP dan PPh bulanan. Input: pegawai Sinta, K/1; upah sebulan Rp7.500.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp98.670. Sesudah: pph21 Rp98.300 | |
| 6 | Contoh **FR02-2** — Januari 2021: PKP kecil, efek pembulatan relatif besar. Input: pegawai Rizal, TK/0; upah sebulan Rp6.350.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp80.791. Sesudah: pph21 Rp80.400 | |
| 7 | Contoh **FR02-3** — Desember 2021: Masa Pajak Terakhir. Input: pegawai Sinta, K/1; upah sebulan Rp7.500.000; tahun 2021. Apakah hasilnya benar? | Sebelum: pkp Rp23.681.000; pph setahun Rp1.184.050; pph desember Rp98.680. Sesudah: pkp Rp23.600.000; pph setahun Rp1.180.000; pph desember Rp98.700 | |

## FR03 — PMK FIKTIF 903/PMK.03/2021

Pencabutan PMK FIKTIF 455/PMK.03/2017 tentang Pengurangan Biaya Transportasi bagi Pegawai Tetap yang Bekerja Gilir Malam. Teks: [FR03.md](../../dataset/09_korpus_peristiwa/fiktif/FR03.md)

Ringkasan: Sejak 2018 (dalam dunia fiktif) pegawai tetap yang bekerja gilir malam paling sedikit 10 hari sebulan boleh mengurangkan biaya transportasi sebesar 2% dari penghasilan bruto, paling banyak Rp100.000 sebulan atau Rp1.200.000 setahun. Peraturan ini mencabut pengurang tersebut tanpa pengganti mulai Masa Pajak Januari 2022. Untuk tahun pajak 2021 pengurang masih boleh dipakai, termasuk di perhitungan Desember 2021.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | |
| 2 | Apakah jenis perubahan **T8** dan sifat **tidak ada** tepat? | Sesuai taksonomi bagian 1 | |
| 3 | Apakah tanggal konsisten (ditetapkan 2021-11-22, diundangkan 2021-11-24, berlaku 2022-01-01)? | Ya | |
| 4 | Apakah Δ KB yang diharapkan tepat? | pencabutan (remove/valid_until 2021-12-31) atas aturan pengurang gilir malam; tidak ada aturan baru | |
| 5 | Contoh **FR03-1** — Januari 2021: pengurang gilir malam masih berlaku. Input: pegawai Bagus, K/0, operator gilir malam 15 hari/bulan; upah sebulan Rp6.800.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp78.712. Sesudah: – | |
| 6 | Contoh **FR03-2** — Januari 2022: setelah pencabutan (tarif UU HPP). Input: pegawai Bagus, K/0; upah sebulan Rp6.800.000; masa 2022-01. Apakah hasilnya benar? | Sebelum: pph21 Rp78.712. Sesudah: pph21 Rp83.712 | |
| 7 | Contoh **FR03-3** — Desember 2022: Masa Pajak Terakhir. Input: pegawai Bagus, K/0; upah sebulan Rp6.800.000; tahun 2022. Apakah hasilnya benar? | Sebelum: pkp Rp18.891.000; pph setahun Rp944.550. Sesudah: pkp Rp20.091.000; pph setahun Rp1.004.550 | |

## FR04 — PMK FIKTIF 904/PMK.03/2018

Perlakuan Pajak Penghasilan Pasal 21 atas Komisi Penjualan yang Diterima Pegawai Tetap. Teks: [FR04.md](../../dataset/09_korpus_peristiwa/fiktif/FR04.md)

Ringkasan: Mulai Masa Pajak Januari 2019, komisi penjualan yang besarnya mengikuti hasil penjualan dan tidak dibayar dalam jumlah tetap setiap bulan dianggap penghasilan tidak teratur. Akibatnya komisi tidak lagi ikut disetahunkan (dikali 12) saat menghitung pajak bulanan; pajaknya dihitung sebagai selisih seperti bonus. Komisi dalam jumlah tetap setiap bulan tetap penghasilan teratur. Pajak setahun tidak berubah.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | |
| 2 | Apakah jenis perubahan **T3** dan sifat **tidak ada** tepat? | Sesuai taksonomi bagian 1 | |
| 3 | Apakah tanggal konsisten (ditetapkan 2018-09-17, diundangkan 2018-09-19, berlaku 2019-01-01)? | Ya | |
| 4 | Apakah Δ KB yang diharapkan tepat? | aturan klasifikasi baru: komisi penjualan variabel -> penghasilan tidak teratur, sejak 2019-01-01; komisi tetap -> teratur | |
| 5 | Contoh **FR04-1** — Februari 2019: bulan dengan komisi. Input: pegawai Lina, staf pemasaran, TK/0; gaji Rp6.000.000; komisi Rp4.000.000; masa 2019-02. Apakah hasilnya benar? | Sebelum: pph21 Rp347.183. Sesudah: pph21 Rp253.937 | |
| 6 | Contoh **FR04-2** — Maret 2019: bulan tanpa komisi. Input: pegawai Lina, TK/0; gaji Rp6.000.000; komisi Rp0; masa 2019-03. Apakah hasilnya benar? | Sebelum: pph21 Rp63.937. Sesudah: pph21 Rp63.937 | |
| 7 | Contoh **FR04-3** — Desember 2019: Masa Pajak Terakhir. Input: pegawai Lina, TK/0; gaji Rp6.000.000; komisi 4 x Rp4.000.000; tahun 2019. Apakah hasilnya benar? | Sebelum: pph setahun Rp1.527.250; pph jan nov Rp1.836.291; pph desember -Rp309.041. Sesudah: pph setahun Rp1.527.250; pph jan nov Rp1.463.307; pph desember Rp63.943 | |

## FR05 — PP FIKTIF 905 Tahun 2021 + PMK FIKTIF 906/PMK.03/2022

Penyesuaian Besarnya Biaya Jabatan (dua dokumen). Teks: [FR05a.md](../../dataset/09_korpus_peristiwa/fiktif/FR05a.md), [FR05b.md](../../dataset/09_korpus_peristiwa/fiktif/FR05b.md)

Ringkasan: Plafon biaya jabatan dinaikkan dari Rp6.000.000 menjadi Rp7.200.000 setahun. Perubahan ini datang dalam dua dokumen: PP fiktif (6 Desember 2021) hanya menetapkan angka tahunan dan menyerahkan batas bulanan serta tanggal berlaku ke peraturan menteri; PMK fiktif (15 Februari 2022) menetapkan batas Rp600.000 sebulan dan menyatakan berlaku sejak Masa Pajak Januari 2022 (surut). Sebelum dokumen kedua terbit, pemotong belum dapat menerapkan perubahan.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | |
| 2 | Apakah jenis perubahan **T1** dan sifat **S4, S1** tepat? | Sesuai taksonomi bagian 1 | |
| 3 | Apakah tanggal konsisten (ditetapkan 2022-02-14, diundangkan 2022-02-15, berlaku 2022-01-01)? | Ya | |
| 4 | Apakah Δ KB yang diharapkan tepat? | parameter biaya jabatan berversi baru (7.200.000/tahun; 600.000/bulan) valid_from 2022-01-01, recorded_on 2022-02-15; dokumen pertama saja seharusnya menghasilkan kandidat tertunda, bukan perubahan aktif | |
| 5 | Contoh **FR05-1** — Tahun 2022, bruto setahun di atas Rp144 juta. Input: pegawai Fajar, K/2; upah sebulan Rp8.000.000; tunjangan kinerja Rp12.000.000; tahun 2022. Apakah hasilnya benar? | Sebelum: pph bulanan Rp1.599.725; biaya jabatan Rp6.000.000; pph setahun Rp19.196.700. Sesudah: pph bulanan Rp1.584.725; biaya jabatan Rp7.200.000; pph setahun Rp19.016.700 | |
| 6 | Contoh **FR05-2** — Tahun 2022, bruto setahun di bawah Rp120 juta (tidak terdampak). Input: pegawai Wulan, TK/0; upah sebulan Rp7.000.000; tahun 2022. Apakah hasilnya benar? | Sebelum: biaya jabatan Rp4.390.680; pph setahun Rp1.345.100. Sesudah: biaya jabatan Rp4.390.680; pph setahun Rp1.345.100 | |
| 7 | Contoh **FR05-3** — Pegawai berhenti 30 Juni 2022: plafon bulanan dari dokumen kedua. Input: pegawai Dimas, TK/0; upah sebulan Rp8.000.000; tunjangan kinerja Rp6.000.000; berhenti 2022-06-30. Apakah hasilnya benar? | Sebelum: biaya jabatan Rp3.000.000; pph setahun Rp1.386.950; pph juni -Rp2.955.425. Sesudah: biaya jabatan Rp3.600.000; pph setahun Rp1.356.950; pph juni -Rp2.910.425 | |
| 8 | Contoh **FR05-4** — Antara dokumen pertama dan kedua: belum ada perubahan yang dapat diterapkan. Input: tanggal pengetahuan 2022-01-31. Apakah hasilnya benar? | Sebelum: plafon biaya jabatan dipakai Rp6.000.000. Sesudah: plafon biaya jabatan dipakai Rp6.000.000 | |

## Pertanyaan umum

1. Apakah ada dokumen yang terlalu mirip regulasi nyata sehingga bisa disangka asli bila keluar dari folder ini?

   Jawaban:

2. Apakah ada jenis perubahan lain sebelum 2023 yang sebaiknya dibuatkan contoh fiktif?

   Jawaban:

## Hasil

- [ ] Disetujui
- [ ] Disetujui dengan perubahan (tulis di atas)
- [ ] Perlu revisi

Status: menunggu
