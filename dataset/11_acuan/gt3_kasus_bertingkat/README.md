# GT3 — Kasus bertingkat dihitung manual

Disusun 2026-10-27. Folder ini berisi 50 kasus PPh 21 pegawai tetap (tahun pajak 2023–2026) yang hasilnya dihitung langkah demi langkah langsung dari teks regulasi dan tabel parameter terverifikasi. GT3 adalah salah satu sumber *ground truth* (acuan) penelitian, terpisah dari GT1 (contoh resmi di `dataset/07_kasus_uji_resmi/`).

**Status:** menunggu tinjauan ahli *payroll* (`review/gold_cases/gt3.review.md`). Sampai tinjauan selesai, angka di sini adalah hitungan penyusun, belum hitungan yang disetujui.

## 1. Tujuan

1. Menguji sistem pada kombinasi yang tidak ada di contoh resmi: batas lapisan TER dan Pasal 17 sampai satuan rupiah, premi BPJS dengan batas upah, natura, zakat, DTP dengan kriteria sektor dan Rp10 juta, keringanan JKK, pegawai masuk/keluar di tengah tahun, serta metode *gross*, *gross-up*, dan ditanggung pemberi kerja.
2. Memberi jejak hitung per langkah dengan rujukan pasal dan halaman PDF, sehingga setiap selisih antara keluaran sistem dan acuan bisa ditelusuri ke satu aturan.
3. Mencatat titik yang regulasinya diam atau ambigu (bagian 7), supaya tidak diam-diam menjadi "kebenaran".

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

**2024–2026 (TER).** Bruto masa = gaji + tunjangan + lembur + THR/bonus + premi JKK, JKM, dan BPJS Kesehatan yang dibayar pemberi kerja + natura objek (PMK 168/2023 Pasal 5 ayat (3), PDF hlm. 9; iuran JHT/JP pemberi kerja bukan objek, Pasal 7 huruf c, PDF hlm. 10). Kategori TER dari status PTKP awal tahun (PP 58/2023 Pasal 2 ayat (3)-(4), PDF hlm. 4); tarif dari Lampiran A/B/C (PDF hlm. 11–24; `batas_bawah` eksklusif, `batas_atas` inklusif). PPh masa = tarif × bruto (PMK 168 Pasal 15 ayat (1) huruf a, PDF hlm. 15), dibulatkan ke bawah ke rupiah (asumsi A1). Masa Pajak Terakhir (PMK 168 Pasal 1 angka 18, PDF hlm. 4): bruto setahun − biaya jabatan min(5%, n × Rp500.000) − iuran JHT+JP pegawai − zakat lewat pemberi kerja (Pasal 10, PDF hlm. 11–12) − PTKP; PKP dibulatkan ke bawah ke ribuan (Pasal 8 ayat (4), PDF hlm. 10); tarif Pasal 17 UU HPP (PDF hlm. 56); dikurangi PPh masa sebelumnya (Pasal 15 ayat (1) huruf b, PDF hlm. 15). Pegawai masuk/keluar tengah tahun yang Subjek Pajak dalam negeri sejak awal tahun: tidak disetahunkan, PTKP penuh (Lampiran B Bagian Pertama I.2 angka 6 huruf a, PDF hlm. 29). Lebih potong dikembalikan (angka 7, PDF hlm. 30), kecuali yang berasal dari DTP (angka 8).

**2023 (PER-16/PJ/2016).** Penghasilan teratur sebulan − biaya jabatan min(5%, Rp500.000) − iuran JHT+JP pegawai, dikali 12 (atau sisa bulan sejak mulai bekerja), − PTKP, PKP dibulatkan ke bawah ribuan, tarif Pasal 17 UU HPP, dibagi 12 (atau faktor yang sama) (Pasal 14 ayat (2)-(4) dan (8), PDF hlm. 13–14; Lampiran I.1.a.1, PDF hlm. 20–21). Penghasilan tidak teratur: selisih PPh setahun dengan dan tanpa penghasilan tidak teratur (Pasal 14 ayat (3) huruf b; Lampiran I.1.b, PDF hlm. 23). Masa terakhir: PPh setahun atas penghasilan sebenarnya − PPh yang telah dipotong (Pasal 14 ayat (5); Lampiran I.2, PDF hlm. 24). Zakat bukan pengurang (Pasal 10 ayat (3), PDF hlm. 10). Natura dipotong mulai Masa Juli 2023 (PMK 66/2023 Pasal 23 ayat (4) dan Pasal 24, PDF hlm. 18).

**Natura (Juli 2023+).** Objek PPh (PMK 66/2023 Pasal 3 ayat (1), PDF hlm. 5) kecuali yang dikecualikan; yang dipakai di kasus: rumah individual maks. Rp2.000.000/bulan (Lampiran A angka 7, PDF hlm. 22), kupon makan dinas luar maks. Rp2.000.000/bulan (Pasal 5 ayat (4)-(5), PDF hlm. 6–7), bingkisan selain hari raya maks. Rp3.000.000/tahun (Lampiran A angka 2, PDF hlm. 21), kendaraan dinas dikecualikan untuk pegawai tanpa penyertaan modal dengan rata-rata bruto ≤ Rp100 juta/bulan (Lampiran A angka 8, PDF hlm. 22). Hanya selisih lebih yang masuk bruto (Pasal 7 ayat (4), PDF hlm. 8).

**BPJS.** JKK 0,24/0,54/0,89/1,27/1,74% (PP 44/2015 Pasal 16 ayat (1), PDF hlm. 12), JKM 0,30% (Pasal 18, PDF hlm. 13), dasar upah = upah pokok + tunjangan tetap (Pasal 19 ayat (2), PDF hlm. 13); JHT 3,7%/2% (PP 46/2015 Pasal 16, PDF hlm. 11); JP 2%/1% dengan batas upah Rp9.077.600 (Jan–Feb 2023), Rp9.559.600 (Mar 2023), Rp10.042.300 (Mar 2024), Rp10.547.400 (Mar 2025), Rp11.086.300 (Mar 2026) (PP 45/2015 Pasal 28–29, PDF hlm. 20–21; `tables/bpjs.csv`); BPJS Kesehatan 4%/1% dengan batas Rp12.000.000 (Perpres 82/2018 Pasal 31; Perpres 75/2019 Pasal 32 ayat (1), PDF hlm. 3). Keringanan JKK 50% industri padat karya tertentu untuk iuran Februari–Juli 2025 (PP 7/2025 Pasal 4 dan 10, PDF hlm. 4 dan 6), diperpanjang s.d. iuran Januari 2026 (PP 36/2025 Pasal 10A, PDF hlm. 4).

**DTP.** 2025: PMK 10/2025 (sektor alas kaki, tekstil & pakaian jadi, furnitur, kulit; KLU Lampiran A; Pasal 3–5, PDF hlm. 4–6) jo. PMK 72/2025 (pariwisata hanya Masa Oktober–Desember 2025, Pasal 4A, PDF hlm. 4). 2026: PMK 105/2025 (lima sektor termasuk pariwisata, sepanjang 2026). Kriteria pegawai: bruto tetap dan teratur Masa Januari (atau bulan pertama bekerja) ≤ Rp10.000.000; status ini berlaku setahun walaupun gaji naik. Seluruh PPh 21 masa itu DTP, dibayar tunai dan bukan penghasilan (PMK 168 Pasal 7 huruf h, PDF hlm. 10); kelebihan DTP tidak dikembalikan (PMK 10/2025 dan PMK 105/2025 Pasal 5 ayat (5), PDF hlm. 6). KLU dicek di `tables/klu_dtp.csv` dan dicocokkan lagi dengan teks PDF Lampiran A.

**Metode.** *Gross-up*: tunjangan pajak tunai = PPh 21 masa yang sama (titik tetap). Ditanggung pemberi kerja: 2023 (PER-16 Pasal 8 ayat (2), PDF hlm. 9) PPh yang ditanggung adalah kenikmatan bukan objek, jadi tanpa *gross-up*; 2024+ (PMK 168 Lampiran B Bagian Kedua I.4, PDF hlm. 44) PPh yang ditanggung adalah kenikmatan dan objek, dihitung *full gross-up* (angka sama dengan *gross-up*, tetapi tidak dipotong dari gaji).

## 5. Aturan independensi yang dipatuhi

- Tidak membuka atau mengimpor apa pun dari `engine/`, `kb/`, `mini_demo/`, `system/`, `baselines/`, `ui/`, `web/`, `jembatan/`, `eksperimen/`, `tests/`, `dataset/06_kasus_uji_sintetis/`, `dataset/02_studi_kasus/`. Kode di `tools/` hanya membaca `dataset/01_regulasi/tables/*.csv`.
- Di `dataset/07_kasus_uji_resmi/` hanya dibaca berkas yang barisnya di `pembagian_holdout.csv` bertanda `pengembangan` (untuk mempelajari cara hitung dan format): PER16_I.1.1, I.1.3, I.4.1, I.4.2, I.6.1.1, I.6.2.1, I.8, I.9; PMK168_B_I.2.1.1, I.2.2.2a, I.2.2.3, I.5; PMK10_B_1, B_2, B_3; PMK72_B_6, B_7; PMK105_B_1, B_3 (sebagian hanya ringkasan `uraian`-nya). Berkas `holdout`, `README.md`, `index.csv`, dan berkas yang tidak tercantum di `pembagian_holdout.csv` tidak dibuka.
- Sumber yang dibaca: PDF di `dataset/01_regulasi/` (PMK 168/2023, PP 58/2023, PMK 10/2025, PMK 72/2025, PMK 105/2025, PMK 66/2023, PP 7/2025, PP 36/2025, PP 44/2015, PP 45/2015, PP 46/2015, Perpres 75/2019, UU HPP), `ocr/PER_16_PJ_2016_ocr.txt`, `tables/*.csv`, `dataset/01_regulasi/README.md`, `docs/spesifikasi/taksonomi.md` bagian 0.
- **Pengungkapan.** Saat membaca teks PMK 168/2023 (sumber yang diizinkan) terlihat sebagian halaman contoh yang transkripsinya berstatus *holdout* (Lampiran B I.1, PDF hlm. 33–34, dan I.4, PDF hlm. 44). Dari I.4 hanya dipakai kaidah perlakuannya ("PPh 21 yang ditanggung … merupakan kenikmatan … objek … *full gross up*"). Tidak ada angka contoh *holdout* yang dipakai; semua masukan GT3 dipilih sendiri dan tidak meniru skenario contoh resmi.
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

Pemeriksa sudah diuji dengan menyuntikkan 6 kesalahan buatan (PPh, PKP, bruto, tunjangan pajak, DTP, satu `value` langkah); keenamnya tertangkap. Hasil per kasus tertulis di `cek_aritmetika` dan `cek_aritmetika_rinci`.

## 8. Ketidakpastian

Pilihan GT3 di bawah dicatat juga di `asumsi` kasus terkait. K1, K3, K4, K5, K6, K7, K8, dan K10 diajukan sebagai pertanyaan kepada peninjau.

| Kode | Masalah | Pilihan GT3 | Kasus terdampak / alternatif |
|---|---|---|---|
| K1 | Pembulatan PPh TER bulanan tidak diatur (PP 58/2023; PMK 168/2023 Pasal 15 ayat (1) huruf a) | dibulatkan **ke bawah** ke rupiah penuh (A1) | 19 kasus punya hasil pecahan: 014, 017, 018, 022, 025, 027, 028, 030, 034, 036, 037, 038, 040, 042, 044, 045, 047, 048, 049. Pembulatan biasa bisa menaikkan Rp1 (mis. 028: 224.999,98 → 225.000). |
| K2 | Pembulatan PPh sebulan metode lama (PPh setahun / 12) | ke bawah ke rupiah (A2) | 001, 005, 006, 007, 008, 010. Contoh resmi PER-16 yang dibaca tidak menyatakan aturan pembulatannya (mis. I.1.3: 4.090.000 / 12 → 340.833, cocok dengan pembulatan ke bawah maupun pembulatan biasa). |
| K3 | *Gross-up*: cara iterasi tidak diatur; dengan pembulatan ke bawah persamaan T = floor(tarif × (X + T)) bisa punya dua solusi | ambil titik tetap **terkecil** (A3) | 24 masa di 017, 022, 025, 038, 044 juga punya solusi T+1 (mis. 017: 522.699 atau 522.700). |
| K4 | PPh ditanggung pemberi kerja tahun 2023: PER-16 Pasal 8 ayat (2) menyebutnya kenikmatan yang bukan objek, sedangkan UU HPP/PMK 66/2023 menjadikan kenikmatan objek (pemotongan mulai Juli 2023) | kasus 2023 ditaruh di semester I (004, Maret) dan dihitung tanpa *gross-up*; semester II 2023 sengaja tidak dibuat | 004. Untuk 2024+ dipakai PMK 168 Lampiran B I.4 (*full gross-up*). |
| K5 | Isi "penghasilan bruto tetap dan teratur" untuk kriteria DTP Rp10 juta (PMK 10/2025 Pasal 4 ayat (3); PMK 105/2025 Pasal 4 ayat (4)) | hanya gaji + tunjangan tetap; premi JKK/JKM/BPJS Kesehatan pemberi kerja, lembur, THR tidak dihitung | 029 menjadi layak (gaji + tunjangan tepat Rp10.000.000, bruto Rp12.019.000). Bila premi ikut dihitung, 029 tidak layak (DTP 0). Kasus DTP lain (031, 033, 034, 037, 042, 043, 047, 048) tetap layak di kedua pembacaan. |
| K6 | Plafon biaya jabatan untuk bagian tahun: agregat n × Rp500.000 (contoh PMK 168 dan PMK 105/2025) atau plafon per bulan (contoh 3 PMK 10/2025) | agregat min(5% × bruto, n × Rp500.000) | Berbeda hanya di 037 (alternatif: biaya jabatan 3.985.232,5; PPh setahun 892.000; masa terakhir −630.613) dan 048 (alternatif: 4.273.025; PPh setahun 1.209.650; masa terakhir −1.071.215). |
| K7 | Keringanan JKK Agustus 2025–Januari 2026 berasal dari PP 36/2025 yang ditetapkan 4 September 2025; perusahaan juga harus diverifikasi BPJS | premi JKK yang dibayar = tarif keringanan untuk iuran Februari 2025 s.d. Januari 2026 | 034, 036, 037 (Agt–Des 2025), 042, 047, 048 (Jan 2026). Bila Agustus 2025 dihitung tarif normal (penggajian sebelum PP 36 terbit), bruto Agustus naik sebesar setengah premi JKK. |
| K8 | Rekomposisi sebagian iuran JKK untuk JKP (PP 37/2021, PP 49/2023, PP 6/2025, PP 7/2025 Pasal 9): perlakuan PPh porsi itu tidak diatur | seluruh tarif nominal JKK dimasukkan ke bruto | semua kasus (selisih maks. 0,14% upah per bulan). |
| K9 | Iuran JP pegawai sebagai pengurang tahun 2023: PER-16 Pasal 10 ayat (3) huruf b tidak menyebut JP BPJS secara eksplisit | pengurang, berdasarkan Lampiran I.1.a.1 angka 1 huruf c (iuran pensiun … kepada BPJS Ketenagakerjaan, PDF hlm. 21) | semua kasus 2023. |
| K10 | Zakat lewat pemberi kerja tahun 2023 | bukan pengurang pemotongan (PER-16 Pasal 10 ayat (3)); baru pengurang mulai PMK 168/2023 | 008. |
| K11 | Batas upah JP Jan–Feb 2023 (Rp9.077.600) berasal dari surat BPJS TK yang menyebut "batas upah tahun 2022"; tanggal berlakunya disimpulkan | dipakai untuk iuran Januari–Februari 2023 | 009, 010, 012 (iuran JP Januari–Februari 2023; pada 001 dan 008 upah di bawah batas sehingga tidak terdampak). |
| K12 | Penggolongan natura dalam metode lama 2023: rumah bulanan dianggap penghasilan teratur, bingkisan dianggap tidak teratur; nilai natura = biaya pemberi kerja | sesuai pilihan di kiri | 006, 009. |
| K13 | DTP pegawai yang berhenti di tengah tahun: PMK 105/2025 Pasal 5 ayat (5) berbicara tentang "1 (satu) Tahun Pajak" | lebih potong yang berasal dari DTP pada masa terakhir (September) tidak dikembalikan, sama seperti Desember | 048. |

Hal lain yang dipilih penyusun dan dicatat di `asumsi`: bulan pembayaran THR (April 2023, April 2024, Maret 2025, Maret 2026), status PTKP tidak berubah dalam tahun, semua pegawai ber-NIK/NPWP valid, dan lembur sebagai penghasilan teratur.
