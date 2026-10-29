# Mockup v2: tampilan untuk admin finance

Rancangan tampilan sistem PPh 21 berbasis knowledge base untuk pengguna sehari-hari (admin finance), bukan peneliti.
Halaman Beranda tidak diubah; tetap seperti di `system/app`.

```
env\Scripts\streamlit run mini_demo\mockup\main.py --server.port 8503
```

Lalu buka http://localhost:8503. Tidak butuh kunci API.

## Mana yang nyata, mana yang simulasi

| Bagian | Data |
|---|---|
| Kalkulator, penampil KB | nyata: knowledge base emas (`dataset/12_emas`) dan engine penelitian (`system/pph21kbs`), hanya dibaca |
| Kartu review dan contoh dampak | nyata: pembaruan emas PMK 105/2025 dan batas upah JP 2026, dihitung sebelum dan sesudah |
| Cek KB | nyata: pemeriksa statis dan tanggal berakhir aturan |
| Setujui, tolak, kembalikan versi, unggah dokumen | simulasi di sesi; knowledge base di disk tidak berubah |
| Asisten | simulasi: pencocokan maksud sederhana atas KB nyata; angka dan sumber jawabannya nyata, kalimatnya disiapkan |

## Prinsip rancangan

1. **Setiap istilah bisa ditanyakan.** Kata bergaris titik dengan tanda "?" menampilkan penjelasan singkat saat
   kursor diarahkan ke kata itu (`glossary.py`, 65 istilah). Kolom isian memakai tooltip "?" bawaan Streamlit dengan
   teks yang sama, dan di sidebar ada "Kamus istilah" yang bisa dicari.
2. **Kata sehari-hari.** Istilah penelitian (abstain, konsensus, kandidat, pengecoh, Δ) diganti dengan kata biasa:
   sistem ragu, kesepakatan, versi usulan, dokumen tidak relevan, pembaruan. Istilah teknis hanya muncul di
   "Detail untuk peneliti".
3. **Angka disertai kalimat.** Setiap hasil punya penjelasan satu kalimat, misalnya "Rp12.056.600 × 3% = Rp361.698,
   dipotong dari gaji".
4. **Tidak ada yang berubah tanpa review.** AI, formulir, dan asisten hanya membuat usulan atau draf. Semuanya masuk
   ke tab Review.
5. **Cakupan jujur.** Kasus di luar cakupan penelitian (pegawai tidak tetap, pesangon, PPh 26, pindahan perusahaan
   lain) disebutkan di layar, tidak dihitung diam-diam.

## Halaman

**Kalkulator PPh 21**
- Mode *Coba hitung satu pegawai*:
  - skenario cepat: pegawai biasa, THR + bonus, masuk Juli, keluar Agustus, gaji naik April, gross-up, DTP 2025,
    lembur tiap bulan;
  - isian dalam tiga langkah: pegawai, penghasilan tetap, lalu tabel per bulan yang bisa diubah untuk lembur, THR,
    bonus, natura, zakat, dan cuti tanpa upah.
- Hasilnya:
  - kartu "PPh 21 bulan ini" dan kartu "Akhir tahun": bruto, biaya jabatan, iuran, neto, PTKP, PKP, Pasal 17, sudah
    dipotong, lalu kurang atau lebih bayar;
  - grafik per bulan, catatan otomatis (lonjakan THR, PTKP karyawati, DTP), rincian per bulan dalam CSV, dan dasar
    hukum per angka (pasal dan kutipan);
  - pembanding cara bayar pajak (gross, gross-up, ditanggung): PPh, gaji bersih, dan pajak yang dibayar perusahaan.
- Mode *Payroll bulanan*: satu tabel untuk banyak pegawai, pilih masa pajak, lalu PPh setiap pegawai dan rekap masa.
  Tombol ekspor e-Bupot dan tutup masa adalah rancangan.

**Penampil knowledge base**
- Peta topik: 9 topik ditambah kebijakan perusahaan, dengan kartu aturan yang dibaca sebagai kalimat (rumus dengan
  nama Indonesia, tanggal berlaku, pasal, kutipan).
- Alur perhitungan: gambar langkah dari bruto ke PPh masa dan PPh setahun; pilih satu langkah untuk melihat aturannya.
- Angka dari waktu ke waktu: grafik tangga untuk setiap parameter, dan isi tabel per versi.
- Riwayat perubahan: per dokumen.
- Bandingkan dua tanggal: apa yang mulai berlaku, berhenti berlaku, dan angka yang berubah.
- Cari dan daftar kebijakan perusahaan.

**Manajemen knowledge base**
- Kotak masuk: unggah PDF, TXT, atau JSON, dengan langkah proses yang terlihat (baca teks, cek relevansi, susun
  usulan, pemeriksaan otomatis, cek kesepakatan, review). Status ditulis jelas, termasuk "Sistem ragu" dan "Tidak
  relevan".
- Review: kartu perubahan lama → baru dengan kutipan, lima pemeriksaan otomatis dalam kalimat biasa, kebijakan
  perusahaan yang mungkin terdampak, dan contoh dampak pada pegawai. Tombolnya Setujui, Perbaiki (sunting lalu
  periksa ulang), dan Tolak.
- Tambah:
  - *angka baru*, perubahan yang paling sering (nilai lama otomatis berakhir sehari sebelumnya);
  - *aturan baru* dengan rumus dan syarat;
  - *tabel baru* dari CSV atau lampiran PDF.
- Ubah atau cabut: mencabut berarti memberi tanggal akhir. Sistem memperingatkan bila sesudah tanggal itu tidak ada
  aturan pengganti.
- Kebijakan perusahaan: dari contoh aturan (THR, bonus, uang makan, gross-up).
- Cek KB:
  - angka tahunan yang belum ada untuk tahun depan (mis. batas upah JP);
  - aturan yang akan berakhir (mis. DTP 31 Des 2026);
  - temuan pemeriksa statis.
- Riwayat: setiap versi, dengan kembali ke versi lama tanpa menghapus riwayat.
- Asisten KB di sidebar.

**Hasil penelitian**
- Empat pertanyaan dalam bahasa biasa. Masing-masing berisi jawaban singkat (Ya / Sebagian / Belum kokoh), angka
  dalam bentuk "x dari y", gambar kotak per dokumen atau kasus, dan "Artinya bagi pengguna". Angka teknis dilipat
  di "Detail untuk peneliti".
- Pembanding: kalkulator yang dikodekan tangan, AI yang langsung menghitung, AI yang menyusun aturan dari nol.

## Asisten KB (rancangan)

- **Model:** `gpt-5.4-mini` (OpenAI). Tersedia di akun proyek, harga USD 0,75 / 4,50 per juta token masukan /
  keluaran, konteks 400 ribu token
  ([halaman model OpenAI](https://developers.openai.com/api/docs/models/gpt-5.4-mini)). Satu percakapan dengan
  konteks KB yang relevan (±20 ribu token) kira-kira USD 0,02.
- **Tool baca:** cari aturan, baca parameter dan riwayatnya, ringkas pembaruan atau isi kotak masuk, jelaskan hasil
  review.
- **Tool tulis, hanya draf:** tambah angka atau aturan, ubah, cabut, aturan kebijakan perusahaan. Draf masuk ke
  Review; asisten tidak pernah menerapkan perubahan sendiri.
- **Jawaban:** selalu menyebut sumber (dokumen, pasal, kutipan) dari KB, bukan dari ingatan model.

## Temuan yang harus dibawa ke sistem penuh

- **Engine:** masa pajak terakhir saat ini diambil dari bulan terakhir yang diisi. Bila admin hanya mengisi
  Januari–Maret untuk pegawai yang bekerja sampai Desember, Maret dihitung sebagai masa terakhir (hasilnya keliru:
  lebih bayar). Mockup ini selalu mengirim semua bulan kerja, jadi masalah itu tidak muncul di sini. Sistem penuh
  harus menentukan masa terakhir dari bulan keluar atau Desember, dan memakai PPh yang benar-benar sudah dipotong
  pada bulan-bulan yang sudah ditutup.
- **Payroll bulanan:** butuh data pegawai yang tersimpan, kunci masa, ekspor e-Bupot, dan bukti potong A1.
