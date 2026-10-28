# Hasil E1 (RQ1, H1): perubahan tak terlihat

Pelaksana: *agent* pelaksana E1 yang tidak ikut merancang representasi, 2026-10-28. Representasi dan *engine* dibekukan pada *tag* `representasi-v1` dan `engine-v1`. Kode `system/pph21kbs/engine`, `kb`, dan `expr` sama dengan *tag* `engine-v1` (`git diff engine-v1 HEAD` kosong untuk ketiga folder itu).

## 1. Pemeriksaan keutuhan sebelum segel dibuka

| Pemeriksaan | Hasil |
|---|---|
| `env\Scripts\python system\tools\seal.py verify review\unseen_changes\sealed` | `intact: 38 files match review\unseen_changes\sealed\MANIFEST.sha256` (kode keluar 0) |
| SHA-256 `sealed/MANIFEST.sha256` | `7ab4bace89add488a6c9ed9d694431102e89adf4bf832bf4b97c9eddc4c1c96a`, **sama** dengan [SEGEL.md](../SEGEL.md) |

Setelah pengujian selesai, `seal.py verify` dijalankan lagi dan hasilnya tetap `intact`. Isi `sealed/` tidak diubah.

## 2. Hasil utama

- **RA = 16/16 = 1,00.** Ke-16 perubahan dapat dinyatakan sebagai Δ tanpa mengubah *engine*, dan seluruh 100 contoh hitungan tereproduksi. Ada 2.609 nilai yang tercantum di `keluaran_diharapkan`, dan semuanya sama persis dengan keluaran *engine*.
- Selang kepercayaan Clopper–Pearson 95%: **[0,794; 1,000]**.
- Batas bawah satu sisi 95% (`1 - upper_bound(0, 16)`): **0,829**.
- **H1 diterima**, karena 0,829 ≥ θ₁ = 0,70.
- Kegagalan menurut kategori: (a) 0, (b) 0, (c) 0, (d) 0 pada hasil akhir.
- Percobaan: 15 perubahan berhasil pada percobaan pertama. U15 berhasil pada percobaan kedua (lihat bagian 5).

## 3. Cara pengujian

**Basis.** Untuk setiap perubahan, basisnya `build_gold.prefix_at(chain, tanggal_diundangkan)`. Karena semua dokumen terbit sesudah 25 Februari 2026, basisnya selalu rantai emas lengkap sampai `GOLD-E12`. Δ diterapkan dengan `apply_delta` dalam mode ketat (validasi skema, tanpa `lenient`).

**Gerbang.** G1 berarti Δ dapat diterapkan dan SHACL (`pph21kbs.kb.shacl.validate`) lolos. Daftar dokumen untuk SHACL adalah registri korpus ditambah `UNSEEN-Uxx` dan `UNSEEN-KONVENSI`. G3 adalah `pph21kbs.static.check` pada ω, dengan lapisan kebijakan terpasang untuk U14 dan U15. G2 tidak berlaku. Setiap unsur mengutip teks perubahan itu sendiri sebagai sumber, dengan dokumen `UNSEEN-Uxx`.

**Tanggal pengetahuan.** ω = tanggal diundangkan (U15: tanggal penandatanganan PKB). Dengan begitu, perubahan yang berlaku surut (U01, U07, U15) dihitung sebagai nilai seharusnya.

**Konversi contoh ke kasus** (`_alat/convert.py`):
- Premi dan iuran BPJS di contoh adalah nilai yang ditagih. Karena itu `employer.premiums_as_billed = true`, dan nilai premi masuk sebagai komponen `income`. KB emas sudah membaca premi dengan cara ini (`REG.INPUT.BILLED.*`).
- Bila bulan terakhir yang tercantum bukan Desember dan bukan `masa_terakhir`, contoh itu tidak punya Masa Pajak Terakhir. Bulan-bulan berikutnya sampai Desember diisi dengan komponen bulan terakhir, sama seperti `refs.gt3_case`. Yang dibandingkan hanya bulan yang tercantum.
- Tanggal (mulai bekerja, lahir, berhenti) diberikan sebagai teks dan juga dipecah menjadi tahun, bulan, dan hari bilangan bulat, karena bahasa ekspresi tidak punya aritmetika tanggal.
- Komponen dan atribut baru diberi nama Inggris di `income`, `hr`, `employee`, dan `employer`. Model kasus memang terbuka untuk nama baru.
- `pph21_dipotong` dipetakan ke fakta `employee_tax_burden`. Nilai di luar daftar fakta keluaran dipetakan ke fakta antara buatan Δ: `kelebihan_dtp_tidak_dikembalikan` (U06), `lebih_potong_menjadi_hak_perusahaan` (U14), dan `komponen_setelah_pkb` (U15).

**Pemeriksaan konversi.** Sebelum Δ ditulis, contoh dihitung pada basis tanpa Δ dan dibandingkan dengan `keluaran_menurut_aturan_2026` (`_alat/baseline.py`). Hanya ada dua sumber selisih:
1. Pembulatan hasil TER: contoh membulatkan ke bawah (konvensi butir 2), sedangkan KB emas membulatkan ke rupiah terdekat sejak 2025 (tafsir K1).
2. Komponen yang belum dikenal KB (Tapera di U04, internet di U05). Δ perubahan itu memang harus menanganinya.

**Δ konvensi** (`delta/KONVENSI.json`, bukan perubahan regulasi). Δ ini diterapkan sebelum setiap Δ perubahan dan berisi dua parameter yang berlaku mulai 1 Januari 2026:
- `pph_round_mode = down`, sesuai konvensi butir 2 di `contoh.json`;
- `bpjs_round_mode = down`, sesuai langkah hitung contoh (`upah * 24 // 10000`; menurut konvensi butir 8, `//` berarti dibulatkan ke bawah).

Parameter kedua hanya berpengaruh bila sebuah Δ menghitung premi sendiri, dan itu hanya terjadi di U15. Parameter ini ditambahkan saat percobaan kedua U15 (bagian 5). Dengan Δ konvensi, contoh tanpa perubahan pada basis tanpa Δ hanya berselisih karena komponen baru U04/U05.

**Kontrol.** Setiap contoh juga dihitung tanpa Δ perubahan. Semua contoh bertanda `perubahan_berpengaruh = true` gagal tanpa Δ, kecuali dua:
- U04-C5 dan U05-C1: basis tanpa Δ kebetulan mengabaikan komponen yang tidak dikenalnya, dan hasilnya sama dengan pengecualian baru.

Sebaliknya, beberapa contoh bertanda "tidak berpengaruh" gagal tanpa Δ:
- U01-C7: PPh tidak berubah, tetapi nilai PTKP yang tercantum berubah.
- U04-C3, U05-C3, U05-C4, U05-C5: Δ juga membawa perlakuan komponen baru menurut aturan 2026.

Jadi lolosnya contoh memang berasal dari Δ, bukan dari basis.

## 4. Tabel per perubahan

| Id | Jenis | Sifat | Contoh cocok | Percobaan | Unsur Δ (add/change) | Cara dinyatakan |
|---|---|---|---|---|---|---|
| U01 | T1 | S1 | 7/7 | 1 | 1/1 | Tabel `ptkp` versi 2027 (berlaku surut 1 Januari 2027, dicatat 19 Maret 2027). *Change* menutup masa berlaku `TAB.PTKP.2016` sesuai pasal pencabutan. |
| U02 | T1 | S5 | 6/6 | 1 | 2/0 | Dua parameter: batas biaya jabatan bulanan dan tahunan mulai 2027. Aturan biaya jabatan yang ada sudah mengalikan batas bulanan dengan jumlah bulan kerja. |
| U03 | T2 | S5;S6 | 7/7 | 1 | 2/0 | Tabel `ter_category` dan `ter_monthly` versi 2027. Lapisan A/B/C disalin tanpa perubahan, lapisan D diambil dari Lampiran E. Karyawati kawin berstatus efektif TK/0 otomatis masuk D. |
| U04 | T3 | – | 6/6 | 1 | 12/2 | Fakta Tapera baru. Iuran Tapera pemberi kerja menjadi penghasilan lewat aturan `default` (perlakuan 2026 menurut contoh), lalu dikecualikan mulai 2027. Pengurang tahunan baru ditambahkan dengan batas per bulan iuran. *Change* `REG.PREMIUMS.TAXABLE` dan `REG.YEAR.DEDUCTIONS`. |
| U05 | T3 | S2;S5 | 6/6 | 1 | 5/1 | Fakta `internet_taxable` dengan syarat hari kerja jarak jauh per bulan dan batas Rp400.000. Tunjangan tetap tetap penuh. *Change* `REG.GROSS.REGULAR`. |
| U06 | T4 | S2;S3 | 7/7 | 1 | 15/0 | Fasilitas DTP baru: usia dihitung dari tanggal, penghasilan diuji pada bulan pertama, syarat jumlah pegawai diuji per bulan, dan pengembalian dibatasi sebesar PPh yang benar-benar dipotong. |
| U07 | T6 | S1;S2;S3;S5;S6 | 6/6 | 1 | 11/0 | Delapan aturan DTP PMK 105/2025 disalin dengan id baru untuk Januari–Juni 2027, ditambah tabel KLU 2027, batas Rp10 juta, dan aturan pengembalian 2027. |
| U08 | T5 | S2;S5 | 7/7 | 1 | 2/0 | Status PTKP efektif K/n → TK/n lewat tabel *lookup*, mengungguli aturan karyawati yang lama. Kategori TER ikut status efektif. |
| U09 | T7 | S4;S5 | 6/6 | 1 | 5/0 | Tarif TER dihitung atas bruto teratur, ditambah metode selisih Pasal 17 untuk penghasilan tidak teratur. Dua dokumen dinyatakan dalam satu Δ. |
| U10 | T8 | S5 | 5/5 | 1 | 0/1 | Satu *change*: masa berlaku `REG.ZAKAT.DEDUCTIBLE` ditutup pada 31 Desember 2026. |
| U11 | T9 | S5 | 6/6 | 1 | 4/0 | Fakta `ter_base` (bruto dibulatkan ke ribuan), ditambah dua aturan TER pengganti dengan pembulatan ke bawah. |
| U12 | T9 | S2;S5 | 6/6 | 1 | 8/0 | Bruto setara untuk bulan pertama. Jumlah hari dalam bulan diambil dari tabel, dengan ekspresi tahun kabisat. |
| U13 | T9 | S2;S5 | 6/6 | 1 | 1/0 | Aturan `ptkp_amount` proporsional untuk masa kerja kurang dari 12 bulan, kecuali kewajiban subjektif tengah tahun. |
| U14 | T10 | S2 | 6/6 | 1 | 4/0 | Lapisan perusahaan: golongan I–III memakai metode *gross-up* lewat aturan *gross-up* yang sudah ada di KB. Lebih potong Desember tidak dibayarkan kepada pegawai. |
| U15 | T10 | S1;S2 | 6/6 | 2 | 21/0 | Lapisan perusahaan: gaji pokok baru, rapel April, premi baru, serta rapel premi dan iuran dengan batas upah. |
| U16 | T2 | S5;S6 | 7/7 | 1 | 1/0 | Tabel `ter_monthly` versi 2027 dari Lampiran A, B, dan C. |

Semua Δ lolos penerapan ketat, SHACL, dan G3 tanpa galat. G3 memberi dua peringatan `dead`, untuk `dtp_excess_not_refunded` (U06) dan `excess_retained_by_company` (U14). Keduanya fakta antara yang hanya dibuat agar nilai yang tercantum di contoh dapat dibandingkan, dan memang tidak dibaca fakta keluaran.

## 5. Kegagalan dan percobaan yang gagal

Pada hasil akhir tidak ada kegagalan, sehingga tidak ada kategori (a), (b), (c), atau (d).

**U15, percobaan 1** (disimpan di `_alat/percobaan/`) gagal karena dua hal.
1. **G3 `dangling`.** Fakta `old_bpjs_wage` hanya berlaku untuk April 2027, padahal aturan JHT dan JP (April 2027–Desember 2028) membacanya. Ini kesalahan penulisan Δ, bukan batas representasi. Perbaikannya: masa berlaku fakta itu disamakan dengan aturan yang membacanya.
2. **Selisih Rp1 di U15-C5.** Premi JKK baru 0,24% × Rp10.667.000 = Rp25.600,8. KB membulatkannya menjadi Rp25.601 (K17: ke rupiah terdekat), sedangkan contoh menulis `10667000 * 24 // 10000` = Rp25.600. Akibatnya rapel premi menjadi 5.697 dan bukan 5.694, dan bruto April berselisih Rp4. Selisih ini berasal dari konvensi pembulatan premi pada contoh, bukan dari isi PKB, karena PKB tidak mengatur pembulatan. Bila dibiarkan, kategorinya (c). Perbaikannya: `bpjs_round_mode = down` ditambahkan ke Δ konvensi.

Percobaan 2 lolos semua gerbang dan 6/6 contoh.

## 6. Kepekaan hasil terhadap konvensi

| Varian | RA | CP 95% | Batas bawah satu sisi | H1 |
|---|---|---|---|---|
| Utama (Δ konvensi: pembulatan PPh dan premi ke bawah) | 16/16 | [0,794; 1,000] | 0,829 | diterima |
| Tanpa parameter premi di konvensi (U15-C5 gagal, kategori (c)) | 15/16 | [0,698; 0,998] | 0,736 | diterima |
| Tanpa Δ konvensi sama sekali | 8/16 | [0,247; 0,753] | 0,279 | ditolak |

Pada varian ketiga, 16 contoh di 8 perubahan gagal (U01, U03, U06, U07, U11, U12, U14, U15). Semua selisihnya berasal dari pembulatan: KB emas 2025+ membulatkan hasil TER ke terdekat (PER-11/PJ/2025) dan premi ke terdekat (K17), sedangkan contoh membulatkan ke bawah menurut konvensinya sendiri. Pada potongan bulanan selisihnya Rp1. Pada Masa Pajak Terakhir selisih itu terakumulasi, paling besar Rp11. Pada U14 (*gross-up*) dan U15 (premi baru) selisihnya ikut masuk ke bruto. Contoh yang sama juga berselisih pada `keluaran_menurut_aturan_2026` tanpa Δ apa pun. Jadi selisih ini perbedaan asumsi dasar antara penulis contoh dan KB emas, bukan kegagalan menyatakan perubahan. Di tingkat perubahan, semua kegagalan pada varian ini berkategori (c); tidak ada (a) atau (b). Hasil per contoh tanpa konvensi ada di `_alat/percobaan/detail_tanpa_konvensi/`.

## 7. Batas representasi yang terlihat walaupun contoh lolos

Hal-hal berikut tidak membuat perubahan gagal, tetapi menunjukkan apa yang harus diubah bila ingin dinyatakan lebih langsung. Semuanya berupa penambahan fungsi, sehingga merupakan perubahan *engine*.

1. **Tidak ada aritmetika tanggal** (U06, U12). Usia pada tanggal mulai bekerja dan jumlah hari kerja di bulan pertama dihitung dari bagian tanggal (tahun, bulan, hari) yang dipecah saat konversi kasus. Jumlah hari dalam bulan diambil dari tabel ditambah ekspresi tahun kabisat. Yang dibutuhkan: fungsi seperti `days_in_month`, `date_diff`, dan `age_on`.
2. **Tidak ada pembentukan teks** (U08). Status K/n → TK/n dinyatakan lewat tabel *lookup*. Yang dibutuhkan: penggabungan teks atau fungsi pengubah status.
3. **Lapisan perusahaan tidak dapat mengganti fakta wajib** (U14). Pasal "lebih potong menjadi hak perusahaan" dinyatakan lewat `employee_tax_burden` (sifat `default`) dan fakta baru `excess_retained_by_company`. Fakta wajib `refund_to_employee` tetap menyatakan ada pengembalian. Contoh tidak mencantumkan fakta itu. Seandainya dicantumkan, nilainya akan berbeda dari harapan, dan aturan perusahaan yang mencoba menggantinya akan tercatat sebagai konflik. Ini sejalan dengan rancangan *lex superior*, bukan cacat.
4. **Golongan per bulan** (U14 Pasal 1 ayat (3)). Metode pemotongan adalah fakta lingkup tahun, sehingga golongan dibaca sekali per tahun. Ini sama dengan batas (vi) di LOG_PENELITIAN.
5. **Satu Δ, satu dokumen** (U09). Dua dokumen (PP dan PMK) dinyatakan dalam satu Δ yang mengutip keduanya dan dicatat pada tanggal PMK.
6. **Perpanjangan masa berlaku** (U07). Perpanjangan dinyatakan dengan menyalin delapan aturan dengan id baru. Cara lain adalah *change* atas `valid_until` aturan lama. Keduanya dapat dipakai, tetapi tidak ada operasi ringkas "perpanjang masa berlaku".
7. **Komponen yang tidak dikenal hanya diperingatkan** (U04, U05). Basis tanpa Δ mengabaikan komponen baru dengan peringatan `UnreadInput`. Karena itu Δ perubahan juga harus menyatakan perlakuan 2026 atas komponen itu.
8. **Syarat tanpa atribut kasus** (U06 Pasal 1 angka 1, "sebelumnya tidak pernah menjadi pegawai tetap pada pemberi kerja yang sama"). Syarat ini dianggap terpenuhi karena kasus tidak memuat atributnya (representasi.md 10.6).

## 8. Kepatuhan aturan pelaksanaan

- Tidak ada berkas di `system/`, `dataset/`, `docs/`, atau `review/unseen_changes/sealed/` yang berubah. `git status --porcelain` dan `git diff --stat` untuk keempat path itu kosong.
- Status git di luar `hasil_E1/` dibandingkan dengan potret sebelum pengujian. Berkas yang berubah selama pengujian hanya ada di `experiments/` (misalnya `e2-ab1/calls.jsonl`, `e2-pengecoh/scores.csv`, `e3-tetap/chain.csv`, dan beberapa folder baru). Waktu ubahnya (23.43–23.56) jatuh saat pelaksana E1 hanya membaca. Perubahan itu berasal dari proses eksperimen lain yang berjalan bersamaan, bukan dari E1. Skrip E1 hanya menulis ke `hasil_E1/`.
- Tidak ada pemanggilan API LLM. `.env` tidak dibaca. `dataset/13_teks/PKB-*/teks.txt` dan `segmen.json` tidak dibuka.

## 9. Isi folder

| Berkas | Isi |
|---|---|
| `delta/U01.json` … `U16.json` | Δ per perubahan (versi terakhir) |
| `delta/KONVENSI.json` | Δ konvensi contoh, diterapkan sebelum setiap Δ perubahan |
| `hasil.csv` | Satu baris per perubahan |
| `detail/Uxx.json` | Hasil gerbang dan, per contoh, jumlah nilai yang dibandingkan, selisih, galat, peringatan, dan kontrol tanpa Δ |
| `_alat/` | `convert.py` (konversi kasus), `deltas.py` (penyusun Δ), `run_e1.py` (penerapan, gerbang, evaluasi), `baseline.py` (pemeriksaan konversi), `report.py` (`hasil.csv` dan statistik), `percobaan/` (percobaan 1 U15, Δ konvensi versi 1, hasil tanpa konvensi) |

Untuk menjalankan ulang dari `hasil_E1/_alat/`: `python deltas.py`, lalu `python run_e1.py`, lalu `python report.py`.
