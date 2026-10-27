# Tinjauan pembaca kedua: Δ\* emas peristiwa regulasi E01–E13

Tanggal: 2026-10-27. Pembaca kedua: Claude (agen terpisah). Berkas:
- `review/gold/regulasi.koding.csv`: koding buta tahap 1 (73 unit), ditulis sebelum berkas emas dibuka dan tidak disunting sesudahnya (SHA-256 `4df1f500…0d35c17`).
- `review/gold/regulasi.banding.csv`: penyelarasan dengan `dataset/12_emas/delta/GOLD-E01..E13.json` (83 baris).

## Ringkasan angka

| Ukuran | Nilai |
|---|---|
| Unsur emas | 73 (E01 1, E02 13, E03 7, E04 13, E05 1, E06 15, E07 2, E08 1, E09 2, E10 5, E11 11, E12 1, E13 1) |
| Unit peninjau | 73, termasuk 11 unit "tanpa unsur" (bukan-perubahan) |
| Pasangan selaras (emas dan peninjau ada) | 68 |
| Emas tanpa padanan unit (fakta atau aturan antara) | 5, semuanya `tafsir` |
| Unit peninjau tanpa padanan emas | 15 (11 `sama` karena kedua pihak tanpa unsur, 2 `tafsir`, 2 `ragu`) |
| Nilai berbeda (`value_same = tidak`) | 7 |
| Tanggal berbeda | 16 baris. Hanya 2 yang substantif (E02, awal fakta nilai bingkisan dan fasilitas olahraga). 3 adalah pilihan model di E10 tanpa beda hasil. 11 adalah notasi, karena emas menulis *change* dengan `valid_from` awal unsur, sedangkan peninjau menulis awal perpanjangan (E09, E11). |
| Putusan | sama 55, tafsir 18, peninjau_benar 8, ragu 2, emas_benar 0 |

Untuk E06, bentuk `REG.DTP.FINAL` di emas lebih umum dan benar untuk pariwisata di E10. Hasilnya di E06 sama, jadi baris itu dicatat `tafsir`.

## Perbedaan yang memengaruhi nilai hitung, per peristiwa

**E01, E05, E08, E12 (batas upah JP).** Nilai dan tanggal sama: 9.559.600 (2023-03), 10.042.300 (2024-03), 10.547.400 (2025-03), 11.086.300 (2026-03).

**E02 (PMK 66/2023, natura).**
1. *Batas tahunan bingkisan dan fasilitas olahraga mengabaikan pemberian Januari–Juni (peninjau_benar).* Di emas, `REG.NATURA.GIFT_VALUE` dan `REG.NATURA.SPORTS_VALUE` baru berlaku 2023-07-01. `REG.NATURA.IRREGULAR` memakai `cumulative()`, yang hanya menjumlah masa yang aturannya aktif. Akibatnya bingkisan Jan–Jun tidak ikut menghabiskan batas Rp3 jt.
   - Bukti: Lampiran A angka 2, PDF hlm. 21: "secara keseluruhan bernilai tidak lebih dari Rp3.000.000,00 … dalam jangka waktu 1 (satu) Tahun Pajak". Lampiran A angka 5, hlm. 22, untuk olahraga (Rp1,5 jt).
   - Tafsir proyek sendiri, K12 butir 3: kumulatif setahun "termasuk bingkisan Januari–Juni yang tidak dipotong". Docstring `ev_natura.py` bertentangan dengan K12.
   - Contoh dampak: bingkisan Rp2,5 jt di Maret dan Rp1 jt di Agustus. Emas memberi objek Agustus 0. Seharusnya objek Agustus Rp0,5 jt.
   - Rekomendasi: fakta nilai bingkisan dan olahraga berlaku mulai 2023-01-01, dan akumulasi memakai `sum_to_date`/`sum_before`. Bruto Jan–Jun tetap 0 (B4), karena aturan objek baru berlaku Juli. GT3-009 tidak membedakan kedua cara karena tidak ada bingkisan Jan–Jun; perlu kasus uji yang membedakannya.
2. *Batas kupon makan (peninjau_benar, dampak sempit).* Emas memakai batas tetap Rp2 jt. Pasal 5 ayat (4) huruf b, hlm. 6–7, memakai nilai makan di tempat kerja bila nilainya lebih dari Rp2 jt. Lampiran B contoh 1, hlm. 23: "nilai kupon … tidak boleh melebihi nilai makanan dan minuman yang diberikan di kantor PT BA yaitu Rp2.500.000,00", sehingga objeknya Rp200.000. GT3-009 menghindarinya lewat asumsi.
   - Rekomendasi: tambahkan atribut data (nilai makan di kantor) dan pakai `max(cap, nilai)`, atau catat sebagai batas cakupan.
3. Selebihnya sama: lima parameter dan *gross-up* PPh ditanggung Jul–Des 2023 (K4). Natura sekali-beri "lain" dimasukkan emas ke penghasilan teratur, peninjau ke tidak teratur; ini tafsir, dengan Desember sama.

**E03 (PP 58/2023).** Sama: kategori dan tabel TER, `valid_from` 2024-01-01. Emas memecah tarif dan PPh menjadi dua aturan; itu tafsir.

**E04 (PMK 168/2023).** Sama: zakat sebagai pengurang dan penutupan 12 aturan PER-16 per 2023-12-31. Peninjau sudah menambah aturan pengembalian tanpa bagian DTP (Pasal 21 ayat (2), hlm. 21), sedangkan emas baru menambahkannya di E06. Tidak ada beda hasil karena tidak ada DTP di 2024.

**E06 (PMK 10/2025).**
1. *Isi "penghasilan bruto tetap dan teratur" (peninjau_benar).* `REG.DTP.FIXED_INCOME` = gaji + tunjangan tetap + `other_regular_income`, tanpa natura tetap.
   - Bukti: Pasal 4 ayat (4), hlm. 5: "dapat diberikan dengan nama dan dalam bentuk apa pun, termasuk penerimaan dalam bentuk natura dan/atau kenikmatan". Tafsir K5 juga menyebut "imbalan/natura yang ditetapkan tetap".
   - Lampiran B contoh 4, hlm. 22–23: yang diuji adalah gaji tetap menurut kontrak (Rp11 jt), bukan Rp9,5 jt yang dibayar Januari karena sanksi. Emas memakai yang dibayar, sehingga Tuan D dinyatakan layak, padahal contoh menyatakan "tidak berhak".
   - Rekomendasi: masukkan natura teratur yang ditetapkan tetap (perlu ditentukan nilai mana yang dipakai) dan atribut opsional gaji tetap kontraktual. Bila tidak, catat sebagai batas di K5.
2. *Syarat "tidak menerima insentif DTP lainnya" (peninjau_benar, dampak bergantung data).* Pasal 4 ayat (2) huruf c, hlm. 5, tidak ada di `REG.DTP.ELIGIBLE`.
3. Selebihnya sama atau tafsir: KLU, batas Rp10 jt, DTP masa = seluruh PPh, DTP tunai untuk metode ditanggung, tanpa *gross-up* (K18), dan pengembalian tanpa bagian DTP.

**E07, E09 (keringanan JKK).** Sama: tarif 0,12/0,27/0,445/0,635/0,87%, iuran Feb–Jul 2025, diperpanjang sampai 2026-01-31.

**E10 (PMK 72/2025).** Model emas dan peninjau berbeda (tabel KLU pariwisata terpisah dibanding atribut sektor), tetapi hasilnya sama. Satu hal `ragu`:
- Untuk pegawai pariwisata yang lebih potongnya ≤ DTP Okt–Nov, emas memberi `pph21_dtp` Desember = `final_period_tax + refund` = −80.000 (contoh 7).
- Lampiran B contoh 7, hlm. 46, menulis DTP Desember "-" dengan total DTP 240.000. Contoh 3, hlm. 41, untuk padat karya justru menulis DTP Desember "(277.500)". Contoh 8, hlm. 48, menggabung kolom "DTP/Pengembalian" sebesar 1.200.000.
- Contoh resmi tidak seragam, padahal `pph21_dtp` termasuk F_nilai.
- Rekomendasi: tetapkan putusan tafsir tertulis (K baru) tentang tanda `pph21_dtp` di Masa Pajak Terakhir, atau keluarkan `pph21_dtp` Desember negatif dari penilaian.

**E11 (PMK 105/2025).** Perpanjangan ke 2026 sama. Dua kekurangan E06 (natura tetap, DTP lain) terbawa: PMK 105 Pasal 4 ayat (5) dan ayat (2) huruf c, hlm. 5.

**E13 (PER-11/PJ/2025).** `pph_round_mode` = `half_up` mulai 2025-01-01, sama dengan peninjau. Satu hal `ragu`: `REG.YEAR.PPH.PART_YEAR` tetap membulatkan `'down'`. PPh setahun untuk kewajiban subjektif bagian tahun dapat berpecahan, misalnya kelipatan 50 × n/12, dan Pasal 129 ayat (1) huruf a, hlm. 106, mencakup PPh di bukti potong 21. Selisihnya ≤ Rp1 dan hanya untuk pegawai yang datang atau pergi dari Indonesia. Rekomendasi: pakai `param('pph_round_mode')` sejak 2025, atau catat di K1 bahwa PPh setahun bagian tahun dikecualikan.

## Unsur emas yang menurut peninjau keliru secara hukum

1. E02 `REG.NATURA.GIFT_VALUE`, `REG.NATURA.SPORTS_VALUE`, `REG.NATURA.IRREGULAR`: batas tahunan tidak menghitung pemberian Jan–Jun. Ini bertentangan dengan Lampiran A angka 2 dan 5 dan dengan K12 butir 3.
2. E02 `REG.NATURA.REGULAR`: batas kupon mengabaikan Pasal 5 ayat (4) huruf b dan contoh 1 Lampiran B.
3. E06/E11 `REG.DTP.FIXED_INCOME`: natura tetap tidak dihitung (PMK 10 Pasal 4 ayat (4); PMK 105 Pasal 4 ayat (5); K5), dan uji memakai gaji yang dibayar, bukan gaji kontrak (PMK 10 Lampiran B contoh 4).
4. E06/E11 `REG.DTP.ELIGIBLE`: syarat Pasal 4 ayat (2) huruf c tidak ada. Unsur ini bisa juga dicatat sebagai batas data, bukan kesalahan.

Butir 3 (sebagian) dan 4 hanya berdampak bila data kasus memuat atribut yang belum ada di skema. Butir 1 dan 2 berdampak pada kasus yang sah dengan skema sekarang.

## Catatan prosedur (relevan untuk Krippendorff's alpha)

1. **Basis memuat emas peristiwa sebelumnya.** Konteks `kb_context.py` untuk E(n) berisi Δ\* emas E(n−1), dan ini memang tampilan pengakuisisi. Akibatnya koding E04–E13 terikat pada nama, id, dan pola emas sebelumnya, misalnya penutupan P16 dan perpanjangan aturan DTP. Kesepakatan representasi pada peristiwa lanjutan menjadi lebih tinggi daripada kesepakatan yang benar-benar independen.
2. **E13 tidak sepenuhnya buta.** Urutan rantai mengikuti tanggal terbit, sehingga E13 (22-05-2025) jatuh sebelum E09. Peninjau melihat basis E09 sebelum menulis unit E13, dan basis itu memuat `PAR.PPH_ROUND_MODE.2025`. Isi unit E13-u1 sama dengan putusan K1/B5 yang sudah diketahui, tetapi unit itu sebaiknya diberi tanda tidak buta atau dikeluarkan dari alpha.
3. **Daftar rekaman lebih lengkap dari yang dilihat LLM.** Peninjau menulis skrip sendiri (`base_for` dari `kb_context.py` + `_record_line`) untuk mendaftar semua rekaman basis, bukan hanya "relevant records".
4. **Tafsir sudah menentukan sebagian jawaban.** `tafsir_perhitungan.md` dan `tafsir_korpus.md` sudah memuat banyak jawaban (K4, K5, K7, K12, K13, K18, B1–B5). K18 bagian "Dampak" bahkan menyebut id unsur emas (`REG.DTP.NO_GROSSUP`, `REG.DTP.THP_CASH`). Jadi alpha mengukur kesepakatan di bawah aturan tafsir yang sama, bukan pembacaan hukum yang independen. Ini perlu disebut di paper.
5. **Satuan unit belum seragam.** Ada pemetaan satu-ke-banyak (E03-u5 ↔ RATE+RUNNING; E06-u6 ↔ ELIGIBLE+INCOME_TEST) dan fakta antara yang hanya ada di satu pihak. Disarankan alpha dihitung atas daftar unit tetap per ketentuan (parameter, tabel, aturan keluaran, penutupan), dengan fakta antara dan "tanpa unsur" dikeluarkan atau diberi kategori sendiri. Tanggal `change` sebaiknya dibandingkan sebagai masa berlaku efektif, bukan `valid_from` rekaman.
