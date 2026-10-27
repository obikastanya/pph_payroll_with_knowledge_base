# Kebijakan perusahaan sintetis (SP01–SP14)

> **DOKUMEN FIKTIF UNTUK PENELITIAN.** Semua perusahaan, nomor dokumen, nomor pengesahan, dan penanda tangan rekaan. Disusun 2026-10-27 sebagai materi sintetis GT5 untuk mengisi jenis konflik yang tidak ada di dokumen nyata (`../kandidat.csv`). Hasil tinjauan dan putusan tercatat di [review/company_policies/sintetis.review.md](../../../review/company_policies/sintetis.review.md) dan bagian *Putusan* di bawah.

## Isi

| Berkas | Isi |
|---|---|
| `SPxx.md` | Teks dokumen: kutipan Peraturan Perusahaan atau PKB (1–4 pasal inti ditambah pasal masa berlaku, total 2–5 pasal) |
| `SPxx.json` | Metadata, `pasal[]` (kutipan sama persis dengan `.md`), `konflik[]`, `contoh[]` (contoh hitung), `label_dampak[]` (E01–E12) |
| `INDEX.csv` | Satu baris per kebijakan: KLU, masa berlaku, kode dan status konflik, peristiwa pemicu, peristiwa yang berdampak |

## Ringkasan konflik

| ID | Perusahaan (fiktif) | KLU | Berlaku | Konflik | Status | Pemicu |
|---|---|---|---|---|---|---|
| SP01 | PT Lintas Gudang Nusantara | 52101 | 2023-04-01 – 2025-03-31 | C6 batas upah JP Rp9.559.600 dikunci | terpicu | E05 |
| SP02 | PT Presisi Komponen Otomotif | 29300 | 2023-01-01 – 2024-12-31 | C5 metode disetahunkan dikunci | terpicu | E03+E04 |
| SP03 | PT Samudra Biru Hospitality | 55110 | 2025-03-01 – 2026-12-31 | C4 DTP ditahan perusahaan | terpicu | E10 |
| SP04 | PT Arunika Energi Mandiri | 09100 | 2023-01-01 – 2024-12-31 | C1 apartemen manajer "bukan penghasilan" | terpicu | E02 |
| SP05 | PT Benang Sutra Lestari | 13112 | 2024-07-01 – 2026-06-30 | C6 tarif JKK 0,54% dikunci | terpicu | E07 |
| SP06 | PT Mitra Niaga Sandang | 46411 | 2025-01-01 – 2026-12-31 | C4 DTP ditukar dengan tunjangan pajak | laten | – |
| SP07 | PT Sentosa Ritel Prima | 47111 | 2024-02-01 – 2025-12-31 | C10 THR hilang bila PHK sebelum hari raya | laten | – |
| SP08 | PT Kreasi Digital Nusantara | 62019 | 2024-02-01 – 2025-12-31 | C3 biaya jabatan tanpa plafon, JKN sebagai pengurang; C9 PKP dibulatkan ke terdekat | aktif; aktif | – |
| SP09 | PT Cahaya Farmasi Sejahtera | 21012 | 2023-08-01 – 2025-07-31 | C2 premi JKK/JKM/JKN tidak masuk bruto | aktif | – |
| SP10 | PT Kemas Plastindo Jaya | 22220 | 2024-04-01 – 2026-03-31 | C7 pekerja menanggung JHT 3% dan JKN 2% | aktif | – |
| SP11 | PT Bumi Konstruksi Persada | 41012 | 2025-01-01 – 2026-12-31 | C8 JP dan JKN tanpa batas upah; C5 bulan berhenti tetap TER | aktif; laten | – |
| SP12 | PT Nusa Teknologi Pembayaran | 63122 | 2024-02-01 – 2025-12-31 | tidak ada (gross-up) | kontrol negatif | – |
| SP13 | PT Kencana Pelayaran Nusantara | 50131 | 2023-06-01 – 2025-05-31 | tidak ada (PPh ditanggung perusahaan, mes awak kapal) | kontrol negatif | – |
| SP14 | PT Rajut Indah Garmenindo | 14111 | 2025-01-01 – 2026-12-31 | tidak ada (THR 1,5 bulan, DTP diteruskan) | kontrol negatif | – |

Jumlah per jenis: C1 1, C2 1, C3 1, C4 2, C5 2, C6 2, C7 1, C8 1, C9 1, C10 1 (13 konflik). Per status: aktif 5, laten 3, terpicu 5. Kontrol negatif 3. Bersama konflik nyata (PKB WIKA C4 laten, Perusahaan X/K1 C1 dan C6), setiap kode C1–C10 punya paling sedikit satu contoh.

Beberapa kebijakan sengaja memuat klausul yang **tampak** berkonflik tetapi tidak: makan siang seluruh pekerja (SP04), pembulatan PPh bulanan ke atas ratusan pada Masa 2024 (SP08 Pasal 18 ayat (3), belum diatur regulasi; untuk Masa 2025 dan Masa Pajak Terakhir lihat *Putusan* butir 3), mes awak kapal (SP13). Konflik nyata PKB yang tersisa setelah tinjauan klausul dicatat di `../klausul/README.md`.

## Label dampak (RQ4)

Untuk setiap peristiwa uji E01–E12, `label_dampak[]` berisi `terdampak` (`ya`/`tidak`), `tipe`, dan `alasan`:

- **a — nilai fakta berubah:** nilai yang dipakai atau diatur kebijakan berubah menurut aturan wajib (misalnya batas JP yang dirujuk secara dinamis). Termasuk di sini peristiwa yang hanya mengubah nilai wajib bagi fakta yang sudah berkonflik sebelumnya (misalnya SP01/E08, SP11/E08): konfliknya tidak baru, hanya besar selisihnya;
- **b — aturan pemenang berubah:** untuk fakta yang diatur kebijakan, aturan yang menentukan nilai akhir berpindah (misalnya DTP mengambil alih beban PPh 21), tanpa konflik;
- **c — menjadi berkonflik:** kebijakan menetapkan nilai yang dilarang aturan wajib setelah peristiwa itu, padahal sebelum peristiwa tidak berkonflik (termasuk konflik yang muncul lagi setelah sempat berakhir, misalnya SP05/E09 dan SP03/E11). Perpindahan aturan pemenang yang terjadi bersamaan sudah tercakup di tipe c, sehingga tidak diberi tipe b.

Aturan pelabelan: peristiwa dihitung hanya bila tanggal mulai berlakunya jatuh di dalam masa berlaku kebijakan. Peristiwa yang berlaku sebelum kebijakan mulai dianggap keadaan awal saat kebijakan disusun (`tidak`). Label hanya menilai klausul kebijakan, bukan seluruh penggajian perusahaan. Total label `ya`: 46 dari 168 (tipe a 34, b 5, c 8; label SP13/E02 bertipe a dan b sekaligus).

## Contoh hitung

38 contoh (2–3 per kebijakan). Setiap contoh memuat `input`, `hasil_menurut_kebijakan`, `hasil_menurut_aturan_wajib`, `langkah` (setiap langkah dengan rujukan pasal dan halaman PDF), dan `cek_aritmetika` (ekspresi yang dapat dievaluasi ulang). 439 ekspresi dihitung ulang dengan pecahan eksak: **0 selisih**; setiap tarif TER yang disebut di `langkah` dicocokkan ulang dengan `tables/ter_bulanan.csv` (28 penyebutan, semua cocok), dan setiap hasil gross-up serta perhitungan Masa Pajak Terakhir dihitung ulang dengan iterasi tersendiri.

Asumsi yang dipakai di semua contoh:

- Bruto = upah + premi JKK + premi JKM + iuran JKN bagian pemberi kerja (+ penghasilan lain). Pengurang Masa Pajak Terakhir = biaya jabatan + iuran JHT 2% + JP 1% bagian pekerja.
- Tingkat risiko JKK per perusahaan tertulis di kebijakan atau di `input`. JKN dibatasi Rp12.000.000; JP mengikuti batas per Maret dari `tables/bpjs.csv`.
- Pembulatan hasil TER x bruto mengikuti tafsir K1 (`docs/spesifikasi/tafsir_perhitungan.md`): Masa 2024 pecahan dibuang; mulai Masa Januari 2025 dibulatkan ke rupiah penuh terdekat, 0,50 ke atas (PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3), PDF hlm. 106). Aturan yang sama dipakai untuk PPh DTP dan untuk persamaan *gross-up* (titik tetap terkecil, tafsir K3). Pembagian /12 pada metode disetahunkan 2023 dibulatkan ke bawah (tafsir K2). PKP dibulatkan ke bawah hingga ribuan (PMK 168/2023 Pasal 8 ayat (4), PDF hlm. 10).
- Gross-up dan PPh ditanggung pemberi kerja dihitung *full gross-up* seperti PMK 168/2023 Lampiran huruf B Bagian Kedua contoh I.4 (PDF hlm. 44): PPh yang ditanggung pemberi kerja adalah kenikmatan dan objek PPh 21. Desember dicari dengan iterasi sampai tunjangan = PPh Masa Pajak Terakhir. Pada masa DTP, PPh 21 pegawai yang memenuhi syarat ditanggung pemerintah (PMK 168/2023 Pasal 7 huruf h, PDF hlm. 10) dan nilainya wajib dibayar tunai walaupun pemberi kerja memberi tunjangan PPh atau menanggung PPh (PMK 10/2025 Pasal 5 ayat (1)-(2), PDF hlm. 6).
- Pegawai yang berhenti di tengah tahun: neto tidak disetahunkan, PTKP penuh, plafon biaya jabatan Rp500.000 x jumlah bulan.
- THR: Permenaker 6/2016 Pasal 2 ayat (1), Pasal 3 ayat (1), dan Pasal 7 ayat (1) dirujuk tanpa halaman PDF karena teksnya tidak disimpan di `dataset/01_regulasi`.
- Pesangon, uang pisah, UPMK, dan UPH dikenai PPh 21 final PP 68/2009 dan tidak masuk perhitungan TER/Pasal 17; tidak ada contoh SP yang menghitungnya.
- Hari raya: Idulfitri 31 Maret 2025, Natal 25 Desember 2025.

## Putusan

1. **PPh ditanggung pemberi kerja sebagai kenikmatan, Juli–Desember 2023 (SP13, E02).** Pemotongan atas natura dan kenikmatan berlaku mulai Masa Pajak Juli 2023; natura/kenikmatan Januari–Juni 2023 dikecualikan dari pemotongan dan dilaporkan sendiri oleh penerima (PMK 66/2023 Pasal 23 ayat (1) dan (4), Pasal 24, PDF hlm. 17-18). PPh 21 yang ditanggung pemberi kerja adalah kenikmatan (PMK 168/2023 Lampiran huruf B contoh I.4, PDF hlm. 44), jadi untuk SP13 masuk bruto dengan *full gross-up* mulai Masa Juli 2023, masih dengan metode disetahunkan sampai Desember 2023 dan dengan TER mulai Januari 2024. Karena itu label SP13/E02 menjadi tipe a dan b.
2. **Keringanan JKK menurunkan bruto (SP05, SP14).** Ya. Yang masuk bruto adalah iuran JKK yang dibayarkan pemberi kerja (PMK 168/2023 Pasal 5 ayat (3) huruf d, PDF hlm. 9), dan besarnya iuran itu ditetapkan PP 7/2025 Pasal 4 ayat (1) (PDF hlm. 4; iuran Februari–Juli 2025) dan PP 36/2025 Pasal 10A (PDF hlm. 4; diperpanjang sampai iuran Januari 2026, surut sejak Agustus 2025). Syaratnya: industri padat karya tertentu (Pasal 3 ayat (4)), paling sedikit 50 peserta aktif (Pasal 3 ayat (3)), lolos verifikasi BPJS Ketenagakerjaan (Pasal 5 ayat (1)-(2)), dan iuran sampai Januari 2025 sudah lunas (Pasal 6 ayat (2)). SP05 (1.350 pekerja) dan SP14 (2.400 pekerja) memenuhinya.
3. **Pembulatan PPh bulanan ke atas ratusan (SP08 Pasal 18 ayat (3)).** Untuk Masa 2024 bukan konflik: pembulatan hasil TER x bruto belum diatur, selisihnya di bawah Rp100, dan terkoreksi di Masa Pajak Terakhir. Mulai Masa Januari 2025 PPh pada bukti potong wajib dibulatkan ke rupiah penuh terdekat (PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3), PDF hlm. 106; Pasal 130 huruf a, PDF hlm. 107), sehingga ayat (3) menyimpang untuk Masa 2025 (kebijakan berlaku sampai Desember 2025). Pada Masa Pajak Terakhir PPh adalah selisih eksak (PMK 168/2023 Pasal 15 ayat (1) huruf b, PDF hlm. 15) dan pembulatan ke atas menimbulkan kelebihan potong yang wajib dikembalikan (Pasal 21 ayat (1), PDF hlm. 21). Kedua bagian dicatat di bawah label C9 SP08 yang sudah ada; PER-11/PJ/2025 bukan peristiwa E01–E12, jadi tidak ada label dampak baru. Hasil kebijakan SP08-1 dan SP08-2 kini memakai PPh bulanan yang sudah dibulatkan (Rp2.305.400 dan Rp164.700).
4. **Kelebihan potong saat PPh ditanggung atau di-*gross-up*.** Mengikuti tafsir K3 butir 2 (`docs/spesifikasi/tafsir_perhitungan.md`): tunjangan/PPh ditanggung di Masa Pajak Terakhir adalah titik tetap terkecil dari PPh setahun dikurangi PPh masa sebelumnya, dan bila hasilnya lebih potong nilainya 0 (tidak ada kenikmatan negatif). Kelebihan potong diselesaikan menurut PMK 168/2023 Pasal 21 (PDF hlm. 21). Contoh SP12-2 dan SP13-2 tidak lebih potong. Pada metode *gross* (SP07-2, SP11-2, SP11-3) kelebihan wajib dikembalikan kepada pegawai paling lambat akhir bulan berikutnya (Pasal 21 ayat (1)).
5. **Pembulatan 2025 dalam contoh.** Contoh dengan masa 2025–2026 kini memakai pembulatan rupiah terdekat (tafsir K1): SP05-2 PPh wajib Rp28.757 (sebelumnya Rp28.756), SP05-3 PPh dipotong Januari–November Rp316.401 dan masa terakhir Rp163.549 (sebelumnya Rp316.391 dan Rp163.559), SP06-1/SP06-2 tunjangan PPh dan PPh Rp84.477 dengan bruto Rp8.447.677 dan penerimaan bersih wajib SP06-2 Rp7.764.477, SP14-2 PPh DTP Rp193.936. Contoh masa 2024 tidak berubah.
6. **Koreksi label setelah pemeriksaan.** SP01/E08 c menjadi a (konflik C6 sudah ada sejak E05); SP02/E04 b,c menjadi c (tipe b didefinisikan tanpa konflik); SP13/E02 b menjadi a,b (lihat butir 1).
