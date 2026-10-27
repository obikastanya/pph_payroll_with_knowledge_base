# 09_korpus_peristiwa — Tabel peristiwa perubahan

Disusun 2026-10-27 dari PDF di [01_regulasi/](../01_regulasi/README.md) dan ditinjau pada tanggal yang sama ([review/corpus/](../../review/corpus/peristiwa.review.md)). Ini adalah korpus peristiwa untuk E2 (akuisisi terisolasi), E3 (*regulation replay*), dan E4 (dampak lintas lapis), sesuai Definisi peristiwa perubahan di *skeleton*: $\epsilon = \langle d, t_{terbit}, t_{berlaku}, \tau \rangle$.

Keputusan relevansi dan semantik berlaku surut yang dipakai untuk jawaban acuan ada di [docs/spesifikasi/tafsir_korpus.md](../../docs/spesifikasi/tafsir_korpus.md).

## Kolom `peristiwa.csv`

| Kolom | Arti |
|---|---|
| `bagian` | `uji`, `pengecoh`, `pengembangan`; nanti juga `prospektif` |
| `relevan` | Apakah dokumen mengubah perhitungan PPh 21 pegawai tetap. Jawaban benar untuk dokumen `tidak` adalah pembaruan kosong |
| `jenis_perubahan` | Kode [taksonomi](../../docs/spesifikasi/taksonomi.md): jenis utama T1–T10 (atau X1–X5 untuk pengecoh), lalu sifat S1–S6 setelah titik koma |
| `tanggal_ditetapkan`, `tanggal_diundangkan` | Dari teks PDF. PMK yang ditandatangani elektronik menampilkan tanggal diundangkan sebagai gambar, sehingga tanggalnya diambil dari metadata JDIH Kemenkeu atau JDIH BPK (dicatat di `bukti_tanggal`). PER Dirjen dan surat BPJS tidak diundangkan |
| `tanggal_terbit` | $t_{terbit}$ = tanggal diundangkan bila ada, selain itu tanggal ditetapkan. Dipakai sebagai tanggal pengetahuan ω (Log keputusan 2026-10-27) |
| `berlaku_mulai`, `berlaku_sampai` | Masa berlaku hukum $[t_s, t_e]$: awal masa pajak atau bulan iuran yang dicakup, bukan sekadar tanggal mulai berlaku dokumen |
| `berlaku_surut` | `ya` bila `berlaku_mulai` < `tanggal_terbit` |
| `bukti_tanggal` | Halaman PDF atau sumber metadata yang memuat tanggal |

## Ringkasan

12 peristiwa uji: 4 parameter tahunan (batas upah JP: E01, E05, E08, E12), 2 keringanan iuran JKK (E07, E09), 1 klasifikasi penghasilan (natura, E02), 2 dokumen pergantian metode ke TER (E03, E04; dievaluasi sebagai dua peristiwa), dan 3 fasilitas DTP (E06, E10, E11). Empat berlaku surut: E06 (Masa Januari 2025), E07 (iuran Februari 2025, jeda 6 hari), E09 (iuran Agustus 2025), dan E10 (Masa Oktober 2025). E02 tidak berlaku surut: natura Januari–Juni 2023 dikecualikan dari pemotongan dan dilaporkan sendiri oleh pegawai.

21 pengecoh, semuanya `relevan = tidak`: administrasi atau pelaporan (X1), subjek di luar lingkup (X2: IKN, magang, bukan penerima upah, ASN, UMKM), perubahan iuran atau upah tanpa perubahan PPh 21 (X3: PP 49/2023, PP 6/2025, Permenaker 5/2023), pernyataan ulang (X4: Perpres 59/2024), dan pergantian dasar hukum tanpa perubahan rumus (X5: PMK 114/2025 dan PER-4/PJ/2026 tentang zakat).

13 peristiwa pengembangan sebelum 2023: perubahan PTKP 2013 dan 2015 (2015 berlaku surut), parameter JKN 2014 dan 2016, keringanan iuran BPJS TK masa COVID, dan rangkaian insentif DTP PPh 21 2020–2021 yang strukturnya analog dengan DTP 2025 (fasilitas baru, penggantian, perluasan KLU, perpanjangan). Tiga di antaranya tidak mengubah perhitungan PPh 21 dan dipakai sebagai pengecoh pengembangan: D08 PMK 110/2020 dan D12 PMK 149/2021 (menyatakan ulang ketentuan DTP PPh 21) serta D13 PMK 3/2022 (mencabut PMK 9/2021 setelah DTP PPh 21 berakhir). Dokumen ini dipakai untuk merancang *prompt* dan gerbang tanpa menyentuh data uji. Jenis perubahan yang tidak punya contoh nyata sebelum 2023 ditutup oleh regulasi fiktif di [fiktif/](fiktif/README.md).

PDF tambahan ada di `01_regulasi/pengecoh/` dan `01_regulasi/pengembangan/`, dengan manifes `01_regulasi/manifest_tambahan.csv` (URL, tanggal akses, ukuran, SHA-256), diunduh oleh `dataset/unduh_dataset.py`. Dokumen tanpa sumber resmi (PER-31/PJ/2012, PER-32/PJ/2015, surat batas upah JP 2019–2022) dan PP 21/2024 tidak diunduh; lihat `kandidat_tambahan.csv`.

## Catatan

- Semua tanggal diverifikasi ke teks PDF atau, untuk tanggal diundangkan yang berupa gambar, ke metadata JDIH. Satu konflik metadata: PMK 72/2025 (E10) diundangkan 28 Oktober 2025 menurut JDIH Kemenkeu, 20 Oktober menurut JDIH BPK; yang dipakai 28 Oktober (tafsir_korpus.md A7).
- Surat batas upah JP (E01, E05, E08, E12) adalah surat kantor cabang BPJS Ketenagakerjaan yang disalin dari situs pihak ketiga; angka dan tanggal berlakunya konsisten dengan rumus PP 45/2015 Pasal 29 ayat (3).
- Mini demo memakai tanggal PMK 81/2024 31-12-2024; tanggal yang benar adalah ditetapkan 14-10-2024 dan diundangkan 18-10-2024.
- Tidak ditemukan perubahan 2023–2026 lain yang memengaruhi PPh 21 pegawai tetap atau iuran BPJS yang masuk PPh 21 (pemeriksaan di tafsir_korpus.md A9).
- Peristiwa prospektif (terbit sesudah *cutoff* model) belum ada. Yang dipantau: batas upah JP 2027, PTKP baru, dan DTP 2027 ([pantauan_prospektif.md](pantauan_prospektif.md)).
