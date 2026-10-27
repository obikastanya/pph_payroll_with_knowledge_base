# Kebijakan perusahaan sintetis (SP01–SP14)

> **DOKUMEN FIKTIF UNTUK PENELITIAN.** Semua perusahaan, nomor dokumen, nomor pengesahan, dan penanda tangan rekaan. Disusun 2026-10-27 sebagai materi sintetis GT5 untuk mengisi jenis konflik yang tidak ada di dokumen nyata (`../kandidat.csv`). Status tinjauan: **menunggu** ([review/company_policies/sintetis.review.md](../../../review/company_policies/sintetis.review.md)).

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

Beberapa kebijakan sengaja memuat klausul yang **tampak** berkonflik tetapi tidak: makan siang seluruh pekerja (SP04), pembulatan PPh bulanan ke atas ratusan (SP08 Pasal 18 ayat (3), tidak diatur regulasi), mes awak kapal (SP13).

## Label dampak (RQ4)

Untuk setiap peristiwa uji E01–E12, `label_dampak[]` berisi `terdampak` (`ya`/`tidak`), `tipe`, dan `alasan`:

- **a — nilai fakta berubah:** nilai yang dipakai atau diatur kebijakan berubah menurut aturan wajib (misalnya batas JP yang dirujuk secara dinamis), dan kebijakan tetap sah;
- **b — aturan pemenang berubah:** untuk fakta yang diatur kebijakan, aturan yang menentukan nilai akhir berpindah (misalnya DTP mengambil alih beban PPh 21), tanpa konflik;
- **c — menjadi berkonflik:** kebijakan menetapkan nilai yang dilarang aturan wajib setelah peristiwa itu.

Aturan pelabelan: peristiwa dihitung hanya bila tanggal mulai berlakunya jatuh di dalam masa berlaku kebijakan. Peristiwa yang berlaku sebelum kebijakan mulai dianggap keadaan awal saat kebijakan disusun (`tidak`). Label hanya menilai klausul kebijakan, bukan seluruh penggajian perusahaan. Total label `ya`: 46 dari 168 (tipe a 32, b 6, c 9; label SP02/E04 bertipe b dan c sekaligus).

## Contoh hitung

38 contoh (2–3 per kebijakan). Setiap contoh memuat `input`, `hasil_menurut_kebijakan`, `hasil_menurut_aturan_wajib`, `langkah` (setiap langkah dengan rujukan pasal dan halaman PDF), dan `cek_aritmetika` (ekspresi yang dapat dievaluasi ulang). 435 ekspresi dihitung ulang dengan pecahan eksak: **0 selisih**.

Asumsi yang dipakai di semua contoh:

- Bruto = upah + premi JKK + premi JKM + iuran JKN bagian pemberi kerja (+ penghasilan lain). Pengurang Masa Pajak Terakhir = biaya jabatan + iuran JHT 2% + JP 1% bagian pekerja.
- Tingkat risiko JKK per perusahaan tertulis di kebijakan atau di `input`. JKN dibatasi Rp12.000.000; JP mengikuti batas per Maret dari `tables/bpjs.csv`.
- Hasil TER x bruto dibulatkan ke bawah ke rupiah penuh. Pembulatan ini **tidak diatur** PP 58/2023 maupun PMK 168/2023 (asumsi implementasi). Pembagian /12 pada metode disetahunkan juga dibulatkan ke bawah.
- Gross-up dan PPh ditanggung pemberi kerja dihitung *full gross-up* seperti PMK 168/2023 Lampiran B contoh I.4 (PDF hlm. 44). Desember dicari dengan iterasi sampai tunjangan = PPh Masa Pajak Terakhir.
- Pegawai yang berhenti di tengah tahun: neto tidak disetahunkan, PTKP penuh, plafon biaya jabatan Rp500.000 x jumlah bulan.
- THR: Permenaker 6/2016 (Pasal 3 dan Pasal 7) **tidak ada** di `dataset/01_regulasi`, jadi rujukannya tanpa halaman PDF.
- Hari raya: Idulfitri 31 Maret 2025, Natal 25 Desember 2025.

## Hal yang perlu diputuskan pakar

1. Perlakuan PPh ditanggung pemberi kerja sebagai kenikmatan untuk Juli–Desember 2023 (SP13, E02).
2. Apakah keringanan JKK (E07/E09) memang menurunkan bruto PPh 21 dalam praktik (SP05, SP14).
3. Apakah pembulatan PPh bulanan ke atas ratusan (SP08) dianggap pilihan sah.
