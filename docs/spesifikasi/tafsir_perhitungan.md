# Tafsir perhitungan PPh 21 pegawai tetap

Ditetapkan 2026-10-27 dari tinjauan GT3 (`dataset/11_acuan/gt3_kasus_bertingkat/`). Dokumen ini memuat aturan tafsir yang dipakai sistem dan acuan GT3 pada titik yang regulasinya diam, ambigu, atau tersebar di beberapa dokumen. Kode K1–K13 sama dengan daftar ketidakpastian di README GT3; K14–K16 ditambahkan saat tinjauan.

**Urutan bukti.** (1) contoh resmi di lampiran regulasi (untuk `dataset/07_kasus_uji_resmi/` hanya berkas berlabel `pengembangan`); (2) teks batang tubuh regulasi; (3) perilaku kalkulator PPh 21 DJP (GT2, `dataset/11_acuan/gt2_kalkulator_djp/`). Bila dua contoh resmi bertentangan, yang dipilih adalah yang sejalan dengan peraturan induk dan dengan lebih banyak contoh lain. Halaman PDF merujuk berkas di `dataset/01_regulasi/`.

## Ringkasan

| Kode | Pertanyaan | Putusan | Kasus GT3 yang berubah |
|---|---|---|---|
| K1 | Pembulatan PPh TER bulanan | s.d. Masa Desember 2024: desimal dibuang (ke bawah). Mulai Masa Januari 2025: ke rupiah terdekat, 0,50 ke atas | 028, 030, 034, 036, 037, 038, 044, 047, 048, 049 |
| K2 | Pembulatan PPh sebulan metode lama 2023 | ke bawah | tidak ada |
| K3 | Cara menghitung *gross-up* | titik tetap terkecil dengan aturan pembulatan masa itu; Desember = kekurangan PPh Desember | 038, 044, 049 (lewat K1) |
| K4 | PPh ditanggung pemberi kerja | Jan–Jun 2023 tanpa *gross-up*; Jul 2023 dst. kenikmatan objek, *full gross-up* | tidak ada |
| K5 | Isi "penghasilan bruto tetap dan teratur" kriteria DTP | gaji + tunjangan tetap + imbalan/natura yang ditetapkan tetap dalam peraturan perusahaan/kontrak; tanpa premi BPJS pemberi kerja, lembur insidental, THR, bonus | tidak ada (asumsi 029 dipertegas) |
| K6 | Plafon biaya jabatan bagian tahun | agregat: min(5% × bruto, n × Rp500.000) | tidak ada |
| K7 | Iuran JKK Agustus 2025 industri padat karya | tarif keringanan | tidak ada |
| K8 | Porsi JKK yang direkomposisi ke JKP | seluruh tarif nominal JKK masuk bruto | tidak ada |
| K9 | Iuran JP pegawai 2023 | pengurang | tidak ada |
| K10 | Zakat lewat pemberi kerja 2023 | bukan pengurang pemotongan | tidak ada |
| K11 | Batas upah JP Januari–Februari 2023 | Rp9.077.600 | tidak ada |
| K12 | Natura dalam metode lama 2023 | rumah bulanan = teratur; bingkisan = tidak teratur; nilai = biaya/nilai pasar; batas bingkisan dihitung kumulatif setahun | tidak ada |
| K13 | DTP pegawai yang berhenti di tengah tahun | lebih potong yang berasal dari DTP tidak dikembalikan | tidak ada |
| K14 | Arti "bruto" masa pada metode lama | seluruh penghasilan masa itu, teratur + tidak teratur | tidak ada |
| K15 | Lembur pada metode lama | penghasilan teratur (disetahunkan) | tidak ada |
| K16 | PTKP karyawati kawin berstatus K/x | butuh keterangan kecamatan bahwa suami tidak berpenghasilan; tanpa itu PTKP diri sendiri | 048 (asumsi ditambahkan, angka tetap) |
| K17 | Pembulatan premi dan iuran BPJS | rupiah penuh terdekat (0,50 ke atas) per program per pihak | tidak ada (GT3 memakai upah yang menghasilkan premi bulat) |
| K18 | DTP pada metode *gross-up* dan ditanggung | *gross-up*: tunjangan pajak tetap dihitung dan DTP dibayar tunai di atasnya; ditanggung: PPh DTP bukan beban pemberi kerja (tanpa *gross-up*), DTP tunai masuk gaji bersih | tidak ada (GT3 tidak punya kasus DTP dengan *gross-up*) |

---

## K1. Pembulatan PPh 21 TER bulanan

**Pertanyaan.** Hasil tarif efektif × bruto sering berpecahan sen. PP 58/2023 dan PMK 168/2023 tidak mengatur pembulatannya. Dibulatkan ke bawah, ke terdekat, atau tidak dibulatkan?

**Putusan.**
1. Masa Pajak Januari–Desember 2024: pecahan di bawah satu rupiah **dibuang** (sama dengan dibulatkan ke bawah).
2. Masa Pajak Januari 2025 dan seterusnya: **dibulatkan ke rupiah penuh terdekat**; pecahan < 0,50 ke bawah, ≥ 0,50 ke atas.
3. Aturan yang sama berlaku untuk PPh DTP masa itu dan untuk persamaan *gross-up* (K3). PPh setahun di Masa Pajak Terakhir selalu bulat karena PKP dibulatkan ke ribuan.

**Dasar.**
- Tidak ada contoh resmi (set pengembangan) yang menghasilkan pecahan TER, jadi keputusan diambil dari teks.
- PER-2/PJ/2024 (bukti potong dan SPT Masa PPh 21 untuk masa 2024), Lampiran I huruf B, Petunjuk Umum angka 7, PDF Lampiran hlm. 5: "Dalam mengisi kolom-kolom yang berisi nilai rupiah, harus tanpa nilai desimal. Contoh: … seratus dua puluh lima rupiah lima puluh sen adalah: 125 (bukan 125,50)." Contoh 125,50 → 125 menunjukkan desimal dibuang, bukan dibulatkan ke terdekat.
- PER-11/PJ/2025 Pasal 129 ayat (1) huruf a, PDF hlm. 106: "Jumlah dasar pengenaan pajak dan Pajak Penghasilan yang tercantum dalam: a. Bukti Pemotongan Pajak Penghasilan Pasal 21/26; … diisi dengan pembulatan ke dalam rupiah penuh." Ayat (3): "a. kurang dari 0,50 …, maka bilangan tersebut dibulatkan ke bawah; atau b. sama dengan atau lebih dari 0,50 …, maka bilangan tersebut dibulatkan ke atas."
- PER-11/PJ/2025 Pasal 130 huruf a, PDF hlm. 107: bukti potong PPh 21/26 "atas Masa Pajak sampai dengan Masa Pajak Desember 2024" tetap mengikuti PER-2/PJ/2024. Jadi PER-11 berlaku mulai Masa Januari 2025.
- Bukti yang bertentangan: kalkulator PPh 21 DJP (GT2, diakses 2026-10-27) memotong desimal, termasuk tepat 0,50: GT2-09 (2% × 9.950.775 = 199.015,5 → 199.015) dan GT2-10 (1,5% × 9.411.300 = 141.169,5 → 141.169); *gross-up* GT2-06 dan GT2-07 juga hanya cocok dengan pemotongan desimal. Karena teks PER-11 lebih tinggi daripada perilaku kalkulator dalam urutan bukti, GT3 mengikuti PER-11. Selisihnya paling banyak Rp1 per masa.

**Dampak.** Kasus 2024 tidak berubah. Kasus 2025–2026 yang berubah (nilai lama → baru):
- GT3-028 Feb: 224.999 → 225.000. GT3-030 Jan: 263.500 → 263.501.
- GT3-034 Feb, Apr–Nov: 91.498 → 91.499 (DTP); Des −94.711 → −94.720.
- GT3-036 Jan 387.969 → 387.970; Mar 1.936.635 → 1.936.636; Des −122.559 → −122.561 (dikembalikan 122.561).
- GT3-037 Mei, Jul–Nov: 199.015 → 199.016; Des −631.313 → −631.319.
- GT3-038 tunjangan pajak = PPh: 522.699 → 522.700 (Jan–Feb, Apr–Nov), Mar 2.727.199 → 2.727.200, Des 128.411 → 128.400.
- GT3-044 tunjangan pajak = PPh: 1.171.257 → 1.171.258 (bruto 16.732.258).
- GT3-047 Jan 199.015 → 199.016; Jul–Nov 404.981 → 404.982; Des 689.842 → 689.836.
- GT3-048 Jan 141.169 → 141.170; Sep −1.082.565 → −1.082.566.
- GT3-049 PPh ditanggung: 1.615.408 → 1.615.409 (Jan–Feb, Apr–Nov), Mar 6.967.085 → 6.967.086, Des 488.235 → 488.224.

Bruto setahun, PKP, dan PPh setahun tidak berubah di kasus mana pun. Pembanding GT2 yang kini berbeda Rp1 dari GT3 atau dari *gross-up* acuan: GT2-06 (GT3-044), GT2-07, GT2-09 (GT3-047 Jan), GT2-10 (GT3-048 Jan); selisih ini dicatat sebagai perbedaan pembulatan kalkulator, bukan kesalahan aturan. Pergantian aturan pembulatan antara 2024 dan 2025 juga merupakan contoh nyata perubahan prosedur hitung (jenis T9 di `taksonomi.md`).

## K2. Pembulatan PPh sebulan metode lama (2023)

**Pertanyaan.** PER-16/PJ/2016 tidak menyatakan cara membulatkan PPh setahun ÷ 12 (atau ÷ faktor bulan bagi pegawai baru).

**Putusan.** Dibulatkan **ke bawah** ke rupiah penuh. Berlaku juga untuk pembagian proporsional lain pada metode lama.

**Dasar.** Contoh resmi PER-16/PJ/2016 Lampiran I.6.2.2, PDF hlm. 43–45 (berkas pengembangan `PER16_I.6.2.2.json`): "5/12 X 17.500.000 = 7.291.666" (nilai eksak 7.291.666,67; pembulatan terdekat akan menghasilkan 7.291.667). Contoh I.1.3 (PDF hlm. 29: 4.090.000 : 12 = 340.833) dan I.6.1.2 (PDF hlm. 41–42: 6.433.333 dan 1.608.333) konsisten dengan pembulatan ke bawah.

**Dampak.** Tidak ada perubahan GT3. Menjadi dasar putusan kelompok 3 adjudikasi engine lama (GT3-007, GT3-010).

## K3. Menghitung tunjangan pajak (*gross-up*) dan PPh ditanggung

**Pertanyaan.** Bila kebijakan perusahaan "tunjangan pajak = PPh 21 terutang", persamaan T = PPh(X + T) dengan pembulatan bisa punya dua solusi. Mana yang dipakai, dan berapa tunjangan pajak di Masa Pajak Terakhir?

**Putusan.**
1. T = **titik tetap terkecil** dari T = R(tarif(X + T) × (X + T)), dengan R aturan pembulatan K1/K2 untuk masa itu. Titik ini diperoleh dengan iterasi mulai T = 0.
2. Di Masa Pajak Terakhir, T = PPh setahun (bruto termasuk T) − PPh masa sebelumnya, juga titik tetap terkecil. Bila hasilnya lebih potong, T = 0.
3. Rumus tertutup PPh ÷ (1 − tarif) tidak dipakai karena bisa melompati titik tetap terkecil.
4. (Ditambahkan Tahap 9.) Bila iterasi masuk siklus tanpa titik tetap (pembulatan di dalam metode selisih PER-16 untuk penghasilan tidak teratur dapat membuat tunjangan lebih besar menghasilkan pajak lebih kecil, sehingga fungsi tidak monoton), T = nilai terkecil dalam siklus yang menutup pajaknya sendiri, PPh(X + T) ≤ T; *engine* mencatat peringatan `FixedPointCycle`. Selisih yang teramati beberapa puluh rupiah (contoh: siklus 5.004.244 → 5.004.127 → 5.004.111; T = 5.004.127, PPh 5.004.111). Ditemukan oleh generator $S^G$ pada kasus *gross-up* 2020 dengan THR dan bonus; tidak ada kasus GT yang terkena.

**Dasar.** Regulasi tidak mengatur cara iterasi. PMK 168/2023 Lampiran B Bagian Kedua I.5, PDF hlm. 45 (pengembangan) menunjukkan bahwa besarnya tunjangan pajak ditentukan kebijakan pemberi kerja (tunjangan tetap Rp300.000 tidak sama dengan PPh Rp34.000), jadi "T = PPh" adalah kebijakan, bukan kewajiban. Untuk kebijakan itu, kalkulator DJP (GT2-06: bruto 15.561.000, TER A 7%) memilih 1.171.257, titik tetap terkecil dari dua solusi di bawah pembulatan ke bawah (1.171.257 dan 1.171.258). Dengan pembulatan 2025+ solusi kasus itu tunggal (1.171.258).

**Dampak.** Tidak ada perubahan karena K3 sendiri; nilai 038, 044, 049 berubah karena K1.

## K4. PPh 21 ditanggung pemberi kerja

**Pertanyaan.** PER-16 menyebut PPh yang ditanggung pemberi kerja sebagai kenikmatan yang bukan objek pemotongan, sedangkan sejak UU HPP natura/kenikmatan menjadi objek dan dipotong mulai Juli 2023. Bagaimana 2023 dan 2024+?

**Putusan.**
1. Masa Januari–Juni 2023: PPh yang ditanggung **tidak** ditambahkan ke bruto (tanpa *gross-up*).
2. Masa Juli–Desember 2023: PPh yang ditanggung adalah kenikmatan yang wajib dipotong, sehingga dihitung *full gross-up* dengan metode PER-16 (belum ada kasus GT3).
3. Tahun 2024 dst.: kenikmatan dan objek pemotongan, dihitung *full gross-up*; angkanya sama dengan metode tunjangan pajak (K3), tetapi tidak dipotong dari gaji.

**Dasar.**
- PER-16/PJ/2016 Pasal 8 ayat (2), PDF hlm. 9: "Pajak Penghasilan yang ditanggung oleh pemberi kerja … merupakan penerimaan dalam bentuk kenikmatan sebagaimana dimaksud pada ayat (1) huruf b." Contoh resmi PER-16 Lampiran I.8, PDF hlm. 46 (pengembangan): PPh yang ditanggung "bukan merupakan penghasilan yang dikenakan pajak" dan tidak di-*gross-up*.
- PMK 66/2023 Pasal 23 ayat (4), PDF hlm. 18: natura/kenikmatan "yang diterima atau diperoleh pada Masa Pajak Januari 2023 sampai dengan Masa Pajak Juni 2023 dikecualikan dari pemotongan"; Pasal 24: pegawai menghitung dan membayar sendiri di SPT. Pemotongan kenikmatan berlaku mulai 1 Juli 2023 (Pasal 27, PDF hlm. 19).
- PMK 168/2023 Lampiran B Bagian Kedua I.4, PDF hlm. 44: PPh yang ditanggung "merupakan penggantian dalam bentuk kenikmatan … dan merupakan objek pemotongan Pajak Penghasilan Pasal 21", dihitung "secara full gross up". Hanya kaidah ini yang dipakai; angka contoh I.4 (set *holdout*) tidak dipakai.

**Dampak.** Tidak ada perubahan. GT3-004 (Maret 2023) tetap tanpa *gross-up*; GT3-018, 025, 045, 049 tetap *full gross-up*.

## K5. Isi "penghasilan bruto tetap dan teratur" untuk kriteria DTP Rp10 juta

**Pertanyaan.** Apakah premi JKK/JKM/BPJS Kesehatan yang dibayar pemberi kerja, lembur, THR, bonus, dan natura ikut dihitung dalam batas Rp10.000.000 (PMK 10/2025, PMK 105/2025)?

**Putusan.** Yang dihitung: gaji dan tunjangan yang tetap dan teratur setiap bulan, ditambah imbalan lain (termasuk natura/kenikmatan) yang ditetapkan tetap dan teratur dalam peraturan perusahaan atau kontrak kerja, pada Masa Januari (atau bulan pertama bekerja). Tidak dihitung: premi JKK, JKM, dan BPJS Kesehatan yang dibayar pemberi kerja; lembur insidental; THR; bonus. Status layak/tidak layak berlaku untuk seluruh masa tahun itu walaupun gaji kemudian naik atau turun.

**Dasar.**
- PMK 10/2025 Pasal 4 ayat (3), PDF hlm. 5 (sama dengan PMK 105/2025 Pasal 4 ayat (4), PDF hlm. 5): penghasilan tetap dan teratur "berupa: a. gaji dan tunjangan yang sifatnya tetap dan teratur setiap bulan; dan/atau b. imbalan sejenis yang bersifat tetap dan teratur, yang ditetapkan berdasarkan ketentuan peraturan perusahaan dan/atau perjanjian kontrak kerja." Ayat (4) (PMK 105: ayat (5)): dapat berupa natura dan/atau kenikmatan.
- Premi BPJS pemberi kerja bukan gaji/tunjangan dan tidak ditetapkan oleh peraturan perusahaan, tetapi oleh PP 44/2015 dan Perpres JKN. PMK 168/2023 Pasal 5 ayat (3), PDF hlm. 9, juga memisahkan "gaji, segala jenis tunjangan" (huruf a) dari iuran JKK/JKM (huruf d) dan iuran jaminan kesehatan (huruf e).
- FAQ DJP PMK 72/2025 nomor 2, hlm. 4: "Penghasilan yang bersifat tidak teratur (seperti bonus, tunjangan hari raya, atau lembur insidentil) tidak dihitung dalam penentuan kelayakan batas Rp10 juta"; nomor 9, hlm. 7: natura dihitung "asalkan imbalan tersebut bersifat tetap dan teratur yang ditentukan pada kontrak/perjanjian"; nomor 11, hlm. 7: kelayakan "diuji satu kali" pada Masa Januari atau bulan pertama bekerja.
- Contoh resmi PMK 10/2025 Lampiran B nomor 2, PDF hlm. 18–20 (pengembangan): bruto Januari Rp15.000.000 (termasuk bonus Rp5.000.000), gaji + tunjangan tetap Rp10.000.000 → layak; tetap layak setelah promosi Rp12.000.000 mulai Oktober.

**Dampak.** Tidak ada perubahan angka. GT3-029 tetap layak; asumsinya dipertegas bahwa lembur Januari adalah lembur insidental. GT3-030 dan GT3-036 tetap tidak layak; GT3-047 tetap layak sepanjang 2026.

## K6. Plafon biaya jabatan untuk bagian tahun

**Pertanyaan.** PMK 168/2023 Pasal 10 ayat (2) menyebut plafon "Rp6.000.000,00 setahun atau … Rp500.000,00 sebulan". Untuk pegawai yang bekerja n bulan, plafonnya agregat n × Rp500.000, atau Rp500.000 per bulan masing-masing?

**Putusan.** **Agregat:** biaya jabatan = min(5% × bruto seluruh masa kerja, n × Rp500.000), dengan n = jumlah bulan bekerja pada pemberi kerja itu (n = 12 → Rp6.000.000).

**Dasar.**
- PMK 168/2023 Lampiran B Bagian Kedua I.2.1.1, PDF hlm. 35–36 (pengembangan): "Biaya jabatan 5% X Rp62.000.000,00 (maksimal 4 X Rp500.000,00)"; I.2.2.3, PDF hlm. 42–43: "(maksimal 8 x Rp500.000,00)".
- PMK 105/2025 Lampiran B nomor 3, PDF hlm. 41–43: skenario yang sama dengan contoh 3 PMK 10/2025 memakai "5% X Rp 95.000.000,00 (maksimal 10 X Rp500.000,00) Rp 4.750.000,00".
- PMK 72/2025 Lampiran B nomor 6 dan 7, PDF hlm. 42–47 (pegawai setahun dengan bulan THR/bonus berbruto di atas Rp10 juta): "5% x Rp96.200.000,00 = Rp4.810.000" dan "5% x Rp104.000.000,00 = Rp5.200.000". Plafon per bulan akan menghasilkan 4.570.000 dan 4.900.000.
- Bukti sebaliknya hanya contoh 3 PMK 10/2025, PDF hlm. 20–22 (disalin di PMK 72/2025 Lampiran B nomor 3): "9 x Rp 450.000,00 … 1 x Rp 500.000,00" = 4.550.000. Contoh ini bertentangan dengan PMK 168/2023 yang mengatur cara menghitung, dengan dua contoh lain di PMK 72/2025, dan dengan contoh yang sama di PMK 105/2025, sehingga diperlakukan sebagai ralat.

**Dampak.** Tidak ada perubahan. Bila plafon per bulan dipakai, hasilnya berubah di GT3-037 (biaya jabatan 3.985.232,5; PPh setahun 892.000; Desember −630.619), GT3-048 (4.273.025; 1.209.650; September −1.071.216), dan juga GT3-034 yang bekerja setahun (4.526.890; 1.690.500; Desember −83.920). Jadi tafsir per bulan tidak hanya memengaruhi pegawai bagian tahun, seperti dugaan README GT3 sebelumnya.

## K7. Keringanan JKK untuk iuran Agustus 2025

**Pertanyaan.** PP 7/2025 berlaku untuk iuran Februari–Juli 2025; perpanjangannya (PP 36/2025) baru ditetapkan 4 September 2025. Berapa premi JKK Agustus 2025 yang masuk bruto PPh 21?

**Putusan.** Iuran JKK Agustus 2025 s.d. Januari 2026 memakai **tarif keringanan 50%**, dan premi itulah yang masuk bruto. Premi yang sempat dibayar dengan tarif normal untuk Agustus adalah kelebihan bayar yang diperhitungkan ke iuran bulan berikutnya, bukan premi JKK Agustus.

**Dasar.**
- PP 36/2025 Pasal I angka 2 (Pasal 10A), PDF hlm. 4: penyesuaian iuran JKK "dilakukan perpanjangan sampai dengan Iuran JKK bulan Januari 2026"; Pasal II angka 1, PDF hlm. 4: perusahaan "yang telah melunasi Iuran JKK bulan Agustus 2025 dan/atau Iuran bulan berikutnya dan terdapat kelebihan maka kelebihan pembayaran Iuran JKK tersebut diperhitungkan untuk Iuran JKK bulan berikutnya."
- PP 7/2025 Pasal 6 ayat (1), PDF hlm. 5: iuran dibayar "paling lambat tanggal 15 bulan berikutnya", sehingga iuran Agustus jatuh tempo 15 September 2025, setelah PP 36/2025 berlaku.
- PMK 168/2023 Pasal 5 ayat (3) huruf d, PDF hlm. 9: yang menjadi penghasilan adalah iuran JKK/JKM "yang dibayarkan oleh pemberi kerja".

**Dampak.** Tidak ada perubahan (GT3-034, 036, 037 untuk Agustus–Desember 2025; 042, 047, 048 untuk Januari 2026).

## K8. Porsi iuran JKK yang direkomposisi untuk JKP

**Pertanyaan.** Sebagian iuran JKK (0,14%; 0,12% untuk risiko sangat rendah) dialihkan BPJS untuk iuran JKP. Apakah porsi itu tetap masuk bruto?

**Putusan.** Ya. Seluruh tarif JKK yang dibayar pemberi kerja (normal atau keringanan) masuk bruto; rekomposisi tidak mengurangi bruto.

**Dasar.** PP 7/2025 Pasal 4 ayat (1), PDF hlm. 4 menetapkan iuran JKK yang dibayar perusahaan (mis. sedang 0,445%), dan Pasal 9 ayat (1), PDF hlm. 5–6, menyebut iuran JKK tersebut "direkomposisi" untuk JKP. Rekomposisi adalah pembagian di BPJS, bukan pembayaran terpisah oleh pemberi kerja. Objek PPh menurut PMK 168/2023 Pasal 5 ayat (3) huruf d (PDF hlm. 9) adalah "pembayaran iuran jaminan kecelakaan kerja … yang dibayarkan oleh pemberi kerja", dan yang dibayar adalah tarif penuh. JKP sendiri tidak memungut iuran tambahan dari pemberi kerja.

**Dampak.** Tidak ada perubahan (semua kasus).

## K9. Iuran JP pegawai pada metode lama 2023

**Pertanyaan.** PER-16 Pasal 10 ayat (3) huruf b menyebut iuran ke dana pensiun dan badan penyelenggara THT/JHT, tidak menyebut Jaminan Pensiun BPJS secara tegas.

**Putusan.** Iuran JP 1% yang dibayar pegawai adalah **pengurang** penghasilan bruto pada 2023.

**Dasar.** PER-16/PJ/2016 Lampiran I.1.a.1 angka 1 huruf c, PDF hlm. 21: penghasilan neto dihitung dengan mengurangkan "iuran pensiun, iuran Jaminan Hari Tua, dan/atau iuran Tunjangan Hari Tua yang dibayar sendiri oleh pegawai … kepada Dana Pensiun … atau kepada BPJS Ketenagakerjaan". JP adalah iuran pensiun ke BPJS Ketenagakerjaan. Untuk 2024+ dasarnya PMK 168/2023 Pasal 10 ayat (1) huruf b, PDF hlm. 11–12 ("iuran terkait program pensiun dan hari tua … kepada … badan penyelenggara jaminan sosial ketenagakerjaan").

**Dampak.** Tidak ada perubahan (semua kasus 2023).

## K10. Zakat lewat pemberi kerja tahun 2023

**Putusan.** Pada 2023 zakat **bukan** pengurang dalam pemotongan PPh 21; pegawai mengurangkannya sendiri di SPT Tahunan. Mulai 2024 zakat lewat pemberi kerja mengurangi neto di Masa Pajak Terakhir saja, tidak mengurangi dasar TER.

**Dasar.** PER-16/PJ/2016 Pasal 10 ayat (3), PDF hlm. 10: neto pegawai tetap = bruto "dikurangi dengan: a. biaya jabatan …; b. iuran …" (daftar tertutup, tanpa zakat). PMK 168/2023 Pasal 10 ayat (1) huruf c, PDF hlm. 12, menambahkan zakat sebagai pengurang mulai 2024; Pasal 8 ayat (1) huruf a dan Pasal 15 ayat (1) huruf a, PDF hlm. 10 dan 15: dasar TER adalah penghasilan bruto.

**Dampak.** Tidak ada perubahan (GT3-008; 2024+: 020, 021, 038, 050).

## K11. Batas upah JP Januari–Februari 2023

**Putusan.** Iuran JP Januari–Februari 2023 memakai batas Rp9.077.600; batas baru berlaku mulai iuran Maret setiap tahun (Rp9.559.600 / 2023, Rp10.042.300 / 2024, Rp10.547.400 / 2025, Rp11.086.300 / 2026).

**Dasar.** Surat BPJS Ketenagakerjaan B/77/022023 (27 Februari 2023, `bpjs_tk_batas_upah_jp/`): "Batas paling tinggi Upah sebagai dasar perhitungan iuran Jaminan Pensiun mulai bulan Maret 2023 … = 9.077.600 x (1 + 5,31/100) … dibulatkan menjadi 9.559.600". Angka 9.077.600 adalah batas yang berlaku sebelum penyesuaian (PP 45/2015 Pasal 29 ayat (3)–(4), PDF hlm. 21: penyesuaian tahunan dengan pertumbuhan PDB). Surat 2024–2026 menyatakan pola yang sama ("mulai Maret").

**Dampak.** Tidak ada perubahan (GT3-009, 010, 012).

## K12. Natura dalam metode lama 2023

**Pertanyaan.** Bagaimana natura Juli–Desember 2023 dimasukkan ke metode PER-16 yang membedakan penghasilan teratur dan tidak teratur, dan berapa nilainya?

**Putusan.**
1. Natura/kenikmatan yang diberikan tiap bulan (rumah dinas) = penghasilan **teratur** (ikut disetahunkan); pemberian sekali (bingkisan) = **tidak teratur** (metode selisih).
2. Nilai: natura = nilai pasar; kenikmatan = biaya yang dikeluarkan atau seharusnya dikeluarkan pemberi kerja, dinilai per bulan.
3. Yang masuk bruto hanya selisih di atas batas pengecualian: rumah individual Rp2.000.000/bulan, kupon makan dinas luar Rp2.000.000/bulan, bingkisan selain hari raya Rp3.000.000 kumulatif setahun (termasuk bingkisan Januari–Juni yang tidak dipotong); kendaraan dikecualikan bagi pegawai tanpa penyertaan modal dengan rata-rata bruto 12 bulan ≤ Rp100.000.000/bulan.
4. Natura Januari–Juni 2023 tidak dipotong dan tidak masuk perhitungan Masa Pajak Terakhir pemberi kerja.

**Dasar.** PER-16 Lampiran I.1.a.1 angka 1 huruf a, PDF hlm. 20 ("segala jenis tunjangan dan pembayaran teratur lainnya") dan I.1.b angka 1, PDF hlm. 23 ("tunjangan hari raya, dan penghasilan lain semacam itu yang sifatnya tidak tetap dan biasanya dibayarkan sekali setahun"). PMK 66/2023 Pasal 22 ayat (1) dan (3), PDF hlm. 16–17 (nilai pasar / biaya; kenikmatan > 1 bulan dinilai setiap bulan); Pasal 5 ayat (4)–(5), PDF hlm. 6–7 (kupon: "Selisih lebih … merupakan objek"); Pasal 7 ayat (4), PDF hlm. 8; Lampiran huruf A angka 2, 7, 8, PDF hlm. 21–22; Lampiran huruf B contoh 2, PDF hlm. 24 (batas bingkisan dihitung dari akumulasi setahun); Pasal 23 ayat (4) dan Pasal 24, PDF hlm. 18.

**Dampak.** Tidak ada perubahan (GT3-006, 009; aturan nilai dan batas juga dipakai untuk 019 dan 050). Menjadi dasar putusan kelompok 1 adjudikasi engine lama.

## K13. DTP pegawai yang berhenti di tengah tahun

**Pertanyaan.** PMK 105/2025 Pasal 5 ayat (5) berbicara tentang kelebihan DTP terhadap PPh "untuk 1 (satu) Tahun Pajak". Apakah lebih potong yang berasal dari DTP di bulan berhenti bekerja juga tidak dikembalikan?

**Putusan.** Ya. Pada setiap Masa Pajak Terakhir, termasuk bulan berhenti bekerja, lebih potong yang berasal dari PPh DTP tidak dikembalikan kepada pegawai. Khusus sektor pariwisata 2025 (DTP hanya Oktober–Desember), bagian lebih potong yang berasal dari PPh yang dipotong sendiri (bukan DTP) tetap dikembalikan (PMK 72/2025 Pasal 5 ayat (5a)); belum ada kasus GT3 untuk ini.

**Dasar.** PMK 168/2023 Pasal 1 angka 18, PDF hlm. 4 (Masa Pajak Terakhir mencakup "Masa Pajak tertentu di mana Pegawai Tetap berhenti bekerja") dan Lampiran B Bagian Pertama I.2 angka 8, PDF hlm. 30: "Tidak termasuk kelebihan Pajak Penghasilan Pasal 21 yang dikembalikan sebagaimana dimaksud pada angka 7 yaitu Pajak Penghasilan Pasal 21 yang ditanggung pemerintah." PMK 105/2025 Pasal 5 ayat (5)–(6), PDF hlm. 6: kelebihan DTP "tidak dikembalikan" dan kelebihan pembayaran pemotong yang berasal dari DTP "tidak dapat dikembalikan dan tidak dapat dikompensasikan". PPh "1 (satu) Tahun Pajak" bagi pegawai yang berhenti adalah PPh atas bagian tahun pajak (PMK 168/2023 Pasal 15 ayat (1) huruf b, PDF hlm. 15).

**Dampak.** Tidak ada perubahan (GT3-048; juga 034 dan 037 di Desember).

## K14. Arti "bruto" masa pada metode lama (baru)

**Pertanyaan.** Pada bulan THR/bonus 2023, nilai "bruto masa" yang dicatat sebagai fakta keluaran: penghasilan teratur saja, atau seluruh penghasilan bulan itu?

**Putusan.** Bruto masa = **seluruh** penghasilan yang diterima pada masa itu, teratur dan tidak teratur (sama dengan arti bruto pada rezim TER). Bruto teratur dicatat terpisah sebagai rincian metode lama.

**Dasar.** PER-16/PJ/2016 Pasal 10 ayat (1), PDF hlm. 10: jumlah penghasilan bruto "adalah seluruh jumlah penghasilan … yang diterima atau diperoleh dalam suatu periode atau pada saat dibayarkan". Lampiran I.2 angka 1 huruf a, PDF hlm. 24: perhitungan akhir atas "seluruh penghasilan …, baik penghasilan yang teratur maupun yang tidak teratur".

**Dampak.** Tidak ada perubahan GT3 (003, 008, 009, 010 sudah memakai arti ini). Menjadi dasar putusan kelompok 2 adjudikasi engine lama.

## K15. Lembur pada metode lama (baru)

**Putusan.** Pada 2023, lembur adalah penghasilan **teratur** dan ikut disetahunkan pada bulan dibayarkan (bukan dihitung dengan metode selisih).

**Dasar.** PER-16 Lampiran I.1.a.1 angka 1 huruf a, PDF hlm. 20: penghasilan sebulan "meliputi seluruh gaji, segala jenis tunjangan dan pembayaran teratur lainnya, termasuk uang lembur (overtime)". Contoh resmi I.1.3, PDF hlm. 29 (pengembangan): lembur Rp2.000.000 dijumlahkan dengan gaji lalu dikalikan 12. Untuk 2024+ lembur masuk bruto masa (PMK 168/2023 Pasal 5 ayat (3) huruf a, PDF hlm. 9). Untuk kriteria DTP lihat K5.

**Dampak.** Tidak ada perubahan (GT3-002, 007, 011).

## K16. PTKP karyawati kawin yang tercatat K/x (baru)

**Pertanyaan.** GT3-048 adalah karyawati berstatus K/1 dan dihitung dengan PTKP K/1 serta TER kategori B, tetapi asumsinya tidak menyebut dasar status itu.

**Putusan.** Karyawati kawin memakai PTKP diri sendiri (TK/0; TER A) kecuali dapat menunjukkan keterangan tertulis pemerintah daerah (serendah-rendahnya kecamatan) bahwa suaminya tidak berpenghasilan; dengan keterangan itu PTKP = diri + kawin + tanggungan, dan kategori TER mengikuti PTKP tersebut.

**Dasar.** PMK 168/2023 Pasal 9 ayat (2) huruf a dan ayat (3), PDF hlm. 11; PER-16 Pasal 11 ayat (3)–(4), PDF hlm. 11; PP 58/2023 Pasal 2 ayat (3), PDF hlm. 4 (kategori TER "berdasarkan besarnya Penghasilan Tidak Kena Pajak"). Contoh resmi PER-16 I.1.3, PDF hlm. 29 (pengembangan) memakai keterangan Pemda.

**Dampak.** GT3-048: asumsi dan uraian ditambah keterangan kecamatan; angka tidak berubah.

## K17. Pembulatan premi dan iuran BPJS (baru, Tahap 5)

**Pertanyaan.** Tarif × upah sering berpecahan. PP 44/2015, PP 45/2015, PP 46/2015, dan Perpres JKN tidak mengatur pembulatan.

**Putusan.** Premi dan iuran dibulatkan ke rupiah penuh terdekat (0,50 ke atas), terpisah untuk setiap program (JKK, JKM, JHT, JP, JKN) dan setiap pihak (pemberi kerja, pegawai).

**Dasar.** Tidak ada aturan tertulis; prototipe lama memakai mode yang sama (`BULAT-BPJS-01`, mengikuti fungsi ROUND di lembar kerja kantor). Kasus GT3 sengaja memakai upah yang menghasilkan premi bulat, sehingga putusan ini tidak mengubah acuan; kasus $S^E$ memakai putusan ini secara konsisten untuk emas dan kandidat. Dinyatakan di dokumen konvensi masukan.

**Dampak.** Tidak ada perubahan GT.

## K18. DTP pada metode *gross-up* dan PPh ditanggung (baru, Tahap 7)

**Pertanyaan.** PMK 10/2025 Pasal 5 ayat (1) mewajibkan PPh 21 DTP dibayar tunai "termasuk dalam hal Pemberi Kerja memberikan tunjangan Pajak Penghasilan Pasal 21 atau menanggung Pajak Penghasilan Pasal 21". Apakah tunjangan pajak (*gross-up*) dan PPh yang ditanggung pemberi kerja tetap dihitung selama masa DTP?

**Putusan.**
1. Metode *gross-up*: tunjangan pajak adalah penghasilan tunai yang diberikan pemberi kerja dan tetap dihitung (titik tetap K3); PPh terutang atas bruto itu ditanggung pemerintah dan dibayar tunai di atas tunjangan.
2. Metode ditanggung: PPh yang ditanggung pemerintah bukan beban pemberi kerja, sehingga tidak ada kenikmatan PPh ditanggung yang di-*gross-up* (K4 tidak berlaku selama masa DTP); DTP yang dibayar tunai masuk gaji bersih pegawai.
3. DTP bukan penghasilan (Pasal 5 ayat (2)).

**Dasar.** PMK 10/2025 Pasal 5 ayat (1)–(2), PDF hlm. 6; PMK 105/2025 Pasal 5 ayat (1)–(2); PMK 168/2023 Pasal 7 huruf h; putusan perlakuan pajak di `dataset/10_kebijakan_perusahaan/klausul/README.md` dan GT5 putusan 5. Sama untuk DTP masa COVID (PMK 23/2020 Pasal 2 ayat (4)).

**Dampak.** Emas E06/E11: `REG.DTP.NO_GROSSUP` hanya untuk metode ditanggung (sebelumnya juga *gross-up*, keliru); aturan baru `REG.DTP.THP_CASH` (dan `REG.COVID_DTP.THP_CASH` di D05). Ditemukan lewat pemeriksaan silang contoh kebijakan SP06 dan GT5-CENTEX; GT3 tidak berubah.

## Hal yang tidak diputuskan di sini

- Perlakuan PPh atas iuran JKK bila perusahaan tidak lolos verifikasi keringanan (PP 7/2025 Pasal 5 ayat (2)): di luar kasus GT3; sistem harus meminta data status verifikasi, bukan menebak.
- PPh ditanggung pemberi kerja Juli–Desember 2023 dengan metode PER-16 (K4 butir 2) belum punya kasus atau contoh resmi pengembangan; bila kasus semacam itu ditambahkan, angkanya perlu ditinjau ulang.
