# Research Plan — Kalkulator PPh Pasal 21 Berbasis Knowledge Base Dua Lapis Berversi Waktu

> **Status:** rencana final v1 (2026-10-01) untuk tugas mata kuliah Knowledge-Based System (S2 Informatika).
> **Dokumen induk:** [proposal_kb_pph21_kebijakan_perusahaan_payroll_v1.md](proposal_kb_pph21_kebijakan_perusahaan_payroll_v1.md). Rencana ini **menggantikan** bagian metode, evaluasi, dan novelty pada proposal. Fokus novelty bergeser: inti sekarang KB dua lapis berversi waktu dengan resolusi konflik, sedangkan analisis gross-up di bawah TER menjadi sub-temuan.
> **Lokasi aset:** semua data ada di [dataset/](dataset/), dengan manifest di setiap subfolder (§8).

---

## Daftar Isi

0. [Ringkasan](#0-ringkasan)
1. [Keputusan Desain yang Dikunci](#1-keputusan-desain-yang-dikunci)
2. [Masalah, Bukti Awal, dan Motivasi](#2-masalah-bukti-awal-dan-motivasi)
3. [Pertanyaan Penelitian dan Hipotesis](#3-pertanyaan-penelitian-dan-hipotesis)
4. [Tujuan dan Ruang Lingkup](#4-tujuan-dan-ruang-lingkup)
5. [Spesifikasi Input Kalkulator](#5-spesifikasi-input-kalkulator)
6. [Rancangan Knowledge Base dan Inference Engine](#6-rancangan-knowledge-base-dan-inference-engine)
7. [Spesifikasi Output](#7-spesifikasi-output)
8. [Data dan Aset](#8-data-dan-aset)
9. [Validasi Tanpa SME: Piramida Oracle](#9-validasi-tanpa-sme-piramida-oracle)
10. [Pembanding (Baseline)](#10-pembanding-baseline)
11. [Metrik Evaluasi](#11-metrik-evaluasi)
12. [Desain Eksperimen](#12-desain-eksperimen)
13. [Novelty Akademis](#13-novelty-akademis)
14. [Arsitektur dan Paket Kerja](#14-arsitektur-dan-paket-kerja)
15. [Risiko, Ancaman Validitas, dan Etika](#15-risiko-ancaman-validitas-dan-etika)
16. [Daftar Luaran](#16-daftar-luaran)
17. [Referensi](#17-referensi)
- [Lampiran A — Inventaris Aturan Lapisan Regulasi](#lampiran-a--inventaris-aturan-lapisan-regulasi)
- [Lampiran B — Skenario Perubahan](#lampiran-b--skenario-perubahan)
- [Lampiran C — Contoh I/O](#lampiran-c--contoh-io)
- [Lampiran D — Temuan Audit xlsx Perusahaan X](#lampiran-d--temuan-audit-xlsx-perusahaan-x)

---

## 0. Ringkasan

Penelitian ini membangun **kalkulator PPh Pasal 21 pegawai tetap** dengan pengetahuan yang sepenuhnya berada di **knowledge base (KB) deklaratif**, bukan di kode. KB terdiri atas dua lapis:

1. **Lapisan regulasi**: UU PPh/HPP, PMK 101/2016, PER-16/PJ/2016, PP 58/2023, PMK 168/2023, PMK 66/2023, regulasi PPh 21 DTP, dan parameter BPJS.
2. **Lapisan kebijakan perusahaan**: komponen gaji, prorata, metode gross/gross-up, jadwal THR/bonus, dan sebagainya.

Setiap aturan **berversi waktu**, yaitu memiliki masa berlaku dan versi KB. Karena itu satu mesin yang sama dapat menghitung tahun pajak 2023 (rezim disetahunkan PER-16) maupun 2024–2026 (rezim TER) tanpa perubahan kode.

Mesin inferensi berupa *forward chaining* dengan tiga komponen tambahan:
- **resolusi konflik berbasis asas hukum** (*lex superior*, *lex specialis*, *lex posterior*) antara regulasi dan kebijakan perusahaan;
- **penyelesai titik tetap** untuk definisi melingkar seperti gross-up;
- **fasilitas penjelasan** yang menautkan setiap angka ke aturan dan pasal sumbernya.

Evaluasi **tidak memakai SME dan tidak memakai LLM**. Kebenaran ditetapkan melalui *piramida oracle*:
1. contoh resmi regulasi;
2. derivasi pasal dengan *differential testing* dan adjudikasi;
3. *metamorphic/property-based testing*;
4. verifikasi formal dengan Z3.

Kalkulator yang sudah ada (spreadsheet kantor, library open source, kalkulator online) **diperlakukan sebagai sistem yang diuji, bukan sebagai kebenaran**.

Karena ini ranah keuangan, seluruh sistem tunduk pada **Kontrak Presisi** (§6.9):
- aritmetika eksak (rupiah `int`, tarif `Decimal`, tanpa float);
- registri pembulatan wajib untuk setiap angka uang;
- interval batas eksplisit;
- model tiga tanggal (masa pajak = saat terutang, PMK 168 Ps. 19);
- rentang tafsir untuk ketentuan yang tidak diatur tegas.

Kriteria penerimaannya **nol selisih rupiah yang tidak terjelaskan**, diperiksa **per masa dan per komponen antara**, bukan hanya total tahunan.

Metrik utama:
- jumlah dan nilai maksimum selisih rupiah tak terjelaskan (target 0), diukur per masa dan per komponen;
- presisi/recall/F1 *dampak perubahan* ketika KB diperbarui;
- F1 deteksi konflik/kesalahan KB melalui *mutation testing*;
- lokalitas perubahan (entri KB vs baris kode);
- cakupan ekspresivitas.

Studi ablasi membuktikan kontribusi setiap fitur KB.

```
             ┌──────────────── KNOWLEDGE BASE ────────────────┐
             │  Lapisan Regulasi (berversi waktu)             │
  Variabel   │   rezim_2023 (PER-16)  rezim_2024+ (PMK 168)   │
  Pemerintah │   PTKP, Ps.17, TER A/B/C, BPJS, DTP, natura    │
  ─────────► │  Lapisan Kebijakan Perusahaan (per tenant)     │
  Variabel   │   komponen, prorata, gross/gross-up, THR/bonus │
  Perusahaan │  Meta-aturan: prioritas & resolusi konflik     │
  ─────────► └───────────────────────┬────────────────────────┘
                                     │ dimuat + diverifikasi statis (Z3)
  Variabel   ┌───────────────────────▼────────────────────────┐
  Karyawan   │ INFERENCE ENGINE (Python, tidak berubah)       │
  ─────────► │ seleksi aturan berlaku(t) → resolusi konflik → │
             │ forward chaining → titik tetap → penjelasan    │
             └───────────────────────┬────────────────────────┘
                                     ▼
             PPh 21 per masa + masa pajak terakhir + rincian +
             jejak aturan/pasal + peringatan (konflik, ambigu)
```

---

## 1. Keputusan Desain yang Dikunci

| # | Keputusan | Nilai | Alasan / dampak |
|---|---|---|---|
| D1 | Skala | Tugas mata kuliah KBS; tanpa jadwal | Paket kerja ditandai **[INTI]** (wajib) dan **[OPSIONAL]** (pengayaan) |
| D2 | Tahun pajak | 2023, 2024, 2025, 2026 | Peralihan rezim 2023→2024 menjadi eksperimen alami untuk RQ3 |
| D3 | Studi kasus | xlsx kantor, dianonimkan sebagai "Perusahaan X" | Hanya sheet kalkulator dummy; sheet berisi data pribadi tidak dipakai (§15.3) |
| D4 | Data riil | Tidak ada | Contoh resmi + data sintetis; data publik Indonesia untuk realisme (§8) |
| D5 | SME | Tidak ada | Diganti piramida oracle 4 lapis (§9) |
| D6 | LLM | **Tidak dipakai sama sekali**, termasuk sebagai baseline | Tidak presisi, berisiko halusinasi, dan tidak deterministik |
| D7 | Formalisme | YAML DSL + inference engine *forward chaining* (Python) buatan sendiri | Dapat diaudit; skema divalidasi JSON Schema |
| D8 | Novelty | KB dua lapis + versi waktu + resolusi konflik; gross-up TER sebagai sub-temuan | §13 |
| D9 | Kalkulator eksisting | Tidak dipercaya; berstatus *system under test* | §9, §10 |
| D10 | Presisi | Selisih Rp1 = bug. Aritmetika eksak, registri pembulatan, tiga tanggal, rentang tafsir | §6.9; kriteria penerimaan §11.1 |

---

## 2. Masalah, Bukti Awal, dan Motivasi

### 2.1 Masalah

1. **Aturan ditanam di kode atau spreadsheet.** Setiap perubahan regulasi (TER 2024, DTP 2025/2026, batas upah JP tahunan) dan setiap kebijakan perusahaan membutuhkan perubahan rumus.
2. **Dua sumber aturan bercampur tanpa batas yang jelas.** Aturan pemerintah dan aturan internal perusahaan tidak dipisahkan. Akibatnya kebijakan perusahaan dapat diam-diam melanggar aturan wajib, misalnya salah klasifikasi objek pajak, tanpa ada yang mendeteksi.
3. **Tidak ada jejak penjelasan.** Pegawai dan auditor tidak bisa menelusuri angka di slip gaji ke pasal yang mendasarinya.
4. **Definisi melingkar (gross-up)** diselesaikan dengan rumus turunan manual, yang tidak lagi berlaku ketika struktur tarif berubah ke TER.

### 2.2 Bukti awal dari artefak kantor (audit xlsx, detail di Lampiran D)

Audit terhadap [payroll_calculator.xlsx](payroll_calculator.xlsx) (sheet *Calculator PPh21 v8*, tahun pajak 2023) menemukan:

- **254 sel rumus menanam konstanta regulasi.** Isinya tarif BPJS, batas upah BPJS Kesehatan Rp12.000.000, batas upah JP **Rp9.559.600** di 24 sel (nilai Maret 2023, padahal untuk Jan–Feb 2023 seharusnya Rp9.077.600), serta biaya jabatan. Setiap pembaruan tahunan menuntut penyuntingan puluhan sel.
- **Kebijakan perusahaan melanggar aturan wajib tanpa terdeteksi.** Change log v5 memindahkan lembur ke kategori penghasilan tidak teratur, padahal PER-16 Pasal 1 angka 15 menyatakan penghasilan teratur "termasuk uang lembur".
- **Tabel PTKP K/I salah dan tidak relevan.** K/I/0 tertulis Rp108.000.000, padahal menurut PMK 101/2016 nilainya Rp112.500.000. Selain itu status K/I tidak dipakai dalam pemotongan oleh pemberi kerja.
- **Seluruh logika berbasis rezim PER-16 (2023)**, sehingga untuk 2024 dan seterusnya kalkulator harus ditulis ulang (RQ3).

### 2.3 Bukti dari implementasi publik

Survei 35 kandidat open source, dengan 7 di antaranya di-clone dan diuji (§10, [dataset/03_pembanding/README.md](dataset/03_pembanding/README.md)), menemukan **kesalahan terverifikasi di ketujuh repo**. Contohnya:
- baris tabel TER salah ketik (34 alih-alih 0,34);
- lapisan Pasal 17 diperlakukan sebagai lebar, bukan batas kumulatif;
- premi BPJS Kes pemberi kerja tidak masuk bruto;
- lebih bayar Desember dipotong ke nol;
- versi tabel TER diabaikan.

Pada kasus acuan sederhana (K/1, gaji Rp10 juta, Januari 2024), hanya 1 dari 4 library yang dapat dijalankan menghasilkan angka yang benar. Bahkan contoh resmi dalam PMK/PER memuat salah cetak dan satu pasang tafsir yang bertentangan (§9.1).

Temuan-temuan ini menjadi dasar keputusan bahwa **kalkulator yang sudah ada tidak boleh dijadikan kebenaran**, dan bahwa sistem perlu fasilitas penjelasan serta deteksi konflik.

---

## 3. Pertanyaan Penelitian dan Hipotesis

| RQ | Pertanyaan | Hipotesis (dapat difalsifikasi) | Diuji di |
|---|---|---|---|
| **RQ1** Representasi | Dapatkah aturan PPh 21 tahun 2023–2026 dan kebijakan perusahaan dinyatakan dalam KB dua lapis berversi waktu tanpa kode khusus? | **H1:** ≥ 90% kebijakan di katalog (20 entri) dapat dinyatakan *native* tanpa perubahan engine | E7 |
| **RQ2** Kebenaran | Apakah setiap angka (per masa dan per komponen antara) yang dihasilkan KB identik sampai rupiah dengan oracle, dan apakah setiap selisih dapat dijelaskan? | **H2a:** 0 selisih pada seluruh kasus V1 terhadap `expected_terkoreksi` (§9.1), per masa dan per komponen. **H2b:** 0 selisih tak terjelaskan pada seluruh kasus sintetis S1–S8 terhadap oracle teradjudikasi. Setiap selisih diberi kelas akar masalah. **H2c:** tidak ada aturan KB berstatus "keyakinan rendah" pada matriks bukti (§9.5) saat evaluasi akhir, atau sisanya dilaporkan eksplisit | E1, E2, E10 |
| **RQ3** Adaptabilitas | Ketika regulasi atau kebijakan berubah, seberapa kecil dan seberapa tepat perubahan yang diperlukan? | **H3a:** semua skenario perubahan (Lampiran B) tertangani tanpa mengubah kode engine. **H3b:** *impact F1* = 1,0, yaitu hanya output yang seharusnya berubah yang berubah. **H3c:** jumlah entri KB yang berubah jauh lebih kecil daripada baris kode yang berubah pada baseline hard-coded | E3 |
| **RQ4** Konflik | Dapatkah sistem mendeteksi dan menyelesaikan konflik antarlapisan serta kesalahan KB secara otomatis? | **H4:** F1 deteksi ≥ 0,95 pada himpunan mutan KB dan konflik berlabel | E4 |
| **RQ5** Gross-up | Kapan persamaan gross-up di bawah TER memiliki solusi tunggal atau ganda? | **H5a:** solusi selalu ada (Knaster–Tarski). **H5b:** ada pita solusi ganda di setiap batas lapisan TER. **H5c:** di masa pajak terakhir (Pasal 17), solusi tunggal | E6 |
| — Ablasi | Apakah setiap fitur KB benar-benar diperlukan? | Mematikan satu fitur menghasilkan **≥ 1 kasus salah** yang dapat ditunjukkan (contoh tandingan konkret), dan jumlah kasus salahnya dilaporkan per strata | E5 |

Klaim kebenaran **tidak** memakai uji signifikansi statistik: satu contoh tandingan sudah cukup untuk menggugurkan klaim, dan persentase dari data sintetis bergantung pada generator. Statistik hanya dipakai secara deskriptif.

---

## 4. Tujuan dan Ruang Lingkup

### 4.1 Tujuan (Goal)

Membangun **kalkulator PPh 21 berbasis knowledge base** yang:
1. menerima tiga kelompok input (karyawan, perusahaan, pemerintah);
2. menghitung PPh 21 per masa pajak dan masa pajak terakhir untuk tahun 2023–2026;
3. menghasilkan rincian dan jejak aturan/pasal;
4. dapat disesuaikan dengan perubahan regulasi dan kebijakan perusahaan **hanya dengan mengubah KB**.

### 4.2 Di dalam ruang lingkup

| Aspek | Cakupan |
|---|---|
| Subjek | Pegawai tetap, termasuk yang masuk/keluar di tengah tahun |
| Rezim | 2023: PER-16/PJ/2016 (disetahunkan + Pasal 17). 2024–2026: PMK 168/2023 (TER bulanan + masa pajak terakhir Pasal 17) |
| Penghasilan | Gaji, tunjangan tetap/tidak tetap, lembur, komisi, THR, bonus, premi BPJS yang dibayar pemberi kerja, natura sederhana (PMK 66/2023), tunjangan pajak |
| Pengurang | Biaya jabatan, iuran pensiun/JHT/JP pegawai, zakat melalui pemberi kerja |
| Metode | Gross, gross-up (termasuk campuran per komponen) |
| Insentif | PPh 21 DTP sesuai regulasi yang terverifikasi di [dataset/01_regulasi/README.md](dataset/01_regulasi/README.md) |
| BPJS | JKK (sesuai kelas risiko), JKM, JHT, JP (batas upah per tahun), Kesehatan (batas Rp12 juta) |

### 4.3 Di luar ruang lingkup

Pegawai tidak tetap, bukan pegawai, dan pensiunan; PPh selain Pasal 21; penghasilan dari lebih dari satu pemberi kerja; P3B dan WNA; pesangon (PPh 21 final); pelaporan e-Bupot/Coretax; LLM dalam bentuk apa pun; serta data pribadi riil.

Catatan: beberapa contoh resmi melibatkan WNA atau PNS. Kasus-kasus ini tetap disimpan dengan tanda (`WNA`, `PNS`) karena mekanisme TER dan masa pajak terakhirnya identik. Kasus tersebut dipakai untuk memvalidasi mekanisme, tetapi dilaporkan terpisah dari metrik utama.

---

## 5. Spesifikasi Input Kalkulator

Input dibagi menjadi tiga kelompok. Kelompok yang berubah paling jarang disimpan sebagai KB (pemerintah, perusahaan), sedangkan yang berubah tiap masa menjadi *fakta* (karyawan).

| Kelompok | Sifat | Disimpan sebagai | Siapa yang mengubah |
|---|---|---|---|
| **Pemerintah** | Berlaku untuk semua pemberi kerja; berubah karena regulasi | Lapisan regulasi KB, berversi waktu | Pemelihara KB |
| **Perusahaan** | Berlaku untuk satu pemberi kerja; berubah karena kebijakan internal | Lapisan perusahaan KB, berversi waktu | HR/payroll |
| **Karyawan** | Per pegawai per masa | Fakta (JSON) | Input transaksi payroll |

### 5.1 Variabel Pemerintah (parameter lapisan regulasi)

| Kode | Variabel | Tipe | Contoh nilai | Sumber | Berubah pada |
|---|---|---|---|---|---|
| G01 | Tabel PTKP per status | tabel | TK/0 = Rp54.000.000 | PMK 101/2016 | — (stabil sejak 2016) |
| G02 | Lapisan tarif Pasal 17 | tabel | 0–60 jt: 5%; … ; > 5 M: 35% | UU HPP Ps. 17 | 2022 (HPP) |
| G03 | Pemetaan status PTKP → kategori TER | tabel | TK/0, TK/1, K/0 → A | PP 58/2023 | 2024 |
| G04 | Tabel TER bulanan A/B/C | tabel | [lihat `tables/ter_bulanan.csv`] | PP 58/2023 Lampiran | 2024 |
| G05 | TER harian | tabel | (di luar lingkup subjek; dimuat untuk kelengkapan) | PP 58/2023 | 2024 |
| G06 | Biaya jabatan | tarif + plafon | 5%; maks Rp500.000/bln; Rp6.000.000/thn | PMK 168/2023, PER-16 | — |
| G07 | Iuran BPJS per program | tarif + porsi | JHT 3,7% PK / 2% PG; JP 2% / 1%; JKM 0,3%; Kes 4% / 1% | PP 44, 45, 46/2015; Perpres 82/2018 jo. 64/2020 | — |
| G08 | Kelas risiko JKK | tabel | 0,24% … 1,74% | PP 44/2015 | — |
| G09 | Batas upah JP | nilai per tahun | Jan–Feb 2023: 9.077.600; Mar 2023: 9.559.600; Mar 2024: 10.042.300; Mar 2025: 10.547.400; Mar 2026: 11.086.300 | Pengumuman BPJS TK | **setiap tahun** |
| G10 | Batas upah BPJS Kesehatan | nilai | Rp12.000.000 | Perpres 64/2020 | — |
| G11 | Perlakuan pajak premi | aturan | premi JKK/JKM/Kes oleh pemberi kerja = objek; JHT/JP oleh pemberi kerja = bukan objek | PMK 168/2023, PER-16 | — |
| G12 | Aturan pembulatan | aturan | PKP dibulatkan ke bawah ribuan rupiah | UU PPh, PMK 168/2023 | — |
| G13 | Syarat & besaran PPh 21 DTP | aturan | sektor (KLU), batas bruto, masa berlaku | PMK DTP 2025–2026 | 2025, 2026 |
| G14 | Natura dikecualikan dan cara penilaiannya | aturan + batas | makan/minuman untuk seluruh pegawai, dan lain-lain | PMK 66/2023 | 2023 |
| G15 | Aturan masa pajak terakhir | aturan | Desember atau bulan keluar | PMK 168/2023 | 2024 |
| G16 | Rezim penghasilan tidak teratur | aturan | 2023: metode selisih; 2024+: masuk bruto TER | PER-16 / PMK 168 | 2024 |
| G17 | Kalender libur nasional & cuti bersama | daftar tanggal | 2023-04-22 Idul Fitri | SKB 3 Menteri (tahunan) | setiap tahun |

### 5.2 Variabel Perusahaan (parameter lapisan perusahaan)

| Kode | Variabel | Tipe | Contoh (Perusahaan X) | Catatan |
|---|---|---|---|---|
| P01 | Identitas & KLU/sektor usaha | teks | — | Dipakai untuk syarat DTP |
| P02 | Kelas risiko JKK | enum | 0,24% | Ditetapkan pemerintah per perusahaan |
| P03 | Metode pajak default dan per komponen | enum | gross | gross / gross_up / campuran |
| P04 | Daftar komponen penghasilan | daftar | gaji pokok, telepon, transport, akomodasi, THR, kompensasi, OTA, lembur, komisi | Setiap komponen **wajib** dipetakan ke kategori pajak regulasi |
| P05 | Rumus komponen | ekspresi | kompensasi = % × gaji × min(masa kerja, 12)/12 | Dibatasi pada ekspresi aman (tanpa kode bebas) |
| P06 | Tipe prorata | enum | tetap / hari_kerja / hari_kalender | |
| P07 | Dasar upah BPJS | ekspresi | gaji pokok | |
| P08 | Jadwal THR/bonus dan cara prorata THR | aturan | prorata per hari | Bandingkan Permenaker 6/2016 (per bulan) |
| P09 | Kebijakan natura | daftar | — | Diuji terhadap PMK 66/2023 |
| P10 | Program pensiun/DPLK, zakat | flag + tarif | — | |
| P11 | Aturan penyelesaian gross-up ganda | enum | `solusi_terkecil` (titik tetap terkecil) | RQ5 |
| P12 | Pembulatan internal | aturan | ROUND per komponen | Tidak boleh menimpa pembulatan wajib regulasi |
| P13 | Kalender kerja perusahaan | daftar | hari kerja Senin–Jumat | |
| P14 | Pemanfaatan DTP | flag | — | |

### 5.3 Variabel Karyawan (fakta per pegawai per masa)

| Kode | Variabel | Tipe | Contoh | Wajib | Dipakai oleh aturan |
|---|---|---|---|---|---|
| E01 | ID pegawai (pseudonim) | str | KAR-A | ✓ | — |
| E02 | Status PTKP pada awal tahun pajak | enum | TK/0 | ✓ | PTKP, kategori TER |
| E03 | Jenis kelamin & status penghasilan suami | enum | — | ✓ jika K | PTKP pegawai wanita |
| E04 | NPWP/NIK terdaftar | bool | ya | ✓ | tarif lebih tinggi (di luar lingkup bila tidak) |
| E05 | Tanggal masuk / tanggal keluar | date | 2022-02-02 / — | ✓ | prorata, masa pajak terakhir |
| E06 | Gaji pokok berlaku & riwayat perubahan | uang + tanggal | 8.178.800; +1.200.000 per 2023-03-23 | ✓ | |
| E07 | Tunjangan tetap/tidak tetap per masa | uang | telepon 150.000 | | |
| E08 | Lembur, komisi, insentif per masa | uang | lembur Feb 1.500.000 | | |
| E09 | THR, bonus (tanggal, nominal) | uang + tanggal | THR April | | |
| E10 | Natura yang diterima | daftar | — | | |
| E11 | Hari kerja aktual, cuti tidak dibayar | int | 20/22 | | prorata |
| E12 | Tanggal terdaftar BPJS TK/Kes | date | 2023-02-01 | | premi BPJS |
| E13 | Zakat melalui pemberi kerja | uang | — | | pengurang |
| E14 | Penghasilan bersih yang dijanjikan (gross-up) | uang | — | ✓ jika gross-up | titik tetap |

Skema JSON lengkap: `kb/skema/fakta_karyawan.schema.json` (WP1). Contoh nyata: [dataset/02_studi_kasus/input_karyawan_A_2023.json](dataset/02_studi_kasus/input_karyawan_A_2023.json).

---

## 6. Rancangan Knowledge Base dan Inference Engine

### 6.1 Konsep inti (ontologi ringan)

`Pegawai` · `MasaPajak` · `TahunPajak` · `KomponenPenghasilan` {teratur, tidak_teratur, natura, premi_pemberi_kerja, tunjangan_pajak} · `KategoriObjek` {objek, bukan_objek, dikecualikan} · `Pengurang` · `PenghasilanBruto` · `PenghasilanNeto` · `PTKP` · `PKP` · `KategoriTER` {A, B, C} · `TarifTER` · `TarifPasal17` · `MasaPajakTerakhir` · `InsentifDTP` · `Aturan` · `Lapisan` · `VersiKB`.

Setiap komponen perusahaan **wajib** dipetakan ke satu `KategoriObjek` milik regulasi. Pemetaan inilah titik temu kedua lapis sekaligus tempat konflik paling sering terjadi.

### 6.2 Skema DSL aturan (YAML)

```yaml
- id: REG-TER-001
  lapisan: regulasi            # regulasi | perusahaan
  sifat: wajib                 # wajib | default | opsional | tafsir
  berlaku: {mulai: 2024-01-01, sampai: null}     # valid time, dibandingkan dengan sumbu waktu §6.9.4
  sumbu_waktu: masa_pajak      # masa_pajak (saat terutang) | periode_iuran | periode_kerja
  versi_kb: {dicatat: 2024-01-02, oleh: pemelihara} # knowledge time
  sumber: {regulasi: "PMK 168/2023", pasal: "Pasal 15 ayat (1) huruf a", halaman_pdf: 15, otoritas: 3}
  menghasilkan: pph21_masa       # fakta turunan yang ditulis aturan ini
  tipe_hasil: rupiah             # rupiah (int) | tarif (Decimal) | kategori | bool
  jika:
    - masa_pajak.bulan != masa_pajak_terakhir.bulan
    - pegawai.jenis == tetap
  maka:
    pph21_masa: tarif_ter(kategori_ter, bruto_masa) * bruto_masa
  pembulatan: {ref: BULAT-TER-01}  # WAJIB untuk tipe_hasil rupiah (§6.9.2)
  prioritas: 0                   # salience; dipakai bila asas hukum belum memutus
```

Tabel bernilai uang/tarif ditulis sebagai **string** (`"0.0025"`, `"5400000"`) dan dibaca sebagai `Decimal`. Interval lapisan dinyatakan eksplisit, misalnya `interval: "(5400000, 5650000]"` (§6.9.3).

Prinsip DSL:
- **(a) Ekspresi aman.** Hanya aritmetika, perbandingan, `min/max/round`, *lookup* tabel, dan agregasi masa (`sum_masa`, `masa_sebelumnya`). Tidak ada kode bebas (*no escape hatch*). Inilah yang membedakan sistem ini dari mesin yang mengizinkan potongan kode di dalam aturan (misalnya *salary rule* Python di Odoo/OCA). Untuk kebijakan yang tidak bisa dinyatakan, hasilnya adalah "tidak bisa", dan itu dihitung jujur di metrik ekspresivitas.
- **(b) Tabel sebagai pengetahuan** (`ter_bulanan`, `ptkp`, `tarif_pasal17`), juga berversi waktu.
- **(c) Validasi skema.** Setiap file divalidasi dengan JSON Schema sebelum dimuat.

### 6.3 Semantik lapisan dan resolusi konflik

Untuk atribut turunan *a* pada waktu *t* bagi pegawai *e* di perusahaan *c*, kandidat aturannya adalah R(a, t) = {aturan dengan `menghasilkan = a`, `t ∈ berlaku`, kondisi terpenuhi}. Pemilihan dilakukan berurutan:

1. **Lex superior.** Jika ada aturan regulasi bersifat `wajib`, aturan perusahaan atas *a* **ditolak** dan sistem mengeluarkan peringatan `KONFLIK_WAJIB`. Contoh: perusahaan memetakan premi JKK sebagai bukan objek.
2. **Lex specialis.** Di dalam satu lapisan, aturan dengan kondisi lebih spesifik (himpunan kondisi yang merupakan superset) menang.
3. **Lex posterior.** Di antara versi aturan yang sama, yang `berlaku.mulai` paling akhir (dan ≤ *t*) menang.
4. **Override yang sah.** Aturan regulasi bersifat `default` (misalnya metode gross) boleh ditimpa aturan perusahaan.
5. **Prioritas eksplisit.** Dipakai bila langkah 1–4 belum memutus. Jika masih seri, terjadi `AMBIGU` yang ditolak saat verifikasi statis (§6.6), bukan saat runtime.

Semua langkah tercatat di jejak penjelasan.

### 6.4 Versi waktu (bitemporal)

- **Valid time** (`berlaku`): kapan aturan berlaku atas fakta pajak. Ini memungkinkan satu engine menghitung 2023 dengan PER-16 dan 2024 dengan PMK 168.
- **Knowledge time** (`versi_kb.dicatat`): kapan KB mengetahui aturan tersebut. Ini memungkinkan dua jenis pertanyaan:
  - *"Berapa yang seharusnya dipotong?"* (pakai KB terbaru);
  - *"Berapa yang dihitung pada saat itu?"* (pakai KB sebagaimana tercatat pada tanggal tersebut).

  Ini relevan untuk regulasi yang berlaku surut, yaitu regulasi yang diundangkan setelah tanggal mulai berlakunya. Contoh nyatanya **PMK 10/2025**: berlaku 4 Februari 2025, tetapi mencakup masa pajak **Januari** 2025. PPh 21 Januari yang sudah dipotong dengan KB "versi 31 Januari" berbeda dengan yang seharusnya menurut KB "versi 5 Februari". Selisih ini diukur di skenario C04.
- **Uji isolasi temporal:** menambahkan aturan 2026 tidak boleh mengubah satu rupiah pun output 2023–2025. Ini menjadi relasi metamorfik MR7 (§9.3).

### 6.5 Inference engine

1. **Loader dan validator.** Muat KB → validasi skema → bangun **graf dependensi** fakta (`aturan.jika`/`maka` → `menghasilkan`).
2. **Seleksi aturan berlaku** berdasarkan sumbu waktu aturan (`saat_terutang` untuk aturan pajak, `periode_iuran` untuk BPJS; §6.9.4) dan lapisan (§6.3, §6.4).
3. **Forward chaining berbasis agenda.** Fakta dasar (input karyawan) memicu aturan. Agenda diurutkan menurut urutan topologis graf dependensi lalu prioritas. Algoritmanya *naive forward chaining*, dengan opsi Rete-lite sebagai optimasi [OPSIONAL].
4. **Siklus.** Komponen yang terhubung kuat (SCC) dalam graf adalah definisi melingkar.
   - SCC yang tidak ditandai `titik_tetap: true` → ditolak saat verifikasi.
   - SCC yang ditandai → diserahkan ke **penyelesai titik tetap** (§6.7).
5. **Masa pajak terakhir.** Aturan agregasi (`sum_masa`) memicu perhitungan tahunan Pasal 17 dan selisih terhadap PPh yang sudah dipotong.
6. **Fasilitas penjelasan.** Setiap fakta turunan menyimpan `(nilai, id_aturan, sumber_pasal, fakta_masukan)`. Jejak ini dapat ditampilkan sebagai penjelasan *how* (bagaimana angka diperoleh) dan *why* (mengapa aturan dipilih atau ditolak).

### 6.6 Verifikasi statis KB (sebelum dipakai)

| Pemeriksaan | Teknik | Contoh kesalahan yang ditangkap |
|---|---|---|
| Kelengkapan & tumpang tindih lapisan TER/Pasal 17 | Z3: ∀x ≥ 0, tepat satu lapisan | Celah antara 5.650.000 dan 5.650.001 |
| Monotonisitas tarif | Z3 | Tarif lapisan lebih tinggi justru lebih kecil (salah ketik) |
| Tumpang tindih masa berlaku dua versi aturan yang sama | Interval check | Dua tabel PTKP berlaku bersamaan |
| Celah masa berlaku | Interval check | Tidak ada aturan TER untuk Januari 2024 |
| Aturan tidak terjangkau / fakta tak terdefinisi | Analisis graf | Komponen perusahaan tanpa kategori objek |
| Siklus tanpa tanda titik tetap | SCC | Tunjangan A bergantung pada B dan sebaliknya |
| Konflik wajib vs perusahaan | §6.3 langkah 1 | Premi JKK dipetakan bukan objek |
| Tipe & satuan | Skema | Tarif ditulis 5 alih-alih 0,05 |
| Aturan uang tanpa entri registri pembulatan | Skema + referensi | `pph21_masa` tanpa `pembulatan` |
| Float literal di KB | Loader | `tarif: 0.29` tanpa tanda kutip |
| Semantik interval | Skema + Z3 (`Int`) | Batas ditulis `[a, b)` padahal pasal "di atas a s.d. b" |
| Integritas tabel | Hash SHA-256 vs manifest | Tabel TER berubah tanpa pencatatan versi |
| Sumbu waktu tidak dinyatakan | Skema | Aturan BPJS dipilih dengan masa pajak, bukan periode iuran |

### 6.7 Penyelesai titik tetap (gross-up)

Definisi gross-up: T = f(T), dengan f(T) = PPh(B + T), di mana B adalah bruto sebelum tunjangan pajak.

- **Keberadaan solusi.** f monoton tidak turun, karena PPh tidak turun ketika bruto naik, baik di TER maupun Pasal 17. f juga memetakan interval [0, B·r_max/(1−r_max)] ke dirinya sendiri. Berdasarkan **teorema Knaster–Tarski**, titik tetap selalu ada dan **titik tetap terkecil** dicapai dengan iterasi Kleene dari T₀ = 0 dalam jumlah langkah terhingga, karena tarif berlapis dan rupiah diskret.
- **Ketunggalan.** Di dalam satu lapisan TER, solusinya x = B/(1−r). Di batas lapisan x_k, g(x) = x(1−r(x)) turun mendadak. Akibatnya, dengan semantik lapisan (a, b], untuk **B ∈ (x_k(1−r_{k+1}), x_k(1−r_k)]** ada **dua** solusi. Solusi bawahnya x = B/(1−r_k) ≤ x_k, dan solusi atasnya x = B/(1−r_{k+1}) > x_k. Inklusivitas ujung pita mengikuti inklusivitas batas lapisan, sehingga salah semantik interval menggeser pita sebesar Rp1. Engine **mengenumerasi semua solusi secara analitis per lapisan** (bukan hanya iterasi), lalu memilih sesuai P11 (default: titik tetap terkecil) dan mengeluarkan peringatan `GROSSUP_GANDA` beserta kedua solusinya.
- **Hasil awal (sudah dihitung dari `tables/ter_bulanan.csv`):**
  - Setiap kenaikan tarif di batas lapisan menghasilkan satu pita solusi ganda: **43 pita (A), 39 (B), 40 (C)**.
  - Contoh proposal (§9.3) **terkonfirmasi** dengan tabel resmi: B = Rp14.100.000 (kategori A) memiliki dua solusi, yaitu x = Rp15.000.000 (6%) dan x = Rp15.161.290 (7%), karena batas lapisan 6%/7% berada di Rp15.100.000.
  - Survei pembanding menemukan hanya `pajakin` yang mengimplementasikan gross-up TER (*closed form*) dan belum ada yang melaporkan solusi ganda. Ini membuka uji H2 lama (implementasi berbeda memilih solusi berbeda) sebagai eksperimen opsional.
- **Masa pajak terakhir (Pasal 17).** Tarif marginal < 1 dan PPh kontinu dalam PKP, sehingga diharapkan ada solusi tunggal (H5c, dibuktikan di E6). Pembulatan ke bawah ribuan dapat menimbulkan anak tangga kecil yang juga dianalisis.
- **Analisis di atas masih di domain real.** Versi yang mengikat adalah versi integer di §6.9.7: setiap kandidat diverifikasi ulang secara eksak, dan peta pita dihitung ulang setelah pembulatan.

### 6.8 Contoh lapisan perusahaan

Lihat [dataset/02_studi_kasus/kebijakan_perusahaan_x.yaml](dataset/02_studi_kasus/kebijakan_perusahaan_x.yaml). File ini merekonstruksi seluruh kebijakan Perusahaan X dari xlsx: prorata per hari kerja, kenaikan gaji di tengah bulan, tunjangan *fixed/prorate*, THR prorata per hari, kompensasi 4×/tahun, lembur/komisi sebagai penghasilan tidak teratur, BPJS tidak dipotong di bulan keluar, blok `pembulatan`, dan blok `resolusi_konflik`.

### 6.9 Kontrak Presisi Numerik dan Waktu

> **Prinsip:** di sistem keuangan, selisih Rp1 adalah bug. Kontrak ini mengikat engine, KB, baseline B1, adaptor pembanding, dan oracle. Pelanggaran kontrak adalah kegagalan verifikasi, bukan peringatan.

#### 6.9.1 Aritmetika

| Aturan | Isi | Alasan / bukti |
|---|---|---|
| AR-1 | Semua nilai uang disimpan sebagai **`int` rupiah**. Nilai antara yang belum dibulatkan disimpan sebagai `Fraction`/`Decimal` eksak | Uji awal: pada 44 tarif TER dan bruto Rp1.000–Rp2 juta (kelipatan Rp1.000), `float` menghasilkan **700 selisih Rp1** terhadap aritmetika eksak bila dibulatkan ke bawah (contoh: 0,29 × 3.000 = 869,999… → 869, seharusnya 870) |
| AR-2 | Tarif dan persentase disimpan sebagai `Decimal` yang dibaca **dari string**. Float literal di YAML ditolak loader | PyYAML membaca `0.29` sebagai `float`, sehingga KB tercemar sejak dimuat |
| AR-3 | `float` **dilarang** di engine dan B1. Ditegakkan dengan tes statis (scan AST) dan tes runtime (setiap fakta uang bertipe `int`) | Mencegah regresi |
| AR-4 | Z3 memakai sort `Int` (rupiah) dan `Real` (tarif rasional), tanpa floating point | Bukti formal harus eksak |
| AR-5 | Adaptor pembanding (B2) mengonversi output ke `int` dan mencatat bila library mengembalikan pecahan/float | Selisih akibat representasi pembanding diklasifikasikan terpisah |

#### 6.9.2 Registri pembulatan

Setiap aturan dengan `tipe_hasil: rupiah` **wajib** merujuk satu entri registri. Verifikator statis menolak aturan tanpa entri tersebut.

```yaml
- id: BULAT-TER-01
  titik: hasil(tarif_ter × bruto_masa)
  satuan: 1               # rupiah
  mode: bawah             # bawah | atas | menuju_nol | setengah_atas | setengah_menjauhi_nol (= Excel ROUND) | setengah_genap (= round() Python)
  urutan: setelah_kali    # dibulatkan sekali setelah perkalian, bukan per komponen
  status: tafsir          # wajib (diatur regulasi) | tafsir (tidak diatur) | kebijakan (perusahaan)
  dasar: "Tidak diatur PP 58/2023 maupun PMK 168/2023 (tables/pembulatan_dan_lainnya.csv)"
  alternatif: [setengah_atas]
  kalibrasi: E10          # mode default dikalibrasi empiris (§12)
```

Inventaris titik pembulatan minimal, beserta status awalnya:

| ID | Titik | Status awal | Dasar |
|---|---|---|---|
| BULAT-PKP-01 | PKP setahun | **wajib**: ke bawah, ribuan | PMK 168 Ps. 8(4); PER-16 Ps. 14(8) |
| BULAT-TER-01 | TER × bruto masa | tafsir | tidak diatur |
| BULAT-P17-01 | PPh Pasal 17 setahun | tafsir | hasil tarif × PKP ribuan selalu bulat untuk 5/15/25/30/35%; diverifikasi Z3 |
| BULAT-BRUTO-01 | Bruto masa sebelum lookup TER (bila mengandung pecahan) | tafsir | tidak diatur; `muhroyhan` gagal di titik ini |
| BULAT-PROPORSI-01 | PPh setahun bagian tahun pajak (× n/12) | tafsir | PMK 168 Ps. 15(3); ditemukan saat WP1a, ketika 2 contoh resmi WNA ternyata diproporsikan |
| BULAT-BJ-01 | Biaya jabatan (5% × bruto) | tafsir | — |
| BULAT-BPJS-01..n | Premi/iuran per program | tafsir | harus sama dengan tagihan BPJS; praktik BPJS belum diketahui |
| BULAT-P16-01 | PPh bulanan rezim 2023 (setahun ÷ n) | tafsir | contoh PER-16 **tidak konsisten**: 126.287,5 → 126.288, tetapi 103.087,5 → 103.087 |
| BULAT-PRO-01 | Prorata gaji/tunjangan | kebijakan | lapisan perusahaan (P12); di Perusahaan X = `PX-BULAT-PRO`, `setengah_menjauhi_nol` per komponen (Excel `ROUND`) |

Semantik mode untuk nilai **negatif** (misalnya lebih bayar masa terakhir) didefinisikan eksplisit di `engine/pembulatan.py`. Contohnya Excel `ROUND(-2,5) = -3`, sedangkan `setengah_atas` menghasilkan -2. Karena itu nama mode harus tepat, bukan sekadar "dibulatkan".
| BULAT-GU-01 | Tunjangan pajak (gross-up) | tafsir | §6.9.6 |

Catatan penting: V1 **hampir tidak menguji pembulatan**. Dari 170 perhitungan TER bulanan di contoh resmi, hanya **1** yang menghasilkan pecahan (PMK168-B-I.4: 13.777.062,39 → 13.777.062), karena bruto contoh resmi selalu bulat. Karena itu pembulatan diuji khusus lewat strata S7 dan dikalibrasi di E10.

#### 6.9.3 Interval dan domain

- Semantik "di atas *a* sampai dengan *b*" ditulis eksplisit sebagai interval **(a, b]** di skema tabel. Lapisan pertama adalah [0, b].
- Verifikator memeriksa (Z3, `Int`) bahwa setiap tabel bertingkat menutup [0, ∞) tanpa celah atau tumpang tindih.
- Domain lookup adalah **integer rupiah**. Bruto pecahan dibulatkan dulu sesuai BULAT-BRUTO-01. Engine tidak boleh *crash* atau jatuh ke lapisan yang salah.
- Uji batas wajib untuk **semua** batas: 125 batas TER bulanan, 4 batas Pasal 17, dan batas TER harian. Setiap batas *b* diuji pada {*b*−1, *b*, *b*+1} serta nilai pecahan *b* + 0,5 sebelum pembulatan.

#### 6.9.4 Model waktu: tiga tanggal

PMK 168/2023 **Pasal 19 ayat (1)** menyatakan PPh 21 terutang pada saat **pembayaran atau terutangnya penghasilan, mana yang terjadi lebih dahulu**. Untuk rezim 2023, PER-16/PJ/2016 **Pasal 21 ayat (1) dan (3)** memuat ketentuan setara (frasa "mana yang lebih dahulu" tidak tertulis eksplisit dan dicatat sebagai `tafsir`). Parameter BPJS mengikuti **periode iuran** (misalnya batas upah JP berlaku "mulai iuran bulan Maret"). Karena itu setiap fakta penghasilan wajib membawa:

| Tanggal | Arti | Dipakai untuk |
|---|---|---|
| `periode_kerja` | Bulan pekerjaan yang dibayar | Prorata, iuran BPJS (`periode_iuran`) |
| `tanggal_terutang` | Saat hak atas penghasilan timbul | — |
| `tanggal_bayar` | Saat dibayarkan | — |
| **`saat_terutang`** = min(`tanggal_bayar`, `tanggal_terutang`) | Turunan, bukan input | **Masa pajak, tahun pajak, dan pemilihan versi aturan pajak** |

- Aturan memilih sumbunya lewat `sumbu_waktu`, sehingga tidak ada lagi "*t*" yang ambigu.
- Kasus batas wajib diuji (strata S8): gaji Desember yang dibayar Januari, THR yang dibayar sebelum bulan Lebaran, rapel lintas tahun, bonus yang diumumkan Desember tetapi dibayar Maret, serta pegawai yang keluar setelah tanggal bayar.
- Temuan terkait: **K-11** (Lampiran D). Di xlsx, THR ditransfer 28-02-2023 tetapi dipajaki pada masa April.

#### 6.9.5 Validasi input (menolak, bukan menebak)

- Skema input ketat dengan invarian lintas-field: `tanggal_keluar ≥ tanggal_masuk`; `hari_kerja_aktual ≤ hari_kerja_penuh`; status PTKP diambil **per 1 Januari** (perubahan di tengah tahun ditolak dengan peringatan); semua nominal bertipe `int ≥ 0`; setiap komponen perusahaan terpetakan ke kategori objek.
- Satu kolom input tidak boleh punya dua makna (pelajaran K-04). "Akhir tahun" dan "tanggal keluar" adalah dua field berbeda.
- `DATA_KURANG` **menghentikan** perhitungan pegawai tersebut. Tidak ada nilai default diam-diam untuk fakta yang memengaruhi pajak.

#### 6.9.6 Tafsir: hierarki otoritas dan rentang tafsir

- **Hierarki otoritas** untuk adjudikasi dan pemilihan varian, dari tertinggi:
  1. UU;
  2. PP;
  3. batang tubuh PMK/PER;
  4. lampiran (contoh perhitungan) PMK/PER;
  5. FAQ dan kalkulator resmi DJP;
  6. sumber sekunder (DDTC, Ortax, buku Brevet).

  Contoh resmi yang bertentangan dengan pasal kalah dari pasal. Dua contoh resmi yang saling bertentangan menjadi **tafsir**.
- Setiap aturan berstatus `tafsir` punya varian `default` dan `alternatif`. Engine menghitung **semua varian secara paralel** dan melaporkan **rentang tafsir** per angka: "PPh Rp X (default); tafsir alternatif: Rp Y (selisih Rp Z)". Pengguna keuangan melihat eksposur risikonya, bukan hanya satu angka.
- Contoh tafsir yang sudah teridentifikasi: plafon biaya jabatan masa kerja < 12 bulan (PMK 10/2025 vs PMK 105/2025), pembulatan TER × bruto, pembulatan bruto pecahan, perlakuan porsi JKP hasil rekomposisi JKK, tunjangan pajak ketika PPh ditanggung DTP, dan klasifikasi komisi (teratur/tidak teratur).

#### 6.9.7 Gross-up dalam rupiah bulat

- Persamaan yang dipakai adalah versi integer: **T = PPh_int(B + T)**, dengan PPh_int sudah memuat pembulatan resmi.
- Solusi analitis per lapisan (§6.7) hanya menghasilkan **kandidat**. Setiap kandidat (dan tetangganya ±Rp1) **wajib diverifikasi ulang** dengan evaluasi integer. Hanya yang memenuhi persamaan secara persis yang diterima.
- Knaster–Tarski tetap berlaku di domain integer, karena pembulatan ke bawah atau setengah-atas bersifat monoton. Namun **jumlah** solusi bisa berubah (0 pita, 1, 2, atau lebih) setelah pembulatan, sehingga peta pita E6 dihitung ulang di domain integer.
- Identitas MR4 (bruto − PPh = B) dapat meleset karena pembulatan. Kriteria penerimaannya adalah **T = PPh_int(B + T) persis**, dan simpangan net terhadap B dilaporkan.
- **Gross-up masa pajak terakhir** adalah persamaan **tahunan**. Tunjangan pajak Desember bergantung pada PPh setahun atas (B_setahun + ΣT_Jan–Nov + T_Des) dikurangi ΣPPh Jan–Nov. Persamaan ini dianalisis tersendiri di E6, termasuk ketika hasilnya lebih bayar (T_Des negatif).
- Interaksi gross-up dengan DTP diperlakukan sebagai tafsir (§6.9.6).

#### 6.9.8 Jejak audit dan reproduktibilitas

- Setiap output memuat: `versi_kb` (commit), hash SHA-256 setiap tabel, daftar aturan `tafsir` beserta varian yang dipakai, `tanggal_kebaruan_kb` (regulasi terakhir yang diperiksa), dan versi engine.
- Hasil acuan (*golden master*) untuk seluruh kasus V1 dan sampel S1–S8 disimpan beserta hash-nya. Setiap perubahan KB atau engine yang mengubah satu rupiah pun pada *golden master* wajib dijelaskan di log perubahan.
- Determinisme: input dan versi KB yang sama menghasilkan output yang identik bit per bit, termasuk urutan jejak.

---

## 7. Spesifikasi Output

### 7.1 Isi output per pegawai per tahun pajak

1. **Ringkasan:** PPh 21 per masa (Jan–Des), PPh 21 masa pajak terakhir, total setahun, kurang/lebih bayar di masa terakhir, PPh 21 DTP (jika ada), dan *take-home pay*.
2. **Rincian per masa:** setiap komponen bruto (dengan kategori objeknya), kategori TER dan lapisan yang dipakai beserta tarifnya, tunjangan pajak (jika gross-up), dan premi BPJS per program (objek/bukan objek).
3. **Rincian tahunan (masa pajak terakhir):** bruto setahun, biaya jabatan, iuran pensiun/JHT/JP, neto, PTKP, PKP (dibulatkan), PPh Pasal 17 setahun, dan PPh yang telah dipotong. Strukturnya mengikuti isian bukti potong tahunan (formulir 1721-A1).
4. **Jejak aturan:** untuk setiap angka, daftar `id_aturan → pasal sumber → fakta masukan → entri pembulatan`.
5. **Rentang tafsir:** untuk setiap angka yang dipengaruhi aturan `tafsir`, nilai default, nilai tiap varian alternatif, dan selisihnya (§6.9.6).
6. **Metadata audit:** `versi_kb`, hash tabel, versi engine, `tanggal_kebaruan_kb`, dan daftar asumsi yang dipakai (§6.9.8).
7. **Peringatan:** `KONFLIK_WAJIB`, `GROSSUP_GANDA`, `AMBIGU_TAFSIR`, `DATA_KURANG` (menghentikan perhitungan), `INPUT_TIDAK_VALID` (menghentikan perhitungan), `ATURAN_TIDAK_BERLAKU`, dan `DTP_TIDAK_MEMENUHI_SYARAT`.

Semua nilai uang di output bertipe integer rupiah. Tidak ada nilai pecahan atau float.

### 7.2 Format

JSON (kanonik, untuk evaluasi), tabel slip (Streamlit), dan CSV per masa (sejajar dengan [output_xlsx_karyawan_A_2023.csv](dataset/02_studi_kasus/output_xlsx_karyawan_A_2023.csv) supaya bisa dibandingkan per sel). Contoh di Lampiran C.

---

## 8. Data dan Aset

> Status: ✅ tersedia & terverifikasi · 🛠 dibangkitkan oleh skrip di repo · 📝 dibangun di WP · ⚠️ terbatas (lihat catatan)

### 8.1 Inventaris aset

| # | Aset | Lokasi | Isi | Status | Dipakai di |
|---|---|---|---|---|---|
| A1 | PDF regulasi pajak | [dataset/01_regulasi/](dataset/01_regulasi/) | UU 7/2021 (HPP), UU 36/2008, PMK 101/2016, PER-16/PJ/2016 (+ OCR), PP 58/2023, PMK 168/2023, PMK 66/2023, PP 55/2022, PMK 81/2024, PER-11/PJ/2025, PER-2/PJ/2024 | ✅ 33 PDF, diverifikasi `%PDF` + jumlah halaman; mayoritas dari JDIH BPK | WP1–WP2 |
| A2 | PDF regulasi DTP | idem | PMK 10/2025, PMK 72/2025 (+ FAQ DJP), PMK 105/2025, PMK 6/2026 (pemagangan, di luar lingkup), PMK 28/2024 (IKN) | ✅ | C04–C06 |
| A3 | PDF regulasi BPJS | idem | PP 44/2015 (+ Lampiran), 82/2019, 49/2023, 45/2015, 46/2015, 37/2021, 6/2025, 7/2025, 36/2025; Perpres 82/2018, 75/2019, 64/2020, 59/2024 | ✅ | G07–G10, C07 |
| A4 | Surat batas upah JP 2023–2026 | `01_regulasi/bpjs_tk_batas_upah_jp/` | 4 surat BPJS TK | ⚠️ dokumen resmi, tetapi diperoleh dari *mirror* pihak ketiga | G09, C02–C03 |
| A5 | **Tabel parameter siap pakai** | [dataset/01_regulasi/tables/](dataset/01_regulasi/tables/) | `ter_bulanan.csv` (A = 44, B = 40, C = 41 lapisan), `ter_harian.csv`, `tarif_pasal17.csv`, `ptkp.csv` (termasuk K/I), `biaya_jabatan.csv`, `bpjs.csv` (berversi), `pembulatan_dan_lainnya.csv` | ✅ setiap baris memuat pasal + halaman; TER direproduksi terhadap contoh resmi (PMK 168 "Tuan A", PP 58). ⚠️ Baru **satu** jalur ekstraksi; ekstraksi kedua + hash wajib sebelum dipakai (§9.6) | Bahan langsung KB (WP2) |
| A6 | **Kasus uji resmi (gold)** | [dataset/07_kasus_uji_resmi/](dataset/07_kasus_uji_resmi/) | 46 kasus dalam lingkup + 4 di luar lingkup (JSON) + 38 entri ringkas; `index.csv` | ✅ diverifikasi dua pass terhadap gambar halaman | V1, E1 |
| A7 | Studi kasus Perusahaan X | [dataset/02_studi_kasus/](dataset/02_studi_kasus/) | `input_karyawan_A_2023.json`, `output_xlsx_karyawan_A_2023.csv` (output B0 per bulan, 43 variabel), `parameter_xlsx_2023.json`, `kebijakan_perusahaan_x.yaml`, skrip `ekstrak_xlsx.py` | ✅ teranonimkan; hanya sheet dummy yang dibaca | E8, WP7 |
| A8 | Pembanding OSS | [dataset/03_pembanding/](dataset/03_pembanding/) | 7 repo clone penuh, `kandidat_repo.csv` (35), `maintenance_ter_commits.csv`, `mesin_rule_as_code.csv`, README dengan `indikasi_kesalahan` per repo | ✅ ⚠️ `repos/pajakin` tanpa lisensi, jangan didistribusikan | E2, E3, E7 |
| A9 | Kalkulator online | `03_pembanding/kalkulator_online.csv` | 22 kalkulator: fitur, ToS, robots.txt | ✅ hanya untuk uji manual | B3 |
| A10 | Data publik Indonesia | [dataset/04_data_publik/](dataset/04_data_publik/) | BPS: upah rata-rata per provinsi/sektor/umur/pendidikan/jabatan (2023–2026), Keadaan Pekerja Agt 2025 & Feb 2026 (distribusi kelompok upah), status kawin, ukuran rumah tangga; Kemnaker UMP 2018–2026; sekunder Kaggle/Zenodo | ✅ ⚠️ upah BPS = **upah bersih rata-rata**, kelompok teratas "2 jt+" | Kalibrasi generator (§8.2) |
| A11 | Katalog kebijakan | [dataset/05_katalog_kebijakan/katalog_kebijakan.yaml](dataset/05_katalog_kebijakan/katalog_kebijakan.yaml) | 20 kebijakan (KP-01..KP-20) + kebutuhan fitur KB | ✅ draf; label konflik ditambahkan di WP7 | E4, E7 |
| A12 | Kasus sintetis | [dataset/06_kasus_uji_sintetis/](dataset/06_kasus_uji_sintetis/) | `bangkitkan_kasus.py` (strata S1–S8, seed tetap), `kasus_sintetis.jsonl`. S7 = bruto pecahan (prorata, kenaikan gaji tengah bulan, premi BPJS); S8 = batas sumbu waktu (tanggal bayar ≠ periode kerja) | 🛠 dapat dibangkitkan ulang hingga 100.000 | E2, E3, E6 |
| A13 | KB (regulasi + perusahaan), skema DSL | `kb/` | — | 📝 WP1–WP2, WP7 | Semua |
| A14 | Operator mutasi + mutan KB berlabel | `tests/mutasi/` | — | 📝 WP8 | E4 |
| A15 | Log adjudikasi + oracle teradjudikasi | `eksperimen/adjudikasi.md` | — | 📝 WP9 | E2 |

### 8.2 Kalibrasi data sintetis

Generator saat ini memakai distribusi kasar: gaji log-normal dengan median Rp7 juta, dan bobot status PTKP perkiraan. Di WP8 distribusi ini dikalibrasi sebagai berikut:
- **Gaji:** distribusi kelompok upah per sektor/provinsi (BPS Keadaan Pekerja, tabel 3.47 dan 4.16), dengan batas bawah UMP tahun bersangkutan (Kemnaker). Karena BPS melaporkan upah **bersih**, konversi bersih → bruto dimodelkan eksplisit memakai KB itu sendiri, yaitu invers PPh + BPJS. Konversi ini adalah asumsi yang dilaporkan.
- **Status PTKP:** proksi dari tabel status perkawinan dan ukuran rumah tangga BPS. Tidak ada tabel status kawin khusus pekerja.
- **Strata titik rawan (S2–S8)** dipertahankan dengan proporsi tetap terlepas dari kalibrasi, karena tujuannya menguji, bukan merepresentasikan populasi.
- Seluruh nilai uang yang dibangkitkan bertipe integer rupiah. Pecahan hanya muncul dari aturan (prorata, persentase) dan harus melewati registri pembulatan.

### 8.3 Celah data yang diketahui

- Tidak ada baseline OSS untuk tahun 2023 (lihat §10).
- Tidak ada contoh resmi untuk sejumlah skenario (§9.1). Area ini bergantung pada V2–V4.
- Upah tingkat atas (ekor distribusi, tempat sebagian besar PPh 21 dibayar) tidak terwakili di data BPS, sehingga ditutup oleh strata sintetis S2/S3/S5.

---

## 9. Validasi Tanpa SME: Piramida Oracle

Karena tidak ada SME dan kalkulator eksisting tidak dipercaya, kebenaran ditetapkan berlapis. Semakin tinggi lapisan, semakin tinggi otoritasnya tetapi semakin sedikit jumlah kasusnya.

```
        ▲ otoritas tinggi, kasus sedikit
   V1   │ Contoh resmi (lampiran PMK 168/2023, PER-16/PJ/2016, publikasi DJP)
   V2   │ Derivasi pasal + differential testing N-versi + adjudikasi tertulis
   V3   │ Metamorphic & property-based testing (ribuan–jutaan kasus)
   V4   │ Verifikasi formal Z3 (properti tabel, keberadaan/ketunggalan solusi)
        ▼ otoritas berbasis bukti, cakupan tak terbatas
```

### 9.1 V1 — Contoh resmi (gold standard)

- Setiap contoh perhitungan di lampiran PMK 168/2023 dan PER-16/PJ/2016 ditranskripsi menjadi kasus uji JSON di `dataset/07_kasus_uji_resmi/`. Setiap kasus memuat rujukan halaman.
- **Status: sudah dikerjakan.** [dataset/07_kasus_uji_resmi/](dataset/07_kasus_uji_resmi/) berisi **46 kasus dalam lingkup**, ditambah 4 kasus di luar lingkup yang ditranskripsi penuh dan 38 entri ringkas (manifest `index.csv`). Sumbernya: PMK 168/2023 (13, termasuk 3 kasus PNS bertanda `PNS`, dipakai hanya untuk validasi mekanisme TER + masa terakhir), PP 58/2023 (1), PER-16/PJ/2016 (22), serta DTP PMK 10/2025, 72/2025, 105/2025 (10). Setiap kasus diverifikasi dalam dua pass independen terhadap **gambar halaman PDF**, dan semua nilai `expected` cocok dengan dokumen.
- **Cakupan:**

  | Skenario | TER | PER-16 |
  |---|---|---|
  | Pemotongan bulanan | 23 | – |
  | Masa terakhir Desember | 16 | – |
  | Masa terakhir bulan keluar | 3 | – |
  | Bonus/THR | 11 | 4 |
  | Masuk tengah tahun | 5 | 2 |
  | DTP | 10 | – |
  | Zakat | 2 | 0 |
  | Gross-up / tunjangan pajak | 1 / 1 | 0 / 1 |
  | Pegawai wanita | 0 | 3 |

- **Celah V1 yang harus ditutup oleh V2–V4:** tahun 2023 dengan tarif HPP (contoh PER-16 berasal dari 2016 dan memakai tarif lama; hanya kasus dengan PKP ≤ Rp50 jt yang hasilnya identik di tarif 2023), premi BPJS Kes & iuran JP, pegawai wanita di rezim TER, gross-up setahun penuh, natura PMK 66/2023, status TK/1–TK/3, serta tahun 2025/2026 tanpa DTP.
- **V1 tidak menguji pembulatan.** Dari 170 perhitungan TER bulanan di contoh resmi, hanya 1 yang menghasilkan pecahan rupiah. Kecocokan V1 karena itu **bukan** bukti bahwa pembulatan sudah benar. Pembulatan divalidasi di S7 dan E10 (§6.9.2).
- **Contoh PER-16 yang dihitung ulang** dengan tarif HPP untuk tahun 2023 **turun status menjadi V2** (turunan, bukan emas). Hanya kasus dengan PKP ≤ Rp50 jt yang tetap V1.
- **Contoh resmi pun memuat salah cetak** (terkonfirmasi dari gambar halaman, bukan OCR):
  - PMK168-B-I.6: bruto 55.000.000, tetapi yang dikalikan 55.500.000;
  - PMK105-B-3: total baris 1.822.500, sedangkan jumlah barisnya 1.812.500;
  - PER16-I.1.3: biaya jabatan 525.000 melewati plafon;
  - PER16-I.2.3: premi justru dikurangkan dari bruto;
  - PER16-I.6.2.2: selisih Rp1;
  - beberapa subtotal lain salah meskipun hasil akhirnya benar.
- **Contoh resmi saling bertentangan:** pada skenario yang sama, PMK 10/2025 contoh 3 memplafon biaya jabatan **per bulan** (9 × 450.000 + 500.000 = 4.550.000), sedangkan PMK 105/2025 dan seluruh contoh PMK 168 memakai 5% × bruto dengan plafon n × 500.000 (= 4.750.000). Bunyi PMK 168 Pasal 10(2) memungkinkan kedua tafsir. Ini **ambiguitas regulasi nyata**. Di KB, keduanya dimodelkan sebagai varian aturan bertanda `tafsir`, dengan satu varian sebagai *default* yang dicatat di daftar asumsi. Sistem mengeluarkan peringatan `AMBIGU_TAFSIR` bila varian lain menghasilkan angka berbeda.
- Karena itu **protokol erratum** berikut berlaku:
  1. `expected` selalu menyimpan angka **sebagaimana tercetak** (tidak pernah "dibetulkan" diam-diam);
  2. kasus yang memuat erratum diberi label `erratum: true` dan nilai `expected_terkoreksi` diturunkan dari pasal, beserta alasan tertulis;
  3. metrik V1 dilaporkan dua kali: (a) terhadap `expected_terkoreksi` (target 0 selisih), dan (b) terhadap angka tercetak (selisihnya **harus tepat** di lokasi erratum, sehingga sistem juga berfungsi sebagai pendeteksi erratum);
  4. setiap koreksi wajib mengutip pasal dengan otoritas lebih tinggi (§6.9.6) dan ditinjau pembaca kedua sebelum dipakai. Ini mencegah "koreksi yang menguntungkan sistem sendiri".
- **Target: 0 selisih** terhadap `expected_terkoreksi`, per masa dan per komponen antara. Setiap ketidakcocokan diklasifikasikan sebagai *bug KB*, *erratum contoh resmi*, atau *ambiguitas tafsir* (masuk daftar asumsi).

### 9.2 V2 — Differential testing dan adjudikasi

- **Versi independen.** Terdiri atas (a) KB engine; (b) baseline B1 hard-coded yang ditulis langsung dari teks pasal tanpa melihat KB; (c) library open source B2; (d) xlsx B0 untuk 2023.
- **Prosedur.** Untuk setiap kasus sintetis, bandingkan semua versi **per masa dan per komponen antara**. **Tidak ada voting mayoritas.** Setiap kelas ketidaksesuaian ditelusuri ke teks pasal dan diputuskan dalam **log adjudikasi** (`eksperimen/adjudikasi.md`). Log memuat kasus, nilai tiap versi, pasal acuan beserta tingkat otoritasnya, keputusan, dan versi yang salah beserta penyebabnya.
- Hasil adjudikasi menjadi **oracle teradjudikasi** untuk metrik RQ2.
- Sisi lain dari prosedur ini: kesalahan pada kalkulator eksisting terdokumentasi sebagai temuan (*conformance study*).

**Pengaman independensi.** KB, B1, dan adjudikasi dibuat oleh orang yang sama, sehingga risiko terbesar adalah salah tafsir yang sama masuk ke ketiganya. Pengamannya:
1. **B1 dibekukan lebih dulu.** B1 ditulis dan di-*tag* git (`b1-frozen`) sebelum file KB regulasi pertama dibuat. Stempel waktu commit menjadi bukti urutan. Perbaikan B1 setelah pembekuan hanya boleh berasal dari putusan adjudikasi dan dicatat.
2. **Adjudikasi buta.** Skrip menampilkan nilai-nilai yang berselisih dengan label acak (X/Y/Z), tanpa nama sistem. Putusan ditulis berdasarkan pasal, baru kemudian label dibuka.
3. **Penengah eksternal per kelas.** Untuk **setiap kelas** selisih, minimal 3 kasus perwakilan dihitung manual di **kalkulator resmi DJP** (B3). Kalkulator DJP adalah satu-satunya implementasi independen yang berasal dari otoritas pajak. Bila putusan berbasis pasal berbeda dengan kalkulator DJP, kasus tersebut naik menjadi `tafsir` dan dilaporkan.
4. **Pembaca kedua untuk daftar asumsi.** Seluruh daftar asumsi dan putusan `tafsir` dibaca oleh pihak kedua, misalnya tim payroll kantor, rekan kuliah, atau dosen. Peran mereka bukan sebagai SME, melainkan untuk menangkap kesalahan baca pasal. Komentar dan tanggapannya dicatat.

### 9.3 V3 — Metamorphic & property-based testing (Hypothesis)

| MR | Relasi | Rezim |
|---|---|---|
| MR1 | Bruto naik (komponen lain tetap) → PPh masa tidak turun (metode gross) | semua |
| MR2 | Tanggungan bertambah (PTKP naik) → PPh setahun tidak naik | semua |
| MR3 | Σ PPh Jan–Des = PPh Pasal 17 atas PKP setahun (identitas masa pajak terakhir) | 2024+ |
| MR4 | Gross-up: T = PPh_int(B + T) **persis** (integer). Simpangan (bruto − PPh − B) dilaporkan, bukan diasumsikan 0 | semua |
| MR5 | Memindahkan bonus antar-bulan (Jan–Nov, dalam tahun pajak yang sama, pegawai setahun penuh, tanpa DTP) tidak mengubah total setahun | 2024+ |
| MR6 | Memecah komponen tunjangan tetap menjadi dua komponen sejumlah sama → output identik | semua |
| MR7 | Menambah aturan dengan masa berlaku di luar tahun *t* → output tahun *t* identik | semua |
| MR8 | Memisahkan satu file kebijakan menjadi dua file setara → output identik | semua |
| MR9 | Kategori TER yang dipilih konsisten dengan status PTKP (tidak bergantung bruto) | 2024+ |
| MR10 | Penghasilan neto setahun ≤ PTKP → PPh setahun = 0 | semua |
| MR11 | Setiap fakta bertipe uang adalah `int` (tidak ada pecahan/float yang lolos ke output) | semua |
| MR12 | Rekonsiliasi buku besar: Σ komponen bruto = bruto; bruto − pengurang = neto; Σ PPh masa (termasuk masa terakhir) = PPh setahun | semua |
| MR13 | Isolasi pembulatan: mengganti mode pembulatan suatu titik `tafsir` hanya mengubah angka yang bergantung pada titik itu (diverifikasi terhadap graf dependensi) | semua |
| MR14 | Sumbu waktu: memindahkan `tanggal_bayar` di dalam bulan yang sama tidak mengubah output; memindahkannya melewati batas bulan atau tahun hanya mengubah masa yang bersangkutan | semua |
| MR15 | Kesetaraan representasi: input yang sama dalam urutan komponen berbeda menghasilkan output bit-identik | semua |

Properti juga dipakai untuk **mutation testing**, yaitu mengukur seberapa sensitif *test suite* terhadap kesalahan KB (§11.4).

### 9.4 V4 — Verifikasi formal Z3

- Kelengkapan dan ketidaktumpangtindihan lapisan TER/Pasal 17 untuk semua x ≥ 0, dalam sort `Int` dengan semantik interval (a, b].
- Monotonisitas f(T) **setelah pembulatan**, sebagai syarat Knaster–Tarski di domain integer.
- Pasal 17 atas PKP kelipatan ribuan selalu menghasilkan rupiah bulat (dasar BULAT-P17-01).
- Enumerasi pita solusi ganda gross-up per kategori dan batas lapisan (RQ5), di domain real dan integer.
- Konsistensi konfigurasi perusahaan terhadap aturan wajib.

### 9.5 Matriks Aturan × Tingkat Bukti

Setiap aturan KB dipetakan ke bukti terkuat yang memvalidasinya:

| Tingkat | Bukti | Label |
|---|---|---|
| BK-1 | ≥ 1 kasus V1 yang mengaktifkan aturan tersebut dan cocok | keyakinan tinggi |
| BK-2 | Cocok dengan kalkulator DJP pada ≥ 3 kasus | keyakinan tinggi |
| BK-3 | Hanya oracle teradjudikasi (V2) + properti (V3) | **keyakinan rendah** |
| BK-4 | Tidak ada bukti selain derivasi penulis | **tidak tervalidasi** (dilarang untuk evaluasi akhir) |

- Matriks dibangkitkan otomatis dari jejak eksekusi: aturan mana yang aktif di kasus mana.
- Setiap aturan berlabel BK-3 atau BK-4 wajib dinaikkan ke BK-2 lewat uji manual kalkulator DJP, atau dilaporkan eksplisit di bagian keterbatasan.
- Calon BK-3 yang sudah diketahui sekarang: premi BPJS Kes, iuran JP, karyawati di rezim TER, tarif 2023 pasca-HPP untuk PKP > Rp50 jt, natura PMK 66/2023, pembulatan, dan gross-up tahunan.

### 9.6 Integritas tabel parameter (double-entry)

Tabel di `dataset/01_regulasi/tables/` saat ini berasal dari **satu** jalur ekstraksi. Jalur itu sudah dicocokkan dengan sumber sekunder dan contoh resmi, tetapi tetap merupakan *single point of failure*. Sebelum tabel dipakai di KB:
1. **Ekstraksi kedua yang independen** dengan metode berbeda, yaitu transkripsi manual dari gambar halaman PDF, bukan dari lapisan teks.
2. **Perbandingan sel demi sel** dengan target 0 selisih. Setiap selisih diputuskan dengan melihat gambar halaman.
3. **Hash SHA-256** setiap tabel final dicatat di manifest KB. Loader menolak tabel yang hash-nya tidak cocok.
4. Ekstraksi tabel yang belum ada: batas nilai natura per jenis (PMK 66/2023), serta daftar KLU sektor DTP (lampiran PMK 10/2025, 72/2025, 105/2025).

---

## 10. Pembanding (Baseline)

> Tidak ada leaderboard "SOTA" berbasis ML untuk perhitungan PPh 21. Di domain *Rules as Code*, *state of the art* yang relevan adalah (i) implementasi praktik yang tersedia dan (ii) kerangka *rules-as-code* mutakhir. Keduanya dipakai sebagai pembanding. **Semua baseline berstatus *system under test*, bukan oracle.**

Survei [dataset/03_pembanding/README.md](dataset/03_pembanding/README.md) menemukan 35 kandidat OSS, 7 di antaranya di-clone penuh, ditambah 22 kalkulator online. **Ketujuh repo OSS memiliki kesalahan terverifikasi.** Hanya satu yang cocok dengan kasus acuan sederhana. Ini menegaskan keputusan D9.

| ID | Pembanding | Jenis | Tahun | Dipakai untuk | Catatan kebenaran (bukan oracle) |
|---|---|---|---|---|---|
| **B0** | xlsx Perusahaan X v8 | Spreadsheet, aturan di sel | 2023 | E1 (PER-16), E3 (biaya perubahan dalam jumlah sel), E8 | 10 temuan audit (Lampiran D) |
| **B1** | Implementasi *hard-coded* Python (dibangun di WP6 langsung dari teks pasal) | Prosedural if-else | 2023–2026 | Pembanding kontrafaktual yang adil: fitur sama, aturan di kode → E2, E3, E7 | Versi independen kedua untuk V2 |
| **B2a** | `muhroyhan/pph21` (TS, MIT) | Library | 2024–2026 | Differential utama (E2) | Paling benar; bug bruto non-integer, tanpa gross-up/zakat/2023, tanpa annualisasi pegawai baru |
| **B2b** | `Peco-lab/id-payroll` (Python, MIT) | Library | 2024+ | Differential + uji sensitivitas (bug terdokumentasi: BPJS Kes tidak masuk bruto, lebih bayar dipotong ke 0) | Selisih yang dapat dijelaskan menjadi *positive control* |
| **B2c** | `teknologi-umum/pph21` (TS, MPL-2.0) | Library | 2024+ | *Mutant* alami: tabel TER & Pasal 17 salah | Kontrol untuk recall deteksi |
| **B2d** | `open-synergy` (Odoo, AGPL) + `pajakin` (tanpa lisensi; hanya metrik) | Aplikasi | 2023–2026 | Studi biaya pemeliharaan dari riwayat git (E3): commit TER, misalnya open-synergy 5d33b69 (+163 baris logika); pajakin be3c9a6 (+504) | Versi TER open-synergy cacat; pajakin tanpa true-up Desember |
| **B3** | Kalkulator online: **DJP kalkulator.pajak.go.id** (resmi), Ortax, DDTCNews | Black-box manual | 2024–2026 (Ortax/DDTC juga pra-2024) | Uji manual ±20–30 kasus terpilih (titik rawan, gross-up) | ToS sebagian melarang otomasi; hanya manual. Kalkulator DJP berotoritas tinggi tetapi tetap bukan teks hukum |
| **B4** | OpenFisca (dan Catala sebagai pembanding konseptual) | Rules-as-code | — | Ekspresivitas (E7) [OPSIONAL]: implementasi subset katalog | Tidak ada paket Indonesia; siklus memicu `CycleError` sehingga gross-up tidak native |

Catatan: tidak ada baseline OSS yang layak untuk 2023. Untuk 2023 dipakai contoh PER-16, B0, B1, dan Ortax mode pra-2024 (manual).

---

## 11. Metrik Evaluasi

Pemilihan metrik mengikuti sifat tugas. Perhitungan pajak bersifat **deterministik dan bernilai rupiah**, sehingga metrik utamanya adalah kecocokan dan galat numerik, bukan F1. **F1 hanya dipakai pada tugas yang memang berupa klasifikasi biner**: deteksi kesalahan/konflik, dan prediksi output mana yang terdampak perubahan.

### 11.1 Kebenaran (RQ2) — kriteria penerimaan

**Satuan pemeriksaan** adalah tupel (kasus, masa, fakta), dengan fakta mencakup setiap komponen antara:

> bruto per komponen · premi objek · kategori TER · lapisan & tarif · PPh masa · biaya jabatan · iuran pengurang · neto · PTKP · PKP · PPh setahun · PPh masa terakhir · tunjangan pajak · DTP

Pemeriksaan **tidak boleh hanya pada total tahunan**, karena masa pajak terakhir selalu menyamakan total setahun sehingga galat bulanan tertutup (pelajaran K-02).

| Metrik | Definisi | Target |
|---|---|---|
| **Selisih tak terjelaskan (STJ)** | Jumlah tupel dengan ŷ ≠ y yang belum punya kelas akar masalah | **0** (kriteria lulus) |
| **Jumlah selisih per kelas** | Kelas: bug KB · erratum contoh resmi · tafsir · bug pembanding · input tidak valid | Dilaporkan semua |
| **MaxAE** | Selisih maksimum dalam rupiah, per kelas dan per strata | 0 untuk kelas "bug KB" |
| **EMR** | % tupel dengan ŷ = y persis. Deskriptif, bukan target, karena nilainya bergantung pada generator | — |
| **Selisih dalam rupiah per bucket** | Jumlah tupel dengan selisih {Rp1, Rp2–99, Rp100–999, ≥ Rp1.000} | Hanya **diagnosis**: selisih Rp1 biasanya pembulatan, sedangkan ≥ Rp1.000 biasanya logika. Bukan toleransi |
| **Lebar rentang tafsir** | Untuk setiap angka: max − min nilai antar-varian `tafsir` | Dilaporkan per aturan tafsir sebagai eksposur risiko |

Aturan pelaporan:
- Tidak ada toleransi. Selisih Rp1 diperlakukan sama dengan selisih Rp1 juta, sampai kelasnya diketahui.
- Rata-rata galat (MAE) **tidak** dipakai sebagai metrik utama karena menyembunyikan kasus salah.
- Tidak ada uji signifikansi untuk klaim kebenaran. Perbandingan antar-sistem dilaporkan sebagai jumlah tupel benar/salah dan daftar contoh tandingan.

### 11.1b Kecukupan pengujian (menggantikan persentase sintetis sebagai bukti)

| Metrik | Definisi | Target |
|---|---|---|
| **Cakupan aturan** | % aturan KB yang pernah aktif di test suite | 100% |
| **Cakupan kondisi** | Setiap kondisi `jika` pernah bernilai benar **dan** salah, dan setiap kondisi terbukti memengaruhi hasil (gaya MC/DC) | 100% |
| **Cakupan batas** | Setiap batas lapisan (TER per kategori, Pasal 17, plafon biaya jabatan, batas upah BPJS, batas DTP Rp10 jt) diuji di {b−1, b, b+1} dan nilai pecahan | 100% |
| **Cakupan kombinasi** | *Pairwise*: status PTKP × metode × masuk/keluar × THR/bonus × DTP × tahun × jenis kelamin | 100% pasangan |
| **Cakupan titik pembulatan** | Setiap entri registri pembulatan pernah menerima nilai pecahan (≠ ,0) | 100% |
| **Matriks bukti** | Proporsi aturan per tingkat BK-1..BK-4 (§9.5) | 0 aturan BK-4; BK-3 dilaporkan |

### 11.2 Adaptabilitas terhadap perubahan (RQ3)

| Metrik | Definisi |
|---|---|
| **Zero-code-change rate** | % skenario perubahan (Lampiran B) yang tertangani tanpa menyentuh kode engine |
| **Change size** | Jumlah entri KB yang diubah vs jumlah file/fungsi/baris kode yang diubah pada B1 dan B2 (`git diff --stat`) dan sel rumus pada B0 |
| **Impact precision / recall / F1** | Untuk setiap skenario, oracle mendefinisikan himpunan **S\*** = (kasus, masa) yang *seharusnya* berubah. **S** = yang *benar-benar* berubah setelah pembaruan. Precision = \|S∩S\*\|/\|S\|, recall = \|S∩S\*\|/\|S\*\|. Precision < 1 berarti ada efek samping, recall < 1 berarti pembaruan tidak lengkap |
| **Correctness after change** | EMR pada S\* setelah pembaruan |
| **Regression rate** | % output di luar S\* yang ikut berubah (harus 0) |
| **Change propagation reach** | Jumlah aturan/fakta yang tersentuh perubahan dalam graf dependensi (ukuran lokalitas) |

### 11.3 Ekspresivitas (RQ1)

- **Coverage** = % kebijakan katalog (20 entri) yang dapat dinyatakan pada tiga tingkat:
  - *native* (hanya KB);
  - *workaround* (KB, tetapi tidak elegan atau butuh komponen bantu);
  - *tidak bisa* (butuh kode).
- Dihitung untuk KB ini, B1, B2, B4 (OpenFisca), dan B3 (konfigurasi kalkulator/vendor berdasarkan dokumentasi publik).
- **Ukuran spesifikasi** per kebijakan: jumlah baris YAML vs baris kode.

### 11.4 Deteksi kesalahan & konflik (RQ4) — penggunaan F1 yang sahih

- **Himpunan uji berlabel**, dibuat dengan *mutation testing* pada KB:
  - **operator mutasi:** ubah tarif, geser batas lapisan, buat celah/tumpang tindih lapisan, tumpang tindihkan masa berlaku, salah petakan kategori objek, hapus aturan, ubah status `wajib` → `default`;
  - **operator mutasi presisi:** batas lapisan ±Rp1 (*off-by-one*), interval (a, b] → [a, b), mode pembulatan (bawah ↔ setengah-atas ↔ setengah-genap), satuan pembulatan PKP (ribuan → rupiah), urutan pembulatan (per komponen ↔ setelah jumlah), sumbu waktu (`saat_terutang` → `periode_kerja`), dan tarif ditulis float;
  - **mutan ekuivalen** (tidak mengubah output apa pun pada domain valid) diidentifikasi lewat Z3 atau enumerasi, lalu dikeluarkan dari penyebut mutation score agar metrik tidak bias;
  - **konflik kebijakan berlabel:** kebijakan katalog yang sengaja dibuat melanggar aturan wajib;
  - kedua jenis dicampur dengan mutan/kebijakan *aman* sebagai kelas negatif.
- **Metrik:**
  - Precision, recall, F1 dari verifikator statis (§6.6) + resolusi konflik (§6.3);
  - **mutation score** *test suite* = % mutan yang terbunuh oleh V1–V3 (metrik standar kecukupan pengujian);
  - kedua metrik dilaporkan per operator mutasi.

### 11.5 Penjelasan (explanation facility)

- **Trace completeness** = % angka output yang memiliki jejak hingga aturan dan pasal sumber (target 100%).
- **Trace fidelity** = menjalankan ulang perhitungan hanya dari jejak menghasilkan angka yang sama (target 100%, diperiksa otomatis).

### 11.6 Gross-up (RQ5)

- Jumlah dan lebar total pita solusi ganda per kategori TER, **di domain real dan setelah pembulatan (integer)**, beserta jumlah kandidat analitis yang gugur saat diverifikasi secara integer.
- Untuk gross-up tahunan (masa pajak terakhir): keberadaan dan ketunggalan solusi, serta kasus dengan T_Des negatif (lebih bayar).
- Selisih maksimum biaya pemberi kerja antar-solusi (Rp/bulan).
- Iterasi naif vs enumerasi analitis: % kasus S3 di mana iterasi naif berosilasi atau memilih solusi berbeda.

### 11.7 Kinerja

Latensi per pegawai-tahun, throughput untuk 10.000 pegawai, dan skalabilitas terhadap jumlah aturan. Ini hanya informasi pendukung, bukan klaim utama.

---

## 12. Desain Eksperimen

| ID | Eksperimen | Data | Sistem | Metrik | RQ | Prioritas |
|---|---|---|---|---|---|---|
| **E1** | Kebenaran terhadap contoh resmi | `07_kasus_uji_resmi` | KB, B1, B2, B0 (2023) | STJ = 0, selisih per kelas, per masa & per komponen | RQ2 | [INTI] |
| **E2** | Differential testing & conformance | `06_kasus_uji_sintetis` (strata S1–S8) | KB, B1, B2 | STJ = 0 vs oracle teradjudikasi, MaxAE per kelas, cakupan §11.1b | RQ2 | [INTI] |
| **E3** | Skenario perubahan | Lampiran B + S6 | KB vs B1 (+ riwayat git B2, + B0) | §11.2 | RQ3 | [INTI] |
| **E4** | Deteksi kesalahan & konflik | mutan KB + konflik berlabel | verifikator KB | P/R/F1, mutation score | RQ4 | [INTI] |
| **E5** | Studi ablasi | E1–E4 | KB dengan 1 fitur dimatikan | jumlah tupel salah + contoh tandingan konkret per varian | semua | [INTI] |
| **E6** | Analisis gross-up | tabel TER (A/B/C) + S3 | Z3 + engine | §11.6 | RQ5 | [INTI] analitis; [OPSIONAL] uji ke B2 |
| **E7** | Ekspresivitas | katalog 20 kebijakan | KB, B1, B2, B3, B4 | coverage | RQ1 | [INTI] KB & B1; [OPSIONAL] B4 |
| **E8** | Studi kasus Perusahaan X | input xlsx 2023 | KB vs B0 | per-sel EMR, daftar selisih + adjudikasi; lalu pegawai yang sama dihitung ulang dengan rezim 2024–2026 | RQ2, RQ3 | [INTI] |
| **E9** | Kinerja | 10k pegawai sintetis | KB | latensi | — | [OPSIONAL] |
| **E10** | **Kalibrasi pembulatan & tafsir** | Strata S7 (bruto pecahan) + kasus perwakilan setiap aturan `tafsir` | KB (semua varian) vs kalkulator DJP (manual) | Varian yang cocok dengan DJP; lebar rentang tafsir; aturan yang naik BK-3 → BK-2 | RQ2 | [INTI] |
| **E11** | **Sumbu waktu** | Strata S8 (gaji Desember dibayar Januari, THR sebelum Lebaran, rapel lintas tahun) | KB vs B1 vs DJP | STJ = 0; MR14 | RQ2 | [INTI] |

**Prosedur E10.**
1. Untuk setiap titik pembulatan berstatus `tafsir`, pilih ≥ 5 kasus yang hasil antar-variannya berbeda. Pemilihan dilakukan otomatis dari rentang tafsir.
2. Hitung kasus-kasus itu secara manual di kalkulator DJP.
3. Varian yang cocok dengan DJP di **semua** kasus menjadi default yang terdokumentasi.
4. Bila tidak ada varian yang konsisten dengan DJP, titik tersebut dilaporkan sebagai ketidakpastian regulasi dan rentang tafsirnya ditampilkan di output.

Kalkulator DJP tidak menggantikan pasal. Namun untuk hal yang tidak diatur pasal, kalkulator DJP adalah bukti terkuat tentang praktik otoritas pajak.

### 12.1 Konfigurasi ablasi (E5)

| Varian | Fitur yang dimatikan | Prediksi dampak |
|---|---|---|
| A0 | — (sistem penuh) | acuan |
| A1 | **Versi waktu** (hanya KB terbaru) | EMR tahun 2023 runtuh; MR7 gagal |
| A2 | **Lapisan perusahaan** (regulasi + kebijakan default) | EMR studi kasus E8 turun; ekspresivitas turun |
| A3 | **Resolusi konflik** (perusahaan selalu menang) | Hasil ilegal tidak terdeteksi; recall E4 turun |
| A4 | **Penyelesai titik tetap**, diganti iterasi naif dengan batas 50 iterasi | Osilasi/solusi tak konsisten di S3 |
| A5 | **Registri pembulatan** (tanpa pembulatan eksplisit; nilai antara tetap eksak) | Selisih Rp1–Rp999 pada S7; MR11 gagal |
| A6 | **Verifikasi statis** | Mutation score dan F1 E4 turun |
| A7 | **Kategori objek wajib** pada komponen | Salah klasifikasi premi/natura lolos |
| A8 | **Aritmetika eksak** (diganti `float`) | Selisih Rp1 (uji awal: 700 kasus pada grid TER × bruto kelipatan Rp1.000) |
| A9 | **Model tiga tanggal** (masa = periode kerja) | Salah masa pada S8, misalnya THR yang dibayar sebelum bulan Lebaran |

---

## 13. Novelty Akademis

### 13.1 Bukan novelty (diadopsi, dikutip)

Pemisahan aturan dari kode (*rules engine*, Catala, OpenFisca); lapisan regulasi yang dapat ditimpa per tenant (Payroll Engine); iterasi gross-up; dan kalkulator/sistem pakar PPh 21 (banyak penelitian Indonesia).

### 13.2 Kontribusi yang diklaim

1. **N1 — KB dua lapis dengan resolusi konflik berbasis asas hukum untuk PPh 21.** Hubungan regulasi ↔ kebijakan pemberi kerja dimodelkan eksplisit dengan sifat `wajib/default/opsional` dan asas *lex superior/specialis/posterior* sebagai strategi resolusi konflik di agenda forward chaining. Hasilnya, pelanggaran kebijakan terhadap aturan wajib **terdeteksi secara otomatis** dan terukur lewat F1 dan mutation score. Sejauh penelusuran awal, kerangka payroll berlapis yang ada hanya mengenal *override*, tanpa pembatasan berbasis sifat aturan.
2. **N2 — Versi waktu bitemporal dan evaluasi dampak perubahan.** Satu KB mencakup dua rezim (PER-16 → TER) dan pembaruan tahunan (batas JP, DTP). Diusulkan pula metrik **impact precision/recall/F1** dan uji isolasi temporal metamorfik sebagai cara mengukur *adaptabilitas* sistem berbasis pengetahuan. Ini ukuran yang lebih ketat daripada "jumlah baris yang berubah".
3. **N3 — Perlakuan deklaratif definisi melingkar dengan jaminan formal.** Gross-up dinyatakan sebagai definisi titik tetap. Keberadaannya dijamin oleh Knaster–Tarski, dan pita solusi gandanya di bawah TER dikarakterisasi lengkap per kategori dan lapisan, disertai aturan penyelesaian kanonik (titik tetap terkecil).
4. **N4 — Artefak terbuka.** KB PPh 21 2023–2026 yang dapat dibaca mesin, kasus uji resmi terstruktur (beserta katalog erratum contoh resmi), relasi metamorfik, operator mutasi KB, registri pembulatan, dan katalog kebijakan.
5. **N5 (pendukung) — Ketidakpastian tafsir sebagai keluaran kelas satu.** Ketentuan yang tidak diatur tegas (pembulatan, plafon biaya jabatan masa kerja < 12 bulan, dan sebagainya) direpresentasikan sebagai varian aturan `tafsir`. Sistem melaporkan **rentang tafsir** per angka, bukan satu angka yang tampak pasti. Klaim ini moderat, karena konsepnya mirip *default logic* di Catala, tetapi penerapannya pada akurasi rupiah payroll belum ditemukan di penelusuran awal.

### 13.3 Penilaian jujur

- Novelty berada di tingkat **terapan/rekayasa pengetahuan**, cukup kuat untuk tugas KBS dan artikel SINTA 2–3. Untuk Scopus Q2, perlu bukti kuat dari N2 dan N3.
- Klaim "belum ada" pada N1–N3 berbasis penelusuran awal dan **wajib dikonfirmasi** lewat tinjauan pustaka di WP0.
- Jika differential testing menemukan kesalahan nyata di kalkulator eksisting, temuan itu memperkuat motivasi, tetapi **bukan** klaim utama.

---

## 14. Arsitektur dan Paket Kerja

### 14.1 Struktur repositori

```
kb_payroll/
├── research_plan.md
├── dataset/                       # §8 — data mentah & turunan
│   ├── 01_regulasi/  02_studi_kasus/  03_pembanding/  04_data_publik/
│   ├── 05_katalog_kebijakan/  06_kasus_uji_sintetis/  07_kasus_uji_resmi/
├── kb/
│   ├── skema/                     # JSON Schema DSL & fakta
│   ├── regulasi/                  # *.yaml + tabel/*.csv, berversi waktu
│   └── perusahaan/                # perusahaan_x.yaml, katalog KP-01..KP-20
├── engine/                        # loader, validator, resolver, agenda, fixpoint, explain
├── verifikasi/                    # pemeriksaan Z3 & graf
├── baselines/
│   ├── b1_hardcoded/              # implementasi prosedural dari teks pasal
│   └── adapters/                  # pembungkus library OSS
├── tests/                         # V1 resmi, V3 metamorfik/property, mutasi
├── eksperimen/                    # E1–E9, adjudikasi.md, hasil/*.csv
└── app/                           # Streamlit: kalkulator, editor kebijakan, jejak
```

### 14.2 Paket kerja (tanpa jadwal; urutan = ketergantungan)

Urutan wajib: **WP1a (kontrak presisi) → WP1b + WP1c → WP6 (B1, lalu dibekukan) → WP2 → WP3 → …**. B1 harus selesai dan dibekukan sebelum KB regulasi ditulis, agar independensinya dapat dibuktikan.

| WP | Isi | Definition of Done | Prioritas |
|---|---|---|---|
| WP0 | Tinjauan pustaka terarah (KBS pajak/payroll, Rules as Code, konflik norma, gross-up) | Tabel pembeda 10–15 karya; klaim N1–N3 dikonfirmasi atau direvisi | [INTI] |
| **WP1a** | **Kontrak presisi** (§6.9): tipe uang/tarif, loader YAML tanpa float, registri pembulatan, skema interval, model tiga tanggal, validasi input, format metadata audit. **Dikerjakan pertama, sebelum kode lain**. ✅ **Selesai 2026-10-01**: `engine/` (angka, pembulatan, muat, interval, waktu, audit), `kb/regulasi/pembulatan.yaml`, `kb/regulasi/tabel_manifest.yaml`, 135 tes lulus, termasuk V1: 169/170 TER bulanan dan 25/25 Pasal 17 resmi direproduksi, dengan satu-satunya selisih tepat di erratum PMK168-B-I.6 | Tes AR-3 (tanpa float) + MR11 lulus pada kerangka kosong; registri memuat seluruh titik §6.9.2 | [INTI] |
| WP1b | Kodifikasi regulasi → tabel kodifikasi (kondisi/akibat/pengecualian/parameter/berlaku/pasal/sumbu waktu/titik pembulatan) + daftar asumsi `tafsir` beserta varian | Setiap aturan Lampiran A punya baris kodifikasi, pasal, dan tingkat otoritas | [INTI] |
| WP1c | Double-entry tabel parameter (§9.6) + ekstraksi tabel natura & KLU DTP | 0 selisih antar-ekstraksi; hash tercatat | [INTI] |
| WP2 | Skema DSL + KB regulasi 2023 & 2024–2026 | Lolos validasi skema & verifikasi statis | [INTI] |
| WP3 | Engine: loader, resolver, agenda, masa terakhir, penjelasan | Uji unit lulus; trace fidelity 100% | [INTI] |
| WP4 | Penyelesai titik tetap + analisis gross-up (Z3) | Peta pita solusi ganda A/B/C | [INTI] |
| WP5 | Transkripsi contoh resmi → `07_kasus_uji_resmi` (dua pass, independen). **Sudah selesai: 46 kasus.** Sisa: menambahkan `expected_terkoreksi` + alasan untuk setiap kasus `erratum`, serta menyelesaikan contoh di PMK 66/2023 dan PMK 81/2024 yang belum diperiksa | Setiap erratum punya koreksi berbasis pasal | [INTI] |
| WP6 | Baseline B1 hard-coded (ditulis dari pasal, tanpa melihat KB, tunduk pada kontrak presisi) + adapter B2. **Dikerjakan sebelum WP2** dan dibekukan dengan tag `b1-frozen` | B1 lulus V1; tag dibuat sebelum commit KB pertama | [INTI] |
| WP7 | Lapisan perusahaan: Perusahaan X + katalog 20 kebijakan | E7 & E8 dapat dijalankan | [INTI] |
| WP8 | Test suite V3 (MR1–MR15) + operator mutasi (termasuk mutasi presisi) + strata S7/S8 + pengukur cakupan §11.1b | Seluruh target cakupan §11.1b tercapai | [INTI] |
| WP9 | Eksperimen E1–E8, E10, E11 + adjudikasi buta + uji manual kalkulator DJP + matriks bukti | STJ = 0; 0 aturan BK-4; semua tabel hasil terisi | [INTI] |
| WP10 | Aplikasi Streamlit (kalkulator, editor kebijakan, tampilan jejak) | Demo end-to-end | [OPSIONAL] |
| WP11 | Penulisan laporan/artikel + rilis artefak | Laporan + repositori publik | [INTI] |

### 14.3 Teknologi

Python 3.12 (venv `env/`); PyYAML + `jsonschema`; `z3-solver`; `pytest` + `hypothesis`; `pandas`; `pdfplumber` (ekstraksi tabel regulasi); Streamlit [OPSIONAL]. Semua sudah terpasang di `env/` (openpyxl, pandas, pyyaml, jsonschema, pdfplumber, pypdf, z3-solver, hypothesis, pytest), kecuali `streamlit` [OPSIONAL]. Baseline B2a/B2c memerlukan Node.js (sudah dipakai saat survei).

---

## 15. Risiko, Ancaman Validitas, dan Etika

### 15.1 Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Salah tafsir pasal tanpa SME | Oracle salah | Piramida oracle; daftar asumsi eksplisit; setiap adjudikasi mengutip pasal; contoh resmi sebagai jangkar; pengaman independensi §9.2; matriks bukti §9.5 |
| Selisih Rp1 akibat representasi angka | Hasil salah secara diam-diam | Kontrak aritmetika AR-1..AR-5; ablasi A8 membuktikan dampaknya |
| Pembulatan yang tidak diatur regulasi | Satu angka benar menurut satu tafsir, salah menurut tafsir lain | Registri pembulatan; kalibrasi ke kalkulator DJP (E10); rentang tafsir ditampilkan di output |
| Salah masa pajak (tanggal bayar ≠ periode kerja) | PPh masuk masa/tahun yang salah | Model tiga tanggal (§6.9.4); strata S8; E11 |
| Tabel parameter salah ketik | Semua hasil salah secara sistematis | Double-entry + hash (§9.6); Z3 kelengkapan & monotonisitas |
| Kalkulator DJP berubah atau tidak tersedia | Penengah eksternal hilang | Catat tanggal akses dan tangkapan layar setiap uji manual; simpan sebagai bukti |
| Contoh resmi sedikit untuk kasus tertentu (gross-up, DTP, keluar tengah tahun) | V1 lemah di area itu | Andalkan V2–V4; laporkan cakupan V1 per jenis kasus secara terbuka |
| Library OSS sedikit/usang | Differential testing lemah | B1 independen menjamin minimal 2 versi; B2 sebagai pelengkap |
| PMK/PER menetapkan prosedur gross-up tertentu | RQ5 berubah | Analisis bergeser ke konsistensi & ketunggalan prosedur resmi |
| Regulasi baru terbit selama penelitian | KB harus diperbarui | Justru menjadi skenario perubahan tambahan untuk E3 |
| Cakupan melebar | Tidak selesai | Prioritas [INTI]/[OPSIONAL]; ruang lingkup §4 dikunci |

### 15.2 Ancaman validitas

- **Internal:** penulis KB dan B1 adalah orang yang sama, sehingga ada risiko kesalahan tafsir yang sama di keduanya (*common-mode failure*). *Mitigasi:* B1 dibekukan lebih dulu (tag git), adjudikasi buta, penengah kalkulator DJP per kelas selisih, dan pembaca kedua untuk daftar asumsi (§9.2). Risiko sisa dilaporkan lewat matriks bukti (§9.5).
- **Konstruk (kebenaran):** kecocokan total tahunan bukan bukti kebenaran bulanan, karena masa pajak terakhir selalu menyamakan total. *Mitigasi:* pemeriksaan per masa dan per komponen antara (§11.1).
- **Konstruk:** "jumlah baris berubah" adalah proksi biaya pemeliharaan. *Mitigasi:* lengkapi dengan impact F1 dan regression rate.
- **Eksternal:** satu studi kasus perusahaan. *Mitigasi:* katalog 20 kebijakan dari sumber regulasi dan praktik umum.
- **Kesimpulan:** data sintetis bisa tidak representatif. *Mitigasi:* strata titik rawan + distribusi gaji/PTKP dari data publik BPS (§8).

### 15.3 Etika & data

- [payroll_calculator.xlsx](payroll_calculator.xlsx) memuat **sheet tersembunyi berisi data pribadi** (nama lengkap, NIK 16 digit, NPWP) di sheet *Timesheet QDN - 2023*, *Data Gaji*, dan *PPh 21 2023 EX*. Sheet-sheet ini **tidak dipakai, tidak disalin, dan file xlsx asli tidak boleh dipublikasikan atau diunggah**. Hanya turunan teranonimkan di `dataset/02_studi_kasus/` yang boleh dirilis.
- Kalkulator online diuji hanya secara manual dan dalam jumlah terbatas, sesuai ketentuan layanan dan `robots.txt`. Tidak dilakukan *scraping* otomatis bila dilarang.
- Ketidaksesuaian pada library OSS dilaporkan ke pengembangnya (*responsible disclosure*) sebelum dipublikasikan.
- Sistem ini prototipe penelitian, bukan alat konsultasi pajak resmi.

---

## 16. Daftar Luaran

1. KB PPh 21 (regulasi 2023–2026 + Perusahaan X + katalog) dalam YAML/CSV beserta skema.
2. Engine forward chaining dengan resolusi konflik, penyelesai titik tetap, dan fasilitas penjelasan.
3. Test suite: kasus resmi, MR1–MR15, operator mutasi (termasuk mutasi presisi), strata S7/S8, dan laporan cakupan.
4. Laporan eksperimen E1–E8, E10, E11; log adjudikasi; matriks bukti; registri pembulatan & rentang tafsir; peta pita gross-up (real dan integer).
5. Laporan tugas KBS / draf artikel.
6. [OPSIONAL] Aplikasi Streamlit.

---

## 17. Referensi

**Ilmiah dan sistem** (detail bibliografi lengkap dicari di WP0):
1. Dumancic, S., Meert, W., Goethals, S., Stuyckens, T., Huygen, J., & Denies, K. (2021). *Automated Reasoning and Learning for Automated Payroll Management.* AAAI-21, 35(17), 15107–15116.
2. Liu, Y., & Liu, B. (2011). *The Preliminary Investigation of Salary Management System Rule-Based Rules Engine.* SciTePress.
3. Merigoux, D., Chataing, N., & Protzenko, J. (2021). *Catala: A Programming Language for the Law.* Proc. ACM Program. Lang. (ICFP).
4. OpenFisca — https://openfisca.org (AGPL-3.0).
5. Payroll Engine — https://payrollengine.org (MIT).
6. Tarski, A. (1955). *A lattice-theoretical fixpoint theorem and its applications.* Pacific J. Math., 5(2), 285–309.
7. de Moura, L., & Bjørner, N. (2008). *Z3: An Efficient SMT Solver.* TACAS 2008.
8. Chen, T. Y., et al. (2018). *Metamorphic Testing: A Review of Challenges and Opportunities.* ACM Computing Surveys, 51(1).
9. Jia, Y., & Harman, M. (2011). *An Analysis and Survey of the Development of Mutation Testing.* IEEE TSE, 37(5).
10. McKeeman, W. M. (1998). *Differential Testing for Software.* Digital Technical Journal, 10(1).
11. Preece, A. (1998/2001). Literatur verifikasi & validasi knowledge-based systems (anomali: redundansi, konflik, ketidaklengkapan, siklus) — dipakai untuk §6.6.
12. Holzenberger, N., Blair-Stanek, A., & Van Durme, B. (2020). *A Dataset for Statutory Reasoning in Tax Law Entailment and Question Answering.*
13. Muninggar, N. S., & Krisnadhi, A. A. (2023). *LexID.* Jurnal Ilmu Komputer dan Informasi, 16(1).
14. Penelitian Indonesia no. 9–16 pada proposal (Tan & Putri 2020; Sari dkk. 2015; dan seterusnya).

**Regulasi** (PDF dan URL sumber lengkap ada di [dataset/01_regulasi/README.md](dataset/01_regulasi/README.md)): UU 36/2008 s.t.d.t.d. UU 7/2021 (HPP); PMK 101/PMK.010/2016; PER-16/PJ/2016; PP 55/2022; PP 58/2023; PMK 66/2023; PMK 168/2023; PMK 10/2025; PMK 72/2025; PMK 105/2025; PP 44/2015, 45/2015, 46/2015 beserta perubahannya; PP 7/2025, 36/2025; Perpres 82/2018, 75/2019, 64/2020, 59/2024; Permenaker 6/2016.

**Catatan:** referensi "HRMQ" pada proposal tidak berhasil diidentifikasi oleh penelusuran web. Rujukan ini dihapus kecuali URL-nya ditemukan di WP0.

---

## Lampiran A — Inventaris Aturan Lapisan Regulasi

Inventaris awal ini akan dirinci di WP1. Pasal yang tertulis adalah rujukan awal dan **wajib diverifikasi** terhadap PDF di `dataset/01_regulasi/` saat kodifikasi.

**Aturan lintas rezim (berlaku 2023–2026)**

| ID | Aturan | Sifat | Sumber |
|---|---|---|---|
| REG-PTKP-01 | PTKP = 54 jt (diri) + 4,5 jt (kawin) + 4,5 jt × tanggungan (maks 3) | wajib | PMK 101/2016 |
| REG-PTKP-02 | Status PTKP ditentukan pada awal tahun pajak | wajib | UU PPh Ps. 7(2) |
| REG-PTKP-03 | Pegawai wanita: PTKP diri sendiri saja, kecuali suami tidak berpenghasilan | wajib | PMK 168/2023; PER-16 |
| REG-P17-01 | Tarif progresif Pasal 17 (5/15/25/30/35%) | wajib | UU HPP |
| REG-PKP-01 | PKP dibulatkan ke bawah ribuan rupiah | wajib | UU PPh / PMK 168 |
| REG-BJ-01 | Biaya jabatan 5%, maks Rp500.000/bln, Rp6.000.000/thn | wajib | PMK 168; PER-16 |
| REG-BJ-02a/b | Plafon untuk masa kerja < 12 bulan: (a) 5% × bruto dengan plafon n × 500.000 [default; PMK 168, PMK 105] vs (b) plafon per bulan [contoh PMK 10/2025] | `tafsir` | PMK 168 Ps. 10(2); §9.1 |
| REG-PENG-01 | Iuran pensiun/JHT/JP yang dibayar pegawai = pengurang | wajib | UU PPh Ps. 6; PMK 168 |
| REG-PENG-02 | Zakat melalui pemberi kerja = pengurang | wajib | UU PPh Ps. 9(1)(g) |
| REG-OBJ-01 | Premi JKK, JKM, BPJS Kes yang dibayar pemberi kerja = objek (bruto) | wajib | PMK 168; PER-16 |
| REG-OBJ-02 | Iuran JHT, JP yang dibayar pemberi kerja = bukan objek saat dibayar | wajib | PMK 168; PER-16 |
| REG-OBJ-03 | Tunjangan pajak / pajak ditanggung = objek (gross-up) | wajib | PMK 66/2023; PMK 168 |
| REG-NAT-01..n | Natura & kenikmatan: objek, pengecualian, dan nilai | wajib | PMK 66/2023 |
| REG-BPJS-01..6 | Tarif, porsi, dan batas upah per program BPJS, berversi tahunan | wajib | PP 44/45/46 2015; Perpres 64/2020; pengumuman BPJS |
| REG-MET-01 | Metode gross sebagai *default*, dapat ditimpa gross-up | default | PMK 168 |
| REG-WAKTU-01 | Saat terutang = pembayaran atau terutangnya penghasilan, mana yang lebih dahulu. Masa pajak & tahun pajak ditentukan oleh saat terutang | wajib | PMK 168 Ps. 19(1) (2024+); PER-16 Ps. 21(1),(3) (2023) |
| REG-WAKTU-02 | Parameter BPJS (tarif, batas upah) dipilih berdasarkan periode iuran | wajib | PP 45/2015 Ps. 29; surat BPJS TK |
| REG-BULAT-* | Titik pembulatan sesuai registri §6.9.2 (BULAT-PKP-01 wajib; lainnya `tafsir`) | wajib / tafsir | §6.9.2 |

**Rezim 2023 (PER-16/PJ/2016), `berlaku: 2023-01-01 – 2023-12-31`**

| ID | Aturan |
|---|---|
| R23-01 | Bruto teratur sebulan = Σ komponen teratur + premi objek |
| R23-02 | Neto sebulan = bruto teratur − biaya jabatan − iuran pegawai |
| R23-03 | Neto disetahunkan = neto sebulan × jumlah bulan (aturan disetahunkan untuk masuk/keluar tengah tahun) |
| R23-04 | PPh setahun = Pasal 17 (PKP); PPh sebulan = PPh setahun / n |
| R23-05 | PPh atas penghasilan tidak teratur = PPh(teratur disetahunkan + tidak teratur) − PPh(teratur disetahunkan) |
| R23-06 | Masa pajak terakhir (Desember atau bulan keluar): PPh setahun aktual − PPh yang telah dipotong |
| R23-07 | Tanpa NPWP: tarif 20% lebih tinggi (di luar lingkup, dimuat untuk validasi B0) |

**Rezim TER (PMK 168/2023), `berlaku: 2024-01-01 – …`**

| ID | Aturan |
|---|---|
| R24-01 | Kategori TER dari status PTKP: A = {TK/0, TK/1, K/0}; B = {TK/2, TK/3, K/1, K/2}; C = {K/3} |
| R24-02 | Masa selain masa pajak terakhir: PPh = tarif_TER(kategori, bruto_masa) × bruto_masa |
| R24-03 | Bruto masa = seluruh penghasilan masa itu (teratur + tidak teratur + premi objek + natura objek + tunjangan pajak) |
| R24-04 | Masa pajak terakhir = Desember, atau bulan berhenti bekerja |
| R24-05 | PPh masa terakhir = PPh Pasal 17 setahun − Σ PPh masa sebelumnya; lebih bayar dikembalikan ke pegawai |
| R24-06 | Biaya jabatan & pengurang hanya dihitung di masa pajak terakhir (setahun) |
| R24-07 | Penghasilan neto disetahunkan hanya untuk kondisi khusus (verifikasi pasal di WP1) |
| R24-08 | Gross-up: tunjangan pajak = PPh terutang atas bruto termasuk tunjangan itu sendiri (titik tetap; `titik_tetap: true`) |
| R24-09 | PPh 21 DTP: pegawai memenuhi syarat (sektor/KLU, batas bruto, masa) → PPh terutang ditanggung pemerintah dan dibayarkan tunai ke pegawai |

## Lampiran B — Skenario Perubahan

Untuk setiap skenario, langkahnya:
1. oracle mendefinisikan **S\*** (output yang harus berubah);
2. perubahan diterapkan pada KB, B1, dan (jika relevan) B0;
3. ukur metrik §11.2.

Asal skenario: **R** = regulasi nyata, **P** = kebijakan perusahaan, **H** = hipotetis (uji ketahanan; dinyatakan eksplisit sebagai rekaan).

| ID | Asal | Perubahan | Berlaku | Jenis perubahan KB yang diharapkan | Mengapa menarik |
|---|---|---|---|---|---|
| C01 | R | Peralihan rezim PER-16 → PMK 168/2023 (TER) | 2024-01-01 | Tutup `berlaku` aturan R23-*; tambah R24-* + 3 tabel TER | Perubahan struktural; B0 harus ditulis ulang |
| C02 | R | Batas upah JP 9.077.600 → 9.559.600 | **2023-03-01** (tengah tahun) | 1 baris tabel `bpjs` | Granularitas versi per bulan; xlsx salah di Jan–Feb 2023 |
| C03 | R | Batas upah JP → 10.042.300 / 10.547.400 / 11.086.300 | Maret 2024/2025/2026 | 1 baris per tahun | Perubahan rutin tahunan; B0 harus menyunting 24 sel |
| C04 | R | PPh 21 DTP PMK 10/2025: 4 sektor, bruto ≤ Rp10 jt | masa Jan–Des 2025, **ditetapkan 04-02-2025** | Aturan R24-09 + tabel KLU | **Berlaku surut** → uji bitemporal (KB per 31-01-2025 vs per 05-02-2025) |
| C05 | R | PMK 72/2025: tambah sektor pariwisata | masa Okt–Des 2025 (berlaku 20-10-2025) | Tambah KLU + aturan pengembalian khusus pariwisata | Amandemen parsial atas aturan yang sedang berlaku |
| C06 | R | PMK 105/2025: DTP 2026 untuk 5 sektor | masa Jan–Des 2026 | Versi baru aturan DTP | *Lex posterior* atas aturan sejenis |
| C07 | R | Keringanan JKK 50% industri padat karya (PP 7/2025, PP 36/2025) | iuran Feb 2025 – Jan 2026 | Tabel tarif JKK bersyarat sektor + jumlah pekerja | Parameter pemerintah yang bergantung pada atribut perusahaan → bruto berubah |
| C08 | R | Zakat melalui pemberi kerja menjadi pengurang eksplisit | 2024-01-01 | Aturan pengurang | Penambahan pengurang |
| C09 | P | Perusahaan X beralih gross → gross-up | 2024-07-01 | 1 baris kebijakan (`metode_pajak`) | Memicu definisi melingkar; B1 butuh kode baru |
| C10 | P | Perusahaan X mengoreksi klasifikasi lembur menjadi teratur | 2023-01-01 (koreksi) | 1 baris pemetaan komponen | Menghapus konflik K-02; uji bitemporal "dihitung saat itu vs seharusnya" |
| C11 | P | Tambah komponen "tunjangan internet" (tetap) | 2025-01-01 | 1 entri komponen | Ekspresivitas; tanpa kode |
| C12 | P | THR prorata per hari → per bulan (Permenaker 6/2016) | 2025-01-01 | Ubah rumus komponen | Hanya pegawai < 12 bulan terdampak (uji impact precision) |
| C13 | P | Dasar upah BPJS: gaji pokok → gaji pokok + tunjangan tetap | 2025-01-01 | Ubah ekspresi `dasar_upah` | Efek berantai ke premi objek → bruto → PPh |
| C14 | H | PTKP TK/0 dinaikkan (rekaan, mis. Rp60 jt) | 2027-01-01 | 1 tabel | Isolasi temporal: output 2023–2026 harus identik |
| C15 | H | Batas lapisan TER kategori A digeser (rekaan) | 2027-01-01 | Tabel TER | Verifikasi statis harus menangkap celah/tumpang tindih yang sengaja dibuat |

## Lampiran C — Contoh I/O

**Input (ringkas):**

```json
{
  "tahun_pajak": 2024, "masa": 4,
  "perusahaan": "perusahaan_x",
  "karyawan": {"id": "KAR-A", "status_ptkp": "TK/0", "tanggal_masuk": "2022-02-02",
               "gaji_pokok": 9378800, "metode_pajak": "gross"},
  "transaksi_masa": {"tunjangan_tetap": 350000, "tunjangan_akomodasi": 500000,
                     "thr": 9378800, "lembur": 500000}
}
```

**Output (ringkas):**

```json
{
  "pph21_masa": 0,
  "rincian": {
    "bruto_masa": {"nilai": 0, "komponen": {"gaji_pokok": 9378800, "thr": 9378800, "...": "..."}},
    "kategori_ter": {"nilai": "A", "aturan": "R24-01", "sumber": "PP 58/2023 Ps. ..."},
    "tarif_ter":    {"nilai": 0.0, "lapisan": [0, 0], "aturan": "R24-02"}
  },
  "jejak": [
    {"fakta": "premi_jkk", "aturan": "REG-OBJ-01", "sumber": "PMK 168/2023 Ps. ...", "masukan": ["gaji_pokok", "kelas_risiko_jkk"]},
    {"fakta": "kategori_objek(lembur)", "aturan": "PX-K02", "keputusan": "ditolak", "alasan": "KONFLIK_WAJIB", "pemenang": "REG-..."}
  ],
  "rentang_tafsir": [
    {"fakta": "pph21_masa", "aturan_tafsir": "BULAT-TER-01", "default": {"mode": "bawah", "nilai": 0},
     "alternatif": [{"mode": "setengah_atas", "nilai": 0}], "selisih_maks": 0}
  ],
  "audit": {"versi_kb": "<commit>", "hash_tabel": {"ter_bulanan.csv": "<sha256>"},
            "versi_engine": "<versi>", "tanggal_kebaruan_kb": "2026-10-01",
            "asumsi_dipakai": ["BULAT-TER-01=bawah", "REG-BJ-02a"]},
  "waktu": {"masa_pajak": "2024-04", "dasar": "REG-WAKTU-01: saat_terutang = min(tanggal_bayar, tanggal_terutang)"},
  "peringatan": ["KONFLIK_WAJIB: Perusahaan X memetakan lembur sebagai tidak_teratur; di rezim TER keduanya sama-sama masuk bruto masa (tanpa dampak angka)"]
}
```

Angka 0 di atas adalah *placeholder* skema. Nilai sebenarnya dihasilkan engine di WP3.

## Lampiran D — Temuan Audit xlsx Perusahaan X

Objek audit: sheet *Calculator PPh21 v8*, karyawan dummy KAR-A (TK/0, masuk 2022-02-02), tahun pajak 2023. Total PPh dipotong Rp7.285.500 sama dengan PPh setahun, sehingga xlsx konsisten secara internal. Temuan di bawah menyangkut kesesuaiannya dengan regulasi. Kolom "Dampak KAR-A" menyatakan apakah temuan mengubah angka untuk karyawan dummy ini, atau bersifat laten (baru muncul pada profil lain).

| ID | Temuan | Dasar | Jenis | Dampak KAR-A |
|---|---|---|---|---|
| K-01 | 254 sel rumus menanam konstanta regulasi (tarif BPJS, batas upah JP Rp9.559.600 di 24 sel, batas Kes Rp12 jt di 24 sel, biaya jabatan 5%/Rp500 rb, pengali 120%) | — | Pemeliharaan | Tidak (metrik C02/C03) |
| K-02 | **Lembur diperlakukan sebagai penghasilan tidak teratur** (change log v5) | PER-16/PJ/2016 Pasal 1 angka 15: penghasilan teratur "… **termasuk uang lembur**" | **Konflik aturan wajib** | Ya: distribusi PPh per bulan dan biaya jabatan bulanan berubah; total setahun dikoreksi di Desember (diverifikasi di E8) |
| K-03 | Komisi diperlakukan sebagai penghasilan tidak teratur | PER-16 Ps. 1 angka 15 ("imbalan dengan nama apapun yang diberikan secara periodik") | Tafsir, perlu asumsi tertulis | Ya (sama seperti K-02) |
| K-04 | **BPJS Kesehatan Desember = 0.** Satu kolom "Last Effective Date" (2023-12-31) dipakai sekaligus sebagai akhir tahun dan tanggal keluar, sehingga Desember selalu diperlakukan sebagai bulan keluar | Perpres 82/2018 jo. 75/2019 | Kesalahan pemodelan (ambiguitas makna input) | **Ya, bila pegawai tidak keluar**: premi objek Rp375.152 hilang dari bruto Desember |
| K-05 | Tabel PTKP K/I/0–3 bernilai Rp108–121,5 jt (seharusnya Rp112,5–126 jt), padahal K/I memang tidak dipakai pemotong | PMK 101/2016; PMK 168/2023 Ps. 9 | Kesalahan nilai + konsep | Laten |
| K-06 | Batas upah JP Rp9.559.600 dipakai sepanjang 2023; untuk Jan–Feb 2023 seharusnya Rp9.077.600 | PP 45/2015 Ps. 29; surat BPJS TK 2023 | Versi waktu | Laten (gaji < batas) |
| K-07 | Dasar upah BPJS (JKK/JKM/Kes/JP) hanya gaji pokok; regulasi: upah pokok + tunjangan tetap | PP 44/2015, PP 45/2015, Perpres 82/2018 | Perlu verifikasi apakah tunjangan telepon/transport termasuk tunjangan tetap | Mungkin (premi objek terlalu kecil) |
| K-08 | Dasar THR hanya gaji pokok (tanpa tunjangan tetap) dan memakai gaji sebelum kenaikan | Permenaker 6/2016 Ps. 3 | Ketenagakerjaan, bukan pajak, tetapi mengubah bruto | Ya |
| K-09 | THR diprorata per hari (Permenaker: per bulan masa kerja/12) | Permenaker 6/2016 | Kebijakan, sah bila lebih menguntungkan pekerja | Laten (masa kerja > 12 bulan) |
| K-10 | Label kolom "Realisasi" baris Overtime/Commission menjumlahkan baris lain (Q6 = Σ baris 40) | — | Presentasi | Tidak |
| K-11 | **THR dipajaki pada masa bulan Lebaran (April), padahal input "Tanggal THR di transfer" = 2023-02-28.** Sel DP19 tidak dirujuk rumus mana pun | Rezim 2023: PER-16/PJ/2016 **Pasal 21 ayat (1) dan (3)**: terutang "pada saat dilakukan pembayaran atau pada saat terutangnya penghasilan", dan saat terutang per masa adalah akhir bulan pembayaran/terutang. Rezim 2024+: PMK 168 Ps. 19(1), yang menambahkan "mana yang lebih dahulu". Diverifikasi: DP19 dirujuk 0 rumus | **Sumbu waktu** | Ya. Dengan input tersebut, KB akan memajaki THR di masa Februari, sedangkan B0 di April. Karena xlsx hanya referensi, nilai tanggal itu cukup diperlakukan sebagai skenario uji di E8 |
| K-12 | Pembulatan memakai `ROUND` Excel (setengah-atas) per komponen di setiap baris, sehingga hasil bergantung pada urutan pembulatan | — | Pembulatan tidak terdokumentasi | Potensial Rp1 per komponen; diukur di E8 |

Implikasi: K-02, K-04, dan (bila tanggal transfernya benar) K-11 adalah **ketidaksesuaian nyata** yang akan direproduksi dan dijelaskan oleh KB di E8 melalui peringatan `KONFLIK_WAJIB` dan jejak. Ini sekaligus demonstrasi mengapa kalkulator eksisting tidak boleh dijadikan oracle.
