# Adjudikasi: selisih GT3 dengan kalkulator prototipe lama

Status: **selesai** (2026-10-27)

Dua perhitungan yang disusun terpisah dibandingkan: 50 kasus GT3 (hitungan manual dari teks regulasi) dan kalkulator prototipe lama. Dari 743 angka, 683 sama. Selisihnya ada di 8 kasus dan terbagi menjadi tiga kelompok. Mohon putuskan mana yang benar menurut praktik dan aturan. Rincian angka ada di [dataset/11_acuan/diferensial_gt3.csv](../../dataset/11_acuan/diferensial_gt3.csv); langkah hitung GT3 ada di `dataset/11_acuan/gt3_kasus_bertingkat/GT3-xxx.json`.

**Sebaiknya jawab dulu dengan hitungan Anda sendiri, baru lihat kolom "dugaan".** Dengan begitu putusan Anda tidak terpengaruh dugaan kami.

## 1. Natura (PMK 66/2023) — GT3-006, GT3-009, GT3-019, GT3-050

Kalkulator lama memasukkan seluruh nilai natura (rumah, kendaraan dinas, kupon makan dinas luar) sebagai penghasilan. GT3 menerapkan pengecualian dan batas nilai di PMK 66/2023.

- Contoh GT3-019 (Agustus 2024, TK/0): bruto GT3 Rp11.884.000, PPh 21 Rp475.360; kalkulator lama bruto Rp15.884.000, PPh 21 Rp1.111.880.
- Pertanyaan: bagian mana dari natura di kasus-kasus ini yang menurut Anda menjadi penghasilan kena pajak?

Jawaban: **GT3 benar.** Yang menjadi bruto hanya selisih di atas batas pengecualian PMK 66/2023 (Pasal 4 huruf e, Pasal 5 ayat (4)–(5), Pasal 7 ayat (4); Lampiran huruf A, PDF hlm. 6–8 dan 21–22):
- rumah dinas individual: kelebihan di atas Rp2.000.000/bulan (Lampiran A angka 7). GT3-006 Rp3.000.000 → Rp1.000.000; GT3-009 Rp2.800.000 → Rp800.000 (mulai Juli 2023); GT3-019 Rp2.500.000 → Rp500.000; GT3-050 Rp2.200.000 → Rp200.000;
- kupon makan pegawai dinas luar: kelebihan di atas Rp2.000.000/bulan (Pasal 5 ayat (4) huruf a dan ayat (5)). GT3-019 Rp2.300.000 → Rp300.000;
- kendaraan dinas: seluruhnya dikecualikan karena pegawai tidak punya penyertaan modal dan rata-rata brutonya ≤ Rp100.000.000/bulan (Lampiran A angka 8) (GT3-006, GT3-050);
- bingkisan selain hari raya: kelebihan kumulatif di atas Rp3.000.000 setahun (Lampiran A angka 2; cara kumulatif sesuai Lampiran B contoh 2, PDF hlm. 24). GT3-009: Agustus Rp2.000.000 → 0; November Rp2.000.000 → Rp1.000.000, dihitung sebagai penghasilan tidak teratur;
- natura Januari–Juni 2023 tidak dipotong pemberi kerja dan tidak masuk perhitungan Desember (Pasal 23 ayat (4) dan Pasal 24, PDF hlm. 18).

Contoh GT3-019: bruto Rp11.884.000, TER A 4%, PPh 21 Rp475.360 (GT3). Angka engine lama (Rp15.884.000; Rp1.111.880) memasukkan seluruh natura dan tidak sesuai PMK 66/2023. Putusan CSV: `gt3_benar` (46 baris). Rincian: tafsir K12 di `docs/spesifikasi/tafsir_perhitungan.md`.

## 2. Bruto pada bulan THR tahun 2023 — GT3-003, GT3-008, GT3-009, GT3-010

PPh 21 kedua perhitungan sama, tetapi angka "bruto" bulan THR berbeda sebesar nilai THR.

- Pertanyaan: di slip atau laporan pemotongan tahun 2023 (metode lama), bruto bulan THR dicatat termasuk THR atau tidak?

Jawaban: **Termasuk THR.** Ini perbedaan definisi, bukan kesalahan hitung: PPh 21 kedua sisi sama, dan engine lama melaporkan bruto teratur saja (nilai antara metode selisih). Arti yang ditetapkan untuk fakta "bruto masa" adalah seluruh penghasilan yang diterima pada masa itu, teratur dan tidak teratur, karena PER-16/PJ/2016 Pasal 10 ayat (1), PDF hlm. 10, menyebut jumlah penghasilan bruto "adalah seluruh jumlah penghasilan … yang diterima atau diperoleh dalam suatu periode atau pada saat dibayarkan", dan perhitungan akhir memakai "seluruh penghasilan …, baik penghasilan yang teratur maupun yang tidak teratur" (Lampiran I.2 angka 1 huruf a, PDF hlm. 24). Bruto teratur tetap disimpan sebagai rincian (`rincian_metode_lama`). Putusan CSV: `definisi_berbeda` (4 baris); arti yang dipakai adalah arti GT3 (tafsir K14).

## 3. Pembulatan PPh bulanan tahun 2023 — GT3-007, GT3-010

Selisih Rp1 per bulan. GT3 membulatkan ke bawah hasil PPh setahun dibagi 12.

- Pertanyaan: di kantor Anda, hasil PPh setahun ÷ 12 dibulatkan bagaimana (ke bawah, ke atas, atau ke rupiah terdekat)?

Jawaban: **Ke bawah; GT3 benar.** Contoh resmi PER-16/PJ/2016 Lampiran I.6.2.2 (PDF hlm. 43–45) menulis "5/12 X 17.500.000 = 7.291.666" padahal nilai eksaknya 7.291.666,67; pembulatan ke terdekat atau ke atas akan menghasilkan 7.291.667. Contoh I.1.3 (340.833) dan I.6.1.2 (6.433.333; 1.608.333) konsisten dengan itu. Jadi GT3-007 September Rp49.416 dan GT3-010 Maret dan Mei–Juli Rp220.416, April Rp1.010.416, masa terakhir Agustus −Rp1.119.596, sudah benar; engine lama yang lebih Rp1 per bulan salah. Putusan CSV: `gt3_benar` (8 baris; tafsir K2).

Catatan tambahan di luar tiga kelompok: dua baris GT3-005 dan GT3-012 (engine lama tidak mendukung *gross-up* 2023) diputus `gt3_benar` karena nilai GT3 sudah dihitung ulang independen. Setelah tinjauan, GT3 dikoreksi untuk pembulatan TER mulai Masa Januari 2025 (PER-11/PJ/2025 Pasal 129; tafsir K1), sehingga 114 baris di 10 kasus 2025–2026 kini berbeda Rp1–Rp11 dari engine lama yang membulatkan ke bawah; baris itu diberi putusan `tafsir`.

## Hasil

- [x] Disetujui (putusan tertulis di atas)
- [ ] Perlu diskusi
