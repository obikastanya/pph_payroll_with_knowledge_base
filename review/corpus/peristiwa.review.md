# Tinjauan: tabel peristiwa perubahan

Berkas yang diperiksa: [dataset/09_korpus_peristiwa/peristiwa.csv](../../dataset/09_korpus_peristiwa/peristiwa.csv)
Status: **selesai**

Untuk setiap pertanyaan, tulis jawaban di bawahnya. Bila ada yang salah, tulis nilai yang benar beserta sumbernya.

Seluruh 46 baris dicek ke teks PDF (tanggal, masa berlaku, relevansi, jenis, sifat surut); tanggal diundangkan yang berupa gambar dicek ke JDIH Kemenkeu atau JDIH BPK. Putusan lengkap dengan kutipan pasal ada di [docs/spesifikasi/tafsir_korpus.md](../../docs/spesifikasi/tafsir_korpus.md) (kode A dan B di bawah).

## Pertanyaan

1. **Kelengkapan.** Apakah ada perubahan aturan tahun 2023–2026 yang memengaruhi PPh 21 pegawai tetap atau iuran BPJS yang ikut dihitung dalam PPh 21, tetapi tidak ada di tabel? Contoh yang perlu dipikirkan: perubahan batas upah BPJS Kesehatan, perubahan tarif atau ketentuan lain yang dipakai di kantor Anda.

   Jawaban: Tidak ada yang hilang (A9). Batas upah JKN tetap Rp12 jt dan tarif PPU 5% (4%/1%) sejak Perpres 64/2020; Perpres 59/2024 (P04) hanya menyatakan ulang batas atas dan mengubah batas bawah untuk usaha mikro dan kecil; kenaikan iuran JKN 2026 masih wacana. PTKP tetap PMK 101/PMK.010/2016. Tarif JHT, JP, JKM, dan JKK normal tidak berubah; perubahan iuran yang masuk bruto hanya keringanan JKK (E07, E09). Perpanjangan keringanan JKK sesudah iuran Januari 2026 dan perubahan atas PMK 105/2025, PMK 168/2023, atau PP 58/2023 tidak ditemukan sampai 27 Oktober 2026.

2. **Relevansi.** Untuk setiap baris `uji`, apakah dokumen itu benar mengubah perhitungan PPh 21 bulanan pegawai tetap? Perhatikan khususnya E07 dan E09 (keringanan iuran JKK): apakah di kantor Anda keringanan ini ikut menurunkan bruto PPh 21?

   Jawaban: Ya, kedua belas baris relevan. Untuk E07 dan E09: ya, keringanan menurunkan bruto. PMK 168/2023 Pasal 5 ayat (3) huruf d (PDF hlm. 9) memasukkan iuran JKK "yang dibayarkan oleh pemberi kerja" ke penghasilan, dan yang dibayar menjadi tarif keringanan (mis. risiko sedang 0,445%). Porsi yang direkomposisi ke JKP tetap bagian dari iuran JKK yang dibayar, jadi seluruhnya masuk bruto (K8). Premi bulan iuran Agustus 2025 memakai tarif keringanan walaupun PP 36/2025 baru terbit 4 September (K7, B2). Batas upah JP (E01, E05, E08, E12) relevan karena iuran JP pegawai 1% adalah pengurang dan dihitung dari upah yang dibatasi. Koreksi pada baris uji: E07 `berlaku_surut` menjadi `ya` (iuran Februari, terbit 7 Februari); E02 `berlaku_surut` menjadi `tidak` (B4); E10 tanggal diundangkan dan terbit menjadi 2025-10-28 (A7); semua `jenis_perubahan` diganti kode taksonomi.

3. **Pengecoh.** Untuk setiap baris `pengecoh`, apakah benar dokumen itu tidak mengubah perhitungan PPh 21 pegawai tetap? Perhatikan khususnya P01 (PP 49/2023, rekomposisi JKK) dan P06 (PP 6/2025, JKP).

   Jawaban: Benar untuk semua 21 baris. P01: rekomposisi JKK 0,14% dan JKM 0,10% ke JKP sudah berlaku sejak PP 37/2021; yang dibayar pemberi kerja tetap 0,24–1,74% + 0,30%, jadi bruto tetap (A1). P06: iuran JKP turun ke 0,36% dari dana pemerintah dan rekomposisi JKK; tidak ada iuran baru dari pemberi kerja (A2). P15 PMK 114/2025 dan P20 PER-4/PJ/2026 diputus sebagai pengecoh X5: zakat lewat pemberi kerja tetap pengurang dengan rumus yang sama; yang berubah dasar hukum, syarat kelayakan input, dan daftar penerima (A3, A4). Koreksi data: P03 diundangkan 16 Mei 2024 dan berlaku sejak itu (sebelumnya 29 April); P02 berlaku s.d. 21 Mei 2025 (dicabut PER-11/PJ/2025); P10 berlaku 6 bulan s.d. 7 September 2023 dan isinya upah dibayar paling sedikit 75% (bukan dipotong hingga 75%); P15 catatan lama keliru menyebut PMK 168/2023 merujuk PMK 254/2010. Di bagian pengembangan, D08, D12, dan D13 juga tidak mengubah perhitungan PPh 21 dan diubah menjadi `relevan = tidak` (A6).

4. **Tanggal berlaku.** Apakah `berlaku_mulai` dan `berlaku_sampai` sesuai praktik? Khususnya E02 (natura mulai 1 Juli 2023), E07 (keringanan JKK iuran Februari–Juli 2025), dan E09 (perpanjangan sejak iuran Agustus 2025).

   Jawaban: Sesuai. E02: PMK 66/2023 Pasal 27 (PDF hlm. 19) berlaku 1 Juli 2023 dan Pasal 23 ayat (4) mengecualikan natura Masa Januari–Juni 2023 dari pemotongan. E07: PP 7/2025 Pasal 10 (PDF hlm. 6) "Iuran JKK bulan Februari 2025 sampai dengan Iuran JKK bulan Juli 2025". E09: PP 36/2025 Pasal 10A (PDF hlm. 4) memperpanjang "sampai dengan Iuran JKK bulan Januari 2026", menyambung dari iuran Juli, sehingga berlaku mulai iuran Agustus 2025; Pasal II menyebut kelebihan iuran "bulan Agustus 2025". Tanggal yang dikoreksi di luar tiga baris ini: E10, P02, P03, P10, D12, D13 (lihat jawaban 2 dan 3).

5. **Berlaku surut.** Untuk E06 (PMK 10/2025 terbit 4 Februari, berlaku Januari 2025), E09, dan E10: bagaimana kantor Anda menyelesaikan masa yang sudah lewat? Apakah potongan bulan itu dihitung ulang, selisihnya dikembalikan di bulan berikutnya, atau diperhitungkan di Desember?

   Jawaban: Berbeda per peristiwa (B1–B3).
   - E06: PPh 21 Januari tidak dihitung ulang (terutangnya sama), tetapi seluruhnya menjadi DTP. Potongan Januari dibayarkan kembali tunai kepada pegawai pada penggajian berikutnya (Februari), tidak dikenai pajak, dan dilaporkan sebagai DTP di SPT Masa Januari atau pembetulannya paling lambat 31 Januari 2026 (PMK 10/2025 Pasal 5 ayat (1)–(2), Pasal 6 ayat (3)–(4)).
   - E09: premi JKK Agustus memakai tarif keringanan; kelebihan iuran yang sudah dibayar diperhitungkan ke iuran bulan berikutnya (PP 36/2025 Pasal II). Selisih PPh 21 Agustus tidak dibetulkan per masa, melainkan terserap di perhitungan Desember karena PPh setahun dihitung dari bruto setahun dengan premi keringanan.
   - E10: sama dengan E06 untuk Masa Oktober (DTP dibayar tunai pada penggajian November, dilaporkan di SPT Masa Oktober). Di Desember berlaku aturan khusus pariwisata: lebih potong dikembalikan hanya sebesar bagian yang bukan DTP Oktober–November, dan pemberi kerja dapat mengompensasikannya dengan kertas kerja dan bukti potong tambahan (PMK 72/2025 Pasal 5 ayat (5a), (6a), (6b)).

## Hasil

- [ ] Disetujui tanpa perubahan
- [x] Disetujui dengan perubahan (tulis di atas)
- [ ] Perlu revisi
