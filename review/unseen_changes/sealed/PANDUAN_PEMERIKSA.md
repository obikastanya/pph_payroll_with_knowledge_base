# Panduan pemeriksa: perubahan tak terlihat U01–U16

Status: **selesai** (2026-10-27)

> **DOKUMEN FIKTIF UNTUK PENELITIAN.** Semua peraturan, surat keputusan, dan PKB dalam folder ini adalah rekaan. Dokumen-dokumen itu tidak berlaku dan tidak boleh dipakai untuk menghitung pajak sungguhan.

## 1. Untuk siapa dan kapan

Panduan ini ditujukan kepada ahli *payroll* atau perpajakan yang memeriksa materi uji **setelah segel dibuka**. Selama pengujian berlangsung, isi folder ini tidak boleh dilihat oleh perancang representasi pengetahuan. Keutuhan isinya dijaga dengan `MANIFEST.sha256`.

Ada dua hal yang diperiksa:

1. **Kewajaran.** Apakah perubahan itu sesuatu yang bisa diterbitkan oleh Kementerian Keuangan, DJP, Pemerintah, atau (untuk U14–U15) oleh perusahaan? Apakah bentuk dan bahasanya meyakinkan?
2. **Contoh perhitungan.** Apakah setiap contoh di `contoh.json` menerapkan aturan yang berlaku pada 2026 ditambah perubahan tersebut dengan benar? Apakah contoh yang ditandai "tidak berpengaruh" memang tidak berubah?

## 2. Isi folder

| Berkas | Isi |
|---|---|
| `Uxx/perubahan.md` | Teks perubahan bergaya peraturan, ditutup bagian "Ringkasan perubahan" |
| `Uxx/contoh.json` | 5–7 contoh perhitungan per perubahan |
| `INDEX.csv` | Jenis utama (T1–T10), sifat (S1–S6), tingkat kesulitan, dan jumlah contoh |
| `_alat/` | Skrip pembuat dan pemeriksa contoh (`buat_contoh.py`, `mesin.py`, `cek_aritmetika.py`, `tulis_lampiran.py`) |
| `MANIFEST.sha256` | Hash semua berkas, dibuat saat penyegelan |

Kode jenis dan sifat mengikuti `docs/spesifikasi/taksonomi.md` bagian 1. **Setiap perubahan berdiri sendiri.** Perubahan diterapkan di atas aturan yang berlaku pada 2026, dan perubahan lain dalam set ini dianggap tidak ada. Karena itu beberapa perubahan sama-sama "mengubah PP 58/2023" atau "mengubah PMK 168/2023" dengan nomor berbeda.

## 3. Cara membaca `contoh.json`

- `konvensi`: asumsi yang dipakai di semua contoh. Yang terpenting: hasil TER × bruto dibulatkan ke bawah ke rupiah penuh, premi BPJS sudah tercantum di input, dan batas upah JP 2027 diasumsikan Rp11.086.300.
- `input`: data kasus, berisi `status_ptkp`, `metode`, `tahun_pajak`, `masa[{bulan, komponen}]`, serta field tambahan bila perlu (`sektor`, `tanggal_mulai_bekerja`, `golongan`, `jenis_kelamin`, dan lain-lain).
- `keluaran_diharapkan`: per masa berisi `bruto`, `pph21` (terutang), dan `pph21_dipotong` (yang benar-benar dipotong dari pegawai). Ada pula `pph21_dtp` bila ada insentif DTP. Bagian `setahun` diisi bila contoh memuat Masa Pajak Terakhir.
- `keluaran_menurut_aturan_2026`: hasil untuk input yang sama bila perubahan diabaikan. Pakai ini untuk melihat dampak perubahan.
- `perubahan_berpengaruh` dan `alasan`: apakah perubahan mengubah hasil contoh, dan mengapa.
- `langkah`: urutan perhitungan. `ekspresi` ditulis dalam notasi Python (`//` = bagi lalu bulatkan ke bawah; `x * 225 // 10000` = 2,25% × x). Langkah tabel mencantumkan `tabel` dan `nilai`.
- `cek_aritmetika`: hasil pemeriksaan otomatis oleh `_alat/cek_aritmetika.py`. Pemeriksaan ini menghitung ulang setiap ekspresi, mencari ulang setiap tarif di tabel, memastikan setiap angka berasal dari input, langkah sebelumnya, atau konstanta, dan memastikan setiap keluaran sama dengan hasil langkah. "cocok" berarti aritmetikanya benar. **Ini tidak membuktikan tafsir hukumnya benar.** Tafsir itulah yang perlu Anda periksa.

Untuk menjalankan ulang: `env\Scripts\python.exe review\unseen_changes\sealed\_alat\buat_contoh.py`, lalu `... cek_aritmetika.py`. Contoh hanya boleh diubah lewat `buat_contoh.py`, bukan dengan mengedit JSON langsung. Setelah itu segel harus dibuat ulang.

## 4. Pertanyaan umum untuk setiap perubahan

1. Apakah jenis dokumen, penerbit, dan nomornya masuk akal? Apakah tanggal penetapan dan tanggal berlakunya masuk akal?
2. Apakah teks pasal cukup jelas untuk dihitung tanpa menebak? Bila ada celah tafsir, tuliskan.
3. Apakah ringkasan sesuai dengan isi pasal?
4. Apakah contoh yang ditandai "berpengaruh" menunjukkan dampak yang benar? Apakah contoh yang ditandai "tidak berpengaruh" memang tidak berubah?
5. Apakah ada kasus penting yang belum tercakup oleh contoh?

## 5. Pertanyaan per perubahan

Jawaban atas lima pertanyaan umum di bagian 4 dicantumkan pada setiap perubahan dengan label "Umum". Semua angka di bawah sudah dihitung ulang dengan program pemeriksa tersendiri yang membaca tabel di `dataset/01_regulasi/tables/` dan teks `perubahan.md`, terpisah dari `_alat/`.

### U01 — Penyesuaian PTKP (T1; S1)
- Apakah angka PTKP baru (Rp60.000.000; Rp5.400.000) dan pola penetapannya lewat PMK masuk akal?
- Contoh C5 memakai Pasal 3 ayat (2): pegawai berhenti Februari 2027, sebelum PMK diundangkan, dihitung ulang lewat pembetulan. Apakah hasil yang diharapkan (perhitungan dengan PTKP baru) sudah tepat?
- Contoh C3 menghasilkan lebih potong di Desember. Apakah perlakuan pengembaliannya benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Angka dan pola penetapan masuk akal. Kenaikannya sekitar 11% (Rp54 juta menjadi Rp60 juta; Rp4,5 juta menjadi Rp5,4 juta). Penetapan lewat PMK setelah konsultasi dengan DPR sesuai Pasal 7 ayat (3) UU PPh. Keberlakuan surut ke awal tahun pajak meniru PMK 101/2016, yang diundangkan Juni 2016 dan berlaku untuk Tahun Pajak 2016.
- Teks direvisi. Pasal 1 ayat (1) semula berbunyi "diberikan paling sedikit sebesar". Rumusan itu berasal dari UU dan di dalam PMK terbaca sebagai batas bawah, bukan angka pasti. Rumusan diganti menjadi "disesuaikan menjadi sebagai berikut", sama dengan PMK 101/2016 Pasal 1.
- C5 tepat. Masa Pajak Terakhir (Februari) berakhir sebelum 19 Maret 2027, sehingga Pasal 3 ayat (2) mewajibkan penghitungan ulang dengan PTKP TK/1 Rp65.400.000 dan biaya jabatan Rp500.000 × 2. Hasilnya PPh setahun Rp658.500 dan lebih potong Februari Rp5.852.860 (semula Rp5.507.860), yang dikembalikan menurut ayat (3).
- C3 benar. PPh setahun Rp178.300 lebih kecil daripada potongan Januari–November Rp316.228, sehingga lebih potong Rp137.928 dikembalikan oleh pemotong kepada pegawai pada Masa Pajak Terakhir. Ini sesuai praktik PMK 168/2023 dan konvensi contoh.
- Umum: penerbit, nomor, dan tanggal (ditetapkan 18 Maret, diundangkan 19 Maret 2027) wajar. Ringkasan sesuai dengan pasal. C1, C3, C4, C5, dan C6 berpengaruh dengan benar. C2 (tahun 2026) dan C7 (PKP tetap nihil) memang tidak berubah. Kasus karyawati kawin tidak dicontohkan, tetapi tidak wajib karena Pasal 1 ayat (3) hanya menegaskan aturan lama.

### U02 — Batas biaya jabatan Rp750.000/Rp9.000.000 (T1; S5)
- Apakah Pasal II ayat (2) (batas Rp750.000 × jumlah bulan bekerja) konsisten dengan praktik untuk pegawai yang masuk di tengah tahun?
- Pada contoh C4, 5% bruto berada di antara batas lama dan batas baru. Apakah dampaknya benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Pasal II ayat (2) konsisten dengan praktik batas bulanan × jumlah bulan bekerja, yang juga dipakai konvensi contoh untuk aturan 2026 (Rp500.000 × bulan). Pada C5 (Juli–Desember), 5% bruto Rp7.684.500 dibatasi menjadi Rp4.500.000 (6 × Rp750.000), sedangkan menurut aturan 2026 menjadi Rp3.000.000.
- Dampak C4 benar. Bruto setahun Rp137.992.800, sehingga 5% = Rp6.899.640, yaitu di atas Rp6 juta dan di bawah Rp9 juta. Biaya jabatan menjadi Rp6.899.640, PPh setahun turun dari Rp4.429.800 menjadi Rp4.294.950, dan Desember berubah dari kurang potong Rp2.531 menjadi lebih potong Rp132.319.
- Umum: bentuk (PMK perubahan PMK 168/2023, ditetapkan 20 November 2026, berlaku 1 Januari 2027) wajar. Teks cukup jelas. C2 (2026), C3 (5% bruto di bawah Rp6 juta), dan C6 (tanpa Masa Pajak Terakhir) memang tidak berubah.

### U03 — Kategori D TER untuk TK/0 (T2; S5, S6)
- Apakah pembentukan kategori keempat lewat perubahan PP 58/2023 dan Lampiran huruf E masuk akal?
- Periksa tabel kategori D: batas di bawah Rp100 juta digeser turun Rp400.000, dan batas Rp100 juta ke atas sama dengan A. Apakah tabelnya menaik dan tidak tumpang tindih?
- Contoh C7: karyawati kawin yang PTKP-nya hanya diri sendiri dimasukkan ke kategori D. Apakah tafsir ini sesuai dengan teks Pasal 2 ayat (4) huruf d?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Pembentukan kategori keempat masuk akal. Kategori dan tabel TER memang diatur dalam PP 58/2023 Pasal 2 ayat (4)–(5) dan lampirannya. Lampiran huruf D (TER harian) tidak tersentuh, sehingga tabel baru tepat diberi huruf E.
- Tabel D diperiksa dengan program. Tabel memuat 44 lapisan, menaik, tanpa celah atau tumpang tindih, dengan tarif sama dengan kategori A. Setiap batas di bawah Rp100 juta sama dengan batas A dikurangi Rp400.000, dan batas Rp100 juta ke atas sama persis dengan A. Tabel di `perubahan.md` sama dengan `tabel_perubahan` di `contoh.json`.
- C7 sesuai dengan teks. Huruf d secara tegas memasukkan "penerima penghasilan yang besarnya PTKP hanya sebesar PTKP untuk dirinya sendiri". Bruto Rp8.300.000 dikenai 1,75% = Rp145.250 (aturan 2026: kategori A 1,5% = Rp124.500).
- Umum: bentuk dan tanggal (ditetapkan 30 Oktober, berlaku 1 Januari 2027) wajar. C5 menunjukkan PPh setahun tetap Rp8.545.350, sesuai ringkasan. C2 (TK/1), C3 (2026), dan C6 (Rp110 juta, di atas batas Rp100 juta) memang tidak berubah.

### U04 — Iuran Tapera (T3)
- Menurut aturan 2026, contoh memperlakukan iuran Tapera bagian pemberi kerja sebagai penghasilan (PMK 168/2023 Pasal 5 ayat (2)). Apakah anggapan ini dapat diterima sebagai titik awal?
- Apakah batas pengurang Rp200.000 per bulan iuran wajar?
- Contoh C6: pegawai masuk Oktober, sehingga batasnya Rp200.000 × 3. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Anggapan itu dapat diterima sebagai titik awal. PMK 168/2023 Pasal 7 huruf c hanya mengecualikan iuran program pensiun dan hari tua yang dibayar pemberi kerja, dan Tapera tidak disebut. Pembayaran pemberi kerja untuk kepentingan pegawai termasuk penghasilan menurut Pasal 5 ayat (2)–(3). Perlakuan ini memang belum seragam di praktik, tetapi asumsi ini konsisten dan dinyatakan terbuka dalam ringkasan.
- Batas Rp200.000 per bulan wajar. Angka ini setara 2,5% dari upah sekitar Rp8 juta dan sejajar dengan batas biaya pensiun Rp200.000 per bulan.
- C6 benar. Iuran dibayar 3 bulan (Oktober–Desember), sehingga batasnya Rp600.000; iuran Rp900.000 dibatasi menjadi Rp600.000. Neto Rp34.481.811 di bawah PTKP K/0, sehingga PKP nol dan seluruh potongan Oktober–November (Rp1.254.480) dikembalikan.
- Umum: PMK berdiri sendiri (bukan perubahan PMK 168/2023) dan bertanggal 22/23 Desember 2026, wajar. Pasal 3 ayat (3) menutup celah tafsir untuk TER bulanan. C3 (2026) dan C4 (bukan peserta) memang tidak berubah.

### U05 — Penggantian internet kerja jarak jauh (T3; S2, S5)
- Apakah bentuk pengecualian, yaitu penggantian berdasarkan bukti dengan batas Rp400.000 dan syarat paling sedikit 8 hari, masuk akal sebagai sisipan Pasal 7 dan Pasal 7A PMK 168/2023?
- Contoh C6: hari kerja jarak jauh berbeda tiap bulan. Periksa bulan-bulan yang lolos syarat dan yang tidak.
- Apakah kelebihan di atas Rp400.000 memang tepat diperlakukan sebagai penghasilan teratur?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Bentuk pengecualian masuk akal. Pasal 7 PMK 168/2023 memang berisi daftar huruf a–h, sehingga penambahan huruf i dan Pasal 7A yang memuat syarat dan batas nilai mengikuti pola pengecualian bersyarat seperti natura dalam PMK 66/2023.
- Penerapan C6 benar. Bulan yang lolos (paling sedikit 8 hari) adalah Januari, Februari, April, Mei (tepat 8 hari), Juli, Agustus, September, November, dan Desember; pada bulan itu hanya kelebihan Rp50.000 yang masuk bruto. Bulan yang tidak lolos adalah Maret (6 hari), Juni (7 hari), dan Oktober (4 hari); pada bulan itu seluruh Rp450.000 masuk bruto.
- Kelebihan di atas Rp400.000 tepat diperlakukan sebagai penghasilan teratur, karena penggantian dibayar setiap bulan dan termasuk "penghasilan teratur lainnya" menurut Pasal 5 ayat (3) huruf a.
- Umum: tanggal (ditetapkan 4 Desember, berlaku Masa Pajak Januari 2027) wajar dan teks cukup jelas. C3 (5 hari), C4 (tunjangan tunai tetap), dan C5 (2026) memang tidak berubah.

### U06 — DTP pegawai baru usia muda (T4; S2, S3)
- Apakah kombinasi kriterianya masuk akal untuk insentif nyata? Kriterianya: mulai bekerja pada 2027, usia ≤ 30, NIK terintegrasi, gaji dan tunjangan tetap ≤ Rp9 juta di bulan pertama, tidak menerima DTP lain, dan jumlah pegawai tetap perusahaan bertambah (diuji per bulan).
- Pasal 6 ayat (4): lebih potong dikembalikan hanya sebatas PPh yang benar-benar dipotong. Periksa C1 dan C6 (sisa kelebihan DTP tidak dikembalikan) serta C5 (lebih potong dikembalikan dari PPh Januari, Februari, Juli, dan Agustus).
- Apakah perhitungan usia pada tanggal mulai bekerja sudah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Kombinasi kriteria masuk akal. NIK terintegrasi, batas penghasilan tetap pada bulan pertama, dan larangan menerima DTP lain meniru PMK 10/2025 dan PMK 105/2025. Syarat usia dan syarat penambahan pegawai lazim untuk insentif penciptaan lapangan kerja. Syarat penambahan pegawai dapat dihitung karena jumlah pegawai akhir bulan tersedia di input.
- Pasal 6 ayat (4) diterapkan dengan benar. C1: PPh setahun Rp911.700 dan DTP Maret–November Rp1.058.463; tidak ada PPh yang dipotong dari pegawai, sehingga kelebihan Rp146.763 tidak dikembalikan dan potongan Desember nol. C6: kelebihan Rp361.876 tidak dikembalikan dengan alasan yang sama. C5: PPh yang benar-benar dipotong pada Januari, Februari, Juli, dan Agustus (4 × Rp125.448 = Rp501.792) melebihi lebih potong Rp96.904, sehingga seluruh lebih potong dikembalikan.
- Usia dihitung dalam tahun penuh pada tanggal mulai bekerja, dan hasilnya benar: C1 25, C2 31 (tidak memenuhi), C3 26, C4 24, C5 22, C6 28, C7 25.
- Umum: PMK baru (ditetapkan 26 Februari, diundangkan 1 Maret 2027) dengan masa insentif mulai Maret 2027, sehingga konsisten dan tidak berlaku surut. C2, C3, C4, dan C7 memang tidak berubah. Ada dua kasus yang belum dicontohkan dan tidak wajib ditambah: usia tepat 30 tahun, dan pegawai yang mulai bekerja di tengah bulan. Untuk kasus kedua, Pasal 5 ayat (1) merujuk pada gaji dan tunjangan yang ditetapkan dalam perjanjian kerja, sehingga yang diuji adalah nilai sebulan penuh.

### U07 — Perpanjangan DTP PMK 105/2025 sampai Juni 2027 (T6; S1, S2, S3, S5, S6)
- Apakah perpanjangan lewat perubahan PMK 105/2025 yang berlaku surut ke Masa Pajak Januari masuk akal? Apakah mekanisme pengembalian PPh Januari sudah memadai?
- Pasal 5 ayat (5a) baru mengatur Masa Pajak Terakhir 2027. Periksa C1 (kurang bayar Desember) dan C5 (lebih potong yang dikembalikan sebatas potongan Juli–November).
- C6: pegawai masuk Maret 2027, sehingga kriteria diuji pada bulan pertama bekerja. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Perpanjangan dengan cara ini masuk akal; polanya sama dengan PMK 72/2025 yang mengubah PMK 10/2025. Rujukan pasal (Pasal 2 ayat (2), Pasal 3 ayat (2), Pasal 4 ayat (2) huruf b, Pasal 5, Pasal 6 ayat (4)) cocok dengan PMK 105/2025. Mekanisme pengembalian PPh Januari memadai: dikembalikan paling lambat bersama gaji Februari, disertai pembetulan SPT Masa Januari dan batas pelaporan baru 31 Juli 2027.
- C1 benar. Desember kurang potong Rp553.048, yaitu PPh setahun Rp1.473.000 dikurangi PPh terutang Januari–November (6 bulan DTP dan 5 bulan dipotong, masing-masing Rp83.632).
- C5 benar. PPh setahun Rp560.700 lebih kecil daripada PPh terutang Januari–November Rp620.961, sehingga lebih potong Rp60.261. Jumlah ini dikembalikan seluruhnya karena potongan Juli–November (Rp282.255) lebih besar.
- C6 benar. Menurut Pasal 4A ayat (1) huruf b, batas Rp10 juta diuji pada bulan pertama bekerja (Maret 2027, gaji Rp9 juta). DTP diberikan Maret–Juni, lalu Juli–Agustus dipotong biasa.
- Umum: semua KLU contoh dicocokkan dengan Lampiran A PMK 105/2025. C3 (KLU 46100 tidak tercantum) dan C4 (Rp10,5 juta) memang tidak berubah.

### U08 — PTKP tanggungan karyawati kawin (T5; S2, S5)
- Apakah perluasan cakupan ini (surat pernyataan, PTKP diri ditambah tanggungan tanpa PTKP kawin) masuk akal?
- Apakah aturan kategori TER mengikuti TK/x (ayat (2b)) tepat? Periksa C1 (K/2 menjadi TK/2, kategori B) dan C4 (K/3 menjadi TK/3, kategori B).
- Apakah perlakuan dasar 2026 dalam contoh benar, yaitu karyawati kawin tanpa keterangan kecamatan memakai PTKP TK/0 dan kategori A?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Perluasan masuk akal. Surat pernyataan yang diketahui suami mencegah tanggungan dihitung dua kali. Teks direvisi: ayat (2a) semula hanya menyebut batas penyampaian "pada awal tahun kalender", sehingga karyawati yang mulai bekerja di tengah tahun tidak terjangkau. Kini ditambahkan "atau pada saat mulai bekerja", dan surat pernyataan berlaku untuk tahun kalender tersebut. Contoh tidak berubah.
- Ayat (2b) tepat dan konsisten dengan PTKP yang diberikan (diri ditambah tanggungan sama dengan TK/x). C1: TK/2, kategori B, Rp12.544.800 × 3% = Rp376.344. C4: TK/3, kategori B (bukan C), Rp9.408.600 × 1,5% = Rp141.129.
- Perlakuan dasar 2026 benar. PMK 168/2023 Pasal 9 ayat (2) huruf a memberi karyawati kawin PTKP dirinya sendiri (Rp54 juta), dan dalam pemotongan ia diperlakukan seperti TK/0 (kategori A).
- Label direvisi: sifat ditambah S2, karena ketentuan hanya berlaku bagi karyawati kawin yang menyerahkan surat pernyataan.
- Umum: tanggal wajar. C2 (tanpa surat pernyataan), C3 (2026), C5 (pegawai laki-laki), C6 (keterangan kecamatan), dan C7 (tanpa tanggungan) memang tidak berubah.

### U09 — Metode penghasilan tidak teratur, dua dokumen (T7; S4, S5)
- Apakah pembagian kewenangan masuk akal, yaitu prinsip di PP dan rumus di PMK?
- Periksa rumus selisih di Pasal 3 PMK 118/2026: biaya jabatan dihitung terpisah untuk tiap PKP, iuran pensiun bulan berjalan dikali 12, dan zakat tidak dihitung.
- C4: PPh setahun harus sama dengan aturan 2026, dan hanya pembagian antarbulan yang berubah. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Pembagian kewenangan masuk akal dan sama dengan pasangan PP 58/2023 (tarif) dan PMK 168/2023 (tata cara), sesuai Pasal 21 ayat (8) UU PPh. Teks direvisi: kedua dokumen semula tidak mencantumkan tanggal pengundangan, sehingga kini ditambahkan "Diundangkan ... 22 Desember 2026" (PP) dan "29 Desember 2026" (PMK) agar bentuknya lengkap. Tanggal berlaku tidak berubah.
- Rumus selisih wajar dan diterapkan dengan benar. Metode ini sama dengan metode penghasilan tidak teratur PER-16/PJ/2016. Biaya jabatan dihitung dan dibatasi Rp6 juta untuk masing-masing PKP, iuran JHT dan JP bulan berjalan dikali 12, PTKP setahun dikurangkan, dan zakat tidak dihitung. Selisihnya: C1 Rp2.250.000, C4 Rp3.000.000, C6 Rp30.000.000.
- C4 benar. PPh setahun tetap Rp29.463.750. Potongan Maret menjadi Rp4.852.920 (9% × Rp20.588.000 ditambah selisih Rp3.000.000), dan Desember Rp6.081.630 menutup sisanya. Bonus Desember jatuh pada Masa Pajak Terakhir, sehingga tidak memakai metode baru.
- Umum: C2 (2026) dan C3 (tanpa penghasilan tidak teratur) memang tidak berubah. Ringkasan sesuai.

### U10 — Penghapusan zakat sebagai pengurang (T8; S5)
- Apakah pencabutan tanpa pengganti ini masuk akal, dengan zakat dikembalikan ke SPT Tahunan?
- C4: Januari–Maret tanpa Masa Pajak Terakhir, sehingga tidak berpengaruh. C5: pegawai berhenti Juni, sehingga berpengaruh. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Pencabutan ini masuk akal. Sebelum PMK 168/2023, PER-16/PJ/2016 juga tidak mengurangkan zakat dalam pemotongan, dan Pasal 9 ayat (1) huruf g UU PPh tetap dapat dipakai di SPT Tahunan. Ketentuan sejenis bagi pejabat negara dan PNS (Pasal 17 ayat (6) huruf c dan ayat (7) huruf b PMK 168/2023) tidak ikut dihapus. Hal ini di luar lingkup penelitian dan tidak memengaruhi contoh, sehingga teks dibiarkan.
- C4 benar karena zakat hanya dipakai pada Masa Pajak Terakhir. C5 benar: Masa Pajak Terakhir Juni, neto naik Rp3.000.000 (zakat 6 bulan), sehingga PPh setahun naik dari Rp3.069.300 menjadi Rp3.519.300 dan lebih potong Juni turun dari Rp6.195.300 menjadi Rp5.745.300.
- Umum: tanggal wajar. C2 (2026) dan C3 (tanpa zakat) memang tidak berubah.

### U11 — Pembulatan dasar TER ke ribuan (T9; S5)
- Apakah pengaturan pembulatan seperti ini masuk akal untuk PMK, misalnya demi keseragaman dengan Coretax?
- C1 dan C5: pembulatan memindahkan bruto ke lapisan yang lebih rendah. Apakah memang dikehendaki bahwa lapisan dicari setelah pembulatan (Pasal 15A ayat (1))?
- Konvensi contoh untuk aturan 2026 sudah membulatkan hasil TER ke bawah ke rupiah penuh. Apakah konvensi ini dapat diterima?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Pengaturan ini masuk akal untuk PMK. Pembulatan PKP sudah diatur di Pasal 8 ayat (4), sedangkan pembulatan dasar TER belum diatur, sehingga alasan keseragaman dengan sistem administrasi wajar.
- Kalimat kedua Pasal 15A ayat (1) tegas menyatakan bahwa lapisan dicari dari bruto yang sudah dibulatkan. Karena itu C1 (Rp5.400.700 menjadi Rp5.400.000, lapisan 0%) dan C5 (Rp9.650.400 menjadi Rp9.650.000, lapisan 1,75%) memang dikehendaki.
- Konvensi itu dapat diterima. PP 58/2023 dan PMK 168/2023 tidak mengatur pembulatan hasil TER, dan pembulatan ke bawah ke rupiah lazim dipakai aplikasi *payroll*. Akibatnya, ayat (2) tidak menambah perbedaan, sehingga C3 benar tidak berubah.
- Umum: C6 menunjukkan potongan Januari–November turun Rp26 per bulan dan Desember menyesuaikan, dengan PPh setahun tetap. C2 (2026) memang tidak berubah.

### U12 — Bulan pertama tidak penuh, tarif dari bruto setara (T9; S2, S5)
- Apakah rumus bruto setara (hari kalender, termasuk tanggal mulai, dibulatkan ke bawah) masuk akal dan cukup jelas?
- C6: penghasilan tidak teratur ditambahkan tanpa disetarakan. Apakah benar?
- C5: Desember menghasilkan lebih potong besar, karena tarif bulanan pegawai yang masuk tengah tahun memang tinggi. Apakah ini wajar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Rumusnya masuk akal. Teks direvisi: penyebut rumus kini menyebut "termasuk tanggal mulai bekerja", yang semula hanya ada di ringkasan. Penyebut yang dipakai contoh: C1 16–30 September (15 hari), C4 20–28 Februari (9 hari), C5 10–31 Juli (22 hari), C6 15–31 Maret (17 hari). Hasil contoh tidak berubah.
- C6 benar. Ayat (2) hanya menyetarakan penghasilan teratur, sehingga bonus Rp5 juta ditambahkan utuh. Bruto setara Rp14.999.998 menghasilkan tarif 6%, dikalikan bruto sebenarnya Rp10.483.870 = Rp629.032.
- C5 wajar. Bruto setara Juli Rp20.784.361 menghasilkan tarif 9%, sehingga potongan Juli Rp1.327.517. Lebih potong Desember (Rp6.077.147) sudah terjadi menurut aturan 2026 (Rp5.634.641), karena TER bulanan dirancang untuk penghasilan setahun penuh sementara pegawai mendapat PTKP setahun penuh. Perubahan hanya menambah Rp442.506, dan PPh setahun tetap Rp2.662.050.
- Umum: tanggal wajar. Ayat (4) dan Pasal II menutup kasus Masa Pajak Terakhir dan pegawai lama. C2 (mulai tanggal 1) dan C3 (2026) memang tidak berubah.

### U13 — PTKP proporsional di Masa Pajak Terakhir (T9; S2, S5)
- Apakah kebijakan ini masuk akal secara hukum, mengingat UU PPh Pasal 7 mengatur PTKP setahun? Atau perlu dasar yang lebih tinggi?
- Pasal II ayat (2): bagian bulan dihitung satu bulan penuh. Apakah konsisten dengan contoh?
- C6: PKP menjadi positif untuk pegawai yang hanya bekerja 2 bulan. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Kebijakan ini masuk akal dengan dasar PMK. Pasal 7 UU PPh menetapkan PTKP setahun untuk menghitung pajak terutang wajib pajak dalam SPT Tahunan, sedangkan Pasal 21 ayat (8) UU PPh mendelegasikan tata cara pemotongan kepada PMK. Ketentuan ini hanya mengatur bagian PTKP yang dikurangkan dalam pemotongan, dan sisanya tetap dipakai di SPT Tahunan (Pasal II ayat (3)), sehingga hak wajib pajak atas PTKP setahun tidak dikurangi.
- Pasal II ayat (2) konsisten dengan contoh. Semua contoh mulai atau berhenti pada batas bulan, sehingga jumlah bulan bekerja sama dengan jumlah masa: C1 6, C2 9, C6 2.
- C6 benar. PTKP Rp54.000.000 × 2/12 = Rp9.000.000, neto Rp11.557.560, PKP Rp2.557.000, PPh setahun Rp127.850, dan Desember kurang potong Rp80.807 (aturan 2026: lebih potong Rp47.043).
- Umum: tanggal wajar. C3 (12 bulan), C4 (2026), dan C5 (tanpa Masa Pajak Terakhir) memang tidak berubah. Pengecualian kewajiban subjektif di tengah tahun (Pasal II ayat (1)) belum dicontohkan; contoh tambahan untuk itu disarankan, tetapi tidak wajib.

### U14 — Gross-up golongan I–III (T10; S2)
- Apakah prosedur iterasi (mulai dari T = 0, ulang sampai tetap; di Desember minimal nol) cukup jelas untuk diterapkan oleh tim *payroll*?
- C6: tunjangan mendorong bruto ke lapisan TER berikutnya. Periksa iterasinya.
- C4: lebih potong Desember menjadi hak perusahaan (Pasal 4 ayat (4)). Apakah perlakuan ini wajar dan sesuai praktik?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Prosedurnya cukup jelas. TER dan PPh setahun tidak pernah turun ketika T naik, sehingga iterasi yang dimulai dari T = 0 selalu naik dan pasti berhenti tanpa berosilasi.
- Iterasi C6 benar. Dengan B = Rp7.286.438 (K/2, kategori B), T bergerak 0 → 54.648 (0,75%) → 73.410 (1%, karena bruto melewati Rp7.300.000) → 73.598 → 73.600 → 73.600.
- Perlakuan C4 wajar sebagai kebijakan perusahaan dan lazim dalam skema *gross-up*: perusahaan memulihkan tunjangan yang berlebih. Dengan T Desember = 0, PPh setahun Rp9.519.450 lebih kecil daripada PPh Januari–November Rp9.636.146, sehingga lebih potong Rp116.696.
- Contoh C4 dikoreksi. Kolom `pph21_dipotong` Desember semula −116.696, yang berarti dikembalikan kepada pegawai. Nilai itu bertentangan dengan Pasal 4 ayat (4), sehingga diubah menjadi 0, sejalan dengan perlakuan kelebihan DTP pada U06/U07. Kolom `pph21` Desember tetap −116.696 (lebih bayar pada SPT Masa), dan `lebih_potong_menjadi_hak_perusahaan` tetap Rp116.696. Perbaikan dilakukan di `_alat/buat_contoh.py` (kelas U14) lalu contoh dibuat ulang.
- Umum: bentuk SK Direksi wajar. C2 (golongan IV), C3 (2026), dan C5 (PPh nol, sehingga tunjangan nol) memang tidak berubah.

### U15 — PKB, kenaikan gaji berlaku surut dengan rapel (T10; S1, S2)
- Apakah klausul PKB ini lazim? Klausulnya: kenaikan 8% dibulatkan ke atas ke ribuan, rapel dibayar April, ada rapel premi BPJS, dan pegawai yang berhenti sebelum penandatanganan tidak berhak.
- Periksa rapel iuran JKN dan JP terhadap batas upah: C6 di atas batas JKN Rp12 juta, dan C1 menyentuh batas JP Rp11.086.300.
- Apakah perlakuan pajak rapel sebagai penghasilan Masa Pajak April, tanpa menghitung ulang Januari–Maret, sudah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Klausulnya lazim. Teks direvisi: Pasal 5 ayat (1) semula berbunyi "Hasil kenaikan dibulatkan ke atas", yang dapat dibaca sebagai pembulatan besaran kenaikan atau pembulatan gaji baru. Kini ditegaskan bahwa yang dibulatkan adalah gaji pokok baru. Hasil contoh tidak berubah karena semua gaji lama kelipatan ribuan (C5: Rp9.876.000 × 108% = Rp10.666.080, dibulatkan menjadi Rp10.667.000).
- Rapel terhadap batas upah benar. C6: upah lama Rp17 juta dan baru Rp18,2 juta sama-sama di atas batas JKN dan JP, sehingga rapel JKN dan JP nihil, sedangkan rapel JKK, JKM, dan JHT tetap ada. C1: upah lama Rp11 juta (JP Rp110.000), upah baru Rp11,8 juta di atas batas JP, sehingga JP baru Rp110.863 dan rapel JP 3 × Rp863 = Rp2.589.
- Perlakuan pajaknya benar. Rapel diterima April, sehingga menjadi penghasilan Masa Pajak April. Potongan Januari–Maret tidak dihitung ulang, dan selisihnya ditampung pada Masa Pajak Terakhir.
- Umum: penandatanganan pada 12 April 2027, sebelum gaji April dibayar, wajar untuk PKB. C2 (berhenti Februari) dan C4 (2026) memang tidak berubah. C3 benar hanya memuat rapel Februari–Maret.

### U16 — Perluasan lapisan 0% TER A/B/C (T2; S5, S6)
- Apakah batas baru (A Rp6.000.000; B Rp6.850.000; C Rp7.350.000) dan penghapusan lapisan 0,25% dan 0,5% masuk akal?
- Periksa tabel lengkap di lampiran: batas di atas lapisan baru harus sama persis dengan PP 58/2023.
- C3 (K/1, Rp7 juta) tidak berubah karena berada di atas lapisan yang diubah. Apakah benar?

- [x] Disetujui  - [ ] Perlu revisi
Catatan:
- Batas baru dan penghapusan kedua lapisan masuk akal. Batas B dan C sama dengan batas atas lapisan 0,5% yang lama, sedangkan batas A jatuh di dalam lapisan 0,75% yang lama, sehingga lapisan 0,75% kategori A menyempit menjadi Rp6.000.000–Rp6.300.000.
- Tabel lengkap diperiksa dengan program. Kategori A memuat 42 lapisan, B 38, dan C 39. Di atas batas baru, semua batas dan tarif sama persis dengan PP 58/2023. Tabel menaik tanpa celah, dan isi `perubahan.md` sama dengan `tabel_perubahan` di `contoh.json`.
- C3 benar. Rp7.000.000 untuk K/1 (kategori B) berada di lapisan 0,75% (Rp6.850.000–Rp7.300.000), yang batas dan tarifnya tidak berubah.
- Umum: bentuk dan tanggal wajar. C6 menunjukkan PPh setahun tetap Rp536.100. C2 (2026) dan C7 (lapisan atas) memang tidak berubah.

## 6. Penutup pemeriksaan

Nama pemeriksa: pemeriksa *payroll* dan perpajakan
Tanggal: 2026-10-27
Status: **selesai**
Ringkasan temuan:
- Ke-16 perubahan dinilai wajar dan dapat dihitung tanpa menebak. Rujukan pasal ke PP 58/2023, PMK 168/2023, dan PMK 105/2025 dicocokkan dengan teks aslinya.
- Seluruh 100 contoh dihitung ulang dengan program pemeriksa tersendiri, baik untuk keluaran yang diharapkan maupun keluaran menurut aturan 2026. Satu contoh dikoreksi (U14-C4, `pph21_dipotong` Desember). Setelah revisi, tidak ada selisih aritmetika (100 contoh, 0 selisih), dan pemeriksaan `_alat/cek_aritmetika.py` juga cocok untuk ke-100 contoh.
- Setiap perubahan memiliki paling sedikit satu contoh yang berpengaruh dan satu yang tidak berpengaruh, dan penanda `perubahan_berpengaruh` sesuai dengan perbandingan terhadap aturan 2026.
- Teks diperjelas pada lima perubahan, tanpa mengubah hasil contoh: U01 (rumusan PTKP), U08 (waktu penyampaian surat pernyataan), U09 (tanggal pengundangan), U12 (penyebut bruto setara), dan U15 (objek pembulatan gaji baru).
- Label dikoreksi pada satu perubahan: U08 ditambah sifat S2 di `INDEX.csv`. Label lain sudah tepat.

Revisi atas contoh atau teks dilakukan peneliti lewat `_alat/`. Setelah revisi, segel dibuat ulang dan hash baru dicatat.
