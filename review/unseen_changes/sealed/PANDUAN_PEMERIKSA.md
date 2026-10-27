# Panduan pemeriksa: perubahan tak terlihat U01–U16

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

### U01 — Penyesuaian PTKP (T1; S1)
- Apakah angka PTKP baru (Rp60.000.000; Rp5.400.000) dan pola penetapannya lewat PMK masuk akal?
- Contoh C5 memakai Pasal 3 ayat (2): pegawai berhenti Februari 2027, sebelum PMK diundangkan, dihitung ulang lewat pembetulan. Apakah hasil yang diharapkan (perhitungan dengan PTKP baru) sudah tepat?
- Contoh C3 menghasilkan lebih potong di Desember. Apakah perlakuan pengembaliannya benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U02 — Batas biaya jabatan Rp750.000/Rp9.000.000 (T1; S5)
- Apakah Pasal II ayat (2) (batas Rp750.000 × jumlah bulan bekerja) konsisten dengan praktik untuk pegawai yang masuk di tengah tahun?
- Pada contoh C4, 5% bruto berada di antara batas lama dan batas baru. Apakah dampaknya benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U03 — Kategori D TER untuk TK/0 (T2; S5, S6)
- Apakah pembentukan kategori keempat lewat perubahan PP 58/2023 dan Lampiran huruf E masuk akal?
- Periksa tabel kategori D: batas di bawah Rp100 juta digeser turun Rp400.000, dan batas Rp100 juta ke atas sama dengan A. Apakah tabelnya menaik dan tidak tumpang tindih?
- Contoh C7: karyawati kawin yang PTKP-nya hanya diri sendiri dimasukkan ke kategori D. Apakah tafsir ini sesuai dengan teks Pasal 2 ayat (4) huruf d?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U04 — Iuran Tapera (T3)
- Menurut aturan 2026, contoh memperlakukan iuran Tapera bagian pemberi kerja sebagai penghasilan (PMK 168/2023 Pasal 5 ayat (2)). Apakah anggapan ini dapat diterima sebagai titik awal?
- Apakah batas pengurang Rp200.000 per bulan iuran wajar?
- Contoh C6: pegawai masuk Oktober, sehingga batasnya Rp200.000 × 3. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U05 — Penggantian internet kerja jarak jauh (T3; S2, S5)
- Apakah bentuk pengecualian, yaitu penggantian berdasarkan bukti dengan batas Rp400.000 dan syarat paling sedikit 8 hari, masuk akal sebagai sisipan Pasal 7 dan Pasal 7A PMK 168/2023?
- Contoh C6: hari kerja jarak jauh berbeda tiap bulan. Periksa bulan-bulan yang lolos syarat dan yang tidak.
- Apakah kelebihan di atas Rp400.000 memang tepat diperlakukan sebagai penghasilan teratur?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U06 — DTP pegawai baru usia muda (T4; S2, S3)
- Apakah kombinasi kriterianya masuk akal untuk insentif nyata? Kriterianya: mulai bekerja pada 2027, usia ≤ 30, NIK terintegrasi, gaji dan tunjangan tetap ≤ Rp9 juta di bulan pertama, tidak menerima DTP lain, dan jumlah pegawai tetap perusahaan bertambah (diuji per bulan).
- Pasal 6 ayat (4): lebih potong dikembalikan hanya sebatas PPh yang benar-benar dipotong. Periksa C1 dan C6 (sisa kelebihan DTP tidak dikembalikan) serta C5 (lebih potong dikembalikan dari PPh Januari, Februari, Juli, dan Agustus).
- Apakah perhitungan usia pada tanggal mulai bekerja sudah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U07 — Perpanjangan DTP PMK 105/2025 sampai Juni 2027 (T6; S1, S2, S3, S5, S6)
- Apakah perpanjangan lewat perubahan PMK 105/2025 yang berlaku surut ke Masa Pajak Januari masuk akal? Apakah mekanisme pengembalian PPh Januari sudah memadai?
- Pasal 5 ayat (5a) baru mengatur Masa Pajak Terakhir 2027. Periksa C1 (kurang bayar Desember) dan C5 (lebih potong yang dikembalikan sebatas potongan Juli–November).
- C6: pegawai masuk Maret 2027, sehingga kriteria diuji pada bulan pertama bekerja. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U08 — PTKP tanggungan karyawati kawin (T5; S5)
- Apakah perluasan cakupan ini (surat pernyataan, PTKP diri ditambah tanggungan tanpa PTKP kawin) masuk akal?
- Apakah aturan kategori TER mengikuti TK/x (ayat (2b)) tepat? Periksa C1 (K/2 menjadi TK/2, kategori B) dan C4 (K/3 menjadi TK/3, kategori B).
- Apakah perlakuan dasar 2026 dalam contoh benar, yaitu karyawati kawin tanpa keterangan kecamatan memakai PTKP TK/0 dan kategori A?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U09 — Metode penghasilan tidak teratur, dua dokumen (T7; S4, S5)
- Apakah pembagian kewenangan masuk akal, yaitu prinsip di PP dan rumus di PMK?
- Periksa rumus selisih di Pasal 3 PMK 118/2026: biaya jabatan dihitung terpisah untuk tiap PKP, iuran pensiun bulan berjalan dikali 12, dan zakat tidak dihitung.
- C4: PPh setahun harus sama dengan aturan 2026, dan hanya pembagian antarbulan yang berubah. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U10 — Penghapusan zakat sebagai pengurang (T8; S5)
- Apakah pencabutan tanpa pengganti ini masuk akal, dengan zakat dikembalikan ke SPT Tahunan?
- C4: Januari–Maret tanpa Masa Pajak Terakhir, sehingga tidak berpengaruh. C5: pegawai berhenti Juni, sehingga berpengaruh. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U11 — Pembulatan dasar TER ke ribuan (T9; S5)
- Apakah pengaturan pembulatan seperti ini masuk akal untuk PMK, misalnya demi keseragaman dengan Coretax?
- C1 dan C5: pembulatan memindahkan bruto ke lapisan yang lebih rendah. Apakah memang dikehendaki bahwa lapisan dicari setelah pembulatan (Pasal 15A ayat (1))?
- Konvensi contoh untuk aturan 2026 sudah membulatkan hasil TER ke bawah ke rupiah penuh. Apakah konvensi ini dapat diterima?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U12 — Bulan pertama tidak penuh, tarif dari bruto setara (T9; S2, S5)
- Apakah rumus bruto setara (hari kalender, termasuk tanggal mulai, dibulatkan ke bawah) masuk akal dan cukup jelas?
- C6: penghasilan tidak teratur ditambahkan tanpa disetarakan. Apakah benar?
- C5: Desember menghasilkan lebih potong besar, karena tarif bulanan pegawai yang masuk tengah tahun memang tinggi. Apakah ini wajar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U13 — PTKP proporsional di Masa Pajak Terakhir (T9; S2, S5)
- Apakah kebijakan ini masuk akal secara hukum, mengingat UU PPh Pasal 7 mengatur PTKP setahun? Atau perlu dasar yang lebih tinggi?
- Pasal II ayat (2): bagian bulan dihitung satu bulan penuh. Apakah konsisten dengan contoh?
- C6: PKP menjadi positif untuk pegawai yang hanya bekerja 2 bulan. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U14 — Gross-up golongan I–III (T10; S2)
- Apakah prosedur iterasi (mulai dari T = 0, ulang sampai tetap; di Desember minimal nol) cukup jelas untuk diterapkan oleh tim *payroll*?
- C6: tunjangan mendorong bruto ke lapisan TER berikutnya. Periksa iterasinya.
- C4: lebih potong Desember menjadi hak perusahaan (Pasal 4 ayat (4)). Apakah perlakuan ini wajar dan sesuai praktik?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U15 — PKB, kenaikan gaji berlaku surut dengan rapel (T10; S1, S2)
- Apakah klausul PKB ini lazim? Klausulnya: kenaikan 8% dibulatkan ke atas ke ribuan, rapel dibayar April, ada rapel premi BPJS, dan pegawai yang berhenti sebelum penandatanganan tidak berhak.
- Periksa rapel iuran JKN dan JP terhadap batas upah: C6 di atas batas JKN Rp12 juta, dan C1 menyentuh batas JP Rp11.086.300.
- Apakah perlakuan pajak rapel sebagai penghasilan Masa Pajak April, tanpa menghitung ulang Januari–Maret, sudah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

### U16 — Perluasan lapisan 0% TER A/B/C (T2; S5, S6)
- Apakah batas baru (A Rp6.000.000; B Rp6.850.000; C Rp7.350.000) dan penghapusan lapisan 0,25% dan 0,5% masuk akal?
- Periksa tabel lengkap di lampiran: batas di atas lapisan baru harus sama persis dengan PP 58/2023.
- C3 (K/1, Rp7 juta) tidak berubah karena berada di atas lapisan yang diubah. Apakah benar?

- [ ] Disetujui  - [ ] Perlu revisi
Catatan:

## 6. Penutup pemeriksaan

Nama pemeriksa:
Tanggal:
Ringkasan temuan:

Revisi atas contoh atau teks dilakukan peneliti lewat `_alat/`. Setelah revisi, segel dibuat ulang dan hash baru dicatat.
