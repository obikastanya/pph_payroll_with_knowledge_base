# Tinjauan: regulasi fiktif data pengembangan FR01–FR05

Berkas yang diperiksa: [dataset/09_korpus_peristiwa/fiktif/](../../dataset/09_korpus_peristiwa/fiktif/) (`FRxx.md` teks, `FRxx.json` metadata dan contoh; ringkasan di `README.md`).
Status: **selesai**

Semua dokumen **fiktif** dan hanya dipakai untuk data pengembangan (menyetel *prompt* dan gerbang), tidak untuk pengujian. Yang dinilai: apakah perubahan itu **masuk akal** sebagai regulasi Indonesia pada tahunnya, apakah tanggal dan sifatnya konsisten, dan apakah contoh hitungnya benar menurut aturan nyata saat itu ditambah perubahan fiktif. Setiap FR adalah kontrafaktual terpisah terhadap aturan nyata (FR tidak saling membangun).

Semua contoh dihitung ulang secara mandiri. Kolom "Penilaian Claude" berisi nilai sebelum tinjauan; nilai yang berlaku setelah koreksi ada di kolom "Setuju? / koreksi" dan sudah ditulis ke `FRxx.json`. Pemeriksaan `cek_aritmetika` setelah koreksi: 307 ekspresi, 0 selisih.

**Koreksi lintas dokumen.**
- Iuran JKK dan JKM bulan Agustus 2020–Januari 2021 mendapat keringanan 99% (PP 49/2020 Pasal 5, 9, 26; D09). Contoh lama memakai tarif penuh untuk bulan itu. FR01-4 dan FR02-3 dihitung ulang; FR02-1, FR02-2, dan FR03-1 dipindah ke Februari 2021 (angkanya tetap).
- Rujukan pembulatan PKP untuk 2019–2021 diganti dari UU 7/2021 (belum berlaku) ke PER-16/PJ/2016 Pasal 14 ayat (8); rujukan pengembalian lebih potong untuk 2019 dan 2022 diganti dari PMK 168/2023 (belum berlaku) ke PER-16/PJ/2016 Pasal 14 ayat (7) dan Lampiran hlm. 24.
- Rujukan "terakhir diubah dengan" di Mengingat disesuaikan dengan tahun dokumen: UU 11/2020 untuk FR02 (November 2020), UU 7/2021 untuk FR03, FR05a, FR05b.

## FR01 — PP FIKTIF 901 Tahun 2019 (semula PMK FIKTIF 901/PMK.03/2019)

Tarif Efektif Pemotongan Pajak Penghasilan Pasal 21 bagi Pegawai Tetap. Teks: [FR01.md](../../dataset/09_korpus_peristiwa/fiktif/FR01.md)

Ringkasan: Mulai Masa Pajak Januari 2020, PPh 21 pegawai tetap untuk Januari sampai November tidak lagi dihitung dengan menyetahunkan gaji, tetapi cukup dengan mengalikan penghasilan bruto sebulan dengan tarif efektif bulanan dari tabel lampiran (dua kategori menurut status PTKP). Bonus dan penghasilan tidak teratur lain cukup ditambahkan ke bruto bulan itu. Pada Desember (atau bulan terakhir bekerja) pajak setahun dihitung ulang dengan tarif Pasal 17 dan dikurangi pajak yang sudah dipotong; kelebihan dikembalikan ke pegawai.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | Dikoreksi. Isinya masuk akal, tetapi PMK tidak berwenang menetapkan tarif pemotongan selain tarif Pasal 17: UU PPh Pasal 21 ayat (5) mensyaratkan Peraturan Pemerintah (itulah sebabnya TER nyata ditetapkan dengan PP 58/2023). Dokumen diubah menjadi PP FIKTIF 901 Tahun 2019 (Presiden, Lembaran Negara), konsiderans merujuk Pasal 21 ayat (5). |
| 2 | Apakah jenis perubahan **T7** dan sifat **S6** tepat? | Sesuai taksonomi bagian 1 | Ya (T7 dengan T2 tambahan). |
| 3 | Apakah tanggal konsisten (ditetapkan 2019-10-14, diundangkan 2019-10-16, berlaku 2020-01-01)? | Ya | Ya. |
| 4 | Apakah Δ KB yang diharapkan tepat? | sekumpulan aturan baru (pemotongan masa Jan-Nov = TEB x bruto, pemilihan kategori, tabel TEB berversi) dan pencabutan aturan disetahunkan untuk masa Jan-Nov sejak 2020-01-01; aturan Masa Pajak Terakhir tetap | Ya. Rujukan yang dicabut dipersempit menjadi PER-16/PJ/2016 Pasal 14 ayat (2)–(4); ayat (5) (Masa Pajak Terakhir) tetap. |
| 5 | Contoh **FR01-1** — Januari 2019: metode disetahunkan (aturan nyata). Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; masa 2019-01. Apakah hasilnya benar? | Sebelum: pph21 Rp112.091. Sesudah: – | Ya. |
| 6 | Contoh **FR01-2** — Januari 2020: tarif efektif bulanan fiktif. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; masa 2020-01. Apakah hasilnya benar? | Sebelum: pph21 Rp112.091. Sesudah: pph21 Rp73.178 | Ya. |
| 7 | Contoh **FR01-3** — Maret 2020: bonus Rp10.000.000. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; bonus Rp10.000.000; masa 2020-03. Apakah hasilnya benar? | Sebelum: pph21 Rp587.091. Sesudah: pph21 Rp1.039.068 | Ya. |
| 8 | Contoh **FR01-4** — Desember 2020: Masa Pajak Terakhir menurut FR01. Input: pegawai Tono, TK/0; upah sebulan Rp7.000.000; bonus maret Rp10.000.000; tahun 2020. Apakah hasilnya benar? | Sebelum: –. Sesudah: pph setahun Rp1.820.100; pph jan nov Rp1.770.848; pph desember Rp49.252 | Dikoreksi. Bruto Agustus–Desember 2020 = Rp7.280.378 (keringanan JKK/JKM 99%), PPh Agustus–November Rp72.803. Sesudah: pph setahun Rp1.811.250; pph jan nov Rp1.769.348; pph desember Rp41.902. |

## FR02 — PER FIKTIF-902/PJ/2020

Perubahan atas PER-16/PJ/2016 mengenai Pembulatan dalam Penghitungan PPh Pasal 21. Teks: [FR02.md](../../dataset/09_korpus_peristiwa/fiktif/FR02.md)

Ringkasan: Mulai Masa Pajak Januari 2021 ada dua aturan pembulatan baru. Pertama, penghasilan kena pajak setahun dibulatkan ke bawah sampai ratus ribu rupiah penuh, bukan lagi sampai ribuan. Kedua, PPh 21 setiap bulan (selain bulan terakhir) dibulatkan ke bawah sampai ratusan rupiah. Tarif, PTKP, dan pengurang tidak berubah.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | Ya, dengan dua koreksi teks: PER-16 Pasal 14 hanya punya ayat (1)–(8), sehingga ketentuan baru menjadi ayat (9) (bukan sisipan "(8a) di antara ayat (8) dan (9)"); Mengingat ditambah PMK 252/PMK.03/2008 dan UU PPh terakhir diubah UU 11/2020. |
| 2 | Apakah jenis perubahan **T9** dan sifat **S5** tepat? | Sesuai taksonomi bagian 1 | Ya. |
| 3 | Apakah tanggal konsisten (ditetapkan 2020-11-23, diundangkan –, berlaku 2021-01-01)? | Ya | Ya; PER Dirjen memang tidak diundangkan. |
| 4 | Apakah Δ KB yang diharapkan tepat? | dua entri registri pembulatan baru (PKP: 100.000 ke bawah; PPh masa: 100 ke bawah) berlaku sejak 2021-01-01, menggantikan pembulatan PKP ribuan | Ya. |
| 5 | Contoh **FR02-1** — Januari 2021: pembulatan PKP dan PPh bulanan. Input: pegawai Sinta, K/1; upah sebulan Rp7.500.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp98.670. Sesudah: pph21 Rp98.300 | Dikoreksi: Januari 2021 masih keringanan JKK/JKM; contoh dipindah ke Februari 2021 (masa 2021-02). Angka tetap Rp98.670 / Rp98.300. |
| 6 | Contoh **FR02-2** — Januari 2021: PKP kecil, efek pembulatan relatif besar. Input: pegawai Rizal, TK/0; upah sebulan Rp6.350.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp80.791. Sesudah: pph21 Rp80.400 | Dikoreksi seperti no. 5: dipindah ke Februari 2021; angka tetap. |
| 7 | Contoh **FR02-3** — Desember 2021: Masa Pajak Terakhir. Input: pegawai Sinta, K/1; upah sebulan Rp7.500.000; tahun 2021. Apakah hasilnya benar? | Sebelum: pkp Rp23.681.000; pph setahun Rp1.184.050; pph desember Rp98.680. Sesudah: pkp Rp23.600.000; pph setahun Rp1.180.000; pph desember Rp98.700 | Dikoreksi. Bruto Januari 2021 Rp7.800.405 (keringanan), PPh Januari Rp96.766 / Rp96.600, bruto setahun Rp94.045.905. Sebelum: pkp Rp23.643.000; pph setahun Rp1.182.150; pph desember Rp98.684. Sesudah: pkp Rp23.600.000; pph setahun Rp1.180.000; pph desember Rp100.400. |

## FR03 — PMK FIKTIF 903/PMK.03/2021

Pencabutan PMK FIKTIF 455/PMK.03/2017 tentang Tambahan Biaya Jabatan bagi Pegawai Tetap yang Bekerja Gilir Malam (semula "Pengurangan Biaya Transportasi"). Teks: [FR03.md](../../dataset/09_korpus_peristiwa/fiktif/FR03.md)

Ringkasan: Sejak 2018 (dalam dunia fiktif) pegawai tetap yang bekerja gilir malam paling sedikit 10 hari sebulan mendapat tambahan biaya jabatan sebesar 2% dari penghasilan bruto, paling banyak Rp100.000 sebulan atau Rp1.200.000 setahun. Peraturan ini mencabut tambahan tersebut tanpa pengganti mulai Masa Pajak Januari 2022. Untuk tahun pajak 2021 tambahan masih boleh dipakai, termasuk di perhitungan Desember 2021.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | Dikoreksi. UU PPh Pasal 21 ayat (3) membatasi pengurang pegawai tetap pada biaya jabatan, iuran pensiun, dan PTKP; "pengurangan biaya transportasi" tidak punya dasar. Pengurang dirumuskan ulang sebagai tambahan biaya jabatan (besarnya memang ditetapkan PMK). Mengingat: UU PPh terakhir diubah UU 7/2021. Angka contoh tidak berubah. |
| 2 | Apakah jenis perubahan **T8** dan sifat **tidak ada** tepat? | Sesuai taksonomi bagian 1 | Ya. |
| 3 | Apakah tanggal konsisten (ditetapkan 2021-11-22, diundangkan 2021-11-24, berlaku 2022-01-01)? | Ya | Ya. |
| 4 | Apakah Δ KB yang diharapkan tepat? | pencabutan (remove/valid_until 2021-12-31) atas aturan pengurang gilir malam; tidak ada aturan baru | Ya (aturan tambahan biaya jabatan gilir malam). |
| 5 | Contoh **FR03-1** — Januari 2021: pengurang gilir malam masih berlaku. Input: pegawai Bagus, K/0, operator gilir malam 15 hari/bulan; upah sebulan Rp6.800.000; masa 2021-01. Apakah hasilnya benar? | Sebelum: pph21 Rp78.712. Sesudah: – | Dikoreksi: dipindah ke Februari 2021 (Januari masih keringanan JKK/JKM); angka tetap Rp78.712. |
| 6 | Contoh **FR03-2** — Januari 2022: setelah pencabutan (tarif UU HPP). Input: pegawai Bagus, K/0; upah sebulan Rp6.800.000; masa 2022-01. Apakah hasilnya benar? | Sebelum: pph21 Rp78.712. Sesudah: pph21 Rp83.712 | Ya. |
| 7 | Contoh **FR03-3** — Desember 2022: Masa Pajak Terakhir. Input: pegawai Bagus, K/0; upah sebulan Rp6.800.000; tahun 2022. Apakah hasilnya benar? | Sebelum: pkp Rp18.891.000; pph setahun Rp944.550. Sesudah: pkp Rp20.091.000; pph setahun Rp1.004.550 | Ya untuk nilai yang tercantum. Langkah "sebelum" memakai potongan Jan–Nov skenario sesudah (Rp920.832 → Desember Rp23.718); yang benar 11 × Rp78.712 = Rp865.832 → Desember Rp78.718. PPh Desember ditambahkan ke hasil: sebelum Rp78.718, sesudah Rp83.718. |

## FR04 — PMK FIKTIF 904/PMK.03/2018

Perlakuan Pajak Penghasilan Pasal 21 atas Komisi Penjualan yang Diterima Pegawai Tetap. Teks: [FR04.md](../../dataset/09_korpus_peristiwa/fiktif/FR04.md)

Ringkasan: Mulai Masa Pajak Januari 2019, komisi penjualan yang besarnya mengikuti hasil penjualan dan tidak dibayar dalam jumlah tetap setiap bulan dianggap penghasilan tidak teratur. Akibatnya komisi tidak lagi ikut disetahunkan (dikali 12) saat menghitung pajak bulanan; pajaknya dihitung sebagai selisih seperti bonus. Komisi dalam jumlah tetap setiap bulan tetap penghasilan teratur. Pajak setahun tidak berubah.

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | Ya; konsiderans ditambah dasar Pasal 21 ayat (8) UU PPh (juklak pemotongan dengan PMK). |
| 2 | Apakah jenis perubahan **T3** dan sifat **tidak ada** tepat? | Sesuai taksonomi bagian 1 | Ya. |
| 3 | Apakah tanggal konsisten (ditetapkan 2018-09-17, diundangkan 2018-09-19, berlaku 2019-01-01)? | Ya | Ya. |
| 4 | Apakah Δ KB yang diharapkan tepat? | aturan klasifikasi baru: komisi penjualan variabel -> penghasilan tidak teratur, sejak 2019-01-01; komisi tetap -> teratur | Ya. |
| 5 | Contoh **FR04-1** — Februari 2019: bulan dengan komisi. Input: pegawai Lina, staf pemasaran, TK/0; gaji Rp6.000.000; komisi Rp4.000.000; masa 2019-02. Apakah hasilnya benar? | Sebelum: pph21 Rp347.183. Sesudah: pph21 Rp253.937 | Ya. |
| 6 | Contoh **FR04-2** — Maret 2019: bulan tanpa komisi. Input: pegawai Lina, TK/0; gaji Rp6.000.000; komisi Rp0; masa 2019-03. Apakah hasilnya benar? | Sebelum: pph21 Rp63.937. Sesudah: pph21 Rp63.937 | Ya. |
| 7 | Contoh **FR04-3** — Desember 2019: Masa Pajak Terakhir. Input: pegawai Lina, TK/0; gaji Rp6.000.000; komisi 4 x Rp4.000.000; tahun 2019. Apakah hasilnya benar? | Sebelum: pph setahun Rp1.527.250; pph jan nov Rp1.836.291; pph desember -Rp309.041. Sesudah: pph setahun Rp1.527.250; pph jan nov Rp1.463.307; pph desember Rp63.943 | Ya. Rujukan pengembalian lebih potong diganti ke PER-16/PJ/2016 Lampiran hlm. 24 (PMK 168/2023 belum berlaku pada 2019). |

## FR05 — PMK FIKTIF 905/PMK.03/2021 + PER FIKTIF-906/PJ/2022 (semula PP FIKTIF 905 Tahun 2021 + PMK FIKTIF 906/PMK.03/2022)

Penyesuaian Besarnya Biaya Jabatan (dua dokumen). Teks: [FR05a.md](../../dataset/09_korpus_peristiwa/fiktif/FR05a.md), [FR05b.md](../../dataset/09_korpus_peristiwa/fiktif/FR05b.md)

Ringkasan: Plafon biaya jabatan dinaikkan dari Rp6.000.000 menjadi Rp7.200.000 setahun. PMK fiktif (6 Desember 2021) menetapkan angka tahunan, menyerahkan batas bulanan dan saat mulai diterapkan kepada PER Dirjen, dan menyatakan plafon lama tetap dipakai sampai saat itu; PER fiktif (14 Februari 2022) menetapkan batas Rp600.000 sebulan dan menerapkannya sejak Masa Pajak Januari 2022 (surut).

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah perubahan ini masuk akal sebagai regulasi pada tahun itu (bentuk dokumen, bahasa, isi)? | Ya | Dikoreksi. UU PPh Pasal 21 ayat (3) menyatakan besarnya biaya jabatan "ditetapkan dengan Peraturan Menteri Keuangan", sehingga PP sebagai dokumen pertama tidak lazim. Diubah menjadi PMK FIKTIF 905/PMK.03/2021 (angka tahunan; Pasal 3 menegaskan plafon lama tetap dipakai) dan PER FIKTIF-906/PJ/2022 (batas bulanan, penerapan surut, penyelesaian selisih Januari–Februari). Mengingat: UU 7/2021. |
| 2 | Apakah jenis perubahan **T1** dan sifat **S4, S1** tepat? | Sesuai taksonomi bagian 1 | Ya. |
| 3 | Apakah tanggal konsisten (ditetapkan 2022-02-14, diundangkan 2022-02-15, berlaku 2022-01-01)? | Ya | Dikoreksi: dokumen kedua kini PER Dirjen, ditetapkan 2022-02-14 dan tidak diundangkan; tanggal pengetahuan peristiwa 2022-02-14. INDEX dan README sudah diselaraskan (README lama menulis 2021-12-06 / 2022-02-14 untuk ditetapkan, INDEX menulis 2022-02-14). |
| 4 | Apakah Δ KB yang diharapkan tepat? | parameter biaya jabatan berversi baru (7.200.000/tahun; 600.000/bulan) valid_from 2022-01-01, recorded_on 2022-02-15; dokumen pertama saja seharusnya menghasilkan kandidat tertunda, bukan perubahan aktif | Ya, dengan `recorded_on` 2022-02-14. |
| 5 | Contoh **FR05-1** — Tahun 2022, bruto setahun di atas Rp144 juta. Input: pegawai Fajar, K/2; upah sebulan Rp8.000.000; tunjangan kinerja Rp12.000.000; tahun 2022. Apakah hasilnya benar? | Sebelum: pph bulanan Rp1.599.725; biaya jabatan Rp6.000.000; pph setahun Rp19.196.700. Sesudah: pph bulanan Rp1.584.725; biaya jabatan Rp7.200.000; pph setahun Rp19.016.700 | Ya. Ditambah catatan: bila Januari–Februari sudah dipotong dengan plafon lama, selisih 2 × Rp15.000 diperhitungkan di masa berikutnya atau Desember (FR05b Pasal 2 ayat (2)). |
| 6 | Contoh **FR05-2** — Tahun 2022, bruto setahun di bawah Rp120 juta (tidak terdampak). Input: pegawai Wulan, TK/0; upah sebulan Rp7.000.000; tahun 2022. Apakah hasilnya benar? | Sebelum: biaya jabatan Rp4.390.680; pph setahun Rp1.345.100. Sesudah: biaya jabatan Rp4.390.680; pph setahun Rp1.345.100 | Ya. |
| 7 | Contoh **FR05-3** — Pegawai berhenti 30 Juni 2022: plafon bulanan dari dokumen kedua. Input: pegawai Dimas, TK/0; upah sebulan Rp8.000.000; tunjangan kinerja Rp6.000.000; berhenti 2022-06-30. Apakah hasilnya benar? | Sebelum: biaya jabatan Rp3.000.000; pph setahun Rp1.386.950; pph juni -Rp2.955.425. Sesudah: biaya jabatan Rp3.600.000; pph setahun Rp1.356.950; pph juni -Rp2.910.425 | Ya. Rujukan pengembalian diganti ke PER-16/PJ/2016 Pasal 14 ayat (7). |
| 8 | Contoh **FR05-4** — Antara dokumen pertama dan kedua: belum ada perubahan yang dapat diterapkan. Input: tanggal pengetahuan 2022-01-31. Apakah hasilnya benar? | Sebelum: plafon biaya jabatan dipakai Rp6.000.000. Sesudah: plafon biaya jabatan dipakai Rp6.000.000 | Ya; dasarnya kini eksplisit di FR05a Pasal 3. |

## Pertanyaan umum

1. Apakah ada dokumen yang terlalu mirip regulasi nyata sehingga bisa disangka asli bila keluar dari folder ini?

   Jawaban: Risikonya kecil. Setiap berkas diawali tanda "DOKUMEN FIKTIF UNTUK PENELITIAN", judulnya memuat "(FIKTIF)", nomornya (901–906, BN/LN 1901–1906 dan 901) jauh di atas nomor nyata tahun itu, dan nama pejabat tidak diisi. Yang paling mirip adalah FR01 karena isinya mendahului TER nyata (PP 58/2023); karena itu tabelnya sengaja memakai dua kategori dan batas yang berbeda dari TER. Bila dokumen dikutip tanpa kepala berkas, nomor dan kata "FIKTIF" di judul tetap menandainya.

2. Apakah ada jenis perubahan lain sebelum 2023 yang sebaiknya dibuatkan contoh fiktif?

   Jawaban: Dua jenis belum tertutup. (a) T10 perubahan kebijakan perusahaan: dokumen PKB atau peraturan perusahaan fiktif sebelum 2023, misalnya perusahaan berhenti menanggung PPh 21 (pergeseran *gross-up* ke *gross*), untuk menyetel gerbang lapisan perusahaan tanpa menyentuh dokumen uji. (b) T6 pengakhiran lebih awal: fasilitas yang dihentikan sebelum `berlaku_sampai`, karena contoh nyata T6 (D07, D11, E09) semuanya perpanjangan. T5 penyempitan cakupan (kriteria diperketat) juga belum punya contoh; bisa digabung dengan (b) dalam satu dokumen.

## Hasil

- [ ] Disetujui
- [x] Disetujui dengan perubahan (tulis di atas)
- [ ] Perlu revisi

Status: selesai
