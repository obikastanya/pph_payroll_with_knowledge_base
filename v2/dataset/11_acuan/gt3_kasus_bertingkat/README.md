# GT3 — Kasus bertingkat dihitung manual

Disusun 2026-10-27. Folder ini berisi 50 kasus PPh 21 pegawai tetap (tahun pajak 2023–2026) yang hasilnya dihitung langkah demi langkah langsung dari teks regulasi dan tabel parameter terverifikasi. GT3 adalah salah satu sumber *ground truth* (acuan) penelitian, terpisah dari GT1 (contoh resmi di `dataset/07_kasus_uji_resmi/`).

**Status:** sudah ditinjau (2026-10-27, `review/gold_cases/gt3.review.md`). Titik tafsir diputuskan di [docs/spesifikasi/tafsir_perhitungan.md](../../../docs/spesifikasi/tafsir_perhitungan.md) (K1–K16). Tinjauan mengoreksi angka 10 kasus 2025–2026 karena aturan pembulatan (K1) dan menambah asumsi di GT3-029 dan GT3-048; angka lain dihitung ulang secara independen dan tidak berubah.

## 1. Tujuan

1. Menguji sistem pada kombinasi yang tidak ada di contoh resmi: batas lapisan TER dan Pasal 17 sampai satuan rupiah, premi BPJS dengan batas upah, natura, zakat, DTP dengan kriteria sektor dan Rp10 juta, keringanan JKK, pegawai masuk/keluar di tengah tahun, serta metode *gross*, *gross-up*, dan ditanggung pemberi kerja.
2. Memberi jejak hitung per langkah dengan rujukan pasal dan halaman PDF, sehingga setiap selisih antara keluaran sistem dan acuan bisa ditelusuri ke satu aturan.
3. Mencatat titik yang regulasinya diam atau ambigu beserta putusan tafsirnya (bagian 8), supaya tidak diam-diam menjadi "kebenaran".

## 2. Isi folder

| Berkas | Isi |
|---|---|
| `GT3-001.json` … `GT3-050.json` | satu kasus per berkas |
| `index.csv` | `id, stratum, tahun, status, metode, bulan, ringkas` |
| `tools/rules.py` | parameter (dibaca dari `dataset/01_regulasi/tables/*.csv`), daftar rujukan pasal/halaman, aritmetika pecahan eksak |
| `tools/cases.py` | spesifikasi masukan 50 kasus (dipilih tangan) |
| `tools/calculator.py` | penghitung GT3: membentuk komponen, `expected`, dan `langkah` |
| `tools/build.py` | menulis ulang semua `GT3-*.json` dan `index.csv` |
| `tools/check_gt3.py` | pemeriksa terpisah (tidak mengimpor `calculator.py`) |

Membangun ulang dan memeriksa (dari folder `tools/`):

```
..\..\..\..\env\Scripts\python.exe build.py
..\..\..\..\env\Scripts\python.exe check_gt3.py --tulis
```

## 3. Format kasus

```
id, stratum ("bulanan" | "tahunan"), tahun_pajak, rezim, uraian, asumsi[],
input {status_ptkp, jenis_kelamin, karyawati_kawin_suami_berpenghasilan, npwp_nik_valid, metode,
       sektor {klu, uraian, kelompok_risiko_jkk, padat_karya_pp7_2025},
       bulan_masuk, bulan_keluar, masa:[{bulan, komponen:{... rupiah bulat}}], info_dtp?},
expected {per_masa:[{bulan, bruto, kategori_ter, tarif_ter, pph21, pph21_dtp, pph21_dipotong,
                     tunjangan_pajak?, pph21_ditanggung_pemberi_kerja?, keterangan?, rincian_metode_lama?}],
          tahunan:{...} | null, berhak_dtp? (2025–2026)},
langkah[{no, text, formula, value, sumber}], cek_aritmetika, cek_aritmetika_rinci
```

Arti kolom yang perlu dijelaskan:

- **stratum** `bulanan` = satu Masa Pajak selain Desember dan bukan masa terakhir; `tahunan` = seluruh masa kerja dalam setahun sampai Masa Pajak Terakhir (Desember, atau bulan berhenti bekerja). Kasus pegawai masuk/keluar di tengah tahun termasuk stratum `tahunan` dengan kurang dari 12 masa.
- **bulan_masuk / bulan_keluar**: bulan pertama dan bulan terakhir bekerja (bulan_keluar = Masa Pajak Terakhir). `null` bila bekerja sepanjang tahun.
- **komponen** memuat semua angka yang dibayar atau dipotong, termasuk yang **bukan objek** (iuran JHT/JP pemberi kerja, iuran BPJS Kesehatan pegawai) dan nilai natura **sebelum** batas pengecualian. Sistem yang diuji harus sendiri memutuskan mana yang masuk bruto. Tunjangan pajak (*gross-up*) dan PPh yang ditanggung pemberi kerja **tidak** ada di input karena merupakan hasil hitung; nilainya ada di `expected.per_masa[].tunjangan_pajak` / `pph21_ditanggung_pemberi_kerja`.
- **bruto**: penghasilan bruto masa yang menjadi dasar (termasuk tunjangan pajak / PPh ditanggung untuk 2024+).
- **pph21**: PPh 21 terutang masa itu sebelum DTP (Masa Pajak Terakhir: PPh setahun dikurangi PPh masa sebelumnya; negatif = lebih potong).
- **pph21_dtp**: bagian yang ditanggung pemerintah. **pph21_dipotong** = `pph21 - pph21_dtp` = jumlah yang dipotong/disetor pemotong (untuk metode ditanggung, dibayar pemberi kerja, bukan dipotong dari gaji).
- **kategori_ter / tarif_ter**: `null` untuk 2023 dan untuk Masa Pajak Terakhir.
- **tahunan.kelebihan_dikembalikan_ke_pegawai**: lebih potong yang wajib dikembalikan; 0 bila lebih potong berasal dari DTP.
- **langkah.formula**: ekspresi angka (`+ - * /`, `floor`, `min`, `max`) yang dievaluasi ulang oleh `check_gt3.py`. Langkah non-numerik (kategori, tarif hasil baca tabel, kelayakan) memakai `formula: null`; nilai tarif dan kategori tetap diperiksa lewat hitung ulang independen.

## 4. Cara menghitung (ringkas)

**2024–2026 (TER).** Bruto masa = gaji + tunjangan + lembur + THR/bonus + premi JKK, JKM, dan BPJS Kesehatan yang dibayar pemberi kerja + natura objek (PMK 168/2023 Pasal 5 ayat (3), PDF hlm. 9; iuran JHT/JP pemberi kerja bukan objek, Pasal 7 huruf c, PDF hlm. 10). Kategori TER dari status PTKP awal tahun (PP 58/2023 Pasal 2 ayat (3)-(4), PDF hlm. 4); tarif dari Lampiran A/B/C (PDF hlm. 11–24; `batas_bawah` eksklusif, `batas_atas` inklusif). PPh masa = tarif × bruto (PMK 168 Pasal 15 ayat (1) huruf a, PDF hlm. 15), dibulatkan ke rupiah penuh: masa 2024 desimal dibuang (PER-2/PJ/2024 Lampiran I huruf B angka 7), mulai Masa Januari 2025 ke terdekat dengan 0,50 ke atas (PER-11/PJ/2025 Pasal 129) (tafsir K1). Masa Pajak Terakhir (PMK 168 Pasal 1 angka 18, PDF hlm. 4): bruto setahun − biaya jabatan min(5% × bruto, n × Rp500.000) (tafsir K6) − iuran JHT+JP pegawai − zakat lewat pemberi kerja (Pasal 10, PDF hlm. 11–12) − PTKP; PKP dibulatkan ke bawah ke ribuan (Pasal 8 ayat (4), PDF hlm. 10); tarif Pasal 17 UU HPP (PDF hlm. 56); dikurangi PPh masa sebelumnya (Pasal 15 ayat (1) huruf b, PDF hlm. 15). Pegawai masuk/keluar tengah tahun yang Subjek Pajak dalam negeri sejak awal tahun: tidak disetahunkan, PTKP penuh (Lampiran B Bagian Pertama I.2 angka 6 huruf a, PDF hlm. 29). Lebih potong dikembalikan (angka 7, PDF hlm. 30), kecuali yang berasal dari DTP (angka 8).

**2023 (PER-16/PJ/2016).** Penghasilan teratur sebulan − biaya jabatan min(5%, Rp500.000) − iuran JHT+JP pegawai, dikali 12 (atau sisa bulan sejak mulai bekerja), − PTKP, PKP dibulatkan ke bawah ribuan, tarif Pasal 17 UU HPP, dibagi 12 (atau faktor yang sama) dan dibulatkan ke bawah (Pasal 14 ayat (2)-(4) dan (8), PDF hlm. 13–14; Lampiran I.1.a.1, PDF hlm. 20–21; contoh I.6.2.2; tafsir K2). Penghasilan tidak teratur: selisih PPh setahun dengan dan tanpa penghasilan tidak teratur (Pasal 14 ayat (3) huruf b; Lampiran I.1.b, PDF hlm. 23). Masa terakhir: PPh setahun atas penghasilan sebenarnya − PPh yang telah dipotong (Pasal 14 ayat (5); Lampiran I.2, PDF hlm. 24). Zakat bukan pengurang (Pasal 10 ayat (3), PDF hlm. 10). Natura dipotong mulai Masa Juli 2023 (PMK 66/2023 Pasal 23 ayat (4) dan Pasal 24, PDF hlm. 18).

**Natura (Juli 2023+).** Objek PPh (PMK 66/2023 Pasal 3 ayat (1), PDF hlm. 5) kecuali yang dikecualikan; yang dipakai di kasus: rumah individual maks. Rp2.000.000/bulan (Lampiran A angka 7, PDF hlm. 22), kupon makan dinas luar maks. Rp2.000.000/bulan (Pasal 5 ayat (4)-(5), PDF hlm. 6–7), bingkisan selain hari raya maks. Rp3.000.000/tahun (Lampiran A angka 2, PDF hlm. 21), kendaraan dinas dikecualikan untuk pegawai tanpa penyertaan modal dengan rata-rata bruto ≤ Rp100 juta/bulan (Lampiran A angka 8, PDF hlm. 22). Hanya selisih lebih yang masuk bruto (Pasal 7 ayat (4), PDF hlm. 8).

**BPJS.** JKK 0,24/0,54/0,89/1,27/1,74% (PP 44/2015 Pasal 16 ayat (1), PDF hlm. 12), JKM 0,30% (Pasal 18, PDF hlm. 13), dasar upah = upah pokok + tunjangan tetap (Pasal 19 ayat (2), PDF hlm. 13); JHT 3,7%/2% (PP 46/2015 Pasal 16, PDF hlm. 11); JP 2%/1% dengan batas upah Rp9.077.600 (Jan–Feb 2023), Rp9.559.600 (Mar 2023), Rp10.042.300 (Mar 2024), Rp10.547.400 (Mar 2025), Rp11.086.300 (Mar 2026) (PP 45/2015 Pasal 28–29, PDF hlm. 20–21; `tables/bpjs.csv`); BPJS Kesehatan 4%/1% dengan batas Rp12.000.000 (Perpres 82/2018 Pasal 31; Perpres 75/2019 Pasal 32 ayat (1), PDF hlm. 3). Keringanan JKK 50% industri padat karya tertentu untuk iuran Februari–Juli 2025 (PP 7/2025 Pasal 4 dan 10, PDF hlm. 4 dan 6), diperpanjang s.d. iuran Januari 2026 (PP 36/2025 Pasal 10A, PDF hlm. 4).

**DTP.** 2025: PMK 10/2025 (sektor alas kaki, tekstil & pakaian jadi, furnitur, kulit; KLU Lampiran A; Pasal 3–5, PDF hlm. 4–6) jo. PMK 72/2025 (pariwisata hanya Masa Oktober–Desember 2025, Pasal 4A, PDF hlm. 4). 2026: PMK 105/2025 (lima sektor termasuk pariwisata, sepanjang 2026). Kriteria pegawai: bruto tetap dan teratur Masa Januari (atau bulan pertama bekerja) ≤ Rp10.000.000; status ini berlaku setahun walaupun gaji naik. Seluruh PPh 21 masa itu DTP, dibayar tunai dan bukan penghasilan (PMK 168 Pasal 7 huruf h, PDF hlm. 10); kelebihan DTP tidak dikembalikan (PMK 10/2025 dan PMK 105/2025 Pasal 5 ayat (5), PDF hlm. 6). KLU dicek di `tables/klu_dtp.csv` dan dicocokkan lagi dengan teks PDF Lampiran A.

**Metode.** *Gross-up*: tunjangan pajak tunai = PPh 21 masa yang sama (titik tetap terkecil, tafsir K3). Ditanggung pemberi kerja: 2023 (PER-16 Pasal 8 ayat (2), PDF hlm. 9) PPh yang ditanggung adalah kenikmatan bukan objek, jadi tanpa *gross-up*; 2024+ (PMK 168 Lampiran B Bagian Kedua I.4, PDF hlm. 44) PPh yang ditanggung adalah kenikmatan dan objek, dihitung *full gross-up* (angka sama dengan *gross-up*, tetapi tidak dipotong dari gaji).

## 5. Aturan independensi yang dipatuhi

- Tidak membuka atau mengimpor apa pun dari `engine/`, `kb/`, `mini_demo/`, `system/`, `baselines/`, `ui/`, `web/`, `jembatan/`, `eksperimen/`, `tests/`, `dataset/06_kasus_uji_sintetis/`, `dataset/02_studi_kasus/`. Kode di `tools/` hanya membaca `dataset/01_regulasi/tables/*.csv`.
- Di `dataset/07_kasus_uji_resmi/` hanya dibaca berkas yang barisnya di `pembagian_holdout.csv` bertanda `pengembangan` (untuk mempelajari cara hitung dan format): PER16_I.1.1, I.1.3, I.4.1, I.4.2, I.6.1.1, I.6.2.1, I.8, I.9; PMK168_B_I.2.1.1, I.2.2.2a, I.2.2.3, I.5; PMK10_B_1, B_2, B_3; PMK72_B_6, B_7; PMK105_B_1, B_3 (sebagian hanya ringkasan `uraian`-nya). Berkas `holdout`, `README.md`, `index.csv`, dan berkas yang tidak tercantum di `pembagian_holdout.csv` tidak dibuka.
- Sumber yang dibaca: PDF di `dataset/01_regulasi/` (PMK 168/2023, PP 58/2023, PMK 10/2025, PMK 72/2025, PMK 105/2025, PMK 66/2023, PP 7/2025, PP 36/2025, PP 44/2015, PP 45/2015, PP 46/2015, Perpres 75/2019, UU HPP), `ocr/PER_16_PJ_2016_ocr.txt`, `tables/*.csv`, `dataset/01_regulasi/README.md`, `docs/spesifikasi/taksonomi.md` bagian 0.
- **Pengungkapan.** Saat membaca teks PMK 168/2023 (sumber yang diizinkan) terlihat sebagian halaman contoh yang transkripsinya berstatus *holdout* (Lampiran B I.1, PDF hlm. 33–34, dan I.4, PDF hlm. 44). Dari I.4 hanya dipakai kaidah perlakuannya ("PPh 21 yang ditanggung … merupakan kenikmatan … objek … *full gross up*"). Tidak ada angka contoh *holdout* yang dipakai; semua masukan GT3 dipilih sendiri dan tidak meniru skenario contoh resmi.
- **Tinjauan.** Peninjau memakai sumber yang sama dan menghitung ulang ke-50 kasus dengan skrip sendiri (tidak mengimpor `tools/`). Saat memastikan kaidah I.4 di PMK 168/2023 PDF hlm. 44, peninjau melihat satu kalimat contoh yang memuat satu angka hasil; angka itu tidak dipakai.
- Pemeriksa `tools/check_gt3.py` ditulis terpisah dari `tools/calculator.py` (membaca tabel dan menghitung ulang dengan kode sendiri), sehingga kesalahan logika di satu tempat tidak otomatis tersalin ke tempat lain. Keduanya tetap ditulis oleh penyusun yang sama; karena itu tinjauan ahli tetap diperlukan.

## 6. Cakupan

**Stratum × tahun**

| Tahun / rezim | bulanan | tahunan | Jumlah |
|---|---|---|---|
| 2023 — PER-16/PJ/2016 + natura PMK 66/2023 | 7 | 5 | 12 |
| 2024 — TER (PP 58/2023 + PMK 168/2023) | 8 | 5 | 13 |
| 2025 — TER + DTP PMK 10/2025 jo. PMK 72/2025 + keringanan JKK | 8 | 5 | 13 |
| 2026 — TER + DTP PMK 105/2025 | 7 | 5 | 12 |
| **Jumlah** | **30** | **20** | **50** |

**Metode:** *gross* 39; *gross-up* 6 (005, 012, 017, 022, 038, 044); ditanggung pemberi kerja 5 (004, 018, 025, 045, 049).

**Status PTKP:** TK/0 13, TK/1 4, TK/2 2, TK/3 1, K/0 7, K/1 8, K/2 6 (+1 karyawati kawin K/2 yang dipotong dengan PTKP diri, GT3-007), K/3 8. Kategori TER (kasus 2024–2026): A 19, B 13, C 6.

**Batas lapisan**

| Uji | Kasus |
|---|---|
| TER A di Rp5.400.000: b / b+1 / b−1 | 013 / 014 / 015 |
| TER B di Rp11.250.000: b / b+1 / b−1 | 026 / 027 / 028 |
| TER C di Rp6.600.000: b / b+1 / b−1 | 039 / 040 / 041 |
| Pasal 17, PKP tepat Rp60.000.000 (neto disusun mundur lewat bonus Desember) | 008 (2023) |
| Pasal 17, PKP tepat Rp250.000.000 | 021 |
| Pasal 17, neto − PTKP = Rp60.000.999 → PKP Rp60.000.000 (pembulatan di batas) | 035 |
| Pasal 17, PKP Rp500.001.000 (batas + 1.000) | 046 |
| Pasal 17, PKP Rp59.999.000 (batas − 1.000) | 050 |
| Lapisan TER bergeser karena keringanan JKK (Jan 3,5% → Feb 3%) | 036 |

**Komponen**

| Komponen / situasi | Kasus |
|---|---|
| Lembur | 002, 007, 011, 013–015, 019, 024, 026–029, 033, 037, 039–041 |
| THR | 003, 008, 009, 010, 016, 021, 022, 023, 025, 031, 034, 035, 036, 038, 043, 046, 047, 048, 049, 050 |
| Bonus | 008, 011, 021, 025, 035, 037, 046, 049, 050 |
| Premi JKK + JKM pemberi kerja (bruto) | semua kasus; risiko sangat rendah s.d. sangat tinggi (002: 1,74%; 036: 1,27%) |
| Iuran JP dengan batas upah mengikat | 002–007, 009–012, 017, 018, 020–028, 032, 036, 038, 044–046, 049; perubahan batas Maret dalam satu tahun: 009, 010, 012, 021, 022, 023, 025, 036, 038, 046, 049 |
| BPJS Kesehatan dengan batas Rp12 juta mengikat | 002, 004, 006, 009, 011, 012, 018, 020–022, 024, 025, 032, 044–046, 049 |
| Zakat lewat pemberi kerja | 2024+: 020 (tidak memengaruhi TER), 021, 038, 050; 2023 (bukan pengurang): 008 |
| Natura | 006 (rumah + kendaraan, Agt 2023), 009 (rumah Jan–Des 2023: Jan–Jun tidak dipotong; bingkisan > Rp3 juta), 019 (rumah + kupon makan), 050 (rumah + kendaraan 2026) |
| Masuk tengah tahun | 007 (2023, faktor 6), 011 (2023, faktor 8), 024 (2024), 037 (2025, kriteria DTP bulan pertama) |
| Keluar tengah tahun | 010 (2023), 023 (2024), 048 (2026, DTP) |
| Keringanan JKK PP 7/2025 jo. PP 36/2025 | 031, 032, 034, 036, 037, 042 (Jan 2026), 047 dan 048 (hanya Jan 2026) |
| DTP diberikan | 029, 031, 033 (pariwisata Okt 2025), 034, 037, 042, 043, 047, 048 |
| DTP ditolak | 030 (tetap-teratur Rp10.020.000), 036 (Rp10.500.000), 032 (sektor makanan: keringanan JKK ya, DTP tidak), semua kasus KLU non-DTP 2025–2026 |
| DTP: lebih potong tidak dikembalikan | 034, 037, 048 |
| Karyawati kawin | 007 |

## 7. Pemeriksaan aritmetika

`tools/check_gt3.py` (pecahan eksak) menjalankan dua pemeriksaan:

1. **2.646 langkah numerik** dari 50 kasus dievaluasi ulang dari string `formula` dan dibandingkan dengan `value`: **0 tidak cocok**.
2. **2.813 item hitung ulang independen** (premi/iuran dari tarif, bruto, kategori dan tarif TER, PPh masa, sifat titik tetap *gross-up*, kelayakan DTP, seluruh angka tahunan): **0 tidak cocok**.

Setelah tinjauan, peninjau menghitung ulang seluruh `expected` (komponen premi/iuran dari tarif, bruto, TER, *gross-up*, DTP, dan perhitungan Masa Pajak Terakhir) dengan skrip terpisah dari `input`: 0 selisih terhadap berkas yang sekarang. Dengan aturan pembulatan lama (semua ke bawah) skrip yang sama juga mereproduksi angka penyusun sebelum koreksi tanpa selisih, sehingga koreksi hanya berasal dari putusan K1.

Pemeriksa sudah diuji dengan menyuntikkan 6 kesalahan buatan (PPh, PKP, bruto, tunjangan pajak, DTP, satu `value` langkah); keenamnya tertangkap. Hasil per kasus tertulis di `cek_aritmetika` dan `cek_aritmetika_rinci`.

## 8. Tafsir yang dipakai

Semua titik yang sebelumnya dicatat sebagai ketidakpastian sudah diputuskan di [docs/spesifikasi/tafsir_perhitungan.md](../../../docs/spesifikasi/tafsir_perhitungan.md); rujukan "tafsir Kn" di `asumsi` dan `langkah.sumber` menunjuk ke bagian dokumen itu.

| Kode | Putusan singkat | Kasus terkait |
|---|---|---|
| K1 | PPh TER masa 2024: desimal dibuang; Masa Januari 2025 dst.: ke rupiah terdekat, 0,50 ke atas (PER-2/PJ/2024 Lampiran I huruf B angka 7; PER-11/PJ/2025 Pasal 129) | dikoreksi: 028, 030, 034, 036, 037, 038, 044, 047, 048, 049 |
| K2 | PPh sebulan metode lama dibulatkan ke bawah (contoh PER-16 I.6.2.2) | 001, 005–008, 010 |
| K3 | *Gross-up*/PPh ditanggung = titik tetap terkecil dengan pembulatan masa itu; Desember = kekurangan PPh Desember | 005, 012, 017, 018, 022, 025, 038, 044, 045, 049 |
| K4 | PPh ditanggung: Jan–Jun 2023 tanpa *gross-up*; Jul 2023 dst. kenikmatan objek, *full gross-up* | 004, 018, 025, 045, 049 |
| K5 | Kriteria DTP Rp10 juta: gaji + tunjangan tetap (+ imbalan/natura tetap menurut kontrak); tanpa premi BPJS pemberi kerja, lembur insidental, THR, bonus | 029–034, 036, 037, 042, 043, 047, 048 |
| K6 | Biaya jabatan bagian tahun: min(5% × bruto, n × Rp500.000) | 010, 011, 023, 024, 037, 048 |
| K7 | Iuran JKK Agustus 2025 s.d. Januari 2026 memakai tarif keringanan | 034, 036, 037, 042, 047, 048 |
| K8 | Seluruh tarif nominal JKK masuk bruto walaupun sebagian direkomposisi ke JKP | semua |
| K9 | Iuran JP pegawai 2023 adalah pengurang | semua kasus 2023 |
| K10 | Zakat 2023 bukan pengurang pemotongan; 2024+ hanya di Masa Pajak Terakhir | 008, 020, 021, 038, 050 |
| K11 | Batas upah JP baru berlaku mulai iuran Maret; Jan–Feb 2023 = Rp9.077.600 | 009, 010, 012 |
| K12 | Natura 2023: rumah = teratur, bingkisan = tidak teratur; batas bingkisan kumulatif setahun | 006, 009 |
| K13 | Lebih potong yang berasal dari DTP tidak dikembalikan, juga di bulan berhenti bekerja | 034, 037, 048 |
| K14 | Bruto masa metode lama = teratur + tidak teratur | 003, 008, 009, 010 |
| K15 | Lembur 2023 = penghasilan teratur | 002, 007, 011 |
| K16 | Karyawati kawin K/x hanya dengan keterangan kecamatan bahwa suami tidak berpenghasilan | 007, 048 |

Hal lain yang dipilih penyusun dan dicatat di `asumsi`: bulan pembayaran THR (April 2023, April 2024, Maret 2025, Maret 2026, sesuai bulan Idulfitri), status PTKP tidak berubah dalam tahun, dan semua pegawai ber-NIK/NPWP valid.

**Catatan GT2.** Kalkulator PPh 21 DJP memotong desimal (GT2-09 dan GT2-10 tepat ,5 dibulatkan ke bawah; GT2-06 memilih titik tetap terkecil di bawah pemotongan desimal). Karena GT3 mengikuti PER-11/PJ/2025 untuk masa 2025+, GT3-044 (GT2-06), GT3-047 Januari (GT2-09), dan GT3-048 Januari (GT2-10) kini berbeda Rp1 dari kalkulator. Selisih ini adalah perbedaan pembulatan kalkulator, bukan kesalahan kategori, lapisan, atau metode *gross-up*.
