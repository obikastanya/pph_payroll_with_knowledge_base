# Tinjauan: kebijakan perusahaan sintetis SP01–SP14

Berkas yang diperiksa: [dataset/10_kebijakan_perusahaan/sintetis/](../../dataset/10_kebijakan_perusahaan/sintetis/) (`SPxx.md` teks dokumen, `SPxx.json` konflik, contoh, dan label dampak; ringkasan di `README.md`).
Pemeriksa: pakar *payroll* · Status: **menunggu**

Semua perusahaan dan dokumen **fiktif**. Untuk setiap kebijakan, isi kolom **Setuju? / koreksi** dengan `ya`, atau tulis nilai/penilaian yang benar beserta alasannya. Langkah hitung lengkap ada di `langkah` pada `SPxx.json`.

Kode konflik (taksonomi bagian 2): C1 klasifikasi penghasilan, C2 komponen bruto hilang, C3 pengurang tidak sah/melebihi plafon, C4 fasilitas pemerintah tidak diteruskan, C5 tarif/metode menyimpang, C6 parameter usang, C7 pembagian iuran menyimpang, C8 batas upah diabaikan, C9 pembulatan menyimpang, C10 hak minimum dilanggar. Status: aktif, laten, terpicu.

Asumsi hitungan yang perlu dinilai sekali untuk semua: hasil TER x bruto dibulatkan ke bawah ke rupiah (tidak diatur regulasi); premi JKK, JKM, dan JKN bagian pemberi kerja masuk bruto; JP dibatasi batas upah per Maret; JKN dibatasi Rp12 juta.

| Asumsi umum | Setuju? / koreksi |
|---|---|
| Pembulatan TER ke bawah ke rupiah penuh | |
| Premi JKK/JKM/JKN pemberi kerja masuk bruto, termasuk saat keringanan JKK (bruto ikut turun) | |
| Pegawai berhenti di tengah tahun: neto tidak disetahunkan, PTKP penuh, biaya jabatan Rp500.000 x bulan bekerja | |

## SP01 — PT Lintas Gudang Nusantara

Peraturan Perusahaan, KLU 52101 (Pergudangan dan penyimpanan), Cikarang, Kabupaten Bekasi; berlaku 2023-04-01 s.d. 2025-03-31. Teks: [SP01.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP01.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C6 (terpicu, pemicu E05)** pada Pasal 22 ayat (4)-(5) benar? | Saat ditetapkan (Maret 2023), Rp9.559.600 sama dengan batas yang berlaku (E01), sehingga sah. Ayat (5) mengunci nilai itu sampai Maret 2025. Sejak iuran Maret 2024 (E05) batas wajib Rp10.042.300, dan sejak Maret 2025 (E08) Rp10.547.400, sehingga iuran JP pekerja berupah di atas batas kurang dipungut dan pengurang PPh 21 di Masa Pajak Terakhir terlalu kecil. Aturan wajib: PP 45/2015 Pasal 29 ayat (3)-(4) (PDF hlm. 21): batas upah JP disesuaikan setiap tahun; Surat BPJS TK B/1387/022024 (BPJSTK_JP_2024_B-1387-022024_mirror_ramco.pdf, teks surat hlm. 1): batas Rp10.042.300 mulai iuran Maret 2024 | |
| 3 | Apakah benar kebijakan ini sah saat ditetapkan dan baru berkonflik setelah peristiwa pemicu? | Ya | |
| 4 | Contoh **SP01-1** — Iuran JP April 2023 (sebelum peristiwa pemicu). Input: pekerja Andi, pegawai tetap, TK/0; upah sebulan Rp12.000.000; masa 2023-04. Apakah hasilnya benar? | Kebijakan: iuran jp pekerja Rp95.596; iuran jp perusahaan Rp191.192. Aturan wajib: iuran jp pekerja Rp95.596; iuran jp perusahaan Rp191.192 | |
| 5 | Contoh **SP01-2** — Iuran JP April 2024 (setelah E05). Input: pekerja Andi, TK/0; upah sebulan Rp12.000.000; masa 2024-04. Apakah hasilnya benar? | Kebijakan: iuran jp pekerja Rp95.596; iuran jp perusahaan Rp191.192. Aturan wajib: iuran jp pekerja Rp100.423; iuran jp perusahaan Rp200.846 | |
| 6 | Contoh **SP01-3** — PPh 21 Masa Pajak Desember 2024 (dampak batas JP usang pada pengurang). Input: pekerja Andi, TK/0; upah sebulan Rp12.000.000; tahun 2024; jkk 0,54% (risiko rendah); jkm 0,30%; jkn pemberi kerja 4% (batas Rp12.000.000). Apakah hasilnya benar? | Kebijakan: iuran jp pekerja setahun Rp1.147.152; neto Rp140.942.448; pkp Rp86.942.000; pph setahun Rp7.041.300; pph masa terakhir Rp121.860. Aturan wajib: iuran jp pekerja setahun Rp1.195.422; neto Rp140.894.178; pkp Rp86.894.000; pph setahun Rp7.034.100; pph masa terakhir Rp114.660 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E03(a), E04(a), E05(c), E08(c); lainnya `tidak` | |

## SP02 — PT Presisi Komponen Otomotif

Peraturan Perusahaan (Lampiran Sistem Penggajian), KLU 29300 (Industri suku cadang dan aksesori kendaraan bermotor roda empat atau lebih), Kawasan Industri Surya Cipta, Karawang; berlaku 2023-01-01 s.d. 2024-12-31. Teks: [SP02.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP02.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C5 (terpicu, pemicu E03+E04)** pada Pasal 31 ayat (2), (3), dan (5) benar? | Ayat (2)-(3) menyalin metode disetahunkan PER-16/PJ/2016 Pasal 14 ayat (2)-(5) (PDF hlm. 13), yang sah sepanjang 2023. Mulai Masa Pajak Januari 2024 pemotongan Januari-November wajib memakai TER x bruto (E03 menetapkan tarif, E04 menetapkan tata cara dan mencabut dasar lama). Ayat (5) mengunci metode lama sampai Desember 2024. Ayat (4) tetap sejalan dengan Masa Pajak Terakhir menurut PMK 168/2023. Aturan wajib: PP 58/2023 Pasal 2 (PDF hlm. 3-5) dan Lampiran A-C (PDF hlm. 11-24); PMK 168/2023 Pasal 15 ayat (1) huruf a (PDF hlm. 15); PMK 168/2023 Pasal 24 huruf b (PDF hlm. 22) mencabut PMK 252/PMK.03/2008 yang menjadi dasar PER-16/PJ/2016 | |
| 3 | Apakah benar kebijakan ini sah saat ditetapkan dan baru berkonflik setelah peristiwa pemicu? | Ya | |
| 4 | Contoh **SP02-1** — Januari 2023: metode disetahunkan masih berlaku. Input: pekerja Sari, K/1; upah sebulan Rp15.000.000; masa 2023-01; jkk 0,89%. Apakah hasilnya benar? | Kebijakan: pph21 Rp927.650. Aturan wajib: pph21 Rp927.650 | |
| 5 | Contoh **SP02-2** — Januari 2024: setelah E03 dan E04. Input: pekerja Sari, K/1; upah sebulan Rp15.000.000; masa 2024-01. Apakah hasilnya benar? | Kebijakan: pph21 Rp926.925; metode disetahunkan (PER-16). Aturan wajib: pph21 Rp939.510; metode TER kategori B | |
| 6 | Contoh **SP02-3** — Maret 2024: bonus tahunan Rp30.000.000. Input: pekerja Sari, K/1; upah sebulan Rp15.000.000; bonus Rp30.000.000; masa 2024-03. Apakah hasilnya benar? | Kebijakan: pph21 Rp5.426.200. Aturan wajib: pph21 Rp7.305.360 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E01(a), E03(c), E04(b,c), E05(a); lainnya `tidak` | |

## SP03 — PT Samudra Biru Hospitality

Perjanjian Kerja Bersama, KLU 55110 (Hotel bintang), Sanur, Denpasar, Bali; berlaku 2025-03-01 s.d. 2026-12-31. Teks: [SP03.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP03.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C4 (terpicu, pemicu E10)** pada Pasal 40 ayat (3) benar? | Saat PKB ditandatangani (Februari 2025) hotel bintang tidak termasuk penerima DTP PMK 10/2025, sehingga ayat (3) tidak berdampak. E10 (terbit 20 Oktober 2025, berlaku surut ke Masa Pajak Oktober 2025) memasukkan sektor pariwisata; DTP wajib dibayar tunai kepada pegawai pada saat pembayaran penghasilan. Ayat (3) menahan DTP di Perusahaan, sehingga berkonflik untuk Oktober-Desember 2025, dan tetap berkonflik pada 2026 karena E11. Aturan wajib: PMK 72/2025 Pasal I angka 3-5: Pasal 3 ayat (1) huruf a angka 5, Pasal 4A huruf b, Pasal 5 ayat (1) PMK 10/2025 (PDF hlm. 3-4), KLU 55110 di Lampiran A (PDF hlm. 17); untuk 2026: PMK 105/2025 Pasal 3 dan Pasal 5 ayat (1) (PDF hlm. 4-6), Lampiran A (PDF hlm. 19) | |
| 3 | Apakah benar kebijakan ini sah saat ditetapkan dan baru berkonflik setelah peristiwa pemicu? | Ya | |
| 4 | Contoh **SP03-1** — Agustus 2025: belum ada DTP untuk pariwisata. Input: pekerja Made, TK/0, bekerja sejak 2022; upah sebulan Rp6.800.000; masa 2025-08. Apakah hasilnya benar? | Kebijakan: pph21 Rp88.859; dtp tunai ke pekerja Rp0; penerimaan bersih Rp6.439.141. Aturan wajib: pph21 Rp88.859; dtp tunai ke pekerja Rp0; penerimaan bersih Rp6.439.141 | |
| 5 | Contoh **SP03-2** — Oktober 2025: setelah E10 (berlaku surut ke Masa Oktober). Input: pekerja Made, TK/0; upah sebulan Rp6.800.000; masa 2025-10. Apakah hasilnya benar? | Kebijakan: pph21 Rp88.859; dtp tunai ke pekerja Rp0; penerimaan bersih Rp6.439.141. Aturan wajib: pph21 Rp88.859; dtp tunai ke pekerja Rp88.859; penerimaan bersih Rp6.528.000 | |
| 6 | Contoh **SP03-3** — Februari 2026: DTP TA 2026 (E11). Input: pekerja Made, TK/0; upah sebulan Rp7.200.000; masa 2026-02. Apakah hasilnya benar? | Kebijakan: pph21 Rp112.903; dtp tunai ke pekerja Rp0; penerimaan bersih Rp6.799.097. Aturan wajib: pph21 Rp112.903; dtp tunai ke pekerja Rp112.903; penerimaan bersih Rp6.912.000 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E08(a), E10(c), E11(c), E12(a); lainnya `tidak` | |

## SP04 — PT Arunika Energi Mandiri

Peraturan Perusahaan, KLU 09100 (Aktivitas penunjang pertambangan minyak bumi dan gas alam (kantor pusat)), Jakarta Selatan; berlaku 2023-01-01 s.d. 2024-12-31. Teks: [SP04.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP04.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C1 (terpicu, pemicu E02)** pada Pasal 27 ayat (2) jo. Pasal 28 benar? | Untuk Masa Januari-Juni 2023 natura dikecualikan dari pemotongan oleh pemberi kerja (PMK 66/2023 Pasal 23 ayat (4), PDF hlm. 18), sehingga Pasal 28 tidak berbeda dengan aturan. Mulai 1 Juli 2023 (E02) kenikmatan apartemen individual di atas Rp2.000.000 per bulan adalah objek PPh 21 yang wajib dipotong; Pasal 28 mengklasifikasikannya sebagai bukan penghasilan. Makan siang untuk seluruh pekerja (ayat (1)) dan APD (ayat (3)) tetap dikecualikan (Pasal 4 huruf a dan c, PDF hlm. 6-7), jadi bagian itu tidak berkonflik. Aturan wajib: PMK 66/2023 Pasal 3 ayat (1) (PDF hlm. 5) dan Pasal 23 ayat (1)-(2) (PDF hlm. 17); pengecualian apartemen individual hanya sampai Rp2.000.000 per bulan: Lampiran A angka 7 (PDF hlm. 22), contoh 3 (PDF hlm. 47) | |
| 3 | Apakah benar kebijakan ini sah saat ditetapkan dan baru berkonflik setelah peristiwa pemicu? | Ya | |
| 4 | Contoh **SP04-1** — Mei 2023: apartemen belum masuk pemotongan. Input: pekerja Rina, manajer, K/2; upah sebulan Rp25.000.000; sewa apartemen Rp6.000.000; masa 2023-05. Apakah hasilnya benar? | Kebijakan: bruto pemotongan Rp25.615.000; pph21 Rp2.334.150. Aturan wajib: bruto pemotongan Rp25.615.000; pph21 Rp2.334.150 | |
| 5 | Contoh **SP04-2** — Agustus 2023: setelah E02 (metode disetahunkan). Input: pekerja Rina, K/2; upah sebulan Rp25.000.000; sewa apartemen Rp6.000.000; masa 2023-08. Apakah hasilnya benar? | Kebijakan: bruto pemotongan Rp25.615.000; pph21 Rp2.334.150. Aturan wajib: bruto pemotongan Rp29.615.000; pph21 Rp3.140.250 | |
| 6 | Contoh **SP04-3** — Februari 2024: TER kategori B. Input: pekerja Rina, K/2; upah sebulan Rp25.000.000; sewa apartemen Rp6.000.000; masa 2024-02. Apakah hasilnya benar? | Kebijakan: bruto pemotongan Rp25.615.000; pph21 Rp2.305.350. Aturan wajib: bruto pemotongan Rp29.615.000; pph21 Rp3.553.800 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E01(a), E02(c), E03(a), E04(a), E05(a); lainnya `tidak` | |

## SP05 — PT Benang Sutra Lestari

Perjanjian Kerja Bersama, KLU 13112 (Industri pemintalan benang (tercantum Lampiran A PMK 10/2025, PDF hlm. 9)), Majalaya, Kabupaten Bandung; berlaku 2024-07-01 s.d. 2026-06-30. Teks: [SP05.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP05.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C6 (terpicu, pemicu E07)** pada Pasal 45 ayat (2) jo. Pasal 46 benar? | Ayat (2) menulis tarif JKK sebagai angka tetap 0,54%. Saat ditandatangani angka itu sama dengan PP 44/2015. E07 menurunkan tarif wajib menjadi 0,27% bagi industri tekstil dengan >= 50 pekerja aktif untuk iuran Februari-Juli 2025, dan E09 memperpanjangnya sampai iuran Januari 2026 secara surut sejak Agustus 2025. Selama masa itu, premi JKK yang dimasukkan ke bruto menurut Pasal 46 (0,54%) lebih besar daripada premi yang benar-benar terutang, sehingga bruto, PPh 21 terutang, dan nilai DTP pada bukti potong salah. Konflik selesai dengan sendirinya mulai iuran Februari 2026. Aturan wajib: PP 7/2025 Pasal 3 ayat (3)-(4) dan Pasal 4 ayat (1) huruf b (PDF hlm. 3-4): iuran JKK risiko rendah 0,27% untuk iuran Februari-Juli 2025; diperpanjang sampai iuran Januari 2026 oleh PP 36/2025 Pasal I angka 2 (Pasal 10A, PDF hlm. 4); premi JKK yang dibayar pemberi kerja menambah bruto: PMK 168/2023 Pasal 5 ayat (3) huruf d (PDF hlm. 9) | |
| 3 | Apakah benar kebijakan ini sah saat ditetapkan dan baru berkonflik setelah peristiwa pemicu? | Ya | |
| 4 | Contoh **SP05-1** — Januari 2025: tarif JKK normal. Input: pekerja Siti, operator pemintalan, TK/0; upah sebulan Rp5.500.000; masa 2025-01. Apakah hasilnya benar? | Kebijakan: premi jkk Rp29.700; bruto Rp5.766.200; pph21 terutang dtp Rp28.831. Aturan wajib: premi jkk Rp29.700; bruto Rp5.766.200; pph21 terutang dtp Rp28.831 | |
| 5 | Contoh **SP05-2** — Maret 2025: setelah E07 (keringanan JKK 50%). Input: pekerja Siti, TK/0; upah sebulan Rp5.500.000; masa 2025-03. Apakah hasilnya benar? | Kebijakan: premi jkk Rp29.700; bruto Rp5.766.200; pph21 terutang dtp Rp28.831. Aturan wajib: premi jkk Rp14.850; bruto Rp5.751.350; pph21 terutang dtp Rp28.756 | |
| 6 | Contoh **SP05-3** — Desember 2025: Masa Pajak Terakhir (E07 dan E09). Input: pekerja Siti, TK/0; upah sebulan Rp5.500.000; tahun 2025. Apakah hasilnya benar? | Kebijakan: bruto Rp69.194.400; pkp Rp9.754.000; pph setahun Rp487.700; pph masa terakhir Rp170.559. Aturan wajib: bruto Rp69.031.050; pkp Rp9.599.000; pph setahun Rp479.950; pph masa terakhir Rp163.559 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E06(b), E07(c), E08(a), E09(c), E11(b), E12(a); lainnya `tidak` | |

## SP06 — PT Mitra Niaga Sandang

Perjanjian Kerja Bersama, KLU 46411 (Perdagangan besar tekstil (tidak tercantum Lampiran A PMK 10/2025, PMK 72/2025, maupun PMK 105/2025)), Kota Bandung; berlaku 2025-01-01 s.d. 2026-12-31. Teks: [SP06.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP06.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C4 (laten)** pada Pasal 33 ayat (3) benar? | Ayat (3) menukar DTP dengan tunjangan PPh yang sudah dijanjikan, sehingga pekerja tidak menerima manfaat insentif. Karena KLU utama 46411 tidak tercantum dalam lampiran DTP mana pun, klausul ini belum pernah menghasilkan nilai yang dilarang. Konflik muncul hanya bila syarat terpenuhi: KLU utama di basis data DJP berubah ke KLU yang tercantum (misalnya 14111 bila Perusahaan membuka lini konveksi) dan pekerja memenuhi kriteria bruto Januari. Pola sama dengan PKB WIKA 2025-2026 Pasal 22 ayat (3). Aturan wajib: PMK 10/2025 Pasal 5 ayat (1) (PDF hlm. 6) dan PMK 105/2025 Pasal 5 ayat (1) (PDF hlm. 6): DTP wajib dibayar tunai kepada pegawai, termasuk dalam hal pemberi kerja memberikan tunjangan PPh 21 atau menanggung PPh 21 | |
| 3 | Apakah benar konflik hanya muncul bila syarat tertentu terpenuhi (bukan sekarang)? | Ya | |
| 4 | Contoh **SP06-1** — Maret 2025: perusahaan tidak memenuhi kriteria DTP. Input: pekerja Dewi, K/1; upah sebulan Rp8.000.000; masa 2025-03; klu 46411. Apakah hasilnya benar? | Kebijakan: bruto Rp8.447.676; tunjangan pph Rp84.476; dtp tunai ke pekerja Rp0; penerimaan bersih Rp7.680.000. Aturan wajib: bruto Rp8.447.676; tunjangan pph Rp84.476; dtp tunai ke pekerja Rp0; penerimaan bersih Rp7.680.000 | |
| 5 | Contoh **SP06-2** — Februari 2026: skenario konflik laten menjadi nyata. Input: pekerja Dewi, K/1; upah sebulan Rp8.000.000; masa 2026-02; klu 14111 (skenario). Apakah hasilnya benar? | Kebijakan: bruto Rp8.447.676; pph21 dtp Rp84.476; dtp tunai ke pekerja Rp0; penerimaan bersih Rp7.680.000. Aturan wajib: bruto Rp8.447.676; pph21 dtp Rp84.476; dtp tunai ke pekerja Rp84.476; penerimaan bersih Rp7.764.476 | |
| 6 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: tidak ada; lainnya `tidak` | |

## SP07 — PT Sentosa Ritel Prima

Perjanjian Kerja Bersama, KLU 47111 (Perdagangan eceran berbagai macam barang yang utamanya makanan, minuman atau tembakau di minimarket), Kota Tangerang; berlaku 2024-02-01 s.d. 2025-12-31. Teks: [SP07.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP07.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C10 (laten)** pada Pasal 52 ayat (6) benar? | Ayat (6) menghapus THR bagi semua pekerja yang hubungan kerjanya berakhir sebelum hari raya. Aturan wajib tetap memberi hak THR kepada pekerja PKWTT yang di-PHK dalam 30 hari sebelum hari raya. Konflik hanya muncul bila ada PHK PKWTT dalam jendela 30 hari itu. Ayat (2)-(4) sama dengan ketentuan minimum. Aturan wajib: Permenaker 6/2016 Pasal 7 ayat (1): pekerja PKWTT yang mengalami PHK terhitung sejak 30 hari sebelum hari raya keagamaan berhak THR (dokumen tidak ada di dataset/01_regulasi; halaman PDF tidak tersedia). Ketentuan ketenagakerjaan, di luar PPh 21, tetapi memengaruhi bruto | |
| 3 | Apakah benar konflik hanya muncul bila syarat tertentu terpenuhi (bukan sekarang)? | Ya | |
| 4 | Contoh **SP07-1** — THR prorata 8 bulan, Maret 2025. Input: pekerja Yoga, TK/0, masa kerja 8 bulan; upah sebulan Rp5.200.000; hari raya Idulfitri 31 Maret 2025. Apakah hasilnya benar? | Kebijakan: thr Rp3.466.666; bruto maret Rp8.918.346; pph21 maret Rp156.071. Aturan wajib: thr Rp3.466.666; bruto maret Rp8.918.346; pph21 maret Rp156.071 | |
| 5 | Contoh **SP07-2** — PHK 25 hari sebelum Natal 2025 (syarat konflik laten terpenuhi). Input: pekerja Yosef, K/0, PKWTT, masa kerja 4 tahun; upah sebulan Rp6.000.000; tanggal phk 2025-11-30; hari raya Natal 2025-12-25. Apakah hasilnya benar? | Kebijakan: thr Rp0; bruto setahun Rp69.194.400; pph masa terakhir -Rp209.080. Aturan wajib: thr Rp6.000.000; bruto setahun Rp75.194.400; pph masa terakhir Rp75.920 | |
| 6 | Contoh **SP07-3** — PHK 45 hari sebelum Natal (syarat tidak terpenuhi). Input: pekerja Yosef, K/0, PKWTT; tanggal phk 2025-11-10. Apakah hasilnya benar? | Kebijakan: thr Rp0. Aturan wajib: thr Rp0 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: tidak ada; lainnya `tidak` | |

## SP08 — PT Kreasi Digital Nusantara

Peraturan Perusahaan (Lampiran Prosedur Penggajian), KLU 62019 (Aktivitas pemrograman komputer lainnya), Jakarta Barat; berlaku 2024-02-01 s.d. 2025-12-31. Teks: [SP08.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP08.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C3 (aktif)** pada Pasal 18 ayat (2) huruf b dan c benar? | Huruf b menghapus plafon biaya jabatan, sehingga pekerja dengan bruto setahun di atas Rp120.000.000 mendapat pengurang berlebih. Huruf c menambah iuran Jaminan Kesehatan pekerja sebagai pengurang, padahal iuran itu tidak termasuk daftar pengurang. Keduanya menghasilkan nilai terlarang bagi pekerja yang ada sekarang. Aturan wajib: PMK 168/2023 Pasal 10 ayat (1)-(2) (PDF hlm. 11-12): biaya jabatan 5% paling banyak Rp6.000.000 setahun / Rp500.000 sebulan; pengurang hanya biaya jabatan, iuran pensiun/JHT/JP yang dibayar pegawai, dan zakat melalui pemberi kerja | |
| 3 | Apakah kebijakan ini sudah menghasilkan nilai yang dilarang bagi pekerja yang ada sekarang? | Ya | |
| 4 | Apakah label konflik **C9 (aktif)** pada Pasal 18 ayat (2) huruf e benar? | Pembulatan ke ribuan terdekat menaikkan PKP Rp1.000 bila sisa >= Rp500. Ayat (3) (pembulatan PPh bulanan ke atas ratusan) bukan konflik karena pembulatan hasil TER x bruto tidak diatur, tetapi perlu konfirmasi pakar. Aturan wajib: PMK 168/2023 Pasal 8 ayat (4) (PDF hlm. 10): Penghasilan Kena Pajak dibulatkan ke bawah hingga ribuan rupiah penuh | |
| 5 | Apakah kebijakan ini sudah menghasilkan nilai yang dilarang bagi pekerja yang ada sekarang? | Ya | |
| 6 | Contoh **SP08-1** — Desember 2024, upah Rp25.000.000 (biaya jabatan melampaui plafon). Input: pekerja Bima, K/1, software engineer; upah sebulan Rp25.000.000; tahun 2024. Apakah hasilnya benar? | Kebijakan: biaya jabatan Rp15.369.000; neto Rp283.375.578; pkp Rp220.376.000; pph setahun Rp27.056.400; pph masa terakhir Rp1.697.550. Aturan wajib: biaya jabatan Rp6.000.000; neto Rp294.184.578; pkp Rp231.184.000; pph setahun Rp28.677.600; pph masa terakhir Rp3.318.750 | |
| 7 | Contoh **SP08-2** — Desember 2024, upah Rp9.000.000 (plafon tidak tercapai; JKN dan pembulatan). Input: pekerja Laras, TK/0; upah sebulan Rp9.000.000; tahun 2024. Apakah hasilnya benar? | Kebijakan: biaya jabatan Rp5.645.160; neto Rp102.938.040; pkp Rp48.938.000; pph setahun Rp2.446.900; pph masa terakhir Rp635.750. Aturan wajib: biaya jabatan Rp5.645.160; neto Rp104.018.040; pkp Rp50.018.000; pph setahun Rp2.500.900; pph masa terakhir Rp689.750 | |
| 8 | Contoh **SP08-3** — Pembulatan PPh bulanan ke atas ratusan (bukan konflik). Input: pekerja Laras, TK/0; masa 2024-02. Apakah hasilnya benar? | Kebijakan: pph21 Rp164.700. Aturan wajib: pph21 Rp164.700 | |
| 9 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E05(a), E08(a); lainnya `tidak` | |

## SP09 — PT Cahaya Farmasi Sejahtera

Peraturan Perusahaan, KLU 21012 (Industri produk farmasi untuk manusia), Kabupaten Bogor; berlaku 2023-08-01 s.d. 2025-07-31. Teks: [SP09.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP09.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C2 (aktif)** pada Pasal 25 ayat (2) benar? | Premi JKK, JKM, dan iuran Jaminan Kesehatan yang dibayar pemberi kerja adalah penghasilan bruto pegawai, baik pada metode PER-16 (2023) maupun TER (2024 dst.). Pasal 25 ayat (2) menghilangkannya dari bruto untuk semua pekerja sejak kebijakan berlaku. Aturan wajib: PMK 168/2023 Pasal 5 ayat (3) huruf d dan e (PDF hlm. 9); untuk Juli-Desember 2023: PER-16/PJ/2016 Lampiran (PDF hlm. 21, teks OCR) yang memasukkan premi JKK, JKM, dan JPK ke bruto | |
| 3 | Apakah kebijakan ini sudah menghasilkan nilai yang dilarang bagi pekerja yang ada sekarang? | Ya | |
| 4 | Contoh **SP09-1** — Agustus 2023 (metode disetahunkan). Input: pekerja Hendra, K/0; upah sebulan Rp9.000.000; masa 2023-08. Apakah hasilnya benar? | Kebijakan: bruto Rp9.000.000; pph21 Rp170.250. Aturan wajib: bruto Rp9.435.600; pph21 Rp190.937 | |
| 5 | Contoh **SP09-2** — Maret 2024 (TER kategori A). Input: pekerja Hendra, K/0; upah sebulan Rp9.000.000; masa 2024-03. Apakah hasilnya benar? | Kebijakan: bruto Rp9.000.000; pph21 Rp157.500. Aturan wajib: bruto Rp9.435.600; pph21 Rp165.123 | |
| 6 | Contoh **SP09-3** — Desember 2024: Masa Pajak Terakhir. Input: pekerja Hendra, K/0; upah sebulan Rp9.000.000; tahun 2024. Apakah hasilnya benar? | Kebijakan: bruto Rp108.000.000; pkp Rp40.860.000; pph setahun Rp2.043.000; pph masa terakhir Rp310.500. Aturan wajib: bruto Rp113.227.200; pkp Rp45.825.000; pph setahun Rp2.291.250; pph masa terakhir Rp474.897 | |
| 7 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E03(a), E04(a), E05(a), E08(a); lainnya `tidak` | |

## SP10 — PT Kemas Plastindo Jaya

Perjanjian Kerja Bersama, KLU 22220 (Industri barang dari plastik untuk pengemasan), Kabupaten Sidoarjo; berlaku 2024-04-01 s.d. 2026-03-31. Teks: [SP10.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP10.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C7 (aktif)** pada Pasal 41 ayat (1), (3), dan (5) benar? | Pembagian iuran ditetapkan peraturan dan tidak dapat dialihkan dengan kesepakatan. Porsi pekerja JHT (3%) dan JKN (2%) melebihi ketentuan. Dampak PPh 21: bruto turun (porsi JKN pemberi kerja yang masuk bruto hanya 3%) dan pengurang naik (JHT pekerja 3%). Ayat (5) menegaskan bahwa ini kesepakatan, tetapi kesepakatan tidak mengesampingkan aturan wajib. Aturan wajib: PP 46/2015 Pasal 16 ayat (1) (PDF hlm. 11): JHT 3,7% pemberi kerja dan 2% pekerja; Perpres 82/2018 Pasal 30 ayat (2) sebagaimana diubah Perpres 75/2019 Pasal I angka 2 (PDF hlm. 2): JKN 4% pemberi kerja dan 1% peserta | |
| 3 | Apakah kebijakan ini sudah menghasilkan nilai yang dilarang bagi pekerja yang ada sekarang? | Ya | |
| 4 | Contoh **SP10-1** — Maret 2025: pembagian iuran dan bruto. Input: pekerja Joko, K/2; upah sebulan Rp7.500.000; masa 2025-03. Apakah hasilnya benar? | Kebijakan: iuran jht pekerja Rp225.000; iuran jkn pekerja Rp150.000; jkn pemberi kerja Rp225.000; bruto Rp7.788.000; pph21 Rp77.880; penerimaan bersih Rp6.972.120. Aturan wajib: iuran jht pekerja Rp150.000; iuran jkn pekerja Rp75.000; jkn pemberi kerja Rp300.000; bruto Rp7.863.000; pph21 Rp78.630; penerimaan bersih Rp7.121.370 | |
| 5 | Contoh **SP10-2** — Desember 2025: Masa Pajak Terakhir. Input: pekerja Joko, K/2; upah sebulan Rp7.500.000; tahun 2025. Apakah hasilnya benar? | Kebijakan: bruto Rp93.456.000; neto Rp85.183.200; pkp Rp17.683.000; pph setahun Rp884.150; pph masa terakhir Rp27.470. Aturan wajib: bruto Rp94.356.000; neto Rp86.938.200; pkp Rp19.438.000; pph setahun Rp971.900; pph masa terakhir Rp106.970 | |
| 6 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E08(a), E12(a); lainnya `tidak` | |

## SP11 — PT Bumi Konstruksi Persada

Perjanjian Kerja Bersama, KLU 41012 (Konstruksi gedung perkantoran), Kota Surabaya; berlaku 2025-01-01 s.d. 2026-12-31. Teks: [SP11.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP11.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah label konflik **C8 (aktif)** pada Pasal 50 ayat (1)-(2) benar? | Iuran JP dan JKN dihitung dari seluruh upah. Bagi pekerja berupah di atas batas, iuran JP pekerja (pengurang) dan iuran JKN pemberi kerja (bruto) lebih besar dari yang diwajibkan; keduanya mengubah PPh 21. Aturan wajib: PP 45/2015 Pasal 28 ayat (3) (PDF hlm. 20) dan Pasal 29 (PDF hlm. 21) jo. Surat BPJS TK B/1387/022024 dan B/726/022025 (teks surat hlm. 1): batas upah JP Rp10.042.300 (Jan-Feb 2025) dan Rp10.547.400 (mulai Maret 2025); Perpres 75/2019 Pasal I angka 3 (Pasal 32 ayat (1), PDF hlm. 3): batas upah JKN Rp12.000.000 | |
| 3 | Apakah kebijakan ini sudah menghasilkan nilai yang dilarang bagi pekerja yang ada sekarang? | Ya | |
| 4 | Apakah label konflik **C5 (laten)** pada Pasal 51 ayat (2) benar? | Bulan berhenti bekerja adalah Masa Pajak Terakhir: PPh dihitung ulang dengan tarif Pasal 17 atas penghasilan setahun atau bagian tahun, dan kelebihan wajib dikembalikan pemotong. Ayat (2) tetap memakai TER. Konflik hanya muncul bila ada pekerja yang berhenti sebelum Desember. Aturan wajib: PMK 168/2023 Pasal 1 definisi Masa Pajak Terakhir (PDF hlm. 4), Pasal 15 ayat (1) huruf b dan ayat (2) (PDF hlm. 15-16), Pasal 21 ayat (1) (PDF hlm. 21) | |
| 5 | Apakah benar konflik hanya muncul bila syarat tertentu terpenuhi (bukan sekarang)? | Ya | |
| 6 | Contoh **SP11-1** — April 2025: iuran JP dan JKN tanpa batas upah. Input: pekerja Agus, site engineer, K/2; upah sebulan Rp18.000.000; masa 2025-04; jkk 1,27% (risiko tinggi). Apakah hasilnya benar? | Kebijakan: iuran jp pekerja Rp180.000; iuran jkn pekerja Rp180.000; jkn pemberi kerja Rp720.000; bruto Rp19.002.600; pph21 Rp1.520.208. Aturan wajib: iuran jp pekerja Rp105.474; iuran jkn pekerja Rp120.000; jkn pemberi kerja Rp480.000; bruto Rp18.762.600; pph21 Rp1.501.008 | |
| 7 | Contoh **SP11-2** — Desember 2025: Masa Pajak Terakhir. Input: pekerja Agus, K/2; upah sebulan Rp18.000.000; tahun 2025. Apakah hasilnya benar? | Kebijakan: bruto Rp228.031.200; neto Rp215.551.200; pkp Rp148.051.000; pph setahun Rp16.207.650; pph masa terakhir -Rp514.638. Aturan wajib: bruto Rp225.151.200; neto Rp213.575.614; pkp Rp146.075.000; pph setahun Rp15.911.250; pph masa terakhir -Rp599.838 | |
| 8 | Contoh **SP11-3** — Pegawai berhenti 30 Juni 2025 (konflik laten C5 terpenuhi). Input: pekerja Rudi, TK/0, resign 2025-06-30; upah sebulan Rp9.500.000. Apakah hasilnya benar? | Kebijakan: pph21 juni Rp200.583; pengembalian ke pegawai Rp0. Aturan wajib: pph21 juni -Rp929.715; pph setahun Rp73.200; pengembalian ke pegawai Rp929.715 | |
| 9 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E08(a), E12(a); lainnya `tidak` | |

## SP12 — PT Nusa Teknologi Pembayaran

Peraturan Perusahaan, KLU 63122 (Portal web dan/atau platform digital dengan tujuan komersial), Jakarta Selatan; berlaku 2024-02-01 s.d. 2025-12-31. Teks: [SP12.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP12.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah benar **tidak ada konflik** (kontrol negatif)? | Tidak ada konflik: pilihan yang diserahkan ke perusahaan | |
| 3 | Contoh **SP12-1** — Februari 2024: tunjangan PPh gross-up dengan TER. Input: pekerja Nadia, TK/0; upah sebulan Rp20.000.000; masa 2024-02. Apakah hasilnya benar? | Kebijakan: tunjangan pph Rp2.036.175; bruto Rp22.624.175; pph21 Rp2.036.175. Aturan wajib: tunjangan pph Rp2.036.175; bruto Rp22.624.175; pph21 Rp2.036.175 | |
| 4 | Contoh **SP12-2** — Desember 2024: gross-up pada Masa Pajak Terakhir. Input: pekerja Nadia, TK/0; upah sebulan Rp20.000.000; tahun 2024. Apakah hasilnya benar? | Kebijakan: tunjangan desember Rp2.495.025; pph setahun Rp24.892.950. Aturan wajib: tunjangan desember Rp2.495.025; pph setahun Rp24.892.950 | |
| 5 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E05(a), E08(a); lainnya `tidak` | |

## SP13 — PT Kencana Pelayaran Nusantara

Perjanjian Kerja Bersama, KLU 50131 (Angkutan laut dalam negeri liner untuk barang), Kota Surabaya (pangkalan Tanjung Perak); berlaku 2023-06-01 s.d. 2025-05-31. Teks: [SP13.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP13.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah benar **tidak ada konflik** (kontrol negatif)? | Tidak ada konflik: pilihan yang diserahkan ke perusahaan | |
| 3 | Contoh **SP13-1** — Februari 2024: PPh ditanggung perusahaan (kenikmatan, full gross-up). Input: pekerja Harun, mualim I, K/3; upah sebulan Rp22.000.000; masa 2024-02. Apakah hasilnya benar? | Kebijakan: pph ditanggung Rp2.257.457; bruto Rp25.082.857. Aturan wajib: pph ditanggung Rp2.257.457; bruto Rp25.082.857 | |
| 4 | Contoh **SP13-2** — Desember 2024: Masa Pajak Terakhir dengan PPh ditanggung. Input: pekerja Harun, mualim I, K/3; upah sebulan Rp22.000.000; tahun 2024. Apakah hasilnya benar? | Kebijakan: pph ditanggung desember Rp1.537.823; pph setahun Rp26.369.850. Aturan wajib: pph ditanggung desember Rp1.537.823; pph setahun Rp26.369.850 | |
| 5 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E02(b), E03(a), E04(a), E05(a), E08(a); lainnya `tidak` | |

## SP14 — PT Rajut Indah Garmenindo

Perjanjian Kerja Bersama, KLU 14111 (Industri pakaian jadi (konveksi) dari tekstil (tercantum Lampiran A PMK 10/2025 dan PMK 105/2025)), Kabupaten Boyolali; berlaku 2025-01-01 s.d. 2026-12-31. Teks: [SP14.md](../../dataset/10_kebijakan_perusahaan/sintetis/SP14.md)

| No | Pertanyaan | Penilaian Claude | Setuju? / koreksi |
|---|---|---|---|
| 1 | Apakah dokumen ini realistis untuk perusahaan sejenis (bahasa, isi, besaran)? | Ya, disusun meniru PP/PKB nyata | |
| 2 | Apakah benar **tidak ada konflik** (kontrol negatif)? | Tidak ada konflik: pilihan yang diserahkan ke perusahaan | |
| 3 | Contoh **SP14-1** — THR 1,5 bulan, Maret 2025. Input: pekerja Ani, operator jahit, TK/1, masa kerja 3 tahun; upah sebulan Rp5.400.000; masa 2025-03. Apakah hasilnya benar? | Kebijakan: thr Rp8.100.000; bruto Rp13.746.780; pph21 dtp Rp687.339; dtp tunai ke pekerja Rp687.339. Aturan wajib: thr minimum Rp5.400.000; thr dibayar Rp8.100.000; bruto Rp13.746.780; pph21 dtp Rp687.339; dtp tunai ke pekerja Rp687.339 | |
| 4 | Contoh **SP14-2** — THR prorata 6 bulan, Maret 2025. Input: pekerja Rio, TK/1, masa kerja 6 bulan; upah sebulan Rp5.400.000; masa 2025-03. Apakah hasilnya benar? | Kebijakan: thr Rp4.050.000; bruto Rp9.696.780; pph21 dtp Rp193.935. Aturan wajib: thr minimum Rp2.700.000; thr dibayar Rp4.050.000; bruto Rp9.696.780; pph21 dtp Rp193.935 | |
| 5 | Contoh **SP14-3** — PHK 15 hari sebelum Natal 2025. Input: pekerja Maria, TK/1, PKWTT, masa kerja 2 tahun; tanggal phk 2025-12-10. Apakah hasilnya benar? | Kebijakan: thr Rp8.100.000. Aturan wajib: thr minimum Rp5.400.000; thr dibayar Rp8.100.000 | |
| 6 | Apakah label dampak E01–E12 benar? (a nilai fakta berubah, b aturan pemenang berubah, c menjadi berkonflik) | Terdampak: E06(b), E07(a), E08(a), E09(a), E11(b), E12(a); lainnya `tidak` | |

## Pertanyaan umum

1. Apakah ada jenis konflik yang sering Anda temui di PP/PKB nyata tetapi belum terwakili di SP01–SP14?

   Jawaban:

2. SP13: apakah PPh 21 yang ditanggung pemberi kerja diperlakukan sebagai kenikmatan (full gross-up) juga untuk Juli–Desember 2023, atau baru sejak 2024?

   Jawaban:

3. SP08 Pasal 18 ayat (3): apakah membulatkan PPh bulanan ke atas ratusan rupiah dapat diterima, mengingat pembulatan hasil TER tidak diatur?

   Jawaban:

## Hasil

- [ ] Disetujui
- [ ] Disetujui dengan perubahan (tulis di atas)
- [ ] Perlu revisi

Status: menunggu
