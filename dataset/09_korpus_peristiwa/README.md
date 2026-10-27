# 09_korpus_peristiwa — Tabel peristiwa perubahan

Disusun 2026-10-27 dari PDF di [01_regulasi/](../01_regulasi/README.md). Ini adalah korpus peristiwa untuk E2 (akuisisi terisolasi), E3 (*regulation replay*), dan E4 (dampak lintas lapis), sesuai Definisi peristiwa perubahan di *skeleton*: $\epsilon = \langle d, t_{terbit}, t_{berlaku}, \tau \rangle$.

**Status: draf, menunggu tinjauan pakar** ([review/corpus/](../../review/corpus/peristiwa.review.md)).

## Kolom `peristiwa.csv`

| Kolom | Arti |
|---|---|
| `bagian` | `uji` (peristiwa relevan), `pengecoh`, nanti juga `pengembangan` dan `prospektif` |
| `relevan` | Apakah dokumen mengubah perhitungan PPh 21 pegawai tetap. Jawaban benar untuk pengecoh adalah pembaruan kosong |
| `jenis_perubahan` | Draf; disesuaikan dengan taksonomi perubahan di Tahap 2 |
| `tanggal_ditetapkan`, `tanggal_diundangkan` | Dari teks PDF. PMK yang ditandatangani elektronik menampilkan tanggal diundangkan sebagai gambar, sehingga tanggalnya diambil dari metadata JDIH BPK (dicatat di `bukti_tanggal`) |
| `tanggal_terbit` | $t_{terbit}$ = tanggal diundangkan bila ada, selain itu tanggal ditetapkan. Dipakai sebagai tanggal pengetahuan ω (Log keputusan 2026-10-27) |
| `berlaku_mulai`, `berlaku_sampai` | Masa berlaku hukum $[t_s, t_e]$ |
| `berlaku_surut` | `ya` bila `berlaku_mulai` < `tanggal_terbit` |
| `bukti_tanggal` | Halaman PDF atau sumber metadata yang memuat tanggal |

## Ringkasan

12 peristiwa relevan: 4 parameter tahunan (batas upah JP), 2 parameter bersyarat (keringanan JKK), 1 klasifikasi penghasilan (natura), 2 dokumen pergantian metode (TER), dan 3 fasilitas DTP. Tiga di antaranya berlaku surut: E06, E09, E10. E02 berlaku surut sebagian.

21 pengecoh, sebagian besar sulit karena tampak relevan, misalnya PP 49/2023 (rekomposisi JKK), PP 50/2025 (keringanan JKK untuk bukan penerima upah), PMK 6/2026 (DTP peserta magang), dan PER-12/PJ/2026 (menyebut bukti potong PPh 21). Dua di antaranya (PMK 114/2025, PER-4/PJ/2026 tentang zakat) masih perlu keputusan apakah pengecoh atau perubahan dasar hukum.

13 peristiwa pengembangan sebelum 2023 (bagian `pengembangan`): perubahan PTKP 2013 dan 2015 (berlaku surut), batas upah JKN, dan rangkaian insentif DTP PPh 21 masa COVID 2020–2022 yang strukturnya analog dengan DTP 2025: fasilitas baru, penggantian, perpanjangan, perubahan, dan pencabutan. Dokumen ini dipakai untuk merancang *prompt* dan gerbang tanpa menyentuh data uji.

PDF tambahan ada di `01_regulasi/pengecoh/` dan `01_regulasi/pengembangan/`, dengan manifes `01_regulasi/manifest_tambahan.csv` (URL, tanggal akses, ukuran, SHA-256), diunduh oleh `dataset/unduh_dataset.py`. Dokumen tanpa sumber resmi (PER-31/PJ/2012, PER-32/PJ/2015, surat batas upah JP 2019–2022) dan PP 21/2024 tidak diunduh; lihat `kandidat_tambahan.csv`.

## Catatan

- E03 dan E04 adalah satu perubahan hukum (pergantian ke TER) dalam dua dokumen yang terbit di hari berbeda. Keduanya dicatat sebagai dua peristiwa; apakah digabung diputuskan di Tahap 2.
- P01 (PP 49/2023) dikelompokkan sebagai pengecoh, karena total iuran JKK yang dibayar pemberi kerja tidak berubah. Ini perlu dikonfirmasi pakar.
- Mini demo memakai tanggal PMK 81/2024 31-12-2024; tanggal yang benar adalah ditetapkan 14-10-2024 dan diundangkan 18-10-2024.
- Peristiwa prospektif (terbit sesudah *cutoff* model) belum ada. Yang dipantau: PTKP baru dan DTP semua sektor 2027.
- Masa berlaku sebagian peristiwa pengembangan masih dari ringkasan pencarian; ditandai di kolom `catatan` dan dicek ke pasal sebelum dipakai.
