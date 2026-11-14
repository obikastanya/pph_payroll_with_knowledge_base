# Regulasi fiktif untuk data pengembangan (FR01–FR05)

> **DOKUMEN FIKTIF UNTUK PENELITIAN.** Nomor, isi, tanggal, dan pejabat rekaan. Hanya untuk bagian **pengembangan** (menyetel *prompt* dan gerbang). **Tidak pernah dipakai untuk pengujian.** Disusun 2026-10-27; ditinjau 2026-10-27 ([review/corpus/fiktif.review.md](../../../review/corpus/fiktif.review.md)).

## Tujuan

Peristiwa pengembangan nyata yang relevan di [peristiwa.csv](../peristiwa.csv) (D01–D07, D09–D11) hanya mencakup T1, T4, T5, dan T6; D13 adalah pencabutan tanpa efek hitung. Dokumen fiktif ini menutup jenis perubahan yang tidak punya contoh nyata sebelum 2023, sehingga *prompt* dan gerbang dapat disetel untuk semua jenis tanpa menyentuh data uji E01–E12.

| ID | Berkas | Nomor (fiktif) | Jenis utama | Sifat | Ditetapkan | Diundangkan | Berlaku mulai | Contoh |
|---|---|---|---|---|---|---|---|---|
| FR01 | `FR01.md` | PP FIKTIF 901 Tahun 2019 | T7 pergantian metode (+T2 tabel baru) | S6 | 2019-10-14 | 2019-10-16 | 2020-01-01 | 4 |
| FR02 | `FR02.md` | PER FIKTIF-902/PJ/2020 | T9 pembulatan | S5 | 2020-11-23 | – | 2021-01-01 | 3 |
| FR03 | `FR03.md` | PMK FIKTIF 903/PMK.03/2021 | T8 pencabutan tanpa pengganti | – | 2021-11-22 | 2021-11-24 | 2022-01-01 | 3 |
| FR04 | `FR04.md` | PMK FIKTIF 904/PMK.03/2018 | T3 klasifikasi penghasilan | – | 2018-09-17 | 2018-09-19 | 2019-01-01 | 3 |
| FR05 | `FR05a.md`, `FR05b.md` | PMK FIKTIF 905/PMK.03/2021 + PER FIKTIF-906/PJ/2022 | T1 parameter | S4, S1 | 2021-12-06 / 2022-02-14 | 2021-12-06 / – | 2022-01-01 (surut) | 4 |

Per jenis: T7 1, T9 1, T8 1, T3 1, dan satu perubahan S4 (jenis utama T1) yang terbagi atas dua dokumen. FR05 sengaja ditulis sebagai dua berkas `.md` (satu peristiwa, satu `.json`) karena tujuannya menguji apakah sistem menunda penerapan sampai dokumen kedua terbit. Tanggal pengetahuan FR05 adalah tanggal penetapan dokumen kedua, 2022-02-14 (PER Dirjen tidak diundangkan).

Jenis dokumen mengikuti kewenangan di UU PPh: tarif pemotongan selain tarif Pasal 17 harus ditetapkan dengan PP (Pasal 21 ayat (5)), sehingga FR01 berbentuk PP; besarnya biaya jabatan ditetapkan dengan PMK (Pasal 21 ayat (3)), sehingga FR03 dan FR05a berbentuk PMK; petunjuk pelaksanaan pemotongan diatur dengan atau berdasarkan PMK (Pasal 21 ayat (8)), sehingga FR04 berbentuk PMK dan FR02 serta FR05b berbentuk PER Dirjen. Rujukan "terakhir diubah dengan" di Mengingat mengikuti tahun dokumen: UU 36/2008 (2018–2019), UU 11/2020 (November 2020), UU 7/2021 (sejak November 2021).

Nomor 901–906 dipilih jauh di atas nomor PMK, PER, dan PP nyata pada tahun yang sama, sehingga tidak bertabrakan dengan regulasi nyata. PMK FIKTIF 455/PMK.03/2017 (tambahan biaya jabatan gilir malam) yang dicabut FR03 juga fiktif; isinya hanya diringkas di konsiderans FR03.

## Cara membaca

- Setiap FR adalah **kontrafaktual terpisah** terhadap aturan nyata yang berlaku saat itu (PER-16/PJ/2016, tarif Pasal 17 UU 36/2008 untuk 2019–2021 dan UU HPP untuk 2022, PTKP PMK 101/2016, biaya jabatan Rp6.000.000). FR tidak saling membangun: misalnya contoh FR02 dan FR03 memakai metode disetahunkan nyata, bukan tarif efektif fiktif FR01.
- `FRxx.json` memuat `jenis_utama`, `sifat`, `ditetapkan`, `diundangkan`, `berlaku_mulai`, `berlaku_sampai`, `ringkasan_perubahan` (bahasa sederhana), `delta_yang_diharapkan` (bentuk Δ KB yang seharusnya dihasilkan), dan `contoh[]`.
- Setiap contoh memuat `hasil_sebelum_perubahan` dan `hasil_sesudah_perubahan` (salah satunya `null` bila contoh hanya menunjukkan satu sisi), `langkah` dengan rujukan, dan `cek_aritmetika`.

## Contoh hitung dan pemeriksaan aritmetika

17 contoh. 307 ekspresi di `cek_aritmetika` dihitung ulang dengan pecahan eksak: **0 selisih**. Asumsi:

- upah contoh di bawah batas upah JP dan JKN tahun berjalan; premi JKK 0,24%, JKM 0,3%, JKN 4% masuk bruto; iuran JHT 2% dan JP 1% pekerja sebagai pengurang; hasil bagi /12 dibulatkan ke bawah ke rupiah (kecuali FR02 yang mengubahnya);
- iuran JKK dan JKM bulan Agustus 2020–Januari 2021 mendapat keringanan 99% (PP 49/2020, D09), sehingga bruto bulan itu lebih kecil (FR01-4, FR02-3). Contoh bulanan 2021 memakai Februari agar bebas dari keringanan;
- rekomposisi JKK/JKM untuk JKP sejak Februari 2021 (PP 37/2021) tidak mengubah jumlah yang dibayar pemberi kerja, sehingga premi di bruto tetap 0,24% + 0,3% (K8 di [tafsir_perhitungan.md](../../../docs/spesifikasi/tafsir_perhitungan.md));
- PPh 21 DTP masa COVID (PMK 23/2020 s.d. PMK 82/2021) tidak dimodelkan: insentif itu mengubah pihak yang menanggung pajak, bukan PPh terutang.

Hal yang diuji per dokumen:

- **FR01**: pencabutan metode lama dan aturan baru sekaligus; PPh setahun tetap sama, sebaran per masa berubah (FR01-4).
- **FR02**: pembulatan PKP ke ratus ribu dan PPh masa ke ratusan; selisih kecil yang mudah terlewat; Masa Pajak Terakhir tidak ikut dibulatkan ke ratusan (FR02-3).
- **FR03**: pencabutan tanpa pengganti dengan ketentuan peralihan (2021 masih boleh); menguji L6 (pencabutan terlewat).
- **FR04**: perubahan klasifikasi yang tidak mengubah PPh setahun tetapi mengubah pemotongan bulanan (FR04-3).
- **FR05**: dokumen pertama saja tidak cukup (FR05-4); plafon bulanan hanya ada di dokumen kedua (FR05-3); berlaku surut ke Januari 2022, dengan selisih Januari–Februari diperhitungkan di masa berikutnya atau Masa Pajak Terakhir (FR05-1).
