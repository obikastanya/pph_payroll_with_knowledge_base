# Tafsir korpus peristiwa

Ditetapkan 2026-10-27 dari tinjauan korpus peristiwa (`dataset/09_korpus_peristiwa/peristiwa.csv`). Dokumen ini memuat dua jenis putusan yang dipakai untuk menyusun jawaban acuan (Δ\* dan nilai per masa): **(A)** keputusan relevansi, klasifikasi, dan tanggal untuk baris yang ditandai perlu keputusan atau keliru, dan **(B)** semantik berlaku surut, yaitu nilai yang seharusnya untuk masa sebelum tanggal terbit dan mekanisme hukum penyelesaiannya. Halaman PDF merujuk berkas di `dataset/01_regulasi/`. Putusan yang menyangkut cara menghitung (bukan korpus) ada di [tafsir_perhitungan.md](tafsir_perhitungan.md); kode K di bawah merujuk dokumen itu.

## Ringkasan

| Kode | Pertanyaan | Putusan |
|---|---|---|
| A1 | P01 PP 49/2023 (rekomposisi JKK/JKM) | pengecoh X3; total iuran pemberi kerja tetap |
| A2 | P06 PP 6/2025 (JKP 0,36%) | pengecoh X3; tidak ada iuran tambahan |
| A3 | P15 PMK 114/2025 (zakat) | pengecoh X5; Δ aturan hitung kosong, rujukan dasar hukum boleh diperbarui |
| A4 | P20 PER-4/PJ/2026 (daftar penerima zakat) | pengecoh X5; Δ kosong |
| A5 | E03 dan E04 satu atau dua peristiwa | dua peristiwa, dihubungkan sifat S4 |
| A6 | D08, D12, D13 (rangkaian DTP COVID) | ketiganya tidak mengubah perhitungan PPh 21 |
| A7 | Tanggal diundangkan E10 PMK 72/2025 | 28 Oktober 2025 |
| A8 | Sifat surut E02 dan E07 | E02 tidak surut; E07 surut |
| A9 | Kelengkapan korpus 2023–2026 | tidak ada peristiwa relevan yang hilang |
| B0 | Konvensi umum masa sebelum terbit | nilai seharusnya per masa + mekanisme penyelesaian terpisah |
| B1 | E06 PMK 10/2025, Masa Januari 2025 | seluruh PPh 21 Januari DTP; dibayar tunai pada pembayaran gaji pertama sesudah 4 Feb; dilaporkan di SPT Masa Januari s.d. 31 Jan 2026 |
| B2 | E07/E09 keringanan JKK sebelum terbit | bruto memakai tarif keringanan; kelebihan iuran diperhitungkan ke iuran berikutnya; selisih PPh 21 diserap Masa Pajak Terakhir |
| B3 | E10 PMK 72/2025, Masa Oktober 2025 | PPh 21 Oktober DTP; mekanisme seperti B1; Desember diatur Ps. 5 ayat (5a), (6a), (6b) |
| B4 | E02 PMK 66/2023, natura Jan–Jun 2023 | tidak dipotong sama sekali; pegawai menghitung sendiri di SPT Tahunan |
| B5 | E13 PER-11/PJ/2025, pembulatan Masa Januari–April 2025 | nilai seharusnya = pembulatan ke rupiah terdekat; selisih paling banyak Rp1 per masa terserap di Masa Pajak Terakhir |
| B6 | DTP Masa Pajak Terakhir yang lebih potong (E06, E10, E11) | `pph21_dtp` masa terakhir = PPh masa terakhir (negatif) ditambah bagian yang dikembalikan; penyajian contoh 3 PMK 10/2025, berlaku juga bagi pegawai pariwisata |

---

## Bagian A. Relevansi, klasifikasi, dan tanggal

### A1. P01 PP 49/2023

**Pertanyaan.** PP 49/2023 mengubah tarif JKK dan JKM di PP 44/2015 (misalnya JKK risiko sangat rendah menjadi 0,10%). Apakah ini mengubah bruto PPh 21?

**Putusan.** Tidak. P01 tetap pengecoh, jenis X3. Δ yang benar: kosong.

**Dasar.**
- PP 49/2023 Pasal 16A ayat (1), PDF hlm. 5: iuran JKK "direkomposisi untuk Iuran jaminan kehilangan pekerjaan sebesar 0,14%"; Pasal 18A ayat (1), PDF hlm. 6: iuran JKM direkomposisi 0,10%. Angka 0,10% dan 0,20% adalah sisa setelah rekomposisi, bukan tarif yang dibayar.
- Rekomposisi itu sudah berlaku sejak PP 37/2021 Pasal 11 ayat (5), PDF hlm. 8–9: sumber pendanaan JKP "merupakan rekomposisi dari iuran program JKK dan JKM". PP 49/2023 hanya memindahkannya ke PP 44/2015.
- PMK 168/2023 Pasal 5 ayat (3) huruf d, PDF hlm. 9: yang masuk penghasilan adalah iuran JKK dan JKM "yang dibayarkan oleh pemberi kerja". Pembayaran pemberi kerja tetap 0,24–1,74% + 0,30% (lihat K8).

**Dampak.** Kandidat Δ yang menurunkan premi JKK/JKM di bruto karena P01 dilabeli L9 (dan L1).

### A2. P06 PP 6/2025

**Pertanyaan.** PP 6/2025 menurunkan iuran JKP menjadi 0,36%. Apakah bruto berubah?

**Putusan.** Tidak. Pengecoh X3, Δ kosong.

**Dasar.** PP 6/2025 Pasal I angka 2 (Pasal 11 ayat (2)–(5) baru), PDF hlm. 3: iuran JKP 0,36% "bersumber dari iuran yang dibayarkan oleh Pemerintah Pusat [0,22%] dan sumber pendanaan JKP", dan sumber pendanaan itu "merupakan rekomposisi dari iuran program JKK" 0,14%. JKM tidak lagi direkomposisi, tetapi tarif JKM yang dibayar pemberi kerja tetap 0,30%. Tidak ada pungutan baru dari pemberi kerja atau pekerja.

**Dampak.** Seperti A1.

### A3. P15 PMK 114/2025

**Pertanyaan.** PMK 114/2025 mencabut PMK 254/PMK.03/2010 dan mengatur ulang zakat sebagai pengurang. Pengecoh atau perubahan dasar hukum?

**Putusan.** Pengecoh, jenis X5. Δ atas aturan hitung PPh 21 kosong. Sistem boleh menambah rujukan dasar hukum (provenance) aturan zakat ke PMK 114/2025 Pasal 12 ayat (3) tanpa mengubah rumus; tindakan itu tidak dihitung sebagai L9. Mengubah rumus, menambah syarat ke perhitungan, atau mencabut aturan zakat dihitung sebagai L9.

**Dasar.**
- PMK 114/2025 Pasal 12 ayat (3) huruf a, PDF hlm. 9: zakat yang dibayar pegawai tetap "melalui pemberi kerja ... dapat dikurangkan dari penghasilan bruto dalam menghitung Pajak Penghasilan sebagaimana dimaksud dalam Pasal 21". Isi ini sama dengan PMK 168/2023 Pasal 10 ayat (1) huruf c, PDF hlm. 12.
- PMK 168/2023 tidak merujuk PMK 254/2010 sama sekali (dicek di seluruh teks), sehingga pencabutan PMK 254/2010 (PMK 114/2025 Pasal 24 huruf b, PDF hlm. 16) tidak memutus dasar pengurang zakat di PPh 21.
- Syarat baru di Pasal 9 ayat (1)–(2), PDF hlm. 7 (penerima ber-NPWP; jumlah "tidak melebihi besaran kewajiban sesuai dengan ketentuan agama") menyangkut kelayakan nilai zakat yang dilaporkan pegawai, yang di sistem adalah input, bukan rumus.
- Berlaku sejak diundangkan (Pasal 25, PDF hlm. 16), yaitu 31 Desember 2025 (JDIH Kemenkeu; BN 2025 No. 1207, dikonfirmasi rujukan di konsiderans PER-4/PJ/2026).

**Dampak.** `relevan = tidak`, `jenis_perubahan = X5`, `berlaku_mulai = 2025-12-31`.

### A4. P20 PER-4/PJ/2026

**Pertanyaan.** PER-4/PJ/2026 menetapkan daftar baru badan penerima zakat. Apakah ini perubahan aturan hitung?

**Putusan.** Pengecoh X5, Δ kosong.

**Dasar.** PER-4/PJ/2026 Pasal 1 ayat (3), PDF hlm. 3: badan atau lembaga penerima "tercantum dalam Lampiran"; Pasal 2: mencabut PER-04/PJ/2022 (terakhir diubah PER-22/PJ/2025) dan PER-6/PJ/2011; Pasal 3: berlaku pada tanggal ditetapkan, 30 Maret 2026. Daftar ini menentukan apakah zakat yang dibayar ke lembaga tertentu sah sebagai input; rumus PPh 21 tidak berubah. Daftar serupa sudah diubah lima kali sejak 2022 tanpa pernah dianggap perubahan aturan hitung.

**Dampak.** Seperti A3.

### A5. E03 dan E04: satu atau dua peristiwa

**Pertanyaan.** PP 58/2023 (27 Des 2023) dan PMK 168/2023 (29 Des 2023) bersama-sama mengganti metode disetahunkan dengan TER. Dievaluasi sebagai satu peristiwa gabungan atau dua?

**Putusan.** Dua peristiwa, dihubungkan dengan sifat S4. Masing-masing punya Δ\* sendiri dan dinilai pada tanggal pengetahuannya sendiri. Antara 27 dan 29 Desember 2023 keadaan acuan adalah "E03 sudah, E04 belum".

**Dasar.**
- PP 58/2023 tidak kehilangan makna tanpa PMK 168/2023. Pasal 2 ayat (1)–(6), PDF hlm. 3–5, menetapkan tarif Pasal 17 dan TER beserta kategori A/B/C dan tabelnya; Penjelasan Pasal 2 ayat (1), PDF hlm. 8–9, sudah memuat skema lengkap: "untuk masa pajak Januari 2024 sampai November 2024 dilakukan dengan menggunakan tarif efektif" dan "Pada bulan Desember 2024 ... dilakukan dengan menggunakan tarif Pasal 17". Berlaku 1 Januari 2024 (Pasal 5, PDF hlm. 5).
- PMK 168/2023 menambah hal yang tidak ada di PP: definisi Masa Pajak Terakhir termasuk bulan berhenti bekerja (Pasal 1 angka 18, PDF hlm. 4), rincian bruto (Pasal 5 ayat (3), PDF hlm. 9), zakat sebagai pengurang (Pasal 10 ayat (1) huruf c, PDF hlm. 12), dan pencabutan PMK 250/2008, 252/2008, 102/2016 (Pasal 24, PDF hlm. 22–23).
- Keduanya berlaku 1 Januari 2024, sehingga tidak ada masa pajak yang dihitung dengan hanya salah satunya. Pemisahan hanya berpengaruh pada tanggal pengetahuan, dan justru itu yang diuji: apakah sistem yang hanya membaca E03 sudah menyiapkan TER untuk Januari 2024 (PP lebih tinggi dari PMK 252/2008), dan apakah E04 menghasilkan pencabutan metode lama serta aturan zakat.

**Dampak.** Δ\*(E03): tabel TER berversi, aturan pemilihan kategori, aturan masa Jan–Nov = TER × bruto, aturan Masa Pajak Terakhir = Pasal 17; semua `valid_from = 2024-01-01`. Δ\*(E04): pencabutan aturan disetahunkan sejak 2024-01-01, definisi Masa Pajak Terakhir untuk pegawai berhenti, zakat sebagai pengurang, rincian bruto. Bila E04 mengulang isi E03, unsur yang sama tidak dihitung dua kali.

### A6. D08, D12, D13

**Pertanyaan.** Tiga dokumen pengembangan dalam rangkaian DTP COVID semula dianggap relevan atau perlu keputusan.

**Putusan.** Ketiganya `relevan = tidak` untuk PPh 21 pegawai tetap.
- D08 PMK 110/2020: jenis X4. Mengubah PMK 86/2020 untuk PPh 25, PPh final jasa konstruksi P3-TGAI, dan Lampiran C, N, R (Pasal I angka 1–7, PDF hlm. 3–12). Daftar KLU DTP PPh 21 (Lampiran A) dinyatakan ulang tanpa perubahan.
- D12 PMK 149/2021: jenis X4. Pasal 19B ayat (1), PDF hlm. 5, tentang pemanfaatan DTP PPh 21 sejak Masa Juli 2021 identik kata demi kata dengan PMK 82/2021 Pasal 19B ayat (1), PDF hlm. 8. Daftar KLU PPh 21 di Lampiran A sama (1.189 kode). Yang berubah: PPh 22 impor, PPh 25, PPN, dan batas pembetulan laporan realisasi (30 November 2021).
- D13 PMK 3/2022: Pasal 16, PDF hlm. 16, memang mencabut PMK 9/2021 beserta perubahannya, tetapi DTP PPh 21 sudah berakhir pada Masa Desember 2021 karena masa berlakunya habis (PMK 82/2021), dan PMK 3/2022 tidak memberi DTP PPh 21 untuk 2022. Jenis T8 tanpa efek hitung.

**Dampak.** Contoh nyata T5 di data pengembangan tinggal D06 (dan D07); daftar contoh di [taksonomi.md](taksonomi.md) bagian 1.1 yang masih menyebut D08 untuk T5 perlu disesuaikan.

### A7. Tanggal diundangkan E10

**Pertanyaan.** JDIH BPK mencatat PMK 72/2025 diundangkan 20 Oktober 2025; JDIH Kemenkeu mencatat 28 Oktober 2025. PDF tidak menampilkan tanggal diundangkan (tanda tangan elektronik).

**Putusan.** 28 Oktober 2025. `tanggal_terbit` E10 = 2025-10-28.

**Dasar.** JDIH Kemenkeu adalah JDIH penerbit. Nomor Berita Negara mendukungnya: BN 2025 No. 833 diundangkan 15 Oktober 2025 (PMK 71/2025), No. 880 adalah PMK 72/2025, No. 904 diundangkan 3 November 2025 (PMK 70/2025). Interpolasi menempatkan No. 880 sekitar 28 Oktober.

**Dampak.** Masa Oktober 2025 tetap surut (dimulai 1 Oktober); jeda antara awal masa dan terbit menjadi 27 hari.

### A8. Sifat surut E02 dan E07

**Putusan.** E02 `berlaku_surut = tidak`: PMK 66/2023 diundangkan 27 Juni 2023 dan kewajiban pemotongannya mulai 1 Juli 2023 (Pasal 27, PDF hlm. 19). Masa Januari–Juni 2023 diatur, tetapi justru dikecualikan dari pemotongan (B4), jadi tidak ada nilai PPh 21 yang berubah surut. E07 `berlaku_surut = ya` menurut definisi kolom: keringanan berlaku untuk iuran bulan Februari 2025 (Pasal 10, PDF hlm. 6), sedangkan PP terbit 7 Februari 2025. Penyelesaiannya di B2.

### A9. Kelengkapan

**Putusan.** Tidak ada peristiwa 2023–2026 yang mengubah PPh 21 pegawai tetap atau iuran BPJS yang masuk PPh 21 dan belum ada di korpus.

**Yang dicek.** PTKP tetap PMK 101/PMK.010/2016 (belum ada PMK pengganti; masuk daftar pantauan). Iuran dan batas upah JKN tetap Perpres 64/2020 jo. 59/2024 (Rp12 jt; 5%); kenaikan iuran 2026 masih wacana. Tarif JHT, JP, JKM, dan JKK normal tidak berubah; satu-satunya perubahan iuran adalah keringanan JKK E07/E09 dan JKP P06. Perpanjangan keringanan JKK sesudah iuran Januari 2026 tidak ditemukan. Perubahan atas PMK 105/2025, PMK 168/2023, atau PP 58/2023 tidak ditemukan. Peraturan BPJS Kesehatan 2/2024, Perpres 59/2024, PP 50/2025, PMK 6/2026, dan dokumen Coretax sudah ada sebagai pengecoh.

---

## Bagian B. Semantik berlaku surut

### B0. Konvensi umum

Untuk peristiwa dengan `berlaku_mulai` < `tanggal_terbit`, setiap masa m sebelum terbit punya dua nilai acuan:

1. **Nilai seperti diketahui saat itu**: dihitung dengan aturan yang sudah terbit pada tanggal penggajian masa m. Inilah yang benar untuk pertanyaan "apa yang seharusnya dihitung sistem pada tanggal itu" (replay dengan ω = tanggal penggajian).
2. **Nilai seharusnya**: dihitung dengan aturan baru untuk masa m, sebagaimana ditetapkan setelah terbit. Ini jawaban acuan untuk pertanyaan dengan ω ≥ `tanggal_terbit`.

Selisih keduanya tidak boleh ditulis ulang ke masa m. Selisih itu diselesaikan dengan **mekanisme hukum** yang ditetapkan per peristiwa (B1–B4), dan mekanisme itu juga bagian dari jawaban acuan: kapan, di masa mana, dan dalam bentuk apa selisih dibayar, dikembalikan, atau diperhitungkan. Kandidat Δ yang benar menyimpan `valid_from` = awal masa yang dicakup dan `recorded_on` = `tanggal_terbit` (G4).

### B1. E06 PMK 10/2025, Masa Pajak Januari 2025

**Pertanyaan.** PMK terbit 4 Februari 2025 tetapi memberi DTP untuk Masa Januari 2025. Gaji Januari umumnya sudah dibayar dan PPh 21-nya dipotong. Berapa nilai seharusnya dan bagaimana diselesaikan?

**Putusan.**
1. Nilai seharusnya Masa Januari 2025 untuk pegawai tetap yang memenuhi syarat: PPh 21 terutang = TER × bruto (tidak berubah); **PPh 21 DTP = seluruh PPh 21 terutang**; PPh 21 yang ditanggung pegawai = 0; bruto tidak bertambah karena pembayaran DTP. Kelayakan diuji pada bruto tetap teratur Januari 2025.
2. Mekanisme: PPh 21 Januari yang sudah dipotong dibayarkan kembali secara tunai kepada pegawai sebagai DTP. Konvensi acuan: dibayar pada pembayaran penghasilan pertama sesudah 4 Februari 2025 (penggajian Februari), dicatat sebagai DTP Masa Januari, tidak dikenai pajak. Pemberi kerja tidak menyetor bagian itu dan melaporkannya sebagai DTP di SPT Masa PPh 21 Januari 2025 (jatuh tempo lapor 20 Februari 2025) atau lewat pembetulan, paling lambat 31 Januari 2026.
3. Bila pemberi kerja sudah menyetor PPh 21 Januari sebelum 4 Februari (batas setor 15 Februari), lebih bayar yang timbul berasal dari DTP dan tidak dapat dikembalikan atau dikompensasikan; jawaban acuan tetap memperlakukan pegawai sebagai penerima DTP penuh.

**Dasar.**
- Pasal 2 ayat (3), PDF hlm. 4: insentif "diberikan untuk Masa Pajak Januari 2025 sampai dengan Masa Pajak Desember 2025"; Pasal 9, PDF hlm. 7: PMK "mulai berlaku pada tanggal diundangkan".
- Pasal 4 ayat (2) huruf b angka 1, PDF hlm. 5: kriteria bruto tetap teratur ≤ Rp10 jt "pada Masa Pajak Januari 2025".
- Pasal 5 ayat (1)–(2), PDF hlm. 6: DTP "harus dibayarkan secara tunai oleh Pemberi Kerja pada saat pembayaran penghasilan" dan "tidak diperhitungkan sebagai penghasilan yang dikenakan pajak". PMK tidak punya pasal peralihan khusus Januari, sehingga pembayaran pada saat pembayaran penghasilan berikutnya adalah tafsir paling dekat dengan teks.
- Pasal 5 ayat (6), PDF hlm. 6: lebih bayar yang berasal dari DTP "tidak dapat dikembalikan dan tidak dapat dikompensasikan".
- Pasal 6 ayat (2)–(4), PDF hlm. 6–7: pelaporan lewat SPT Masa Januari–Desember 2025 dan pembetulannya diakui "sepanjang disampaikan paling lambat pada tanggal 31 Januari 2026"; ayat (5)–(6): bila terlambat, seluruh insentif setahun gugur dan PPh yang dipotong wajib disetor.
- PMK 81/2024 Pasal 94 ayat (2) huruf c, PDF hlm. 78: PPh 21 disetor paling lambat tanggal 15 bulan berikutnya.

**Dampak.** GT dengan ω < 2025-02-04 untuk Masa Januari: tanpa DTP. GT dengan ω ≥ 2025-02-04: Januari DTP penuh, ditambah satu entri penyelesaian di Februari (pembayaran tunai DTP Januari, nonobjek). PPh setahun di Desember tidak berubah karena DTP tidak mengubah PPh terutang.

### B2. E07 dan E09 keringanan JKK sebelum tanggal terbit

**Pertanyaan.** PP 7/2025 (terbit 7 Februari 2025) berlaku untuk iuran Februari 2025; PP 36/2025 (terbit 4 September 2025) menyambung keringanan mulai iuran Agustus 2025, sesudah keringanan PP 7/2025 berakhir pada iuran Juli. Penggajian Agustus 2025 mungkin sudah menghitung premi JKK tarif penuh. Berapa premi yang masuk bruto dan bagaimana selisihnya diselesaikan?

**Putusan.**
1. Nilai seharusnya: premi JKK di bruto bulan Februari–Juli 2025 dan Agustus 2025–Januari 2026 adalah **tarif keringanan** untuk perusahaan yang memenuhi syarat (K7). Bruto ditetapkan per bulan iuran (akrual), bukan per arus kas: kelebihan iuran yang dikompensasikan ke bulan berikutnya bukan premi bulan itu dan tidak mengurangi premi bulan kompensasi.
2. Mekanisme iuran: kelebihan bayar iuran diperhitungkan ke iuran JKK bulan berikutnya. Iuran bulan Februari 2025 dan Agustus 2025 jatuh tempo tanggal 15 bulan berikutnya, setelah kedua PP terbit, sehingga umumnya iuran itu bisa langsung dibayar dengan tarif keringanan.
3. Mekanisme PPh 21: kedua PP tidak mengatur PPh. Selisih PPh 21 masa Februari 2025 atau Agustus 2025 yang dihitung dengan premi penuh tidak wajib dibetulkan per masa; selisihnya terserap di Masa Pajak Terakhir, karena PPh setahun dihitung ulang dengan tarif Pasal 17 atas bruto setahun yang memakai premi keringanan. Pembetulan SPT Masa tetap boleh (hak pemotong), tetapi bukan bagian jawaban acuan.

**Dasar.**
- PP 7/2025 Pasal 10, PDF hlm. 6: keringanan "berlaku untuk Iuran JKK bulan Februari 2025 sampai dengan Iuran JKK bulan Juli 2025"; Pasal 6 ayat (1) dan (3), PDF hlm. 5: iuran dibayar "paling lambat tanggal 15 bulan berikutnya" dan kelebihan pembayaran "diperhitungkan untuk Iuran JKK bulan berikutnya".
- PP 36/2025 Pasal I angka 2 (Pasal 10A), PDF hlm. 4: "dilakukan perpanjangan sampai dengan Iuran JKK bulan Januari 2026"; Pasal II angka 1, PDF hlm. 4: kelebihan iuran "bulan Agustus 2025 dan/atau Iuran bulan berikutnya ... diperhitungkan untuk Iuran JKK bulan berikutnya".
- PMK 168/2023 Pasal 5 ayat (3) huruf d, PDF hlm. 9 (iuran JKK "yang dibayarkan oleh pemberi kerja" masuk penghasilan); Pasal 15 ayat (1), PDF hlm. 15 (Masa Pajak Terakhir = PPh setahun tarif Pasal 17 dikurangi yang telah dipotong).

**Dampak.** GT dengan ω < 2025-09-04: premi Agustus 2025 tarif penuh (PP 7/2025 sudah berakhir). GT dengan ω ≥ 2025-09-04: premi Agustus tarif keringanan; PPh Masa Agustus "seharusnya" dihitung ulang dengan bruto itu, dan Desember 2025 memakai bruto setahun akrual. Untuk E07, jeda hanya 6 hari dan penggajian Februari umumnya sesudah 7 Februari; nilai seperti diketahui saat itu dan nilai seharusnya biasanya sama.

### B3. E10 PMK 72/2025, Masa Pajak Oktober 2025

**Pertanyaan.** PMK 72/2025 (ditetapkan 20 Oktober, diundangkan 28 Oktober 2025) memasukkan sektor pariwisata untuk Masa Oktober–Desember 2025. Bagaimana Masa Oktober dan Masa Pajak Terakhir diselesaikan?

**Putusan.**
1. Nilai seharusnya Masa Januari–September 2025 untuk pegawai pariwisata: **tidak ada DTP** (tidak surut sampai Januari). Kelayakan tetap diuji pada bruto tetap teratur Januari 2025 atau bulan pertama bekerja.
2. Nilai seharusnya Masa Oktober 2025: PPh 21 = TER × bruto, seluruhnya DTP. Mekanismenya sama dengan B1: bila gaji Oktober dibayar sebelum 28 Oktober dengan PPh dipotong, potongan itu dibayarkan tunai sebagai DTP Masa Oktober pada pembayaran penghasilan berikutnya (penggajian November), dilaporkan di SPT Masa Oktober (jatuh tempo 20 November 2025) atau pembetulannya paling lambat 31 Januari 2026.
3. Masa Pajak Terakhir 2025: PPh setahun (Pasal 17) atas seluruh bruto Januari–Desember. Bila hasilnya kurang bayar, kekurangan Desember adalah DTP. Bila lebih bayar, bagian yang dikembalikan kepada pegawai = lebih bayar − DTP Oktober dan November (minimal nol); sisanya tidak dikembalikan. Bagian yang dikembalikan dapat dikompensasikan pemberi kerja ke masa berikutnya dengan kertas kerja dan bukti potong tambahan.

**Dasar.**
- Pasal I angka 4 (Pasal 4A huruf b), PDF hlm. 4: DTP untuk "Masa Pajak Oktober 2025 sampai dengan Masa Pajak Desember 2025" bagi bidang pariwisata. Pasal 4 PMK 10/2025 tidak diubah, sehingga kriteria tetap diukur pada Masa Januari 2025 (dikonfirmasi FAQ DJP versi 04.11.2025, no. 1).
- Pasal I angka 5 (Pasal 5 ayat (5a)), PDF hlm. 4–5: kelebihan "dapat dikembalikan oleh Pemberi Kerja kepada Pegawai Tetap bersangkutan hanya sebesar bagian kelebihan pemotongan pajak yang tidak ditanggung pemerintah"; ayat (6a)–(6b), PDF hlm. 5: bagian itu "dapat dikompensasikan ke masa pajak berikutnya" dengan kertas kerja dan bukti pemotongan tambahan.
- Lampiran B contoh 7 (Tuan G), PDF hlm. 46–47: lebih potong Rp80.000 < DTP Okt–Nov Rp240.000, "tidak dikembalikan"; contoh 8 (Tuan H), PDF hlm. 48–49: lebih potong Rp1.425.000 − DTP Rp225.000 = Rp1.200.000 dikembalikan "paling lambat akhir bulan Januari 2026".
- Pasal II, PDF hlm. 6: berlaku pada tanggal diundangkan; tanggal 28 Oktober 2025 menurut A7. PMK 10/2025 Pasal 5 ayat (1) dan Pasal 6 ayat (3)–(4) tetap berlaku untuk pembayaran dan pelaporan.

**Dampak.** GT dengan ω < 2025-10-28: pegawai pariwisata tanpa DTP untuk Oktober. GT dengan ω ≥ 2025-10-28: Oktober DTP penuh, ditambah entri penyelesaian di November; Desember mengikuti Pasal 5 ayat (5a). Pasal 5 ayat (5a), (6a), (6b) bukan mekanisme penyelesaian Masa Oktober; catatan lama E10 yang menyiratkan itu sudah dikoreksi.

### B4. E02 PMK 66/2023, natura Januari–Juni 2023

**Pertanyaan.** Natura menjadi objek PPh sejak 2023 (PP 55/2022), tetapi PMK pelaksananya baru terbit 27 Juni 2023. Apakah natura Januari–Juni 2023 harus dipotong surut, misalnya di perhitungan Desember 2023?

**Putusan.**
1. Nilai seharusnya PPh 21 Masa Januari–Juni 2023: natura **tidak dimasukkan** ke bruto pemotongan, baik di masa itu maupun di perhitungan Masa Pajak Terakhir Desember 2023. Tidak ada pemotongan surut.
2. Mekanisme: pegawai menghitung, membayar, dan melaporkan sendiri PPh atas natura Januari–Juni 2023 di SPT Tahunan 2023. Di luar lingkup pemotongan yang dihitung sistem.
3. Natura sejak Masa Juli 2023 masuk bruto pemotongan (metode lama 2023; klasifikasi teratur/tidak teratur menurut K12).

**Dasar.**
- PMK 66/2023 Pasal 23 ayat (4), PDF hlm. 18: natura yang diterima "pada Masa Pajak Januari 2023 sampai dengan Masa Pajak Juni 2023 dikecualikan dari pemotongan"; Pasal 24, PDF hlm. 18: atas natura 1 Januari–30 Juni 2023 yang belum dipotong, PPh "wajib dihitung dan dibayar sendiri serta dilaporkan oleh penerima dalam Surat Pemberitahuan"; Pasal 27, PDF hlm. 19: berlaku 1 Juli 2023.
- PP 55/2022 Pasal 73 ayat (2) huruf a, PDF hlm. 68: kewajiban pemotongan natura berlaku untuk penghasilan "sejak tanggal 1 Januari 2023"; PMK 66/2023 mengecualikan semester pertama dari pemotongan itu.

**Dampak.** Untuk E02 nilai seperti diketahui saat itu dan nilai seharusnya sama di semua masa pemotongan; peristiwa ini menguji klasifikasi (T3) dan pengecualian masa (L5), bukan penyelesaian surut. Kandidat Δ yang memasukkan natura Januari–Juni ke perhitungan Desember 2023 dilabeli L2 dan L5.

### B5. E13 PER-11/PJ/2025, pembulatan Masa Januari–April 2025

Ditambahkan di Tahap 3 bersama pemindahan P07 menjadi E13.

**Pertanyaan.** PER-11/PJ/2025 terbit 22 Mei 2025, tetapi Pasal 129–130 membuat pembulatan ke rupiah terdekat berlaku untuk bukti potong Masa Januari 2025 dan sesudahnya. Bukti potong Masa Januari–April 2025 mungkin sudah dibuat dengan membuang desimal. Berapa nilai seharusnya dan bagaimana selisihnya diselesaikan?

**Putusan.**
1. Nilai seharusnya PPh 21 Masa Januari–April 2025 (ω ≥ 2025-05-22): TER × bruto dibulatkan ke rupiah terdekat (0,50 ke atas), sama dengan masa sesudahnya (tafsir K1).
2. Nilai seperti diketahui saat itu (ω < 2025-05-22): desimal dibuang, melanjutkan konvensi PER-2/PJ/2024 dan K2.
3. Mekanisme: PER-11 tidak mengatur pembetulan bukti potong yang sudah dibuat. Selisih paling banyak Rp1 per masa tidak wajib dibetulkan; selisih itu terserap di Masa Pajak Terakhir, karena PPh setahun dihitung dengan tarif Pasal 17 atas PKP yang dibulatkan ke ribuan, lalu dikurangi PPh masa sebelumnya. Konvensi acuan (B0) memakai jumlah nilai seharusnya, sehingga entri penyelesaian tidak dinilai.

**Dasar.** PER-11/PJ/2025 Pasal 129 ayat (1) huruf a dan ayat (3), PDF hlm. 106; Pasal 130 huruf a, PDF hlm. 107; Pasal 147: berlaku pada tanggal ditetapkan; tafsir_perhitungan.md K1.

**Dampak.** GT dengan ω < 2025-05-22 untuk masa 2025: desimal dibuang. GT dengan ω ≥ 2025-05-22: rupiah terdekat. GT3 kasus 2025–2026 (dihitung dengan K1) sama dengan nilai ω ≥ 2025-05-22.

### B6. DTP Masa Pajak Terakhir yang lebih potong (E06, E10, E11)

Ditambahkan 2026-10-28 atas temuan pembaca kedua (review/gold/regulasi.tanggapan.md).

**Pertanyaan.** Contoh 3 PMK 10/2025 (Lampiran B, padat karya) menyajikan DTP Desember negatif (277.500) ketika Masa Pajak Terakhir lebih potong; contoh 7 PMK 72/2025 (pariwisata) menyajikan "-" di kolom DTP Desember dengan PPh Desember (80.000) dan total DTP 240.000. Berapa nilai `pph21_dtp` Desember?

**Putusan.** `pph21_dtp` masa terakhir = PPh masa terakhir bila positif; bila negatif, PPh masa terakhir ditambah bagian lebih potong yang dikembalikan kepada pegawai (Pasal 5 ayat (5) dan (5a)). Untuk padat karya hasilnya sama dengan contoh 3. Untuk pariwisata dalam contoh 7, lebih potong 80.000 tidak melebihi DTP Oktober–November 240.000, sehingga tidak ada yang dikembalikan dan `pph21_dtp` Desember = (80.000). Kedua contoh menggambarkan perlakuan yang sama (lebih potong yang berasal dari DTP tidak dikembalikan) dengan penyajian berbeda; satu konvensi dipakai untuk semua penerima DTP.

**Dasar.** PMK 10/2025 Pasal 5 ayat (5), Lampiran B contoh 3 (PDF hlm. 21); PMK 72/2025 Pasal 5 ayat (5a), Lampiran B contoh 7 (PDF hlm. 45–47).

**Dampak.** Tidak ada perubahan emas; GT1 pengembangan PMK72-B-7 tidak memuat DTP Desember sehingga tidak terpengaruh.
