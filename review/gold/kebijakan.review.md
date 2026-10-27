# Tinjauan emas lapisan kebijakan perusahaan (pembaca kedua)

Tanggal: 2026-10-27. Peninjau: *agent* pembaca kedua, terpisah dari penyusun emas.

Berkas:
- [kebijakan.koding.csv](kebijakan.koding.csv): pengodean buta SP01–SP14 (bagian A). Ditulis sebelum membuka emas dan tidak disunting sesudahnya (`git hash-object` fee66c2e…).
- [kebijakan.banding.csv](kebijakan.banding.csv): penyelarasan dengan `GOLD-SP01..14` (bagian B.1).
- [pkb.cek.csv](pkb.cek.csv): pemeriksaan tidak buta lima emas PKB (bagian B.2), hanya berisi masalah.

## 1. Ringkasan angka

| Hal | Jumlah |
|---|---|
| Unsur emas SP01–SP14 | 44 aturan (+3 definisi fakta) |
| Baris pengodean peninjau | 50: 36 unsur, 14 klausul "tanpa unsur" (menyatakan ulang atau hanya tampak berkonflik) |
| Pasangan selaras (baris banding) | 46: 40 aturan emas berpasangan dengan 36 unit peninjau (satu unit bisa ke beberapa aturan), 4 aturan emas tanpa unit peninjau, 2 klausul yang sama-sama tidak dikodekan |
| Unit peninjau tanpa padanan emas | 0 |
| Beda nilai | 1 (SP08 pengurang: zakat hilang di emas) |
| Beda target dengan hasil berbeda bagi laporan konflik | 2 (SP03, SP06) |
| Beda kode konflik | 7 (anotasi C6 pada `jkk_rate` di SP01, SP02, SP09, SP10, SP11, SP13; C10 pada THR SP14) |
| Putusan | sama 31, emas_benar 8, tafsir 5, ragu 1, peninjau_benar 1 |

## 2. Perbedaan yang mengubah nilai atau laporan konflik

**SP08, `PRS.SP08.DEDUCTIONS` (peninjau_benar).** Ps. 18 ayat (2) huruf c hanya menambahkan iuran JKN pegawai ke pengurang. Ekspresi emas `job_expense + annual_pension_contributions + sum_periods('health_employee')` mengganti seluruh `REG.YEAR.DEDUCTIONS`, sehingga `annual_zakat_deduction` (berlaku sejak 2024, `REG.ZAKAT.DEDUCTIBLE`) ikut hilang. Kebijakan tidak mengatur zakat (Ps. 39 ayat (2): hal lain mengikuti peraturan). Pada kasus yang punya zakat lewat pemberi kerja, emas akan melaporkan C3 yang sebenarnya tidak ada. Selain itu, kandidat LLM yang mempertahankan zakat akan dinilai berbeda dari emas. **Rekomendasi:** tambahkan `+ annual_zakat_deduction`, atau pindahkan perubahannya ke `employee_pension_contributions` seperti pada pengodean peninjau.

**SP03 dan SP06, DTP tidak diteruskan (emas_benar).** Peninjau mengodekan klausul ini pada `employee_tax_burden`. Emas memakai `pph21_dtp := 0` (C4). Pilihan emas lebih tepat. `pph21_dtp` dihasilkan aturan wajib `REG.DTP.RUNNING/FINAL`, sehingga C4 dilaporkan tepat saat `dtp_facility` benar. Sebaliknya, untuk metode *gross* dan *gross-up* fakta `employee_tax_burden` hanya punya pesaing *default* (`REG.THP.TAX_BURDEN`; `REG.DTP.THP_CASH` hanya untuk `employer_borne`), jadi konflik tidak akan pernah dilaporkan. Yang perlu dicatat: model ini mendeteksi C4 hanya lewat fakta `pph21_dtp`. Kebijakan lain yang menahan DTP dengan cara memotong gaji bersih tidak akan terdeteksi.

**Anotasi C6 pada `jkk_rate` (emas_benar, 6 baris).** Nilainya sama. Peninjau menulis `none` karena pada kasus yang kelompok risikonya cocok tidak muncul konflik. Karena `conflict_code` hanya dipakai saat aturan kalah dengan nilai berbeda, anotasi C6 tetap tepat untuk kasus kelompok risiko lain atau keringanan JKK. Untuk SP05 kedua pihak sama-sama C6 (tekstil, keringanan Februari 2025 sampai Januari 2026).

**`withholding_method = 'gross'` dari kata "dipotong" (tafsir, SP04, SP07, SP11, SP14).** Pada keempat kebijakan ini teks hanya menyatakan PPh "dipotong (sesuai ketentuan)". Teks tidak menyebut beban pekerja, padahal metode *gross-up* juga memotong. Bacaan emas wajar, tetapi aturan ini mengalahkan `case('method')`, jadi nilainya berubah bila data kasus memakai metode lain. **Rekomendasi:** catat aturan bacaan ini di README kebijakan sintetis, atau batasi `METHOD` pada teks yang menyebut beban pekerja (SP01, SP02, SP03, SP05, SP09).

**SP04 (ragu, kelemahan bersama).** Emas dan peninjau sama-sama menetapkan `benefits_taxable_regular := 0`. Akibatnya semua natura teratur ikut dinolkan, termasuk kendaraan dan `other_benefit` yang tidak termasuk Ps. 27. C1 akan dilaporkan juga untuk natura yang tidak diatur kebijakan. **Rekomendasi:** tulis ekspresi sebagai `REG.NATURA.REGULAR` tanpa suku `housing_individual`, atau batasi lewat kondisi.

**SP14 THR (tafsir).** Anotasi C10 tidak pernah terpakai karena 1,5 kali upah selalu di atas `thr_minimum`. Ini tidak berdampak.

## 3. Temuan pada emas PKB (rinci di pkb.cek.csv)

Yang berdampak pada nilai PPh 21 atau laporan konflik:
1. **WIKA Ps. 22 ayat (2)** tidak diformalkan. Metode `employer_borne` membuat seluruh PPh, termasuk atas Jasa Produksi dan IHL, ditanggung dan di-*gross-up*, sehingga bruto, PPh setahun, dan THP bulan bonus terlalu tinggi. Penyebabnya, `REG.BORNE.GROSSUP.*` bersifat *mandatory* dan menetapkan bahwa yang ditanggung adalah seluruh PPh masa. Ini batas representasi yang perlu dicatat di representasi.md bagian 10 atau diselesaikan dengan fakta dasar *default*.
2. **WIKA `BPJS_WAGE`.** Konflik C8 akan muncul pada setiap bulan sakit, dirumahkan, atau ditahan, juga saat UMP lebih besar dari Fixed Pay, padahal di situ dasar perusahaan justru lebih tinggi. Label emas ("laten, hanya bila Tunjangan Grade tetap") tidak sesuai dengan perilaku *engine*.
3. **CENTEX `BPJS_WAGE`.** Jeda dua bulan tidak pernah berlaku untuk kenaikan 21 Desember karena dijepit ke `first_month`. Sebaliknya, perubahan faktor sakit memicu C6 palsu.
4. **SANSAN ditahan (Ps. 82 ayat 2).** Tunjangan jabatan tetap dibayar 100% dan bantuan dihitung dari gaji pokok saja, sehingga bruto bulan ditahan terlalu tinggi. Untuk bulan sakit (Ps. 34 ayat 2), emas tidak konsisten dengan lembar klausul (C10 laten).
5. **CENTEX dan Taekwang.** Komponen teratur tetapi tidak tetap (tunjangan kehadiran, transportasi, dan shift harian, perangsang panggilan, potongan absen) disalurkan ke `other_regular_income`, yang dibaca `REG.DTP.FIXED_INCOME`. Menurut K5 komponen ini tidak dihitung dalam batas Rp10 juta. Keduanya KLU padat karya penerima DTP 2025–2026. Hal yang sama terjadi pada uang makan dan transport SP01 (Januari–Maret 2025). Ini masalah di tingkat kosakata regulasi: `other_regular_income` dipakai sekaligus sebagai "penghasilan teratur" (bruto) dan "penghasilan tetap" (uji DTP).

Yang kecil (nilai fakta antara atau kasus jarang): syarat uang pisah WIKA, plafon kacamata AVCO yang dijumlahkan, bantuan pemakaman tanggungan AVCO, jam reguler hari ke-6 AVCO, izin pulang cepat Taekwang, `valid_from` CENTEX dan SANSAN yang memasukkan bulan sebelum PKB berlaku, dan Ps. 26 ayat 4 WIKA yang tidak dicatat.

Tidak ditemukan kesalahan nilai pada: tarif lembur CENTEX, AVCO, dan Taekwang; pita bonus dan THR CENTEX; THR WIKA, AVCO, Taekwang, dan SANSAN; tabel Lampiran WIKA dan AVCO (dicocokkan dengan `dataset/13_teks/*/tabel/`); faktor sakit dan dirumahkan WIKA; uang pisah AVCO, WIKA (nilai), dan SANSAN L2; bantuan hidup AVCO; serta sumbangan CENTEX.

## 4. Catatan prosedur

1. **Kebutaan.** Sebelum bagian A selesai, peninjau membuka `review/README.md` (indeks folder, tanpa isi tinjauan kebijakan) dan melihat daftar nama berkas `sintetis/`, tetapi tidak membuka isi `*.json`, `INDEX.csv`, `README.md` sintetis, maupun `review/company_policies/`. Untuk melihat seluruh rekaman regulasi, peninjau juga menjalankan skrip sendiri yang memuat rantai emas regulasi lewat `build_gold.build(side=False)`. Skrip ini tidak menyertakan Δ kebijakan.
2. **Konteks *pipeline* kurang.** `kb_context.py` (yang juga dipakai LLM) tidak memuat `REG.BPJS.JKK_RATE`, `REG.BPJS.JP_WAGE`, `REG.BPJS.JP_EMPLOYEE`, dan `REG.BPJS.JHT_EMPLOYEE` untuk SP01, SP05, SP10, dan SP11, padahal klausul kebijakan itu justru mengatur hal-hal tersebut. SP01 dan SP11 malah mendapat `REG.JKN.WAGE.2014` yang sudah tidak berlaku. Penyebabnya, pemilihan *seed* mencocokkan label lengkap ("iuran jaminan pensiun pekerja"), sedangkan teks memakai singkatan (JKK, JP, JHT). Ini akan merugikan kandidat LLM pada eksperimen kebijakan. Perlu diperbaiki (sinonim atau singkatan pada label) sebelum eksperimen dibekukan.
3. **Satuan untuk Krippendorff's α.** Satuan pengodean peninjau tidak sama dengan satuan aturan emas. Ada pemetaan satu ke banyak (SP01-U1, SP02-U2, SP11-U2), dan target berbeda dengan efek sama (JP dan JKN di SP01 dan SP11). Disarankan α dihitung per klausul dengan dua variabel nominal: (ada unsur? ya/tidak) dan (kode konflik atau none), bukan per aturan. Anotasi `jkk_rate` sebaiknya disepakati dulu (status konflik atau kode bila kalah), karena 6 dari 7 beda kode berasal dari perbedaan arti kolom itu, bukan dari perbedaan bacaan klausul.
4. Tidak ada berkas emas atau kode yang diubah.
