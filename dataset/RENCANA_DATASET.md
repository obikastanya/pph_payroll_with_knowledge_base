# Rencana dataset penelitian

Disusun 2026-10-27. Dokumen ini memetakan setiap dataset yang dibutuhkan [skeleton](../paper/draft/skeleton.tex) dan [blueprint](../mini_demo/BLUEPRINT.md) ke salah satu dari empat asal:

| Kode | Asal | Siapa | Verifikasi |
|---|---|---|---|
| **A** | Sudah ada di `dataset/` dan bisa dipakai | dikumpulkan di tahap prototipe | sudah diverifikasi (lihat README tiap folder) |
| **P** | Bisa diperoleh dari sumber publik | Claude mengunduh atau mencatat | dicek terhadap sumber resmi; dokumen non-pemerintah didaftar dulu sebelum diunduh |
| **S** | Disusun sintetis oleh Claude | Claude | **wajib** diperiksa pakar lewat [review/](../review/README.md) sebelum dipakai |
| **G** | Dibangkitkan program secara deterministik | skrip di `system/` | diuji dengan uji unit dan *mutation score* (E0) |

Semua dataset dikumpulkan sebelum sistem penuh dibangun, kecuali yang bergantung pada sistem (ditandai "Tahap" di kolom terakhir).

## 1. Ringkasan

| ID | Dataset | Asal | Status | Target | Dipakai di |
|---|---|---|---|---|---|
| D01 | PDF regulasi peristiwa nyata 2023–2026 | A | ada (33 PDF) | semua peristiwa relevan | korpus E2, E3 |
| D02 | Tabel peristiwa (tanggal terbit, berlaku, jenis, bagian data) | S dari D01 | belum | ±11 relevan + ±7 pengecoh | korpus, RQ2–RQ4 |
| D03 | Pengecoh, termasuk pengecoh sulit | A + P | sebagian | ≥7 | penilaian relevansi |
| D04 | Data pengembangan: perubahan sebelum 2023 | A + P | sebagian | 5–8 | kalibrasi prompt dan gerbang |
| D05 | Data pengembangan: regulasi fiktif | S | belum | 3–5 | kalibrasi |
| D06 | Kontrafaktual | G dari D01 + D17 | belum | ≥1 per dokumen uji | strata kontrafaktual RQ2 |
| D07 | Perubahan tak terlihat + contoh hitungan | S (agent terpisah, disegel) | belum (1 contoh demo) | ≥15, @5–10 contoh | RQ1 |
| D08 | Dokumen kebijakan perusahaan nyata | P | belum | 5–10 dokumen | E1, E2 lapisan perusahaan |
| D09 | Kebijakan dan konflik buatan | S | sebagian (katalog 20 variasi) | melengkapi jenis konflik yang tidak muncul di D08 | E1, E2, RQ4 |
| D10 | Katalog variasi kebijakan | A | ada (20) | - | ekspresivitas E1 |
| D11 | Studi kasus Perusahaan X | A | ada (teranonimkan) | - | kebijakan nyata pertama |
| D12 | GT1 contoh resmi + *holdout* | A | ada (46); *holdout* belum dibagi | 46 | E0 |
| D13 | GT2 kalkulator DJP | P | tercatat; belum dipakai | sel ruang uji rezim TER | E0 |
| D14 | GT3 kasus bertingkat dihitung manual | S | belum | ±50 | E0 |
| D15 | GT4 implementasi pihak ketiga | A | ada (7 repo, 22 kalkulator *online*) | - | E0 |
| D16 | GT5 contoh hitungan kebijakan | S | belum | 3–5 per dokumen kebijakan | E0 lapisan perusahaan |
| D17 | Δ\* dan K\* (kunci jawaban) | S | belum | satu per dokumen | E2–E4 (Tahap 7) |
| D18 | Tabel tarif dan parameter | A | ada, *double entry* | - | KB |
| D19 | Distribusi operasional (upah, PTKP) | A | ada (BPS, Kemnaker) | - | sampel operasional, *drift*, B2 |
| D20 | Profil pegawai sintetis | A + G | ada (2.600 profil) | diperluas | $S^E$ |
| D21 | Ruang uji $S^E$ | G | belum | ±3.000+ | E2–E4 (Tahap 8) |
| D22 | Label dampak RQ4 jenis (c) | S | belum | semua pasangan kebijakan–peristiwa | E4 |
| D23 | B1 riwayat *commit* kalkulator OSS | A | ada (15 *commit*) | diperluas bila perlu | motivasi, RQ3 |
| D24 | Kasus B2 (LLM menghitung langsung) | G dari D19 | belum | ±100 (menyesuaikan anggaran) | E5 |
| D25 | Info *training cutoff* model | P | belum | 2 model | analisis kontaminasi |
| D26 | Peristiwa prospektif | P | dipantau | yang terbit sesudah pra-registrasi | uji prospektif |

## 2. Rincian

### D01–D02 Peristiwa nyata

D01 sudah ada di [01_regulasi/](01_regulasi/README.md). D02 adalah tabel peristiwa yang disusun dari PDF itu. Tanggal penetapan dan tanggal diundangkan dicatat terpisah, karena ω memakai tanggal terbit (pengetahuan hukum). Pemeriksaan otomatis 2026-10-27 menemukan selisih dengan catatan lama, misalnya PMK 105/2025 ditetapkan 29 Desember 2025, sedangkan README mencatat 31 Desember. Setiap tanggal di D02 diberi halaman PDF sumbernya.

Calon peristiwa relevan:

| Peristiwa | Berlaku | Jenis perubahan |
|---|---|---|
| Batas upah JP BPJS TK, Maret 2023, 2024, 2025, 2026 | tahunan | parameter (4 peristiwa) |
| PMK 66/2023, natura | 1 Juli 2023 | klasifikasi penghasilan baru |
| PP 49/2023, rekomposisi JKK | Oktober 2023 | parameter; dampak ke PPh 21 masih harus dicek |
| PP 58/2023 + PMK 168/2023, TER | 1 Januari 2024 | pergantian metode |
| PMK 10/2025, DTP | Januari 2025, ditetapkan 4 Februari | fasilitas baru, berlaku surut |
| PP 7/2025 dan PP 36/2025, keringanan JKK padat karya | Februari 2025 – Januari 2026 | parameter bersyarat (2 peristiwa) |
| PMK 72/2025, DTP pariwisata | Oktober 2025 | perluasan cakupan |
| PMK 105/2025, DTP 2026 | Januari 2026 | fasilitas baru |

### D03 Pengecoh

Sudah ada: PMK 81/2024 (Coretax), PER-2/PJ/2024 dan PER-11/PJ/2025 (bukti potong, pelaporan), PP 20/2026 (UMKM). Pengecoh sulit, yaitu dokumen yang menyebut PPh 21 tetapi tidak mengubah perhitungan pegawai tetap: PMK 6/2026 (DTP untuk peserta magang), PMK 28/2024 (DTP final IKN, di luar lingkup), PP 6/2025 (iuran JKP, tidak berdampak pada PPh 21), Perpres 59/2024 (menyatakan ulang batas upah JKN tanpa perubahan). Tambahan publik dicari di JDIH BPK untuk 2023–2026.

### D04–D05 Data pengembangan

Pengembangan memakai perubahan **sebelum** 2023 agar tidak menyentuh data uji. Sudah ada PDF PMK 101/2016 (PTKP), UU HPP (lapisan Pasal 17, 2022), Perpres 75/2019 (batas upah JKN 2020), dan PP 45/2015 (JP). Yang perlu dicari: surat batas upah JP 2019–2022 dan perubahan PTKP sebelumnya (PMK 122/2015). Regulasi fiktif (D05) disusun Claude untuk jenis perubahan yang tidak punya contoh nyata sebelum 2023, misalnya pergantian metode.

### D07 Perubahan tak terlihat

Disusun *agent* terpisah yang hanya membaca taksonomi perubahan (Tahap 2), tanpa spesifikasi representasi. Hasilnya disegel dengan `system/tools/seal.py` sebelum representasi dibekukan, lalu diperiksa pakar setelah dibuka. **Bergantung pada taksonomi perubahan**, jadi dikerjakan setelah taksonomi ditulis.

### D08–D09 Kebijakan perusahaan

D08 adalah dokumen nyata yang terbuka untuk umum, yaitu perjanjian kerja bersama (PKB) atau peraturan perusahaan yang dipublikasikan, misalnya oleh BUMN atau serikat pekerja. Kandidat didaftar dulu (URL, ukuran, lisensi), baru diunduh. D09 melengkapi jenis konflik yang tidak muncul di D08, berdasarkan taksonomi konflik (Tahap 2).

### D12 GT1 dan *holdout*

Ke-46 contoh resmi sudah dipakai untuk menguji prototipe lama, sehingga *holdout* tidak sepenuhnya bersih. *Holdout* ditetapkan sekarang, berstrata per sumber dan rezim, lalu disegel dan tidak dipakai selama sistem baru dibangun. Riwayat pemakaian di prototipe dilaporkan sebagai keterbatasan.

### D13 GT2 kalkulator DJP

kalkulator.pajak.go.id hanya menghitung rezim yang berlaku sekarang, tanpa pilihan tahun pajak. Kalkulator ini dipakai manual untuk sel rezim TER. Hasil setiap masukan dicatat dengan tanggal akses.

### D14, D16, D22 Materi yang diperiksa pakar

Disusun Claude dengan langkah hitung tertulis, lalu masuk `review/gold_cases/`, `review/company_policies/`, dan `review/impact_labels/`. GT3 dihitung dari teks regulasi, **bukan** dari *engine*, supaya tetap independen dari sistem yang diuji.

### D25 *Training cutoff*

Tanggal *cutoff* Claude Opus 5.5 dan GPT-6 dicatat dari dokumentasi resmi penyedia, untuk membagi peristiwa sebelum dan sesudah *cutoff*.

## 3. Urutan pengumpulan

1. D02 tabel peristiwa, D03 pengecoh, D12 pembagian *holdout*. Tidak bergantung apa pun.
2. Pencarian publik: D03 tambahan, D04, D08, D25.
3. Taksonomi (Tahap 2), lalu D05, D07, D09.
4. D14, D16, dan D13, yang dipakai untuk memvalidasi K\*.
5. Bergantung pada sistem: D17 (Tahap 7), D06, D21, D24 (Tahap 8), D22 (Tahap 17).

## 4. Status

| ID | Status | Tanggal | Catatan |
|---|---|---|---|
| D02 | draf selesai, menunggu tinjauan | 2026-10-27 | `09_korpus_peristiwa/peristiwa.csv`: 12 peristiwa relevan, 9 pengecoh; tanggal dari PDF dan metadata JDIH BPK |
| D03 | selesai, menunggu tinjauan | 2026-10-27 | 21 pengecoh (12 PDF baru di `01_regulasi/pengecoh/`) |
| D04 | sebagian | 2026-10-27 | 13 peristiwa pengembangan (13 PDF di `01_regulasi/pengembangan/`); masa berlaku sebagian belum dicek ke pasal |
| D08 | diunduh | 2026-10-27 | 5 dokumen uji + 1 pengembangan (Koja) di `10_kebijakan_perusahaan/dokumen/` (lokal); manifes di-commit |
| D04 | selesai, menunggu tinjauan | 2026-10-27 | masa berlaku 11 peristiwa pengembangan dicek ke pasal; PMK 149/2021 ternyata perubahan cakupan dan PMK 3/2022 ternyata pengecoh |
| D06 | spesifikasi selesai | 2026-10-27 | `09_korpus_peristiwa/kontrafaktual_spesifikasi.csv`: 12 varian, teks asli diverifikasi ada di dokumen; teks dan Δ* dibangkitkan setelah Δ* ada |
| D25 | selesai | 2026-10-27 | `09_korpus_peristiwa/model_cutoff.csv`; tidak ada peristiwa uji sesudah cutoff |
| D12 | selesai | 2026-10-27 | 32 pengembangan, 14 *holdout*, disegel `HOLDOUT.sha256` |
