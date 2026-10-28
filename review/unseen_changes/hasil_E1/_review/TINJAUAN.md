# Tinjauan independen E1 (RQ1, H1)

Peninjau: *agent* independen yang tidak ikut menulis perubahan U01–U16, tidak ikut menulis Δ, dan tidak ikut merancang representasi. Tanggal: 2026-10-29. Semua keluaran tinjauan ada di folder ini. Tidak ada berkas lain yang diubah. Tidak ada pemanggilan API LLM, `.env` tidak dibaca, dan teks `dataset/13_teks/PKB-*` tidak dibuka.

## 1. Ringkasan

| Hal | Temuan |
|---|---|
| Jalankan ulang | Hasil pelaksana tereproduksi persis: 16/16 (utama), 15/16 (tanpa bagian premi), 8/16 (tanpa Δ konvensi). |
| *Engine* | `git diff engine-v1 -- system/pph21kbs/engine system/pph21kbs/expr` kosong. Segel `sealed/` tetap utuh. |
| Δ konvensi | Sah, dengan syarat diungkapkan terang. Konvensi itu tertulis di bahan tersegel sendiri, diterapkan sama untuk ke-16 perubahan, dan tidak menyentuh isi perubahan mana pun. |
| Pemeriksaan sampel | U04, U06, U09, U14: Δ menyatakan aturan tertulis, bukan angka contoh. Tidak ada nilai contoh yang ditanam di Δ. Ada satu catatan kecil di U14 (bagian 4.4). |
| Rekomendasi | **H1 diterima.** Hasil utama tetap RA = 16/16 (batas bawah 0,829). Varian 15/16 (batas bawah 0,736) dilaporkan sebagai varian konservatif. Varian 8/16 dilaporkan sebagai ukuran kecocokan asumsi dasar, bukan ukuran H1. |

## 2. Jalankan ulang

Skrip `rerun.py` di folder ini memanggil `run_e1.run()` milik pelaksana (`../_alat/`) tanpa mengubahnya. Keluaran per perubahan ditulis ke `utama/`, `tanpa_premi/`, dan `tanpa_konvensi/`, bukan ke `../detail/`. Varian "tanpa premi" memakai `../_alat/percobaan/KONVENSI_v1.json`, yaitu Δ konvensi yang hanya berisi `pph_round_mode = down`.

```
env\Scripts\python review\unseen_changes\hasil_E1\_review\rerun.py
```

| Varian | RA | Contoh cocok | CP 95% | Batas bawah satu sisi 95% | H1 (θ₁ = 0,70) |
|---|---|---|---|---|---|
| Utama (PPh dan premi dibulatkan ke bawah) | 16/16 | 100/100 | [0,794; 1,000] | 0,829 | diterima |
| Tanpa bagian premi | 15/16 (U15-C5 gagal) | 99/100 | [0,698; 0,998] | 0,736 | diterima |
| Tanpa Δ konvensi | 8/16 | 84/100 | [0,247; 0,753] | 0,279 | ditolak |

Pemeriksaan tambahan:
- Hasil varian utama sama dengan `../detail/` untuk setiap contoh: status cocok, jumlah nilai yang dibandingkan, kontrol tanpa Δ, peringatan G3, dan SHACL.
- Hasil varian tanpa konvensi sama dengan `../_alat/percobaan/detail_tanpa_konvensi/`.
- Pada varian tanpa premi, satu-satunya selisih adalah U15-C5: premi JKK Rp25.601 lawan Rp25.600, rapel premi 5.697 lawan 5.694, dan bruto April berselisih Rp4. Ini sama dengan laporan pelaksana.
- Penilai ketat. Nilai di `keluaran_diharapkan` yang tidak dapat dipetakan ke fakta dihitung sebagai selisih, bukan dilewati.
- `seal.py verify` menghasilkan `intact: 38 files match`.
- `git status` untuk `system/`, `dataset/`, `docs/`, dan `sealed/` bersih.

## 3. Apakah Δ konvensi sah?

### 3.1 Apa kata bahan tersegel

- `contoh.json` setiap perubahan memuat daftar `konvensi` yang sama. Butir 2 berbunyi: "Hasil TER x bruto dibulatkan ke bawah ke rupiah penuh (asumsi implementasi; PP 58/2023 dan PMK 168/2023 tidak mengatur), kecuali perubahan menyatakan lain." Jadi pembulatan PPh dinyatakan **tersurat** sebagai asumsi dasar contoh.
- Pembulatan premi tidak disebut sebagai konvensi tersendiri. Pembulatan itu **tersirat**: langkah hitung premi ditulis `upah * 24 // 10000`, dan butir 8 menjelaskan bahwa `//` berarti dibulatkan ke bawah.
- U11 `perubahan.md` (Ringkasan) menyebut konvensi ini secara langsung: "untuk aturan 2026, konvensi contoh sudah membulatkan hasil TER ke bawah ke rupiah penuh, jadi yang benar-benar baru adalah pembulatan dasar ke ribuan." Penulis contoh memang memaksudkan pembulatan ke bawah sebagai keadaan dasar 2026.
- U11, U12, U13, dan U14 sendiri juga mengatur pembulatan ke bawah untuk hal tertentu. Itu isi perubahan, bukan konvensi. Δ masing-masing menyatakannya sendiri, kecuali satu hal di U14 (bagian 4.4).

### 3.2 Apa kata regulasi nyata di KB

| Parameter | Nilai di KB emas | Sumber |
|---|---|---|
| `pph_round_mode` 2009–2024 | `truncate` | `BG-000` (INPUT-CONVENTION, butir 4) |
| `pph_round_mode` mulai 2025-01-01 | `half_up` | `GOLD-E13`, PER-11/PJ/2025 Pasal 129 ayat (1) dan ayat (3) huruf b ("sama dengan atau lebih dari 0,50 ... dibulatkan ke atas"), Pasal 130 huruf a |
| `bpjs_round_mode` | `half_up` | `BG-000` (INPUT-CONVENTION). Menurut tafsir K17, tidak ada regulasi yang mengatur pembulatan premi. Pilihan ini mengikuti fungsi ROUND di lembar kerja. |

Jadi:
- **PPh.** Asumsi contoh berbeda dengan bacaan KB atas hukum yang berlaku. Contoh menganggap pembulatan tidak diatur, sedangkan KB membaca PER-11/PJ/2025 sebagai pembulatan ke rupiah terdekat. Contoh disusun dan disegel pada 2026-10-27 pukul 18.36–19.32, sebelum tafsir K1 (ke rupiah terdekat mulai 2025) masuk ke spesifikasi pukul 19.37 dan sebelum E13 masuk ke rantai emas pukul 21.59. Waktu itu proyek sendiri masih menggolongkan PER-11/PJ/2025 sebagai pengecoh. Penulis contoh tidak salah menurut pengetahuan proyek saat itu.
- **Premi.** Tidak ada hukum yang dilanggar. Nilai di KB (`half_up`) dan nilai di contoh (ke bawah) sama-sama konvensi.

### 3.3 Bukti bahwa konvensi hanya menyelaraskan keadaan dasar

Saya menjalankan `../_alat/baseline.py`, yang hanya mencetak, dengan dan tanpa konvensi. KB 2026 tanpa Δ perubahan dibandingkan dengan `keluaran_menurut_aturan_2026` milik penulis contoh (log: `baseline_konvensi.log`, `baseline_tanpa.log`).

- **Dengan konvensi:** 89/100 contoh cocok. Sebelas sisanya hanya U04 dan U05, karena komponen Tapera dan internet belum dikenal KB. Itu memang tugas Δ perubahan.
- **Tanpa konvensi:** 76/100 contoh cocok. Tiga belas contoh tambahan berselisih Rp1 per bulan pada PPh.
- Semua kegagalan pada varian tanpa konvensi bernilai paling banyak Rp11, yaitu selisih Rp1 per bulan yang terakumulasi di Masa Pajak Terakhir.
- Salah satunya, U11-C2, adalah contoh **tahun 2026 yang tidak terpengaruh perubahan**. Kegagalan itu jelas tidak ada hubungannya dengan kemampuan menyatakan perubahan.

### 3.4 Penilaian

Δ konvensi **dapat dipertanggungjawabkan** karena empat hal:
1. Isinya dikutip dari bahan tersegel, bukan dicocokkan dengan angka.
2. Δ yang sama dipakai untuk ke-16 perubahan dan tidak menyentuh isi perubahan mana pun.
3. Δ itu sendiri berupa data (dua parameter berversi) tanpa perubahan *engine*. Ini justru contoh adaptivitas yang dirancang (representasi.md: pembulatan adalah parameter, sehingga perubahan pembulatan adalah pembaruan data).
4. Tanpa konvensi, contoh tidak lagi mengukur apa yang diukur H1. Yang diukur menjadi kecocokan asumsi dasar penulis contoh dengan tafsir K1/K17.

Cara membingkainya perlu dirapikan. Δ konvensi sebaiknya **tidak** disebut "bagian dari Δ setiap perubahan". Sebut saja sebagai penyelarasan keadaan dasar alat uji (*test fixture*) dengan asumsi tertulis penulis contoh, yang dipasang sekali di bawah semua perubahan. Pelaksana sudah menulisnya begitu di catatan Δ ("Applied before every change Delta; not part of any change"). Rumusan di makalah perlu mengikutinya.

Dua kelemahan perlu diungkapkan:
- **Bagian premi ditambahkan setelah kegagalan terlihat.** Bagian ini ditambahkan pada percobaan kedua U15, sesudah selisih U15-C5 diketahui. Ini keleluasaan peneliti (*researcher degree of freedom*). Dua hal meredamnya: dasarnya dapat ditunjuk di bahan tersegel (langkah `//` dan butir 8), dan parameter ini hanya berpengaruh pada U15, karena premi di kasus lain berupa nilai tagihan. Inilah alasan varian 15/16 perlu dilaporkan di samping hasil utama.
- **Nama mode berbeda.** Konvensi memakai mode `down`, sedangkan KB sebelum 2025 memakai `truncate`. Untuk nilai positif keduanya sama. Hasil TER dan premi selalu positif, jadi tidak ada dampak. Konvensi juga ikut mengubah `REG.YEAR.PPH.PART_YEAR` dan aturan lain yang membaca `pph_round_mode`. Itu tetap konsisten dengan asumsi contoh, yang membulatkan ke bawah di semua tempat.

### 3.5 Varian mana yang menjadi hasil utama

- Varian 8/16 **tidak tepat** dijadikan hasil utama, karena ia gagal pada contoh 2026 yang tidak terpengaruh perubahan. Laporkan sebagai analisis kepekaan dengan tafsir yang jelas: "kecocokan asumsi pembulatan dasar", bukan "kemampuan menyatakan perubahan".
- Hasil utama 16/16 dapat dipertahankan.
- Varian 15/16 adalah varian konservatif yang wajar, karena membuang satu-satunya bagian konvensi yang ditambahkan sesudah melihat kegagalan.
- Keputusan H1 sama pada kedua varian itu. Batas bawah 0,736 sudah dekat dengan ambang, dan itu perlu disebut.

## 4. Pemeriksaan sampel Δ

**Cara kerja.** Untuk keempat perubahan, saya membaca `perubahan.md`, Δ, dan contoh. Untuk ke-16 Δ, saya juga mencari angka di ekspresi aturan dan nilai parameter yang tidak muncul di teks perubahannya. Tidak ada yang ditemukan, kecuali:
- bagian tanggal "2027-01-01" (dari "1 Januari 2027");
- angka 400 untuk aturan tahun kabisat (U12);
- jumlah hari per bulan (U12);
- nilai turunan PTKP K/2 dan K/3 (U01: Rp60 juta + 2 × Rp5,4 juta).

Tabel kategori D pada U03 sama baris demi baris dengan Lampiran huruf E (44/44). Tabel U16 juga ditemukan seluruhnya di teks. Tidak ada aturan yang bersyarat pada nilai kasus tertentu.

### 4.1 U04 (T3, Tapera)

Δ ini sesuai dengan pasal-pasalnya:
- Iuran pemberi kerja menjadi nol mulai 2027 (Pasal 2).
- Iuran pegawai menjadi pengurang tahunan sebesar `min(dibayar, Rp200.000 × bulan iuran, Rp2.400.000)` (Pasal 3 ayat (2)).
- Pengurang ini tidak masuk dasar TER (Pasal 3 ayat (3)).

Perlakuan 2026, yaitu iuran pemberi kerja dihitung sebagai penghasilan, diambil dari Ringkasan perubahan, bukan dari angka. Catatan gaya: dua *change* (`REG.PREMIUMS.TAXABLE`, `REG.YEAR.DEDUCTIONS`) menulis ulang ekspresi dengan `valid_from` 2009. Untuk kasus tanpa Tapera, suku tambahannya bernilai nol, sehingga tidak ada dampak.

### 4.2 U06 (T4, DTP pegawai muda)

Kelima kriteria Pasal 3 dinyatakan semuanya:
- usia dihitung dari tanggal;
- penghasilan tetap bulan pertama ≤ Rp9 juta, tanpa premi, sesuai Pasal 5;
- syarat jumlah pegawai diuji per bulan, sesuai Pasal 4;
- DTP = PPh terutang, sesuai Pasal 6 ayat (1);
- pengembalian dibatasi sebesar PPh yang benar-benar dipotong, sesuai Pasal 6 ayat (4).

Batasan yang sudah diakui pelaksana: syarat "sebelumnya tidak pernah menjadi Pegawai Tetap pada pemberi kerja yang sama" dianggap terpenuhi, karena kasus tidak memuat atributnya.

### 4.3 U09 (T7, penghasilan tidak teratur)

TER atas bruto teratur dan metode selisih Pasal 17 sesuai dengan PMK Pasal 2–3:
- biaya jabatan 5% dengan batas Rp6 juta;
- iuran pensiun × 12;
- PTKP;
- PKP dibulatkan ke bawah ke ribuan dan tidak negatif;
- zakat tidak dikurangkan.

Catatan kecil: 5% biaya jabatan dibulatkan ke bawah ke rupiah, padahal teks tidak mengaturnya. Dampaknya hanya mungkin pada kasus batas yang sangat jarang, karena PKP langsung dibulatkan ke ribuan. Ini bukan pencocokan angka.

### 4.4 U14 (T10, *gross-up* golongan I–III)

Δ ini sesuai dengan Pasal 1–4:
- metode *gross-up* untuk golongan I–III, dan metode *gross* untuk golongan lain;
- titik tetap memakai aturan *gross-up* yang sudah ada di KB;
- pada Masa Pajak Terakhir, nilai minimal nol;
- lebih potong menjadi hak perusahaan.

Ada dua catatan:
- **Pembulatan tunjangan tidak dinyatakan oleh Δ U14 sendiri.** Pasal 3 ayat (1) SK U14 menyatakan tunjangan T "dibulatkan ke bawah hingga rupiah penuh". Δ U14 tidak menyatakannya. T di KB sama dengan `pph21_running`, yang mengikuti `pph_round_mode` global, sehingga ketentuan SK ini terpenuhi hanya karena Δ konvensi. Pada varian tanpa konvensi, U14-C1 gagal tepat di sini (T Rp323.320 lawan Rp323.319). Untuk U14, sebagian kegagalan di varian 8/16 berasal dari Δ yang tidak lengkap, bukan murni dari asumsi dasar. Ini tidak mengubah hasil utama, tetapi perlu dicatat di §7 RINGKASAN. Pertanyaan apakah T yang dibulatkan ke bawah dan PPh yang dibulatkan ke terdekat dapat dinyatakan terpisah tanpa perubahan *engine* tidak diuji dalam tinjauan ini.
- **Golongan dibaca sekali per tahun.** Pasal 1 ayat (3) meminta golongan dibaca per bulan. Semua contoh U14 memakai satu golongan sepanjang tahun, jadi ketentuan ini tidak teruji. Pelaksana sudah mengakuinya sebagai batas (§7 butir 4).

**Kesimpulan pemeriksaan sampel:** tidak ada Δ yang menanam nilai contoh. Semua Δ menyatakan aturan tertulis, dengan catatan U14 di atas.

## 5. Keutuhan *engine*

- `git diff engine-v1 -- system/pph21kbs/engine system/pph21kbs/expr` menghasilkan 0 baris.
- `git diff engine-v1 --stat -- system/pph21kbs/kb` juga kosong.
- *Tag* `engine-v1` dibuat 2026-10-28 01.39, sebelum E1 dijalankan.

## 6. Rekomendasi untuk pelaporan

1. **Putusan utama: H1 diterima.** RA = 16/16 = 1,00; CP 95% [0,794; 1,000]; batas bawah satu sisi 0,829 ≥ 0,70.
2. **Laporkan dalam satu tabel** varian 15/16 (batas bawah 0,736; tetap diterima) dan varian 8/16 (batas bawah 0,279). Untuk varian 8/16, sebutkan bahwa yang diukur adalah kecocokan asumsi pembulatan dasar, dan bahwa ia gagal juga pada contoh 2026 yang tidak terpengaruh perubahan.
3. **Sebut Δ konvensi sebagai penyelarasan keadaan dasar alat uji**, bukan bagian dari Δ perubahan. Kutip butir 2 dan 8 `konvensi` serta Ringkasan U11 sebagai dasarnya. Ungkapkan pula bahwa bagian premi ditambahkan pada percobaan kedua U15.
4. **Tambahkan catatan U14** (bagian 4.4) ke daftar batas di §7 RINGKASAN.
5. **Sebut sumber selisih pembulatan PPh.** Contoh disusun sebelum proyek membaca PER-11/PJ/2025 sebagai aturan pembulatan (K1/E13). Kalau ada revisi bahan uji di masa depan, `konvensi` sebaiknya mengikuti tafsir yang berlaku, atau menyebut PER-11/PJ/2025 secara tersurat.

## 7. Isi folder ini

| Berkas | Isi |
|---|---|
| `rerun.py` | Skrip jalankan ulang tiga varian; memakai `../_alat/` tanpa mengubahnya |
| `rerun.log`, `rerun_summary.json` | Keluaran dan ringkasan statistik |
| `utama/`, `tanpa_premi/`, `tanpa_konvensi/` | Hasil per perubahan (format sama dengan `../detail/`) |
| `baseline_konvensi.log`, `baseline_tanpa.log` | Keluaran `../_alat/baseline.py`: KB 2026 lawan `keluaran_menurut_aturan_2026` |
